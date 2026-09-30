#!/usr/bin/env python3
"""Finalize the BASE_CENSUS output (integrity metadata only, no analysis).

- merges data/blocks-{bf,bf2,fw,gf}-*.csv.gz into ../blocks.csv.gz (sorted, one row per block); the per-stream
  blocks parts are moved to collect/state/blocks-parts/ afterwards
- checks: every block of [bf_start, final_block] present; parent_hash(n) == block_hash(n-1); number of txs rows per
  block == tx_count; writes the lists of exceptions to ../integrity.json
- ../gaps-final.csv: one row per block that ever failed (from ../gaps.csv) with final_status recovered|unrecoverable
- ../swap-topics.csv: fills verified_example_* from the first occurrence seen by the census (state/first_seen_*.json)
  when not already verified by verify_topics.py
- ../data/file_index.csv: file, bytes, rows (data rows, header excluded), min_block, max_block
- replaces the AUTO-STATUS block in ../MANIFEST.md
Safe to re-run.
"""
import csv, glob, gzip, json, os, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, 'state')
OUT = os.path.abspath(os.path.join(HERE, '..'))
DATA = os.path.join(OUT, 'data')
LIMIT = 90 * 1024 * 1024


def utcnow():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def lj(p, d=None):
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return d


def main():
    cfg = lj(os.path.join(STATE, 'config.json'))
    ck = {s: lj(os.path.join(STATE, '%s.ckpt.json' % s), {}) for s in ('bf', 'bf2', 'fw', 'gf')}
    first = cfg['bf_start']
    last = (ck['fw'].get('next') or cfg['fw_start']) - 1
    # 1. blocks
    rows = {}
    dups = 0
    header = None
    parts_dir = os.path.join(STATE, 'blocks-parts')
    srcs = sorted(glob.glob(os.path.join(DATA, 'blocks-*-*.csv.gz'))) + sorted(glob.glob(os.path.join(parts_dir, 'blocks-*-*.csv.gz')))
    for p in srcs:
        with gzip.open(p, 'rt') as f:
            r = csv.reader(f)
            for row in r:
                if row[0] == 'block_number':
                    header = row; continue
                n = int(row[0])
                if n in rows:
                    if rows[n] != row:
                        dups += 1
                    continue
                rows[n] = row
    if header is None:
        header = ['block_number', 'timestamp', 'base_fee_per_gas', 'gas_used', 'gas_limit', 'tx_count', 'miner', 'block_hash', 'parent_hash']
    tmp = os.path.join(OUT, 'blocks.csv.gz.tmp')
    with gzip.open(tmp, 'wt', newline='') as f:
        w = csv.writer(f, lineterminator='\n'); w.writerow(header)
        for n in sorted(rows):
            w.writerow(rows[n])
    os.replace(tmp, os.path.join(OUT, 'blocks.csv.gz'))
    os.makedirs(parts_dir, exist_ok=True)
    for p in glob.glob(os.path.join(DATA, 'blocks-*-*.csv.gz')):
        shutil.move(p, os.path.join(parts_dir, os.path.basename(p)))
    missing = [n for n in range(first, last + 1) if n not in rows]
    parent_mismatch = [n for n in range(first + 1, last + 1) if n in rows and n - 1 in rows and rows[n][8] != rows[n - 1][7]]
    # 2. txs per block
    txc = {}
    file_index = []
    for p in sorted(glob.glob(os.path.join(DATA, '*.gz'))):
        name = os.path.basename(p)
        nrows = 0; mn = None; mx = None
        with gzip.open(p, 'rt') as f:
            if name.endswith('.jsonl.gz'):
                for line in f:
                    if not line.strip():
                        continue
                    o = json.loads(line); b = o['block_number']; nrows += 1
                    mn = b if mn is None else min(mn, b); mx = b if mx is None else max(mx, b)
            else:
                r = csv.reader(f)
                for row in r:
                    if row[0] == 'block_number':
                        continue
                    b = int(row[0]); nrows += 1
                    mn = b if mn is None else min(mn, b); mx = b if mx is None else max(mx, b)
                    if name.startswith('txs-'):
                        txc[b] = txc.get(b, 0) + 1
        file_index.append([os.path.relpath(p, OUT), os.path.getsize(p), nrows, mn if mn is not None else '', mx if mx is not None else ''])
    bsz = os.path.getsize(os.path.join(OUT, 'blocks.csv.gz'))
    file_index.insert(0, ['blocks.csv.gz', bsz, len(rows), min(rows) if rows else '', max(rows) if rows else ''])
    txcount_mismatch = [n for n in sorted(rows) if int(rows[n][5]) != txc.get(n, 0)]
    oversize = [fi[0] for fi in file_index if fi[1] > LIMIT]
    with open(os.path.join(DATA, 'file_index.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['file', 'bytes', 'rows', 'min_block', 'max_block']); w.writerows(file_index)
    # 3. gaps-final
    gp = os.path.join(OUT, 'gaps.csv')
    gap_blocks = {}
    if os.path.exists(gp):
        with open(gp) as f:
            for r in csv.DictReader(f):
                gap_blocks.setdefault(int(r['block_number']), []).append(r['stream'] + ':' + r['reason'][:120])
    with open(os.path.join(OUT, 'gaps-final.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['block_number', 'final_status', 'failure_events'])
        for n in sorted(set(gap_blocks) | set(missing)):
            w.writerow([n, 'recovered' if n in rows else 'unrecoverable', ' | '.join(gap_blocks.get(n, ['missing (no failure event recorded)']))])
    # 4. swap topics examples
    fs = {}
    for s in ('bf', 'bf2', 'fw', 'gf'):
        for t, v in (lj(os.path.join(STATE, 'first_seen_%s.json' % s), {}) or {}).items():
            if t not in fs or v['block_number'] < fs[t]['block_number']:
                fs[t] = v
    stp = os.path.join(OUT, 'swap-topics.csv')
    if os.path.exists(stp):
        with open(stp) as f:
            st = list(csv.DictReader(f))
        cols = list(st[0].keys()) if st else []
        for c in ('census_first_seen_tx', 'census_first_seen_block', 'census_first_seen_emitter'):
            if c not in cols:
                cols.append(c)
        for r in st:
            v = fs.get(r['topic0'])
            r['census_first_seen_tx'] = v['tx_hash'] if v else ''
            r['census_first_seen_block'] = v['block_number'] if v else ''
            r['census_first_seen_emitter'] = v['emitter'] if v else ''
        with open(stp + '.tmp', 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(st)
        os.replace(stp + '.tmp', stp)
    ts = {n: int(rows[n][1]) for n in (min(rows), max(rows))} if rows else {}
    summ = {
        'finalized_utc': utcnow(), 'range_first_block': first, 'range_last_block': last,
        'range_first_block_timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts[min(rows)])) if rows else None,
        'range_last_block_timestamp_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts[max(rows)])) if rows else None,
        'blocks_present': len(rows), 'blocks_expected': last - first + 1, 'missing_blocks': len(missing),
        'parent_hash_mismatches': len(parent_mismatch), 'txcount_mismatches': len(txcount_mismatch), 'conflicting_duplicate_block_rows': dups,
        'oversize_files': oversize, 'fw_stop_reason': ck['fw'].get('stop_reason'), 'fw_stop_detected_utc': ck['fw'].get('stop_detected_utc'),
        'fw_stop_block': ck['fw'].get('stop_block'), 'gf_ran': bool(ck['gf']),
    }
    with open(os.path.join(OUT, 'integrity.json'), 'w') as f:
        json.dump({'summary': summ, 'missing_blocks': missing, 'parent_hash_mismatch_blocks': parent_mismatch,
                   'txcount_mismatch_blocks': txcount_mismatch}, f, indent=1)
    with open(os.path.join(STATE, 'finalize_summary.json'), 'w') as f:
        json.dump(summ, f, indent=1)
    # 5. manifest status block
    mp = os.path.join(OUT, 'MANIFEST.md')
    if os.path.exists(mp):
        s = open(mp).read()
        a, b = '<!-- AUTO-STATUS-BEGIN -->', '<!-- AUTO-STATUS-END -->'
        if a in s and b in s:
            lines = [a, '', '**Status: COMPLETE** (written by collect/finalize.py at %s)' % summ['finalized_utc'], '',
                     '```json', json.dumps(summ, indent=1), '```', '', '| file | bytes | rows | min_block | max_block |', '|---|---|---|---|---|']
            lines += ['| %s | %s | %s | %s | %s |' % tuple(fi) for fi in file_index]
            lines += ['', b]
            s = s[:s.index(a)] + '\n'.join(lines) + s[s.index(b) + len(b):]
            open(mp, 'w').write(s)
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
