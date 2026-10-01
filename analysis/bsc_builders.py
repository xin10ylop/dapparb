#!/usr/bin/env python3
"""BSC line 6: who orders the arbitrage. Joins the valued BSC arbitrages (chains/bsc/arbs-valued.csv.gz) with the builder of
each block (bsc/builder/block-mev-info.csv.gz, bnb-chain good-will-alliance builder list) and reports: builder block shares,
arbitrage position in the block, zero-gas-price share (only a builder can include a 0-gwei tx), and for the top beneficiaries
how their profit splits across builders versus those builders' block shares (exclusive flow shows up as a mismatch)."""
import csv, gzip, json, collections, re
R = '/home/user/dapparb/research-material/06-other-chains-onchain/bsc'; A = '/home/user/dapparb/analysis'
names, org = {}, {}
for r in csv.DictReader(open(f'{R}/builders.csv')):  # an address can appear in several rows; keep any non-empty organisation
    a = r['address_lower']; names.setdefault(a, r['builder_name'])
    o = r['builder_org_derived'] or ('48club' if re.search(r'48club|club48|puissant', r['builder_name'], re.I) else '')
    if o: org[a] = '48club' if o == 'puissant' else o  # Puissant is 48 Club's builder brand
blk = {}
for r in csv.DictReader(gzip.open(f'{R}/builder/block-mev-info.csv.gz', 'rt')):
    b = (r['builder'] or '').lower(); blk[int(r['block_number'])] = org.get(b) or names.get(b) or (b[:10] if b else 'none (no builder)')
nb = len(blk); bshare = collections.Counter(blk.values())
arbs = list(csv.DictReader(gzip.open(f'{A}/chains/bsc/arbs-valued.csv.gz', 'rt')))
G = sum(float(r['gross_usd']) for r in arbs)
pos = collections.Counter(); posn = collections.Counter(); zero = 0.0; zn = 0
bb = collections.defaultdict(collections.Counter); bg = collections.Counter(); byb = collections.Counter()
for r in arbs:
    g = float(r['gross_usd']); i = int(r['tx_index'])
    k = 'index 0-2' if i <= 2 else 'index 3-9' if i < 10 else 'index 10+'
    pos[k] += g; posn[k] += 1
    if float(r['fee_usd']) == 0: zero += g; zn += 1
    b = blk.get(int(r['block']), 'unknown'); ben = r['profit_to'] or r['to']
    bb[ben][b] += g; bg[ben] += g; byb[b] += g
rep = {'blocks': nb, 'builder_block_share': {k: round(v / nb, 4) for k, v in bshare.most_common()},
       'arbs': len(arbs), 'gross_usd': round(G, 2),
       'gross_share_by_builder': {k: round(v / G, 3) for k, v in byb.most_common()},
       'position': {k: {'arbs': posn[k], 'gross_share': round(pos[k] / G, 3)} for k in sorted(pos)},
       'zero_gas_price': {'arbs': zn, 'gross_share': round(zero / G, 3)},
       'top_beneficiaries': []}
for ben, g in bg.most_common(10):
    rep['top_beneficiaries'].append({'beneficiary': ben, 'gross_usd': round(g, 2), 'share_of_all': round(g / G, 3),
                                     'by_builder': {k: round(v / g, 3) for k, v in bb[ben].most_common(4)}})
json.dump(rep, open(f'{A}/chains/bsc-builders.json', 'w'), indent=1)
print(json.dumps(rep, indent=1))
