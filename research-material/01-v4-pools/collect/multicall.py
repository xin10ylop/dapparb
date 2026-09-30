#!/usr/bin/env python3
"""Minimal Multicall3.aggregate3 ABI encoder/decoder + chunked eth_call runner with endpoint fallback and bisection."""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MULTICALL3, RpcError, log

AGG3 = "82ad56cb"  # aggregate3((address,bool,bytes)[])


def _w(n):
    return "%064x" % n


def encode_aggregate3(calls):
    """calls: list of (target_hex, calldata_hex). allowFailure = true for all."""
    n = len(calls)
    heads, tails = [], []
    off = 32 * n
    for tgt, data in calls:
        d = data[2:] if data.startswith("0x") else data
        blen = len(d) // 2
        pad = d + "0" * ((64 - len(d) % 64) % 64)
        t = tgt[2:].lower().rjust(64, "0") + _w(1) + _w(0x60) + _w(blen) + pad
        heads.append(_w(off))
        tails.append(t)
        off += len(t) // 2
    return "0x" + AGG3 + _w(0x20) + _w(n) + "".join(heads) + "".join(tails)


def decode_aggregate3(ret_hex, n):
    d = ret_hex[2:]
    B = bytes.fromhex(d)

    def word(pos):
        return int.from_bytes(B[pos:pos + 32], "big")

    arr = word(0)
    cnt = word(arr)
    if cnt != n:
        raise RpcError("aggregate3 returned %d results for %d calls" % (cnt, n), kind="other")
    base = arr + 32
    out = []
    for i in range(cnt):
        t = base + word(base + 32 * i)
        ok = word(t) == 1
        boff = t + word(t + 32)
        ln = word(boff)
        out.append((ok, "0x" + B[boff + 32:boff + 32 + ln].hex()))
    return out


def run_multicall(eps, calls, block_hex, gas=None):
    """Execute calls (list of (target, data)) at block via Multicall3 on the first endpoint that answers.
    On endpoint errors tries the next endpoint; on repeated failure bisects the batch. Returns list of (ok, returndata_hex)."""
    if not calls:
        return []
    data = encode_aggregate3(calls)
    last = None
    order = list(eps)
    random.shuffle(order)
    for attempt in range(3):
        for ep in order:
            try:
                obj = {"to": MULTICALL3, "data": data}
                if gas:
                    obj["gas"] = hex(gas)
                ret = ep.call("eth_call", [obj, block_hex], timeout=120)
                return decode_aggregate3(ret, len(calls))
            except RpcError as e:
                last = e
                if e.kind == "rate":
                    time.sleep(2 + 3 * random.random())
                continue
        time.sleep(3 * (attempt + 1))
    if len(calls) > 1:
        mid = len(calls) // 2
        log("multicall bisect", len(calls), repr(last)[:200])
        return run_multicall(eps, calls[:mid], block_hex, gas) + run_multicall(eps, calls[mid:], block_hex, gas)
    raise last


def direct_call(eps, target, data, block_hex, gas=5_000_000):
    """Single eth_call (no multicall). Returns (ok, returndata_or_error_text)."""
    last = None
    for attempt in range(3):
        for ep in eps:
            try:
                return True, ep.call("eth_call", [{"to": target, "data": data, "gas": hex(gas)}, block_hex], timeout=60)
            except RpcError as e:
                last = e
                if e.kind in ("rate", "http"):
                    time.sleep(1 + 2 * random.random())
                    continue
                # execution error (revert / out of gas / invalid opcode): deterministic answer
                return False, "error: %s" % str(e)[:300]
        time.sleep(3 * (attempt + 1))
    raise last
