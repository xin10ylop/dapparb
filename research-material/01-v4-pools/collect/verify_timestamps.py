#!/usr/bin/env python3
"""Verify Base block timestamps follow ts = genesis_ts + 2*block_number on sample blocks spread over the V4INIT range.
Writes ../timestamps-check.csv (block_number, timestamp_rpc, timestamp_formula, equal)."""
import csv, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Endpoint, POOL_MANAGER_DEPLOY_BLOCK, BASE_GENESIS_TS, log
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
ep = Endpoint("mainnet.base.org", "https://mainnet.base.org", 2000, inflight=1)
g = ep.call_retry("eth_getBlockByNumber", ["0x0", False])
genesis = int(g["timestamp"], 16)
log("genesis block 0 timestamp", genesis, "hash", g["hash"])
assert genesis == BASE_GENESIS_TS
pin = json.load(open(os.path.join(HERE, "state", "v4init-pin.json")))
end = pin["end_block"]
samples = [0, 1, POOL_MANAGER_DEPLOY_BLOCK] + [POOL_MANAGER_DEPLOY_BLOCK + (end - POOL_MANAGER_DEPLOY_BLOCK) * i // 10 for i in range(1, 10)] + [end - 43200, end]
rows = []
for b in sorted(set(samples)):
    blk = ep.call_retry("eth_getBlockByNumber", [hex(b), False])
    ts = int(blk["timestamp"], 16)
    f = genesis + 2 * b
    rows.append([b, ts, f, "1" if ts == f else "0"])
    log(b, ts, f, ts == f)
with open(os.path.join(OUT, "timestamps-check.csv"), "w", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["block_number", "timestamp_rpc", "timestamp_formula", "equal"]); w.writerows(rows)
