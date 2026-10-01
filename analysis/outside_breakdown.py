#!/usr/bin/env python3
"""Line 2: split Base arbitrage through pools outside the engine's enumerated universe by the pool's factory (factory() at
latest, cached in base/outside-pools-factory.csv.gz): older pairs of a V2 factory the engine supports, V3-style pools of a
supported factory whose pair the engine never enumerated, and DEXes the engine does not support."""
import csv, gzip, json, collections, urllib.request, time, os
A = '/home/user/dapparb/analysis/base'; R = '/home/user/dapparb/research-material'; H = 21552 * 2 / 3600
V2 = {'0x420dd381b31aef6683db6b902084cb0ffece40da': 'Aerodrome V2', '0x8909dc15e40173ff4699343b6eb8132c65e18ec6': 'Uniswap V2',
      '0x71524b4f93c58fcbf659783284e38825f0622859': 'Sushi V2', '0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e': 'Pancake V2', '0xfda619b6d20975be80a10332cd39b9a4b0faa8bb': 'BaseSwap'}
V3 = {'0x33128a8fc17869897dce68ed026d694621f6fdfd': 'Uniswap V3', '0x5e7bb104d84c7cb9b682aac2f3d509f5f406809a': 'Aerodrome CL', '0xf8f2eb4940cfe7d13603dddd87f123820fc061ef': 'Aerodrome CL3',
      '0xade65c38cd4849adba595a4323a8c7ddfe89716a': 'Aerodrome CL2', '0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865': 'Pancake V3', '0xc35dadb65012ec5796536bd9864ed8773abc74c4': 'Sushi V3'}
known = set()
for fn in (f'{R}/04-shallow-pools/pools-prefilter.csv.gz', f'{R}/02-v4-live-test/v4universe-pools-prefilter.csv.gz', f'{R}/04-shallow-pools/pools-pruned-empty.csv.gz'):
    for r in csv.DictReader(gzip.open(fn, 'rt')): known.add((r.get('v4_pool_id') or r['pool_address']).lower())
rows = [r for r in csv.DictReader(gzip.open(f'{A}/arbs-valued.csv.gz', 'rt')) if r['category'].startswith('outside')]
cache = f'{A}/outside-pools-factory.csv.gz'
fac = {r['pool']: r['factory_at_latest'] for r in csv.DictReader(gzip.open(cache, 'rt'))} if os.path.exists(cache) else {}
miss = sorted(set(p for r in rows for p in r['pools'].split() if p not in known) - set(fac))
for i in range(0, len(miss), 25):
    ch = miss[i:i + 25]; body = [{'jsonrpc': '2.0', 'id': j, 'method': 'eth_call', 'params': [{'to': p, 'data': '0xc45a0155'}, 'latest']} for j, p in enumerate(ch)]
    d = json.loads(urllib.request.urlopen(urllib.request.Request('https://base-rpc.publicnode.com', json.dumps(body).encode(), {'content-type': 'application/json', 'user-agent': 'curl/8'}), timeout=60).read())
    for x in d:
        if isinstance(x.get('id'), int): r_ = x.get('result') or ''; fac[ch[x['id']]] = '0x' + r_[-40:] if len(r_) >= 66 else ''
    time.sleep(0.2)
with gzip.open(cache, 'wt', newline='') as f: w = csv.writer(f); w.writerow(['pool', 'factory_at_latest']); w.writerows(sorted(fac.items()))
agg = collections.defaultdict(collections.Counter)
for r in rows:
    fs = [fac.get(p, '') for p in r['pools'].split() if p not in known]
    kinds = {'unsupported DEX' if f not in V2 and f not in V3 else 'V3-style pool, pair not enumerated' if f in V3 else 'older pair of a supported V2 factory' for f in fs}
    k = next(x for x in ('unsupported DEX', 'V3-style pool, pair not enumerated', 'older pair of a supported V2 factory') if x in kinds)
    g = float(r['gross_usd']); a = agg[k]; a['n'] += 1; a['g'] += g; a['f'] += float(r['fee_usd']); a['p'] += float(r['priority_usd']); a['bg'] += g * (r['backrun'] == '1'); a['max'] = max(a['max'], g)
res = {k: {'arbs': v['n'], 'gross_usd_per_hour': round(v['g'] / H, 2), 'net_of_arb_tx_fees_usd_per_hour': round((v['g'] - v['f']) / H, 2), 'priority_share': round(v['p'] / v['g'], 3),
           'backrun_share_of_gross': round(v['bg'] / v['g'], 3), 'largest_usd': round(v['max'], 2), 'largest_share': round(v['max'] / v['g'], 3)} for k, v in agg.items()}
json.dump(res, open(f'{A}/outside-universe-breakdown.json', 'w'), indent=1); print(json.dumps(res, indent=1))
