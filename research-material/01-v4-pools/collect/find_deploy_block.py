#!/usr/bin/env python3
"""Binary search the Uniswap V4 PoolManager deployment block on Base via eth_getCode (archive endpoint),
then cross-check the boundary on a second archive endpoint and fetch the creation tx from the block receipts."""
import json, sys, time, requests
PM = "0x498581ff718922c3f8e6a244956af099b2652b2b"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36", "content-type": "application/json"}
def rpc(url, method, params, tries=8):
    for i in range(tries):
        try:
            r = requests.post(url, json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, headers=UA, timeout=60)
            if r.status_code in (429,) or r.status_code >= 500:
                time.sleep(1.5 * (i + 1)); continue
            j = r.json()
            if "error" in j:
                if i < tries - 1: time.sleep(1.5 * (i + 1)); continue
                raise RuntimeError(str(j["error"]))
            return j["result"]
        except requests.RequestException:
            time.sleep(1.5 * (i + 1))
    raise RuntimeError("rpc failed %s %s" % (url, method))
def has_code(url, b):
    return rpc(url, "eth_getCode", [PM, hex(b)]) not in ("0x", "0x0", None)
A = "https://base.drpc.org"
B = "https://base-mainnet.public.blastapi.io"
lo, hi = 0, int(rpc(A, "eth_blockNumber", []), 16)
assert has_code(A, hi) and not has_code(A, lo)
while hi - lo > 1:
    mid = (lo + hi) // 2
    if has_code(A, mid): hi = mid
    else: lo = mid
print(json.dumps({"endpoint": A, "last_block_without_code": lo, "first_block_with_code": hi}))
chk = {}
for ep in (A, B):
    try:
        chk[ep] = {"code_at_%d" % lo: has_code(ep, lo), "code_at_%d" % hi: has_code(ep, hi)}
    except Exception as e:
        chk[ep] = {"error": str(e)}
print(json.dumps({"crosscheck": chk}))
rcpts = rpc(A, "eth_getBlockReceipts", [hex(hi)])
for r in rcpts:
    ca = (r.get("contractAddress") or "").lower()
    touched = ca == PM or any(l["address"].lower() == PM for l in r["logs"])
    if touched:
        print(json.dumps({"tx_hash": r["transactionHash"], "from": r["from"], "to": r["to"], "contractAddress": r.get("contractAddress"), "status": r["status"], "n_logs_from_pm": sum(1 for l in r["logs"] if l["address"].lower() == PM)}))
blk = rpc(A, "eth_getBlockByNumber", [hex(hi), False])
print(json.dumps({"block": hi, "timestamp": int(blk["timestamp"], 16)}))
