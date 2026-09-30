#!/usr/bin/env python3
"""Fill the AUTO-STATUS block of ../MANIFEST.md with per-file row counts, sizes and sha256, write ../file-index.csv,
and write .sentinels/V2OLD.DONE (or .FAILED) from the component sentinels. Descriptive metadata only."""
import csv, glob, gzip, hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..'))
SENT = '/home/user/dapparb/research-material/.sentinels'
COMP = ['V2OLD_SNAPSHOT', 'V2OLD_CENSUS', 'V2OLD_TOKENS']


def utcnow():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def info(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for blk in iter(lambda: f.read(1 << 20), b''):
            h.update(blk)
    rows = ''
    ok = 'ok'
    try:
        if p.endswith('.csv.gz'):
            with gzip.open(p, 'rt', newline='') as f:
                rows = sum(1 for _ in csv.reader(f)) - 1
        elif p.endswith('.csv'):
            with open(p, newline='') as f:
                rows = sum(1 for _ in csv.reader(f)) - 1
    except Exception as e:
        ok = 'READ ERROR ' + repr(e)[:100]
    return rows, os.path.getsize(p), h.hexdigest(), ok


def main():
    st = {}
    for c in COMP:
        st[c] = 'DONE' if os.path.exists(os.path.join(SENT, c + '.DONE')) else ('FAILED' if os.path.exists(os.path.join(SENT, c + '.FAILED')) else 'NOT FINISHED')
    files = sorted(x for x in glob.glob(os.path.join(OUT, '*')) if os.path.isfile(x) and not x.endswith('MANIFEST.md') and not x.endswith('file-index.csv'))
    rows = []
    for p in files:
        r, sz, sh, ok = info(p)
        rows.append((os.path.basename(p), r, sz, sh, ok))
    with open(os.path.join(OUT, 'file-index.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'data_rows_excluding_header', 'bytes', 'sha256', 'read_check'])
        for x in rows:
            w.writerow(x)
    too_big = [x[0] for x in rows if x[2] > 90 * 1024 * 1024]
    all_done = all(v == 'DONE' for v in st.values()) and not too_big and all(x[4] == 'ok' for x in rows)
    gaps = os.path.join(OUT, 'gaps.csv')
    ngaps = (sum(1 for _ in open(gaps)) - 1) if os.path.exists(gaps) else 0
    meta = {}
    for m in ('snapshot-meta.json', 'census-meta.json', 'tokens-meta.json'):
        p = os.path.join(OUT, m)
        if os.path.exists(p):
            meta[m] = json.load(open(p))
    lines = ['<!-- AUTO-STATUS-BEGIN -->', '',
             '**Status: %s** (filled by `collect/finalize.py` at %s).' % ('COMPLETE' if all_done else 'INCOMPLETE - see below', utcnow()), '',
             '| Component sentinel | State |', '|---|---|']
    lines += ['| `.sentinels/%s` | %s |' % (c, v) for c, v in st.items()]
    lines += ['', 'Rows in gaps.csv (unrecoverable batches/ranges): %d. Files over 90 MB: %s.' % (ngaps, too_big or 'none'), '',
              '| File | Data rows (excl. header) | Bytes | sha256 |', '|---|---:|---:|---|']
    lines += ['| `%s` | %s | %d | `%s` |' % (x[0], x[1], x[2], x[3][:16] + '…') for x in rows]
    sm = meta.get('snapshot-meta.json', {}); cm = meta.get('census-meta.json', {}); tm = meta.get('tokens-meta.json', {})
    lines += ['', 'Snapshot rows by factory/sample group: `%s`' % json.dumps(sm.get('rows_by_factory_group', {})),
              '', 'Census: window %s-%s, log rows %s by event `%s`, activity rows %s, distinct emitters %s, missing chunks %s.' % (
                  cm.get('window_start_block'), cm.get('window_end_block'), cm.get('log_rows'), json.dumps(cm.get('log_rows_by_event', {})),
                  cm.get('activity_rows'), cm.get('distinct_emitters'), cm.get('chunks_missing')),
              '', 'Tokens: %s tokens with metadata; WETH-route set %s tokens, %s lookups, %s pool rows.' % (
                  tm.get('tokens'), tm.get('route_tokens'), tm.get('lookups'), tm.get('route_rows')),
              '', 'Full per-file list with complete sha256: `file-index.csv`.', '', '<!-- AUTO-STATUS-END -->']
    mp = os.path.join(OUT, 'MANIFEST.md')
    if os.path.exists(mp):
        s = open(mp).read()
        a = s.find('<!-- AUTO-STATUS-BEGIN -->'); b = s.find('<!-- AUTO-STATUS-END -->')
        if a >= 0 and b > a:
            s = s[:a] + '\n'.join(lines) + s[b + len('<!-- AUTO-STATUS-END -->'):]
            open(mp, 'w').write(s)
    os.makedirs(SENT, exist_ok=True)
    for sfx in ('.DONE', '.FAILED'):
        q = os.path.join(SENT, 'V2OLD' + sfx)
        if os.path.exists(q):
            os.remove(q)
    with open(os.path.join(SENT, 'V2OLD' + ('.DONE' if all_done else '.FAILED')), 'w') as f:
        f.write('%s components=%s gaps=%d too_big=%s\n' % (utcnow(), json.dumps(st), ngaps, too_big))
    print('finalize', 'DONE' if all_done else 'FAILED', st, ngaps)


if __name__ == '__main__':
    main()
