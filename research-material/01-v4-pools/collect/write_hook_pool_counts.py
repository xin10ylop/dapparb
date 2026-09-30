#!/usr/bin/env python3
"""Write ../hook-pool-counts-all.csv.gz: Initialize-row count per hook address over the Initialize data available (final V4INIT parts
once initialize-parts.json exists). Runs hook_counts.py and stores its output also in state/hook-counts-final.json."""
import csv, gzip, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
raw = subprocess.check_output([sys.executable, os.path.join(HERE, "hook_counts.py")])
open(os.path.join(HERE, "state", "hook-counts-final.json"), "wb").write(raw)
j = json.loads(raw)
cov = ";".join("%d-%d" % tuple(x) for x in j["coverage_block_ranges"])
with gzip.open(os.path.join(OUT, "hook-pool-counts-all.csv.gz"), "wt", newline="") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["hook_address", "pool_count", "first_init_block", "last_init_block", "count_block_range"])
    for h, c, a, b in j["hooks"]:
        w.writerow([h, c, a, b, cov])
print(len(j["hooks"]), j["rows_scanned"])
