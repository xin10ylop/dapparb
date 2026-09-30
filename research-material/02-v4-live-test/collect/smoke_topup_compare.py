#!/usr/bin/env python3
"""Smoke check for topup_initialize.py: compare its output for a block range already covered by V4INIT with the
V4INIT rows of the same range (row-for-row equality). Usage: smoke_topup_compare.py SMOKE_FILE FROM TO"""
import csv, glob, gzip, sys
smoke, frm, to = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
a = list(csv.reader(gzip.open(smoke, "rt", newline="")))
hdr, a = a[0], a[1:]
b = []
for p in sorted(glob.glob("/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz"))[-1:]:
    with gzip.open(p, "rt", newline="") as f:
        r = csv.reader(f); h2 = next(r)
        b += [row for row in r if frm <= int(row[0]) <= to]
print("range", frm, to, "header_equal", hdr == h2, "smoke_rows", len(a), "v4init_rows", len(b), "identical", a == b)
