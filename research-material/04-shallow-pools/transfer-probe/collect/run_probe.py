#!/usr/bin/env python3
"""Transfer-behaviour probe (raw). For every token in ../work/holders.csv.gz with a holder pool, one eth_call per batch
at the pinned snapshot block with state overrides: the batcher address and every holder address get the runtime of
src/TransferProbe.sol. probeOne runs inside the holder, so the token sees msg.sender == holder pool (the token movement
of a buy out of that pool). Two passes, one per bps (100 = 1 %, 1 = 0.01 %), in separate eth_calls.
Resumable: finished batches are appended to work/probe-batches.jsonl and skipped on restart.
Usage: python3 run_probe.py [--smoke] [--batch 16] [--workers 3]
"""
import csv, gzip, json, os, sys, time, hashlib, threading, subprocess
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.abspath(os.path.join(HERE, '..'))
WORK = os.path.join(HERE, 'work')
BLOCK = 52008246
RPC = 'https://base-mainnet.public.blastapi.io'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
BATCHER = '0x000000000000000000000000000000000070b3e1'
CALL_GAS = 60_000_000
SEL_RUN = None
RUNTIME = open(os.path.join(HERE, 'probe-runtime.hex')).read().strip()

def k256(b): h = keccak.new(digest_bits=256); h.update(b); return h.digest()
RECIPIENT = '0x' + k256(b'dapparb transfer probe recipient').hex()[-40:]
SEL_RUN = '0x' + k256(b'run((address,address)[],address,uint256)').hex()[:8]

def w(x): return x.to_bytes(32, 'big')
def addr(a): return bytes(12) + bytes.fromhex(a[2:])

def encode_run(items, recipient, bps):
    head = w(0x60) + addr(recipient) + w(bps)
    arr = w(len(items)) + b''.join(addr(h) + addr(t) for h, t in items)
    return SEL_RUN + (head + arr).hex()

def rd(b, off): return int.from_bytes(b[off:off+32], 'big')

def decode_run(b):
    o_ok, o_data = rd(b, 0), rd(b, 32)
    n = rd(b, o_ok); oks = [rd(b, o_ok + 32 + 32*i) != 0 for i in range(n)]
    m = rd(b, o_data); base = o_data + 32; datas = []
    for i in range(m):
        eo = base + rd(b, base + 32*i); ln = rd(b, eo); datas.append(b[eo+32: eo+32+ln])
    return oks, datas

def decode_probe(d):
    v = [rd(d, 32*i) for i in range(9)]
    ro = v[5]; rl = rd(d, ro); ret = d[ro+32: ro+32+rl]
    return {'bal_ok': v[0] != 0, 'holder_before': v[1], 'amount': v[2], 'recipient_before': v[3], 'call_success': v[4] != 0,
            'ret': ret, 'gas_used': v[6], 'recipient_after': v[7], 'holder_after': v[8]}

def rpc(payload, tries=8):
    body = json.dumps(payload)
    for k in range(tries):
        r = subprocess.run(['curl', '-sS', '--max-time', '120', '-H', 'content-type: application/json', '-H', 'user-agent: ' + UA,
                            '--data-binary', '@-', RPC], input=body, capture_output=True, text=True)
        try:
            j = json.loads(r.stdout)
            if 'result' in j or ('error' in j and 'rate' not in str(j['error']).lower() and k >= 2):
                return j
        except Exception:
            pass
        time.sleep(min(30, 2 ** k))
    return {'error': {'message': 'no response after retries', 'last': r.stdout[:300]}}

def probe_batch(items, bps):
    holders = sorted({h for h, _ in items})
    overrides = {BATCHER: {'code': RUNTIME}}
    for h in holders: overrides[h] = {'code': RUNTIME}
    call = {'to': BATCHER, 'data': encode_run(items, RECIPIENT, bps), 'gas': hex(CALL_GAS)}
    j = rpc({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_call', 'params': [call, hex(BLOCK), overrides]})
    return j

def main():
    smoke = '--smoke' in sys.argv
    bsz = int(sys.argv[sys.argv.index('--batch') + 1]) if '--batch' in sys.argv else 16
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 3
    os.makedirs(WORK, exist_ok=True)
    rows = list(csv.DictReader(gzip.open(os.path.join(WORK, 'holders.csv.gz'), 'rt')))
    probe = [r for r in rows if r['holder']]
    if smoke:
        want = {'0x4200000000000000000000000000000000000006', '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913'}
        probe = [r for r in probe if r['token'] in want] + [r for r in probe if r['token'] not in want][:30]
    out = os.path.join(WORK, 'probe-batches-smoke.jsonl' if smoke else 'probe-batches.jsonl')
    done = set()
    if os.path.exists(out):
        for l in open(out):
            try: done.add(json.loads(l)['batch_id'])
            except Exception: pass
    jobs = []
    for bps in (100, 1):
        for i in range(0, len(probe), bsz):
            bid = f'bps{bps}-{i // bsz:05d}'
            if bid not in done: jobs.append((bid, bps, probe[i:i + bsz]))
    print(f'recipient {RECIPIENT} batcher {BATCHER} block {BLOCK} tokens_with_holder {len(probe)} jobs {len(jobs)} already_done {len(done)}', flush=True)
    lock = threading.Lock(); n = [0]
    def work(job):
        bid, bps, chunk = job
        items = [(r['holder'], r['token']) for r in chunk]
        j = probe_batch(items, bps)
        rec = {'batch_id': bid, 'bps': bps, 'items': items, 'utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        if 'result' in j: rec['result'] = j['result']
        else: rec['error'] = j.get('error')
        with lock:
            with open(out, 'a') as f: f.write(json.dumps(rec) + '\n')
            n[0] += 1
            if n[0] % 50 == 0 or smoke: print(time.strftime('%H:%M:%SZ', time.gmtime()), 'batches', n[0], '/', len(jobs), 'last', bid, 'error' if 'error' in rec else 'ok', flush=True)
    with ThreadPoolExecutor(workers) as ex: list(ex.map(work, jobs))
    print('done', n[0], flush=True)

if __name__ == '__main__':
    main()
