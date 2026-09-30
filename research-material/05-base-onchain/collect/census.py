#!/usr/bin/env python3
"""Base contiguous-block census collector (raw data only).

One process = one stream over a contiguous block range:
  --stream bf : backfill [start, end] via base.drpc.org (eth_getBlockReceipts + eth_getBlockByNumber(n,false))
  --stream bf2 (bf3, ...): backfill helper for the upper part of the backfill range via gateway.tenderly.co/public/base
                (fallback base-rpc.publicnode.com); added 2026-09-30 ~21:15Z because drpc throughput dropped (HTTP 429)
  --stream fw : follow the head from --start via base-rpc.publicnode.com (fallback base.drpc.org),
                until the stop condition in state/config.json holds (see supervisor.py), then drain to stop_block.
  --stream gf (gf1, ...): re-fetch the block numbers listed in --blocks-file (gap fill) via gateway.tenderly.co,
                base.drpc.org (1 in-flight), base-rpc.publicnode.com; blocks already present in any blocks part are skipped
                (listed in the checkpoint as skipped_already_present).

Per block it writes (gzip members appended per chunk, parts rotated below PART_LIMIT bytes):
  blocks-<stream>-NNNN.csv.gz, txs-<stream>-NNNN.csv.gz, reverted-<stream>-NNNN.csv.gz, candidates-<stream>-NNNN.jsonl.gz
Resumable: state/<stream>.ckpt.json holds next block + byte size of every open part; on restart parts are
truncated back to the checkpointed size (drops any partially written member) and newer parts are deleted.
Unrecoverable blocks are appended to gaps.csv (never silently skipped).
"""
import argparse, csv, gzip, io, json, os, random, re, sys, threading, time, zlib
from concurrent.futures import ThreadPoolExecutor
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
STATE = os.path.join(HERE, 'state')
DATA = os.path.join(OUTDIR, 'data')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
DRPC = 'https://base.drpc.org'
PUBLICNODE = 'https://base-rpc.publicnode.com'
TENDERLY = 'https://gateway.tenderly.co/public/base'
PART_LIMIT = 85 * 1024 * 1024
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
KINDS = {
    'blocks': ('csv', ['block_number', 'timestamp', 'base_fee_per_gas', 'gas_used', 'gas_limit', 'tx_count', 'miner', 'block_hash', 'parent_hash']),
    'txs': ('csv', ['block_number', 'tx_index', 'tx_hash', 'from', 'to', 'status', 'gas_used', 'effective_gas_price', 'l1_fee', 'tx_type', 'logs_count', 'candidate_criterion']),
    'reverted': ('csv', ['block_number', 'tx_index', 'tx_hash', 'from', 'to', 'gas_used', 'effective_gas_price', 'l1_fee', 'logs_count', 'tx_type']),
    'candidates': ('jsonl', None),
    'provenance': ('csv', ['block_number', 'endpoint', 'receipts_method']),
}


def utcnow():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def log(*a):
    print(utcnow(), *a, flush=True)


def load_topics():
    p = os.path.join(HERE, 'swap_topics_used.csv')
    with open(p) as f:
        return {r['topic0'].lower(): r['signature'] for r in csv.DictReader(f)}


class RateLimiter:
    def __init__(self, per_sec):
        self.iv = 1.0 / per_sec if per_sec else 0
        self.lock = threading.Lock()
        self.next = 0.0

    def wait(self):
        if not self.iv:
            return
        with self.lock:
            now = time.time()
            t = max(now, self.next)
            self.next = t + self.iv
        d = t - time.time()
        if d > 0:
            time.sleep(d)


class Endpoint:
    def __init__(self, url, max_inflight, per_sec=None):
        self.url = url
        self.sem = threading.BoundedSemaphore(max_inflight)
        self.rl = RateLimiter(per_sec)
        self.tl = threading.local()

    def session(self):
        s = getattr(self.tl, 's', None)
        if s is None:
            s = requests.Session()
            s.headers.update({'User-Agent': UA, 'Content-Type': 'application/json'})
            self.tl.s = s
        return s

    def call(self, method, params, timeout=90):
        """One attempt. Raises RpcErr(kind, msg)."""
        self.rl.wait()
        with self.sem:
            try:
                r = self.session().post(self.url, data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}), timeout=timeout)
            except Exception as e:
                raise RpcErr('net', repr(e)[:200])
        if r.status_code == 429:
            raise RpcErr('429', 'http 429')
        if r.status_code >= 500:
            raise RpcErr('5xx', 'http %d' % r.status_code)
        if r.status_code != 200:
            raise RpcErr('http', 'http %d %s' % (r.status_code, r.text[:200]))
        try:
            j = r.json()
        except Exception as e:
            raise RpcErr('json', repr(e)[:200])
        if 'error' in j and j['error']:
            msg = json.dumps(j['error'])[:300]
            kind = 'size' if any(k in msg.lower() for k in ('too large', 'size', 'limit exceeded', 'response is too big')) else 'rpc'
            if 'rate' in msg.lower() or 'too many' in msg.lower():
                kind = '429'
            raise RpcErr(kind, msg)
        return j.get('result')


class RpcErr(Exception):
    def __init__(self, kind, msg):
        super().__init__(kind + ': ' + msg)
        self.kind = kind


def hx(v):
    return None if v is None else int(v, 16)


def lower(v):
    return v.lower() if isinstance(v, str) else v


def fetch_block(n, eps, max_attempts, stats):
    """Returns (block, receipts) validated, or raises after max_attempts.
    Endpoint order: eps[0] for the first 3 attempts, then alternate over eps.
    After a size error, or after 6 failed attempts with other errors, switch to per-tx eth_getTransactionReceipt."""
    back = 1.0
    last = ''
    per_tx_mode = False
    for attempt in range(max_attempts):
        ep = eps[0] if attempt < 3 else eps[attempt % len(eps)]
        try:
            blk = ep.call('eth_getBlockByNumber', [hex(n), False])
            if blk is None:
                raise RpcErr('notyet', 'block null')
            if per_tx_mode:
                rcpts = []
                for h in blk['transactions']:
                    rc = ep.call('eth_getTransactionReceipt', [h])
                    if rc is None:
                        raise RpcErr('notyet', 'receipt null ' + h)
                    rcpts.append(rc)
            else:
                rcpts = ep.call('eth_getBlockReceipts', [hex(n)])
            if rcpts is None:
                raise RpcErr('notyet', 'receipts null')
            txh = [h.lower() for h in blk['transactions']]
            if len(rcpts) != len(txh):
                raise RpcErr('mismatch', 'receipts %d != txs %d' % (len(rcpts), len(txh)))
            bh = blk['hash'].lower()
            for i, rc in enumerate(rcpts):
                if hx(rc['transactionIndex']) != i or rc['transactionHash'].lower() != txh[i] or rc['blockHash'].lower() != bh:
                    raise RpcErr('mismatch', 'receipt %d does not match block tx list/hash' % i)
            stats['ok'] += 1
            return blk, rcpts, ep.url, ('eth_getTransactionReceipt per tx' if per_tx_mode else 'eth_getBlockReceipts')
        except RpcErr as e:
            last = '%s via %s' % (e, ep.url)
            stats[e.kind] = stats.get(e.kind, 0) + 1
            if e.kind == 'size' or (attempt >= 6 and e.kind not in ('429', 'notyet', 'mismatch')):
                per_tx_mode = True
            if e.kind in ('notyet', 'mismatch'):
                time.sleep(2 + random.random())
            else:
                time.sleep(back + random.random())
                back = min(back * 2, 60)
    raise RuntimeError('block %d failed after %d attempts: %s' % (n, max_attempts, last))


def classify(logs, topics):
    nswap = 0
    ntr = 0
    toks = set()
    for L in logs:
        t = L['topics']
        if not t:
            continue
        t0 = t[0].lower()
        if t0 in topics:
            nswap += 1
        elif t0 == TRANSFER and len(t) == 3:
            ntr += 1
            toks.add(L['address'].lower())
    if nswap >= 2:
        return 'A', nswap, ntr, len(toks)
    if ntr >= 3 and len(toks) >= 2:
        return 'B', nswap, ntr, len(toks)
    return '', nswap, ntr, len(toks)


def dec(v):
    return '' if v is None else str(int(v, 16))


def render(blk, rcpts, topics, first_seen):
    n = hx(blk['number'])
    ts = hx(blk['timestamp'])
    bf = blk.get('baseFeePerGas')
    brow = [n, ts, dec(bf), dec(blk['gasUsed']), dec(blk['gasLimit']), len(blk['transactions']), lower(blk.get('miner')), blk['hash'].lower(), blk['parentHash'].lower()]
    txrows, revrows, cands = [], [], []
    for rc in rcpts:
        i = hx(rc['transactionIndex'])
        logs = rc.get('logs') or []
        crit, nswap, ntr, ntok = classify(logs, topics)
        for L in logs:
            if L['topics']:
                t0 = L['topics'][0].lower()
                if t0 in topics and t0 not in first_seen:
                    first_seen[t0] = {'tx_hash': rc['transactionHash'].lower(), 'block_number': n, 'emitter': L['address'].lower()}
        st = hx(rc.get('status')) if rc.get('status') is not None else ''
        frm = lower(rc.get('from'))
        to = lower(rc.get('to')) or ''
        txrows.append([n, i, rc['transactionHash'].lower(), frm, to, st, dec(rc.get('gasUsed')), dec(rc.get('effectiveGasPrice')), dec(rc.get('l1Fee')), lower(rc.get('type')) or '', len(logs), crit])
        if st == 0:
            revrows.append([n, i, rc['transactionHash'].lower(), frm, to, dec(rc.get('gasUsed')), dec(rc.get('effectiveGasPrice')), dec(rc.get('l1Fee')), len(logs), lower(rc.get('type')) or ''])
        if crit:
            sub = {k: v for k, v in rc.items() if k != 'logs'}
            cands.append(json.dumps({
                'block_number': n, 'block_timestamp': ts, 'tx_index': i, 'tx_hash': rc['transactionHash'].lower(),
                'from': frm, 'to': to or None, 'status': st, 'gas_used': dec(rc.get('gasUsed')),
                'effective_gas_price': dec(rc.get('effectiveGasPrice')), 'criterion': crit,
                'derived': {'n_swap_topic_logs': nswap, 'n_erc20_transfer_logs': ntr, 'n_erc20_transfer_token_contracts': ntok},
                'receipt': sub,
                'logs': [{'address': L['address'].lower(), 'topics': [t.lower() for t in L['topics']], 'data': L['data'].lower(), 'log_index': hx(L['logIndex'])} for L in logs],
            }, separators=(',', ':')))
    return brow, txrows, revrows, cands


class PartWriter:
    def __init__(self, stream, ck):
        self.stream = stream
        self.parts = ck.setdefault('parts', {})
        for k in KINDS:
            st = self.parts.setdefault(k, {'part': 1, 'size': 0})
            p = self.path(k, st['part'])
            if os.path.exists(p):
                if os.path.getsize(p) > st['size']:
                    with open(p, 'r+b') as f:
                        f.truncate(st['size'])
                    log('truncated', p, 'to', st['size'])
            # remove parts newer than checkpoint
            j = st['part'] + 1
            while os.path.exists(self.path(k, j)):
                os.remove(self.path(k, j)); log('removed stale part', self.path(k, j)); j += 1

    def path(self, k, part):
        ext = 'csv.gz' if KINDS[k][0] == 'csv' else 'jsonl.gz'
        return os.path.join(DATA, '%s-%s-%04d.%s' % (k, self.stream, part, ext))

    def append(self, k, payload_rows):
        st = self.parts[k]
        if st['size'] >= PART_LIMIT:
            st['part'] += 1; st['size'] = 0
        p = self.path(k, st['part'])
        buf = io.StringIO()
        fmt, header = KINDS[k]
        if fmt == 'csv':
            w = csv.writer(buf, lineterminator='\n')
            if st['size'] == 0:
                w.writerow(header)
            w.writerows(payload_rows)
        else:
            for line in payload_rows:
                buf.write(line); buf.write('\n')
        data = buf.getvalue().encode()
        if not data:
            if st['size'] == 0 and not os.path.exists(p):
                open(p, 'wb').close()
            return
        with open(p, 'ab') as f:
            f.seek(0, 2)
            if f.tell() != st['size']:
                f.truncate(st['size'])
                f.seek(st['size'])
            with gzip.GzipFile(fileobj=f, mode='wb', compresslevel=6, mtime=0) as g:
                g.write(data)
            f.flush(); os.fsync(f.fileno())
            st['size'] = f.tell()


def blocks_present():
    import glob
    out = set()
    for p in glob.glob(os.path.join(DATA, 'blocks-*-*.csv.gz')) + glob.glob(os.path.join(STATE, 'blocks-parts', 'blocks-*-*.csv.gz')):
        try:
            with gzip.open(p, 'rt') as f:
                for row in csv.reader(f):
                    if row and row[0] != 'block_number':
                        out.add(int(row[0]))
        except (EOFError, OSError, ValueError, zlib.error):
            pass  # a part being appended by a running stream; its complete members were read
    return out


def save_json(p, obj):
    tmp = p + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=1, sort_keys=True); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def load_json(p, default):
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return default


def record_gap(stream, n, reason):
    p = os.path.join(OUTDIR, 'gaps.csv')
    new = not os.path.exists(p)
    with open(p, 'a', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['stream', 'block_number', 'recorded_utc', 'reason'])
        w.writerow([stream, n, utcnow(), reason[:500]])
        f.flush(); os.fsync(f.fileno())


def sentinel_stop(cfg):
    sd = cfg['sentinel_dir']
    v4 = any(os.path.exists(os.path.join(sd, 'V4LIVE.' + s)) for s in ('DONE', 'FAILED'))
    sh = any(os.path.exists(os.path.join(sd, 'SHALLOW_LIVE.' + s)) for s in ('DONE', 'FAILED'))
    if v4 and sh:
        return 'sentinels V4LIVE.* and SHALLOW_LIVE.* both present'
    if time.time() >= cfg['launch_unix'] + cfg['max_follow_seconds']:
        return 'max follow time reached (%d s after launch)' % cfg['max_follow_seconds']
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stream', required=True, help='bf | bf2, bf3, ... | fw | gf, gf1, ... | smoke')
    ap.add_argument('--start', type=int)
    ap.add_argument('--end', type=int)
    ap.add_argument('--blocks-file')
    ap.add_argument('--chunk', type=int, default=40)
    ap.add_argument('--workers', type=int, default=3)
    args = ap.parse_args()
    if not re.match(r'^(bf\d*|fw|gf\d*|smoke)$', args.stream):
        ap.error('bad --stream')
    os.makedirs(STATE, exist_ok=True); os.makedirs(DATA, exist_ok=True)
    topics = load_topics()
    cfg = load_json(os.path.join(STATE, 'config.json'), {})
    stream = args.stream
    ckp = os.path.join(STATE, '%s.ckpt.json' % stream)
    ck = load_json(ckp, {})
    if not ck:
        ck = {'stream': stream, 'start': args.start, 'end': args.end, 'next': args.start, 'created_utc': utcnow(), 'topics_n': len(topics)}
        if stream.startswith('gf'):
            with open(args.blocks_file) as f:
                req = sorted({int(x) for x in f.read().split() if x.strip()})
            present = blocks_present()
            ck['requested'] = req
            ck['skipped_already_present'] = [n for n in req if n in present]
            ck['todo'] = [n for n in req if n not in present]
            ck['next'] = 0
        save_json(ckp, ck)
    if ck.get('done'):
        log('stream already done', stream); return 0
    fs_p = os.path.join(STATE, 'first_seen_%s.json' % stream)
    first_seen = load_json(fs_p, {})
    pw = PartWriter(stream, ck)
    stats = {'ok': 0}
    drpc = Endpoint(DRPC, max_inflight=args.workers if stream in ('bf', 'smoke') else 1)
    pn = Endpoint(PUBLICNODE, max_inflight=2, per_sec=2.0)
    if stream in ('bf', 'smoke'):
        eps, max_att = [drpc], 14
    elif re.match(r'^bf\d+$', stream):
        eps, max_att = [Endpoint(TENDERLY, max_inflight=3), Endpoint(PUBLICNODE, max_inflight=1, per_sec=1.0)], 14
    elif stream == 'fw':
        eps, max_att = [pn, drpc], 16
    else:  # gf, gf1, ...: gap fill
        eps, max_att = [Endpoint(TENDERLY, max_inflight=2), drpc, Endpoint(PUBLICNODE, max_inflight=1, per_sec=1.0)], 20
    pool = ThreadPoolExecutor(max_workers=args.workers)
    lag = cfg.get('head_lag', 10)
    t_last = time.time(); blocks_since = 0
    head_cache = [0, 0.0]

    def head():
        if time.time() - head_cache[1] > 4:
            for ep in eps:
                try:
                    head_cache[0] = int(ep.call('eth_blockNumber', []), 16); head_cache[1] = time.time(); break
                except Exception as e:
                    log('head err', e)
        return head_cache[0]

    while True:
        # decide next chunk
        if stream.startswith('gf'):
            todo = ck['todo']
            if ck['next'] >= len(todo):
                break
            nums = todo[ck['next']: ck['next'] + args.chunk]
        else:
            nxt = ck['next']
            if stream == 'fw':
                if ck.get('stop_block') is None:
                    reason = sentinel_stop(cfg)
                    if reason:
                        h = head()
                        ck['stop_block'] = h - lag + cfg.get('stop_margin_blocks', 150)
                        ck['stop_reason'] = reason; ck['stop_detected_utc'] = utcnow(); ck['stop_detected_head'] = h
                        save_json(ckp, ck); log('STOP condition:', reason, 'stop_block', ck['stop_block'])
                hi = head() - lag
                if ck.get('stop_block') is not None:
                    hi = min(hi, ck['stop_block'])
                    if nxt > ck['stop_block']:
                        break
                if hi < nxt:
                    time.sleep(2); continue
                nums = list(range(nxt, min(hi, nxt + args.chunk - 1) + 1))
            else:
                if nxt > ck['end']:
                    break
                nums = list(range(nxt, min(ck['end'], nxt + args.chunk - 1) + 1))

        def job(n):
            try:
                return n, fetch_block(n, eps, max_att, stats), None
            except Exception as e:
                return n, None, str(e)
        results = list(pool.map(job, nums))
        B, T, R, C, P = [], [], [], [], []
        for n, res, err in results:
            if err:
                log('GAP', n, err); record_gap(stream, n, err); continue
            b, t, r, c = render(res[0], res[1], topics, first_seen)
            B.append(b); T.extend(t); R.extend(r); C.extend(c); P.append([n, res[2], res[3]])
        pw.append('blocks', B); pw.append('txs', T); pw.append('reverted', R); pw.append('candidates', C); pw.append('provenance', P)
        if stream.startswith('gf'):
            ck['next'] += len(nums)
        else:
            ck['next'] = nums[-1] + 1
        ck['last_written_utc'] = utcnow()
        ck['stats'] = stats
        save_json(fs_p, first_seen)
        save_json(ckp, ck)
        blocks_since += len(nums)
        if time.time() - t_last > 60:
            log('progress stream=%s next=%s blocks/s=%.2f stats=%s parts=%s' % (stream, ck['next'], blocks_since / (time.time() - t_last), stats, {k: v['part'] for k, v in ck['parts'].items()}))
            t_last = time.time(); blocks_since = 0
    ck['done'] = True; ck['done_utc'] = utcnow(); ck['stats'] = stats
    save_json(ckp, ck)
    log('stream done', stream, ck)
    return 0


if __name__ == '__main__':
    sys.exit(main())
