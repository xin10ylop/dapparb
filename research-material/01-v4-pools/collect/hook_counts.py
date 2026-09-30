#!/usr/bin/env python3
"""Count pools per hook address in the Initialize data available NOW (partial while V4INIT runs).
Sources: V4INIT final parts if present, else V4INIT work chunks (work/v4init/c_<from>_<to>.csv.gz).
Output (stdout JSON): coverage (list of contiguous covered block ranges), counts per hook (all hooks), rows scanned."""
import csv, gzip, json, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
idx = os.path.join(OUT, "initialize-parts.json")
files = []
if os.path.exists(idx):
    j = json.load(open(idx)); files = [(os.path.join(OUT, p["file"]), True) for p in j["parts"]]; ranges = [(j["block_from"], j["block_to"])]
else:
    wd = os.path.join(HERE, "work", "v4init"); rs = []
    for f in os.listdir(wd):
        m = re.match(r"c_(\d+)_(\d+)\.csv\.gz$", f)
        if m: rs.append((int(m.group(1)), int(m.group(2)), os.path.join(wd, f)))
    rs.sort(); files = [(p, False) for _, _, p in rs]
    ranges = []
    for a, b, _ in rs:
        if ranges and ranges[-1][1] + 1 == a: ranges[-1] = (ranges[-1][0], b)
        else: ranges.append((a, b))
cnt = collections.Counter(); first = {}; last = {}; n = 0
for p, hdr in files:
    with gzip.open(p, "rt", newline="") as f:
        rd = csv.reader(f)
        if hdr: next(rd)
        for r in rd:
            h = r[9]; b = int(r[0]); cnt[h] += 1; n += 1
            if h not in first or b < first[h]: first[h] = b
            if h not in last or b > last[h]: last[h] = b
json.dump({"coverage_block_ranges": ranges, "rows_scanned": n, "hooks": [[h, c, first[h], last[h]] for h, c in cnt.most_common()]}, sys.stdout)
