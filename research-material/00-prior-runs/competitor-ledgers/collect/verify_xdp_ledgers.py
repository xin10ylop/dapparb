#!/usr/bin/env python3
"""Verify the outputs of xdp_ledgers.py (structure + completeness) and re-read a random sample of balances and
receipts from a second endpoint (gateway.tenderly.co/public/base). Logs counts and mismatches only; no analysis."""
import csv
import gzip
import json
import os
import random
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ALT = "https://gateway.tenderly.co/public/base"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SAMPLE = 40
for _v in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
    if not os.environ.get(_v) and os.path.exists("/root/.ccr/ca-bundle.crt"):
        os.environ[_v] = "/root/.ccr/ca-bundle.crt"


def log(*a):
    print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), *a, flush=True)


def rpc(method, params):
    for attempt in range(30):
        try:
            r = requests.post(ALT, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
                              headers={"User-Agent": UA}, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError(f"HTTP {r.status_code}")
            o = r.json()
            if "error" in o:
                raise RuntimeError(json.dumps(o["error"])[:200])
            return o["result"]
        except Exception as e:  # noqa: BLE001
            log("alt rpc retry", attempt, method, str(e)[:160])
            time.sleep(min(30, 1.5 ** attempt))
    raise RuntimeError("alt rpc failed")


def main():
    rnd = random.Random(20261001)
    arbers = json.load(gzip.open(os.path.join(D, "arbers_XDP.json.gz"), "rt"))
    problems = 0
    for sender, short in (("0x000000c557fa9a96d66cd6371abde62d879d0e61", "0x000000c5"),
                          ("0x3be22b314654c396a12c5e8d79abdd65aac3caaf", "0x3be22b31")):
        sel = sorted(arbers[sender], key=lambda r: r[0])[-60:]
        blocks = sorted({r[0] for r in sel})
        rows = list(csv.DictReader(gzip.open(os.path.join(D, f"ledger_{short}.raw.csv.gz"), "rt")))
        keys = {(int(r["block"]), r["block_tag"], r["address"], r["asset"]) for r in rows}
        addrs = sorted({r["address"] for r in rows})
        expected = len(blocks) * 2 * len(addrs) * 4
        bad_int = sum(1 for r in rows if not r["balance"].isdigit())
        bad_q = sum(1 for r in rows if int(r["queried_block"]) != int(r["block"]) - (1 if r["block_tag"] == "b-1" else 0))
        # rows that query the same (queried_block, address, asset) under different tx blocks must carry the same value
        seen, incons = {}, 0
        for r in rows:
            k = (r["queried_block"], r["address"], r["asset"])
            if k in seen and seen[k] != r["balance"]:
                incons += 1
            seen.setdefault(k, r["balance"])
        log(f"{short} ledger: rows {len(rows)} (expected {expected}), distinct keys {len(keys)}, "
            f"blocks {len(blocks)} file-blocks {len({int(r['block']) for r in rows})}, addresses {addrs}, "
            f"non-integer balances {bad_int}, queried_block mismatches {bad_q}, same-query inconsistencies {incons}")
        problems += (len(rows) != expected) + (len(keys) != expected) + bad_int + bad_q + incons
        rc = list(csv.DictReader(gzip.open(os.path.join(D, f"receipts_{short}.csv.gz"), "rt")))
        empty = {c: sum(1 for r in rc if r[c] == "") for c in rc[0]}
        empty = {c: n for c, n in empty.items() if n}
        hashes = {r["tx_hash"] for r in rc}
        log(f"{short} receipts: rows {len(rc)}, distinct hashes {len(hashes)}, "
            f"match input selection {hashes == {r[1].lower() for r in sel}}, empty cells per column {empty}")
        problems += (len(rc) != 60) + (hashes != {r[1].lower() for r in sel})
        # second-endpoint spot check
        mism = 0
        for r in rnd.sample(rows, SAMPLE // 2):
            qb = hex(int(r["queried_block"]))
            if r["asset"] == "ETH":
                v = int(rpc("eth_getBalance", [r["address"], qb]), 16)
            else:
                data = "0x70a08231" + r["address"][2:].rjust(64, "0")
                v = int(rpc("eth_call", [{"to": r["asset_address"], "data": data}, qb]), 16)
            if str(v) != r["balance"]:
                mism += 1
                log("balance mismatch", r, v)
        for r in rnd.sample(rc, 5):
            o = rpc("eth_getTransactionReceipt", [r["tx_hash"]])
            for f, c in (("gasUsed", "gas_used"), ("effectiveGasPrice", "effective_gas_price"), ("l1Fee", "l1_fee"),
                         ("status", "status"), ("blockNumber", "block_number")):
                if str(int(o[f], 16)) != r[c]:
                    mism += 1
                    log("receipt mismatch", r["tx_hash"], f, o[f], r[c])
        log(f"{short} second-endpoint check ({ALT}): {SAMPLE // 2} balances + 5 receipts, mismatches {mism}")
        problems += mism
    log(f"verification problems total {problems}")


if __name__ == "__main__":
    main()
