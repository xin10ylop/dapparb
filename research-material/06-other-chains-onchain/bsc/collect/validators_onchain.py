#!/usr/bin/env python3
"""Snapshot of BSC validators from the system contracts, pinned to one block (head-5 at run time):
  StakeHub 0x...2002 getValidators(offset,limit) -> operator addresses + credit contracts
  StakeHub getValidatorConsensusAddress(operator), getValidatorDescription(operator) (moniker, identity, website, details)
  ValidatorSet 0x...1000 getValidators() (current consensus set) and getMiningValidators()
Output ../validators-onchain.csv. The consensus address is what appears as `miner` in block headers.
Uses foundry `cast call` against bsc-dataseed.bnbchain.org (fallback bsc-dataseed1.defibit.io); sequential calls.
"""
import csv
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "validators-onchain.csv"))
CAST = "/root/.foundry/bin/cast"
RPCS = ["https://bsc-dataseed.bnbchain.org", "https://bsc-dataseed1.defibit.io", "https://bsc-dataseed2.bnbchain.org"]
STAKEHUB = "0x0000000000000000000000000000000000002002"
VSET = "0x0000000000000000000000000000000000001000"


def cast(*args):
    last = None
    for attempt in range(8):
        rpc = RPCS[attempt % len(RPCS)]
        try:
            return subprocess.check_output([CAST, *args, "--rpc-url", rpc], text=True, stderr=subprocess.STDOUT,
                                           timeout=60).strip(), rpc
        except subprocess.CalledProcessError as e:
            last = e.output
        except subprocess.TimeoutExpired as e:
            last = repr(e)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"cast {' '.join(args)} failed: {last}")


def parse_addr_list(s):
    s = s.strip().strip("[]")
    return [x.strip().lower() for x in s.split(",") if x.strip()]


def main():
    head, rpc = cast("block-number")
    blk = str(int(head) - 5)
    out, _ = cast("call", "--block", blk, STAKEHUB, "getValidators(uint256,uint256)(address[],address[],uint256)", "0", "1000")
    lines = out.splitlines()
    ops, credits, total = parse_addr_list(lines[0]), parse_addr_list(lines[1]), lines[2].split()[0]
    cur, _ = cast("call", "--block", blk, VSET, "getValidators()(address[])")
    cur = set(parse_addr_list(cur))
    mining, _ = cast("call", "--block", blk, VSET, "getMiningValidators()(address[],bytes[])")
    mining = set(parse_addr_list(mining.splitlines()[0]))
    rows = []
    for op, cr in zip(ops, credits):
        cons, _ = cast("call", "--block", blk, STAKEHUB, "getValidatorConsensusAddress(address)(address)", op)
        desc, _ = cast("call", "--json", "--block", blk, STAKEHUB,
                       "getValidatorDescription(address)((string,string,string,string))", op)
        try:
            d = json.loads(desc)[0]
            if isinstance(d, str):
                d = d.strip("()").split(", ")
        except Exception:
            d = [desc, "", "", ""]
        rows.append({"operator_address": op, "consensus_address": cons.lower(), "credit_contract": cr,
                     "moniker": d[0] if len(d) > 0 else "", "identity": d[1] if len(d) > 1 else "",
                     "website": d[2] if len(d) > 2 else "", "details": d[3] if len(d) > 3 else "",
                     "in_validatorset_getValidators": int(cons.lower() in cur),
                     "in_validatorset_getMiningValidators": int(cons.lower() in mining),
                     "queried_block": blk, "stakehub_total_length": total})
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("validators", len(rows), "block", blk, "current set", len(cur), "mining", len(mining))


if __name__ == "__main__":
    main()
