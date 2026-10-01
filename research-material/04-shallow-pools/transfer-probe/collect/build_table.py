#!/usr/bin/env python3
"""work/probe-batches.jsonl + work/holders.csv.gz -> ../transfer-probe.csv.gz and ../probe-meta.json (raw values only)."""
import csv, gzip, json, os, hashlib, subprocess, collections, time
import run_probe as R

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..'))
holders = list(csv.DictReader(gzip.open(os.path.join(HERE, 'work', 'holders.csv.gz'), 'rt')))
by_token = {h['token']: h for h in holders}
res = {}  # (token, bps) -> dict
batches = 0; batch_errors = 0
for l in open(os.path.join(HERE, 'work', 'probe-batches.jsonl')):
    rec = json.loads(l); batches += 1
    if 'error' in rec:
        batch_errors += 1
        for h, t in rec['items']: res[(t, rec['bps'])] = {'status': 'rpc_error', 'batch_id': rec['batch_id'], 'rpc_error': json.dumps(rec['error'])[:300]}
        continue
    oks, datas = R.decode_run(bytes.fromhex(rec['result'][2:]))
    assert len(oks) == len(rec['items']) == len(datas), rec['batch_id']
    for (h, t), ok, d in zip(rec['items'], oks, datas):
        if not ok:
            res[(t, rec['bps'])] = {'status': 'probe_call_failed', 'batch_id': rec['batch_id'], 'outer_revert_hex': '0x' + d.hex()}
            continue
        p = R.decode_probe(d); p['status'] = 'ok'; p['batch_id'] = rec['batch_id']; res[(t, rec['bps'])] = p
cols = ['token', 'symbol', 'holder', 'holder_kind', 'holder_dex', 'holder_balance_snapshot', 'bps', 'status', 'balance_of_ok',
        'holder_balance_at_call', 'amount', 'call_success', 'returned_bool', 'return_or_revert_data_hex', 'gas_used',
        'recipient_before', 'recipient_after', 'received', 'holder_before', 'holder_after', 'holder_debited',
        'outer_revert_hex', 'rpc_error', 'pinned_block', 'endpoint', 'batch_id']
counts = collections.Counter(); n = 0
path = os.path.join(OUT, 'transfer-probe.csv.gz')
with gzip.open(path + '.tmp', 'wt', newline='') as f:
    w = csv.writer(f, lineterminator='\n'); w.writerow(cols)
    for h in holders:
        for bps in (100, 1):
            base = [h['token'], h['symbol'], h['holder'], h['holder_kind'], h['holder_dex'], h['holder_balance_snapshot'], bps]
            if not h['holder']:
                row = base + ['no_holder'] + [''] * 15 + [R.BLOCK, '', '']
            else:
                p = res.get((h['token'], bps))
                if p is None:
                    row = base + ['missing'] + [''] * 15 + [R.BLOCK, R.RPC, '']
                elif p['status'] != 'ok':
                    row = base + [p['status']] + [''] * 13 + [p.get('outer_revert_hex', ''), p.get('rpc_error', ''), R.BLOCK, R.RPC, p['batch_id']]
                else:
                    ret = p['ret']
                    rb = 'none'
                    if len(ret) == 32: rb = 'true' if int.from_bytes(ret, 'big') == 1 else ('false' if int.from_bytes(ret, 'big') == 0 else 'none')
                    row = base + ['ok', str(p['bal_ok']).lower(), p['holder_before'], p['amount'], str(p['call_success']).lower(), rb,
                                  '0x' + ret.hex(), p['gas_used'], p['recipient_before'], p['recipient_after'],
                                  p['recipient_after'] - p['recipient_before'], p['holder_before'], p['holder_after'],
                                  p['holder_before'] - p['holder_after'], '', '', R.BLOCK, R.RPC, p['batch_id']]
            assert len(row) == len(cols), (len(row), len(cols), row[:8])
            w.writerow(row); n += 1; counts[row[7]] += 1
os.replace(path + '.tmp', path)
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
fv = subprocess.run(['/root/.foundry/bin/forge', '--version'], capture_output=True, text=True).stdout.splitlines()[0]
meta = {'pinned_block': R.BLOCK, 'endpoint': R.RPC, 'recipient': R.RECIPIENT, 'batcher_address': R.BATCHER,
        'eth_call_gas': R.CALL_GAS, 'per_probe_transfer_gas_cap': 1500000, 'bps_values': [100, 1],
        'bps_passes_in_separate_eth_calls': True, 'batch_size_tokens': 16,
        'compiler': 'solc 0.8.28 via ' + fv + ', optimizer 200 runs, evm cancun',
        'probe_source': 'collect/src/TransferProbe.sol', 'probe_runtime_sha256': hashlib.sha256(bytes.fromhex(R.RUNTIME[2:])).hexdigest(),
        'holders_file': 'collect/work/holders.csv.gz', 'holders_file_sha256': sha(os.path.join(HERE, 'work', 'holders.csv.gz')),
        'raw_batches_file': 'collect/work/probe-batches.jsonl.gz', 'batches': batches, 'batches_with_rpc_error': batch_errors,
        'rows': n, 'rows_by_status': dict(counts), 'output_sha256': sha(path), 'built_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
json.dump(meta, open(os.path.join(OUT, 'probe-meta.json'), 'w'), indent=1)
print(json.dumps({k: meta[k] for k in ('rows', 'rows_by_status', 'batches', 'batches_with_rpc_error')}))
