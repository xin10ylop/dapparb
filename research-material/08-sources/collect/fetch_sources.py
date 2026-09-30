#!/usr/bin/env python3
"""Fetch every source listed in sources.json, save raw bytes (gzip) and extracted text, write sources.csv.

Usage (from this directory):
    python3 fetch_sources.py                 # fetch all entries not fetched yet (resumable)
    python3 fetch_sources.py --only SLUG ... # (re)fetch only these slugs
    python3 fetch_sources.py --force         # refetch everything
    python3 fetch_sources.py --rebuild-csv   # only rebuild ../sources.csv from fetch-state.json

Output (relative to ../):
    raw/<slug>.<part>.<ext>.gz   raw HTTP bodies, gzip-compressed, bytes unchanged
    texts/<slug>.txt.gz          main extracted text (arXiv: HTML full text if available, else PDF text)
    texts/<slug>.pdf.txt.gz      PDF text with '=== page N ===' markers (arXiv / pdf kinds)
    sources.csv                  one row per source
    collect/fetch-state.json     checkpoint: per-slug fetch metadata
    collect/fetch-log.jsonl      one line per HTTP request (url, status, bytes, sha256, time)

Kinds:
    arxiv      id -> abs page (metadata), html full text (arxiv.org/html/<id>v<latest>), pdf (arxiv.org/pdf/<id>v<latest>)
    html       url -> raw html; text = block-aware HTML->text of <main>/<article> if present else <body>
    discourse  forum topic id + base -> /raw/<id> (markdown of all posts, used as text) + /t/<id>.json
    pdf        url -> pdf; text = PyMuPDF page text with page markers
    text       url -> body saved as-is and used as text (markdown, source code, llms.txt)
    json       url -> raw json; text = the json pretty-printed? no: text = the raw body (unchanged)
"""
import argparse, csv, datetime as dt, gzip, hashlib, io, json, os, re, sys, time
import requests
from bs4 import BeautifulSoup, NavigableString, Comment

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
RAW = os.path.join(OUT, 'raw')
TXT = os.path.join(OUT, 'texts')
STATE = os.path.join(HERE, 'fetch-state.json')
FLOG = os.path.join(HERE, 'fetch-log.jsonl')
SOURCES = os.path.join(HERE, 'sources.json')
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/124.0 Safari/537.36')
CA = '/root/.ccr/ca-bundle.crt'
if os.path.exists(CA):
    os.environ.setdefault('REQUESTS_CA_BUNDLE', CA)
    os.environ.setdefault('SSL_CERT_FILE', CA)

S = requests.Session()
S.headers.update({'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
LAST_HOST_T = {}


def now():
    return dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(msg):
    print(f'[{now()}] {msg}', flush=True)


def get(url, min_gap=1.5, tries=6):
    """GET with per-host pacing (one request at a time), backoff on 429/5xx/network errors."""
    host = re.sub(r'^https?://([^/]+).*$', r'\1', url)
    delay = 5
    last_exc = None
    for attempt in range(tries):
        gap = time.time() - LAST_HOST_T.get(host, 0)
        if gap < min_gap:
            time.sleep(min_gap - gap)
        t0 = time.time()
        try:
            r = S.get(url, timeout=90, allow_redirects=True)
            LAST_HOST_T[host] = time.time()
        except Exception as e:  # network error
            LAST_HOST_T[host] = time.time()
            last_exc = e
            log(f'  network error {url}: {e!r}; retry in {delay}s')
            time.sleep(delay); delay = min(delay * 2, 120)
            continue
        rec = {'t': now(), 'url': url, 'final_url': r.url, 'status': r.status_code,
               'bytes': len(r.content), 'sha256': hashlib.sha256(r.content).hexdigest(),
               'content_type': r.headers.get('content-type', ''), 'ms': int((time.time() - t0) * 1000),
               'attempt': attempt}
        with open(FLOG, 'a') as f:
            f.write(json.dumps(rec) + '\n')
        if r.status_code == 429 or r.status_code >= 500:
            ra = r.headers.get('retry-after')
            wait = int(ra) if ra and ra.isdigit() else delay
            log(f'  HTTP {r.status_code} {url}; retry in {wait}s')
            time.sleep(wait); delay = min(delay * 2, 120)
            continue
        return r, rec
    raise RuntimeError(f'giving up on {url}: {last_exc!r}')


def save_raw(slug, part, ext, content):
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, f'{slug}.{part}.{ext}.gz')
    with gzip.open(p, 'wb') as f:
        f.write(content)
    return os.path.relpath(p, OUT)


def save_text(name, text):
    os.makedirs(TXT, exist_ok=True)
    p = os.path.join(TXT, name)
    with gzip.open(p, 'wt', encoding='utf-8') as f:
        f.write(text)
    return os.path.relpath(p, OUT)


BLOCK = {'p', 'div', 'section', 'article', 'main', 'header', 'footer', 'aside', 'nav', 'li', 'ul', 'ol',
         'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'br', 'hr', 'table', 'thead', 'tbody', 'tr', 'figure',
         'figcaption', 'blockquote', 'pre', 'dl', 'dt', 'dd', 'details', 'summary', 'caption', 'form'}


def html_to_text(html, prefer_main=True, with_links=True):
    soup = BeautifulSoup(html, 'html.parser')
    for t in soup(['script', 'style', 'noscript', 'svg', 'template', 'iframe', 'button']):
        t.decompose()
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    # MathML (arXiv LaTeXML): replace by its LaTeX alttext so formulas stay readable.
    for m in soup.find_all('math'):
        m.replace_with(NavigableString(m.get('alttext', m.get_text(' ', strip=True))))
    # Tables: one line per row, cells joined by ' | '.
    for tr in soup.find_all('tr'):
        cells = [re.sub(r'\s+', ' ', c.get_text(' ', strip=True)) for c in tr.find_all(['td', 'th'])]
        tr.replace_with(NavigableString('\n' + ' | '.join(cells) + '\n'))
    for pre in soup.find_all('pre'):
        pre.replace_with(NavigableString('\n' + pre.get_text() + '\n'))
    root = None
    if prefer_main:
        for sel in ['main', 'article', '[role=main]']:
            cand = soup.select_one(sel)
            if cand is not None and len(cand.get_text(strip=True)) > 400:
                root = cand
                break
    if root is None:
        root = soup.body or soup
    links = []
    for a in root.find_all('a', href=True):
        h = a['href'].strip()
        if h.startswith('#') or h.startswith('javascript:'):
            continue
        links.append((re.sub(r'\s+', ' ', a.get_text(' ', strip=True))[:200], h))
    for tag in root.find_all(True):
        if tag.name in BLOCK:
            tag.insert_before(NavigableString('\n'))
            tag.insert_after(NavigableString('\n'))
        elif tag.name in ('td', 'th'):
            tag.insert_after(NavigableString(' '))
    text = root.get_text('')
    lines = []
    for ln in text.split('\n'):
        ln = re.sub(r'[ \t ​]+', ' ', ln).strip()
        lines.append(ln)
    out = '\n'.join(lines)
    out = re.sub(r'\n{3,}', '\n\n', out).strip() + '\n'
    if with_links and links:
        seen, lk = set(), []
        for t, h in links:
            if (t, h) not in seen:
                seen.add((t, h)); lk.append(f'{t}\t{h}')
        out += '\n=== hyperlinks in the extracted part of the page (anchor text<TAB>href; derived, appended by fetch_sources.py) ===\n' + '\n'.join(lk) + '\n'
    return out


def pdf_to_text(content):
    import fitz  # PyMuPDF
    doc = fitz.open(stream=content, filetype='pdf')
    parts = []
    for i, page in enumerate(doc, 1):
        parts.append(f'=== page {i} ===\n' + page.get_text('text'))
    return '\n'.join(parts), doc.page_count


def meta(html):
    soup = BeautifulSoup(html, 'html.parser')
    d = {}
    def m(names):
        for n in names:
            t = soup.find('meta', attrs={'name': n}) or soup.find('meta', attrs={'property': n})
            if t and t.get('content'):
                return t['content'].strip()
        return ''
    d['title'] = m(['citation_title', 'og:title', 'twitter:title']) or (soup.title.get_text(strip=True) if soup.title else '')
    authors = [t['content'].strip() for t in soup.find_all('meta', attrs={'name': 'citation_author'}) if t.get('content')]
    d['authors'] = '; '.join(authors) if authors else m(['author', 'article:author', 'twitter:creator'])
    d['date'] = m(['citation_date', 'citation_publication_date', 'article:published_time', 'date',
                   'publish-date', 'datePublished', 'og:published_time'])
    if not d['date']:
        for s in soup.find_all('script', attrs={'type': 'application/ld+json'}):
            mm = re.search(r'"datePublished"\s*:\s*"([^"]+)"', s.get_text() or '')
            if mm:
                d['date'] = mm.group(1)
                break
    return d


def fetch_arxiv(src):
    aid = src['id']
    files, texts, notes = [], [], []
    r, rec = get(f'https://arxiv.org/abs/{aid}', min_gap=3)
    if r.status_code != 200:
        raise RuntimeError(f'abs HTTP {r.status_code}')
    files.append(save_raw(src['slug'], 'abs', 'html', r.content))
    html = r.text
    md = meta(html)
    versions = re.findall(r'\[v(\d+)\]', html)
    latest = max(int(v) for v in versions) if versions else 1
    if src.get('version'):  # pin an earlier version explicitly (e.g. the version a figure was quoted from)
        latest = int(src['version'])
    hist = re.search(r'<div class="submission-history">(.*?)</div>', html, re.S)
    hist_txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', hist.group(1))).strip() if hist else ''
    abs_m = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.S)
    abstract = re.sub(r'\s+', ' ', BeautifulSoup(abs_m.group(1), 'html.parser').get_text(' ')).strip() if abs_m else ''
    abstract = re.sub(r'^Abstract:\s*', '', abstract)
    comments = ''
    cm = re.search(r'<td class="tablecell comments[^"]*">(.*?)</td>', html, re.S)
    if cm:
        comments = re.sub(r'\s+', ' ', BeautifulSoup(cm.group(1), 'html.parser').get_text(' ')).strip()
    header = (f'arXiv:{aid}v{latest}\nTitle: {md["title"]}\nAuthors: {md["authors"]}\n'
              f'Submission history: {hist_txt}\nComments: {comments}\n\nAbstract (from the abs page):\n{abstract}\n\n')
    main_text = None
    # HTML full text (LaTeXML), if arXiv produced one for the latest version.
    r2, rec2 = get(f'https://arxiv.org/html/{aid}v{latest}', min_gap=3)
    if r2.status_code == 200 and 'ltx_' in r2.text:
        files.append(save_raw(src['slug'], f'html-v{latest}', 'html', r2.content))
        main_text = header + '=== full text (arxiv.org/html, LaTeXML) ===\n' + html_to_text(r2.text, prefer_main=False)
        notes.append(f'html v{latest} ok')
    else:
        notes.append(f'html v{latest} HTTP {r2.status_code} (no LaTeXML HTML)')
    r3, rec3 = get(f'https://arxiv.org/pdf/{aid}v{latest}', min_gap=3)
    if r3.status_code == 200 and r3.content[:4] == b'%PDF':
        files.append(save_raw(src['slug'], f'pdf-v{latest}', 'pdf', r3.content))
        ptxt, npages = pdf_to_text(r3.content)
        texts.append(save_text(f'{src["slug"]}.pdf.txt.gz', header + ptxt))
        notes.append(f'pdf v{latest} {npages} pages')
        if main_text is None:
            main_text = header + ptxt
    else:
        notes.append(f'pdf HTTP {r3.status_code}')
    if main_text is None:
        raise RuntimeError('no full text')
    texts.insert(0, save_text(f'{src["slug"]}.txt.gz', main_text))
    return {
        'url': f'https://arxiv.org/abs/{aid}v{latest}', 'title': md['title'], 'authors': md['authors'],
        'date': f'v1 {md["date"]}; latest v{latest}; history: {hist_txt}' if md['date'] else hist_txt,
        'raw_files': files, 'text_files': texts, 'access_notes': '; '.join(notes),
    }


def fetch_html(src):
    r, rec = get(src['url'], min_gap=src.get('min_gap', 1.5))
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}')
    files = [save_raw(src['slug'], 'page', 'html', r.content)]
    md = meta(r.text)
    text = (f'Source URL: {src["url"]}\nFinal URL: {r.url}\nPage title: {md["title"]}\n\n'
            + html_to_text(r.text, prefer_main=src.get('prefer_main', True)))
    texts = [save_text(f'{src["slug"]}.txt.gz', text)]
    return {'url': src['url'], 'title': md['title'], 'authors': md['authors'], 'date': md['date'],
            'raw_files': files, 'text_files': texts,
            'access_notes': f'HTTP 200, {len(r.content)} bytes' + ('' if r.url == src['url'] else f', redirected to {r.url}')}


def fetch_discourse(src):
    base, tid = src['base'].rstrip('/'), src['topic_id']
    files, notes = [], []
    rj, _ = get(f'{base}/t/{tid}.json', min_gap=2)
    if rj.status_code != 200:
        raise RuntimeError(f'json HTTP {rj.status_code}')
    files.append(save_raw(src['slug'], 'topic', 'json', rj.content))
    d = rj.json()
    posts = d.get('post_stream', {}).get('posts', [])
    stream = d.get('post_stream', {}).get('stream', [])
    rr, _ = get(f'{base}/raw/{tid}', min_gap=2)
    if rr.status_code != 200:
        raise RuntimeError(f'raw HTTP {rr.status_code}')
    files.append(save_raw(src['slug'], 'raw', 'md', rr.content))
    # /raw/<id> pages at 100 posts; fetch further pages if the topic is longer.
    raw_text = rr.text
    npages = 1
    while d.get('posts_count', 0) > 100 * npages:
        npages += 1
        rp, _ = get(f'{base}/raw/{tid}?page={npages}', min_gap=2)
        if rp.status_code != 200:
            notes.append(f'raw page {npages} HTTP {rp.status_code}')
            break
        files.append(save_raw(src['slug'], f'raw-p{npages}', 'md', rp.content))
        raw_text += '\n' + rp.text
    op = posts[0] if posts else {}
    text = (f'Source URL: {src["url"]}\nTopic: {d.get("title")}\nTopic created_at: {d.get("created_at")}\n'
            f'posts_count: {d.get("posts_count")}\n\n=== all posts, Discourse /raw/{tid} (markdown; each post headed "username | time | #n") ===\n'
            + raw_text)
    texts = [save_text(f'{src["slug"]}.txt.gz', text)]
    notes.append(f'{d.get("posts_count")} posts; stream ids {len(stream)}')
    return {'url': src['url'], 'title': d.get('title', ''),
            'authors': src.get('authors', f'{op.get("name") or op.get("username")} (opening post)'),
            'date': src.get('date', f'topic created {d.get("created_at")}'),
            'raw_files': files, 'text_files': texts, 'access_notes': '; '.join(notes)}


def fetch_pdf(src):
    r, _ = get(src['url'], min_gap=2)
    if r.status_code != 200 or r.content[:4] != b'%PDF':
        raise RuntimeError(f'HTTP {r.status_code} ctype {r.headers.get("content-type")}')
    files = [save_raw(src['slug'], 'doc', 'pdf', r.content)]
    ptxt, n = pdf_to_text(r.content)
    texts = [save_text(f'{src["slug"]}.txt.gz', f'Source URL: {src["url"]}\n\n' + ptxt)]
    import fitz
    md = fitz.open(stream=r.content, filetype='pdf').metadata or {}
    return {'url': src['url'], 'title': md.get('title', ''), 'authors': md.get('author', ''),
            'date': md.get('creationDate', ''), 'raw_files': files, 'text_files': texts,
            'access_notes': f'PDF {n} pages; title/author/date from PDF metadata unless overridden'}


def fetch_text(src):
    r, _ = get(src['url'], min_gap=1.5)
    if r.status_code != 200:
        raise RuntimeError(f'HTTP {r.status_code}')
    ext = src.get('ext', 'txt')
    files = [save_raw(src['slug'], 'body', ext, r.content)]
    texts = [save_text(f'{src["slug"]}.txt.gz', r.content.decode('utf-8', errors='replace'))]
    return {'url': src['url'], 'title': '', 'authors': '', 'date': '', 'raw_files': files,
            'text_files': texts, 'access_notes': f'HTTP 200, {len(r.content)} bytes, saved unchanged'}


KINDS = {'arxiv': fetch_arxiv, 'html': fetch_html, 'discourse': fetch_discourse, 'pdf': fetch_pdf,
         'text': fetch_text, 'json': fetch_text}

CSV_COLS = ['slug', 'url', 'title', 'authors_or_org', 'publication_date_if_stated', 'fetched_at_utc',
            'access_notes', 'question_lines', 'kind', 'text_files', 'raw_files', 'status']


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE))
    return {}


def write_csv(sources, state):
    with open(os.path.join(OUT, 'sources.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(CSV_COLS)
        for src in sources:
            st = state.get(src['slug'])
            if not st:
                continue
            w.writerow([
                src['slug'], st.get('url', src.get('url', '')),
                src.get('title') or st.get('title', ''),
                src.get('authors_or_org') or st.get('authors', ''),
                src.get('publication_date') or st.get('date', ''),
                st.get('fetched_at', ''),
                '; '.join(x for x in [st.get('access_notes', ''), src.get('access_notes', '')] if x),
                ' '.join(src.get('question_lines', [])), src['kind'],
                ' '.join(st.get('text_files', [])), ' '.join(st.get('raw_files', [])), st.get('status', ''),
            ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--rebuild-csv', action='store_true')
    a = ap.parse_args()
    sources = json.load(open(SOURCES))
    slugs = [s['slug'] for s in sources]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        sys.exit(f'duplicate slugs: {dup}')
    state = load_state()
    if not a.rebuild_csv:
        for src in sources:
            slug = src['slug']
            if a.only and slug not in a.only:
                continue
            if not a.force and not a.only and state.get(slug, {}).get('status') == 'ok':
                continue
            log(f'fetch {slug} ({src["kind"]})')
            try:
                res = KINDS[src['kind']](src)
                res['status'] = 'ok'
            except Exception as e:
                log(f'  FAILED {slug}: {e!r}')
                res = {'status': f'failed: {e!r}', 'url': src.get('url', ''), 'access_notes': f'fetch failed: {e!r}'}
            res['fetched_at'] = now()
            state[slug] = res
            json.dump(state, open(STATE, 'w'), indent=1)
    write_csv(sources, state)
    bad = [s['slug'] for s in sources if state.get(s['slug'], {}).get('status') != 'ok']
    log(f'done; {len(sources)} sources, {len(bad)} not ok: {bad}')


if __name__ == '__main__':
    main()
