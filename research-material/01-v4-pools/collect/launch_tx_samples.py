#!/usr/bin/env python3
"""For each hook address in <hooks_file>, take up to 3 sample Initialize events (earliest, middle, latest by block in the Initialize
data available locally: V4INIT final parts or work chunks, plus V4RECENT 7-day chunks), fetch the transaction and its receipt, and
record every log the transaction emitted (emitter address, topics, data) plus the tx sender / target / 4-byte selector.
Event names are resolved (derived) by matching topic0 against keccak256 of event signatures in Blockscout-verified ABIs of the
emitter (and of its proxy implementations), read from ../hook-docs/blockscout/<addr>.smart_contract.json.gz (fetched here if absent).
Outputs: ../hook-docs/launch-tx-samples-logs.csv.gz, ../hook-docs/launch-tx-samples-tx.csv.gz
Usage: python3 launch_tx_samples.py <hooks_file>"""
import csv, gzip, json, os, re, sys, time
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Endpoint, keccak_hex, log

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE); D = os.path.join(OUT, "hook-docs"); BS = os.path.join(D, "blockscout")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
hooks = [l.strip().lower() for l in open(sys.argv[1]) if l.strip()]
want = set(hooks)

# ---- sample Initialize rows per hook
per = {h: [] for h in hooks}
files = []
idx = os.path.join(OUT, "initialize-parts.json")
if os.path.exists(idx):
    files += [(os.path.join(OUT, p["file"]), True) for p in json.load(open(idx))["parts"]]
else:
    wd = os.path.join(HERE, "work", "v4init")
    files += [(os.path.join(wd, f), False) for f in os.listdir(wd) if re.match(r"c_\d+_\d+\.csv\.gz$", f)]
wr = os.path.join(HERE, "work", "v4recent")
files += [(os.path.join(wr, f), False) for f in os.listdir(wr) if f.startswith("init_") and f.endswith(".csv.gz")]
seen = set()
for p, hdr in files:
    with gzip.open(p, "rt", newline="") as f:
        rd = csv.reader(f)
        if hdr:
            next(rd)
        for r in rd:
            if r[9] in want and r[4] not in seen:
                seen.add(r[4])
                per[r[9]].append((int(r[0]), int(r[3]), r[1], r[4]))
samples = []
for h in hooks:
    rows = sorted(per[h])
    if not rows:
        continue
    pick = {0, len(rows) // 2, len(rows) - 1}
    for i in sorted(pick):
        samples.append((h, len(rows)) + rows[i])
log("hooks", len(hooks), "samples", len(samples))

ep = Endpoint("tenderly", "https://gateway.tenderly.co/public/base", 1000, inflight=1)
ep2 = Endpoint("mainnet.base.org", "https://mainnet.base.org", 2000, inflight=1)


def call(method, params):
    for e in (ep, ep2):
        try:
            return e.call_retry(method, params, tries=5)
        except Exception as ex:  # noqa: BLE001
            last = ex
    raise last


txrows, logrows = [], []
emitters = set()
for (h, n_avail, blk, li, txh, pid) in samples:
    tx = call("eth_getTransactionByHash", [txh])
    rc = call("eth_getTransactionReceipt", [txh])
    sel = tx["input"][:10] if tx.get("input") and len(tx["input"]) >= 10 else tx.get("input", "")
    txrows.append([h, pid, str(blk), txh, tx["from"].lower(), (tx.get("to") or "").lower(), sel, str(int(tx.get("value", "0x0"), 16)), rc["status"],
                   str(len(rc["logs"])), str(n_avail)])
    for lg in rc["logs"]:
        emitters.add(lg["address"].lower())
        t = lg["topics"]
        logrows.append([h, pid, str(blk), txh, str(int(lg["logIndex"], 16)), lg["address"].lower(), t[0].lower() if t else "", str(len(t)),
                        ";".join(x.lower() for x in t), lg["data"].lower()])
    time.sleep(0.2)
log("txs", len(txrows), "logs", len(logrows), "distinct emitters", len(emitters))

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
        return json.load(gzip.open(p, "rt"))["body"]
    u = "https://base.blockscout.com/api/v2/%s/%s" % ("addresses" if kind == "address" else "smart-contracts", addr)
    st, b = bs_get(u)
    with gzip.open(p, "wt") as f:
        json.dump({"url": u, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "http_status": st, "body": b}, f)
    time.sleep(0.3)
    return b


def canon(inp):
    t = inp["type"]
    if t.startswith("tuple"):
        return "(" + ",".join(canon(c) for c in inp.get("components", [])) + ")" + t[5:]
    return t


topic_names = {}  # (emitter, topic0) -> "Contract.Event(sig)"
for a in sorted(emitters):
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
for r in logrows:
    r.append(topic_names.get((r[5], r[6]), ""))

with gzip.open(os.path.join(D, "launch-tx-samples-tx.csv.gz"), "wt", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook", "sample_pool_id", "block_number", "tx_hash", "tx_from", "tx_to", "tx_selector", "tx_value_wei", "receipt_status", "n_logs",
                "hook_pools_in_local_data"])
    w.writerows(txrows)
with gzip.open(os.path.join(D, "launch-tx-samples-logs.csv.gz"), "wt", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook", "sample_pool_id", "block_number", "tx_hash", "log_index", "log_address", "topic0", "n_topics", "topics", "data",
                "event_resolved_derived"])
    w.writerows(logrows)
log("done; resolved topic names", len(topic_names))
