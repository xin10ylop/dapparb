#!/usr/bin/env python3
"""Snapshot of the Uniswap hook registry repository https://github.com/Uniswap/hooklist (hooks/base/*.json, Base = chain 8453).
Clones the repo (depth 1) into a scratch dir given as argv[1] (or re-uses an existing clone), records the commit hash, and writes every
hooks/base/<address>.json verbatim into ../hook-docs/uniswap-hooklist-base.jsonl.gz as
{"repo","commit","commit_time","path","raw_url","fetched_utc","content": <parsed JSON of the file>}."""
import glob, gzip, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
clone = sys.argv[1]
if not os.path.isdir(os.path.join(clone, ".git")):
    subprocess.check_call(["git", "clone", "--depth", "1", "https://github.com/Uniswap/hooklist.git", clone])
commit, ctime = subprocess.check_output(["git", "-C", clone, "log", "-1", "--format=%H %cI"]).decode().split()
fetched = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
n = 0
with gzip.open(os.path.join(OUT, "hook-docs", "uniswap-hooklist-base.jsonl.gz"), "wt") as f:
    for p in sorted(glob.glob(os.path.join(clone, "hooks", "base", "*.json"))):
        rel = os.path.relpath(p, clone)
        f.write(json.dumps({"repo": "https://github.com/Uniswap/hooklist", "commit": commit, "commit_time": ctime, "path": rel,
                            "raw_url": "https://raw.githubusercontent.com/Uniswap/hooklist/%s/%s" % (commit, rel), "fetched_utc": fetched,
                            "content": json.load(open(p))}) + "\n")
        n += 1
print("entries", n, "commit", commit, ctime)
