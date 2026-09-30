#!/usr/bin/env python3
"""Deterministic post-processing of the raw BSC census download (census/raw/chunk-*.jsonl.gz).

Inputs : ../census/raw/chunk-*.jsonl.gz, ../census/window.json, ../census/swap-topics.csv
Outputs: ../census/blocks.csv.gz
         ../census/txs-NNN.csv.gz            every tx
         ../census/reverted-NNN.csv.gz       every status-0 tx
         ../census/candidates-NNN.jsonl.gz   txs meeting criterion A or B (definition below)
         ../census/topic0-inventory.csv.gz   (derived index of every log topic0 seen in the window)
         ../census/postprocess-summary.json  row counts, part files, missing blocks
         ../builder/builder-material-NNN.jsonl.gz
Criterion A: >= 2 logs whose topics[0] is in swap-topics.csv.
Criterion B: not A, and >= 3 ERC-20 Transfer logs (topics[0] == keccak('Transfer(address,address,uint256)')
             AND exactly 3 topics, i.e. ERC-721 style 4-topic Transfers excluded) emitted by >= 2 distinct contracts.
No filtering by value, profit, address or anything else.
Every output part is rotated before its compressed size reaches ROTATE_BYTES (80 MB).
"""
import csv
import gzip
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.abspath(os.path.join(HERE, "..", "census"))
BUILDER = os.path.abspath(os.path.join(HERE, "..", "builder"))
RAW = os.path.join(CENSUS, "raw")
ROTATE_BYTES = 80 * 1024 * 1024
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def h2i(x):
    return None if x is None else int(x, 16)


def s(x):
    """int -> base-10 string; None -> ''"""
    return "" if x is None else str(x)


class PartWriter:
    """Writes numbered gzip parts; rotates when compressed size >= ROTATE_BYTES."""

    def __init__(self, outdir, stem, ext, header=None):
        self.outdir, self.stem, self.ext, self.header = outdir, stem, ext, header
        self.n = 0
        self.rows_per_part = []
        self.files = []
        self._open()

    def _open(self):
        self.n += 1
        path = os.path.join(self.outdir, f"{self.stem}-{self.n:03d}.{self.ext}.gz")
        self.raw = open(path + ".tmp", "wb")
        self.gz = gzip.GzipFile(fileobj=self.raw, mode="wb", compresslevel=6)
        self.txt = io.TextIOWrapper(self.gz, encoding="utf-8", newline="")
        self.path = path
        self.rows = 0
        if self.header is not None:
            self.w = csv.writer(self.txt, lineterminator="\n")
            self.w.writerow(self.header)

    def _close(self):
        self.txt.flush()
        self.txt.close()
        self.raw.close()
        os.replace(self.path + ".tmp", self.path)
        self.files.append(os.path.basename(self.path))
        self.rows_per_part.append(self.rows)

    def write(self, row):
        if self.raw.tell() >= ROTATE_BYTES:
            self._close()
            self._open()
        if self.header is not None:
            self.w.writerow(row)
        else:
            self.txt.write(json.dumps(row, separators=(",", ":")) + "\n")
        self.rows += 1

    def close(self):
        self._close()
        return {"files": self.files, "rows_per_part": self.rows_per_part, "rows": sum(self.rows_per_part)}


def load_swap_topics():
    p = os.path.join(CENSUS, "swap-topics.csv")
    topics = {}
    with open(p) as f:
        for r in csv.DictReader(f):
            t = r["topic0"].strip().lower()
            assert re.fullmatch(r"0x[0-9a-f]{64}", t), t
            topics.setdefault(t, []).append(r["protocol"])
    return topics


def iter_blocks(start, end, missing):
    files = sorted(fn for fn in os.listdir(RAW) if fn.startswith("chunk-") and fn.endswith(".jsonl.gz"))
    main = [fn for fn in files if not fn.startswith("chunk-gapfill")]
    main.sort(key=lambda fn: int(fn.split("-")[1]))
    extra = {}
    for fn in files:
        if fn.startswith("chunk-gapfill"):
            with gzip.open(os.path.join(RAW, fn), "rt") as g:
                for line in g:
                    d = json.loads(line)
                    extra[int(d["block"]["number"], 16)] = d
    expected = start

    def fill_until(n):
        nonlocal expected
        while expected < n:
            if expected in extra:
                yield extra.pop(expected)
            else:
                missing.append(expected)
            expected += 1

    for fn in main:
        with gzip.open(os.path.join(RAW, fn), "rt") as g:
            for line in g:
                d = json.loads(line)
                n = int(d["block"]["number"], 16)
                if n < expected:
                    continue  # duplicate
                yield from fill_until(n)
                expected = n + 1
                yield d
    yield from fill_until(end + 1)


TX_KEEP = ("hash", "type", "from", "to", "nonce", "value", "gas", "gasPrice", "maxFeePerGas",
           "maxPriorityFeePerGas", "chainId", "accessList", "authorizationList", "blobVersionedHashes",
           "maxFeePerBlobGas", "v", "r", "s", "yParity", "transactionIndex")


def tx_lite(tx):
    """verbatim tx object without 'input'; plus derived input_selector / input_len_bytes"""
    o = {k: v for k, v in tx.items() if k not in ("input", "blockHash", "blockNumber")}
    inp = tx.get("input") or "0x"
    o["input_selector"] = inp[:10] if len(inp) >= 10 else inp
    o["input_len_bytes"] = (len(inp) - 2) // 2
    return o


def main():
    global CENSUS, BUILDER, RAW
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--census-dir", default=CENSUS, help="output dir (window.json and swap-topics.csv read from here)")
    ap.add_argument("--builder-dir", default=BUILDER)
    ap.add_argument("--raw-dir", default=RAW)
    ap.add_argument("--start", type=int)
    ap.add_argument("--end", type=int)
    a = ap.parse_args()
    CENSUS, BUILDER, RAW = a.census_dir, a.builder_dir, a.raw_dir
    w = json.load(open(os.path.join(CENSUS, "window.json")))
    start, end = w["start_block"], w["end_block"]
    if a.start is not None:
        start, end = a.start, a.end
    swap_topics = load_swap_topics()
    os.makedirs(BUILDER, exist_ok=True)
    t0 = time.time()
    blocks_w = gzip.open(os.path.join(CENSUS, "blocks.csv.gz.tmp"), "wt", newline="")
    bw = csv.writer(blocks_w, lineterminator="\n")
    bw.writerow(["block_number", "timestamp", "base_fee_per_gas", "gas_used", "gas_limit", "tx_count", "miner",
                 "extra_data", "milli_timestamp", "block_hash", "parent_hash", "mix_hash", "requests_hash",
                 "size", "difficulty", "nonce", "blob_gas_used", "excess_blob_gas", "parent_beacon_block_root",
                 "withdrawals_root", "state_root", "transactions_root", "receipts_root"])
    txs_w = PartWriter(CENSUS, "txs", "csv", ["block_number", "tx_index", "tx_hash", "from", "to", "status", "gas_used",
                                              "effective_gas_price", "type", "nonce", "value", "gas_price",
                                              "max_fee_per_gas", "max_priority_fee_per_gas", "gas_limit",
                                              "input_selector", "input_len_bytes", "logs_count",
                                              "contract_address", "cumulative_gas_used"])
    rev_w = PartWriter(CENSUS, "reverted", "csv", ["block_number", "tx_index", "tx_hash", "from", "to", "gas_used",
                                                   "effective_gas_price", "logs_count", "gas_price",
                                                   "max_priority_fee_per_gas", "gas_limit", "input_selector",
                                                   "input_len_bytes", "nonce", "type"])
    cand_w = PartWriter(CENSUS, "candidates", "jsonl")
    bld_w = PartWriter(BUILDER, "builder-material", "jsonl")
    inv = {}  # topic0 -> [log_count, tx_count, emitters set, example(block, tx, emitter)]
    missing = []
    nblocks = ntx = nrev = ncand_a = ncand_b = nlogs = 0
    first_block = last_block = None
    for d in iter_blocks(start, end, missing):
        b, rcs = d["block"], d["receipts"]
        n = int(b["number"], 16)
        first_block = n if first_block is None else first_block
        last_block = n
        txs = b["transactions"]
        nblocks += 1
        bw.writerow([n, h2i(b["timestamp"]), s(h2i(b.get("baseFeePerGas"))), h2i(b["gasUsed"]), h2i(b["gasLimit"]),
                     len(txs), b["miner"].lower(), b["extraData"].lower(), s(h2i(b.get("milliTimestamp"))),
                     b["hash"], b["parentHash"], b.get("mixHash", ""), b.get("requestsHash", ""),
                     s(h2i(b.get("size"))), s(h2i(b.get("difficulty"))), b.get("nonce", ""),
                     s(h2i(b.get("blobGasUsed"))), s(h2i(b.get("excessBlobGas"))),
                     b.get("parentBeaconBlockRoot", ""), b.get("withdrawalsRoot", ""), b.get("stateRoot", ""),
                     b.get("transactionsRoot", ""), b.get("receiptsRoot", "")])
        for i, (tx, rc) in enumerate(zip(txs, rcs)):
            ntx += 1
            idx = h2i(rc["transactionIndex"])
            status = h2i(rc.get("status"))
            logs = rc.get("logs") or []
            nlogs += len(logs)
            inp = tx.get("input") or "0x"
            sel = inp[:10] if len(inp) >= 10 else inp
            ilen = (len(inp) - 2) // 2
            frm = (rc.get("from") or tx.get("from") or "").lower()
            to = (rc.get("to") or tx.get("to") or "")
            to = to.lower() if to else ""
            gas_used = h2i(rc["gasUsed"])
            egp = h2i(rc.get("effectiveGasPrice"))
            txs_w.write([n, idx, rc["transactionHash"], frm, to, s(status), gas_used, s(egp), s(h2i(tx.get("type"))),
                         s(h2i(tx.get("nonce"))), s(h2i(tx.get("value"))), s(h2i(tx.get("gasPrice"))),
                         s(h2i(tx.get("maxFeePerGas"))), s(h2i(tx.get("maxPriorityFeePerGas"))),
                         s(h2i(tx.get("gas"))), sel, ilen, len(logs), (rc.get("contractAddress") or "").lower(),
                         h2i(rc["cumulativeGasUsed"])])
            if status == 0:
                nrev += 1
                rev_w.write([n, idx, rc["transactionHash"], frm, to, gas_used, s(egp), len(logs),
                             s(h2i(tx.get("gasPrice"))), s(h2i(tx.get("maxPriorityFeePerGas"))), s(h2i(tx.get("gas"))),
                             sel, ilen, s(h2i(tx.get("nonce"))), s(h2i(tx.get("type")))])
            # topic inventory + criteria
            nswap = 0
            transfer_emitters = set()
            ntransfer = 0
            seen_t0 = set()
            for lg in logs:
                tps = lg.get("topics") or []
                t0_ = tps[0].lower() if tps else "(no-topics)"
                e = inv.get(t0_)
                if e is None:
                    e = inv[t0_] = [0, 0, set(), (n, rc["transactionHash"], lg["address"].lower())]
                e[0] += 1
                e[2].add(lg["address"].lower())
                if t0_ not in seen_t0:
                    e[1] += 1
                    seen_t0.add(t0_)
                if t0_ in swap_topics:
                    nswap += 1
                if t0_ == TRANSFER and len(tps) == 3:
                    ntransfer += 1
                    transfer_emitters.add(lg["address"].lower())
            crit = None
            if nswap >= 2:
                crit = "A"
                ncand_a += 1
            elif ntransfer >= 3 and len(transfer_emitters) >= 2:
                crit = "B"
                ncand_b += 1
            if crit:
                other = {k: v for k, v in rc.items() if k not in ("logs",)}
                cand_w.write({
                    "block_number": n, "tx_index": idx, "tx_hash": rc["transactionHash"], "from": frm, "to": to,
                    "status": status, "gas_used": s(gas_used), "effective_gas_price": s(egp),
                    "criterion": crit,
                    "derived_swap_topic_log_count": nswap,
                    "derived_erc20_transfer_log_count": ntransfer,
                    "derived_erc20_transfer_distinct_emitters": len(transfer_emitters),
                    "receipt_other_fields": other,
                    "tx": tx_lite(tx),
                    "logs": logs,
                })
        # builder material
        def brief(tx, rc):
            o = tx_lite(tx)
            o["receipt_status"] = rc.get("status")
            o["receipt_gasUsed"] = rc.get("gasUsed")
            o["receipt_effectiveGasPrice"] = rc.get("effectiveGasPrice")
            o["receipt_logs_count"] = len(rc.get("logs") or [])
            return o
        pairs = list(zip(txs, rcs))
        bld_w.write({
            "block_number": n, "block_hash": b["hash"], "timestamp": h2i(b["timestamp"]),
            "milli_timestamp": s(h2i(b.get("milliTimestamp"))), "miner": b["miner"].lower(),
            "extra_data": b["extraData"].lower(), "mix_hash": b.get("mixHash"), "requests_hash": b.get("requestsHash"),
            "tx_count": len(txs), "gas_used": s(h2i(b["gasUsed"])),
            "first_txs": [dict(position=j, **brief(tx, rc)) for j, (tx, rc) in enumerate(pairs[:5])],
            "last_txs": [dict(position=len(pairs) - len(pairs[-5:]) + j, **brief(tx, rc))
                         for j, (tx, rc) in enumerate(pairs[-5:])],
        })
        if nblocks % 500 == 0:
            print(time.strftime("%H:%M:%S"), "processed", nblocks, "blocks", ntx, "txs", f"{time.time() - t0:.0f}s",
                  flush=True)
    blocks_w.close()
    os.replace(os.path.join(CENSUS, "blocks.csv.gz.tmp"), os.path.join(CENSUS, "blocks.csv.gz"))
    res = {"txs": txs_w.close(), "reverted": rev_w.close(), "candidates": cand_w.close(),
           "builder_material": bld_w.close()}
    with gzip.open(os.path.join(CENSUS, "topic0-inventory.csv.gz.tmp"), "wt", newline="") as f:
        cw = csv.writer(f, lineterminator="\n")
        cw.writerow(["topic0", "log_count", "tx_count", "distinct_emitters", "example_block", "example_tx_hash",
                     "example_emitter", "in_swap_topics_csv", "swap_topics_csv_protocols"])
        for t, (lc, tc, em, ex) in sorted(inv.items(), key=lambda kv: -kv[1][0]):
            cw.writerow([t, lc, tc, len(em), ex[0], ex[1], ex[2], int(t in swap_topics),
                         "|".join(swap_topics.get(t, []))])
    os.replace(os.path.join(CENSUS, "topic0-inventory.csv.gz.tmp"), os.path.join(CENSUS, "topic0-inventory.csv.gz"))
    summ = {
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "window": {"start_block": start, "end_block": end},
        "blocks_written": nblocks, "first_block": first_block, "last_block": last_block,
        "missing_blocks": missing, "tx_rows": ntx, "reverted_rows": nrev, "logs_seen": nlogs,
        "candidates_criterion_A": ncand_a, "candidates_criterion_B": ncand_b,
        "distinct_topic0": len(inv), "swap_topics_used": {k: v for k, v in swap_topics.items()},
        "files": res, "blocks_file": "blocks.csv.gz", "topic0_inventory_file": "topic0-inventory.csv.gz",
        "elapsed_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(CENSUS, "postprocess-summary.json"), "w") as f:
        json.dump(summ, f, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "swap_topics_used"}, indent=1))
    if missing:
        print("WARNING missing blocks:", len(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
