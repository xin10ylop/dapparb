#!/usr/bin/env python3
"""Rebuild the original Initialize rows (27 columns of initialize-part-*.csv.gz) from initialize-compact/.

Usage: python3 expand_initialize.py [--rpc URL] > initialize-full.csv
  pool_id and hf_*/dynamic_fee are rebuilt offline. tx_hash is left empty unless --rpc is given, in which case it is
  fetched with eth_getTransactionByBlockNumberAndIndex(block_number, tx_index) (slow for 15 M rows; meant for subsets).
Import iter_rows() to stream dicts without writing a file.
"""
import csv, glob, gzip, json, os, sys, urllib.request
from compact_initialize import pool_id

HERE = os.path.dirname(os.path.abspath(__file__)); C = os.path.join(HERE, '..', 'initialize-compact')
COLS = ['block_number','tx_hash','tx_index','log_index','pool_id','currency0','currency1','fee_raw','tick_spacing','hooks','sqrt_price_x96','tick','dynamic_fee']

def load_hooks():
    with open(os.path.join(C, 'hooks.csv')) as f:
        r = csv.DictReader(f); flags = [c for c in r.fieldnames if c.startswith('hf_')]
        return {row['hook_id']: row for row in r}, flags

def iter_rows(rpc=None):
    hooks, flags = load_hooks()
    for p in sorted(glob.glob(os.path.join(C, 'pools-part-*.csv.gz'))):
        with gzip.open(p, 'rt', newline='') as f:
            for d in csv.DictReader(f):
                h = hooks[d['hook_id']]
                out = {'block_number': d['block_number'], 'tx_hash': '', 'tx_index': d['tx_index'], 'log_index': d['log_index'],
                       'pool_id': pool_id(d['currency0'], d['currency1'], d['fee_raw'], d['tick_spacing'], h['hooks']),
                       'currency0': d['currency0'], 'currency1': d['currency1'], 'fee_raw': d['fee_raw'], 'tick_spacing': d['tick_spacing'],
                       'hooks': h['hooks'], 'sqrt_price_x96': d['sqrt_price_x96'], 'tick': d['tick'],
                       'dynamic_fee': '1' if int(d['fee_raw']) == 8388608 else '0'}
                for c in flags: out[c] = h[c]
                if rpc:
                    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getTransactionByBlockNumberAndIndex',
                                       'params': [hex(int(d['block_number'])), hex(int(d['tx_index']))]}).encode()
                    req = urllib.request.Request(rpc, data=body, headers={'content-type': 'application/json', 'user-agent': 'Mozilla/5.0'})
                    out['tx_hash'] = json.load(urllib.request.urlopen(req, timeout=30))['result']['hash']
                yield out

if __name__ == '__main__':
    rpc = sys.argv[sys.argv.index('--rpc') + 1] if '--rpc' in sys.argv else None
    hooks, flags = load_hooks()
    w = csv.DictWriter(sys.stdout, fieldnames=COLS + flags, lineterminator='\n'); w.writeheader()
    for row in iter_rows(rpc): w.writerow(row)
