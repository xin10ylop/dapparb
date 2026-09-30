#!/usr/bin/env python3
"""Pin the BSC census window: the contiguous block range covering the most recent 60 minutes of
chain time, ending SAFETY blocks behind the head at the time this script runs.

Writes ../census/window.json (never overwrites an existing one unless --force).
Block time source: header field milliTimestamp (BSC-specific; ms resolution) and timestamp (s).
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rpc import Pool  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "census", "window.json")
SAFETY = 30          # blocks behind head (BSC fast finality is ~2 blocks; margin against reorgs)
SPAN_MS = 3600 * 1000

pool = Pool()


def hdr(n):
    b, u = pool.call("eth_getBlockByNumber", [hex(n), False])
    ms = int(b["milliTimestamp"], 16) if b.get("milliTimestamp") else int(b["timestamp"], 16) * 1000
    return {"number": int(b["number"], 16), "timestamp": int(b["timestamp"], 16), "milliTimestamp": ms,
            "hash": b["hash"], "endpoint": u}


def main():
    if os.path.exists(OUT) and "--force" not in sys.argv:
        print("window.json exists; use --force to re-pin", file=sys.stderr)
        print(open(OUT).read())
        return
    heads = {}
    for u in list(pool.endpoints)[:3]:
        p = Pool(endpoints={u: 1}, fallback={})
        r, _ = p.call("eth_blockNumber", [])
        heads[u] = int(r, 16)
    head = min(heads.values())
    end = head - SAFETY
    he = hdr(end)
    target = he["milliTimestamp"] - SPAN_MS
    # header samples to measure the block interval before choosing the range
    samples = [hdr(end - k) for k in (0, 100, 1000, 2000, 4000, 6000, 8000, 10000)]
    # binary search smallest block S with milliTimestamp >= target
    lo, hi = end - 20000, end
    hlo = hdr(lo)
    assert hlo["milliTimestamp"] < target, "search lower bound too high"
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if hdr(mid)["milliTimestamp"] >= target:
            hi = mid
        else:
            lo = mid
    start = hi
    hs = hdr(start)
    hprev = hdr(start - 1)
    w = {
        "chain": "bsc", "chain_id": 56,
        "pinned_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "heads_seen": heads, "safety_blocks_behind_head": SAFETY,
        "start_block": start, "end_block": end, "block_count": end - start + 1,
        "start_block_milliTimestamp": hs["milliTimestamp"], "end_block_milliTimestamp": he["milliTimestamp"],
        "start_block_utc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(hs["milliTimestamp"] / 1000)) + "Z",
        "end_block_utc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(he["milliTimestamp"] / 1000)) + "Z",
        "rule": "start_block = smallest block with milliTimestamp >= milliTimestamp(end_block) - 3600000",
        "block_before_start_milliTimestamp": hprev["milliTimestamp"],
        "header_samples": samples,
        "derived_interval_ms_over_window": (he["milliTimestamp"] - hs["milliTimestamp"]) / (end - start),
        "derived_interval_ms_over_header_samples": [
            {"from": samples[i + 1]["number"], "to": samples[0]["number"],
             "ms_per_block": (samples[0]["milliTimestamp"] - samples[i + 1]["milliTimestamp"]) /
             (samples[0]["number"] - samples[i + 1]["number"])} for i in range(len(samples) - 1)],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT + ".tmp", "w") as f:
        json.dump(w, f, indent=1)
    os.replace(OUT + ".tmp", OUT)
    print(json.dumps(w, indent=1))


if __name__ == "__main__":
    main()
