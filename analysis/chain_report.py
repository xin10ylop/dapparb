#!/usr/bin/env python3
"""Per-chain arbitrage report for the other-chain censuses (DefiLlama prices, confidence >= 0.9, strict pool-gain check;
V4 PoolManager payouts to third parties count on the venue side, as in base_report.py)."""
import csv, gzip, glob, json, collections, sys, os
R = '/home/user/dapparb/research-material/06-other-chains-onchain'; A = '/home/user/dapparb/analysis'
CH = {'arbitrum': (2677.8167, 'arbitrum'), 'optimism': (2677.8167, 'optimism'), 'unichain': (2677.8167, 'unichain'),
      'ethereum': (2679.9075, 'ethereum'), 'polygon': (0.1118, 'polygon'), 'ink': (2690.9298, 'ink'), 'mantle': (0.6938, 'mantle'),
      'abstract': (2690.9298, 'abstract'), 'worldchain': (2690.9298, 'worldchain'), 'zksync': (2690.9555, 'zksync'),
      'soneium': (2690.9298, 'soneium'), 'bsc': (766.4748, 'bsc/census')}
out = {}
for c, (usd, folder) in CH.items():
    price = {}
    for r in csv.DictReader(open(f'{A}/prices/{c}.csv')):
        conf = r['confidence']
        try: ok = conf in ('manual',) or conf.startswith('defillama') or float(conf or 0) >= 0.9
        except ValueError: ok = False
        if ok: price[r['token']] = (float(r['price_native']) * usd, int(r['decimals']))
    def val(t, raw):
        p = price.get(t); return raw / 10 ** p[1] * p[0] if p else None
    blocks = list(csv.DictReader(gzip.open(f'{R}/{folder}/blocks.csv.gz', 'rt')))
    t0 = int(blocks[0]['timestamp']); t1 = int(blocks[-1]['timestamp']); hours = max(t1 - t0, 1) / 3600
    excl = collections.Counter(); arbs = []
    for r in csv.DictReader(gzip.open(f'{A}/chains/{c}/arbs.csv.gz', 'rt')):
        if r.get('profit_token_inflow_raw', '1') in ('0', ''): excl['no_profit_token_inflow_invisible_leg'] += 1; continue
        pays = [p.split(':') for p in (r.get('pm_payouts_other') or '').split(';') if p]
        praw = int(r['profit_raw']) - sum(int(x) for _, t, x in pays if t == r['profit_token'])
        if praw <= 0: excl['payout_consumes_profit'] += 1; continue
        v = val(r['profit_token'], praw)
        gains = [g.split(':') for g in r.get('pool_gains', '').split(';') if g] + [[t, x] for _, t, x in pays if t != r['profit_token']]
        gv = 0.0; gun = False
        for t, raw in gains:
            x = val(t, int(raw)); gun |= x is None; gv += x or 0
        if v is None: excl['profit_token_unvalued'] += 1; continue
        if gun: excl['pool_gain_token_unvalued'] += 1; continue
        if gv > 0.05 * v: excl['pools_gained_other_token_over_5pct'] += 1; continue
        r['g'] = v - gv; r['f'] = float(r['fee_native']) * usd; r['p'] = float(r['priority_native']) * usd; arbs.append(r)
    with gzip.open(f'{A}/chains/{c}/arbs-valued.csv.gz', 'wt', newline='') as fo:
        w = csv.writer(fo); w.writerow(['block', 'tx_index', 'tx_hash', 'from', 'to', 'profit_to', 'profit_token', 'gross_usd', 'fee_usd', 'priority_usd', 'n_swaps', 'v4_pools', 'backrun', 'pools'])
        for r in sorted(arbs, key=lambda r: -r['g']):
            w.writerow([r['block'], r['tx_index'], r['tx_hash'], r['from'], r['to'], r.get('profit_to', ''), r['profit_token'], round(r['g'], 4), round(r['f'], 6), round(r['p'], 6), r['n_swaps'], r['v4_pools'], r.get('prior_swap_same_pool_same_block', ''), r['pools']])
    ops = collections.defaultdict(lambda: collections.Counter())
    for r in arbs: ops[r['from']]['n'] += 1; ops[r['from']]['g'] += r['g']
    pos = {}
    for fn in sorted(glob.glob(f'{R}/{folder}/txs-*.csv.gz')):
        for r in csv.DictReader(gzip.open(fn, 'rt')):
            fr = r['from'].lower()
            if (r['to'] or '').lower() and fr in ops:
                l1 = r.get('l1_fee') or '0'
                l1 = int(l1, 16) if str(l1).startswith('0x') else int(l1 or 0)
                o = ops[fr]; o['txs'] += 1; o['rev'] += r['status'] in ('0', '0x0'); o['s'] += (int(r['gas_used']) * int(r['effective_gas_price']) + l1) / 1e18 * usd
    G = sum(r['g'] for r in arbs); S = sum(o['s'] for o in ops.values())
    nets = sorted((o['g'] - o['s'] for o in ops.values()), reverse=True)
    big = sorted(arbs, key=lambda r: -r['g'])[:5]
    sz = collections.defaultdict(lambda: [0, 0.0, 0.0])
    for r in arbs:
        b = '<$1' if r['g'] < 1 else '$1-10' if r['g'] < 10 else '$10-100' if r['g'] < 100 else '>=$100'
        sz[b][0] += 1; sz[b][1] += r['g']; sz[b][2] += r['p']
    bg = collections.Counter(); bcount = collections.Counter()
    for r in arbs: bg[r.get('profit_to') or r['to']] += r['g']; bcount[r.get('profit_to') or r['to']] += 1
    bb = sorted(bg.values(), reverse=True)
    v4g = sum(r['g'] for r in arbs if int(r['v4_pools'] or 0) > 0)
    out[c] = {'hours': round(hours, 3),
              'beneficiaries': len(bg), 'top3_beneficiary_gross_share': round(sum(bb[:3]) / G, 3) if G else None,
              'backrun_share_of_gross': round(sum(r['g'] for r in arbs if r.get('prior_swap_same_pool_same_block') == '1') / G, 3) if G else None,
              'v4_share_of_gross': round(v4g / G, 3) if G else None,
              'v4_unresolved_txs_skipped': json.load(open(f'{A}/chains/{c}/arbs-meta.json'))['counts'].get('v4_unresolved_tx', 0), 'blocks': len(blocks), 'arbs_valued': len(arbs), 'excluded': dict(excl),
              'gross_usd': round(G, 2), 'gross_usd_per_hour': round(G / hours, 2), 'fees_on_arbs_usd': round(sum(r['f'] for r in arbs), 2),
              'priority_on_arbs_usd': round(sum(r['p'] for r in arbs), 2), 'operators': len(ops), 'operator_spend_all_txs_usd': round(S, 2),
              'operator_net_usd_per_hour': round((G - S) / hours, 2), 'operators_net_positive': sum(1 for n in nets if n > 0),
              'top3_net_share': round(sum(nets[:3]) / max(sum(n for n in nets if n > 0), 1e-9), 3) if nets else None,
              'largest': [{'tx': r['tx_hash'], 'gross_usd': round(r['g'], 2), 'priority_usd': round(r['p'], 4)} for r in big],
              'by_size': {b: {'arbs': v[0], 'gross_usd': round(v[1], 2), 'priority_share': round(v[2] / v[1], 3) if v[1] else None} for b, v in sorted(sz.items())}}
    print(c, json.dumps({k: out[c][k] for k in ('hours', 'arbs_valued', 'gross_usd_per_hour', 'operator_net_usd_per_hour', 'operators', 'operators_net_positive', 'beneficiaries',
                                                'top3_beneficiary_gross_share', 'backrun_share_of_gross', 'v4_share_of_gross', 'v4_unresolved_txs_skipped', 'excluded')}))
json.dump(out, open(f'{A}/chains/report.json', 'w'), indent=1)
