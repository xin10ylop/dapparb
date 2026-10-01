#!/usr/bin/env python3
"""Raw DefiLlama TVL material for the DEX protocols of one chain (bytes unchanged, gzip-compressed).

Steps
 1. https://api.llama.fi/protocols is fetched ONCE and saved as --protocols-file (gzip of the unchanged body)
    plus <protocols-file minus .json.gz>.meta.json (url, fetched_at_utc, http_status, bytes, sha256, content_type).
    If --protocols-file already exists it is reused and NOT refetched (the same snapshot serves every chain).
 2. Selection (deterministic, from the saved file only): entries whose "chains" list contains --chain and whose
    "category" equals --category (default "Dexs"), ordered by chainTvls[--chain] (descending; ties by slug) = column selection_order;
    the first --top entries are selected. Entries in the filter whose chainTvls has no --chain key are listed with
    rank "" and never selected. Numbers are copied as the literal JSON tokens (parse_float/parse_int=str).
    Written to --selection-csv (derived file).
 3. https://api.llama.fi/protocol/<slug> for each selected slug, streamed to <--out-dir>/<--prefix><slug>.json.gz
    (gzip of the unchanged body). Resumable: a file listed with http_status 200 in --index and present on disk is skipped.
    One request at a time, >= 2 s apart, retries with backoff on 429/5xx/network errors (Retry-After honoured, max 300 s).
 4. --index CSV (file, url, http_status, bytes, sha256, fetched_at_utc) is merged (existing rows kept) and written sorted
    by file name. sha256/bytes are of the uncompressed body.

Usage (BSC, from research-material/06-other-chains-onchain/bsc/collect). DefiLlama's /protocols names BSC "Binance"
(no chain is named "BSC" there; /v2/chains lists both "BSC" and "Binance" with chainId 56), so --chain Binance:
  python3 fetch_defillama_tvl.py --chain Binance --protocols-file ../dex/defillama-protocols.json.gz \
      --out-dir ../dex --prefix defillama-protocol-bsc-dex- --index ../dex/defillama-tvl-index.csv \
      --selection-csv ../dex/defillama-protocols-bsc-dex-selection.csv \
      --extra https://api.llama.fi/v2/chains defillama-v2-chains.json.gz
Usage (Base, from research-material/08-sources/collect; reuses the BSC folder's /protocols snapshot):
  python3 fetch_defillama_tvl.py --chain Base \
      --protocols-file ../../06-other-chains-onchain/bsc/dex/defillama-protocols.json.gz --no-fetch-protocols \
      --out-dir ../defillama --prefix protocols-base-dex- --index ../defillama/index.csv \
      --selection-csv ../defillama/protocols-base-dex-selection.csv
"""
import argparse, csv, datetime as dt, gzip, hashlib, json, os, sys, time
from decimal import Decimal
import requests

CA = '/root/.ccr/ca-bundle.crt'
if os.path.exists(CA):
    os.environ.setdefault('REQUESTS_CA_BUNDLE', CA)
    os.environ.setdefault('SSL_CERT_FILE', CA)
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
S = requests.Session()
S.headers.update({'User-Agent': UA, 'Accept': 'application/json'})
LAST = [0.0]
INDEX_COLS = ['file', 'url', 'http_status', 'bytes', 'sha256', 'fetched_at_utc']


def now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(msg):
    print(f'[{now()}] {msg}', flush=True)


def fetch_to_gz(url, path, min_gap=2.0, tries=8):
    """Stream url into gzip file `path` (body unchanged). Returns (status, bytes, sha256, content_type, fetched_at)."""
    delay = 5
    for attempt in range(tries):
        gap = time.time() - LAST[0]
        if gap < min_gap:
            time.sleep(min_gap - gap)
        try:
            r = S.get(url, timeout=300, stream=True)
        except Exception as e:
            LAST[0] = time.time()
            log(f'  network error {url}: {e!r}; retry in {delay}s')
            time.sleep(delay); delay = min(delay * 2, 300); continue
        if r.status_code == 429 or r.status_code >= 500:
            LAST[0] = time.time()
            ra = r.headers.get('retry-after')
            wait = min(int(ra), 300) if ra and ra.isdigit() else delay
            log(f'  HTTP {r.status_code} {url}; retry in {wait}s')
            r.close(); time.sleep(wait); delay = min(delay * 2, 300); continue
        h, n = hashlib.sha256(), 0
        tmp = path + '.part'
        try:
            with gzip.open(tmp, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    if chunk:
                        h.update(chunk); n += len(chunk); f.write(chunk)
        except Exception as e:
            LAST[0] = time.time()
            log(f'  transfer error {url}: {e!r}; retry in {delay}s')
            if os.path.exists(tmp):
                os.remove(tmp)
            time.sleep(delay); delay = min(delay * 2, 300); continue
        LAST[0] = time.time()
        os.replace(tmp, path)
        return r.status_code, n, h.hexdigest(), r.headers.get('content-type', ''), now()
    raise RuntimeError(f'giving up on {url}')


def read_index(p):
    rows = {}
    if os.path.exists(p):
        for r in csv.DictReader(open(p, newline='')):
            rows[r['file']] = r
    return rows


def write_index(p, rows):
    with open(p + '.tmp', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=INDEX_COLS)
        w.writeheader()
        for k in sorted(rows):
            w.writerow({c: rows[k].get(c, '') for c in INDEX_COLS})
    os.replace(p + '.tmp', p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chain', required=True, help='chain name exactly as in DefiLlama "chains" / "chainTvls" (e.g. BSC, Base)')
    ap.add_argument('--category', default='Dexs')
    ap.add_argument('--top', type=int, default=15)
    ap.add_argument('--protocols-file', required=True)
    ap.add_argument('--no-fetch-protocols', action='store_true', help='fail instead of fetching /protocols if the file is missing')
    ap.add_argument('--out-dir', required=True)
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--index', required=True)
    ap.add_argument('--selection-csv', required=True)
    ap.add_argument('--select-only', action='store_true', help='stop after writing the selection CSV')
    ap.add_argument('--extra', nargs=2, action='append', default=[], metavar=('URL', 'FILE'),
                    help='also save this URL (raw, gzip) as FILE in --out-dir and list it in --index (e.g. /v2/chains)')
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)

    # 1. /protocols snapshot (fetched once, reused afterwards)
    pf = a.protocols_file
    meta_p = pf[:-len('.json.gz')] + '.meta.json' if pf.endswith('.json.gz') else pf + '.meta.json'
    url_all = 'https://api.llama.fi/protocols'
    if not os.path.exists(pf):
        if a.no_fetch_protocols:
            sys.exit(f'{pf} missing and --no-fetch-protocols given')
        log(f'fetch {url_all}')
        st, n, sha, ctype, t = fetch_to_gz(url_all, pf)
        meta = {'url': url_all, 'fetched_at_utc': t, 'http_status': st, 'bytes': n, 'sha256': sha,
                'content_type': ctype, 'note': 'raw response body, gzip-compressed, not modified'}
        json.dump(meta, open(meta_p, 'w'), indent=1)
        log(f'  /protocols HTTP {st} {n} bytes sha256 {sha}')
        if st != 200:
            sys.exit('protocols fetch not 200')
    else:
        log(f'reuse {pf} (not refetched)')
    meta = json.load(open(meta_p))

    # 2. selection
    with gzip.open(pf, 'rt', encoding='utf-8') as f:
        allp = json.load(f, parse_float=str, parse_int=str)
    log(f'{len(allp)} entries in /protocols snapshot')
    cand = [p for p in allp if a.chain in (p.get('chains') or []) and p.get('category') == a.category]
    ranked = [p for p in cand if a.chain in (p.get('chainTvls') or {})]
    unranked = [p for p in cand if a.chain not in (p.get('chainTvls') or {})]
    ranked.sort(key=lambda p: (-Decimal(str(p['chainTvls'][a.chain])), p.get('slug') or ''))
    log(f'filter chains contains {a.chain!r} and category == {a.category!r}: {len(cand)} entries '
        f'({len(ranked)} with chainTvls[{a.chain!r}], {len(unranked)} without)')
    if not cand:
        names = sorted({c for p in allp for c in (p.get('chains') or []) if a.chain.lower()[:3] in c.lower()})
        sys.exit(f'no entries; chain names resembling {a.chain!r}: {names}')
    sel = ranked[:a.top]
    cols = ['selection_order', 'selected', 'slug', 'name', 'category', 'parentProtocol', f'chainTvls_{a.chain}', 'tvl',
            'chains', 'id', 'source_file', 'source_fetched_at_utc', 'protocol_file']
    with open(a.selection_csv + '.tmp', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, p in enumerate(ranked + unranked, 1):
            is_ranked = i <= len(ranked)
            is_sel = i <= len(sel)
            w.writerow([i if is_ranked else '', 1 if is_sel else 0, p.get('slug', ''), p.get('name', ''),
                        p.get('category', ''), p.get('parentProtocol', '') or '',
                        p.get('chainTvls', {}).get(a.chain, ''), p.get('tvl', '') if p.get('tvl') is not None else '',
                        ' '.join(p.get('chains') or []), p.get('id', ''),
                        os.path.basename(pf), meta.get('fetched_at_utc', ''),
                        f'{a.prefix}{p.get("slug")}.json.gz' if is_sel else ''])
    os.replace(a.selection_csv + '.tmp', a.selection_csv)
    log(f'selection written: {a.selection_csv} ({len(ranked) + len(unranked)} rows, {len(sel)} selected)')
    for i, p in enumerate(sel, 1):
        log(f'  {i:2d} {p["slug"]} chainTvls[{a.chain}]={p["chainTvls"][a.chain]}')
    del allp
    if a.select_only:
        return

    # 3. per-protocol responses (+ optional extra raw responses)
    rows = read_index(a.index)
    if os.path.dirname(os.path.abspath(pf)) == os.path.abspath(a.out_dir) and os.path.basename(pf) not in rows:
        rows[os.path.basename(pf)] = {'file': os.path.basename(pf), 'url': url_all, 'http_status': str(meta['http_status']),
                                      'bytes': str(meta['bytes']), 'sha256': meta['sha256'], 'fetched_at_utc': meta['fetched_at_utc']}
        write_index(a.index, rows)
    for url, fn in a.extra:
        out = os.path.join(a.out_dir, fn)
        if rows.get(fn, {}).get('http_status') == '200' and os.path.exists(out):
            log(f'skip {fn} (already saved)'); continue
        log(f'fetch {url}')
        st, n, sha, ctype, t = fetch_to_gz(url, out)
        rows[fn] = {'file': fn, 'url': url, 'http_status': str(st), 'bytes': str(n), 'sha256': sha, 'fetched_at_utc': t}
        write_index(a.index, rows)
        log(f'  {fn} HTTP {st} {n} bytes {ctype}')
    for p in sel:
        slug = p['slug']
        fn = f'{a.prefix}{slug}.json.gz'
        out = os.path.join(a.out_dir, fn)
        if rows.get(fn, {}).get('http_status') == '200' and os.path.exists(out):
            log(f'skip {fn} (already saved)'); continue
        url = f'https://api.llama.fi/protocol/{slug}'
        log(f'fetch {url}')
        st, n, sha, ctype, t = fetch_to_gz(url, out)
        rows[fn] = {'file': fn, 'url': url, 'http_status': str(st), 'bytes': str(n), 'sha256': sha, 'fetched_at_utc': t}
        write_index(a.index, rows)
        log(f'  {fn} HTTP {st} {n} bytes (gz {os.path.getsize(out)}) {ctype}')
    bad = [r for r in rows.values() if r['file'].startswith(a.prefix) and r['http_status'] != '200']
    log(f'done; {len(sel)} selected, {len(bad)} not 200: {[r["file"] for r in bad]}')


if __name__ == '__main__':
    main()
