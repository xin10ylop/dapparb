#!/usr/bin/env python3
"""Holder selection for the transfer probe (deterministic, from the pinned snapshot files only).

For each token in ../../tokens.csv.gz pick the non-V4 pool (V2-style or CL pool contract) with the largest
ERC-20 balanceOf(pool) at block 52008246, using the snapshot columns token0_balance_of_pool / token1_balance_of_pool
(only rows with token*_balance_ok == true) from ../../pools-prefilter.csv.gz and ../../pools-pruned-empty.csv.gz.
Tie-break: lowest pool address (lexicographic). If no pool has a positive balance, fall back to the V4 PoolManager
when ../../v4-poolmanager-balances.csv.gz has a positive balance for the token (holder_kind=v4_poolmanager).
Otherwise holder is empty (status no_holder downstream).

Streams the inputs row by row; memory is O(#tokens).
Output: work/holders.csv.gz with columns
  token, symbol, decimals, holder, holder_kind, holder_dex, holder_balance_snapshot, holder_source_file,
  n_pools_with_balance_ok, n_pools_positive_balance
"""
import csv, gzip, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'work', 'holders.csv.gz')
PM = '0x498581ff718922c3f8e6a244956af099b2652b2b'
KIND = {'univ2': 'v2', 'aero-v2': 'v2', 'univ3': 'cl', 'aero-cl': 'cl', 'pancake-v3': 'cl'}


def main():
    tokens = []  # (token, symbol, decimals)
    with gzip.open(os.path.join(SNAP, 'tokens.csv.gz'), 'rt', newline='') as f:
        for r in csv.DictReader(f):
            tokens.append((r['token'].lower(), r['symbol_engine'], r['decimals_engine']))
    best = {}   # token -> (balance:int, pool, dex, kind, source)
    nok = {}
    npos = {}
    for fn in ('pools-prefilter.csv.gz', 'pools-pruned-empty.csv.gz'):
        with gzip.open(os.path.join(SNAP, fn), 'rt', newline='') as f:
            for r in csv.DictReader(f):
                if r['is_v4'] == 'true':
                    continue
                pool = r['pool_address'].lower()
                kind = KIND[r['kind']]
                for side in ('0', '1'):
                    if r['token%s_balance_ok' % side] != 'true':
                        continue
                    t = r['token' + side].lower()
                    b = int(r['token%s_balance_of_pool' % side])
                    nok[t] = nok.get(t, 0) + 1
                    if b <= 0:
                        continue
                    npos[t] = npos.get(t, 0) + 1
                    cur = best.get(t)
                    if cur is None or b > cur[0] or (b == cur[0] and pool < cur[1]):
                        best[t] = (b, pool, r['dex'], kind, fn)
    pm = {}
    with gzip.open(os.path.join(SNAP, 'v4-poolmanager-balances.csv.gz'), 'rt', newline='') as f:
        for r in csv.DictReader(f):
            if r['balance_ok'] == 'true' and r['holder'].lower() == PM:
                pm[r['token'].lower()] = int(r['balance'])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + '.tmp'
    cnt = {}
    with gzip.open(tmp, 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['token', 'symbol', 'decimals', 'holder', 'holder_kind', 'holder_dex', 'holder_balance_snapshot',
                    'holder_source_file', 'n_pools_with_balance_ok', 'n_pools_positive_balance'])
        for t, sym, dec in tokens:
            b = best.get(t)
            if b is not None:
                row = [t, sym, dec, b[1], b[3], b[2], str(b[0]), b[4]]
            elif pm.get(t, 0) > 0:
                row = [t, sym, dec, PM, 'v4_poolmanager', 'UniswapV4', str(pm[t]), 'v4-poolmanager-balances.csv.gz']
            else:
                row = [t, sym, dec, '', '', '', '', '']
            k = row[4] or 'none'
            cnt[k] = cnt.get(k, 0) + 1
            w.writerow(row + [str(nok.get(t, 0)), str(npos.get(t, 0))])
    os.replace(tmp, OUT)
    print('tokens', len(tokens), 'holder_kind counts', cnt, file=sys.stderr)


if __name__ == '__main__':
    main()
