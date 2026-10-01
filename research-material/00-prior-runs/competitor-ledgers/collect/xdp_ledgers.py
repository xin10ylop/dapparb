#!/usr/bin/env python3
"""Raw per-block balance ledgers + receipts for two XDP/USDC senders (Base, chain id 8453).

Fills the 00-prior-runs gap "ledgers of XDP senders 0x000000c5... and 0x3be22b31... computed but not saved".
Same selection as ledger_0x778951 / ledger_0x0190f0 (see 00-prior-runs/MANIFEST.md, competitor-ledgers/):
  - input: competitor-ledgers/arbers_XDP.json.gz  ({sender: [[block, tx_hash, max_priority_fee_gwei, to], ...]})
  - per sender: the 60 rows with the highest block numbers
  - for every distinct block b among them, at block tags b-1 and b: ETH (eth_getBalance) and
    WETH / USDC / XDP balanceOf(address) (eth_call) of the EOA and of every distinct `to` of those 60 txs
  - eth_getTransactionReceipt of each of the 60 txs
Values are stored RAW (base-10 integer strings in the token's smallest unit). Nothing is converted, summed or differenced.

Collect-only. Resumable: every successful JSON-RPC result is appended to a cache file (collect/state/) and reused on
re-run; the outputs are written only when every call has a valid result.

Usage:  python3 xdp_ledgers.py [--smoke]        (run from anywhere; paths are relative to this file)
"""
import csv
import gzip
import io
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER_DIR = os.path.dirname(HERE)  # competitor-ledgers/
INPUT = os.path.join(LEDGER_DIR, "arbers_XDP.json.gz")
STATE_DIR = os.path.join(HERE, "state")
CACHE = os.path.join(STATE_DIR, "xdp_ledgers.cache.jsonl")

RPC = "https://base-mainnet.public.blastapi.io"  # archive eth_getBalance / eth_call / receipts
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
MAX_INFLIGHT = 2      # <= 4 in-flight per endpoint (other sessions may also use blastapi)
BATCH = 25
LAST_N = 60

SENDERS = {
    "0x000000c557fa9a96d66cd6371abde62d879d0e61": "0x000000c5",
    "0x3be22b314654c396a12c5e8d79abdd65aac3caaf": "0x3be22b31",
}
ASSETS = [  # (label, token address or None for native ETH)
    ("ETH", None),
    ("WETH", "0x4200000000000000000000000000000000000006"),
    ("USDC", "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"),
    ("XDP", "0x07b3d902783c3c12b077508c3b5c00113d1291d0"),
]
BALANCE_OF = "0x70a08231"  # balanceOf(address)

for _v in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
    if not os.environ.get(_v) and os.path.exists("/root/.ccr/ca-bundle.crt"):
        os.environ[_v] = "/root/.ccr/ca-bundle.crt"

_log_lock = threading.Lock()


def log(*a):
    with _log_lock:
        print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), *a, flush=True)


# ---------------------------------------------------------------------------------------------------------------
# cache (append-only jsonl: {"k": key, "r": result})
_cache = {}
_cache_lock = threading.Lock()


def cache_load():
    if not os.path.exists(CACHE):
        return
    with open(CACHE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue  # torn last line after a kill
            _cache[o["k"]] = o["r"]


def cache_put(items):
    with _cache_lock:
        with open(CACHE, "a") as f:
            for k, r in items:
                _cache[k] = r
                f.write(json.dumps({"k": k, "r": r}, separators=(",", ":")) + "\n")


# ---------------------------------------------------------------------------------------------------------------
_session_local = threading.local()


def session():
    s = getattr(_session_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})
        _session_local.s = s
    return s


STATS = {"http_req": 0, "http_err": 0, "rpc_item_err": 0, "invalid": 0}
_stats_lock = threading.Lock()


def bump(k, n=1):
    with _stats_lock:
        STATS[k] += n


def valid(kind, r):
    if kind == "bal":
        return isinstance(r, str) and r.startswith("0x") and len(r) > 2
    if kind == "call":
        return isinstance(r, str) and r.startswith("0x") and len(r) == 66
    if kind == "rcpt":
        return isinstance(r, dict) and r.get("transactionHash") and r.get("blockNumber")
    return False


def run_batch(calls):
    """calls: list of (key, kind, method, params). Retries until every item has a valid result."""
    pending = list(calls)
    attempt = 0
    while pending:
        attempt += 1
        body = [{"jsonrpc": "2.0", "id": i, "method": m, "params": p} for i, (_, _, m, p) in enumerate(pending)]
        got = {}
        try:
            bump("http_req")
            resp = session().post(RPC, data=json.dumps(body), timeout=60)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise RuntimeError(f"HTTP {resp.status_code}")
            resp.raise_for_status()
            out = resp.json()
            if isinstance(out, dict):
                raise RuntimeError(f"non-batch response: {str(out)[:200]}")
            for o in out:
                if "error" in o:
                    bump("rpc_item_err")
                    if attempt <= 3 or attempt % 10 == 0:
                        log("rpc item error", pending[o["id"]][0], json.dumps(o["error"])[:200])
                    continue
                key, kind, _, _ = pending[o["id"]]
                r = o.get("result")
                if valid(kind, r):
                    got[o["id"]] = r
                else:
                    bump("invalid")
                    log("invalid result", key, str(r)[:120])
        except Exception as e:  # noqa: BLE001
            bump("http_err")
            log(f"batch attempt {attempt} failed ({len(pending)} items): {str(e)[:200]}")
        if got:
            cache_put([(pending[i][0], r) for i, r in got.items()])
        pending = [c for i, c in enumerate(pending) if i not in got]
        if pending:
            if attempt >= 200:
                raise RuntimeError(f"giving up after {attempt} attempts; {len(pending)} items pending")
            time.sleep(min(30.0, 0.5 * (2 ** min(attempt, 6))) * (0.5 + random.random()))


# ---------------------------------------------------------------------------------------------------------------
def select(arbers, sender):
    rows = arbers[sender]
    rows_sorted = sorted(rows, key=lambda r: r[0])  # stable: file order within a block
    sel = rows_sorted[-LAST_N:]
    if len(rows_sorted) > LAST_N:
        # the cut must not fall inside a block (otherwise "last 60" would be ambiguous)
        assert rows_sorted[-LAST_N - 1][0] < sel[0][0], "tie at the 60-tx boundary"
    return sel


def plan(arbers):
    out = {}
    for sender, short in SENDERS.items():
        sel = select(arbers, sender)
        tos = sorted({r[3].lower() for r in sel})
        addrs = [(sender, "eoa")] + [(t, "to_contract") for t in tos if t != sender]
        blocks = sorted({int(r[0]) for r in sel})
        out[sender] = {"short": short, "sel": sel, "addrs": addrs, "blocks": blocks}
    return out


def bal_key(addr, asset, qb):
    return f"bal|{addr}|{asset}|{qb}"


def all_calls(p):
    calls = {}
    for sender, d in p.items():
        for b in d["blocks"]:
            for qb in (b - 1, b):
                for addr, _ in d["addrs"]:
                    for label, tok in ASSETS:
                        k = bal_key(addr, label, qb)
                        if k in calls:
                            continue
                        if tok is None:
                            calls[k] = (k, "bal", "eth_getBalance", [addr, hex(qb)])
                        else:
                            data = BALANCE_OF + addr[2:].rjust(64, "0")
                            calls[k] = (k, "call", "eth_call", [{"to": tok, "data": data}, hex(qb)])
        for r in d["sel"]:
            k = f"rcpt|{r[1].lower()}"
            calls[k] = (k, "rcpt", "eth_getTransactionReceipt", [r[1].lower()])
    return calls


def hx(v):
    """hex quantity -> base-10 string ('' if absent)."""
    if v is None:
        return ""
    return str(int(v, 16))


def block_ts(rc):
    """blockTimestamp: top-level receipt field if present, else the (identical) value carried by the receipt's logs
    (blastapi returns it only inside log entries). None if neither exists."""
    if rc.get("blockTimestamp"):
        return rc["blockTimestamp"]
    ts = {lg.get("blockTimestamp") for lg in (rc.get("logs") or []) if lg.get("blockTimestamp")}
    assert len(ts) <= 1, f"log blockTimestamps differ in {rc.get('transactionHash')}"
    return ts.pop() if ts else None


def write_csv_gz(path, header, rows):
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    os.replace(tmp, path)


RCPT_HEADER = [
    "sender", "tx_hash", "input_block", "block_number", "block_hash", "block_timestamp", "transaction_index",
    "from", "to", "type", "status", "gas_used", "cumulative_gas_used", "effective_gas_price",
    "l1_fee", "l1_gas_used", "l1_gas_price", "l1_base_fee_scalar", "l1_blob_base_fee", "l1_blob_base_fee_scalar",
    "logs_count", "input_max_priority_fee_gwei",
]
LEDGER_HEADER = ["block", "block_tag", "queried_block", "address", "address_role", "asset", "asset_address", "balance"]


def write_outputs(p):
    for sender, d in p.items():
        short = d["short"]
        # ledger
        rows = []
        for b in d["blocks"]:
            for tag, qb in (("b-1", b - 1), ("b", b)):
                for addr, role in d["addrs"]:
                    for label, tok in ASSETS:
                        r = _cache[bal_key(addr, label, qb)]
                        rows.append([b, tag, qb, addr, role, label, tok or "", str(int(r, 16))])
        lp = os.path.join(LEDGER_DIR, f"ledger_{short}.raw.csv.gz")
        write_csv_gz(lp, LEDGER_HEADER, rows)
        log(f"wrote {lp}: {len(rows)} rows, {len(d['blocks'])} blocks, {len(d['addrs'])} addresses")
        # receipts
        rrows = []
        full = []
        for blk, txh, tip, to in sorted(d["sel"], key=lambda r: r[0]):
            rc = _cache[f"rcpt|{txh.lower()}"]
            full.append(rc)
            rrows.append([
                sender, txh.lower(), blk, hx(rc.get("blockNumber")), (rc.get("blockHash") or "").lower(),
                hx(block_ts(rc)), hx(rc.get("transactionIndex")),
                (rc.get("from") or "").lower(), (rc.get("to") or "").lower(), hx(rc.get("type")), hx(rc.get("status")),
                hx(rc.get("gasUsed")), hx(rc.get("cumulativeGasUsed")), hx(rc.get("effectiveGasPrice")),
                hx(rc.get("l1Fee")), hx(rc.get("l1GasUsed")), hx(rc.get("l1GasPrice")), hx(rc.get("l1BaseFeeScalar")),
                hx(rc.get("l1BlobBaseFee")), hx(rc.get("l1BlobBaseFeeScalar")), len(rc.get("logs") or []), repr(tip),
            ])
        rp = os.path.join(LEDGER_DIR, f"receipts_{short}.csv.gz")
        write_csv_gz(rp, RCPT_HEADER, rrows)
        fp = os.path.join(LEDGER_DIR, f"receipts_{short}.full.jsonl.gz")
        tmp = fp + ".tmp"
        with gzip.open(tmp, "wt") as f:
            for rc in full:
                f.write(json.dumps(rc, separators=(",", ":"), sort_keys=True) + "\n")
        os.replace(tmp, fp)
        log(f"wrote {rp}: {len(rrows)} rows; {fp}: {len(full)} receipts")


def checks(p):
    """Descriptive consistency checks (logged only)."""
    for sender, d in p.items():
        mism = 0
        for blk, txh, _, to in d["sel"]:
            rc = _cache[f"rcpt|{txh.lower()}"]
            if int(rc["blockNumber"], 16) != int(blk) or (rc.get("from") or "").lower() != sender \
                    or (rc.get("to") or "").lower() != to.lower():
                mism += 1
                log("receipt/input mismatch", txh, rc.get("blockNumber"), rc.get("from"), rc.get("to"), blk, to)
        st = {}
        for blk, txh, _, _ in d["sel"]:
            s = _cache[f"rcpt|{txh.lower()}"].get("status")
            st[s] = st.get(s, 0) + 1
        missing_l1 = sum(1 for _, txh, _, _ in d["sel"] if _cache[f"rcpt|{txh.lower()}"].get("l1Fee") is None)
        shared = sum(1 for b in d["blocks"] if (b - 1) in set(d["blocks"]))
        log(f"{d['short']}: txs {len(d['sel'])}, blocks {len(d['blocks'])} ({d['blocks'][0]}..{d['blocks'][-1]}), "
            f"addresses {[a for a, _ in d['addrs']]}, receipt/input mismatches {mism}, status counts {st}, "
            f"receipts without l1Fee {missing_l1}, blocks whose b-1 is also a selected block {shared}")


def main():
    smoke = "--smoke" in sys.argv
    os.makedirs(STATE_DIR, exist_ok=True)
    log("start", "smoke" if smoke else "full", "rpc", RPC)
    arbers = json.load(gzip.open(INPUT, "rt"))
    p = plan(arbers)
    cache_load()
    calls = all_calls(p)
    if smoke:
        keys = list(calls)[:10] + [k for k in calls if k.startswith("rcpt|")][:2]
        calls = {k: calls[k] for k in keys}
    todo = [c for k, c in calls.items() if k not in _cache]
    log(f"calls total {len(calls)}, cached {len(calls) - len(todo)}, to fetch {len(todo)}")
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    with ThreadPoolExecutor(max_workers=MAX_INFLIGHT) as ex:
        for i, _ in enumerate(ex.map(run_batch, batches)):
            if (i + 1) % 10 == 0 or i + 1 == len(batches):
                log(f"batches done {i + 1}/{len(batches)}")
    missing = [k for k in calls if k not in _cache or not valid(calls[k][1], _cache[k])]
    log(f"verification: {len(calls)} calls, {len(missing)} missing/invalid; stats {STATS}")
    if missing:
        log("INCOMPLETE; rerun to resume", missing[:10])
        sys.exit(2)
    if smoke:
        for k in keys:
            log("smoke", k, json.dumps(_cache[k])[:300])
        log("smoke done")
        return
    checks(p)
    write_outputs(p)
    log("done")


if __name__ == "__main__":
    main()
