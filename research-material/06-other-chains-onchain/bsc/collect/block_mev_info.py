#!/usr/bin/env python3
"""For every block of the census window, call the BSC JSON-RPC method eth_getBlockMevInfo(blockNumber)
(bsc client; used by bnb-chain/bsc cmd/jsutils/getchainstatus.js GetMevStatus to attribute blocks to builders).
Output ../builder/block-mev-info.csv.gz:
  block_number, block_hash (from response), miner (from response), version, builder, census_block_hash,
  hash_matches_census (derived: 1 if response blockHash == census blocks.csv block_hash), raw_result_json, endpoint
A null/absent 'builder' field is written as an empty string (the result JSON is kept verbatim in raw_result_json).
Endpoints: bsc-dataseed*.bnbchain.org, defibit, ninicoin (publicnode answers 'Method not found').
Failures after retries are listed in ../builder/block-mev-info-gaps.csv.
"""
import concurrent.futures as cf
import csv
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpc import Pool, RpcError  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "census")
OUTD = os.path.join(HERE, "..", "builder")


def main():
    w = json.load(open(os.path.join(CENSUS, "window.json")))
    start, end = w["start_block"], w["end_block"]
    census_hash = {}
    with gzip.open(os.path.join(CENSUS, "blocks.csv.gz"), "rt") as f:
        for r in csv.DictReader(f):
            census_hash[int(r["block_number"])] = r["block_hash"]
    pool = Pool(fallback={})

    def one(n):
        try:
            res, ep = pool.call("eth_getBlockMevInfo", [hex(n)], max_attempts=30)
            return n, res, ep, None
        except RpcError as e:
            return n, None, None, str(e)

    results, gaps = {}, []
    with cf.ThreadPoolExecutor(max_workers=16) as ex:
        for n, res, ep, err in ex.map(one, range(start, end + 1)):
            if res is None:
                gaps.append((n, err))
            else:
                results[n] = (res, ep)
    os.makedirs(OUTD, exist_ok=True)
    out = os.path.join(OUTD, "block-mev-info.csv.gz")
    with gzip.open(out + ".tmp", "wt", newline="") as f:
        cw = csv.writer(f, lineterminator="\n")
        cw.writerow(["block_number", "block_hash", "miner", "version", "builder", "census_block_hash",
                     "hash_matches_census", "raw_result_json", "endpoint"])
        for n in range(start, end + 1):
            if n not in results:
                continue
            res, ep = results[n]
            bh = (res.get("blockHash") or "").lower()
            ch = census_hash.get(n, "")
            cw.writerow([n, bh, (res.get("miner") or "").lower(), res.get("version") or "",
                         (res.get("builder") or "").lower(), ch, int(bh == ch), json.dumps(res, separators=(",", ":")),
                         ep])
    os.replace(out + ".tmp", out)
    with open(os.path.join(OUTD, "block-mev-info-gaps.csv"), "w") as f:
        f.write("block_number,error\n")
        for n, err in gaps:
            f.write(f"{n},\"{str(err).replace(chr(34), chr(39))}\"\n")
    print("rows", len(results), "gaps", len(gaps), "ep_stats", json.dumps(pool.stats))


if __name__ == "__main__":
    main()
