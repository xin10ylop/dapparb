#!/usr/bin/env python3
"""Fetch Blockscout (base.blockscout.com API v2) metadata for hook / factory addresses; raw responses saved verbatim (gzip JSON)
under ../hook-docs/blockscout/ with fetch time. Usage: python3 hook_blockscout.py <addresses_file>  (one address per line)
Writes ../hook-docs/blockscout/index.jsonl.gz (one line per address: address, fetched_utc, url, http_status, name, is_contract,
is_verified, creator_address_hash, creation_transaction_hash, creation_tx_from, creation_tx_to, creation_tx_method, contract_name,
compiler_version, file_path, proxy_type, implementations)."""
import gzip, json, os, sys, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
D = os.path.join(OUT, "hook-docs", "blockscout"); os.makedirs(D, exist_ok=True)
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36"
BASE = "https://base.blockscout.com/api/v2"
def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
def get(url):
    for i in range(10):
        try:
            r = S.get(url, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(min(60, 2 ** i)); continue
            return r.status_code, (r.json() if r.headers.get("content-type", "").startswith("application/json") else {"_text": r.text[:2000]})
        except (requests.RequestException, ValueError) as e:
            time.sleep(min(60, 2 ** i)); err = str(e)
    return -1, {"_error": "failed after retries"}
def save(name, url, status, body):
    with gzip.open(os.path.join(D, name + ".json.gz"), "wt") as f:
        json.dump({"url": url, "fetched_utc": now(), "http_status": status, "body": body}, f)
addrs = [l.strip().lower() for l in open(sys.argv[1]) if l.strip()]
idx_path = os.path.join(D, "index.jsonl.gz")
done = {}
if os.path.exists(idx_path):
    for l in gzip.open(idx_path, "rt"):
        j = json.loads(l); done[j["address"]] = j
for a in addrs:
    if a in done and done[a].get("http_status") == 200: continue
    u = "%s/addresses/%s" % (BASE, a); st, b = get(u); save(a + ".address", u, st, b)
    rec = {"address": a, "fetched_utc": now(), "url": u, "http_status": st}
    if st == 200:
        for k in ("name", "is_contract", "is_verified", "creator_address_hash", "creation_transaction_hash", "proxy_type", "implementations"):
            rec[k] = b.get(k)
        if b.get("creation_transaction_hash"):
            tu = "%s/transactions/%s" % (BASE, b["creation_transaction_hash"]); ts, tb = get(tu); save(a + ".creation_tx", tu, ts, tb)
            if ts == 200:
                rec["creation_tx_from"] = (tb.get("from") or {}).get("hash"); rec["creation_tx_to"] = (tb.get("to") or {}).get("hash")
                rec["creation_tx_method"] = tb.get("method"); rec["creation_tx_block"] = tb.get("block_number") or tb.get("block"); rec["creation_tx_timestamp"] = tb.get("timestamp")
        if b.get("is_verified"):
            su = "%s/smart-contracts/%s" % (BASE, a); ss, sb = get(su); save(a + ".smart_contract", su, ss, sb)
            if ss == 200:
                rec["contract_name"] = sb.get("name"); rec["compiler_version"] = sb.get("compiler_version"); rec["file_path"] = sb.get("file_path")
    done[a] = rec
    with gzip.open(idx_path + ".tmp", "wt") as f:
        for v in done.values(): f.write(json.dumps(v) + "\n")
    os.replace(idx_path + ".tmp", idx_path)
    print(now(), a, rec.get("name"), rec.get("is_verified"), rec.get("creation_tx_from"), flush=True)
    time.sleep(0.4)
