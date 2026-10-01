#!/usr/bin/env python3
"""Independent check of state/launch-tx-samples-selection.json (written by launch_tx_samples.py), by a different method:
no bitmap, no sort. Per hook, n = Initialize rows in the V4INIT parts (state/hook-counts-final.json, written by hook_counts.py)
+ V4RECENT 7-day rows with block > V4INIT end block (rows at or below it are the same events as in V4INIT; MANIFEST
"Consistency check"). The parts are in (block, log_index) order, so the picked rows are the 0th, (n//2)-th and (n-1)-th rows
of the hook in stream order. Prints mismatches and exits 1 if any. Usage: python3 verify_launch_tx_selection.py <hooks_file>"""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
hooks = [l.strip().lower() for l in open(sys.argv[1]) if l.strip()]
want = set(hooks)
ip = json.load(open(os.path.join(OUT, "initialize-parts.json")))
end = ip["block_to"]
hc = {h: c for h, c, a, b in json.load(open(os.path.join(HERE, "state", "hook-counts-final.json")))["hooks"]}
wr = os.path.join(HERE, "work", "v4recent")
rfiles = [os.path.join(wr, f) for f in sorted(os.listdir(wr)) if f.startswith("init_") and f.endswith(".csv.gz")]


def stream(only_after_end):
    for p, hdr in [(os.path.join(OUT, x["file"]), True) for x in ip["parts"]] if not only_after_end else [(p, False) for p in rfiles]:
        with gzip.open(p, "rt") as f:
            if hdr:
                next(f)
            for line in f:
                r = line.split(",", 10)
                if r[9] in want and (not only_after_end or int(r[0]) > end):
                    yield r


extra = {}
for r in stream(True):
    extra[r[9]] = extra.get(r[9], 0) + 1
n = {h: hc.get(h, 0) + extra.get(h, 0) for h in want}
targets = {h: {0, n[h] // 2, n[h] - 1} for h in want if n[h]}
c = {h: 0 for h in want}
got = {h: [] for h in want}
for src in (False, True):
    for r in stream(src):
        h = r[9]
        if c[h] in targets[h]:
            got[h].append([h, n[h], int(r[0]), int(r[3]), r[1], r[4]])
        c[h] += 1
exp = []
for h in hooks:
    exp += got[h]
sel = json.load(open(os.path.join(HERE, "state", "launch-tx-samples-selection.json")))["samples"]
bad = [(a, b) for a, b in zip(exp, sel) if a != b]
print("hooks", len(hooks), "expected samples", len(exp), "selection samples", len(sel), "mismatches", len(bad) + abs(len(exp) - len(sel)),
      "hooks_with_rows_after_v4init_end", len(extra), "rows_after_v4init_end", sum(extra.values()))
for a, b in bad[:10]:
    print("MISMATCH", a, b)
sys.exit(1 if bad or len(exp) != len(sel) else 0)
