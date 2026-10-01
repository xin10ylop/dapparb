#!/usr/bin/env python3
"""Summarise a dry run of the engine (bot/data/live-*.jsonl written by main.ts --mode dry --source logs).

Reports simulations at the block the state came from (simAtBlock) and at `latest` (sim), the simulated value per hour,
and how much of the simulated value needed the coverage extension: routes with three legs (event-mode triangles) and
routes through a pool outside the old factory universe (research-material 04 prefilter / 02 V4 rebuild, depth >= 0.1).

usage: dryrun_summary.py ../bot/data/live-final.jsonl [--log ../bot/data/final.log]
"""
import sys, json, csv, gzip, collections, re, datetime
R = '/home/user/dapparb/research-material'
f = sys.argv[1]
old = set()
for fn in (f'{R}/04-shallow-pools/pools-prefilter.csv.gz', f'{R}/02-v4-live-test/v4universe-pools-prefilter.csv.gz'):
    for r in csv.DictReader(gzip.open(fn, 'rt')):
        try: dep = float(r['engine_depth_eth_derived'] or 0)
        except ValueError: dep = 0
        if dep >= 0.1:
            k = (r.get('v4_pool_id') or r['pool_address']).lower()
            old.add(k[:42])  # V4 pools appear in routes under their synthetic address (first 20 bytes of the id)
recs = [json.loads(l) for l in open(f) if l.strip()]
sims = [r for r in recs if 'sim' in r]
t = [datetime.datetime.fromisoformat(r['t'].replace('Z', '+00:00')) for r in recs if 't' in r]
hours = (max(t) - min(t)).total_seconds() / 3600 if t else 0
err = lambda d: re.sub(r'\(.*', '', (d or {}).get('error') or 'OK')
pin = collections.Counter(err(r.get('simAtBlock')) for r in sims if 'simAtBlock' in r)
lat = collections.Counter(err(r['sim']) for r in sims)
ok_pin = [r for r in sims if r.get('simAtBlock') and not r['simAtBlock'].get('error')]
ok_lat = [r for r in sims if not r['sim'].get('error')]
def value(rs, key): return sum((r[key] or {}).get('profitUsd', 0) for r in rs)
def net(rs): return sum(r.get('simNetUsd') or 0 for r in rs)
def split(rs, key):
    out = collections.Counter()
    for r in rs:
        v = (r[key] or {}).get('profitUsd', 0)
        newpool = any(p.lower()[:42] not in old for p in r['pools'])
        out['3 legs' if len(r['pools']) == 3 else '2 legs'] += v
        out['uses a pool outside the old universe' if newpool else 'old-universe pools only'] += v
    return {k: round(v, 4) for k, v in out.items()}
rep = {'file': f, 'hours': round(hours, 3), 'simulations': len(sims), 'pinned': dict(pin), 'latest': dict(lat),
       'ok_at_block': {'n': len(ok_pin), 'gross_usd': round(value(ok_pin, 'simAtBlock'), 4), 'gross_usd_per_hour': round(value(ok_pin, 'simAtBlock') / hours, 4) if hours else None, 'split': split(ok_pin, 'simAtBlock')},
       'ok_at_latest': {'n': len(ok_lat), 'gross_usd': round(value(ok_lat, 'sim'), 4), 'net_after_gas_usd': round(net(ok_lat), 4), 'net_usd_per_hour': round(net(ok_lat) / hours, 4) if hours else None, 'split': split(ok_lat, 'sim')},
       'distinct_ok_routes': len(set(r['route'] for r in ok_lat)), 'ok_routes': collections.Counter(r['route'] for r in ok_lat).most_common(10)}
if '--log' in sys.argv:
    lg = open(sys.argv[sys.argv.index('--log') + 1]).read()
    rep['tokens_parked'] = lg.count('token parked'); rep['live_merges'] = lg.count('live-discovered pools merged')
print(json.dumps(rep, indent=1))
