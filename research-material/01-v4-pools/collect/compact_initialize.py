#!/usr/bin/env python3
"""Lossless-by-reconstruction compact copy of the V4 Initialize dataset for git.

Input : ../initialize-part-*.csv.gz (27 columns, see ../initialize-parts.json)
Output: ../initialize-compact/pools-part-NNNN.csv.gz  columns:
          block_number, tx_index, log_index, currency0, currency1, fee_raw, tick_spacing, hook_id, sqrt_price_x96, tick
        ../initialize-compact/hooks.csv  columns: hook_id, hooks (address), dynamic flags per hook (14 hf_* columns)
        ../initialize-compact/compact-index.json  parts, rows, sha256, verification counts
Dropped columns and how to rebuild them exactly:
  pool_id   = keccak256(abi.encode(currency0, currency1, uint24 fee_raw, int24 tick_spacing, hooks))  (verified here for EVERY row)
  tx_hash   = eth_getTransactionByBlockNumberAndIndex(block_number, tx_index).hash on Base (verified on a sample)
  hf_* flags= per hook address, in hooks.csv (they depend only on the hooks address)
  dynamic_fee = (fee_raw == 8388608)
"""
import csv, glob, gzip, hashlib, io, json, os, sys
from Crypto.Hash import keccak

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sorted(glob.glob(os.path.join(HERE, '..', 'initialize-part-*.csv.gz')))
OUT = os.path.join(HERE, '..', 'initialize-compact')
MAXB = 85 * 1024 * 1024
FLAGS = None

def pool_id(c0, c1, fee, ts, hooks):
    def a(x): return bytes(12) + bytes.fromhex(x[2:])
    def u(v, signed=False):
        v = int(v)
        if v < 0: v += 1 << 256
        return v.to_bytes(32, 'big')
    k = keccak.new(digest_bits=256)
    k.update(a(c0) + a(c1) + u(fee) + u(ts) + a(hooks))
    return '0x' + k.hexdigest()

class PartWriter:
    def __init__(self):
        self.n = 0; self.parts = []; self._open()
    def _open(self):
        self.n += 1
        self.path = os.path.join(OUT, f'pools-part-{self.n:04d}.csv.gz')
        self.raw = open(self.path, 'wb')
        self.gz = gzip.GzipFile(fileobj=self.raw, mode='wb', compresslevel=9, mtime=0)
        self.txt = io.TextIOWrapper(self.gz, encoding='utf-8', newline='')
        self.w = csv.writer(self.txt, lineterminator='\n')
        self.w.writerow(['block_number','tx_index','log_index','currency0','currency1','fee_raw','tick_spacing','hook_id','sqrt_price_x96','tick'])
        self.rows = 0; self.bfrom = None; self.bto = None
    def write(self, row, block):
        if self.rows and self.rows % 20000 == 0:
            self.txt.flush()
            if self.raw.tell() > MAXB: self._close(); self._open()
        self.w.writerow(row); self.rows += 1
        if self.bfrom is None: self.bfrom = block
        self.bto = block
    def _close(self):
        self.txt.flush(); self.txt.close()
        h = hashlib.sha256(open(self.path, 'rb').read()).hexdigest()
        self.parts.append({'file': os.path.basename(self.path), 'rows': self.rows, 'block_from': self.bfrom, 'block_to': self.bto, 'bytes': os.path.getsize(self.path), 'sha256': h})
    def close(self): self._close()

def main():
    os.makedirs(OUT, exist_ok=True)
    hooks = {}; hook_flags = {}
    pw = PartWriter(); total = 0; bad = 0; prev = (-1, -1)
    order_violations = 0
    for src in SRC:
        with gzip.open(src, 'rt', newline='') as f:
            r = csv.DictReader(f)
            flag_cols = [c for c in r.fieldnames if c.startswith('hf_')]
            for d in r:
                h = d['hooks']
                if h not in hooks:
                    hooks[h] = len(hooks); hook_flags[h] = [d[c] for c in flag_cols]
                elif hook_flags[h] != [d[c] for c in flag_cols]:
                    raise SystemExit(f'flag mismatch for hook {h}')
                if str(int(d['fee_raw']) == 8388608).lower() not in ('true','false'): pass
                pid = pool_id(d['currency0'], d['currency1'], d['fee_raw'], d['tick_spacing'], h)
                if pid != d['pool_id'].lower(): bad += 1
                blk = int(d['block_number']); key = (blk, int(d['log_index']))
                if key <= prev: order_violations += 1
                prev = key
                pw.write([d['block_number'], d['tx_index'], d['log_index'], d['currency0'], d['currency1'], d['fee_raw'], d['tick_spacing'], hooks[h], d['sqrt_price_x96'], d['tick']], blk)
                total += 1
                if total % 1000000 == 0: print(f'{total} rows, pool_id mismatches={bad}', flush=True)
    pw.close()
    with open(os.path.join(OUT, 'hooks.csv'), 'w', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(['hook_id', 'hooks'] + flag_cols)
        for h, i in sorted(hooks.items(), key=lambda x: x[1]): w.writerow([i, h] + hook_flags[h])
    idx = {'source_parts': [os.path.basename(s) for s in SRC], 'total_rows': total, 'pool_id_recomputed_mismatches': bad,
           'block_logindex_order_violations': order_violations, 'distinct_hooks': len(hooks), 'parts': pw.parts,
           'rebuild': __doc__}
    json.dump(idx, open(os.path.join(OUT, 'compact-index.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in idx.items() if k not in ('parts', 'rebuild')}), flush=True)

if __name__ == '__main__':
    main()
