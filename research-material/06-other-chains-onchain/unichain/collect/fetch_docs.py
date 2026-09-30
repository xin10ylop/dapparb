#!/usr/bin/env python3
"""Fetch official documentation pages verbatim.
usage: python3 fetch_docs.py <out_docs_dir> <url> [<url> ...]
For each URL writes:
  <slug>.html.gz   raw response body (gzip), unmodified
  <slug>.txt       verbatim visible text of the page (HTML tags removed, scripts/styles dropped, entities decoded,
                   whitespace collapsed per line), preceded by a header with URL, final URL, HTTP status, UTC fetch time
PDF responses are stored as <slug>.pdf plus <slug>.txt from `pdftotext -layout` when available.
index.csv lists every URL attempted with status (including failures)."""
import csv, datetime, gzip, html, os, re, subprocess, sys, time, requests
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
idx_path = os.path.join(out, "index.csv")
rows = []
if os.path.exists(idx_path):
    rows = list(csv.DictReader(open(idx_path)))
def slug(u):
    s = re.sub(r"^https?://", "", u).strip("/")
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:150]
def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>", "\n", h)
    h = re.sub(r"(?i)</(p|div|h[1-6]|li|tr|section|article|pre|table|ul|ol|blockquote|dt|dd)>", "\n", h)
    h = re.sub(r"(?i)<(h[1-6])[^>]*>", "\n\n## ", h)
    h = re.sub(r"(?i)<li[^>]*>", "\n* ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = html.unescape(h)
    lines = [re.sub(r"[ \t ]+", " ", l).strip() for l in h.split("\n")]
    outl, blank = [], 0
    for l in lines:
        if not l:
            blank += 1
            if blank <= 1: outl.append("")
        else:
            blank = 0; outl.append(l)
    return "\n".join(outl).strip() + "\n"
for u in sys.argv[2:]:
    t = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    st, final, note = "", "", ""
    r = None
    for i in range(4):
        try:
            r = requests.get(u, headers=UA, timeout=60, allow_redirects=True)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(3 * (i + 1)); continue
            break
        except requests.RequestException as ex:
            note = str(ex)[:200]; time.sleep(3 * (i + 1))
    s = slug(u)
    if r is not None:
        st, final = r.status_code, r.url
        ctype = r.headers.get("content-type", "")
        if "pdf" in ctype or u.lower().endswith(".pdf"):
            p = os.path.join(out, s if s.endswith(".pdf") else s + ".pdf")
            open(p, "wb").write(r.content)
            try:
                txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True, timeout=120).stdout
            except Exception as ex:  # noqa
                txt = ""; note = "pdftotext unavailable: %s" % ex
        else:
            open(os.path.join(out, s + ".html.gz"), "wb").write(gzip.compress(r.content))
            txt = text_of(r.content.decode(r.encoding or "utf-8", errors="replace"))
        hdr = "SOURCE_URL: %s\nFINAL_URL: %s\nHTTP_STATUS: %s\nFETCHED_AT_UTC: %s\nEXTRACTION: verbatim visible text (tags stripped); raw body in the .html.gz/.pdf file next to this one\n\n" % (u, final, st, t)
        if txt:
            open(os.path.join(out, s + ".txt"), "w").write(hdr + txt)
    rows = [x for x in rows if x["url"] != u]
    rows.append({"url": u, "final_url": final, "http_status": st, "fetched_at_utc": t, "file_stem": s, "note": note})
    print(u, st, final)
with open(idx_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["url", "final_url", "http_status", "fetched_at_utc", "file_stem", "note"])
    w.writeheader(); w.writerows(rows)
