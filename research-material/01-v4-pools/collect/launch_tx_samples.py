#!/usr/bin/env python3
"""For each hook address in <hooks_file>, take up to 3 sample Initialize events (earliest, middle, latest by block in the Initialize
data available locally: V4INIT final parts or work chunks, plus V4RECENT 7-day chunks), fetch the transaction and its receipt, and
record every log the transaction emitted (emitter address, topics, data) plus the tx sender / target / 4-byte selector.
Event names are resolved (derived) by matching topic0 against keccak256 of event signatures in Blockscout-verified ABIs of the
emitter (and of its proxy implementations), read from ../hook-docs/blockscout/<addr>.smart_contract.json.gz (fetched here if absent).
Outputs: ../hook-docs/launch-tx-samples-logs.csv.gz, ../hook-docs/launch-tx-samples-tx.csv.gz
Usage: python3 launch_tx_samples.py <hooks_file>

Memory fix (2026-10-01; the first run was OOM-killed at 6.5 GB RSS on 2026-09-30 22:07Z). The first version kept one Python tuple
(block, log_index, tx_hash, pool_id) for EVERY Initialize row of every candidate hook (15.0 M of the 15.3 M rows; one hook alone has
8.2 M pools) plus a set of all their pool-id strings, and held both until the process exited. This version selects exactly the
same samples while streaming the input files three times:
  pass 1  per hook, an array('q') of sort keys block*2^24+log_index (8 bytes per row). Pool-id de-duplication (first occurrence
          wins, as before) uses a 2^31-bit bitmap indexed by 31 bits of the pool id. A row whose bit is already set is only a
          POSSIBLE duplicate; its sequence number and pool id are recorded.
  pass 2  exact check of the possible duplicates: rows whose pool id is in that small set are tracked by full pool id, and every
          occurrence after the first is a true duplicate. True duplicates are removed from the per-hook arrays.
  pass 3  each array is sorted (no-op for V4INIT order), the earliest / middle (index n//2) / latest keys are picked exactly as
          before (sorted by block, log_index; ties are impossible because (block, log_index) identifies one log, and the
          script aborts if one is found), and the full rows (tx_hash, pool_id) of the picked keys are read back.
The selected samples are checkpointed in state/launch-tx-samples-selection.json, and fetched tx/receipt fields in
work/launch_tx_cache.jsonl, so a restarted run resumes. Peak RSS is logged after each phase."""
import array, csv, gzip, hashlib, json, os, re, resource, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Endpoint, keccak_hex, log

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE); D = os.path.join(OUT, "hook-docs"); BS = os.path.join(D, "blockscout")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
hooks = [l.strip().lower() for l in open(sys.argv[1]) if l.strip()]
want = set(hooks)
SEL_PATH = os.path.join(HERE, "state", "launch-tx-samples-selection.json")
CACHE_PATH = os.path.join(HERE, "work", "launch_tx_cache.jsonl")


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024


# ---- input files (same list as the first version; the V4RECENT chunk list is sorted for a deterministic order)
files = []
idx = os.path.join(OUT, "initialize-parts.json")
if os.path.exists(idx):
    files += [(os.path.join(OUT, p["file"]), True) for p in json.load(open(idx))["parts"]]
else:
    wd = os.path.join(HERE, "work", "v4init")
    files += [(os.path.join(wd, f), False) for f in sorted(os.listdir(wd)) if re.match(r"c_\d+_\d+\.csv\.gz$", f)]
wr = os.path.join(HERE, "work", "v4recent")
files += [(os.path.join(wr, f), False) for f in sorted(os.listdir(wr)) if f.startswith("init_") and f.endswith(".csv.gz")]

LI_BITS = 24


def rows():
    """Stream (block, tx_hash, log_index, pool_id, hook) of every row whose hook is wanted, in file order. Fields hold only
    decimal numbers and 0x-hex, so a plain split equals csv parsing; a line with a quote is parsed with csv as a fallback."""
    for p, hdr in files:
        with gzip.open(p, "rt", newline="") as f:
            if hdr:
                next(f)
            for line in f:
                r = line.split(",", 10)
                if r[9] not in want:
                    continue
                if '"' in line:
                    r = next(csv.reader([line]))
                    if r[9] not in want:
                        continue
                yield r[0], r[1], r[3], r[4], r[9]


def select_samples():
    # pass 1: per-hook sort keys + bitmap pre-filter for pool-id duplicates
    keys = {h: array.array("q") for h in want}
    NB = 1 << 31
    bm = bytearray(NB >> 3)  # 256 MB
    maybe = []  # (seq, hook, position in keys[hook], pool_id) of rows whose bitmap bit was already set
    seq = 0
    for blk, txh, li, pid, h in rows():
        li_i = int(li)
        if li_i >= (1 << LI_BITS):
            raise SystemExit("log_index %s >= 2^%d at block %s" % (li, LI_BITS, blk))
        x = int(pid[2:10], 16) & (NB - 1)
        a = keys[h]
        if bm[x >> 3] & (1 << (x & 7)):
            maybe.append((seq, h, len(a), pid))
        else:
            bm[x >> 3] |= 1 << (x & 7)
        a.append((int(blk) << LI_BITS) | li_i)
        seq += 1
    del bm
    n_rows = seq
    log("pass1 rows_with_candidate_hook", n_rows, "possible_duplicates", len(maybe), "maxrss_mb", rss_mb())

    # pass 2: exact pool-id duplicate check, restricted to the pool ids of the possible duplicates
    dup_seq = set()
    if maybe:
        F = set(m[3] for m in maybe)
        first = {}
        last_maybe = maybe[-1][0]
        seq = 0
        for blk, txh, li, pid, h in rows():
            if pid in F:
                if pid in first:
                    dup_seq.add(seq)
                else:
                    first[pid] = seq
            seq += 1
            if seq > last_maybe:
                break
        del F, first
        maybe_seqs = set(m[0] for m in maybe)
        assert dup_seq <= maybe_seqs, "a duplicate was not pre-flagged by the bitmap"
        drop = {}
        for s, h, pos, pid in maybe:
            if s in dup_seq:
                drop.setdefault(h, set()).add(pos)
        for h, ps in drop.items():
            a = keys[h]
            keys[h] = array.array("q", (v for i, v in enumerate(a) if i not in ps))
        del maybe, maybe_seqs, drop
    log("pass2 pool_id_duplicates_dropped", len(dup_seq), "maxrss_mb", rss_mb())

    # selection: earliest, middle (index n//2), latest in (block, log_index) order
    need = {}  # (hook, key) -> None until found
    n_avail = {}
    n_sorted_already = 0
    for h in want:
        a = keys[h]
        n = len(a)
        n_avail[h] = n
        if n == 0:
            continue
        ok = all(a[i] < a[i + 1] for i in range(n - 1))
        if ok:
            n_sorted_already += 1
            srt = a
        else:
            srt = sorted(a)
            for i in range(n - 1):
                if srt[i] == srt[i + 1]:
                    raise SystemExit("tie on (block, log_index) key %d for hook %s: two pool ids at one log" % (srt[i], h))
        for i in {0, n // 2, n - 1}:
            need[(h, srt[i])] = None
        keys[h] = None
        del srt
    del keys
    log("selection hooks_with_rows", sum(1 for v in n_avail.values() if v), "already_sorted", n_sorted_already, "picked_keys", len(need),
        "maxrss_mb", rss_mb())

    # pass 3: read back the picked rows (skipping the dropped duplicates)
    seq = 0
    left = len(need)
    for blk, txh, li, pid, h in rows():
        if seq not in dup_seq:
            k = (h, (int(blk) << LI_BITS) | int(li))
            if k in need and need[k] is None:
                need[k] = (int(blk), int(li), txh, pid)
                left -= 1
        seq += 1
    if left:
        raise SystemExit("pass3: %d picked keys not found" % left)
    samples = []
    for h in hooks:
        n = n_avail[h]
        if not n:
            continue
        picked = sorted(v for (hh, k), v in need.items() if hh == h)
        for r in picked:
            samples.append((h, n) + r)
    stats = {"rows_with_candidate_hook": n_rows, "pool_id_duplicates_dropped": len(dup_seq)}
    return samples, n_avail, stats


hooks_sha = hashlib.sha256("\n".join(hooks).encode()).hexdigest()
in_files = [[os.path.relpath(p, OUT), os.path.getsize(p)] for p, _ in files]
samples = None
if os.path.exists(SEL_PATH):
    j = json.load(open(SEL_PATH))
    if j.get("hooks_sha256") == hooks_sha and j.get("input_files") == in_files:
        samples = [tuple(s) for s in j["samples"]]
        log("selection loaded from checkpoint", os.path.relpath(SEL_PATH, HERE))
if samples is None:
    samples, n_avail, stats = select_samples()
    tmp = SEL_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"hooks_file": sys.argv[1], "hooks_sha256": hooks_sha, "input_files": in_files, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "columns": ["hook", "hook_pools_in_local_data", "block_number", "log_index", "tx_hash", "pool_id"], "stats": stats,
                   "samples": [list(s) for s in samples]}, f)
    os.replace(tmp, SEL_PATH)
log("hooks", len(hooks), "samples", len(samples), "maxrss_mb", rss_mb())

ep = Endpoint("tenderly", "https://gateway.tenderly.co/public/base", 1000, inflight=1)
ep2 = Endpoint("mainnet.base.org", "https://mainnet.base.org", 2000, inflight=1)


def call(method, params):
    last = None
    for e in (ep, ep2):
        try:
            res = e.call_retry(method, params, tries=5)
            if res is None:
                raise RuntimeError("%s returned null on %s" % (method, e.name))
            return res
        except Exception as ex:  # noqa: BLE001
            last = ex
    raise last


# ---- tx + receipt per sample (cached per tx hash so a restarted run does not refetch)
cache = {}
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH) as f:
        for l in f:
            try:
                j = json.loads(l)
            except ValueError:
                continue  # partial last line from an interrupted run
            cache[j["tx_hash"]] = j
    log("tx cache entries", len(cache))
cf = open(CACHE_PATH, "a")
txrows, logrows = [], []
emitters = set()
n_fetched = 0
for (h, n_avail, blk, li, txh, pid) in samples:
    c = cache.get(txh)
    if c is None:
        tx = call("eth_getTransactionByHash", [txh])
        rc = call("eth_getTransactionReceipt", [txh])
        c = {"tx_hash": txh, "from": tx["from"].lower(), "to": (tx.get("to") or "").lower(),
             "sel": tx["input"][:10] if tx.get("input") and len(tx["input"]) >= 10 else tx.get("input", ""),
             "value": str(int(tx.get("value", "0x0"), 16)), "status": rc["status"],
             "logs": [[int(lg["logIndex"], 16), lg["address"].lower(), [x.lower() for x in lg["topics"]], lg["data"].lower()] for lg in rc["logs"]]}
        cf.write(json.dumps(c) + "\n"); cf.flush()
        cache[txh] = c
        n_fetched += 1
        time.sleep(0.2)
    txrows.append([h, pid, str(blk), txh, c["from"], c["to"], c["sel"], c["value"], c["status"], str(len(c["logs"])), str(n_avail)])
    for li_, addr, t, data in c["logs"]:
        emitters.add(addr)
        logrows.append([h, pid, str(blk), txh, str(li_), addr, t[0] if t else "", str(len(t)), ";".join(t), data])
cf.close()
log("txs", len(txrows), "logs", len(logrows), "distinct emitters", len(emitters), "fetched_now", n_fetched, "maxrss_mb", rss_mb())

# ---- ABI-based event name resolution (Blockscout verified ABIs)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0"


def bs_get(url):
    for i in range(8):
        try:
            r = S.get(url, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(60, 2 ** i)); continue
            return r.status_code, r.json()
        except (requests.RequestException, ValueError):
            time.sleep(min(60, 2 ** i))
    return -1, {}


def load_or_fetch(addr, kind):
    p = os.path.join(BS, "%s.%s.json.gz" % (addr, kind))
    if os.path.exists(p):
        try:
            with gzip.open(p, "rt") as f:
                j = json.load(f)
            if j.get("http_status") in (200, 404):
                return j["body"]
        except (OSError, EOFError, ValueError):
            pass  # truncated file from an interrupted run: refetch
    u = "https://base.blockscout.com/api/v2/%s/%s" % ("addresses" if kind == "address" else "smart-contracts", addr)
    st, b = bs_get(u)
    with gzip.open(p + ".tmp", "wt") as f:
        json.dump({"url": u, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "http_status": st, "body": b}, f)
    os.replace(p + ".tmp", p)
    time.sleep(0.3)
    return b if isinstance(b, dict) else {}


def canon(inp):
    t = inp["type"]
    if t.startswith("tuple"):
        return "(" + ",".join(canon(c) for c in inp.get("components", [])) + ")" + t[5:]
    return t


topic_names = {}  # (emitter, topic0) -> "Contract.Event(sig)"
for k, a in enumerate(sorted(emitters)):
    ab = load_or_fetch(a, "address")
    cands = [a] + [(i.get("address_hash") or i.get("address") or "").lower() for i in (ab.get("implementations") or [])]
    for c in [c for c in cands if c]:
        cb = load_or_fetch(c, "address") if c != a else ab
        if not cb.get("is_verified"):
            continue
        sc = load_or_fetch(c, "smart_contract")
        for item in sc.get("abi") or []:
            if item.get("type") == "event":
                sig = "%s(%s)" % (item["name"], ",".join(canon(i) for i in item.get("inputs", [])))
                topic_names.setdefault((a, keccak_hex(sig.encode())), "%s:%s" % (sc.get("name") or cb.get("name") or "", sig))
    if k % 100 == 99:
        log("emitters resolved", k + 1, "of", len(emitters), "maxrss_mb", rss_mb())
for r in logrows:
    r.append(topic_names.get((r[5], r[6]), ""))

with gzip.open(os.path.join(D, "launch-tx-samples-tx.csv.gz.tmp"), "wt", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook", "sample_pool_id", "block_number", "tx_hash", "tx_from", "tx_to", "tx_selector", "tx_value_wei", "receipt_status", "n_logs",
                "hook_pools_in_local_data"])
    w.writerows(txrows)
os.replace(os.path.join(D, "launch-tx-samples-tx.csv.gz.tmp"), os.path.join(D, "launch-tx-samples-tx.csv.gz"))
with gzip.open(os.path.join(D, "launch-tx-samples-logs.csv.gz.tmp"), "wt", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook", "sample_pool_id", "block_number", "tx_hash", "log_index", "log_address", "topic0", "n_topics", "topics", "data",
                "event_resolved_derived"])
    w.writerows(logrows)
os.replace(os.path.join(D, "launch-tx-samples-logs.csv.gz.tmp"), os.path.join(D, "launch-tx-samples-logs.csv.gz"))
log("done; resolved topic names", len(topic_names), "maxrss_mb", rss_mb())
