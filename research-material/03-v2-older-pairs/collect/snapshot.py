#!/usr/bin/env python3
"""V2-style factory pool snapshot at one pinned Base block (raw data only, no analysis).

Phases (each resumable through state/<phase>.jsonl, one line per completed batch):
  1. factories   : allPairsLength/allPoolsLength of every V2-style factory in bot/src/config/chains.ts (BASE) and of the
                   three Slipstream factories, at the pinned block, at the blocks of the section 2.6 / 2.6-v0 enumeration
                   log lines, and on a 500,000-block grid (factory length history). -> factories.csv, factory-length-history.csv
  2. indices     : work list. Aerodrome V2, PancakeV2, BaseSwap, SushiV2: every index [0, N_pin).
                   UniswapV2: uniform random sample (seed SEED) of SAMPLE_N indices from [0, N_s26 - 6000) plus the newest
                   6,000 indices at the pinned block [N_pin - 6000, N_pin).  -> uniswapv2-sample-indices.csv.gz
  3. pairs       : allPairs(i) / allPools(i) at the pinned block.
  4. poolfields  : token0(), token1(), getReserves(), totalSupply() (LP token) and, for Aerodrome V2, stable().
  5. aerofee     : Aerodrome PoolFactory getFee(pool, stable) with the pool's own stable() result.
  6. output      : pools.csv.gz (split into pools-part-NNNN.csv.gz if > 85 MB).
Every call goes through Multicall3.aggregate3 with allowFailure=true; per-call status is recorded.
Sentinel: .sentinels/V2OLD_SNAPSHOT.DONE / .FAILED
"""
import argparse, csv, gzip, io, json, os, random, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpclib import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..'))
SEED = 20260930
SAMPLE_N = 60000
PART_LIMIT = 85 * 1024 * 1024

# name, kind (bot/src/config/chains.ts), factory, length fn, item fn, v2_style
FACTORIES = [
    ('Aerodrome', 'aero-v2', '0x420dd381b31aef6683db6b902084cb0ffece40da', 'allPoolsLength', 'allPools', True),
    ('UniswapV2', 'univ2', '0x8909dc15e40173ff4699343b6eb8132c65e18ec6', 'allPairsLength', 'allPairs', True),
    ('SushiV2', 'univ2', '0x71524b4f93c58fcbf659783284e38825f0622859', 'allPairsLength', 'allPairs', True),
    ('PancakeV2', 'univ2', '0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e', 'allPairsLength', 'allPairs', True),
    ('BaseSwap', 'univ2', '0xfda619b6d20975be80a10332cd39b9a4b0faa8bb', 'allPairsLength', 'allPairs', True),
    ('AerodromeCL', 'aero-cl', '0x5e7bb104d84c7cb9b682aac2f3d509f5f406809a', 'allPoolsLength', 'allPools', False),
    ('AerodromeCL3', 'aero-cl', '0xf8f2eb4940cfe7d13603dddd87f123820fc061ef', 'allPoolsLength', 'allPools', False),
    ('AerodromeCL2', 'aero-cl', '0xade65c38cd4849adba595a4323a8c7ddfe89716a', 'allPoolsLength', 'allPools', False),
]
# From research-material/00-prior-runs/engine-runs/dry-all.log.gz (section 2.6 run) and dry-all-v0.log.gz
# ('factory enumerated' lines: dex, total, enumerated; log time = when that factory's enumeration multicall returned).
S26 = {  # name: (log_time_utc, total, enumerated)
    'AerodromeCL': ('2026-09-30T16:55:48.378Z', 3648, 3648), 'AerodromeCL3': ('2026-09-30T16:55:48.988Z', 2771, 2771),
    'AerodromeCL2': ('2026-09-30T16:55:49.415Z', 2259, 2259), 'Aerodrome': ('2026-09-30T16:55:50.569Z', 29600, 6000),
    'UniswapV2': ('2026-09-30T16:55:52.561Z', 3063605, 6000), 'SushiV2': ('2026-09-30T16:55:53.735Z', 6093, 6000),
    'PancakeV2': ('2026-09-30T16:55:55.067Z', 15231, 6000), 'BaseSwap': ('2026-09-30T16:55:56.192Z', 8258, 6000),
}
V0 = {
    'AerodromeCL': ('2026-09-30T16:37:12.373Z', 3648, 3648), 'AerodromeCL3': ('2026-09-30T16:37:12.963Z', 2766, 2766),
    'AerodromeCL2': ('2026-09-30T16:37:13.486Z', 2259, 2259), 'Aerodrome': ('2026-09-30T16:37:14.773Z', 29600, 6000),
    'UniswapV2': ('2026-09-30T16:37:17.012Z', 3063599, 6000), 'SushiV2': ('2026-09-30T16:37:18.314Z', 6093, 6000),
    'PancakeV2': ('2026-09-30T16:37:19.487Z', 15231, 6000), 'BaseSwap': ('2026-09-30T16:37:20.585Z', 8258, 6000),
}
DOCS_TEXT = {'Aerodrome': 29600, 'UniswapV2': 3063599}  # figures quoted in docs/ANALYSIS.md section 2.6


def block_at(iso):
    import datetime
    ts = datetime.datetime.strptime(iso, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=datetime.timezone.utc).timestamp()
    return int((int(ts) - BASE_GENESIS_TS) // 2)


def run_batches(name, store, batches, fn, workers, gaps_path):
    todo = [b for b in range(len(batches)) if b not in store.done]
    log(name, 'batches total', len(batches), 'done', len(batches) - len(todo), 'todo', len(todo))
    if not todo:
        return
    t0 = time.time(); n = 0
    with ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fn, b, batches[b]): b for b in todo}
        for f in as_completed(futs):
            b = futs[f]
            try:
                rows = f.result()
                store.add(b, rows)
            except Exception as e:
                append_gap(gaps_path, ['snapshot', name, 'batch %d' % b, repr(e)[:300]])
                log(name, 'batch FAILED', b, repr(e)[:300])
            n += 1
            if n % 50 == 0 or n == len(todo):
                log(name, 'progress', n, '/', len(todo), 'elapsed %.0fs' % (time.time() - t0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pin', type=int, required=True)
    ap.add_argument('--smoke', type=int, default=0, help='limit each group to the first N items; writes to --out')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--state', default=os.path.join(HERE, 'state'))
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--sentinel', default='V2OLD_SNAPSHOT')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.state, exist_ok=True)
    gaps = os.path.join(a.out, 'gaps.csv')
    P = a.pin; tag = hex(P)
    blast = Endpoint(BLAST, 2); drpc = Endpoint(DRPC, 1)
    eps = [blast, drpc]
    meta = {'pinned_block': P, 'pinned_block_timestamp_formula': BASE_GENESIS_TS + 2 * P, 'started_utc': utcnow(),
            'seed': SEED, 'sample_n': SAMPLE_N, 'endpoints_eth_call': [BLAST, DRPC], 'multicall3': MULTICALL3}

    # ---- phase 1: factories
    hdr = call_with_retry([Endpoint(BLAST, 1), Endpoint(DRPC, 1)], 'eth_getBlockByNumber', [tag, False])
    meta['pinned_block_hash'] = hdr['hash']; meta['pinned_block_timestamp'] = int(hdr['timestamp'], 16)
    log('pinned block', P, hdr['hash'], int(hdr['timestamp'], 16))

    def lengths_at(block):
        calls = [(f[2], '0x' + SEL[f[3]]) for f in FACTORIES]
        r = multicall(eps, hex(block), calls, what='len@%d' % block)
        return [(st, dec_uint(st, d)[0], err) for st, d, err in r]

    nP = {}
    rP = lengths_at(P)
    for f, (st, v, err) in zip(FACTORIES, rP):
        if st != 'ok':
            raise SystemExit('factory length failed at pin: %s %s %s' % (f[0], st, err))
        nP[f[0]] = int(v)
    with open(os.path.join(a.out, 'factories.csv'), 'w', newline='') as fo:
        w = csv.writer(fo)
        w.writerow(['factory_name', 'dex_kind', 'factory', 'v2_style', 'length_fn', 'snapshot_block', 'n_at_snapshot',
                    's26_log_time_utc', 's26_block_at_log_time', 's26_total_logged', 'n_onchain_at_s26_block', 's26_enumerated_logged',
                    's26_enum_index_start', 's26_enum_index_end_excl', 'v0_log_time_utc', 'v0_block_at_log_time', 'v0_total_logged',
                    'n_onchain_at_v0_block', 'v0_enum_index_start', 'v0_enum_index_end_excl', 'docs_analysis_text_total',
                    'n_growth_since_s26_derived', 'this_snapshot_index_selection'])
        for f in FACTORIES:
            name = f[0]
            b26 = block_at(S26[name][0]); b0 = block_at(V0[name][0])
            r26 = lengths_at(b26)[FACTORIES.index(f)]; r0 = lengths_at(b0)[FACTORIES.index(f)]
            t26, e26 = S26[name][1], S26[name][2]; t0, e0 = V0[name][1], V0[name][2]
            if name == 'UniswapV2':
                sel = 'random sample of %d from [0,%d) seed %d + newest 6000 at snapshot [%d,%d)' % (SAMPLE_N, t26 - 6000, SEED, nP[name] - 6000, nP[name])
            elif f[5]:
                sel = 'all indices [0,%d)' % nP[name]
            else:
                sel = 'not collected (Slipstream; listed for reference only)'
            w.writerow([name, f[1], f[2], f[5], f[3], P, nP[name], S26[name][0], b26, t26, r26[1] or r26[0], e26, t26 - e26, t26,
                        V0[name][0], b0, t0, r0[1] or r0[0], t0 - e0, t0, DOCS_TEXT.get(name, ''), nP[name] - t26, sel])
    # factory length history (grid)
    hist_path = os.path.join(a.out, 'factory-length-history.csv')
    grid = list(range(500000, P, 500000)) + [P]
    hist = BatchStore(os.path.join(a.state, 'lenhist.jsonl'))
    def do_hist(b, blk):
        return [[st, v, err] for st, v, err in lengths_at(blk)]
    run_batches('lenhist', hist, grid, do_hist, a.workers, gaps)
    with open(hist_path, 'w', newline='') as fo:
        w = csv.writer(fo)
        w.writerow(['block', 'block_timestamp_formula', 'factory_name', 'factory', 'length_fn', 'status', 'length'])
        for b, blk in enumerate(grid):
            rows = hist.done.get(b)
            for f, r in zip(FACTORIES, rows or [['rpc_failed', '', '']] * len(FACTORIES)):
                w.writerow([blk, BASE_GENESIS_TS + 2 * blk, f[0], f[2], f[3], r[0], r[1]])
    hist.close()
    log('phase 1 done', nP)

    # ---- phase 2: index work list
    items = []  # (factory_idx, index, sample_group)
    t26u = S26['UniswapV2'][1]
    M = t26u - 6000
    rng = random.Random(SEED)
    sample = sorted(rng.sample(range(M), SAMPLE_N))
    with gzip.open(os.path.join(a.out, 'uniswapv2-sample-indices.csv.gz'), 'wt', newline='') as fo:
        w = csv.writer(fo)
        w.writerow(['index', 'group', 'population_start', 'population_end_excl', 'seed', 'method'])
        for i in sample:
            w.writerow([i, 'random_sample_older', 0, M, SEED, 'python3.11 random.Random(seed).sample(range(M), %d), sorted' % SAMPLE_N])
        for i in range(nP['UniswapV2'] - 6000, nP['UniswapV2']):
            w.writerow([i, 'newest_6000_at_snapshot', nP['UniswapV2'] - 6000, nP['UniswapV2'], '', 'newest 6000 at snapshot block'])
    lim = a.smoke or None
    for fi, f in enumerate(FACTORIES):
        if not f[5]:
            continue
        if f[0] == 'UniswapV2':
            items += [(fi, i, 'random_sample_older') for i in sample[:lim]]
            items += [(fi, i, 'newest_6000_at_snapshot') for i in list(range(nP[f[0]] - 6000, nP[f[0]]))[:lim]]
        else:
            rng_all = list(range(nP[f[0]]))
            if lim:
                rng_all = rng_all[:lim] + rng_all[-lim:]
            items += [(fi, i, 'all_indices') for i in rng_all]
    log('work items', len(items))
    meta['work_items'] = len(items)

    # ---- phase 3: pair addresses
    B3 = 1000
    batches3 = [items[k:k + B3] for k in range(0, len(items), B3)]
    st3 = BatchStore(os.path.join(a.state, 'pairs.jsonl'))
    def do3(b, batch):
        calls = [(FACTORIES[fi][2], '0x' + SEL[FACTORIES[fi][4]] + enc_uint(i)) for fi, i, g in batch]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(eps, tag, calls, what='pairs b%d' % b)]
    run_batches('pairs', st3, batches3, do3, a.workers, gaps)
    pair_res = []
    for b in range(len(batches3)):
        rows = st3.done.get(b)
        pair_res += rows if rows else [['rpc_failed', '0x', 'batch not collected, see gaps.csv']] * len(batches3[b])
    st3.close()

    # ---- phase 4: pool fields
    pools = []  # (item, pair_addr, pair_status, err)
    for it, (s, dh, e) in zip(items, pair_res):
        addr, ast = dec_addr(s, bytes.fromhex(dh[2:]))
        if addr == '0x' + '0' * 40:
            ast = 'zero_address'
        pools.append((it, addr, ast, e, dh))
    B4 = 100
    idx4 = [k for k, p in enumerate(pools) if p[2] in ('ok', 'ok_extra_bytes')]
    batches4 = [idx4[k:k + B4] for k in range(0, len(idx4), B4)]
    def fns_for(k):
        fi = pools[k][0][0]
        base = ['token0', 'token1', 'getReserves', 'totalSupply']
        return base + (['stable'] if FACTORIES[fi][1] == 'aero-v2' else [])
    st4 = BatchStore(os.path.join(a.state, 'poolfields.jsonl'))
    def do4(b, batch):
        calls = []
        for k in batch:
            for fn in fns_for(k):
                calls.append((pools[k][1], '0x' + SEL[fn]))
        r = multicall(eps, tag, calls, what='fields b%d' % b)
        return [[s, '0x' + d.hex(), e] for s, d, e in r]
    run_batches('poolfields', st4, batches4, do4, a.workers, gaps)
    fields = {}
    for b, batch in enumerate(batches4):
        rows = st4.done.get(b)
        pos = 0
        for k in batch:
            fl = fns_for(k)
            if rows:
                fields[k] = dict(zip(fl, rows[pos:pos + len(fl)]))
                pos += len(fl)
            else:
                fields[k] = {fn: ['rpc_failed', '0x', 'batch not collected, see gaps.csv'] for fn in fl}
    st4.close()

    # ---- phase 5: aerodrome fee
    idx5 = []
    for k in idx4:
        fi = pools[k][0][0]
        if FACTORIES[fi][1] == 'aero-v2':
            s, dh, e = fields[k]['stable']
            v, vs = dec_bool(s, bytes.fromhex(dh[2:]))
            if vs in ('ok', 'ok_extra_bytes'):
                idx5.append((k, v == 'true'))
    B5 = 500
    batches5 = [idx5[k:k + B5] for k in range(0, len(idx5), B5)]
    st5 = BatchStore(os.path.join(a.state, 'aerofee.jsonl'))
    def do5(b, batch):
        calls = [(FACTORIES[pools[k][0][0]][2], '0x' + SEL['getFee'] + enc_addr(pools[k][1]) + enc_bool(stv)) for k, stv in batch]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(eps, tag, calls, what='fee b%d' % b)]
    run_batches('aerofee', st5, batches5, do5, a.workers, gaps)
    fee = {}
    for b, batch in enumerate(batches5):
        rows = st5.done.get(b)
        for j, (k, stv) in enumerate(batch):
            fee[k] = rows[j] if rows else ['rpc_failed', '0x', 'batch not collected, see gaps.csv']
    st5.close()

    # ---- phase 6: output
    cols = ['snapshot_block', 'factory_name', 'factory', 'dex_kind', 'index', 'sample_group', 'index_vs_s26_range', 'pair', 'pair_status',
            'token0', 'token0_status', 'token1', 'token1_status', 'reserves_status', 'reserves_ret_bytes', 'reserve0', 'reserve1',
            'block_timestamp_last', 'reserves_extra_hex', 'lp_total_supply', 'lp_total_supply_status', 'stable', 'stable_status',
            'factory_fee', 'factory_fee_status', 'failures']
    part = [1]; written = [0]
    counts = {}
    def open_part():
        p = os.path.join(a.out, 'pools-part-%04d.csv.gz' % part[0])
        fo = open(p, 'wb')
        gz = gzip.GzipFile(fileobj=fo, mode='wb')
        tw = io.TextIOWrapper(gz, newline='', encoding='utf-8')
        w = csv.writer(tw); w.writerow(cols)
        return p, fo, gz, tw, w
    for old in [x for x in os.listdir(a.out) if x.startswith('pools-part-')]:
        os.remove(os.path.join(a.out, old))
    p, fo, gz, tw, w = open_part()
    for k, (it, addr, ast, perr, pdh) in enumerate(pools):
        fi, i, g = it
        f = FACTORIES[fi]; name = f[0]
        t26 = S26[name][1]
        vs = 'below_s26_range' if i < t26 - 6000 else ('in_s26_range' if i < t26 else 'above_s26_range')
        fails = []
        if ast not in ('ok', 'ok_extra_bytes'):
            fails.append('allPairs=%s:%s%s' % (ast, pdh, (':' + perr) if perr else ''))
        row = {'snapshot_block': P, 'factory_name': name, 'factory': f[2], 'dex_kind': f[1], 'index': i, 'sample_group': g,
               'index_vs_s26_range': vs, 'pair': addr, 'pair_status': ast}
        fd = fields.get(k)
        if fd:
            def g3(fn):
                s, dh, e = fd[fn]
                d = bytes.fromhex(dh[2:])
                if s != 'ok':
                    fails.append('%s=%s:%s%s' % (fn, s, dh, (':' + e) if e else ''))
                return s, d
            s, d = g3('token0'); row['token0'], row['token0_status'] = dec_addr(s, d)
            s, d = g3('token1'); row['token1'], row['token1_status'] = dec_addr(s, d)
            s, d = g3('getReserves')
            (r0, r1, tl), rs = dec_words(s, d, 3)
            row.update(reserves_status=rs, reserves_ret_bytes=len(d) if s == 'ok' else '', reserve0=r0, reserve1=r1,
                       block_timestamp_last=tl, reserves_extra_hex=('0x' + d[96:].hex()) if (s == 'ok' and len(d) > 96) else '')
            s, d = g3('totalSupply'); row['lp_total_supply'], row['lp_total_supply_status'] = dec_uint(s, d)
            if 'stable' in fd:
                s, d = g3('stable'); row['stable'], row['stable_status'] = dec_bool(s, d)
                fr = fee.get(k)
                if fr:
                    s, dh, e = fr; d = bytes.fromhex(dh[2:])
                    if s != 'ok':
                        fails.append('getFee=%s:%s%s' % (s, dh, (':' + e) if e else ''))
                    row['factory_fee'], row['factory_fee_status'] = dec_uint(s, d)
                else:
                    row['factory_fee_status'] = 'not_called_stable_unknown'
        else:
            for c in ('token0_status', 'token1_status', 'reserves_status', 'lp_total_supply_status'):
                row[c] = 'not_called_no_pair'
        row['failures'] = '|'.join(fails)
        counts[(name, g)] = counts.get((name, g), 0) + 1
        w.writerow([row.get(c, '') for c in cols])
        written[0] += 1
        if written[0] % 5000 == 0:
            tw.flush()
            if fo.tell() > PART_LIMIT:
                tw.close(); fo.close(); part[0] += 1
                p, fo, gz, tw, w = open_part()
    tw.close(); fo.close()
    meta['rows_by_factory_group'] = {'%s/%s' % kg: v for kg, v in sorted(counts.items())}
    meta['rows_total'] = written[0]
    meta['pool_parts'] = part[0]
    meta['finished_utc'] = utcnow()
    meta['endpoint_stats'] = {BLAST: blast.stats, DRPC: drpc.stats}
    with open(os.path.join(a.out, 'snapshot-meta.json'), 'w') as fo:
        json.dump(meta, fo, indent=1)
    log('snapshot done', json.dumps(meta)[:2000])
    if a.sentinel != 'none':
        g = 0
        if os.path.exists(gaps):
            g = sum(1 for l in open(gaps) if l.startswith('"snapshot"'))
        write_sentinel(a.sentinel, True, 'rows=%d parts=%d snapshot_gaps=%d pinned_block=%d' % (written[0], part[0], g, P))


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        tb = traceback.format_exc()
        log('FATAL', tb)
        if '--smoke' not in sys.argv:
            write_sentinel('V2OLD_SNAPSHOT', False, tb[-1500:])
        sys.exit(1)
