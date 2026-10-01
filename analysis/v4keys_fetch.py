#!/usr/bin/env python3
"""Resolve Uniswap V4 pool keys for the pools seen in each chain's census, via PositionManager.poolKeys(bytes25) at latest.
Writes analysis/v4keys/<chain>.csv.gz (pool_id,currency0,currency1,hooks,block_number,fee_raw,tick_spacing,source)."""
import csv, gzip, glob, json, sys, time, urllib.request
R = '/home/user/dapparb/research-material/06-other-chains-onchain'
V4 = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
CH = {  # chain: (census dir, PoolManager, PositionManager, rpc)
 'ethereum': ('ethereum', '0x000000000004444c5dc75cb358380d2e3de08a90', '0xbd216513d74c8cf14cf4747e6aaa6420ff64ee9e', 'https://ethereum-rpc.publicnode.com'),
 'arbitrum': ('arbitrum', '0x360e68faccca8ca495c1b759fd9eee466db9fb32', '0xd88f38f930b7952f2db2432cb002e7abbf3dd869', 'https://arbitrum-one-rpc.publicnode.com'),
 'optimism': ('optimism', '0x9a13f98cb987694c9f086b1f5eb990eea8264ec3', '0x3c3ea4b57a46241e54610e5f022e5c45859a1017', 'https://optimism-rpc.publicnode.com'),
 'unichain': ('unichain', '0x1f98400000000000000000000000000000000004', '0x4529a01c7a0410167c5740c487a8de60232617bf', 'https://mainnet.unichain.org'),
 'polygon': ('polygon', '0x67366782805870060151383f4bbff9dab53e5cd6', '0x1ec2ebf4f37e7363fdfe3551602425af0b3ceef9', 'https://polygon-bor-rpc.publicnode.com'),
 'ink': ('ink', '0x360e68faccca8ca495c1b759fd9eee466db9fb32', '0x1b35d13a2e2528f192637f14b05f0dc0e7deb566', 'https://ink-rpc.publicnode.com'),
 'worldchain': ('worldchain', '0xb1860d529182ac3bc1f51fa2abd56662b7d13f33', '0xc585e0f504613b5fbf874f21af14c65260fb41fa', 'https://worldchain-mainnet.g.alchemy.com/public'),
 'soneium': ('soneium', '0x360e68faccca8ca495c1b759fd9eee466db9fb32', '0x1b35d13a2e2528f192637f14b05f0dc0e7deb566', 'https://soneium-rpc.publicnode.com'),
 'bsc': ('bsc/census', '0x28e2ea090877bf75740558f6bfb36a5ffee9e9df', '0x7a4a5c919ae2541aed11041a1aeee68f1287f95b', 'https://bsc-dataseed.bnbchain.org'),
}
def rpc(url, batch):
    req = urllib.request.Request(url, json.dumps(batch).encode(), {'content-type': 'application/json', 'user-agent': 'curl/8'})
    for i in range(7):
        try: return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except Exception as e: err = e; time.sleep(3 * 2 ** i)
    raise err
for chain in (sys.argv[1:] or CH):
    d, pm, posm, url = CH[chain]
    ids = {}
    for fn in sorted(glob.glob(f'{R}/{d}/candidates-*.jsonl.gz')):
        for l in gzip.open(fn, 'rt'):
            if V4[:20] not in l: continue
            x = json.loads(l)
            for g in x['logs']:
                if g['topics'] and g['topics'][0] == V4 and g['address'].lower() == pm: ids[g['topics'][1].lower()] = x['block_number']
    ids = sorted(ids); out = []; miss = 0
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        res = rpc(url, [{'jsonrpc': '2.0', 'id': j, 'method': 'eth_call', 'params': [{'to': posm, 'data': '0x86b6be7d' + p[2:52] + '0' * 14}, 'latest']} for j, p in enumerate(chunk)])
        res = res if isinstance(res, list) else [res]
        got = {r['id']: r for r in res if isinstance(r.get('id'), int) and 'result' in r}
        for j in range(len(chunk)):  # anything the batch did not answer is asked again on its own
            k = 0
            while j not in got and k < 6:
                r = rpc(url, {'jsonrpc': '2.0', 'id': j, 'method': 'eth_call', 'params': [{'to': posm, 'data': '0x86b6be7d' + chunk[j][2:52] + '0' * 14}, 'latest']})
                if 'result' in r: got[j] = r
                elif 'revert' in json.dumps(r.get('error', '')).lower(): got[j] = {'id': j, 'result': '0x'}
                else: time.sleep(2 ** k)
                k += 1
        for j, r in sorted(got.items()):
            p = chunk[j]; h = (r.get('result') or '0x')[2:]
            if len(h) < 320: miss += 1; continue
            w = [h[k:k + 64] for k in range(0, 320, 64)]
            c0, c1, hk = '0x' + w[0][-40:], '0x' + w[1][-40:], '0x' + w[4][-40:]
            fee = int(w[2], 16); ts = int(w[3], 16); ts = ts - (1 << 256) if ts >> 255 else ts
            if c0 == c1 == hk and int(c0, 16) == 0 and fee == 0: miss += 1; continue
            out.append([p, c0, c1, hk, 0, fee, ts, 'PositionManager.poolKeys@latest'])
        time.sleep(0.2)
    with gzip.open(f'/home/user/dapparb/analysis/v4keys/{chain}.csv.gz', 'wt', newline='') as f:
        w = csv.writer(f); w.writerow(['pool_id', 'currency0', 'currency1', 'hooks', 'block_number', 'fee_raw', 'tick_spacing', 'source']); w.writerows(out)
    print(chain, 'pools', len(ids), 'resolved', len(out), 'missing', miss, flush=True)
