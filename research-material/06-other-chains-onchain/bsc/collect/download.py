#!/usr/bin/env python3
"""Raw download for the BSC census window.

For every block in [start, end] (from ../census/window.json, or --start/--end):
  eth_getBlockByNumber(block, true)  -> full block incl. transaction objects
  eth_getBlockReceipts(block)        -> all receipts
Consistency checks per block: receipts count == tx count, receipt i txHash == tx i hash, receipt
blockHash == block hash (all receipts), receipt blockNumber == block. On failure the block is refetched
(possibly from another endpoint); after MAX_TRIES it is recorded in ../census/raw/gaps.csv.

Output: ../census/raw/chunk-<first>-<last>.jsonl.gz, one JSON line per block:
  {"block": <verbatim block object>, "receipts": [<verbatim receipts>], "src": {"block": url, "receipts": url}}
Chunks are written atomically (tmp + rename); a present chunk file is the checkpoint (resume = rerun).
"""
import argparse
import concurrent.futures as cf
import gzip
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpc import Pool, RpcError  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "census")
MAX_TRIES = 6

lock = threading.Lock()


def log(*a):
    with lock:
        print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), *a, flush=True)


def fetch_block(pool, n):
    last = None
    for t in range(MAX_TRIES):
        try:
            blk, ub = pool.call("eth_getBlockByNumber", [hex(n), True])
            rcs, ur = pool.call("eth_getBlockReceipts", [hex(n)])
        except RpcError as e:
            last = str(e)
            log("rpc-fail", n, last[:300])
            time.sleep(5 * (t + 1))
            continue
        txs = blk["transactions"]
        why = None
        if int(blk["number"], 16) != n:
            why = "block number mismatch"
        elif len(rcs) != len(txs):
            why = f"receipt count {len(rcs)} != tx count {len(txs)}"
        else:
            for i, (tx, rc) in enumerate(zip(txs, rcs)):
                if rc["transactionHash"] != tx["hash"]:
                    why = f"tx {i} hash mismatch"
                    break
                if rc["blockHash"] != blk["hash"]:
                    why = f"receipt {i} blockHash {rc['blockHash']} != block hash {blk['hash']} (reorg/inconsistent node)"
                    break
                if int(rc["blockNumber"], 16) != n:
                    why = f"receipt {i} blockNumber mismatch"
                    break
        if why is None:
            return {"block": blk, "receipts": rcs, "src": {"block": ub, "receipts": ur}}, None
        last = why
        log("inconsistent", n, why, ub, ur)
        time.sleep(2 * (t + 1))
    return None, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int)
    ap.add_argument("--end", type=int)
    ap.add_argument("--out", default=os.path.join(CENSUS, "raw"))
    ap.add_argument("--chunk", type=int, default=200)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    if a.start is None or a.end is None:
        w = json.load(open(os.path.join(CENSUS, "window.json")))
        a.start, a.end = w["start_block"], w["end_block"]
    os.makedirs(a.out, exist_ok=True)
    gaps_path = os.path.join(a.out, "gaps.csv")
    pool = Pool(log=log)
    log("range", a.start, a.end, "blocks", a.end - a.start + 1, "endpoints", list(pool.endpoints))
    t0 = time.time()
    done_blocks = 0
    chunk_starts = list(range(a.start, a.end + 1, a.chunk))
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        for cs in chunk_starts:
            ce = min(cs + a.chunk - 1, a.end)
            path = os.path.join(a.out, f"chunk-{cs}-{ce}.jsonl.gz")
            if os.path.exists(path):
                done_blocks += ce - cs + 1
                continue
            futs = {n: ex.submit(fetch_block, pool, n) for n in range(cs, ce + 1)}
            results, gaps = {}, []
            for n, f in futs.items():
                res, err = f.result()
                if res is None:
                    gaps.append((n, err))
                else:
                    results[n] = res
            with gzip.open(path + ".tmp", "wt", compresslevel=6) as g:
                for n in range(cs, ce + 1):
                    if n in results:
                        g.write(json.dumps(results[n], separators=(",", ":")) + "\n")
            if gaps:
                new = not os.path.exists(gaps_path)
                with open(gaps_path, "a") as gf:
                    if new:
                        gf.write("block_number,chunk_file,error\n")
                    for n, err in gaps:
                        gf.write(f"{n},{os.path.basename(path)},\"{str(err).replace(chr(34), chr(39))}\"\n")
                log("GAPS in chunk", cs, ce, [n for n, _ in gaps])
            os.replace(path + ".tmp", path)
            done_blocks += ce - cs + 1
            el = time.time() - t0
            log(f"chunk {cs}-{ce} written ({len(results)} blocks); progress {done_blocks}/{a.end - a.start + 1}; "
                f"elapsed {el:.0f}s; ep_stats={json.dumps({k.split('//')[1]: v for k, v in pool.stats.items()})}")
    # gap-fill pass: retry every block recorded in gaps.csv that is not present in any chunk file
    if os.path.exists(gaps_path):
        import csv
        have = set()
        for fn in sorted(os.listdir(a.out)):
            if fn.startswith("chunk-") and fn.endswith(".jsonl.gz"):
                with gzip.open(os.path.join(a.out, fn), "rt") as g:
                    for line in g:
                        have.add(int(json.loads(line)["block"]["number"], 16))
        want = sorted({int(r["block_number"]) for r in csv.DictReader(open(gaps_path))} - have)
        log("gap-fill: retrying", len(want), "blocks")
        filled, still = {}, []
        for n in want:
            res, err = fetch_block(pool, n)
            if res is None:
                still.append((n, err))
            else:
                filled[n] = res
        if filled:
            fp = os.path.join(a.out, f"chunk-gapfill-{int(time.time())}.jsonl.gz")
            with gzip.open(fp + ".tmp", "wt") as g:
                for n in sorted(filled):
                    g.write(json.dumps(filled[n], separators=(",", ":")) + "\n")
            os.replace(fp + ".tmp", fp)
        with open(os.path.join(a.out, "gaps-unrecovered.csv"), "w") as gf:
            gf.write("block_number,error\n")
            for n, err in still:
                gf.write(f"{n},\"{str(err).replace(chr(34), chr(39))}\"\n")
        log("gap-fill: filled", len(filled), "unrecovered", len(still))
    log("download complete")


if __name__ == "__main__":
    main()
