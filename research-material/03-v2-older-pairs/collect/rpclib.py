#!/usr/bin/env python3
"""Shared helpers for the 03-v2-older-pairs collectors (raw data collection only).

- Endpoint: JSON-RPC over HTTPS with a per-endpoint in-flight cap, browser User-Agent, typed errors.
- call_with_retry: exponential backoff with jitter on HTTP 429 / 5xx / network errors, alternating endpoints.
- Multicall3 aggregate3 (allowFailure=true) hand-rolled ABI encode/decode, with batch bisection when the whole
  eth_call fails (e.g. out of gas caused by one sub-call), so that every sub-call ends with a recorded status.
- Lossless decoders for address / uint / bool / string-or-bytes32 return data.
- BatchStore: append-only JSONL of completed batches (resumable checkpoint), gaps file for unrecoverable batches.
"""
import json, os, random, threading, time
import requests

UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
BLAST = 'https://base-mainnet.public.blastapi.io'
DRPC = 'https://base.drpc.org'
TENDERLY = 'https://gateway.tenderly.co/public/base'
BASEORG = 'https://mainnet.base.org'
PUBLICNODE = 'https://base-rpc.publicnode.com'
MULTICALL3 = '0xca11bde05977b3631167028862be2a173976ca11'
BASE_GENESIS_TS = 1686789347  # Base block n has timestamp BASE_GENESIS_TS + 2*n (checked on live headers)

SEL = {
    'allPairs': '1e3dd18b', 'allPairsLength': '574f2ba3', 'allPools': '41d1de97', 'allPoolsLength': 'efde4e64',
    'token0': '0dfe1681', 'token1': 'd21220a7', 'getReserves': '0902f1ac', 'stable': '22be3de1',
    'getFee': 'cc56b2c5', 'symbol': '95d89b41', 'name': '06fdde03', 'decimals': '313ce567',
    'totalSupply': '18160ddd', 'factory': 'c45a0155', 'aggregate3': '82ad56cb',
}


def utcnow():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def log(*a):
    print(utcnow(), *a, flush=True)


class RpcErr(Exception):
    def __init__(self, kind, msg):
        super().__init__(kind + ': ' + msg)
        self.kind = kind  # '429' | '5xx' | 'net' | 'http' | 'json' | 'size' | 'range' | 'revert' | 'rpc'
        self.msg = msg


class Endpoint:
    def __init__(self, url, max_inflight=2, min_interval=0.0):
        self.url = url
        self.sem = threading.BoundedSemaphore(max_inflight)
        self.tl = threading.local()
        self.lock = threading.Lock()
        self.min_interval = min_interval
        self.next_t = 0.0
        self.stats = {'ok': 0, 'err': 0}

    def _session(self):
        s = getattr(self.tl, 's', None)
        if s is None:
            s = requests.Session()
            s.headers.update({'User-Agent': UA, 'Content-Type': 'application/json'})
            self.tl.s = s
        return s

    def call(self, method, params, timeout=120):
        if self.min_interval:
            with self.lock:
                now = time.time()
                t = max(now, self.next_t)
                self.next_t = t + self.min_interval
            d = t - time.time()
            if d > 0:
                time.sleep(d)
        with self.sem:
            try:
                r = self._session().post(self.url, data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}), timeout=timeout)
            except Exception as e:
                self.stats['err'] += 1
                raise RpcErr('net', repr(e)[:200])
        if r.status_code == 429:
            self.stats['err'] += 1
            raise RpcErr('429', 'http 429')
        if r.status_code >= 500:
            self.stats['err'] += 1
            raise RpcErr('5xx', 'http %d %s' % (r.status_code, r.text[:200]))
        if r.status_code != 200:
            self.stats['err'] += 1
            raise RpcErr('http', 'http %d %s' % (r.status_code, r.text[:200]))
        try:
            j = r.json()
        except Exception as e:
            self.stats['err'] += 1
            raise RpcErr('json', repr(e)[:200] + ' body=' + r.text[:200])
        if isinstance(j, dict) and j.get('error'):
            self.stats['err'] += 1
            err = j['error']
            msg = json.dumps(err)[:400]
            low = msg.lower()
            if 'execution reverted' in low or 'out of gas' in low or 'revert' in low or 'gas required exceeds' in low:
                kind = 'revert'
            elif 'timeout' in low or 'timed out' in low or 'execution aborted' in low:
                kind = 'timeout'
            elif 'rate' in low or 'too many requests' in low or 'capacity' in low or 'exceeded the quota' in low:
                kind = '429'
            elif any(k in low for k in ('block range', 'range', 'too many results', 'more than', 'limit', 'too large', 'response size', 'query returned')):
                kind = 'range'
            else:
                kind = 'rpc'
            raise RpcErr(kind, msg)
        self.stats['ok'] += 1
        return j.get('result')


def call_with_retry(eps, method, params, max_attempts=30, no_retry_kinds=('revert', 'range'), logger=log, what=''):
    """Try endpoints in rotation (eps[0] first). Retries transient errors with exponential backoff + jitter.
    Errors whose kind is in no_retry_kinds are raised immediately (caller bisects). Raises the last RpcErr."""
    back = 1.0
    last = None
    for attempt in range(max_attempts):
        ep = eps[attempt % len(eps)] if attempt >= 2 else eps[0]
        try:
            return ep.call(method, params)
        except RpcErr as e:
            last = e
            if e.kind in no_retry_kinds:
                # 'range' on one endpoint may be fine on another; let caller decide
                raise
            if attempt % 5 == 4:
                logger('retry', what, method, ep.url, e.kind, e.msg[:160], 'attempt', attempt + 1)
            time.sleep(min(60.0, back) * (0.5 + random.random()))
            back = min(60.0, back * 2)
    raise last


# ---------------- ABI helpers ----------------

def _w(n):
    return '%064x' % n


def enc_addr(a):
    return '0' * 24 + a.lower()[2:]


def enc_uint(n):
    return _w(n)


def enc_bool(b):
    return _w(1 if b else 0)


def encode_aggregate3(calls):
    """calls: list of (target, calldata_hex_without_0x). allowFailure = true for all."""
    n = len(calls)
    tuples = []
    for target, cd in calls:
        cd = cd[2:] if cd.startswith('0x') else cd
        blen = len(cd) // 2
        pad = (-len(cd)) % 64
        t = enc_addr(target) + enc_bool(True) + _w(0x60) + _w(blen) + cd + '0' * pad
        tuples.append(t)
    offsets = []
    off = 32 * n
    for t in tuples:
        offsets.append(_w(off))
        off += len(t) // 2
    body = _w(0x20) + _w(n) + ''.join(offsets) + ''.join(tuples)
    return '0x' + SEL['aggregate3'] + body


def decode_aggregate3(ret_hex, n_expected):
    b = bytes.fromhex(ret_hex[2:])
    def word(o):
        return int.from_bytes(b[o:o + 32], 'big')
    base = word(0)
    n = word(base)
    if n != n_expected:
        raise ValueError('aggregate3 returned %d results, expected %d' % (n, n_expected))
    head = base + 32
    out = []
    for i in range(n):
        to = head + word(head + 32 * i)
        ok = word(to) == 1
        doff = to + word(to + 32)
        ln = word(doff)
        data = b[doff + 32: doff + 32 + ln]
        out.append((ok, data))
    return out


def multicall(eps, block_tag, calls, logger=log, what=''):
    """Returns list of (status, data_bytes, err) per call.
    status: 'ok' (success, >=1 byte returned), 'empty' (success, 0 bytes: e.g. target has no code),
            'revert' (sub-call failed; data = revert data), 'batch_error' (even a 1-call aggregate3 failed at RPC level;
            err holds the RPC message).
    Transient RPC errors are retried (call_with_retry); whole-batch reverts are bisected."""
    if not calls:
        return []
    data = encode_aggregate3(calls)
    try:
        res = call_with_retry(eps, 'eth_call', [{'to': MULTICALL3, 'data': data}, block_tag], max_attempts=12,
                              no_retry_kinds=('revert', 'range', 'timeout'), logger=logger, what=what)
        dec = decode_aggregate3(res, len(calls))
    except RpcErr as e:
        if e.kind not in ('revert', 'range', 'rpc', 'json', 'timeout'):
            raise
        if len(calls) == 1:
            return [('batch_error', b'', e.kind + ': ' + e.msg[:300])]
        mid = len(calls) // 2
        return multicall(eps, block_tag, calls[:mid], logger, what) + multicall(eps, block_tag, calls[mid:], logger, what)
    except ValueError as e:
        if len(calls) == 1:
            return [('batch_error', b'', 'decode: ' + str(e)[:300])]
        mid = len(calls) // 2
        return multicall(eps, block_tag, calls[:mid], logger, what) + multicall(eps, block_tag, calls[mid:], logger, what)
    out = []
    for ok, d in dec:
        if ok:
            out.append(('ok' if len(d) > 0 else 'empty', d, ''))
        else:
            out.append(('revert', d, ''))
    return out


def dec_addr(st, d):
    """-> (value, status). value '' unless ok. Status 'baddata' if not exactly one clean address word."""
    if st != 'ok':
        return '', st
    if len(d) < 32 or any(d[:12]):
        return '', 'baddata'
    return '0x' + d[12:32].hex(), ('ok' if len(d) == 32 else 'ok_extra_bytes')


def dec_uint(st, d):
    if st != 'ok':
        return '', st
    if len(d) < 32:
        return '', 'baddata'
    return str(int.from_bytes(d[:32], 'big')), ('ok' if len(d) == 32 else 'ok_extra_bytes')


def dec_bool(st, d):
    if st != 'ok':
        return '', st
    if len(d) < 32:
        return '', 'baddata'
    v = int.from_bytes(d[:32], 'big')
    if v not in (0, 1):
        return '', 'baddata'
    return ('true' if v else 'false'), ('ok' if len(d) == 32 else 'ok_extra_bytes')


def dec_words(st, d, k):
    """First k 32-byte words as base-10 strings (lossless for the words; ret length recorded separately)."""
    if st != 'ok' or len(d) < 32 * k:
        return [''] * k, (st if st != 'ok' else 'baddata')
    return [str(int.from_bytes(d[32 * i:32 * i + 32], 'big')) for i in range(k)], ('ok' if len(d) == 32 * k else 'ok_extra_bytes')


def _printable(s):
    return all((ord(c) >= 0x20 and ord(c) != 0x7f) for c in s)


def dec_text(st, d):
    """symbol()/name() decoding. Returns (text, encoding, raw_hex).
    encoding: 'string' (ABI string, valid UTF-8, printable) -> raw_hex ''
              'bytes32' (exactly 32 bytes, right-zero-padded printable UTF-8) -> raw_hex set
              'undecodable' -> text '', raw_hex set
    For non-ok statuses encoding is the status and raw_hex holds the revert data (if any)."""
    if st != 'ok':
        return '', st, ('0x' + d.hex() if d else '')
    raw = '0x' + d.hex()
    if len(d) >= 64:
        off = int.from_bytes(d[0:32], 'big')
        if off + 32 <= len(d):
            ln = int.from_bytes(d[off:off + 32], 'big')
            if off + 32 + ln <= len(d):
                try:
                    s = d[off + 32: off + 32 + ln].decode('utf-8')
                    if _printable(s):
                        return s, 'string', ''
                except UnicodeDecodeError:
                    pass
    if len(d) == 32:
        t = d.rstrip(b'\x00')
        try:
            s = t.decode('utf-8')
            if _printable(s):
                return s, 'bytes32', raw
        except UnicodeDecodeError:
            pass
    return '', 'undecodable', raw


# ---------------- resumable batch store ----------------

class BatchStore:
    """Append-only JSONL: one line per completed batch {"b": batch_id, "rows": [...]}. Resumable."""
    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.done = {}
        if os.path.exists(path):
            good = 0
            with open(path, 'rb') as f:
                raw = f.read()
            pos = 0
            for line in raw.split(b'\n'):
                if not line:
                    pos += 1
                    continue
                try:
                    j = json.loads(line)
                    self.done[j['b']] = j['rows']
                    pos += len(line) + 1
                    good = pos
                except Exception:
                    break
            if good < len(raw):
                with open(path, 'r+b') as f:
                    f.truncate(good)
        self.f = open(path, 'a')

    def add(self, b, rows):
        line = json.dumps({'b': b, 'rows': rows}, separators=(',', ':'))
        with self.lock:
            self.f.write(line + '\n')
            self.f.flush()
            os.fsync(self.f.fileno())
            self.done[b] = rows

    def close(self):
        self.f.close()


def append_gap(path, row):
    new = not os.path.exists(path)
    with open(path, 'a') as f:
        if new:
            f.write('collector,phase,what,detail,time_utc\n')
        f.write(','.join('"%s"' % str(x).replace('"', "'") for x in row) + ',' + utcnow() + '\n')


def write_sentinel(name, ok, text):
    d = '/home/user/dapparb/research-material/.sentinels'
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name + ('.DONE' if ok else '.FAILED'))
    with open(p, 'w') as f:
        f.write(utcnow() + ' ' + text + '\n')
    return p
