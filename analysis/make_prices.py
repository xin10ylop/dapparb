#!/usr/bin/env python3
"""DefiLlama historical price responses (research-material/06-*/<chain>/prices-defillama-historical.jsonl.gz) ->
analysis/prices/<chain>.csv (token, price_native, decimals) with price_native = usd / native_usd."""
import gzip, json, sys, csv
chain, native_usd = sys.argv[1], float(sys.argv[2]); src = sys.argv[3]; out = sys.argv[4]
extra = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
rows = {}
for l in gzip.open(src, 'rt'):
    d = json.loads(l)
    for k, v in ((d.get('response') or {}).get('coins') or {}).items():
        if ':' not in k or 'price' not in v or 'decimals' not in v: continue
        rows[k.split(':', 1)[1].lower()] = (v['price'] / native_usd, int(v['decimals']), v.get('confidence'))
for t, (p, dcm) in extra.items(): rows[t.lower()] = (p, dcm, 'manual')
w = csv.writer(open(out, 'w', newline=''), lineterminator='\n'); w.writerow(['token', 'price_native', 'decimals', 'confidence'])
for t, (p, dcm, c) in sorted(rows.items()): w.writerow([t, p, dcm, c])
print(chain, len(rows), 'prices')
