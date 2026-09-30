#!/usr/bin/env python3
"""One-off raw capture of the RSR episode, Base blocks 51998755..51998758 (raw data only).

Writes ../rsr-episode/:
  headers.jsonl.gz            eth_getBlockByNumber(n, false)  (one line per block, verbatim result)
  blocks_full.jsonl.gz        eth_getBlockByNumber(n, true)   (verbatim: header + full transaction objects)
  receipts.jsonl.gz           eth_getBlockReceipts(n)         (one line per receipt, verbatim)
  transactions_by_hash.jsonl.gz eth_getTransactionByHash(h)   (one line per tx, verbatim)
  pool_state.csv              eth_call at the end of blocks 51998754..51998758 on the two pools (raw return + derived decode)
  trace_winner.json           debug_traceTransaction(callTracer) of the winning tx, if an endpoint serves it
  errors.csv                  every call that could not be completed
Endpoints: base-mainnet.public.blastapi.io first for every call, base.drpc.org as fallback (sequential, 1 in-flight).
errors.csv also lists calls that failed on the first endpoint before a fallback succeeded.
"""
import csv, gzip, json, os, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'rsr-episode'))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
DRPC = 'https://base.drpc.org'
BLAST = 'https://base-mainnet.public.blastapi.io'
BLOCKS = list(range(51998755, 51998759))
STATE_BLOCKS = list(range(51998754, 51998759))
V3 = '0x11e26bbd1a5547895a50fc39a2d4c0025dec0bda'
AERO = '0xd204058452f57464e0e5ab8c3cc9cbcb6b41d4ee'
WIN_TX = '0x2310e683fe40902529cad07cde417d9062cc857c6052fb905101ce4b6d532e77'
S = requests.Session(); S.headers.update({'User-Agent': UA, 'Content-Type': 'application/json'})
errors = []


def rpc(url, method, params, tries=8):
    back = 1
    last = ''
    for _ in range(tries):
        try:
            r = S.post(url, data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}), timeout=90)
            if r.status_code != 200:
                last = 'http %d %s' % (r.status_code, r.text[:200]); raise RuntimeError(last)
            j = r.json()
            if j.get('error'):
                last = json.dumps(j['error'])[:300]
                if 'not supported' in last.lower() or 'method not found' in last.lower() or 'not available' in last.lower():
                    break
                raise RuntimeError(last)
            return j.get('result')
        except Exception as e:
            last = str(e)[:300]; time.sleep(back); back = min(back * 2, 30)
    errors.append([url, method, json.dumps(params)[:200], last])
    return None


def wjsonl(name, objs):
    with gzip.open(os.path.join(OUT, name), 'wt') as f:
        for o in objs:
            f.write(json.dumps(o, separators=(',', ':')) + '\n')


def main():
    os.makedirs(OUT, exist_ok=True)
    headers, fulls, rcpts, txs = [], [], [], []
    for n in BLOCKS:
        h = rpc(BLAST, 'eth_getBlockByNumber', [hex(n), False], tries=4) or rpc(DRPC, 'eth_getBlockByNumber', [hex(n), False]); headers.append(h)
        b = rpc(BLAST, 'eth_getBlockByNumber', [hex(n), True], tries=4) or rpc(DRPC, 'eth_getBlockByNumber', [hex(n), True]); fulls.append(b)
        rs = rpc(BLAST, 'eth_getBlockReceipts', [hex(n)], tries=4) or rpc(DRPC, 'eth_getBlockReceipts', [hex(n)]) or []
        rcpts.extend(rs)
        hashes = (h or {}).get('transactions', [])
        for tx in hashes:
            t = rpc(BLAST, 'eth_getTransactionByHash', [tx])
            if t is None:
                t = rpc(DRPC, 'eth_getTransactionByHash', [tx])
            txs.append(t if t is not None else {'hash': tx, '_error': 'not retrieved'})
        print(n, 'txs', len(hashes), 'receipts', len(rs), flush=True)
    wjsonl('headers.jsonl.gz', headers)
    wjsonl('blocks_full.jsonl.gz', fulls)
    wjsonl('receipts.jsonl.gz', rcpts)
    wjsonl('transactions_by_hash.jsonl.gz', txs)
    # pool state (end of block): raw eth_call results
    calls = [
        (V3, 'slot0()', '0x3850c7bd'), (V3, 'liquidity()', '0x1a686502'), (V3, 'fee()', '0xddca3f43'),
        (V3, 'token0()', '0x0dfe1681'), (V3, 'token1()', '0xd21220a7'), (V3, 'tickSpacing()', '0xd0c93a7c'),
        (AERO, 'getReserves()', '0x0902f1ac'), (AERO, 'token0()', '0x0dfe1681'), (AERO, 'token1()', '0xd21220a7'),
        (AERO, 'stable()', '0x22be3de1'), (AERO, 'factory()', '0xc45a0155'),
    ]
    rows = []
    for n in STATE_BLOCKS:
        for addr, sig, data in calls:
            res = rpc(BLAST, 'eth_call', [{'to': addr, 'data': data}, hex(n)])
            rows.append([n, addr, sig, data, res if res is not None else ''])
    # Aerodrome factory getFee(pool, stable)
    fac = next((r[4] for r in rows if r[1] == AERO and r[2] == 'factory()' and r[4]), None)
    stable = next((r[4] for r in rows if r[1] == AERO and r[2] == 'stable()' and r[4]), None)
    if fac and stable:
        facaddr = '0x' + fac[-40:]
        data = '0xcc56b2c5' + AERO[2:].rjust(64, '0') + stable[2:].rjust(64, '0')[-64:]
        for n in STATE_BLOCKS:
            res = rpc(BLAST, 'eth_call', [{'to': facaddr, 'data': data}, hex(n)])
            rows.append([n, facaddr, 'getFee(address,bool) [pool=%s]' % AERO, data, res if res is not None else ''])
    with open(os.path.join(OUT, 'pool_state.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['state_at_end_of_block', 'contract', 'call_signature', 'calldata', 'raw_return_hex', 'derived_decoded_words_base10'])
        for r in rows:
            raw = r[4]
            words = []
            if raw and raw.startswith('0x') and len(raw) > 2:
                hx = raw[2:]
                for i in range(0, len(hx), 64):
                    words.append(str(int(hx[i:i + 64], 16)))
            w.writerow(r + [' '.join(words)])
    # trace of the winning tx (optional)
    tr = None
    for url in (DRPC, BLAST):
        tr = rpc(url, 'debug_traceTransaction', [WIN_TX, {'tracer': 'callTracer', 'tracerConfig': {'withLog': True}}], tries=2)
        if tr is not None:
            with open(os.path.join(OUT, 'trace_winner.json'), 'w') as f:
                json.dump({'endpoint': url, 'method': 'debug_traceTransaction callTracer withLog', 'tx': WIN_TX, 'result': tr}, f)
            break
    with open(os.path.join(OUT, 'errors.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['endpoint', 'method', 'params', 'last_error']); w.writerows(errors)
    print('done; errors', len(errors), flush=True)


if __name__ == '__main__':
    sys.exit(main())
