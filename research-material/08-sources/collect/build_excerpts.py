#!/usr/bin/env python3
"""Build ../excerpts.jsonl from excerpt-specs.jsonl by locating every passage verbatim in the saved texts.

Spec line fields:
  slug           source slug (see ../sources.csv)
  question_line  question-line key (see ../MANIFEST.md)
  location       section / page / table as stated in the source
  quote          the passage to locate            -- or --
  start, end     first and last words of a longer passage (the whole span start..end is extracted)
  file           optional: 'main' (texts/<slug>.txt.gz, default) or 'pdf' (texts/<slug>.pdf.txt.gz)
  occurrence     optional: 1-based occurrence of the match to use (default 1)

Matching is whitespace-insensitive (runs of whitespace in the spec and the text are treated as one space), but the
`quote` written to excerpts.jsonl is always the exact substring of the text file (original whitespace kept), with its
character offsets. A spec that cannot be located is written to excerpt-failures.jsonl and not to excerpts.jsonl.
"""
import gzip, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SPECS = os.path.join(HERE, 'excerpt-specs.jsonl')
_cache = {}


def load(slug, which):
    name = f'{slug}.txt.gz' if which == 'main' else f'{slug}.pdf.txt.gz'
    p = os.path.join(OUT, 'texts', name)
    if p not in _cache:
        with gzip.open(p, 'rt', encoding='utf-8') as f:
            raw = f.read()
        # normalized text + map from normalized index to raw index
        norm_chars, idx = [], []
        prev_space = False
        for i, ch in enumerate(raw):
            if ch.isspace():
                if prev_space:
                    continue
                norm_chars.append(' '); idx.append(i); prev_space = True
            else:
                norm_chars.append(ch); idx.append(i); prev_space = False
        _cache[p] = (raw, ''.join(norm_chars), idx, os.path.relpath(p, OUT))
    return _cache[p]


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def find(norm_text, needle, start=0, occurrence=1):
    pos = start - 1
    for _ in range(occurrence):
        pos = norm_text.find(needle, pos + 1)
        if pos < 0:
            return -1
    return pos


def main():
    out, fails, seen = [], [], set()
    with open(SPECS) as f:
        specs = [json.loads(l) for l in f if l.strip() and not l.startswith('//')]
    for n, sp in enumerate(specs, 1):
        which = sp.get('file', 'main')
        try:
            raw, nt, idx, rel = load(sp['slug'], which)
        except FileNotFoundError as e:
            fails.append({**sp, 'spec_line': n, 'error': f'text file missing: {e}'}); continue
        occ = int(sp.get('occurrence', 1))
        if 'quote' in sp:
            q = norm(sp['quote'])
            a = find(nt, q, 0, occ)
            if a < 0:
                fails.append({**sp, 'spec_line': n, 'error': 'quote not found'}); continue
            b = a + len(q) - 1
        else:
            s, e = norm(sp['start']), norm(sp['end'])
            a = find(nt, s, 0, occ)
            if a < 0:
                fails.append({**sp, 'spec_line': n, 'error': 'start not found'}); continue
            eb = nt.find(e, a + len(s) - len(e) if len(e) < len(s) else a)
            if eb < 0:
                fails.append({**sp, 'spec_line': n, 'error': 'end not found after start'}); continue
            b = eb + len(e) - 1
        ra, rb = idx[a], idx[b] + 1
        quote = raw[ra:rb]
        key = (sp['slug'], sp['question_line'], ra, rb)
        if key in seen:
            continue
        seen.add(key)
        out.append({'slug': sp['slug'], 'question_line': sp['question_line'], 'quote': quote,
                    'location': sp.get('location', ''), 'text_file': rel, 'char_start': ra, 'char_end': rb})
    with open(os.path.join(OUT, 'excerpts.jsonl'), 'w') as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')
    with open(os.path.join(HERE, 'excerpt-failures.jsonl'), 'w') as f:
        for o in fails:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')
    print(f'{len(specs)} specs -> {len(out)} excerpts, {len(fails)} failures')
    for fl in fails:
        print('  FAIL line', fl['spec_line'], fl['slug'], fl['error'], (fl.get('quote') or fl.get('start', ''))[:80])


if __name__ == '__main__':
    main()
