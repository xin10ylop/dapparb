#!/usr/bin/env python3
"""Probe the public MEV RPC endpoint of every validator listed in bnb-chain/bsc-mev-info mainnet/validator-list.toml
with the BSC validator MEV JSON-RPC methods `mev_running` and `mev_params` (validator-side builder settings as
exposed by the bsc client), plus `eth_chainId` and `web3_clientVersion`. Responses are stored verbatim.
The TOML file contains a duplicate key, so sections are parsed line-by-line (Address / RPC / URL keys).
Output: ../validator-mev-rpc-probe.jsonl.gz  one line per (validator entry, method):
  {validator_entry, consensus_address_listed, rpc_url, method, http_status, response_text, error, probed_at_utc}
Sequential requests (1 in flight), 20 s timeout, 2 attempts.
"""
import gzip
import json
import os
import re
import time

import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "validator-mev-rpc-probe.jsonl.gz"))
SRC = "/home/user/bnb-chain/bsc-mev-info/mainnet/validator-list.toml"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def parse(path):
    ents, cur = [], None
    for ln in open(path):
        m = re.match(r"^\[([^\]]+)\]", ln.strip())
        if m:
            cur = {"name": m.group(1)}
            ents.append(cur)
            continue
        m = re.match(r'^\s*(Address|RPC|URL)\s*=\s*"([^"]*)"', ln)
        if m and cur is not None:
            cur.setdefault(m.group(1), m.group(2))
    return [e for e in ents if e["name"] != "example"]


def main():
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})
    n = 0
    with gzip.open(OUT + ".tmp", "wt") as f:
        for e in parse(SRC):
            url = e.get("RPC") or e.get("URL") or ""
            for m in ("eth_chainId", "web3_clientVersion", "mev_running", "mev_params"):
                rec = {"validator_entry": e["name"], "consensus_address_listed": e.get("Address", "").lower(),
                       "rpc_url": url, "method": m, "http_status": None, "response_text": None, "error": None}
                if not url.startswith("http"):
                    rec["error"] = "no http(s) RPC URL in list entry"
                else:
                    for attempt in range(2):
                        try:
                            r = s.post(url, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": []}),
                                       timeout=20)
                            rec["http_status"], rec["response_text"], rec["error"] = r.status_code, r.text[:20000], None
                            break
                        except Exception as ex:
                            rec["error"] = repr(ex)[:500]
                            time.sleep(2)
                rec["probed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                f.write(json.dumps(rec) + "\n")
                n += 1
    os.replace(OUT + ".tmp", OUT)
    print("records", n)


if __name__ == "__main__":
    main()
