#!/usr/bin/env python3
"""Cyclic-arbitrage classifier over an EVM on-chain census (research-material/05-base-onchain or 06-*/<chain>).

A transaction is a cyclic arbitrage when it has >= 2 swap logs and the swap venues it touched, taken together,
lose exactly one token on net while every other token nets to zero (pools only received back what they paid out).
Pool-side flows: ERC-20 Transfer logs to/from swap-log emitters (V2/V3/Slipstream/Curve/Balancer/...), plus Uniswap V4
Swap event deltas (pool side = -event amounts, native ETH counted as WETH); PoolManager Transfers count only where the other
side is a pool. Hook fees minted as ERC-6909 claims to third parties count as venue gains; PoolManager ERC-20 payouts to addresses other than
the sender/contract/pools are listed in pm_payouts_other (recipient:token:raw) for the report to decide.
Gross profit = value of the token the venues lost, minus the value of any other token they net-gained (tolerance).
profit_to = the non-pool address receiving most of the profit token (operator identity; bots rotate sender EOAs).
WETH Deposit/Withdrawal on a pool count as its inflow/outflow. ERC-6909 claims of the sender/contract are ignored (settlement).
profit_token_inflow_raw = how much of the profit token was paid into the venues; 0 means a leg was invisible (native ETH sent
to a pool), so the report drops the row.
prior_swap_same_pool_same_block = another sender's successful swap touched one of the arb's pools earlier in the block.
Costs: gas_used * effective_gas_price + L1 fee. Priority fee: gas_used * (effective_gas_price - base_fee).
Usage: arb_census.py --census DIR --chain base --out OUTDIR [--prices file.csv.gz] [--v4-init glob ...]
"""
import argparse, csv, glob, gzip, json, os, sys, time, collections

T_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
V4_SWAP = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
ZERO = '0x0000000000000000000000000000000000000000'
WETH_DEPOSIT = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c'  # Deposit(address indexed dst, uint wad)
WETH_WITHDRAWAL = '0x7fcf532c15f0a6db0bd6d0e038bea71d30d808c7d98cb3bf7268a95bf5081b65'  # Withdrawal(address indexed src, uint wad)
ERC6909 = '0x1b3d7edb2e9c0b0e7c525b20aaaef0f5940d2ed71663c7d39266ecafac728859'  # PoolManager claim Transfer(caller, from, to, id, amount)
AERO_FEES = '0x112c256902bf554b6ed882d2936687aaeb4225e8cd5b51303c90ca6cf43a8602'  # Fees(address,uint256,uint256): pool forwards fee to its PoolFees contract
LIQ_TOPICS = {  # liquidity add/remove/collect: a pool losing a token here is not trading profit
    '0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c',  # V3 Burn
    '0x70935338e69775456a85ddef226c395fb668b63fa0115f5f20610b388e6ca9c0',  # V3 Collect
    '0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde',  # V3 Mint
    '0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f',  # V2 Mint
    '0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496',  # V2 Burn
    '0x5d624aa9c148153ab3446c1b154f660ee7701e549fe9b62dab7171b1c80e6fa2',  # Aerodrome V2 Burn
    '0x205860e66845f2bbc0966bfab80db9bf93fca93862ea2b9fcf6945748352b4a3',  # CollectFees
    '0x596b573906218d3411850b26a6b437d6c4522fdb43d2d2386263f86d50b8b151',  # CollectProtocol
    '0x865ca08d59f5cb456e85cd2f7ef63664ea4f73327414e9d8152c4158b0e94645',  # Aerodrome Claim
}

def s256(h):
    v = int(h, 16); return v - (1 << 256) if v >= 1 << 255 else v

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--census', required=True); ap.add_argument('--chain', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--weth', required=True); ap.add_argument('--pool-manager', default='')
    ap.add_argument('--prices', action='append', default=[]); ap.add_argument('--v4-init', action='append', default=[])
    ap.add_argument('--native-usd', type=float, required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    WETH = a.weth.lower(); PM = a.pool_manager.lower()
    topics = set()
    for r in csv.DictReader(open(os.path.join(a.census, 'swap-topics.csv'))):
        if r['topic0'].startswith('0x'): topics.add(r['topic0'].lower())
    # prices: token -> (price in native, decimals)
    price = {}
    for pf in a.prices:
        for r in csv.DictReader(gzip.open(pf, 'rt') if pf.endswith('.gz') else open(pf)):
            t = (r.get('token') or r.get('address') or '').lower()
            p = r.get('engine_price_eth_derived') or r.get('price_eth') or r.get('price_native') or ''
            d = r.get('decimals') or r.get('decimals_engine') or ''
            if p and d and t not in price:
                try: price[t] = (float(p), int(d))
                except ValueError: pass
    price.setdefault(WETH, (1.0, 18))
    # base fee per block
    basefee = {}
    bf = os.path.join(a.census, 'blocks.csv.gz')
    for r in csv.DictReader(gzip.open(bf, 'rt')):
        basefee[int(r['block_number'])] = int(r['base_fee_per_gas'] or 0)
    files = sorted(glob.glob(os.path.join(a.census, 'data', 'candidates-*.jsonl.gz')) + glob.glob(os.path.join(a.census, 'candidates-*.jsonl.gz')))
    recs = []; nlines = 0; t0 = time.time(); nliq = [0]
    touches = collections.defaultdict(list)  # block -> [(tx_index, from, {pool keys})] for every successful swap tx
    for fn in files:
        for line in gzip.open(fn, 'rt'):
            nlines += 1
            d = json.loads(line)
            if int(d.get('status', 1)) != 1: continue
            logs = d['logs']
            swaps = [x for x in logs if x['topics'] and x['topics'][0].lower() in topics]
            if swaps:
                touches[int(d['block_number'])].append((int(d['tx_index']), d['from'].lower(),
                    frozenset(x['topics'][1].lower() if (PM and x['address'].lower() == PM and len(x['topics']) > 1) else x['address'].lower() for x in swaps)))
            if len(swaps) < 2: continue
            pools = set(x['address'].lower() for x in swaps if x['address'].lower() != PM)
            if any(x['topics'] and x['topics'][0].lower() in LIQ_TOPICS for x in logs):
                nliq[0] += 1; continue
            net = collections.defaultdict(int); transfers_from_pool = []; pm_out = collections.defaultdict(int)
            bot = {d['from'].lower(), (d['to'] or '').lower()}
            outside = collections.defaultdict(collections.Counter)  # non-pool address -> token -> net received
            inflow = collections.Counter()  # token -> amount paid into the venues (a real cycle pays its profit token in)
            # Aerodrome V2: the fee leaves the pool for its PoolFees contract in a separate Transfer; add it back
            fee_back = []
            for x in logs:
                if x['topics'] and x['topics'][0].lower() == AERO_FEES and x['address'].lower() in pools:
                    w0 = x['data'][2:]; fee_back.append((x['address'].lower(), int(w0[0:64], 16), int(w0[64:128], 16)))
            for x in logs:
                tp = x['topics']
                if not tp or tp[0].lower() != T_TRANSFER or len(tp) != 3: continue
                f = '0x' + tp[1][-40:].lower(); t = '0x' + tp[2][-40:].lower(); tok = x['address'].lower()
                if PM and f == PM and t not in pools and t not in bot: pm_out[(t, tok)] += int(x['data'], 16) if x['data'] not in ('0x', '') else 0
                try: amt = int(x['data'], 16) if x['data'] not in ('0x', '') else 0
                except ValueError: continue
                if t in pools: net[tok] += amt; inflow[tok] += amt
                if f in pools: net[tok] -= amt
                if t not in pools and t != PM and t != ZERO: outside[t][tok] += amt
                if f not in pools and f != PM and f != ZERO: outside[f][tok] -= amt
                if f in pools and fee_back: transfers_from_pool.append((f, tok, amt))
            # match each Fees event to the pool's outgoing Transfer of exactly that fee amount and undo it
            for (pa, f0, f1) in fee_back:
                for famt in (f0, f1):
                    if famt == 0: continue
                    for i, (fp, tok, amt) in enumerate(transfers_from_pool):
                        if fp == pa and amt == famt:
                            net[tok] += amt; transfers_from_pool.pop(i); break
            # native ETH wrapped into / unwrapped out of a pool's own WETH balance emits Deposit/Withdrawal, not Transfer
            for x in logs:
                tp = x['topics']
                if tp and x['address'].lower() == WETH and len(tp) == 2 and tp[0].lower() in (WETH_DEPOSIT, WETH_WITHDRAWAL):
                    who = '0x' + tp[1][-40:].lower()
                    if who in pools:
                        amt = int(x['data'], 16)
                        if tp[0].lower() == WETH_DEPOSIT: net[WETH] += amt; inflow[WETH] += amt
                        else: net[WETH] -= amt
            # V4 hook fees minted as PoolManager claims (ERC-6909) to anyone but the sender/contract count as venue gains,
            # claims such a third party burns as venue losses
            for x in logs:
                tp = x['topics']
                if PM and x['address'].lower() == PM and tp and tp[0].lower() == ERC6909 and len(tp) == 4:
                    fa = '0x' + tp[1][-40:].lower(); ta = '0x' + tp[2][-40:].lower(); cid = int(tp[3], 16)
                    cur = WETH if cid == 0 else '0x' + format(cid, '040x'); amt = int(x['data'][2 + 64:2 + 128], 16)
                    # claims minted to / burned by the sender or its contract are its own settlement: not venue flows
                    if fa == ZERO and ta not in bot: net[cur] += amt
                    elif ta == ZERO and fa not in bot: net[cur] -= amt
            v4 = []
            for x in swaps:
                if PM and x['address'].lower() == PM and x['topics'][0].lower() == V4_SWAP:
                    w = x['data'][2:]; v4.append((x['topics'][1].lower(), s256(w[0:64]), s256(w[64:128])))
            rc = d.get('receipt', {})
            l1 = rc.get('l1Fee'); l1 = int(l1, 16) if isinstance(l1, str) and l1.startswith('0x') else int(l1 or 0)
            recs.append((int(d['block_number']), int(d['tx_index']), d['tx_hash'], d['from'].lower(), (d['to'] or '').lower(),
                         int(d['gas_used']), int(d['effective_gas_price']), l1, dict(net), v4, sorted(pools), len(swaps),
                         ';'.join(f'{t}:{k}:{v}' for (t, k), v in pm_out.items() if v),
                         {a: dict(c) for a, c in outside.items() if any(v > 0 for v in c.values())}, dict(inflow)))
            if nlines % 100000 == 0: print(f'{nlines} lines, {len(recs)} multi-swap txs, {time.time()-t0:.0f}s', flush=True)
    print(f'pass1 done: {nlines} candidate lines, {len(recs)} successful multi-swap txs, {nliq[0]} skipped for liquidity events', flush=True)
    # resolve V4 pool keys
    need = set(p for r in recs for (p, _, _) in r[9])
    keys = {}
    for pat in a.v4_init:
        for fn in sorted(glob.glob(pat)):
            for r in csv.DictReader(gzip.open(fn, 'rt')):
                pid = r['pool_id'].lower()
                if pid in need and pid not in keys:
                    keys[pid] = (r['currency0'].lower(), r['currency1'].lower(), r['hooks'].lower(), int(r['block_number']), r['fee_raw'])
    print(f'v4 pools needed {len(need)}, resolved {len(keys)}', flush=True)
    out = gzip.open(os.path.join(a.out, 'arbs.csv.gz'), 'wt', newline='')
    w = csv.writer(out, lineterminator='\n')
    w.writerow(['block', 'tx_index', 'tx_hash', 'from', 'to', 'n_swaps', 'n_pools', 'pools', 'v4_pools', 'v4_hooked', 'v4_min_age_blocks',
                'profit_token', 'profit_raw', 'profit_native', 'other_gain_native', 'gross_native', 'gas_native', 'l1_native', 'fee_native',
                'priority_native', 'base_fee', 'gross_usd', 'fee_usd', 'priority_usd', 'net_usd', 'priced', 'pool_gains', 'pm_payouts_other',
                'profit_to', 'prior_swap_same_pool_same_block', 'prior_tx_index', 'prior_from', 'profit_token_inflow_raw'])
    stats = collections.Counter()
    for (blk, txi, h, fr, to, gu, egp, l1, net, v4, pools, nsw, pmo, outside, inflow) in recs:
        inflow = collections.Counter(inflow)
        net = collections.defaultdict(int, net); hooked = 0; minage = ''; unresolved = 0
        for (pid, a0, a1) in v4:
            k = keys.get(pid)
            if not k: unresolved += 1; continue
            c0 = WETH if k[0] == ZERO else k[0]; c1 = WETH if k[1] == ZERO else k[1]
            net[c0] -= a0; net[c1] -= a1
            if a0 < 0: inflow[c0] -= a0
            if a1 < 0: inflow[c1] -= a1
            if k[2] != ZERO: hooked = 1
            if k[3] > 0: age = blk - k[3]; minage = age if minage == '' else min(minage, age)  # 0 = key from PositionManager, block unknown
        if unresolved: stats['v4_unresolved_tx'] += 1; continue
        neg = [(t, v) for t, v in net.items() if v < 0]
        pos = [(t, v) for t, v in net.items() if v > 0]
        if len(neg) != 1: stats['not_single_loss_token'] += 1; continue
        ptok, pv = neg[0]; praw = -pv
        pp = price.get(ptok)
        other = 0.0; other_unpriced = 0
        for t, v in pos:
            q = price.get(t)
            if q: other += v / 10 ** q[1] * q[0]
            else: other_unpriced += 1
        if other_unpriced: stats['pos_unpriced_kept'] += 1
        if pp:
            pnat = praw / 10 ** pp[1] * pp[0]
            if not other_unpriced and other > 0.05 * pnat: stats['pools_gain_other_tokens_flag'] += 1  # final decision in the report (reliable prices)
            gross = pnat - other; priced = 1
        else:
            pnat = ''; gross = ''; priced = 0
        # profit recipient: the non-pool address that received the most of the profit token (tx.to when none did,
        # e.g. native ETH taken from the PoolManager, which emits no Transfer)
        rc = [(c.get(ptok, 0), a) for a, c in outside.items() if c.get(ptok, 0) > 0]
        profit_to = max(rc)[1] if rc else to
        # backrun test: did another sender's successful swap touch one of these pools earlier in the same block?
        keyset = set(pools) | set(p for (p, _, _) in v4)
        prior = [(i, f) for (i, f, ks) in touches.get(blk, ()) if i < txi and f != fr and ks & keyset]
        pidx, pfrom = max(prior) if prior else ('', '')
        bfee = basefee.get(blk, 0)
        gas = gu * egp / 1e18; l1n = l1 / 1e18; fee = gas + l1n; prio = gu * max(0, egp - bfee) / 1e18
        U = a.native_usd
        w.writerow([blk, txi, h, fr, to, nsw, len(pools) + len(v4), ' '.join(pools), len(v4), hooked, minage, ptok, praw,
                    pnat, other, gross, gas, l1n, fee, prio, bfee, gross * U if priced else '', fee * U, prio * U,
                    (gross - fee) * U if priced else '', priced, ';'.join(f'{t}:{v}' for t, v in pos), pmo,
                    profit_to, 1 if prior else 0, pidx, pfrom, inflow.get(ptok, 0)])
        stats['arb'] += 1; stats['arb_priced'] += priced
    out.close()
    json.dump({'candidate_lines': nlines, 'multi_swap_success_txs': len(recs), 'skipped_liquidity_event_txs': nliq[0], 'v4_needed': len(need), 'v4_resolved': len(keys), 'counts': stats,
               'native_usd': a.native_usd}, open(os.path.join(a.out, 'arbs-meta.json'), 'w'), indent=1)
    print(json.dumps(stats), flush=True)

if __name__ == '__main__':
    main()
