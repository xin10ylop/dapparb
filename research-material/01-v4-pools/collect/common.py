#!/usr/bin/env python3
"""Shared helpers for the 01-v4-pools collectors (Uniswap V4 on Base, chain id 8453).

Contents: JSON-RPC client with backoff, eth_getLogs with range bisection, V4 event decoders,
Hooks.sol permission-flag decoding, size-capped gzip CSV part writer, sentinel helpers.
Collect-only: nothing here interprets the data.
"""
import csv
import gzip
import hashlib
import io
import json
import os
import random
import threading
import time

import requests

# ----------------------------------------------------------------------------------------------------------------
# constants
POOL_MANAGER = "0x498581ff718922c3f8e6a244956af099b2652b2b"
STATE_VIEW = "0xa3c0c9b65bad0b08107aa264b0f3db444b867a71"
POSITION_MANAGER = "0x7c5f5a4bbd8fd63184577525326123b519429bdc"
MULTICALL3 = "0xca11bde05977b3631167028862be2a173976ca11"
POOL_MANAGER_DEPLOY_BLOCK = 25350988  # first block with code at POOL_MANAGER (binary search, see find_deploy_block.log)
BASE_GENESIS_TS = 1686789347          # verified in timestamps-check.csv: ts(block) = BASE_GENESIS_TS + 2*block

# topic0 = keccak256(event signature); computed with `cast keccak` and checked against real logs
T_INITIALIZE = "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"  # Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)
T_SWAP = "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"        # Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)
T_MODIFY = "0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"      # ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)
T_DONATE = "0x29ef05caaff9404b7cb6d1c0e9bbae9eaa7ab2541feba1a9c4248594c08156cb"      # Donate(bytes32,address,uint256,uint256)

DYNAMIC_FEE_FLAG = 0x800000

# Uniswap v4-core src/libraries/Hooks.sol: permission flag = bit in the low 14 bits of the hook address.
# (name, bit)  -- bit 13 is the most significant of the 14.
HOOK_FLAGS = [
    ("before_initialize", 13),
    ("after_initialize", 12),
    ("before_add_liquidity", 11),
    ("after_add_liquidity", 10),
    ("before_remove_liquidity", 9),
    ("after_remove_liquidity", 8),
    ("before_swap", 7),
    ("after_swap", 6),
    ("before_donate", 5),
    ("after_donate", 4),
    ("before_swap_returns_delta", 3),
    ("after_swap_returns_delta", 2),
    ("after_add_liquidity_returns_delta", 1),
    ("after_remove_liquidity_returns_delta", 0),
]
HOOK_FLAG_COLUMNS = ["hf_" + n for n, _ in HOOK_FLAGS]


def hook_flags(hooks_addr: str):
    v = int(hooks_addr, 16)
    return ["1" if (v >> b) & 1 else "0" for _, b in HOOK_FLAGS]


UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

for _v in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
    if not os.environ.get(_v) and os.path.exists("/root/.ccr/ca-bundle.crt"):
        os.environ[_v] = "/root/.ccr/ca-bundle.crt"


def now_utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


_log_lock = threading.Lock()


def log(*a):
    with _log_lock:
        print(now_utc(), *a, flush=True)


# ----------------------------------------------------------------------------------------------------------------
# RPC
class RpcError(Exception):
    def __init__(self, msg, code=None, kind="other"):
        super().__init__(msg)
        self.code = code
        self.kind = kind  # 'range' (block-range/result-size limit), 'archive', 'rate', 'http', 'other'


RANGE_MARKERS = ("block range", "range", "too many", "limit exceeded", "exceed", "response size", "query returned more than",
                 "10000 results", "timeout", "timed out", "too large", "larger than", "max results", "log response size")


def classify_error(msg: str, code):
    m = (msg or "").lower()
    if "archive" in m or "personal token" in m or "missing trie node" in m or "pruned" in m:
        return "archive"
    if code == 429 or "rate" in m or "compute units" in m or "capacity" in m or "too many requests" in m or "usage limit" in m:
        # 'too many requests' is a rate limit, but 'too many results/logs' is size
        if "results" not in m and "logs" not in m:
            return "rate"
    if any(k in m for k in RANGE_MARKERS):
        return "range"
    return "other"


class Endpoint:
    def __init__(self, name, url, max_range, inflight=2, min_interval=0.0, min_bisect=1):
        self.name = name
        self.url = url
        self.max_range = max_range
        self.min_bisect = min_bisect  # range errors on ranges <= this size are raised instead of bisected further
        self.sem = threading.Semaphore(inflight)
        self.min_interval = min_interval
        self._last = 0.0
        self._lk = threading.Lock()
        self.local = threading.local()
        self.stats = {"req": 0, "err": 0, "rate": 0}

    def session(self):
        s = getattr(self.local, "s", None)
        if s is None:
            s = requests.Session()
            s.headers.update({"User-Agent": UA, "content-type": "application/json"})
            self.local.s = s
        return s

    def call(self, method, params, timeout=90):
        """One JSON-RPC call; raises RpcError. No retry here (callers decide)."""
        with self.sem:
            if self.min_interval:
                with self._lk:
                    wait = self._last + self.min_interval - time.time()
                    if wait > 0:
                        time.sleep(wait)
                    self._last = time.time()
            self.stats["req"] += 1
            try:
                r = self.session().post(self.url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=timeout)
            except requests.RequestException as e:
                self.stats["err"] += 1
                raise RpcError("%s: %s" % (type(e).__name__, str(e)[:200]), kind="http")
        if r.status_code == 429:
            self.stats["rate"] += 1
            raise RpcError("HTTP 429", code=429, kind="rate")
        if r.status_code != 200:
            # some providers wrap JSON-RPC errors in non-200 responses (e.g. publicnode archive refusal = HTTP 403 + JSON error)
            try:
                jj = r.json()
                ee = jj.get("error") if isinstance(jj, dict) else None
            except ValueError:
                ee = None
            if ee:
                msg = "HTTP %d %s %s" % (r.status_code, ee.get("message", ""), str(ee.get("data", "")))
                kind = classify_error(msg, ee.get("code"))
                self.stats["err"] += 1
                if kind == "rate":
                    self.stats["rate"] += 1
                raise RpcError(msg[:300], code=ee.get("code"), kind=kind if kind != "other" else "http")
        if r.status_code >= 500 or r.status_code in (403, 408):
            self.stats["err"] += 1
            k = "range" if r.status_code in (413,) else "http"
            raise RpcError("HTTP %d %s" % (r.status_code, r.text[:200]), code=r.status_code, kind=k)
        if r.status_code == 413:
            raise RpcError("HTTP 413", code=413, kind="range")
        try:
            j = r.json()
        except ValueError:
            self.stats["err"] += 1
            raise RpcError("non-JSON HTTP %d %s" % (r.status_code, r.text[:200]), code=r.status_code, kind="http")
        if isinstance(j, dict) and j.get("error"):
            e = j["error"]
            msg = e.get("message", "") + " " + str(e.get("data", ""))
            kind = classify_error(msg, e.get("code"))
            self.stats["err"] += 1
            if kind == "rate":
                self.stats["rate"] += 1
            raise RpcError(msg[:300], code=e.get("code"), kind=kind)
        if "result" not in j:
            raise RpcError("no result: %s" % str(j)[:200], kind="other")
        return j["result"]

    def call_retry(self, method, params, tries=8, timeout=90):
        last = None
        for i in range(tries):
            try:
                return self.call(method, params, timeout=timeout)
            except RpcError as e:
                last = e
                if e.kind in ("range", "archive"):
                    raise
                time.sleep(min(60, (2 ** i) * (1.0 + random.random())))
        raise last


# ----------------------------------------------------------------------------------------------------------------
# getLogs with bisection
SAFE_RESULT_CAP = 5000  # a response with >= this many logs is re-fetched as two halves (guards against silent provider caps)


def get_logs_range(ep: Endpoint, frm: int, to: int, topics, address=POOL_MANAGER, tries=6, depth=0):
    """Return all logs in [frm, to] (inclusive) from endpoint ep. Bisects on range/size errors and on large results.
    Raises RpcError if a single block cannot be fetched after retries (caller records a gap / tries another endpoint)."""
    if to - frm + 1 > ep.max_range:
        mid = frm + ep.max_range - 1
        return get_logs_range(ep, frm, mid, topics, address, tries, depth) + get_logs_range(ep, mid + 1, to, topics, address, tries, depth)
    last = None
    for i in range(tries):
        try:
            res = ep.call("eth_getLogs", [{"address": address, "fromBlock": hex(frm), "toBlock": hex(to), "topics": topics}])
            if len(res) >= SAFE_RESULT_CAP and to > frm:
                mid = (frm + to) // 2
                return get_logs_range(ep, frm, mid, topics, address, tries, depth + 1) + get_logs_range(ep, mid + 1, to, topics, address, tries, depth + 1)
            for lg in res:
                b = int(lg["blockNumber"], 16)
                if b < frm or b > to:
                    raise RpcError("log outside requested range", kind="other")
                if lg.get("removed"):
                    raise RpcError("removed log returned", kind="other")
            return res
        except RpcError as e:
            last = e
            if e.kind == "archive":
                raise
            if e.kind == "range" and (to - frm + 1) <= ep.min_bisect:
                raise
            if e.kind == "range" or (e.kind in ("http", "other") and i >= 1 and to > frm):
                if to > frm and (to - frm + 1) > ep.min_bisect:
                    mid = (frm + to) // 2
                    return get_logs_range(ep, frm, mid, topics, address, tries, depth + 1) + get_logs_range(ep, mid + 1, to, topics, address, tries, depth + 1)
            time.sleep(min(60, (2 ** i) * (1.0 + random.random())))
    raise last


# ----------------------------------------------------------------------------------------------------------------
# decoding helpers
def words(data_hex):
    d = data_hex[2:] if data_hex.startswith("0x") else data_hex
    return [d[i:i + 64] for i in range(0, len(d), 64)]


def u(w):
    return int(w, 16)


def s(w, bits=256):
    v = int(w, 16)
    if v >= 1 << 255:
        v -= 1 << 256
    return v


def addr_topic(t):
    return "0x" + t[-40:].lower()


def addr_word(w):
    return "0x" + w[-40:].lower()


INIT_COLUMNS = ["block_number", "tx_hash", "tx_index", "log_index", "pool_id", "currency0", "currency1", "fee_raw", "tick_spacing",
                "hooks", "sqrt_price_x96", "tick", "dynamic_fee"] + HOOK_FLAG_COLUMNS


def base_fields(lg):
    return [str(int(lg["blockNumber"], 16)), lg["transactionHash"].lower(), str(int(lg["transactionIndex"], 16)), str(int(lg["logIndex"], 16))]


def decode_initialize(lg):
    t = lg["topics"]
    assert t[0].lower() == T_INITIALIZE and len(t) == 4
    w = words(lg["data"])
    assert len(w) == 5, "Initialize data words %d" % len(w)
    fee = u(w[0])
    hooks = addr_word(w[2])
    return base_fields(lg) + [t[1].lower(), addr_topic(t[2]), addr_topic(t[3]), str(fee), str(s(w[1])), hooks, str(u(w[3])), str(s(w[4])),
                              "1" if fee == DYNAMIC_FEE_FLAG else "0"] + hook_flags(hooks)


SWAP_COLUMNS = ["block_number", "tx_hash", "tx_index", "log_index", "pool_id", "sender", "amount0", "amount1", "sqrt_price_x96", "liquidity", "tick", "fee"]
MODIFY_COLUMNS = ["block_number", "tx_hash", "tx_index", "log_index", "pool_id", "sender", "tick_lower", "tick_upper", "liquidity_delta", "salt"]
DONATE_COLUMNS = ["block_number", "tx_hash", "tx_index", "log_index", "pool_id", "sender", "amount0", "amount1"]


def decode_activity(lg):
    """Returns (kind, row) for Swap / ModifyLiquidity / Donate."""
    t = lg["topics"]
    t0 = t[0].lower()
    w = words(lg["data"])
    if t0 == T_SWAP:
        assert len(w) == 6
        return "swap", base_fields(lg) + [t[1].lower(), addr_topic(t[2]), str(s(w[0])), str(s(w[1])), str(u(w[2])), str(u(w[3])), str(s(w[4])), str(u(w[5]))]
    if t0 == T_MODIFY:
        assert len(w) == 4
        return "modify", base_fields(lg) + [t[1].lower(), addr_topic(t[2]), str(s(w[0])), str(s(w[1])), str(s(w[2])), "0x" + w[3].lower()]
    if t0 == T_DONATE:
        assert len(w) == 2
        return "donate", base_fields(lg) + [t[1].lower(), addr_topic(t[2]), str(u(w[0])), str(u(w[1]))]
    raise ValueError("unexpected topic0 %s" % t0)


# ----------------------------------------------------------------------------------------------------------------
# files
def atomic_write_rows_gz(path, rows, header=None):
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", newline="", compresslevel=6) as f:
        w = csv.writer(f, lineterminator="\n")
        if header:
            w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


def read_rows_gz(path):
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.reader(f))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


class PartWriter:
    """Writes gzip CSV parts named <prefix>-part-0001.csv.gz ... each <= max_bytes compressed (rotation only at caller-chosen
    boundaries via maybe_rotate(), so each part covers a clean block range)."""

    def __init__(self, out_dir, prefix, header, max_bytes=85_000_000):
        self.out_dir, self.prefix, self.header, self.max_bytes = out_dir, prefix, header, max_bytes
        self.parts = []
        self.n = 0
        self.raw = None
        self._open()

    def _open(self):
        self.n += 1
        self.path = os.path.join(self.out_dir, "%s-part-%04d.csv.gz" % (self.prefix, self.n))
        self.raw = open(self.path + ".tmp", "wb")
        self.gz = gzip.GzipFile(fileobj=self.raw, mode="wb", compresslevel=6)
        self.txt = io.TextIOWrapper(self.gz, encoding="utf-8", newline="")
        self.w = csv.writer(self.txt, lineterminator="\n")
        self.w.writerow(self.header)
        self.rows = 0
        self.first_block = None
        self.last_block = None

    def write_block_range(self, rows, range_from, range_to):
        if self.first_block is None:
            self.first_block = range_from
        self.last_block = range_to
        self.w.writerows(rows)
        self.rows += len(rows)

    def size(self):
        self.txt.flush()
        return self.raw.tell()

    def maybe_rotate(self):
        if self.size() >= self.max_bytes:
            self._close()
            self._open()

    def _close(self):
        self.txt.flush()
        self.txt.detach()
        self.gz.close()
        self.raw.close()
        os.replace(self.path + ".tmp", self.path)
        self.parts.append({"file": os.path.basename(self.path), "rows": self.rows, "block_from": self.first_block, "block_to": self.last_block,
                           "bytes": os.path.getsize(self.path), "sha256": sha256_file(self.path)})

    def close(self):
        self._close()
        return self.parts


SENTINEL_DIR = "/home/user/dapparb/research-material/.sentinels"


def write_sentinel(name, ok, text):
    os.makedirs(SENTINEL_DIR, exist_ok=True)
    p = os.path.join(SENTINEL_DIR, "%s.%s" % (name, "DONE" if ok else "FAILED"))
    with open(p + ".tmp", "w") as f:
        f.write(text if text.endswith("\n") else text + "\n")
    os.replace(p + ".tmp", p)
    return p


# ----------------------------------------------------------------------------------------------------------------
# PoolId = keccak256(abi.encode(PoolKey)) (v4-core PoolIdLibrary); used as an integrity check on decoded Initialize logs
from Crypto.Hash import keccak as _keccak


def keccak_hex(b: bytes) -> str:
    k = _keccak.new(digest_bits=256)
    k.update(b)
    return "0x" + k.hexdigest()


def pool_id_of(currency0, currency1, fee, tick_spacing, hooks) -> str:
    enc = bytes.fromhex(currency0[2:].rjust(64, "0")) + bytes.fromhex(currency1[2:].rjust(64, "0")) + int(fee).to_bytes(32, "big") \
        + (int(tick_spacing) % (1 << 256)).to_bytes(32, "big") + bytes.fromhex(hooks[2:].rjust(64, "0"))
    return keccak_hex(enc)
