#!/usr/bin/env python3
"""Verbatim excerpts from the stored documentation texts (added 2026-10-01).

Reads <chain_dir>/collect/docs_excerpts_spec.json: a list of {"file": <docs/*.txt file name>, "start": <text>,
"end": <text>}. Each excerpt is the exact character span of docs/<file> from the first occurrence of `start` through
the end of the first occurrence of `end` after it. Writes <chain_dir>/docs/excerpts.jsonl, one JSON object per
excerpt: excerpt_id, source_url, final_url, http_status, fetched_at_utc (from docs/index.csv, written by
fetch_docs.py), text_file, char_start, char_end (Python character offsets into the UTF-8 decoded .txt file, end
exclusive), start_anchor_occurrences (how often `start` occurs in the file), text (the verbatim span).
The script re-reads every span from the file and stops with an error if an anchor is missing.
usage: python3 make_doc_excerpts.py <chain> <chain_dir>
"""
import csv, json, os, sys

chain, d = sys.argv[1], os.path.abspath(sys.argv[2])
spec = json.load(open(os.path.join(d, "collect", "docs_excerpts_spec.json")))
idx = {r["file_stem"]: r for r in csv.DictReader(open(os.path.join(d, "docs", "index.csv")))}
out = []
for i, x in enumerate(spec, 1):
    fn = x["file"]
    stem = fn[:-4] if fn.endswith(".txt") else fn
    meta = idx.get(stem)
    if meta is None:
        raise SystemExit("no index.csv row for %s" % fn)
    content = open(os.path.join(d, "docs", fn), encoding="utf-8").read()
    s = content.find(x["start"])
    if s < 0:
        raise SystemExit("start anchor not found in %s: %r" % (fn, x["start"][:80]))
    e = content.find(x["end"], s)
    if e < 0:
        raise SystemExit("end anchor not found in %s: %r" % (fn, x["end"][:80]))
    e += len(x["end"])
    text = content[s:e]
    assert content[s:e] == text and text.startswith(x["start"]) and text.endswith(x["end"])
    out.append({"excerpt_id": "%s-%02d" % (chain, i), "source_url": meta["url"], "final_url": meta["final_url"],
                "http_status": meta["http_status"], "fetched_at_utc": meta["fetched_at_utc"], "text_file": "docs/" + fn,
                "char_start": s, "char_end": e, "start_anchor_occurrences": content.count(x["start"]), "text": text})
with open(os.path.join(d, "docs", "excerpts.jsonl"), "w", encoding="utf-8") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote %s excerpts=%d" % (os.path.join(d, "docs", "excerpts.jsonl"), len(out)))
