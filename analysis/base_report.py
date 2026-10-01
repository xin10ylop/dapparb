#!/usr/bin/env python3
"""Aggregate analysis/base/arbs.csv.gz with the census tx tables and pool universe into analysis/base/report.json."""
import csv, gzip, glob, json, collections, os
R = '/home/user/dapparb/research-material'; A = '/home/user/dapparb/analysis/base'
USD = 2684.88; BLOCKS = 52017160 - 51995609 + 1; HOURS = BLOCKS * 2 / 3600
arbs = list(csv.DictReader(gzip.open(f'{A}/arbs.csv.gz', 'rt')))
# --- valuation: reliable tokens at engine prices (anchored WETH/USDC pools); long tail only via DefiLlama (confidence >= 0.9) ---
HARD = {'0x4200000000000000000000000000000000000006','0x833589fcd6edb6e08f4c7c32d4f71b54bda02913','0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca',
        '0xfde4c96c8593536e31f229ea8f37b2ada2699bb2','0x50c5725949a6f0c72e6c4a641f24049a917db0cb','0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf',
        '0x2ae3f1ec7f1f5012cfeab0185bfc7aa3cf0dec22','0xc1cba3fcea344f92d9239c08c0568f6f2f0ee452','0x04c0599ae5a44757c0af6f9ec3b93da8976c150a',
        '0x60a3e35cc302bfa44cb288bc5a4f316fdb1adb42','0x2416092f143378750bb29b79ed961ab195cceea5'}
eng = {r['token']: (float(r['engine_price_eth_derived']), int(r['decimals']), r['symbol']) for r in csv.DictReader(gzip.open(f'{R}/02-v4-live-test/v4universe-prices.csv.gz', 'rt')) if r['engine_price_eth_derived']}
dl = {t: v for t, v in json.load(open('/home/user/dapparb/analysis/prices/base-longtail-defillama.json'))['coins'].items() if v.get('confidence', 0) >= 0.9}
def tok_usd(t, raw):
    if t in HARD and t in eng: return raw / 10 ** eng[t][1] * eng[t][0] * USD, 'hard'
    if t in dl: return raw / 10 ** int(dl[t]['decimals']) * dl[t]['price'], 'defillama'
    return None, 'unvalued'
excluded = collections.Counter()
kept = []
for r in arbs:
    # PoolManager payouts to third parties (hook/protocol fees, or a user's recipient) count on the venue side:
    # in the profit token they reduce the profit, in another token they join the venue's gains
    if r.get('profit_token_inflow_raw', '1') in ('0', ''): excluded['no_profit_token_inflow_invisible_leg'] += 1; continue
    pays = [p.split(':') for p in r.get('pm_payouts_other', '').split(';') if p]
    praw = int(r['profit_raw']) - sum(int(v) for _, t, v in pays if t == r['profit_token'])
    if praw <= 0: excluded['payout_consumes_profit'] += 1; continue
    v, how = tok_usd(r['profit_token'], praw); r['_how'] = how
    gains = [g.split(':') for g in r.get('pool_gains', '').split(';') if g] + [[t, v_] for _, t, v_ in pays if t != r['profit_token']]
    gv = 0.0; g_unvalued = False
    for t, raw in gains:
        x, _ = tok_usd(t, int(raw))
        if x is None: g_unvalued = True
        else: gv += x
    if v is None:
        excluded['profit_token_unvalued'] += 1; r['priced'] = '0'; kept.append(r); continue
    if g_unvalued:
        excluded['pool_gain_token_unvalued'] += 1; continue
    if gv > 0.05 * v:
        excluded['pools_gained_other_token_over_5pct'] += 1; continue
    r['gross_usd'] = v - gv; r['priced'] = '1'; r['net_usd'] = r['gross_usd'] - float(r['fee_usd']); kept.append(r)
arbs = kept
big = sorted((r for r in arbs if r['priced'] == '1' and float(r['gross_usd']) > 5000), key=lambda r: -float(r['gross_usd']))
# --- pool universe of the engine (non-V4 from the 04 snapshot; V4 from the 02 rebuild) ---
depth = {}
for fn in (f'{R}/04-shallow-pools/pools-prefilter.csv.gz', f'{R}/02-v4-live-test/v4universe-pools-prefilter.csv.gz'):
    for r in csv.DictReader(gzip.open(fn, 'rt')):
        k = (r.get('v4_pool_id') or r['pool_address']).lower()
        try: depth[k] = max(depth.get(k, 0.0), float(r['engine_depth_eth_derived'] or 0))
        except ValueError: depth.setdefault(k, 0.0)
for r in csv.DictReader(gzip.open(f'{R}/04-shallow-pools/pools-pruned-empty.csv.gz', 'rt')): depth.setdefault(r['pool_address'].lower(), 0.0)
older = set(r['pair'].lower() for r in csv.DictReader(gzip.open(f'{R}/03-v2-older-pairs/pools-part-0001.csv.gz', 'rt')) if r['sample_group'] != 'newest_6000_at_snapshot')
def category(r):
    if int(r['v4_pools'] or 0) > 0:
        if r['v4_hooked'] == '1':
            age = r['v4_min_age_blocks']
            return 'V4 hooked, pool < 1 h old' if age != '' and int(age) < 1800 else 'V4 hooked'
        return 'V4 hookless'
    pools = r['pools'].split()
    if any(p not in depth for p in pools):
        return 'outside engine universe (older V2 pair)' if any(p in older for p in pools) else 'outside engine universe (other)'
    return 'engine universe, a pool < 0.1 ETH' if any(depth[p] < 0.1 for p in pools) else 'engine universe, all pools >= 0.1 ETH'
cat = collections.defaultdict(lambda: collections.Counter())
size = collections.defaultdict(lambda: collections.Counter())
ops = collections.defaultdict(lambda: collections.Counter())
contracts = collections.defaultdict(set)
priced = [r for r in arbs if r['priced'] == '1']
for r in priced:
    g = float(r['gross_usd']); f = float(r['fee_usd']); p = float(r['priority_usd'])
    c = category(r); cat[c]['n'] += 1; cat[c]['gross'] += g; cat[c]['fee'] += f; cat[c]['prio'] += p
    b = '<$0.10' if g < 0.1 else '$0.10-1' if g < 1 else '$1-10' if g < 10 else '$10-100' if g < 100 else '>=$100'
    size[b]['n'] += 1; size[b]['gross'] += g; size[b]['prio'] += p; size[b]['fee'] += f
    ops[r['from']]['n'] += 1; ops[r['from']]['gross'] += g; contracts[r['from']].add(r['to'])
# --- total spend of every arbitrage operator over the window (all its txs: wins, reverts, no-ops) ---
# plus every sender with no valued arbitrage that called one of the arbitrage contracts (zero-win senders)
arbto = set(r['to'] for r in priced)
zero = collections.defaultdict(lambda: collections.Counter()); zero_to = collections.defaultdict(collections.Counter)
pair_spend = collections.Counter(); pair_txs = collections.Counter()
for fn in sorted(glob.glob(f'{R}/05-base-onchain/data/txs-*.csv.gz')):
    for r in csv.DictReader(gzip.open(fn, 'rt')):
        fr = r['from'].lower()
        to_ = (r['to'] or '').lower()
        if fr in ops: o = ops[fr]
        elif to_ in arbto: o = zero[fr]; zero_to[fr][to_] += 1
        else: continue
        cost = int(r['gas_used']) * int(r['effective_gas_price']) / 1e18 + int(r['l1_fee'] or 0) / 1e18
        o['txs'] += 1; o['spend'] += cost * USD; o['reverted'] += (r['status'] == '0')
        pair_spend[(fr, to_)] += cost * USD; pair_txs[(fr, to_)] += 1
with gzip.open(f'{A}/operators.csv.gz', 'wt', newline='') as fo:
    w = csv.writer(fo); w.writerow(['from', 'valued_arbs', 'txs', 'reverted', 'gross_usd', 'spend_usd', 'net_usd', 'contracts'])
    for fr, o in sorted(ops.items(), key=lambda x: -(x[1]['gross'] - x[1]['spend'])):
        w.writerow([fr, o['n'], o['txs'], o['reverted'], round(o['gross'], 4), round(o['spend'], 4), round(o['gross'] - o['spend'], 4), ' '.join(sorted(contracts[fr]))])
    for fr, o in sorted(zero.items(), key=lambda x: x[1]['spend']):
        w.writerow([fr, 0, o['txs'], o['reverted'], 0, round(o['spend'], 4), round(-o['spend'], 4), ''])
nets = sorted(((o['gross'] - o['spend'], fr, o) for fr, o in ops.items()), reverse=True)
tot_g = sum(o['gross'] for o in ops.values()); tot_s = sum(o['spend'] for o in ops.values())
rep = {
  'window': {'blocks': BLOCKS, 'hours': HOURS, 'first_block': 51995609, 'last_block': 52017160, 'eth_usd': USD},
  'excluded_by_reliable_price_check': dict(excluded),
  'arbs': {'detected': len(arbs), 'valued': len(priced), 'valued_hard_token': sum(1 for r in priced if r['_how']=='hard'), 'valued_defillama': sum(1 for r in priced if r['_how']=='defillama'), 'unvalued_long_tail': len(arbs) - len(priced)},
  'over_5000_usd': [{'tx': r['tx_hash'], 'token': r['profit_token'], 'how': r['_how'], 'gross_usd': round(float(r['gross_usd']), 2)} for r in big],
  'totals_priced': {'gross_usd': tot_g, 'gross_usd_per_hour': tot_g / HOURS,
                    'fees_on_arb_txs_usd': sum(float(r['fee_usd']) for r in priced), 'priority_on_arb_txs_usd': sum(float(r['priority_usd']) for r in priced),
                    'operators': len(ops), 'operator_total_spend_usd_all_txs': tot_s, 'operator_net_usd': tot_g - tot_s, 'operator_net_usd_per_hour': (tot_g - tot_s) / HOURS},
  'operators_net_positive': sum(1 for n, _, _ in nets if n > 0),
  'zero_win_senders_to_arb_contracts': {'senders': len(zero), 'txs': sum(o['txs'] for o in zero.values()), 'spend_usd': round(sum(o['spend'] for o in zero.values()), 2)},
  'top_operators': [{'from': fr, 'arbs': o['n'], 'all_txs': o['txs'], 'reverted': o['reverted'], 'gross_usd': round(o['gross'], 2),
                     'spend_usd': round(o['spend'], 2), 'net_usd': round(n, 2), 'net_usd_per_hour': round(n / HOURS, 2), 'contracts': len(contracts[fr])} for n, fr, o in nets[:15]],
  'bottom_operators': [{'from': fr, 'arbs': o['n'], 'all_txs': o['txs'], 'gross_usd': round(o['gross'], 2), 'spend_usd': round(o['spend'], 2), 'net_usd': round(n, 2)} for n, fr, o in nets[-5:]],
  'by_category': {c: {'arbs': v['n'], 'gross_usd': round(v['gross'], 2), 'gross_usd_per_hour': round(v['gross'] / HOURS, 2), 'priority_usd': round(v['prio'], 2),
                      'fees_usd': round(v['fee'], 2), 'priority_share_of_gross': round(v['prio'] / v['gross'], 3) if v['gross'] else None} for c, v in sorted(cat.items(), key=lambda x: -x[1]['gross'])},
  'by_size': {b: {'arbs': v['n'], 'gross_usd': round(v['gross'], 2), 'priority_usd': round(v['prio'], 2), 'priority_share_of_gross': round(v['prio'] / v['gross'], 3) if v['gross'] else None}
              for b, v in sorted(size.items())},
}
# --- operators by beneficiary (the address receiving the profit; bots rotate sender EOAs) ---
def ben(r): return r.get('profit_to') or r['to']
tmp = collections.defaultdict(collections.Counter)
for r in priced: tmp[r['from']][ben(r)] += 1
eoa_ben = {e: c.most_common(1)[0][0] for e, c in tmp.items()}
tmp = collections.defaultdict(collections.Counter)
for r in priced: tmp[r['to']][ben(r)] += 1
con_ben = {}  # contract -> its beneficiary when one beneficiary takes >= 90% of its valued arbs (a bot contract, not a public router)
for c_, cnt in tmp.items():
    b, n = cnt.most_common(1)[0]
    if n >= 0.9 * sum(cnt.values()): con_ben[c_] = b
B = collections.defaultdict(lambda: collections.Counter()); unattributed = collections.Counter()
for r in priced: B[ben(r)]['gross'] += float(r['gross_usd']); B[ben(r)]['arbs'] += 1
# each tx's cost goes to the beneficiary of the contract it called (when that contract has one dominant beneficiary),
# else to the sender's main beneficiary; a zero-win sender calling a shared contract (public router) stays unattributed
eoas = collections.defaultdict(set)
for (e, c_), sp in pair_spend.items():
    b_ = con_ben.get(c_) or eoa_ben.get(e)
    if b_ is None: unattributed['txs'] += pair_txs[(e, c_)]; unattributed['spend'] += sp; unattributed['_s_' + e] = 1; continue
    B[b_]['spend'] += sp; B[b_]['txs'] += pair_txs[(e, c_)]; eoas[b_].add(e)
for b_, es in eoas.items(): B[b_]['eoas'] = len(es); B[b_]['zero_win_eoas'] = sum(1 for e in es if e in zero)
unattributed = {'senders': sum(1 for k in unattributed if k.startswith('_s_')), 'txs': unattributed['txs'], 'spend': unattributed['spend']}
bn = sorted(((v['gross'] - v['spend'], k, v) for k, v in B.items()), reverse=True)
posum = sum(n for n, _, _ in bn if n > 0)
rep['operators_by_beneficiary'] = {
  'beneficiaries': len(bn), 'net_positive': sum(1 for n, _, _ in bn if n > 0), 'share_net_positive': round(sum(1 for n, _, _ in bn if n > 0) / len(bn), 3),
  'total_net_usd_per_hour': round(sum(n for n, _, _ in bn) / HOURS, 2),
  'unattributed_txs (zero-win senders calling shared contracts)': {k: round(v, 2) for k, v in unattributed.items()},
  'top_k_share_of_positive_net': {k: round(sum(n for n, _, _ in bn[:k]) / posum, 3) for k in (1, 3, 10, 30, 100)},
  'count_net_over_usd_per_hour': {t: sum(1 for n, _, _ in bn if n / HOURS > t) for t in (0.5, 1, 5, 10, 25, 50)},
  'top': [{'beneficiary': k, 'arbs': v['arbs'], 'eoas': v['eoas'], 'zero_win_eoas': v['zero_win_eoas'], 'txs': v['txs'], 'gross_usd': round(v['gross'], 2),
           'spend_usd': round(v['spend'], 2), 'net_usd_per_hour': round(n / HOURS, 2)} for n, k, v in bn[:20]]}
# --- same-block backruns: another sender swapped one of the arb's pools earlier in the same block ---
bk = collections.defaultdict(lambda: collections.Counter())
for r in priced:
    c_ = category(r); f = r.get('prior_swap_same_pool_same_block') == '1'; g = float(r['gross_usd'])
    for key in (c_, 'ALL'):
        bk[key]['n'] += 1; bk[key]['g'] += g; bk[key]['bn'] += f; bk[key]['bg'] += g * f
rep['backrun_share'] = {k: {'arbs': v['n'], 'share_of_arbs': round(v['bn'] / v['n'], 3), 'share_of_gross': round(v['bg'] / v['g'], 3) if v['g'] else None} for k, v in bk.items()}
json.dump(rep, open(f'{A}/report.json', 'w'), indent=1)
with gzip.open(f'{A}/arbs-valued.csv.gz', 'wt', newline='') as fo:
    w = csv.writer(fo); w.writerow(['block', 'tx_index', 'tx_hash', 'from', 'to', 'profit_to', 'category', 'profit_token', 'valued_by', 'gross_usd', 'fee_usd', 'priority_usd', 'n_swaps', 'backrun', 'pools'])
    for r in sorted(priced, key=lambda r: -float(r['gross_usd'])):
        w.writerow([r['block'], r['tx_index'], r['tx_hash'], r['from'], r['to'], r.get('profit_to', ''), category(r), r['profit_token'], r['_how'], round(float(r['gross_usd']), 4), r['fee_usd'], r['priority_usd'], r['n_swaps'], r.get('prior_swap_same_pool_same_block', ''), r['pools']])
print(json.dumps({k: rep[k] for k in ('window', 'arbs', 'totals_priced', 'operators_net_positive')}, indent=1))
print(json.dumps(rep['by_category'], indent=1)); print(json.dumps(rep['by_size'], indent=1))
print(json.dumps({k: v for k, v in rep['operators_by_beneficiary'].items() if k != 'top'}, indent=1)); print(json.dumps(rep['backrun_share'], indent=1))
for t in rep['operators_by_beneficiary']['top'][:10]: print('ben', t)
for t in rep['top_operators'][:10]: print(t)
for t in rep['bottom_operators']: print('bottom', t)
