#!/usr/bin/env python3
"""On-chain arbitrage census collector for one EVM chain (SHARED DEFINITION of the research-material task).

For every block in a pinned, contiguous, recent window it calls eth_getBlockReceipts(block) and
eth_getBlockByNumber(block, false) and writes (under <out_dir>):

  blocks.csv.gz                  one row per block
  txs-NNN.csv.gz                 one row per transaction receipt
  reverted-NNN.csv.gz            one row per status-0 transaction
  candidates-NNN.jsonl.gz        one line per tx meeting criterion A or B (all logs + full receipt verbatim)
  topic0-counts.csv.gz           per topic0 (or anonymous-log emitter) log/tx counts in the window + first example
  extra-<name>.jsonl.gz          (chain-specific) every log emitted by configured addresses, verbatim
  window.json                    pinned window, endpoints, measured block interval, counts, checks
  gaps.csv                       blocks that could not be fetched after all retries (header only if none)
  swap-topics.csv                (updated) verified_example_* filled from the first matching log in the window

Criterion A: >= 2 logs whose topic0 is a KNOWN SWAP TOPIC (swap-topics.csv, match_rule=topic0), or which are
             zero-topic logs emitted by an address listed with match_rule=log0_address (Ekubo Core swaps).
Criterion B: (not A) >= 3 ERC-20 Transfer logs (topic0 0xddf252ad..., exactly 3 topics) emitted by
             >= 2 distinct token contracts.

Resumable: work is done in segments (contiguous block ranges) under <out_dir>/_segments/; a segment is
complete when its DONE marker exists; incomplete segments are deleted and redone on restart.
Sentinel: /home/user/dapparb/research-material/.sentinels/<SENTINEL>.DONE or .FAILED

usage: python3 census.py --chain arbitrum --out <out_dir> [--smoke N] [--workers 4]
"""
import argparse, csv, datetime, gzip, io, json, os, random, shutil, sys, threading, time, traceback
import requests

SENTINEL_DIR = "/home/user/dapparb/research-material/.sentinels"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "content-type": "application/json"}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PART_LIMIT = 85 * 1024 * 1024  # bytes per final part (hard rule: <= 90 MB)

CHAINS = {
    "arbitrum": dict(chain_id=42161, primary="https://arbitrum-one-rpc.publicnode.com",
                     fallbacks=["https://arbitrum.drpc.org"], window_s=3600, end_tag="latest", head_margin=40,
                     batch=20, seg_blocks=1000, nominal_interval=0.25, sentinel="EVM_CENSUS_ARBITRUM",
                     extra_logs={"timeboost-auction-logs": ["0x5fcb496a31b7ae91e7c9078ec662bd7a55cd3079"]},
                     extra_data_text=False),
    "optimism": dict(chain_id=10, primary="https://optimism-rpc.publicnode.com",
                     fallbacks=["https://optimism.drpc.org"], window_s=3600, end_tag="latest", head_margin=5,
                     batch=2, seg_blocks=300, nominal_interval=2.0, sentinel="EVM_CENSUS_OPTIMISM",
                     extra_logs={}, extra_data_text=False),
    "unichain": dict(chain_id=130, primary="https://unichain-rpc.publicnode.com",
                     fallbacks=["https://unichain.drpc.org", "https://mainnet.unichain.org"], window_s=3600,
                     end_tag="latest", head_margin=10, batch=8, seg_blocks=600, nominal_interval=1.0,
                     sentinel="EVM_CENSUS_UNICHAIN", extra_logs={}, extra_data_text=False),
    "ethereum": dict(chain_id=1, primary="https://ethereum-rpc.publicnode.com",
                     fallbacks=["https://eth.drpc.org"], window_s=21600, end_tag="latest", head_margin=3,
                     batch=1, seg_blocks=100, nominal_interval=12.0, sentinel="EVM_CENSUS_ETHEREUM",
                     extra_logs={}, extra_data_text=True),
    "polygon": dict(chain_id=137, primary="https://polygon-bor-rpc.publicnode.com",
                    fallbacks=["https://polygon.drpc.org"], window_s=3600, end_tag="finalized", head_margin=0,
                    batch=1, seg_blocks=150, nominal_interval=2.0, sentinel="EVM_CENSUS_POLYGON",
                    extra_logs={}, extra_data_text=False),
}

BLOCK_COLS = ["block_number", "timestamp", "base_fee_per_gas", "gas_used", "gas_limit", "tx_count", "miner",
              "extra_data", "block_hash", "parent_hash", "receipts_count"]
TX_COLS = ["block_number", "tx_index", "tx_hash", "from", "to", "status", "gas_used", "effective_gas_price",
           "type", "logs_count", "contract_address", "l1_fee", "gas_used_for_l1", "timeboosted", "in_block_tx_list"]
REV_COLS = ["block_number", "tx_index", "tx_hash", "from", "to", "gas_used", "effective_gas_price", "logs_count",
            "type", "l1_fee", "gas_used_for_l1", "timeboosted"]

_tls = threading.local()


def log(*a):
    print(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), *a, flush=True)


def session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update(UA)
        _tls.s = s
    return s


class RpcError(Exception):
    def __init__(self, msg, kind="retry"):
        super().__init__(msg)
        self.kind = kind  # retry | refused | toolarge


def classify_error(e):
    m = json.dumps(e) if not isinstance(e, str) else e
    ml = m.lower()
    if "archive" in ml or "personal token" in ml or "not supported on free plan" in ml or "pruned" in ml or "missing trie node" in ml:
        return "refused"
    if "too large" in ml or "limit exceeded" in ml or "response size" in ml or "batch" in ml and "limit" in ml:
        return "toolarge"
    return "retry"


def post(url, payload, timeout=90):
    try:
        r = session().post(url, data=json.dumps(payload), timeout=timeout)
    except requests.RequestException as ex:
        raise RpcError("net %s: %s" % (url, str(ex)[:200]))
    if r.status_code == 429 or r.status_code >= 500:
        raise RpcError("http %d %s: %s" % (r.status_code, url, r.text[:200]))
    if r.status_code in (413,):
        raise RpcError("http 413 %s" % url, "toolarge")
    try:
        j = r.json()
    except ValueError:
        raise RpcError("bad json http %d %s: %s" % (r.status_code, url, r.text[:200]))
    if isinstance(j, dict) and "error" in j and r.status_code != 200 and not isinstance(payload, list):
        raise RpcError("http %d %s: %s" % (r.status_code, url, str(j["error"])[:300]), classify_error(j["error"]))
    if isinstance(payload, list) and isinstance(j, dict):
        # batch rejected as a whole
        raise RpcError("batch rejected %s: %s" % (url, str(j.get("error"))[:300]), classify_error(j.get("error") or ""))
    return j


def rpc1(url, method, params):
    j = post(url, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    if "error" in j:
        raise RpcError("%s %s: %s" % (url, method, str(j["error"])[:300]), classify_error(j["error"]))
    return j.get("result")


def hx(v):
    if v is None or v == "":
        return None
    return int(v, 16)


def sdec(v):
    """hex quantity -> base-10 string ('' if absent)"""
    if v is None or v == "":
        return ""
    return str(int(v, 16))


class Fetcher:
    def __init__(self, cfg):
        self.cfg = cfg
        self.primary = cfg["primary"]
        self.fallbacks = cfg["fallbacks"]
        self.stats_lock = threading.Lock()
        self.req_count = {}
        self.err_count = {}

    def _count(self, url, err=None):
        with self.stats_lock:
            self.req_count[url] = self.req_count.get(url, 0) + 1
            if err:
                k = "%s|%s" % (url, err)
                self.err_count[k] = self.err_count.get(k, 0) + 1

    @staticmethod
    def validate(b, blk, rcpts):
        if blk is None:
            return "block result null"
        if rcpts is None:
            return "receipts result null"
        if hx(blk["number"]) != b:
            return "block number mismatch"
        h = blk["hash"].lower()
        for r in rcpts:
            if (r.get("blockHash") or "").lower() != h:
                return "receipt blockHash != block hash (reorg between calls?)"
            if hx(r.get("blockNumber")) != b:
                return "receipt blockNumber mismatch"
        rh = set(r["transactionHash"].lower() for r in rcpts)
        missing = [t for t in blk["transactions"] if t.lower() not in rh]
        if missing:
            return "block tx without receipt (%d)" % len(missing)
        return None

    def fetch_batch_once(self, url, blocks):
        payload = []
        for i, b in enumerate(blocks):
            payload.append({"jsonrpc": "2.0", "id": 2 * i, "method": "eth_getBlockReceipts", "params": [hex(b)]})
            payload.append({"jsonrpc": "2.0", "id": 2 * i + 1, "method": "eth_getBlockByNumber", "params": [hex(b), False]})
        j = post(url, payload if len(payload) > 1 else payload[0])
        if isinstance(j, dict):
            j = [j]
        byid = {x.get("id"): x for x in j}
        out, errs = {}, {}
        for i, b in enumerate(blocks):
            a, c = byid.get(2 * i), byid.get(2 * i + 1)
            if a is None or c is None:
                errs[b] = ("retry", "missing item in batch response")
                continue
            if "error" in a or "error" in c:
                e = a.get("error") or c.get("error")
                errs[b] = (classify_error(e), str(e)[:300])
                continue
            v = self.validate(b, c.get("result"), a.get("result"))
            if v:
                errs[b] = ("retry", v)
                continue
            out[b] = (c["result"], a["result"])
        return out, errs

    def fetch_blocks(self, blocks, max_attempts=14):
        """returns ({block: (blk, receipts, endpoint)}, {block: last_error})"""
        done = {}
        pending = list(blocks)
        attempt = 0
        refused = set()
        last_err = {}
        order = [self.primary] + self.fallbacks
        while pending and attempt < max_attempts:
            # endpoint rotation: primary first; alternate with fallbacks after 2 failed attempts;
            # a block the primary refused (archive / range) goes straight to a fallback
            url = self.primary if attempt < 2 else order[attempt % len(order)]
            # after 3 failed attempts, fetch one block per request (handles oversized batches)
            use_batch = pending if attempt < 3 else pending[:1]
            if url == self.primary and any(b in refused for b in use_batch):
                url = self.fallbacks[attempt % len(self.fallbacks)]
            try:
                out, errs = self.fetch_batch_once(url, use_batch)
                self._count(url)
            except RpcError as ex:
                self._count(url, ex.kind)
                out, errs = {}, {b: (ex.kind, str(ex)) for b in use_batch}
            for b, (bk, rc) in out.items():
                done[b] = (bk, rc, url)
            for b, (kind, msg) in errs.items():
                last_err[b] = "%s @ %s: %s" % (kind, url, msg)
                if kind == "refused":
                    refused.add(b)
                with self.stats_lock:
                    k = "%s|item-%s" % (url, kind)
                    self.err_count[k] = self.err_count.get(k, 0) + 1
            pending = [b for b in pending if b not in done]
            if pending and not out:
                # no progress in this attempt -> count it and back off (no sleep for pure refusals)
                attempt += 1
                if not (errs and all(k == "refused" for k, _ in errs.values())):
                    time.sleep(min(60.0, 0.5 * (1.7 ** attempt)) + random.random())
        return done, {b: last_err.get(b, "unknown") for b in pending}


def open_gz(path):
    raw = open(path, "wb")
    gz = gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=6)
    return raw, io.TextIOWrapper(gz, encoding="utf-8", newline="")


class SegmentWriter:
    def __init__(self, segdir, extra_names):
        os.makedirs(segdir, exist_ok=True)
        self.files = {}
        for k in ["blocks", "txs", "reverted"]:
            self.files[k] = open_gz(os.path.join(segdir, k + ".csv.gz"))
        self.files["candidates"] = open_gz(os.path.join(segdir, "candidates.jsonl.gz"))
        for n in extra_names:
            self.files["extra-" + n] = open_gz(os.path.join(segdir, "extra-" + n + ".jsonl.gz"))
        self.w = {k: csv.writer(self.files[k][1], lineterminator="\n") for k in ["blocks", "txs", "reverted"]}

    def close(self):
        for raw, t in self.files.values():
            t.close()
            raw.close()


def load_swap_topics(chain_dir):
    topics, log0_addrs = {}, {}
    with open(os.path.join(chain_dir, "swap-topics.csv")) as f:
        for r in csv.DictReader(f):
            if r["match_rule"] == "topic0":
                topics[r["topic0"].lower()] = r["signature"]
            elif r["match_rule"] == "log0_address":
                for a in r["match_address"].split(";"):
                    log0_addrs[a.strip().lower()] = r["protocol"]
    return topics, log0_addrs


def process_block(cfg, b, blk, rcpts, swap_topics, log0_addrs, sw, st, extra_addr):
    ts = hx(blk["timestamp"])
    in_list = set(t.lower() for t in blk["transactions"])
    row = [b, ts, sdec(blk.get("baseFeePerGas")), sdec(blk.get("gasUsed")), sdec(blk.get("gasLimit")),
           len(blk["transactions"]), (blk.get("miner") or "").lower(), (blk.get("extraData") or "").lower(),
           blk["hash"].lower(), blk["parentHash"].lower(), len(rcpts)]
    if cfg["extra_data_text"]:
        try:
            row.append(bytes.fromhex((blk.get("extraData") or "0x")[2:]).decode("utf-8", errors="backslashreplace"))
        except ValueError:
            row.append("")
    sw.w["blocks"].writerow(row)
    st["blocks"] += 1
    st["receipts_not_in_block_tx_list"] += sum(1 for r in rcpts if r["transactionHash"].lower() not in in_list)
    tstats = st["topics"]
    for r in rcpts:
        txh = r["transactionHash"].lower()
        idx = hx(r["transactionIndex"])
        status = hx(r.get("status")) if r.get("status") is not None else ""
        logs = r.get("logs") or []
        frm = (r.get("from") or "").lower()
        to = (r.get("to") or "").lower()
        tb = r.get("timeboosted")
        tbs = "" if tb is None else ("true" if tb else "false")
        l1fee = sdec(r.get("l1Fee"))
        gl1 = sdec(r.get("gasUsedForL1"))
        typ = sdec(r.get("type"))
        sw.w["txs"].writerow([b, idx, txh, frm, to, status, sdec(r.get("gasUsed")), sdec(r.get("effectiveGasPrice")),
                              typ, len(logs), (r.get("contractAddress") or "").lower(), l1fee, gl1, tbs,
                              "true" if txh in in_list else "false"])
        st["txs"] += 1
        if status == 0:
            sw.w["reverted"].writerow([b, idx, txh, frm, to, sdec(r.get("gasUsed")), sdec(r.get("effectiveGasPrice")),
                                       len(logs), typ, l1fee, gl1, tbs])
            st["reverted"] += 1
        n_swap, matched, n_tr, tr_tokens = 0, [], 0, set()
        seen_keys = set()
        for lg in logs:
            topics = lg.get("topics") or []
            addr = (lg.get("address") or "").lower()
            key = topics[0].lower() if topics else "log0:" + addr
            ts_ = tstats.get(key)
            if ts_ is None:
                ts_ = tstats[key] = {"n_logs": 0, "n_txs": 0, "addrs": set(), "ex_tx": txh, "ex_block": b, "ex_addr": addr}
            ts_["n_logs"] += 1
            ts_["addrs"].add(addr)
            if key not in seen_keys:
                ts_["n_txs"] += 1
                seen_keys.add(key)
            if topics:
                t0 = topics[0].lower()
                if t0 in swap_topics:
                    n_swap += 1
                    if t0 not in matched:
                        matched.append(t0)
                elif t0 == TRANSFER and len(topics) == 3:
                    n_tr += 1
                    tr_tokens.add(addr)
            elif addr in log0_addrs:
                n_swap += 1
                k0 = "log0:" + addr
                if k0 not in matched:
                    matched.append(k0)
            if addr in extra_addr:
                rec = {"block_number": b, "block_timestamp": ts, "tx_index": idx, "tx_hash": txh, "from": frm, "to": to,
                       "status": status, "log": lg}
                sw.files["extra-" + extra_addr[addr]][1].write(json.dumps(rec, separators=(",", ":")) + "\n")
                st["extra"][extra_addr[addr]] = st["extra"].get(extra_addr[addr], 0) + 1
        crit = None
        if n_swap >= 2:
            crit = "A"
        elif n_tr >= 3 and len(tr_tokens) >= 2:
            crit = "B"
        if crit:
            other = {k: v for k, v in r.items() if k != "logs"}
            rec = {"block_number": b, "block_timestamp": ts, "tx_index": idx, "tx_hash": txh, "from": frm, "to": to,
                   "status": status, "gas_used": sdec(r.get("gasUsed")),
                   "effective_gas_price": sdec(r.get("effectiveGasPrice")), "criterion": crit,
                   "derived": {"n_logs": len(logs), "n_swap_logs": n_swap, "swap_keys_matched": matched,
                               "n_erc20_transfer_logs": n_tr, "n_distinct_transfer_tokens": len(tr_tokens)},
                   "receipt": other, "logs": logs}
            sw.files["candidates"][1].write(json.dumps(rec, separators=(",", ":")) + "\n")
            st["candidates_" + crit] += 1


def new_stats():
    return {"blocks": 0, "txs": 0, "reverted": 0, "candidates_A": 0, "candidates_B": 0, "extra": {},
            "receipts_not_in_block_tx_list": 0, "topics": {}}


def stats_to_json(st):
    d = dict(st)
    d["topics"] = {k: {"n_logs": v["n_logs"], "n_txs": v["n_txs"], "addrs": sorted(v["addrs"]), "ex_tx": v["ex_tx"],
                       "ex_block": v["ex_block"], "ex_addr": v["ex_addr"]} for k, v in st["topics"].items()}
    return d


def pin_window(cfg, f):
    url = cfg["primary"]

    def ts_of(n):
        for i in range(10):
            try:
                return hx(rpc1(url, "eth_getBlockByNumber", [hex(n), False])["timestamp"])
            except Exception as ex:  # noqa
                log("pin_window retry", n, str(ex)[:200])
                time.sleep(2 + 2 * i)
        raise RuntimeError("cannot read timestamp of %d" % n)

    if cfg["end_tag"] == "finalized":
        end = hx(rpc1(url, "eth_getBlockByNumber", ["finalized", False])["number"])
        head = hx(rpc1(url, "eth_blockNumber", []))
    else:
        head = hx(rpc1(url, "eth_blockNumber", []))
        end = head - cfg["head_margin"]
    ts_end = ts_of(end)
    target = ts_end - cfg["window_s"]  # window = blocks with timestamp in (target, ts_end]
    step = int(cfg["window_s"] / cfg["nominal_interval"] * 1.3) + 10
    lo = end - step
    while ts_of(lo) > target:
        lo -= step
    hi = end  # ts(lo) <= target < ts(hi)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if ts_of(mid) > target:
            hi = mid
        else:
            lo = mid
    start = hi
    ts_start = ts_of(start)
    return {"chain": None, "head_at_pin": head, "end_tag": cfg["end_tag"], "head_margin": cfg["head_margin"],
            "start_block": start, "end_block": end, "start_timestamp": ts_start, "end_timestamp": ts_end,
            "window_rule": "all blocks with timestamp in (end_timestamp - %d s, end_timestamp]" % cfg["window_s"],
            "window_seconds_requested": cfg["window_s"],
            "pinned_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}


def segments_of(start, end, size):
    s = start
    while s <= end:
        e = min(end, s + size - 1)
        yield s, e
        s = e + 1


def run_segment(cfg, fetcher, s, e, segdir, swap_topics, log0_addrs, workers, gaps):
    from concurrent.futures import ThreadPoolExecutor
    extra_addr = {}
    for name, addrs in cfg["extra_logs"].items():
        for a in addrs:
            extra_addr[a.lower()] = name
    if os.path.exists(segdir):
        shutil.rmtree(segdir)
    sw = SegmentWriter(segdir, list(cfg["extra_logs"].keys()))
    st = new_stats()
    batches = []
    bs = cfg["batch"]
    b = s
    while b <= e:
        batches.append(list(range(b, min(e, b + bs - 1) + 1)))
        b += bs
    seg_gaps = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = []
        nxt = 0
        window = workers * 2
        while nxt < len(batches) and len(futs) < window:
            futs.append(ex.submit(fetcher.fetch_blocks, batches[nxt])); nxt += 1
        bi = 0
        while futs:
            done, failed = futs.pop(0).result()
            for blk_n in batches[bi]:
                if blk_n in done:
                    bk, rc, _ = done[blk_n]
                    process_block(cfg, blk_n, bk, rc, swap_topics, log0_addrs, sw, st, extra_addr)
                else:
                    seg_gaps.append((blk_n, failed.get(blk_n, "unknown")))
            bi += 1
            if nxt < len(batches):
                futs.append(ex.submit(fetcher.fetch_blocks, batches[nxt])); nxt += 1
    sw.close()
    st["gaps"] = [[g, r] for g, r in seg_gaps]
    with open(os.path.join(segdir, "stats.json"), "w") as f:
        json.dump(stats_to_json(st), f)
    open(os.path.join(segdir, "DONE"), "w").write("%d-%d\n" % (s, e))
    gaps.extend(seg_gaps)
    return st


def concat_parts(chain_dir, segdirs, seg_fname, out_prefix, ext, header, single=False):
    """byte-concatenate gzip members (header member first) into parts <= PART_LIMIT; returns list of files.
    A new part is opened only when the current part already holds data rows; an empty output is still a
    valid gzip file (empty member)."""
    outs = []
    st = {"f": None, "size": 0, "rows": False, "part": 0}

    def new_part():
        if st["f"]:
            st["f"].close()
        st["part"] += 1
        name = ("%s.%s" % (out_prefix, ext)) if single else ("%s-%03d.%s" % (out_prefix, st["part"], ext))
        st["f"] = open(os.path.join(chain_dir, name), "wb")
        outs.append(name)
        st["size"], st["rows"] = 0, False
        hb = gzip.compress((",".join(header) + "\n").encode()) if header is not None else gzip.compress(b"")
        st["f"].write(hb)
        st["size"] += len(hb)

    def put(data):
        if st["rows"] and not single and st["size"] + len(data) > PART_LIMIT:
            new_part()
        st["f"].write(data)
        st["size"] += len(data)
        st["rows"] = True

    new_part()
    for sd in segdirs:
        p = os.path.join(sd, seg_fname)
        if not os.path.exists(p):
            continue
        sz = os.path.getsize(p)
        if sz > PART_LIMIT // 2:
            # large segment file: re-stream its lines into ~4 MB (uncompressed) gzip members
            with gzip.open(p, "rt", encoding="utf-8", newline="") as fin:
                buf, bsz = [], 0
                for line in fin:
                    buf.append(line); bsz += len(line)
                    if bsz >= 4 * 1024 * 1024:
                        put(gzip.compress("".join(buf).encode(), 6)); buf, bsz = [], 0
                if buf:
                    put(gzip.compress("".join(buf).encode(), 6))
            continue
        with open(p, "rb") as fin:
            put(fin.read())
    st["f"].close()
    return outs


def count_lines(path):
    n = 0
    with gzip.open(path, "rb") as f:
        for _ in f:
            n += 1
    return n


def finalize(cfg, chain, chain_dir, win, fetcher, gaps_all):
    segroot = os.path.join(chain_dir, "_segments")
    segdirs = sorted([os.path.join(segroot, d) for d in os.listdir(segroot) if d.startswith("seg-")],
                     key=lambda d: (int(os.path.basename(d).split("-")[1]), int(os.path.basename(d).split("-")[2])))
    for sd in segdirs:
        if not os.path.exists(os.path.join(sd, "DONE")):
            raise RuntimeError("segment not complete at finalize: %s" % sd)
    tot = new_stats()
    tot["topics"] = {}
    gaps = []
    for sd in segdirs:
        s = json.load(open(os.path.join(sd, "stats.json")))
        for k in ["blocks", "txs", "reverted", "candidates_A", "candidates_B", "receipts_not_in_block_tx_list"]:
            tot[k] += s[k]
        for k, v in s["extra"].items():
            tot["extra"][k] = tot["extra"].get(k, 0) + v
        gaps.extend(s.get("gaps", []))
        for k, v in s["topics"].items():
            t = tot["topics"].get(k)
            if t is None:
                tot["topics"][k] = {"n_logs": v["n_logs"], "n_txs": v["n_txs"], "addrs": set(v["addrs"]),
                                    "ex_tx": v["ex_tx"], "ex_block": v["ex_block"], "ex_addr": v["ex_addr"]}
            else:
                t["n_logs"] += v["n_logs"]; t["n_txs"] += v["n_txs"]; t["addrs"].update(v["addrs"])
    bh = BLOCK_COLS + (["extra_data_text_derived"] if cfg["extra_data_text"] else [])
    files = {}
    files["blocks"] = concat_parts(chain_dir, segdirs, "blocks.csv.gz", "blocks", "csv.gz", bh, single=True)
    files["txs"] = concat_parts(chain_dir, segdirs, "txs.csv.gz", "txs", "csv.gz", TX_COLS)
    files["reverted"] = concat_parts(chain_dir, segdirs, "reverted.csv.gz", "reverted", "csv.gz", REV_COLS)
    files["candidates"] = concat_parts(chain_dir, segdirs, "candidates.jsonl.gz", "candidates", "jsonl.gz", None)
    for n in cfg["extra_logs"]:
        files["extra-" + n] = concat_parts(chain_dir, segdirs, "extra-%s.jsonl.gz" % n, "extra-" + n, "jsonl.gz", None, single=True)
    # verify line counts
    expect = {"blocks": tot["blocks"] + 1, "txs": tot["txs"] + len(files["txs"]),
              "reverted": tot["reverted"] + len(files["reverted"]),
              "candidates": tot["candidates_A"] + tot["candidates_B"]}
    for n in cfg["extra_logs"]:
        expect["extra-" + n] = tot["extra"].get(n, 0)
    counts = {}
    for k, names in files.items():
        c = sum(count_lines(os.path.join(chain_dir, nm)) for nm in names)
        counts[k] = {"files": names, "lines_including_headers": c,
                     "sizes_bytes": {nm: os.path.getsize(os.path.join(chain_dir, nm)) for nm in names}}
        if c != expect[k]:
            raise RuntimeError("line count mismatch for %s: %d != %d" % (k, c, expect[k]))
        for nm in names:
            if os.path.getsize(os.path.join(chain_dir, nm)) > 90 * 1024 * 1024:
                raise RuntimeError("file too large: %s" % nm)
    # topic0 counts
    swap_rows = list(csv.DictReader(open(os.path.join(chain_dir, "swap-topics.csv"))))
    swap_keys = {}
    for r in swap_rows:
        if r["match_rule"] == "topic0":
            swap_keys[r["topic0"].lower()] = r["signature"]
        else:
            for a in r["match_address"].split(";"):
                swap_keys["log0:" + a.strip().lower()] = r["signature"]
    tp = os.path.join(chain_dir, "topic0-counts.csv.gz")
    with gzip.open(tp, "wt", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["topic0_or_log0_emitter", "n_logs", "n_txs", "n_distinct_emitting_addresses", "first_example_tx",
                    "first_example_block", "first_example_log_address", "in_known_swap_topics"])
        for k, v in sorted(tot["topics"].items(), key=lambda kv: -kv[1]["n_logs"]):
            w.writerow([k, v["n_logs"], v["n_txs"], len(v["addrs"]), v["ex_tx"], v["ex_block"], v["ex_addr"],
                        "true" if k in swap_keys else "false"])
    # swap-topics verification from the window
    for r in swap_rows:
        k = r["topic0"].lower() if r["match_rule"] == "topic0" else "log0:" + r["match_address"].split(";")[0].strip().lower()
        v = tot["topics"].get(k)
        if v:
            r["verified_example_tx"] = v["ex_tx"]; r["verified_example_block"] = str(v["ex_block"])
            r["verified_example_log_address"] = v["ex_addr"]
            r["verification_note"] = "first log with this key in census window %d-%d (%s)" % (win["start_block"], win["end_block"], chain)
        else:
            r["verified_example_tx"] = ""; r["verified_example_block"] = ""; r["verified_example_log_address"] = ""
            r["verification_note"] = "no log with this key in census window %d-%d (%s); not verified on this chain" % (
                win["start_block"], win["end_block"], chain)
    with open(os.path.join(chain_dir, "swap-topics.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(swap_rows[0].keys()))
        w.writeheader(); w.writerows(swap_rows)
    # continuity check (parent hash chain) over blocks.csv.gz
    breaks, prev = [], None
    missing_blocks = []
    with gzip.open(os.path.join(chain_dir, files["blocks"][0]), "rt") as f:
        rd = csv.DictReader(f)
        rows = sorted(((int(x["block_number"]), x["block_hash"], x["parent_hash"], int(x["timestamp"])) for x in rd))
    exp = win["start_block"]
    for n, h, ph, ts in rows:
        if n != exp:
            missing_blocks.extend(range(exp, n))
        if prev is not None and prev[0] == n - 1 and prev[1] != ph:
            breaks.append(n)
        prev = (n, h)
        exp = n + 1
    missing_blocks.extend(range(exp, win["end_block"] + 1))
    # canonical recheck of first/last block hash
    recheck = {}
    for n in (win["start_block"], win["end_block"]):
        try:
            bk = rpc1(cfg["primary"], "eth_getBlockByNumber", [hex(n), False])
            stored = [h for (m, h, _, _) in rows if m == n]
            recheck[str(n)] = {"rpc_hash": bk["hash"].lower(), "stored_hash": stored[0] if stored else None,
                               "match": bool(stored) and bk["hash"].lower() == stored[0]}
        except Exception as ex:  # noqa
            recheck[str(n)] = {"error": str(ex)[:200]}
    with open(os.path.join(chain_dir, "gaps.csv"), "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["block_number", "reason"])
        for g, r in sorted(gaps):
            w.writerow([g, r])
    n_blocks = win["end_block"] - win["start_block"] + 1
    win_out = dict(win)
    win_out.update({
        "status": "complete",
        "finalized_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_blocks_in_window": n_blocks,
        "measured_block_interval_s": (win["end_timestamp"] - win["start_timestamp"]) / max(1, (win["end_block"] - win["start_block"])),
        "measured_block_interval_note": "(end_timestamp - start_timestamp) / (end_block - start_block); timestamps have 1 s resolution",
        "counts": {"blocks_written": tot["blocks"], "txs": tot["txs"], "reverted": tot["reverted"],
                   "candidates_A": tot["candidates_A"], "candidates_B": tot["candidates_B"], "extra": tot["extra"],
                   "receipts_not_in_block_tx_list": tot["receipts_not_in_block_tx_list"],
                   "distinct_topic0_keys": len(tot["topics"]), "gap_blocks": len(gaps)},
        "files": counts,
        "checks": {"parent_hash_breaks_at": breaks, "blocks_missing_from_blocks_csv": missing_blocks[:1000],
                   "n_blocks_missing": len(missing_blocks), "canonical_recheck": recheck},
        "rpc_requests_by_endpoint": fetcher.req_count, "rpc_errors_by_endpoint_kind": fetcher.err_count,
    })
    json.dump(win_out, open(os.path.join(chain_dir, "window.json"), "w"), indent=1)
    shutil.rmtree(segroot)
    return win_out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", required=True, choices=sorted(CHAINS))
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--smoke", type=int, default=0, help="smoke test: only the last N blocks, no sentinel")
    ap.add_argument("--seg-blocks", type=int, default=0, help="override segment size (testing)")
    ap.add_argument("--part-limit-mb", type=float, default=0, help="override part size limit (testing)")
    args = ap.parse_args()
    cfg = dict(CHAINS[args.chain])
    if args.seg_blocks:
        cfg["seg_blocks"] = args.seg_blocks
    if args.part_limit_mb:
        global PART_LIMIT
        PART_LIMIT = int(args.part_limit_mb * 1024 * 1024)
    chain_dir = os.path.abspath(args.out)
    os.makedirs(chain_dir, exist_ok=True)
    sentinel = None if args.smoke else os.path.join(SENTINEL_DIR, cfg["sentinel"])
    try:
        swap_topics, log0_addrs = load_swap_topics(chain_dir)
        log("chain", args.chain, "swap topics", len(swap_topics), "log0 addrs", len(log0_addrs))
        wp = os.path.join(chain_dir, "window.json")
        if os.path.exists(wp) and json.load(open(wp)).get("status") == "complete":
            log("already complete"); return
        if os.path.exists(wp):
            win = json.load(open(wp))
            log("resuming pinned window", win["start_block"], win["end_block"])
        else:
            win = pin_window(cfg, None)
            win["chain"] = args.chain
            win["chain_id"] = cfg["chain_id"]
            win["endpoints"] = {"primary": cfg["primary"], "fallbacks": cfg["fallbacks"]}
            win["config"] = {k: v for k, v in cfg.items() if k not in ("primary", "fallbacks")}
            if args.smoke:
                win["start_block"] = win["end_block"] - args.smoke + 1
                win["start_timestamp"] = hx(rpc1(cfg["primary"], "eth_getBlockByNumber", [hex(win["start_block"]), False])["timestamp"])
                win["smoke_test"] = True
            win["status"] = "in_progress"
            win["collector"] = "census.py"
            json.dump(win, open(wp, "w"), indent=1)
            log("pinned window", json.dumps(win))
        fetcher = Fetcher(cfg)
        segroot = os.path.join(chain_dir, "_segments")
        os.makedirs(segroot, exist_ok=True)
        gaps = []
        segs = list(segments_of(win["start_block"], win["end_block"], cfg["seg_blocks"]))
        t0 = time.time(); nb = 0
        for i, (s, e) in enumerate(segs):
            sd = os.path.join(segroot, "seg-%d-%d" % (s, e))
            if os.path.exists(os.path.join(sd, "DONE")):
                continue
            st = run_segment(cfg, fetcher, s, e, sd, swap_topics, log0_addrs, args.workers, gaps)
            nb += e - s + 1
            el = time.time() - t0
            log("segment %d/%d %d-%d blocks=%d txs=%d rev=%d candA=%d candB=%d gaps=%d | %.1f blk/s | req=%s err=%s" % (
                i + 1, len(segs), s, e, st["blocks"], st["txs"], st["reverted"], st["candidates_A"],
                st["candidates_B"], len(st["gaps"]), nb / max(el, 1e-6), fetcher.req_count, fetcher.err_count))
        # retry gaps once more as separate segments
        allgaps = []
        for d in sorted(os.listdir(segroot)):
            p = os.path.join(segroot, d, "stats.json")
            if os.path.exists(p):
                for g, r in json.load(open(p)).get("gaps", []):
                    allgaps.append(g)
        if allgaps:
            log("retrying %d gap blocks" % len(allgaps))
            for g in allgaps:
                done, failed = fetcher.fetch_blocks([g], max_attempts=20)
                if g in done:
                    sd = os.path.join(segroot, "seg-%d-%d-gapfill" % (g, g))
                    run_segment(cfg, fetcher, g, g, sd, swap_topics, log0_addrs, 1, [])
                    # remove gap from original segment stats
                    for d in os.listdir(segroot):
                        p = os.path.join(segroot, d, "stats.json")
                        if os.path.exists(p) and "gapfill" not in d:
                            sj = json.load(open(p))
                            if any(x[0] == g for x in sj.get("gaps", [])):
                                sj["gaps"] = [x for x in sj["gaps"] if x[0] != g]
                                sj.setdefault("gapfilled", []).append(g)
                                json.dump(sj, open(p, "w"))
        out = finalize(cfg, args.chain, chain_dir, win, fetcher, gaps)
        log("finalized", json.dumps(out["counts"]), "interval", out["measured_block_interval_s"])
        if sentinel:
            if os.path.exists(sentinel + ".FAILED"):
                os.remove(sentinel + ".FAILED")
            with open(sentinel + ".DONE", "w") as f:
                f.write("%s census complete %s blocks %d-%d gap_blocks=%d dir=%s\n" % (
                    args.chain, out["finalized_at_utc"], win["start_block"], win["end_block"],
                    out["counts"]["gap_blocks"], chain_dir))
    except Exception as ex:
        log("FATAL", repr(ex)); traceback.print_exc()
        if sentinel:
            with open(sentinel + ".FAILED", "w") as f:
                f.write("%s census failed %s: %s\n(resumable: re-run the same command)\n" % (
                    args.chain, datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), repr(ex)[:2000]))
        sys.exit(1)


if __name__ == "__main__":
    main()
