"""Decode one Base census tx: per-address ERC-20 flows, V4 Swap deltas (pool side = -amount), and every non-Transfer log topic."""
import csv, gzip, json, sys, collections
R = '/home/user/dapparb/research-material/05-base-onchain'
idx = list(csv.DictReader(open(f'{R}/data/file_index.csv')))
T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
V4 = '0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f'
topics = {r['topic0']: r['signature'].split('(')[0] + ' ' + r['protocol'][:30] for r in csv.DictReader(open(f'{R}/swap-topics.csv'))}
def s256(h): x = int(h, 16); return x - (1 << 256) if x >> 255 else x
def find(h, blk):
    for f in idx:
        if 'candidates' in f['file'] and int(f['min_block']) <= blk <= int(f['max_block']):
            for l in gzip.open(f"{R}/{f['file']}", 'rt'):
                if h[:20] in l[:400]:
                    d = json.loads(l)
                    if d['tx_hash'] == h: return d
for a in sys.argv[1:]:
    h, blk = a.split(':'); d = find(h, int(blk))
    if not d: print('not found', h); continue
    print('==', h[:18], 'block', blk, 'from', d['from'], 'to', d['to'], 'gas', d['gas_used'], 'value', d.get('value'))
    net = collections.defaultdict(lambda: collections.defaultdict(int))
    for x in d['logs']:
        tp = x['topics']
        if tp and tp[0] == T and len(tp) == 3:
            f = '0x' + tp[1][-40:]; t = '0x' + tp[2][-40:]; v = int(x['data'], 16); tok = x['address'].lower()
            net[f][tok] -= v; net[t][tok] += v
        elif tp and tp[0] == V4:
            dd = x['data'][2:]; a0 = s256(dd[0:64]); a1 = s256(dd[64:128])
            print('    V4 Swap pool', tp[1][:18], 'pool-side d0', -a0, 'd1', -a1)
        elif tp:
            print('    log', x['address'][:12], tp[0][:10], topics.get(tp[0], ''))
    for addr, m in net.items():
        nz = {k[:12]: v for k, v in m.items() if v}
        if nz: print('   ', addr, '[from]' if addr == d['from'].lower() else '[to]' if addr == (d['to'] or '').lower() else '', nz)
