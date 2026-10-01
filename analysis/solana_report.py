#!/usr/bin/env python3
"""Cyclic-arbitrage detector for the Solana 600-slot sample, venue-side (same test as the EVM classifier).

Input: research-material/06-other-chains-onchain/solana/data/raw-slots (local-only full getBlock JSON).
For each successful non-vote tx with at least two AMM legs (invocations of a known DEX program from dex-programs.csv
that is not an aggregator/router, not counting a program's self-CPI event logs):
  * trader side = the tx's signers; venue side = every other account.
  * venue flows = SPL token balance changes of token accounts not owned by a signer (per mint; wSOL merged into SOL)
    + native lamport changes of non-signer, non-token accounts (pump.fun curves hold native SOL), excluding the 8 Jito
    tip accounts (tips are a cost).
  * arbitrage = the venue loses exactly one asset, and any other asset it gains is priced and worth <= 5% of that loss;
    and the signers' own balances mirror it: that asset is the only one up (SOL before fee and tips) and none is down
    (SOL may move by <= 0.01 SOL of token-account rent when the profit is an SPL token).
  * dropped: txs where a DEX program logged an instruction whose name contains liquidity, deposit, withdraw, claim,
    position, rebalance, harvest, collect, migrate, lock, reward, fee, distribute, cancel or order.
Gross = the venue's loss net of the other assets it gained, valued at DefiLlama (confidence >= 0.9).
Costs = tx fee + Jito tips. Limits: a bot whose profit lands in an account owned by its own program (not a signer) fails the trader-side test
and is not detected, so this undercounts PDA-vault bots."""
import collections, csv, glob, gzip, json, re
S = '/home/user/dapparb/research-material/06-other-chains-onchain/solana'
WSOL = 'So11111111111111111111111111111111111111112'
dex = {r['program_id']: r['name'] for r in csv.DictReader(open(f'{S}/dex-programs.csv'))}
tips = set(r[list(r)[0]] for r in csv.DictReader(open(f'{S}/jito-tip-accounts.csv')))
ROUTERS = {p for p, n in dex.items() if re.search(r'Aggregat|Routing|DCA|Limit Order|DFlow|OKX|Lend Earn|JupiterRfq', n)}
LIQ = re.compile(r'liquidity|deposit|withdraw|claim|position|rebalance|harvest|collect|migrate|lock|reward|fee|distribute|cancel|order', re.I)
px = {}
for l in gzip.open(f'{S}/prices-defillama-historical.jsonl.gz', 'rt'):
    for k, v in ((json.loads(l).get('body') or {}).get('coins') or {}).items():
        if v.get('confidence', 0) >= 0.9: px[k] = v
SOL = px['coingecko:solana']['price']
def usd(asset, raw):
    if asset == 'SOL': return raw / 1e9 * SOL
    q = px.get('solana:' + asset)
    return raw / 10 ** q['decimals'] * q['price'] if q else None
slots = list(csv.DictReader(gzip.open(f'{S}/slots.csv.gz', 'rt')))
secs = int(slots[-1]['block_time']) - int(slots[0]['block_time']) + 0.4
H = secs / 3600
st = collections.Counter(); arbs = []; fails = collections.Counter(); failfee = collections.Counter()
for fn in sorted(glob.glob(f'{S}/data/raw-slots/slot-*.json.gz')):
    blk = json.load(gzip.open(fn))
    for e in blk['nonvote']:
        tx = e['tx']; m = tx['meta']; msg = tx['transaction']['message']
        stack = []; ndex = 0; legs = 0; names = set(); progs = set()
        for line in m.get('logMessages') or []:
            if line.startswith('Program ') and ' invoke [' in line:
                p = line.split()[1]
                if p in dex:
                    ndex += 1; progs.add(dex[p])
                    if p not in ROUTERS and (not stack or stack[-1] != p): legs += 1  # a self-CPI is an event log, not a swap
                stack.append(p)
            elif line.startswith('Program ') and (line.endswith(' success') or ' failed' in line) and stack: stack.pop()
            elif line.startswith('Program log: Instruction: ') and stack and stack[-1] in dex: names.add(line[26:].strip())
        if ndex == 0: continue
        if m.get('err') is not None:
            k0 = msg['accountKeys'][0]; fails[k0] += 1; failfee[k0] += m['fee']; st['dex_failed'] += 1; continue
        st['dex_ok'] += 1
        if legs < 2: continue
        st['dex_ok_2plus_amm_legs'] += 1
        if any(LIQ.search(x) for x in names): st['liquidity_or_fee_op_excluded'] += 1; continue
        keys = list(msg['accountKeys']) + m['loadedAddresses']['writable'] + m['loadedAddresses']['readonly']
        signers = set(keys[:msg['header']['numRequiredSignatures']])
        venue = collections.Counter(); tokacc = set()
        for sign, k in ((-1, 'preTokenBalances'), (1, 'postTokenBalances')):
            for b in m[k]:
                tokacc.add(b['accountIndex'])
                if b.get('owner') in signers: continue
                mint = 'SOL' if b['mint'] == WSOL else b['mint']
                venue[mint] += sign * int(b['uiTokenAmount']['amount'])
        tip = 0
        for i, (a, b) in enumerate(zip(m['preBalances'], m['postBalances'])):
            k = keys[i]
            if k in tips: tip += max(0, b - a); continue
            if k in signers or i in tokacc: continue
            venue['SOL'] += b - a
        neg = [(t, v) for t, v in venue.items() if v < 0]; pos = [(t, v) for t, v in venue.items() if v > 0]
        if len(neg) != 1: continue
        # trader side must mirror it: signers' own assets (SOL before fee and tips, wSOL merged) - one up, none down
        trader = collections.Counter()
        for sign, k in ((-1, 'preTokenBalances'), (1, 'postTokenBalances')):
            for b in m[k]:
                if b.get('owner') in signers: trader['SOL' if b['mint'] == WSOL else b['mint']] += sign * int(b['uiTokenAmount']['amount'])
        for i, (a, b) in enumerate(zip(m['preBalances'], m['postBalances'])):
            if keys[i] in signers: trader['SOL'] += b - a
        trader['SOL'] += m['fee'] + tip
        if neg[0][0] != 'SOL' and abs(trader['SOL']) <= 10_000_000: trader['SOL'] = 0  # token-account rent paid or refunded
        tdown = [t for t, v in trader.items() if v < 0]; tup = [t for t, v in trader.items() if v > 0]
        if tdown or tup != [neg[0][0]]: st['venue_only_not_trader'] += 1; continue
        asset, raw = neg[0][0], -neg[0][1]
        loss = usd(asset, raw)
        if loss is None: st['arb_profit_unpriced'] += 1; continue
        gv = [usd(t, v) for t, v in pos]
        if any(x is None for x in gv): st['excluded_gain_unpriced'] += 1; continue
        if sum(gv) > 0.05 * loss: st['excluded_gain_over_5pct'] += 1; continue
        st['arb_priced'] += 1
        arbs.append({'sig': tx['transaction']['signatures'][0], 'slot': blk['slot'], 'signer': keys[0], 'asset': asset,
                     'gross_usd': loss - sum(gv), 'fee_usd': m['fee'] / 1e9 * SOL, 'tip_usd': tip / 1e9 * SOL,
                     'dex_invocations': ndex, 'programs': sorted(progs), 'dex_instructions': sorted(names)})
g = sum(a['gross_usd'] for a in arbs); f = sum(a['fee_usd'] for a in arbs); t = sum(a['tip_usd'] for a in arbs)
size = collections.defaultdict(lambda: collections.Counter())
for a in arbs:
    x = a['gross_usd']; b = '<$0.10' if x < .1 else '$0.10-1' if x < 1 else '$1-10' if x < 10 else '$10-100' if x < 100 else '>=$100'
    size[b]['n'] += 1; size[b]['gross'] += x; size[b]['cost'] += a['fee_usd'] + a['tip_usd']
sg = collections.defaultdict(lambda: collections.Counter())
for a in arbs: s = sg[a['signer']]; s['n'] += 1; s['gross'] += a['gross_usd']; s['cost'] += a['fee_usd'] + a['tip_usd']
rep = {'window': {'slots': len(slots), 'seconds': secs, 'sol_usd': SOL}, 'counts': dict(st),
       'priced_arbs': len(arbs), 'gross_usd': g, 'gross_usd_per_hour': g / H, 'tx_fees_usd': f, 'jito_tips_usd': t,
       'cost_share_of_gross': (f + t) / g if g else None, 'net_after_fees_tips_usd_per_hour': (g - f - t) / H,
       'profit_asset_sol_share': sum(1 for a in arbs if a['asset'] == 'SOL') / max(1, len(arbs)),
       'by_size': {b: {'arbs': v['n'], 'gross_usd': round(v['gross'], 2), 'fee_tip_share': round(v['cost'] / v['gross'], 3) if v['gross'] else None} for b, v in sorted(size.items())},
       'signers': len(sg), 'failed_dex_tx_fees_of_arb_signers_usd': sum(failfee[s] for s in sg) / 1e9 * SOL,
       'operator_net_usd_per_hour_after_failed_fees': (g - f - t - sum(failfee[s] for s in sg) / 1e9 * SOL) / H,
       'signers_net_positive_after_failed_fees': sum(1 for s, v in sg.items() if v['gross'] - v['cost'] - failfee[s] / 1e9 * SOL > 0),
       'top_signers': [{'signer': s, 'arbs': v['n'], 'gross_usd': round(v['gross'], 2), 'fee_tip_usd': round(v['cost'], 3), 'failed_dex_txs': fails[s],
                        'failed_fee_usd': round(failfee[s] / 1e9 * SOL, 3), 'net_usd': round(v['gross'] - v['cost'] - failfee[s] / 1e9 * SOL, 2)}
                                           for s, v in sorted(sg.items(), key=lambda x: -x[1]['gross'])[:15]],
       'top_arbs': sorted(arbs, key=lambda a: -a['gross_usd'])[:25]}
json.dump(rep, open('/home/user/dapparb/analysis/chains/solana-report.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k not in ('top_arbs', 'top_signers')}, indent=1))
for s in rep['top_signers'][:8]: print(s)
for a in rep['top_arbs'][:15]: print(round(a['gross_usd'], 2), a['sig'][:20], a['signer'][:8], a['asset'][:8], a['programs'][:3], a['dex_instructions'][:4], round(a['tip_usd'], 3))
