#!/usr/bin/env python3
"""Declared getReserves() return shape per DEX, from Blockscout-verified ABIs of one pool per factory (raw record).
Output ../getreserves-abi.csv. Observed return length per pool is in pools-part-*.csv.gz (reserves_ret_bytes)."""
import csv, json, os, sys, time, requests
OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
POOLS = [('Aerodrome', '0x723aef6543aece026a15662be4d3fb3424d502a9'), ('UniswapV2', '0x88a43bbdf9d098eec7bceda4e2494615dfd9bb9c'),
         ('SushiV2', '0x206a3356d7d4d2d2c9ebcd7cf489f1661a488ca1'), ('PancakeV2', '0x92363f9817f92a7ae0592a4cb29959a88d885cc8'),
         ('BaseSwap', '0xf4b96d5162adee867b6361e9f1848d701c4286c7')]
def get(url):
    for i in range(8):
        try:
            r = requests.get(url, headers={'User-Agent': UA}, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return {'_http': 404}
        except Exception as e:
            pass
        time.sleep(2 * (i + 1))
    return {'_http': 'failed'}
rows = []
for name, addr in POOLS:
    url = 'https://base.blockscout.com/api/v2/smart-contracts/' + addr
    j = get(url); src = addr; via = 'direct'
    abi = j.get('abi')
    if not abi:
        a = get('https://base.blockscout.com/api/v2/addresses/' + addr)
        impls = a.get('implementations') or []
        if impls:
            src = impls[0].get('address') or impls[0].get('address_hash'); via = 'implementation (proxy/clone) per /api/v2/addresses'
            j = get('https://base.blockscout.com/api/v2/smart-contracts/' + src); abi = j.get('abi')
    ent = [e for e in (abi or []) if e.get('type') == 'function' and e.get('name') == 'getReserves']
    outs = json.dumps(ent[0]['outputs']) if ent else ''
    rows.append([name, addr, src, via, j.get('name', ''), j.get('compiler_version', ''), outs, 'found' if ent else 'no verified ABI with getReserves', url])
    time.sleep(1)
with open(os.path.join(OUT, 'getreserves-abi.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['factory_name', 'example_pool', 'abi_source_address', 'abi_via', 'contract_name', 'compiler_version', 'getReserves_outputs_json', 'status', 'blockscout_url'])
    w.writerows(rows)
print(open(os.path.join(OUT, 'getreserves-abi.csv')).read())
