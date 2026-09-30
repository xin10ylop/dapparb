#!/usr/bin/env python3
"""Zora on-chain hook registry (ZoraHookRegistry 0x777777c4c14b133858c3982d41dbf02509fc18d7 on Base, address from
https://docs.zora.co/coins/contracts/hook-registry). Fetches ALL logs of the registry via the Blockscout Etherscan-compatible API
(module=logs&action=getLogs, fromBlock=0, toBlock=latest), cross-checks each log's block with an RPC eth_getLogs over that block, and
decodes ZoraHookRegistered(address indexed hook, string tag, string version) / ZoraHookRemoved(...).
Outputs: ../hook-docs/zora-hook-registry-logs.jsonl.gz (raw logs, verbatim) and ../hook-docs/zora-hook-registry-events.csv
(block_number, tx_hash, log_index, event, hook, tag, version; decoded = derived)."""
import csv, gzip, json, os, sys, time, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import Endpoint, keccak_hex, log
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE); D = os.path.join(OUT, "hook-docs")
REG = "0x777777c4c14b133858c3982d41dbf02509fc18d7"
T_REG = keccak_hex(b"ZoraHookRegistered(address,string,string)"); T_REM = keccak_hex(b"ZoraHookRemoved(address,string,string)")
url = "https://base.blockscout.com/api?module=logs&action=getLogs&address=%s&fromBlock=0&toBlock=latest" % REG
for i in range(8):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    if r.status_code == 200: break
    time.sleep(2 ** i)
j = r.json(); logs = j["result"]; fetched = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
assert len(logs) < 1000, "Blockscout getLogs page cap reached; paginate"
with gzip.open(os.path.join(D, "zora-hook-registry-logs.jsonl.gz"), "wt") as f:
    for lg in logs: f.write(json.dumps({"source_url": url, "fetched_utc": fetched, "log": lg}) + "\n")
ep = Endpoint("mainnet.base.org", "https://mainnet.base.org", 2000, inflight=1)
blocks = sorted({int(lg["blockNumber"], 16) for lg in logs})
rpc_n = 0
for b in blocks:
    rl = ep.call_retry("eth_getLogs", [{"address": REG, "fromBlock": hex(b), "toBlock": hex(b)}]); rpc_n += len(rl)
log("blockscout logs", len(logs), "rpc logs at same blocks", rpc_n)
def dstr(data, off):
    b = bytes.fromhex(data[2:]); o = int.from_bytes(b[off:off+32], "big"); n = int.from_bytes(b[o:o+32], "big"); return b[o+32:o+32+n].decode("utf-8", "replace")
rows = []
for lg in logs:
    t0 = lg["topics"][0].lower()
    if t0 in (T_REG, T_REM):
        rows.append([int(lg["blockNumber"], 16), lg["transactionHash"], int(lg["logIndex"], 16), "ZoraHookRegistered" if t0 == T_REG else "ZoraHookRemoved",
                     "0x" + lg["topics"][1][-40:].lower(), dstr(lg["data"], 0), dstr(lg["data"], 32)])
with open(os.path.join(D, "zora-hook-registry-events.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n"); w.writerow(["block_number", "tx_hash", "log_index", "event", "hook", "tag", "version"]); w.writerows(sorted(rows))
for r in sorted(rows): print(r)
print("topic ZoraHookRegistered", T_REG, "ZoraHookRemoved", T_REM, "blockscout_vs_rpc_count", len(logs), rpc_n)
