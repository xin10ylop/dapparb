#!/usr/bin/env python3
"""Fetch DefiLlama DEX volume overview raw JSON for one chain.
usage: python3 fetch_defillama.py <defillama_chain_slug> <out_json>
Writes <out_json> (raw response body, unmodified) and <out_json minus .json>.fetch.json (URL, UTC fetch time, HTTP status, bytes)."""
import datetime, json, sys, time, requests
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
slug, out = sys.argv[1], sys.argv[2]
url = "https://api.llama.fi/overview/dexs/%s" % slug
for i in range(8):
    t = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        r = requests.get(url, headers=UA, timeout=120)
    except requests.RequestException as ex:
        print("net error", ex); time.sleep(5 * (i + 1)); continue
    if r.status_code == 429 or r.status_code >= 500:
        print("http", r.status_code); time.sleep(5 * (i + 1)); continue
    break
open(out, "wb").write(r.content)
json.loads(r.content)  # must be valid JSON
meta = {"url": url, "fetched_at_utc": t, "http_status": r.status_code, "bytes": len(r.content)}
json.dump(meta, open(out[:-5] + ".fetch.json", "w"), indent=1)
print(json.dumps(meta))
