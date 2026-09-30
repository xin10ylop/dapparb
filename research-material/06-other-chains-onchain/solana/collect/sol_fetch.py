#!/usr/bin/env python3
"""Solana consecutive-slot sample: raw fetch phase.

Pins a window of N consecutive slots ending at the 'finalized' slot observed at pin time, then for every
slot of the window calls getBlock(slot, {encoding:'json', maxSupportedTransactionVersion:1,
transactionDetails:'full', rewards:false, commitment:'finalized'}).

NOTE maxSupportedTransactionVersion: the task asked for 0, but mainnet blocks of 2026-09 contain version-1
transactions and both RPC endpoints answer version 0 requests with error -32015 ("Transaction version (1) is
not supported by the requesting client ... maxSupportedTransactionVersion: 1"). 1 is the lowest value accepted.

Per slot writes <data>/raw-slots/slot-<slot>.json.gz (this file is the checkpoint: existing files are skipped):
  {"slot", "status": "ok"|"skipped", "endpoint", "fetched_at_utc", "rpc_error" (skipped only, verbatim),
   "header": {blockTime, blockhash, previousBlockhash, parentSlot, blockHeight} (verbatim),
   "tx_count", "vote_tx_count", "vote_tx_mixed_count",
   "vote_tx_indices_mixed": [...],
   "nonvote": [{"index": i, "tx": <verbatim getBlock transaction object: {transaction, meta, version}>} ...]}
'vote tx' := a transaction whose every top-level instruction invokes Vote111111111111111111111111111111111111111.
Transactions that contain a Vote instruction plus any other top-level instruction are NOT vote txs here
(stored verbatim in 'nonvote'; counted in vote_tx_mixed_count for reference).

Also saves (once): pin.json, slot-leaders.json (getSlotLeaders verbatim), get-blocks.json (getBlocks verbatim),
and at the end integrity/crosscheck.json (a few slots fetched from both endpoints and compared).

usage: python3 sol_fetch.py --n 600 [--end-slot S]
"""
import argparse, datetime, gzip, json, os, random, sys, threading, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "data")
RAW = os.path.join(DATA, "raw-slots")
STATE = os.path.join(HERE, "state")
GAPS = os.path.join(DATA, "fetch-gaps.csv")
VOTE = "Vote111111111111111111111111111111111111111"
EP_PUBLICNODE = "https://solana-rpc.publicnode.com"
EP_MAINNET = "https://api.mainnet-beta.solana.com"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Content-Type": "application/json", "Accept-Encoding": "gzip"}
BLOCK_CFG = {"encoding": "json", "maxSupportedTransactionVersion": 1, "transactionDetails": "full",
             "rewards": False, "commitment": "finalized"}
# error codes that mean the slot has no block (skipped slot) per Solana RPC
SKIP_CODES = {-32007, -32009}
# transient codes: -32004 block not available, -32014 block status not yet available, -32016 min context slot
RETRY_CODES = {-32004, -32014, -32016, -32005}

def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def log(*a):
    print(now(), *a, flush=True)

class Endpoint:
    """per-endpoint concurrency + minimum spacing between request starts"""
    def __init__(self, url, max_inflight, min_interval):
        self.url, self.sem, self.min_interval = url, threading.Semaphore(max_inflight), min_interval
        self.lock, self.last = threading.Lock(), 0.0
        self.sess = threading.local()
        self.stats = {"requests": 0, "http_429": 0, "http_5xx": 0, "net_err": 0, "rpc_err": 0}
    def session(self):
        s = getattr(self.sess, "s", None)
        if s is None:
            s = requests.Session(); self.sess.s = s
        return s
    def call(self, method, params, timeout=90):
        """returns (result, error_obj). raises RuntimeError after retries on transport errors"""
        body = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        delay = 1.0
        for attempt in range(12):
            with self.sem:
                with self.lock:
                    w = self.last + self.min_interval - time.time()
                    if w > 0: time.sleep(w)
                    self.last = time.time()
                self.stats["requests"] += 1
                try:
                    r = self.session().post(self.url, json=body, headers=UA, timeout=timeout)
                except requests.RequestException as ex:
                    self.stats["net_err"] += 1
                    log("net error", self.url, method, str(ex)[:160]); r = None
            if r is None:
                time.sleep(delay + random.random()); delay = min(delay * 2, 60); continue
            if r.status_code == 429:
                self.stats["http_429"] += 1
                ra = r.headers.get("retry-after")
                wait = float(ra) if ra and ra.replace('.', '', 1).isdigit() else delay
                log("429", self.url, method, "wait", wait)
                time.sleep(wait + random.random()); delay = min(delay * 2, 60); continue
            if r.status_code >= 500:
                self.stats["http_5xx"] += 1
                log("http", r.status_code, self.url, method)
                time.sleep(delay + random.random()); delay = min(delay * 2, 60); continue
            if r.status_code != 200:
                raise RuntimeError("HTTP %s from %s: %s" % (r.status_code, self.url, r.text[:300]))
            try:
                j = r.json()
            except ValueError:
                self.stats["net_err"] += 1
                log("bad json", self.url, method, r.text[:200])
                time.sleep(delay); delay = min(delay * 2, 60); continue
            if "error" in j:
                self.stats["rpc_err"] += 1
                return None, j["error"]
            return j.get("result"), None
        raise RuntimeError("giving up after retries: %s %s" % (self.url, method))

def is_vote(tx):
    msg = tx["transaction"]["message"]; keys = msg["accountKeys"]
    progs = [keys[ix["programIdIndex"]] if ix["programIdIndex"] < len(keys) else None for ix in msg["instructions"]]
    has_vote = VOTE in progs
    pure = has_vote and all(p == VOTE for p in progs)
    return pure, has_vote and not pure

def norm(x, drop_logs=False):
    if isinstance(x, bool) or x is None: return x
    if isinstance(x, (int, float)): return float(x)
    if isinstance(x, list): return [norm(v, drop_logs) for v in x]
    if isinstance(x, dict): return {k: norm(v, drop_logs) for k, v in x.items() if not (drop_logs and k == "logMessages")}
    return x

def write_json_gz(path, obj):
    tmp = path + ".tmp"
    with gzip.open(tmp, "wt", compresslevel=6) as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(tmp, path)

def append_gap(slot, reason):
    new = not os.path.exists(GAPS)
    with open(GAPS, "a") as f:
        if new: f.write("slot,reason,recorded_at_utc\n")
        f.write("%d,%s,%s\n" % (slot, json.dumps(reason).replace(",", ";"), now()))

def fetch_slot(slot, eps, primary_idx):
    order = eps[primary_idx:] + eps[:primary_idx]
    last_err = None
    for rnd in range(8):
        for ep in order:
            try:
                res, err = ep.call("getBlock", [slot, BLOCK_CFG])
            except RuntimeError as ex:
                last_err = {"transport": str(ex)}; continue
            if err is None and res is not None:
                return ep.url, res, None
            if err is not None and err.get("code") in SKIP_CODES:
                return ep.url, None, err
            last_err = err
            if err is not None and err.get("code") not in RETRY_CODES:
                log("unexpected rpc error", slot, ep.url, err)
        time.sleep(2 * (rnd + 1))
    raise RuntimeError("slot %d unrecoverable: %s" % (slot, json.dumps(last_err)[:400]))

def process(slot, eps, primary_idx):
    path = os.path.join(RAW, "slot-%d.json.gz" % slot)
    if os.path.exists(path):
        return "exists"
    url, res, err = fetch_slot(slot, eps, primary_idx)
    if res is None:
        write_json_gz(path, {"slot": slot, "status": "skipped", "endpoint": url, "fetched_at_utc": now(), "rpc_error": err})
        return "skipped"
    txs = res.get("transactions") or []
    nonvote, nvote, nmixed, mixed_idx = [], 0, 0, []
    for i, t in enumerate(txs):
        pure, mixed = is_vote(t)
        if pure:
            nvote += 1
        else:
            if mixed:
                nmixed += 1; mixed_idx.append(i)
            nonvote.append({"index": i, "tx": t})
    hdr = {k: res.get(k) for k in ("blockTime", "blockhash", "previousBlockhash", "parentSlot", "blockHeight")}
    extra_keys = sorted(set(res.keys()) - set(hdr.keys()) - {"transactions"})
    obj = {"slot": slot, "status": "ok", "endpoint": url, "fetched_at_utc": now(), "header": hdr,
           "other_block_fields": {k: res.get(k) for k in extra_keys},
           "tx_count": len(txs), "vote_tx_count": nvote, "vote_tx_mixed_count": nmixed,
           "vote_tx_indices_mixed": mixed_idx, "nonvote": nonvote}
    write_json_gz(path, obj)
    return "ok"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--end-slot", type=int, default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--only", default=None, help="comma list of slots (smoke test); does not pin")
    a = ap.parse_args()
    for d in (DATA, RAW, STATE):
        os.makedirs(d, exist_ok=True)
    pn = Endpoint(EP_PUBLICNODE, 3, 0.15)
    mb = Endpoint(EP_MAINNET, 1, 2.0)     # getBlock method limit header on mainnet-beta: 6
    eps = [pn, mb]
    if a.only:
        for s in [int(x) for x in a.only.split(",")]:
            log("smoke", s, process(s, eps, 0))
        return
    pin_path = os.path.join(STATE, "pin.json")
    if os.path.exists(pin_path):
        pin = json.load(open(pin_path))
        log("resuming with pin", pin)
    else:
        fin, err = mb.call("getSlot", [{"commitment": "finalized"}])
        if err: fin, err = pn.call("getSlot", [{"commitment": "finalized"}])
        end = a.end_slot if a.end_slot is not None else fin
        pin = {"pinned_at_utc": now(), "finalized_slot_at_pin": fin, "start_slot": end - a.n + 1, "end_slot": end,
               "n_slots": a.n, "getBlock_config": BLOCK_CFG,
               "endpoints": {"primary": EP_PUBLICNODE, "secondary": EP_MAINNET},
               "vote_tx_definition": "every top-level instruction invokes " + VOTE}
        json.dump(pin, open(pin_path, "w"), indent=1)
        log("pinned", pin)
    start, end, n = pin["start_slot"], pin["end_slot"], pin["n_slots"]
    # leaders + produced-block list (verbatim)
    lp = os.path.join(DATA, "slot-leaders.json")
    if not os.path.exists(lp):
        res, err = mb.call("getSlotLeaders", [start, n])
        if err: res, err = pn.call("getSlotLeaders", [start, n])
        json.dump({"method": "getSlotLeaders", "params": [start, n], "fetched_at_utc": now(), "result": res, "error": err},
                  open(lp, "w"))
        log("slot leaders", "ok" if res else err)
    bp = os.path.join(DATA, "get-blocks.json")
    if not os.path.exists(bp):
        res, err = mb.call("getBlocks", [start, end, {"commitment": "finalized"}])
        if err: res, err = pn.call("getBlocks", [start, end, {"commitment": "finalized"}])
        json.dump({"method": "getBlocks", "params": [start, end, {"commitment": "finalized"}], "fetched_at_utc": now(),
                   "result": res, "error": err}, open(bp, "w"))
        log("getBlocks", len(res) if res else err)
    slots = list(range(start, end + 1))
    todo = [s for s in slots if not os.path.exists(os.path.join(RAW, "slot-%d.json.gz" % s))]
    log("todo", len(todo), "of", len(slots))
    lock = threading.Lock(); q = list(todo); counts = {}
    def worker(wid):
        while True:
            with lock:
                if not q: return
                s = q.pop(0)
            prim = 1 if wid == a.workers - 1 else 0   # last worker prefers mainnet-beta
            try:
                st = process(s, eps, prim)
            except Exception as ex:
                st = "failed"; append_gap(s, str(ex)[:300]); log("GAP", s, ex)
            with lock:
                counts[st] = counts.get(st, 0) + 1
                tot = sum(counts.values())
                if tot % 25 == 0: log("progress", tot, "/", len(todo), counts, "pn", pn.stats, "mb", mb.stats)
    th = [threading.Thread(target=worker, args=(i,)) for i in range(a.workers)]
    [t.start() for t in th]; [t.join() for t in th]
    log("fetch done", counts, "pn", pn.stats, "mb", mb.stats)
    # cross-check a few slots on the other endpoint
    cp = os.path.join(DATA, "integrity-crosscheck.json")
    if not os.path.exists(cp):
        checks = []
        for s in [start, start + n // 3, start + 2 * n // 3, end]:
            path = os.path.join(RAW, "slot-%d.json.gz" % s)
            if not os.path.exists(path): continue
            obj = json.load(gzip.open(path, "rt"))
            other = mb if obj.get("endpoint") == EP_PUBLICNODE else pn
            try:
                res, err = other.call("getBlock", [s, BLOCK_CFG])
            except RuntimeError as ex:
                res, err = None, {"transport": str(ex)}
            if obj["status"] == "skipped":
                checks.append({"slot": s, "stored": "skipped", "other_endpoint": other.url, "other_error": err,
                               "other_has_block": res is not None}); continue
            if res is None:
                checks.append({"slot": s, "other_endpoint": other.url, "other_error": err}); continue
            nonvote_other = [{"index": i, "tx": t} for i, t in enumerate(res["transactions"]) if not is_vote(t)[0]]
            checks.append({"slot": s, "stored_endpoint": obj["endpoint"], "other_endpoint": other.url,
                           "blockhash_equal": res["blockhash"] == obj["header"]["blockhash"],
                           "tx_count_equal": len(res["transactions"]) == obj["tx_count"],
                           "nonvote_json_equal_strict": json.dumps(nonvote_other, sort_keys=True) == json.dumps(obj["nonvote"], sort_keys=True),
                           "nonvote_json_equal_numbers_normalized": json.dumps(norm(nonvote_other), sort_keys=True) == json.dumps(norm(obj["nonvote"]), sort_keys=True),
                           "nonvote_json_equal_numbers_normalized_excluding_logMessages": json.dumps(norm(nonvote_other, True), sort_keys=True) == json.dumps(norm(obj["nonvote"], True), sort_keys=True),
                           "logMessages_length_differs_tx_indices": [x["index"] for x, y in zip(nonvote_other, obj["nonvote"]) if len(x["tx"]["meta"].get("logMessages") or []) != len(y["tx"]["meta"].get("logMessages") or [])],
                           "note": "strict: byte-identical JSON. numbers_normalized: all JSON numbers compared as floats (one server writes whole-number floats such as uiTokenAmount.uiAmount as 1150, the other as 1150.0). excluding_logMessages: additionally ignores meta.logMessages, which servers truncate at different byte limits ('Log truncated' line)"})
        json.dump({"checked_at_utc": now(), "checks": checks}, open(cp, "w"), indent=1)
        log("crosscheck", checks)
    with open(os.path.join(STATE, "fetch-stats.jsonl"), "a") as f:   # one line per invocation (re-runs append)
        f.write(json.dumps({"finished_at_utc": now(), "counts": counts, "publicnode": pn.stats, "mainnet_beta": mb.stats}) + "\n")
    missing = [s for s in slots if not os.path.exists(os.path.join(RAW, "slot-%d.json.gz" % s))]
    if missing:
        log("MISSING slots", len(missing)); sys.exit(3)

if __name__ == "__main__":
    main()
