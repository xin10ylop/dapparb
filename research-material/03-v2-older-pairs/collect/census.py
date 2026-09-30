#!/usr/bin/env python3
"""V2-style activity census on Base over the 43,200 blocks (24 h) ending at the pinned block (raw data only).

eth_getLogs with a topic-only filter (no address) for four topic0 values:
  sync_uint112 : Sync(uint112,uint112)                                   Uniswap V2 style
  sync_uint256 : Sync(uint256,uint256)                                   Aerodrome / Solidly style
  swap_univ2   : Swap(address,uint256,uint256,uint256,uint256,address)   Uniswap V2 style
  swap_aero_v2 : Swap(address,address,uint256,uint256,uint256,uint256)   Aerodrome V2 style
Endpoints (all of them reject or cap address-less getLogs differently, probed 2026-09-30 ~22:10Z):
  gateway.tenderly.co/public/base (<= 1,000 blocks)  primary, 2 in flight
  mainnet.base.org                (<= 2,000 blocks)  secondary, 1 in flight, >= 1 s between requests
  base.drpc.org                   (<= 10 blocks for address-less filters) last resort
  base-rpc.publicnode.com rejects address-less getLogs ('Please specify an address'), so it is not used.
Chunks of CHUNK blocks aligned to the window start; bisection on range/size errors and on >= 10,000 results
(possible silent cap). Resumable: each finished chunk is state/chunks/<a>_<b>.csv.gz (atomic rename).
Unrecoverable ranges go to ../gaps.csv. After all chunks: raw log parts, per (pool, topic, hour) aggregates,
bucket headers, cross-endpoint check, emitter metadata at the pinned block (Multicall3 aggregate3 allowFailure),
topic verification on real logs. Sentinel: .sentinels/V2OLD_CENSUS.DONE / .FAILED
"""
import argparse, csv, glob, gzip, io, json, os, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpclib import *

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..'))
WINDOW = 43200
HOUR = 1800
CHUNK = 500
CAP_SUSPECT = 10000
PART_LIMIT = 85 * 1024 * 1024
TOPICS = {
    '0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1': ('sync_uint112', 'Sync(uint112,uint112)'),
    '0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a': ('sync_uint256', 'Sync(uint256,uint256)'),
    '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822': ('swap_univ2', 'Swap(address,uint256,uint256,uint256,uint256,address)'),
    '0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b': ('swap_aero_v2', 'Swap(address,address,uint256,uint256,uint256,uint256)'),
}
KNOWN_FACTORIES = {
    '0x420dd381b31aef6683db6b902084cb0ffece40da': 'Aerodrome', '0x8909dc15e40173ff4699343b6eb8132c65e18ec6': 'UniswapV2',
    '0x71524b4f93c58fcbf659783284e38825f0622859': 'SushiV2', '0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e': 'PancakeV2',
    '0xfda619b6d20975be80a10332cd39b9a4b0faa8bb': 'BaseSwap',
}
LOG_COLS = ['block_number', 'block_timestamp', 'block_hash', 'tx_index', 'tx_hash', 'log_index', 'address', 'event', 'topic0',
            'topic1', 'topic2', 'topic3', 'n_topics', 'data', 'decode_status', 'd_sender', 'd_to', 'd_reserve0', 'd_reserve1',
            'd_amount0_in', 'd_amount1_in', 'd_amount0_out', 'd_amount1_out']

TEN = Endpoint(TENDERLY, 2); TEN.maxrange = 1000
BORG = Endpoint(BASEORG, 1, min_interval=1.0); BORG.maxrange = 2000
DR = Endpoint(DRPC, 1, min_interval=0.3); DR.maxrange = 10
ROT = [TEN, TEN, BORG, TEN, BORG, DR]


def validate(res, a, b):
    if not isinstance(res, list):
        raise RpcErr('json', 'result not a list')
    seen = set()
    for l in res:
        bn = int(l['blockNumber'], 16)
        if bn < a or bn > b:
            raise RpcErr('json', 'log block %d outside [%d,%d]' % (bn, a, b))
        if l['topics'][0].lower() not in TOPICS:
            raise RpcErr('json', 'unexpected topic0 %s' % l['topics'][0])
        if l.get('removed'):
            raise RpcErr('json', 'removed log at %d' % bn)
        k = (bn, int(l['logIndex'], 16))
        if k in seen:
            raise RpcErr('json', 'duplicate log %s' % (k,))
        seen.add(k)


def get_logs(a, b, eps_rot=ROT, depth=0):
    """-> list of (log, endpoint_url). Raises RpcErr when unrecoverable at size 1."""
    back = 1.0
    last = None
    size = b - a + 1
    for attempt in range(12):
        cands = [e for e in eps_rot if e.maxrange >= size]
        if not cands:
            break
        ep = cands[attempt % len(cands)]
        try:
            res = ep.call('eth_getLogs', [{'fromBlock': hex(a), 'toBlock': hex(b), 'topics': [list(TOPICS)]}], timeout=180)
            validate(res, a, b)
            if len(res) >= CAP_SUSPECT and size > 1:
                last = RpcErr('range', '%d results (possible cap)' % len(res))
                break
            return [(l, ep.url) for l in res]
        except RpcErr as e:
            last = e
            if e.kind in ('range', 'size') and size > 1:
                break
            if attempt % 4 == 3:
                log('getLogs retry', a, b, ep.url, e.kind, e.msg[:160])
            time.sleep(min(60.0, back) * (0.5 + __import__('random').random()))
            back = min(60.0, back * 2)
    if size > 1:
        m = (a + b) // 2
        return get_logs(a, m, eps_rot, depth + 1) + get_logs(m + 1, b, eps_rot, depth + 1)
    raise last or RpcErr('rpc', 'no endpoint')


def word(d, i):
    return int(d[2 + 64 * i: 2 + 64 * (i + 1)], 16)


def log_row(l):
    t0 = l['topics'][0].lower()
    ev = TOPICS[t0][0]
    tp = [x.lower() for x in l['topics']] + ['', '', '']
    data = l['data'].lower()
    nd = (len(data) - 2) // 2
    r = {'block_number': int(l['blockNumber'], 16),
         'block_timestamp': int(l['blockTimestamp'], 16) if l.get('blockTimestamp') else '',
         'block_hash': l.get('blockHash', '').lower(), 'tx_index': int(l['transactionIndex'], 16),
         'tx_hash': l['transactionHash'].lower(), 'log_index': int(l['logIndex'], 16), 'address': l['address'].lower(),
         'event': ev, 'topic0': t0, 'topic1': tp[1], 'topic2': tp[2], 'topic3': tp[3], 'n_topics': len(l['topics']), 'data': data}
    if ev.startswith('sync'):
        if len(l['topics']) == 1 and nd == 64:
            r.update(decode_status='ok', d_reserve0=str(word(data, 0)), d_reserve1=str(word(data, 1)))
        else:
            r['decode_status'] = 'layout_mismatch'
    else:
        if len(l['topics']) == 3 and nd == 128 and not any(int(tp[i][2:26] or '0', 16) for i in (1, 2)):
            r.update(decode_status='ok', d_sender='0x' + tp[1][26:], d_to='0x' + tp[2][26:], d_amount0_in=str(word(data, 0)),
                     d_amount1_in=str(word(data, 1)), d_amount0_out=str(word(data, 2)), d_amount1_out=str(word(data, 3)))
        else:
            r['decode_status'] = 'layout_mismatch'
    return r


def chunk_path(state, a, b):
    return os.path.join(state, 'chunks', '%09d_%09d.csv.gz' % (a, b))


def do_chunk(state, a, b):
    p = chunk_path(state, a, b)
    if os.path.exists(p):
        return None
    t0 = time.time()
    got = get_logs(a, b)
    rows = [log_row(l) for l, u in got]
    rows.sort(key=lambda r: (r['block_number'], r['log_index']))
    eps = {}
    for l, u in got:
        eps[u] = eps.get(u, 0) + 1
    tmp = p + '.tmp'
    with gzip.open(tmp, 'wt', newline='') as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([r.get(c, '') for c in LOG_COLS])
    os.replace(tmp, p)
    with open(os.path.join(state, 'chunks.jsonl'), 'a') as f:
        f.write(json.dumps({'a': a, 'b': b, 'n': len(rows), 'endpoints': eps, 'secs': round(time.time() - t0, 2), 'utc': utcnow()}) + '\n')
    return len(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pin', type=int, required=True)
    ap.add_argument('--window', type=int, default=WINDOW)
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--state', default=os.path.join(HERE, 'state', 'census'))
    ap.add_argument('--sentinel', default='V2OLD_CENSUS')
    a = ap.parse_args()
    P = a.pin; S = P - a.window + 1
    os.makedirs(os.path.join(a.state, 'chunks'), exist_ok=True); os.makedirs(a.out, exist_ok=True)
    gaps = os.path.join(a.out, 'gaps.csv')
    meta = {'pinned_block': P, 'window_start_block': S, 'window_end_block': P, 'window_blocks': a.window, 'hour_bucket_blocks': HOUR,
            'chunk_blocks': CHUNK, 'started_utc': utcnow(), 'topics': {k: v[1] for k, v in TOPICS.items()}}
    log('census window', S, P)

    # ---- chunks
    chunks = []
    x = S
    while x <= P:
        chunks.append((x, min(P, x + CHUNK - 1))); x += CHUNK
    todo = [c for c in chunks if not os.path.exists(chunk_path(a.state, *c))]
    log('chunks', len(chunks), 'todo', len(todo))
    failed = []
    with ThreadPoolExecutor(2) as ex:
        futs = {ex.submit(do_chunk, a.state, c[0], c[1]): c for c in todo}
        n = 0
        for f in as_completed(futs):
            c = futs[f]; n += 1
            try:
                k = f.result()
                if n % 10 == 0 or n == len(todo):
                    log('chunk done', c, k, 'progress', n, '/', len(todo))
            except Exception as e:
                failed.append(c)
                append_gap(gaps, ['census', 'getLogs', '%d-%d' % c, repr(e)[:300]])
                log('chunk FAILED', c, repr(e)[:300])
    missing = [c for c in chunks if not os.path.exists(chunk_path(a.state, *c))]
    meta['chunks_total'] = len(chunks); meta['chunks_missing'] = ['%d-%d' % c for c in missing]

    # ---- raw log parts + aggregation
    for old in glob.glob(os.path.join(a.out, 'census-logs-part-*.csv.gz')):
        os.remove(old)
    part = 1; nrows = 0
    agg = {}
    emit = {}
    per_event = {}
    def open_part(k):
        pth = os.path.join(a.out, 'census-logs-part-%04d.csv.gz' % k)
        fo = open(pth, 'wb'); gz = gzip.GzipFile(fileobj=fo, mode='wb'); tw = io.TextIOWrapper(gz, newline='', encoding='utf-8')
        w = csv.writer(tw); w.writerow(LOG_COLS)
        return fo, tw, w
    fo, tw, w = open_part(part)
    ts_mismatch = 0
    for c in chunks:
        pth = chunk_path(a.state, *c)
        if not os.path.exists(pth):
            continue
        with gzip.open(pth, 'rt', newline='') as f:
            for row in csv.reader(f):
                w.writerow(row); nrows += 1
                r = dict(zip(LOG_COLS, row))
                bn = int(r['block_number']); li = int(r['log_index'])
                if r['block_timestamp'] and int(r['block_timestamp']) != BASE_GENESIS_TS + 2 * bn:
                    ts_mismatch += 1
                bk = (bn - S) // HOUR
                key = (r['address'], r['topic0'], bk)
                g = agg.get(key)
                if g is None:
                    g = agg[key] = {'count': 0, 'first': bn, 'last': bn, 'last_li': -1, 'r0': '', 'r1': '', 's': [0, 0, 0, 0], 'bad': 0,
                                    'txs': set()}
                g['count'] += 1
                g['txs'].add(r['tx_hash'])
                g['first'] = min(g['first'], bn)
                if (bn, li) >= (g['last'], g['last_li']):
                    g['last'], g['last_li'] = bn, li
                    if r['event'].startswith('sync'):
                        g['r0'], g['r1'] = r['d_reserve0'], r['d_reserve1']
                if r['decode_status'] != 'ok':
                    g['bad'] += 1
                elif r['event'].startswith('swap'):
                    for i, cc in enumerate(('d_amount0_in', 'd_amount1_in', 'd_amount0_out', 'd_amount1_out')):
                        g['s'][i] += int(r[cc])
                emit.setdefault(r['address'], set()).add(r['event'])
                per_event[r['event']] = per_event.get(r['event'], 0) + 1
                if nrows % 20000 == 0:
                    tw.flush()
                    if fo.tell() > PART_LIMIT:
                        tw.close(); fo.close(); part += 1
                        fo, tw, w = open_part(part)
    tw.close(); fo.close()
    meta['log_rows'] = nrows; meta['log_parts'] = part; meta['log_rows_by_event'] = per_event
    meta['log_timestamp_formula_mismatches'] = ts_mismatch
    log('raw logs written', nrows, 'parts', part, per_event)

    with gzip.open(os.path.join(a.out, 'activity-pool-hour.csv.gz'), 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['pool_address', 'event', 'topic0', 'hour_bucket_index', 'hour_bucket_start_block', 'hour_bucket_end_block', 'count',
                    'distinct_tx_count', 'first_block', 'last_block', 'last_log_index', 'last_sync_reserve0', 'last_sync_reserve1',
                    'sum_amount0_in', 'sum_amount1_in', 'sum_amount0_out', 'sum_amount1_out', 'layout_mismatch_count'])
        for (addr, t0, bk) in sorted(agg):
            g = agg[(addr, t0, bk)]
            ev = TOPICS[t0][0]
            sw = ev.startswith('swap')
            w.writerow([addr, ev, t0, bk, S + bk * HOUR, min(P, S + bk * HOUR + HOUR - 1), g['count'], len(g['txs']), g['first'], g['last'],
                        g['last_li'], g['r0'], g['r1']] + ([str(v) for v in g['s']] if sw else ['', '', '', '']) + [g['bad']])
    meta['activity_rows'] = len(agg); meta['distinct_emitters'] = len(emit)
    log('activity rows', len(agg), 'emitters', len(emit))

    # ---- buckets (headers)
    hdr_eps = [TEN, BORG, Endpoint(DRPC, 1)]
    nb = (P - S) // HOUR + 1
    with open(os.path.join(a.out, 'buckets.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hour_bucket_index', 'start_block', 'end_block', 'start_timestamp', 'end_timestamp', 'start_utc', 'end_utc', 'start_block_hash', 'end_block_hash'])
        for k in range(nb):
            sb = S + k * HOUR; eb = min(P, sb + HOUR - 1)
            hs = call_with_retry(hdr_eps, 'eth_getBlockByNumber', [hex(sb), False], what='hdr')
            he = call_with_retry(hdr_eps, 'eth_getBlockByNumber', [hex(eb), False], what='hdr')
            ts0 = int(hs['timestamp'], 16); ts1 = int(he['timestamp'], 16)
            w.writerow([k, sb, eb, ts0, ts1, time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts0)),
                        time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts1)), hs['hash'], he['hash']])

    # ---- cross-endpoint check on 3 chunks
    with open(os.path.join(a.out, 'census-crosscheck.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['chunk_start', 'chunk_end', 'primary_rows', 'check_endpoint', 'check_rows', 'identical_log_sets', 'only_in_primary', 'only_in_check', 'error'])
        for c in [chunks[0], chunks[len(chunks) // 2], chunks[-1]]:
            pth = chunk_path(a.state, *c)
            if not os.path.exists(pth):
                continue
            with gzip.open(pth, 'rt', newline='') as fz:
                prim = {tuple(r[i] for i in (0, 4, 5, 6, 8, 13)) for r in csv.reader(fz)}
            try:
                res = []
                for sa in range(c[0], c[1] + 1, 2000):
                    res += call_with_retry([BORG], 'eth_getLogs', [{'fromBlock': hex(sa), 'toBlock': hex(min(c[1], sa + 1999)), 'topics': [list(TOPICS)]}], what='xcheck')
                chk = set()
                for l in res:
                    r = log_row(l)
                    chk.add(tuple(str(r[k]) for k in ('block_number', 'tx_hash', 'log_index', 'address', 'topic0', 'data')))
                w.writerow([c[0], c[1], len(prim), BASEORG, len(chk), prim == chk, len(prim - chk), len(chk - prim), ''])
            except Exception as e:
                w.writerow([c[0], c[1], len(prim), BASEORG, '', '', '', '', repr(e)[:200]])

    # ---- emitter metadata at the pinned block
    addrs = sorted(emit)
    blast = Endpoint(BLAST, 1); drpc = Endpoint(DRPC, 1)
    mc_eps = [blast, drpc]
    def fns(addr):
        f = ['factory', 'token0', 'token1', 'getReserves']
        if emit[addr] & {'sync_uint256', 'swap_aero_v2'}:
            f.append('stable')
        return f
    B = 100
    batches = [addrs[k:k + B] for k in range(0, len(addrs), B)]
    store = BatchStore(os.path.join(a.state, 'emitters.jsonl'))
    def do_b(b, batch):
        calls = [(ad, '0x' + SEL[fn]) for ad in batch for fn in fns(ad)]
        return [[s, '0x' + d.hex(), e] for s, d, e in multicall(mc_eps, hex(P), calls, what='emit b%d' % b)]
    todo = [b for b in range(len(batches)) if b not in store.done]
    log('emitter batches', len(batches), 'todo', len(todo))
    with ThreadPoolExecutor(1) as ex:
        futs = {ex.submit(do_b, b, batches[b]): b for b in todo}
        for f in as_completed(futs):
            b = futs[f]
            try:
                store.add(b, f.result())
            except Exception as e:
                append_gap(gaps, ['census', 'emitters', 'batch %d' % b, repr(e)[:300]])
    with gzip.open(os.path.join(a.out, 'emitters.csv.gz'), 'wt', newline='') as f:
        w = csv.writer(f)
        w.writerow(['address', 'snapshot_block', 'events_seen', 'factory', 'factory_status', 'known_factory_name_derived', 'token0', 'token0_status',
                    'token1', 'token1_status', 'reserves_status', 'reserves_ret_bytes', 'reserve0', 'reserve1', 'block_timestamp_last',
                    'reserves_extra_hex', 'stable', 'stable_status', 'failures'])
        for b, batch in enumerate(batches):
            rows = store.done.get(b)
            pos = 0
            for ad in batch:
                fl = fns(ad)
                rr = rows[pos:pos + len(fl)] if rows else [['rpc_failed', '0x', 'batch not collected, see gaps.csv']] * len(fl)
                pos += len(fl)
                res = dict(zip(fl, rr)); fails = []
                def g(fn):
                    s, dh, e = res[fn]; d = bytes.fromhex(dh[2:])
                    if s != 'ok':
                        fails.append('%s=%s:%s%s' % (fn, s, dh, (':' + e) if e else ''))
                    return s, d
                fa, fst = dec_addr(*g('factory'))
                t0, t0s = dec_addr(*g('token0')); t1, t1s = dec_addr(*g('token1'))
                s, d = g('getReserves'); (r0, r1, tl), rs = dec_words(s, d, 3)
                if 'stable' in res:
                    sv, svs = dec_bool(*g('stable'))
                else:
                    sv, svs = '', 'not_called'
                w.writerow([ad, P, ';'.join(sorted(emit[ad])), fa, fst, KNOWN_FACTORIES.get(fa, ''), t0, t0s, t1, t1s, rs,
                            len(d) if s == 'ok' else '', r0, r1, tl, ('0x' + d[96:].hex()) if (s == 'ok' and len(d) > 96) else '',
                            sv, svs, '|'.join(fails)])
    store.close()
    meta['emitter_rows'] = len(addrs)

    # ---- topic verification on real logs
    emitter_factory = {}
    with gzip.open(os.path.join(a.out, 'emitters.csv.gz'), 'rt', newline='') as f:
        for r in csv.DictReader(f):
            emitter_factory[r['address']] = r['known_factory_name_derived']
    want = {'sync_uint112': 'UniswapV2', 'swap_univ2': 'UniswapV2', 'sync_uint256': 'Aerodrome', 'swap_aero_v2': 'Aerodrome'}
    examples = {}
    last_in_block = {}
    for c in reversed(chunks):
        pth = chunk_path(a.state, *c)
        if not os.path.exists(pth):
            continue
        with gzip.open(pth, 'rt', newline='') as fz:
            rows = [dict(zip(LOG_COLS, r)) for r in csv.reader(fz)]
        for r in rows:
            kk = (r['address'], r['block_number'], r['event'])
            last_in_block[kk] = r  # rows sorted by (block, log_index): keeps the last log of that pool/event in the block
        for r in rows:
            ev = r['event']
            if ev not in examples and emitter_factory.get(r['address']) == want[ev] and r['decode_status'] == 'ok' \
                    and last_in_block[(r['address'], r['block_number'], ev)] is r:
                examples[ev] = r
        if len(examples) == 4:
            break
    import subprocess
    with open(os.path.join(a.out, 'topics.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['event', 'signature', 'topic0', 'topic0_cast_keccak', 'topic0_python_keccak', 'example_block', 'example_tx', 'example_log_index',
                    'example_emitter', 'emitter_factory_name_derived', 'check', 'check_result', 'rows_in_window'])
        from eth_hash.auto import keccak
        for t0, (ev, sig) in TOPICS.items():
            try:
                ck = subprocess.run(['/root/.foundry/bin/cast', 'keccak', sig], capture_output=True, text=True, timeout=30).stdout.strip()
            except Exception as e:
                ck = 'error ' + repr(e)[:60]
            pk = '0x' + keccak(sig.encode()).hex()
            r = examples.get(ev)
            if not r:
                w.writerow([ev, sig, t0, ck, pk, '', '', '', '', '', 'no example log from a known factory pool in window', '', per_event.get(ev, 0)])
                continue
            blk = int(r['block_number'])
            if ev.startswith('sync'):
                res = multicall(mc_eps, hex(blk), [(r['address'], '0x' + SEL['getReserves'])])
                (g0, g1, gl), gs = dec_words(res[0][0], res[0][1], 3)
                chk = 'getReserves() at end of example block == decoded Sync(reserve0,reserve1) of the last Sync of that pool in the block'
                cres = 'match' if (g0, g1) == (r['d_reserve0'], r['d_reserve1']) else 'MISMATCH getReserves=(%s,%s) status=%s' % (g0, g1, gs)
            else:
                chk = 'topics=[topic0,sender,to], data=4x uint256, emitter factory() is the expected factory'
                cres = 'match' if (r['n_topics'] == '3' and len(r['data']) == 2 + 256) else 'MISMATCH'
            w.writerow([ev, sig, t0, ck, pk, blk, r['tx_hash'], r['log_index'], r['address'], emitter_factory.get(r['address'], ''), chk, cres,
                        per_event.get(ev, 0)])

    # chunk provenance
    with open(os.path.join(a.state, 'chunks.jsonl')) as fz:
        prov = {}
        for line in fz:
            j = json.loads(line); prov[(j['a'], j['b'])] = j
    with open(os.path.join(a.out, 'census-chunks.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['chunk_start', 'chunk_end', 'log_rows', 'endpoints_used', 'fetch_secs', 'fetched_utc', 'status'])
        for c in chunks:
            j = prov.get(c)
            st = 'ok' if os.path.exists(chunk_path(a.state, *c)) else 'MISSING (see gaps.csv)'
            w.writerow([c[0], c[1], j['n'] if j else '', json.dumps(j['endpoints']) if j else '', j['secs'] if j else '', j['utc'] if j else '', st])
    meta['finished_utc'] = utcnow()
    meta['endpoint_stats'] = {e.url: e.stats for e in (TEN, BORG, DR, blast, drpc)}
    with open(os.path.join(a.out, 'census-meta.json'), 'w') as f:
        json.dump(meta, f, indent=1)
    if a.sentinel != 'none':
        if missing:
            write_sentinel(a.sentinel, False, 'missing chunks: %s (rerun census.py to retry)' % meta['chunks_missing'])
        else:
            write_sentinel(a.sentinel, True, 'log_rows=%d activity_rows=%d emitters=%d window=%d-%d' % (nrows, len(agg), len(addrs), S, P))
    log('census done', json.dumps(meta)[:1500])


if __name__ == '__main__':
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log('FATAL', tb)
        if '--sentinel' not in sys.argv:
            write_sentinel('V2OLD_CENSUS', False, tb[-1500:])
        sys.exit(1)
