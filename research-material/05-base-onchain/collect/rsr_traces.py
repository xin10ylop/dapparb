#!/usr/bin/env python3
"""One-off: debug_traceBlockByNumber (callTracer, withLog) for Base blocks 51998755..51998758 via base.drpc.org
(sequential, 1 in-flight). Resumable: blocks already in the output are skipped (appends a gzip member).
If a block trace times out, falls back to debug_traceTransaction for each tx of the block. Output ../rsr-episode/block_traces.jsonl.gz, one line per block:
{"block_number": n, "endpoint": url, "tracer": "callTracer withLog", "method": ..., "result": <verbatim result array>}
(lines written by the first run, blocks 51998757-51998758, have no "method" key: they are debug_traceBlockByNumber) ; failures -> ../rsr-episode/trace_errors.csv"""
import csv, gzip, json, os, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..', 'rsr-episode'))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
S = requests.Session(); S.headers.update({'User-Agent': UA, 'Content-Type': 'application/json'})
errs = []
BT = os.path.join(OUT, 'block_traces.jsonl.gz')
done = set()
if os.path.exists(BT):
    for line in gzip.open(BT, 'rt'):
        done.add(json.loads(line)['block_number'])
hashes = {}
for line in gzip.open(os.path.join(OUT, 'headers.jsonl.gz'), 'rt'):
    h = json.loads(line); hashes[int(h['number'], 16)] = h['transactions']

def call(method, params, tries=6):
    last = ''
    for i in range(tries):
        try:
            r = S.post('https://base.drpc.org', data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}), timeout=180)
            j = r.json()
            if j.get('error'): raise RuntimeError(json.dumps(j['error'])[:300])
            return j['result'], ''
        except Exception as e:
            last = str(e)[:300]; time.sleep(min(2 ** i, 30))
    return None, last

with gzip.open(BT, 'at') as f:
    for n in range(51998755, 51998759):
        if n in done:
            continue
        res, last = call('debug_traceBlockByNumber', [hex(n), {'tracer': 'callTracer', 'tracerConfig': {'withLog': True}}], tries=3)
        if res is None:
            # fallback: per-transaction traces, same tracer; result array in block order, each {"txHash", "result"}
            per = []
            ok = True
            for h in hashes[n]:
                r1, l1 = call('debug_traceTransaction', [h, {'tracer': 'callTracer', 'tracerConfig': {'withLog': True}}])
                if r1 is None:
                    errs.append([n, 'tx ' + h + ': ' + l1]); per.append({'txHash': h, 'error': l1}); ok = False
                else:
                    per.append({'txHash': h, 'result': r1})
            f.write(json.dumps({'block_number': n, 'endpoint': 'https://base.drpc.org', 'tracer': 'callTracer withLog', 'method': 'debug_traceTransaction per tx (debug_traceBlockByNumber timed out: ' + last[:120] + ')', 'result': per}, separators=(',', ':')) + '\n')
            print(n, 'per-tx traces', len(per), 'all_ok', ok, flush=True)
            continue
        f.write(json.dumps({'block_number': n, 'endpoint': 'https://base.drpc.org', 'tracer': 'callTracer withLog', 'method': 'debug_traceBlockByNumber', 'result': res}, separators=(',', ':')) + '\n')
        print(n, 'traces', len(res), flush=True)
with open(os.path.join(OUT, 'trace_errors.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['block_number', 'last_error']); w.writerows(errs)
