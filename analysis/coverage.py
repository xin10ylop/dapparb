#!/usr/bin/env python3
"""Coverage of the engine's pool universe against the Base census (docs/ANALYSIS.md §7).

An arbitrage counts as covered when every pool it used (V2/V3 addresses and V4 pool ids) is in the universe and it
has at most three legs (the engine searches two-pool cycles and triangles). Reported as shares of valued gross, for all
arbitrages and for the non-backrun part (gaps visible at block boundaries), old universe vs new.

  old universe: pools of the engine's factory enumeration with depth >= 0.1 ETH (research-material 04 prefilter and the
                02 V4 rebuild), i.e. the census category "engine universe".
  new universe: the pool candidates the engine wrote with --dump-pools (factory enumeration + activity registry, after
                its empty filter at startup) with depthEth >= --min-depth.
Out-of-sample: arbitrages in blocks the registry (--registry) never scanned: before its first block, or after its last
when it was built from the days before the census. --registry-universe scores a registry's accepted pools directly.

usage: coverage.py --universe ../bot/data/universe-active.jsonl [--registry ../bot/data/pool-registry-base.json]
"""
import argparse, csv, gzip, glob, json, collections
R = '/home/user/dapparb/research-material'; A = '/home/user/dapparb/analysis/base'
V4_SWAP = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
PM = '0x498581ff718922c3f8e6a244956af099b2652b2b'
ap = argparse.ArgumentParser(); ap.add_argument('--universe', required=True); ap.add_argument('--registry'); ap.add_argument('--out', default=f'{A}/coverage.json')
ap.add_argument('--min-depth', type=float, default=0.1, help='depth threshold applied to the dump (depthEth field)')
ap.add_argument('--registry-universe', action='store_true', help='--universe is a registry file: every accepted pool, no depth filter')
a = ap.parse_args()

new = set()
if a.registry_universe:
    new = set(json.load(open(a.universe))['pools'])
else:
    for l in open(a.universe):
        if not l.strip(): continue
        d = json.loads(l)
        if d.get('depthEth', 1e9) >= a.min_depth: new.add((d.get('poolId') or d['address']).lower())
old = set()
for fn in (f'{R}/04-shallow-pools/pools-prefilter.csv.gz', f'{R}/02-v4-live-test/v4universe-pools-prefilter.csv.gz'):
    for r in csv.DictReader(gzip.open(fn, 'rt')):
        try: dep = float(r['engine_depth_eth_derived'] or 0)
        except ValueError: dep = 0
        if dep >= 0.1: old.add((r.get('v4_pool_id') or r['pool_address']).lower())
oos = None  # (lo, hi) block range of arbitrages no registry block could have seen
if a.registry:
    rg = json.load(open(a.registry))
    oos = (rg['scannedTo'] + 1, 10**12) if rg['scannedTo'] < 51995609 else (0, rg['scannedFrom'] - 1)

rows = list(csv.DictReader(gzip.open(f'{A}/arbs-valued.csv.gz', 'rt')))
want = {r['tx_hash'] for r in rows}
v4ids = collections.defaultdict(set)
idx = list(csv.DictReader(open(f'{R}/05-base-onchain/data/file_index.csv')))
for f in idx:
    if 'candidates' not in f['file']: continue
    for line in gzip.open(f"{R}/05-base-onchain/{f['file']}", 'rt'):
        if V4_SWAP[:20] not in line: continue
        d = json.loads(line)
        if d['tx_hash'] not in want: continue
        for x in d['logs']:
            if x['topics'] and x['topics'][0] == V4_SWAP and x['address'].lower() == PM: v4ids[d['tx_hash']].add(x['topics'][1].lower())

def covered(r, uni):
    pools = set(r['pools'].split()) | v4ids.get(r['tx_hash'], set())
    return int(r['n_swaps']) <= 3 and len(pools) <= 3 and all(p in uni for p in pools)

out = {'min_depth_eth': None if a.registry_universe else a.min_depth, 'universe_sizes': {'old': len(old), 'new': len(new), 'new_minus_old': len(new - old)}, 'oos_before_block': oos}
for label, sel in (('all', lambda r: True), ('non_backrun', lambda r: r['backrun'] == '0')):
    for scope, scope_sel in (('full window', lambda r: True), ('out of sample', lambda r: oos is not None and oos[0] <= int(r['block']) <= oos[1])):
        rs = [r for r in rows if sel(r) and scope_sel(r)]
        G = sum(float(r['gross_usd']) for r in rs)
        if not G: continue
        res = {'arbs': len(rs), 'gross_usd': round(G, 2)}
        for name, uni in (('old', old), ('new', new)):
            g = sum(float(r['gross_usd']) for r in rs if covered(r, uni))
            res[f'{name}_covered_share'] = round(g / G, 3)
        # what the rest is: too many legs, or pools outside
        rest = collections.Counter()
        for r in rs:
            if covered(r, new): continue
            pools = set(r['pools'].split()) | v4ids.get(r['tx_hash'], set())
            k = '4+ legs' if int(r['n_swaps']) > 3 or len(pools) > 3 else ('V4 pool missing' if any(p not in new and len(p) == 66 for p in pools) else 'V2/V3 pool missing')
            rest[k] += float(r['gross_usd'])
        res['new_uncovered_by_reason'] = {k: round(v / G, 3) for k, v in rest.items()}
        out[f'{label} / {scope}'] = res
json.dump(out, open(a.out, 'w'), indent=1)
print(json.dumps(out, indent=1))
