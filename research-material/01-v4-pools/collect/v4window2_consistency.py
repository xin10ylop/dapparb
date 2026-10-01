#!/usr/bin/env python3
"""Read-only consistency checks of the V4WINDOW2 outputs against other files already in research-material/ (no RPC).

1. Initialize rows: v4-window2-initialize-part-0001.csv.gz vs ../../02-v4-live-test/initialize-topup.csv.gz on the blocks both
   cover (52,006,433 to the top-up's block_to); all 27 columns compared.
2. Block-range adjacency with V4RECENT: last block of the v4-swap/modify/donate parts (recent-parts.json) + 1 == first window-2 block.
3. Snapshot vs logs: for each pool, the sqrt_price_x96 and tick of its last Swap (or of its Initialize when there is no Swap) at a
   block <= 52,017,008 inside the window, compared with getSlot0 at 52,017,008 in v4-window2-state-snapshot.csv.gz.
Output: one JSON object per check to stdout (redirected to v4window2_consistency.log).
"""
import csv
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
RM = os.path.dirname(OUT)
S = 52017008


def rows(path):
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        hdr = next(rd)
        for r in rd:
            yield hdr, r


def main():
    # 1
    w2 = {}
    for hdr, r in rows(os.path.join(OUT, "v4-window2-initialize-part-0001.csv.gz")):
        w2[(int(r[0]), int(r[3]))] = r
        h_w2 = hdr
    tp_path = os.path.join(RM, "02-v4-live-test", "initialize-topup.csv.gz")
    if os.path.exists(tp_path):
        tp_meta = json.load(open(os.path.join(RM, "02-v4-live-test", "initialize-topup.json")))
        lo, hi = 52006433, tp_meta["block_to"]
        tp = {}
        for hdr, r in rows(tp_path):
            if lo <= int(r[0]) <= hi:
                tp[(int(r[0]), int(r[3]))] = r
                h_tp = hdr
        w2o = {k: v for k, v in w2.items() if lo <= k[0] <= hi}
        print(json.dumps({"check": "initialize_vs_02_topup", "blocks": [lo, hi], "window2_rows": len(w2o), "topup_rows": len(tp),
                          "same_header": h_w2 == h_tp, "keys_only_window2": len(set(w2o) - set(tp)), "keys_only_topup": len(set(tp) - set(w2o)),
                          "rows_with_any_column_different": sum(1 for k in set(w2o) & set(tp) if w2o[k] != tp[k])}))
    # 2
    rp = json.load(open(os.path.join(OUT, "recent-parts.json")))
    w2p = json.load(open(os.path.join(OUT, "v4-window2-parts.json")))
    print(json.dumps({"check": "adjacent_to_v4recent", "v4recent_activity_block_to": max(p["block_to"] for k in ("swap", "modify", "donate") for p in rp["parts"][k]),
                      "window2_block_from": w2p["window"]["block_from"]}))
    # 3
    last = {}
    for hdr, r in rows(os.path.join(OUT, "v4-window2-initialize-part-0001.csv.gz")):
        if int(r[0]) <= S:
            last[r[4]] = ((int(r[0]), int(r[3])), r[10], r[11], "initialize")
    for hdr, r in rows(os.path.join(OUT, "v4-window2-swap-part-0001.csv.gz")):
        b = int(r[0])
        if b <= S:
            k = (b, int(r[3]))
            if r[4] not in last or last[r[4]][0] < k:
                last[r[4]] = (k, r[8], r[10], "swap")
    snap = {}
    for hdr, r in rows(os.path.join(OUT, "v4-window2-state-snapshot.csv.gz")):
        snap[r[0]] = r
    eq_p = eq_t = 0
    diff = []
    by_src = {"swap": [0, 0], "initialize": [0, 0]}
    for pid, (k, sp, tk, src) in last.items():
        s = snap[pid]
        ok = s[5] == sp and s[6] == tk
        by_src[src][0 if ok else 1] += 1
        eq_p += s[5] == sp
        eq_t += s[6] == tk
        if not ok:
            diff.append({"pool_id": pid, "last_event": src, "last_event_block_logindex": list(k), "event_sqrt_price_x96": sp, "event_tick": tk,
                         "slot0_sqrt_price_x96": s[5], "slot0_tick": s[6]})
    print(json.dumps({"check": "slot0_vs_last_swap_or_initialize_at_or_before_snapshot", "snapshot_block": S, "pools_compared": len(last),
                      "pools_not_compared": len(snap) - len(last), "sqrt_price_equal": eq_p, "tick_equal": eq_t,
                      "both_equal_by_last_event": {k: v[0] for k, v in by_src.items()},
                      "different_by_last_event": {k: v[1] for k, v in by_src.items()}, "different_rows": diff[:50]}))


if __name__ == "__main__":
    main()
