#!/usr/bin/env python3
"""ERC-20 metadata for every token seen in this directory, plus a WETH-route state reference (raw data only).

Waits for .sentinels/V2OLD_SNAPSHOT.DONE and .sentinels/V2OLD_CENSUS.(DONE|FAILED).
Token set = token0/token1 of pools-part-*.csv.gz (status ok) UNION token0/token1 of emitters.csv.gz (status ok).
  tokens.csv.gz: symbol(), name(), decimals(), totalSupply() at the pinned block (Multicall3 aggregate3, allowFailure).
WETH-route set = every token of a pool (snapshot or census emitter) whose two sides include neither WETH nor one of
  USDC / USDbC / DAI / USDT (Base addresses below), plus those four stablecoins themselves.
  For each such token, factory lookups against WETH on every DEX in bot/src/config/chains.ts (BASE):
    UniswapV2, SushiV2, PancakeV2, BaseSwap getPair(token, WETH); Aerodrome getPool(token, WETH, false|true);
    UniswapV3, SushiV3 getPool(token, WETH, 100|500|3000|10000); PancakeV3 getPool(token, WETH, 100|500|2500|10000);
    AerodromeCL, AerodromeCL2, AerodromeCL3 getPool(token, WETH, tickSpacing 1|10|50|100|200|2000).
  For every non-zero pool returned: V2-style token0(), getReserves(); V3-style token0(), slot0(), liquidity(),
  WETH.balanceOf(pool), token.balanceOf(pool).  -> price-reference-weth-pools.csv.gz
Then runs finalize.py (row counts into MANIFEST.md auto-status block) and writes .sentinels/V2OLD.DONE.
Sentinel: .sentinels/V2OLD_TOKENS.DONE / .FAILED
"""
import argparse, csv, glob, gzip, json, os, subprocess, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpclib import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..'))
SENT = '/home/user/dapparb/research-material/.sentinels'
WETH = '0x4200000000000000000000000000000000000006'
STABLES = {'0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': 'USDC', '0xd9aaec86b65d86f6a7b5b1b0c42ffa531710b6ca': 'USDbC',
           '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': 'DAI', '0xfde4c96c8593536e31f229ea8f37b2ada2699bb2': 'USDT'}
SEL2 = {'getPair': 'e6a43905', 'getPoolBool': '79bc57d5', 'getPoolU24': '1698ee82', 'getPoolI24': '28af8d0b',
        'slot0': '3850c7bd', 'liquidity': '1a686502', 'balanceOf': '70a08231'}
# (venue, kind, factory, lookup-fn, params)
VENUES = [
    ('UniswapV2', 'univ2', '0x8909dc15e40173ff4699343b6eb8132c65e18ec6', 'getPair', [None]),
    ('SushiV2', 'univ2', '0x71524b4f93c58fcbf659783284e38825f0622859', 'getPair', [None]),
    ('PancakeV2', 'univ2', '0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e', 'getPair', [None]),
    ('BaseSwap', 'univ2', '0xfda619b6d20975be80a10332cd39b9a4b0faa8bb', 'getPair', [None]),
    ('Aerodrome', 'aero-v2', '0x420dd381b31aef6683db6b902084cb0ffece40da', 'getPoolBool', [False, True]),
    ('UniswapV3', 'univ3', '0x33128a8fc17869897dce68ed026d694621f6fdfd', 'getPoolU24', [100, 500, 3000, 10000]),
    ('SushiV3', 'univ3', '0xc35dadb65012ec5796536bd9864ed8773abc74c4', 'getPoolU24', [100, 500, 3000, 10000]),
    ('PancakeV3', 'pancake-v3', '0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865', 'getPoolU24', [100, 500, 2500, 10000]),
    ('AerodromeCL', 'aero-cl', '0x5e7bb104d84c7cb9b682aac2f3d509f5f406809a', 'getPoolI24', [1, 10, 50, 100, 200, 2000]),
    ('AerodromeCL3', 'aero-cl', '0xf8f2eb4940cfe7d13603dddd87f123820fc061ef', 'getPoolI24', [1, 10, 50, 100, 200, 2000]),
    ('AerodromeCL2', 'aero-cl', '0xade65c38cd4849adba595a4323a8c7ddfe89716a', 'getPoolI24', [1, 10, 50, 100, 200, 2000]),
]


def lookup_calldata(fn, token, param):
    if fn == 'getPair':
        return '0x' + SEL2['getPair'] + enc_addr(token) + enc_addr(WETH)
    if fn == 'getPoolBool':
        return '0x' + SEL2['getPoolBool'] + enc_addr(token) + enc_addr(WETH) + enc_bool(param)
    if fn == 'getPoolU24':
        return '0x' + SEL2['getPoolU24'] + enc_addr(token) + enc_addr(WETH) + enc_uint(param)
    if fn == 'getPoolI24':
        return '0x' + SEL2['getPoolI24'] + enc_addr(token) + enc_addr(WETH) + enc_uint(param % (1 << 256))
    raise ValueError(fn)


def run_batches(name, store, batches, fn, workers, gaps):
    todo = [b for b in range(len(batches)) if b not in store.done]
    log(name, 'batches', len(batches), 'todo', len(todo))
    n = 0; t0 = time.time()
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fn, b, batches[b]): b for b in todo}
        for f in as_completed(futs):
            b = futs[f]; n += 1
            try:
                store.add(b, f.result())
            except Exception as e:
                append_gap(gaps, ['tokens', name, 'batch %d' % b, repr(e)[:300]])
                log(name, 'batch FAILED', b, repr(e)[:300])
            if n % 100 == 0 or n == len(todo):
                log(name, 'progress', n, '/', len(todo), '%.0fs' % (time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--state', default=os.path.join(HERE, 'state', 'tokens'))
    ap.add_argument('--limit', type=int, default=0, help='smoke: only the first N tokens / route tokens')
    ap.add_argument('--sentinel', default='V2OLD_TOKENS')
    ap.add_argument('--no-wait', action='store_true')
    ap.add_argument('--no-finalize', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.state, exist_ok=True)
    gaps = os.path.join(a.out, 'gaps.csv')
    if not a.no_wait:
        t0 = time.time()
        while True:
            snap = os.path.exists(os.path.join(SENT, 'V2OLD_SNAPSHOT.DONE'))
            cen = any(os.path.exists(os.path.join(SENT, 'V2OLD_CENSUS' + s)) for s in ('.DONE', '.FAILED'))
            if snap and cen:
                break
            if os.path.exists(os.path.join(SENT, 'V2OLD_SNAPSHOT.FAILED')):
                raise SystemExit('snapshot failed; nothing to do')
            if time.time() - t0 > 12 * 3600:
                raise RuntimeError('timed out waiting for snapshot/census sentinels')
            time.sleep(30)
    meta = json.load(open(os.path.join(a.out, 'snapshot-meta.json')))
    P = meta['pinned_block']; tag = hex(P)
    blast = Endpoint(BLAST, 2); drpc = Endpoint(DRPC, 1)
    eps = [blast, drpc]

    # ---- token set
    in_pools, in_emit, route = set(), set(), set(STABLES)
    def consider(t0, t1, s0, s1, target):
        for t, s in ((t0, s0), (t1, s1)):
            if s in ('ok', 'ok_extra_bytes') and t:
                target.add(t)
        if s0 in ('ok', 'ok_extra_bytes') and s1 in ('ok', 'ok_extra_bytes'):
            if not ({t0, t1} & ({WETH} | set(STABLES))):
                route.add(t0); route.add(t1)
    for p in sorted(glob.glob(os.path.join(a.out, 'pools-part-*.csv.gz'))):
        with gzip.open(p, 'rt', newline='') as f:
            for r in csv.DictReader(f):
                consider(r['token0'], r['token1'], r['token0_status'], r['token1_status'], in_pools)
    ep = os.path.join(a.out, 'emitters.csv.gz')
    if os.path.exists(ep):
        with gzip.open(ep, 'rt', newline='') as f:
            for r in csv.DictReader(f):
                consider(r['token0'], r['token1'], r['token0_status'], r['token1_status'], in_emit)
    route.discard(WETH)
    tokens = sorted(in_pools | in_emit | set(STABLES) | {WETH})
    route = sorted(route)
    if a.limit:
        tokens = tokens[:a.limit]; route = route[:max(1, a.limit // 10)] + sorted(STABLES)
    log('tokens', len(tokens), 'route tokens', len(route))

    # ---- metadata
    FN = ['symbol', 'name', 'decimals', 'totalSupply']
    B = 100
    tb = [tokens[k:k + B] for k in range(0, len(tokens), B)]
    st = BatchStore(os.path.join(a.state, 'meta.jsonl'))
    def do_meta(b, batch):
        calls = [(t, '0x' + SEL[fn]) for t in batch for fn in FN]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(eps, tag, calls, what='meta b%d' % b)]
    run_batches('meta', st, tb, do_meta, 2, gaps)
    with gzip.open(os.path.join(a.out, 'tokens.csv.gz'), 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['token', 'snapshot_block', 'in_snapshot_pools', 'in_census_emitters', 'in_weth_route_set', 'symbol', 'symbol_encoding', 'symbol_raw',
                    'name', 'name_encoding', 'name_raw', 'decimals', 'decimals_status', 'total_supply', 'total_supply_status', 'failures'])
        rs = set(route)
        for b, batch in enumerate(tb):
            rows = st.done.get(b)
            for j, t in enumerate(batch):
                rr = rows[4 * j:4 * j + 4] if rows else [['rpc_failed', '0x', 'batch not collected, see gaps.csv']] * 4
                d = [bytes.fromhex(x[1][2:]) for x in rr]
                fails = ['%s=%s:%s%s' % (fn, x[0], x[1], (':' + x[2]) if x[2] else '') for fn, x in zip(FN, rr) if x[0] != 'ok']
                sy, se, sr = dec_text(rr[0][0], d[0]); nm, ne, nr = dec_text(rr[1][0], d[1])
                de, ds = dec_uint(rr[2][0], d[2]); ts, tss = dec_uint(rr[3][0], d[3])
                w.writerow([t, P, t in in_pools, t in in_emit, t in rs, sy, se, sr, nm, ne, nr, de, ds, ts, tss, '|'.join(fails)])
    st.close()

    # ---- WETH-route lookups
    lk = []  # (token, venue_idx, param)
    for t in route:
        for vi, v in enumerate(VENUES):
            for prm in v[4]:
                lk.append((t, vi, prm))
    B2 = 432
    lb = [lk[k:k + B2] for k in range(0, len(lk), B2)]
    st2 = BatchStore(os.path.join(a.state, 'lookups.jsonl'))
    def do_lk(b, batch):
        calls = [(VENUES[vi][2], lookup_calldata(VENUES[vi][3], t, prm)) for t, vi, prm in batch]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(eps, tag, calls, what='lookup b%d' % b)]
    run_batches('lookups', st2, lb, do_lk, 2, gaps)
    found = []  # (token, vi, prm, pool, lookup_status, raw)
    for b, batch in enumerate(lb):
        rows = st2.done.get(b)
        for j, (t, vi, prm) in enumerate(batch):
            s, dh, e = rows[j] if rows else ['rpc_failed', '0x', 'batch not collected, see gaps.csv']
            addr, ast = dec_addr(s, bytes.fromhex(dh[2:]))
            if ast in ('ok', 'ok_extra_bytes') and addr == '0x' + '0' * 40:
                continue
            found.append((t, vi, prm, addr, ast, dh + ((':' + e) if e else '')))
    st2.close()
    log('route pools found (incl. lookup failures)', len(found))

    def state_fns(k):
        t, vi, prm, pool, ast, raw = found[k]
        if ast not in ('ok', 'ok_extra_bytes'):
            return []
        if VENUES[vi][1] in ('univ2', 'aero-v2'):
            return [('token0', pool, '0x' + SEL['token0']), ('getReserves', pool, '0x' + SEL['getReserves'])]
        return [('token0', pool, '0x' + SEL['token0']), ('slot0', pool, '0x' + SEL2['slot0']), ('liquidity', pool, '0x' + SEL2['liquidity']),
                ('wethBalance', WETH, '0x' + SEL2['balanceOf'] + enc_addr(pool)), ('tokenBalance', t, '0x' + SEL2['balanceOf'] + enc_addr(pool))]
    idx = [k for k in range(len(found)) if state_fns(k)]
    B3 = 80
    sb = [idx[k:k + B3] for k in range(0, len(idx), B3)]
    st3 = BatchStore(os.path.join(a.state, 'routestate.jsonl'))
    def do_st(b, batch):
        calls = [(tgt, cd) for k in batch for (_, tgt, cd) in state_fns(k)]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(eps, tag, calls, what='rstate b%d' % b)]
    run_batches('routestate', st3, sb, do_st, 2, gaps)
    res = {}
    for b, batch in enumerate(sb):
        rows = st3.done.get(b); pos = 0
        for k in batch:
            fl = state_fns(k)
            rr = rows[pos:pos + len(fl)] if rows else [['rpc_failed', '0x', 'batch not collected, see gaps.csv']] * len(fl)
            pos += len(fl)
            res[k] = {n: x for (n, _, _), x in zip(fl, rr)}
    st3.close()
    with gzip.open(os.path.join(a.out, 'price-reference-weth-pools.csv.gz'), 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['token', 'snapshot_block', 'venue', 'venue_kind', 'factory', 'lookup_param', 'pool', 'lookup_status', 'pool_token0', 'pool_token0_status',
                    'reserves_status', 'reserve0', 'reserve1', 'block_timestamp_last', 'slot0_status', 'slot0_ret_bytes', 'sqrt_price_x96', 'tick',
                    'liquidity', 'liquidity_status', 'weth_balance_of_pool', 'weth_balance_status', 'token_balance_of_pool', 'token_balance_status', 'failures'])
        for k, (t, vi, prm, pool, ast, raw) in enumerate(found):
            v = VENUES[vi]
            row = [t, P, v[0], v[1], v[2], '' if prm is None else str(prm).lower(), pool, ast]
            r = res.get(k, {})
            fails = [] if ast in ('ok', 'ok_extra_bytes') else ['lookup=%s:%s' % (ast, raw)]
            def g(n):
                if n not in r:
                    return 'not_called', b''
                s, dh, e = r[n]
                if s != 'ok':
                    fails.append('%s=%s:%s%s' % (n, s, dh, (':' + e) if e else ''))
                return s, bytes.fromhex(dh[2:])
            t0, t0s = dec_addr(*g('token0')) if 'token0' in r else ('', 'not_called')
            if 'getReserves' in r:
                s, d = g('getReserves'); (r0, r1, tl), rst = dec_words(s, d, 3)
            else:
                r0 = r1 = tl = ''; rst = 'not_called'
            if 'slot0' in r:
                s, d = g('slot0')
                (sp, tk), sst = dec_words(s, d, 2)
                if sst == 'ok_extra_bytes':
                    sst = 'ok'  # slot0 returns 6 (Slipstream) or 7 (Uniswap/Pancake V3) words; only words 0-1 are decoded
                if tk:
                    tv = int(tk); tv = tv - (1 << 256) if tv >= (1 << 255) else tv
                    tk = str(tv)
                slen = len(d) if s == 'ok' else ''
                lq, lqs = dec_uint(*g('liquidity')); wb, wbs = dec_uint(*g('wethBalance')); tb_, tbs = dec_uint(*g('tokenBalance'))
            else:
                sp = tk = slen = lq = wb = tb_ = ''; sst = lqs = wbs = tbs = 'not_called'
            w.writerow(row + [t0, t0s, rst, r0, r1, tl, sst, slen, sp, tk, lq, lqs, wb, wbs, tb_, tbs, '|'.join(fails)])
    info = {'tokens': len(tokens), 'route_tokens': len(route), 'lookups': len(lk), 'route_rows': len(found), 'finished_utc': utcnow(),
            'endpoint_stats': {BLAST: blast.stats, DRPC: drpc.stats}}
    with open(os.path.join(a.out, 'tokens-meta.json'), 'w') as f:
        json.dump(info, f, indent=1)
    log('tokens done', info)
    if a.sentinel != 'none':
        write_sentinel(a.sentinel, True, json.dumps(info))
    if not a.no_finalize:
        subprocess.run([sys.executable, os.path.join(HERE, 'finalize.py')], check=False)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log('FATAL', tb)
        if '--sentinel' not in sys.argv:
            write_sentinel('V2OLD_TOKENS', False, tb[-1500:])
            write_sentinel('V2OLD', False, 'tokens stage failed: ' + tb[-800:])
        sys.exit(1)
