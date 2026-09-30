#!/usr/bin/env python3
"""Compute the KNOWN SWAP TOPICS for one chain from swap_signatures.csv with `cast keccak`.

Writes <chain_dir>/swap-topics.csv with verified_example_* columns EMPTY; census.py fills them at
finalization from the first log observed in the census window (on-chain verification).

usage: python3 make_swap_topics.py <chain> <chain_dir>
"""
import csv, os, subprocess, sys

CAST = os.environ.get("CAST", "/root/.foundry/bin/cast")
HERE = os.path.dirname(os.path.abspath(__file__))

COLUMNS = ["topic0", "signature", "protocol", "source_url", "verified_example_tx",
           "match_rule", "match_address", "verified_example_block", "verified_example_log_address",
           "verification_note", "topic0_tool"]


def keccak(sig):
    out = subprocess.run([CAST, "keccak", sig], capture_output=True, text=True, check=True).stdout.strip().lower()
    assert out.startswith("0x") and len(out) == 66, out
    return out


def main():
    chain, chain_dir = sys.argv[1], sys.argv[2]
    rows = list(csv.DictReader(open(os.path.join(HERE, "swap_signatures.csv"))))
    out = []
    for r in rows:
        chains = [c.strip() for c in r["chains"].split(";")]
        if "all" not in chains and chain not in chains:
            continue
        if r["match_rule"] == "topic0":
            t0 = keccak(r["signature"])
            tool = "cast keccak \"%s\"" % r["signature"]
            addr = ""
        elif r["match_rule"] == "log0_address":
            t0 = ""  # anonymous log: no topic0; matched by emitting address with zero topics
            tool = "n/a (anonymous log0)"
            addr = r["match_addresses"].lower()
        else:
            raise SystemExit("unknown match_rule %r" % r["match_rule"])
        out.append({"topic0": t0, "signature": r["signature"], "protocol": r["protocol"], "source_url": r["source_url"],
                    "verified_example_tx": "", "match_rule": r["match_rule"], "match_address": addr,
                    "verified_example_block": "", "verified_example_log_address": "",
                    "verification_note": "not yet verified (filled by census.py finalization)", "topic0_tool": tool})
    os.makedirs(chain_dir, exist_ok=True)
    p = os.path.join(chain_dir, "swap-topics.csv")
    with open(p, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out)
    print("wrote %s rows=%d" % (p, len(out)))


if __name__ == "__main__":
    main()
