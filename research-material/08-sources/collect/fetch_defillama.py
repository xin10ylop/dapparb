#!/usr/bin/env python3
"""Save raw DefiLlama JSON responses (bytes unchanged, gzip-compressed) into ../defillama/.
Usage: python3 fetch_defillama.py   (resumable: skips files already saved with HTTP 200; --force refetches)
Writes ../defillama/index.csv (file, url, http_status, bytes, sha256, fetched_at_utc) and the sentinel is written by the caller.
"""
import csv, gzip, hashlib, json, os, sys, time, datetime as dt
import requests
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'defillama')
os.makedirs(OUT, exist_ok=True)
CA = '/root/.ccr/ca-bundle.crt'
if os.path.exists(CA):
    os.environ.setdefault('REQUESTS_CA_BUNDLE', CA)
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
Q = '?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=false'
JOBS = [(f'overview-dexs-{c}.json', f'https://api.llama.fi/overview/dexs/{c}{Q}')
        for c in ['base', 'arbitrum', 'optimism', 'unichain', 'ethereum', 'polygon', 'bsc', 'solana']]
JOBS += [(f'summary-dexs-{p}.json', f'https://api.llama.fi/summary/dexs/{p}')
         for p in ['uniswap-v4', 'uniswap-v2', 'uniswap-v3', 'uniswap']]
force = '--force' in sys.argv
idx_path = os.path.join(OUT, 'index.csv')
rows = {}
if os.path.exists(idx_path):
    for r in csv.DictReader(open(idx_path)):
        rows[r['file']] = r
for name, url in JOBS:
    fn = name + '.gz'
    if not force and rows.get(fn, {}).get('http_status') == '200' and os.path.exists(os.path.join(OUT, fn)):
        print('skip', fn); continue
    delay = 5
    for attempt in range(8):
        try:
            r = requests.get(url, headers={'User-Agent': UA}, timeout=180)
        except Exception as e:
            print('net error', url, e); time.sleep(delay); delay = min(delay * 2, 120); continue
        if r.status_code == 429 or r.status_code >= 500:
            print('http', r.status_code, url, 'retry in', delay); time.sleep(delay); delay = min(delay * 2, 120); continue
        break
    t = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with gzip.open(os.path.join(OUT, fn), 'wb') as f:
        f.write(r.content)
    rows[fn] = {'file': fn, 'url': url, 'http_status': str(r.status_code), 'bytes': str(len(r.content)),
                'sha256': hashlib.sha256(r.content).hexdigest(), 'fetched_at_utc': t}
    print(fn, r.status_code, len(r.content), flush=True)
    time.sleep(2)
with open(idx_path, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['file', 'url', 'http_status', 'bytes', 'sha256', 'fetched_at_utc'])
    w.writeheader()
    for k in sorted(rows):
        w.writerow(rows[k])
