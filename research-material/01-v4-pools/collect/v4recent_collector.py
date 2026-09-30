#!/usr/bin/env python3
"""V4RECENT + V4STATE: recent Uniswap V4 activity on Base and a state snapshot at one pinned block.

Pinned block P = eth_blockNumber - 10 at first launch (stored in state/v4recent-pin.json; reruns reuse it).
Stage A (V4RECENT): all PoolManager Swap / ModifyLiquidity / Donate logs in [P-43199, P] (43,200 blocks = 24 h), 250-block chunks.
Stage B (V4RECENT): all PoolManager Initialize logs in [P-302399, P] (302,400 blocks = 7 days), 2,000-block chunks.
  Endpoints (work queue): base-rpc.publicnode.com (takes newest chunks first; stops at its first archive-depth refusal),
  developer-access-mainnet.base.org, gateway.tenderly.co/public/base. Bisection on range/size errors; results with >= 5,000
  logs re-fetched as halves. Chunk files in work/v4recent/ are the checkpoint.
  -> ../v4-swap-part-NNNN.csv.gz, ../v4-modify-liquidity-part-NNNN.csv.gz, ../v4-donate-part-NNNN.csv.gz,
     ../v4-initialize-7d-part-NNNN.csv.gz, ../recent-parts.json ; sentinel V4RECENT.DONE
Stage C (V4STATE): pool set = pools with any Stage-A event U pools initialized in Stage B. StateView.getSlot0 and
  getLiquidity for each pool via Multicall3.aggregate3 (allowFailure) at block P (archive eth_call endpoints).
Stage D (V4STATE): PoolKey for each pool: Stage-B Initialize logs; else PositionManager.poolKeys(bytes25) at P (accepted only when
  keccak256(abi.encode(key)) == pool_id); then, after V4INIT.DONE, the V4INIT Initialize data (authoritative, fills init_block).
Stage E (V4STATE): ERC-20 symbol(), name(), decimals(), totalSupply() at P for every non-native currency in the snapshot pools
  (Multicall3 first; every failed item retried with a direct eth_call, gas 5,000,000).
  -> ../state-snapshot.csv.gz, ../pool-keys-snapshot.csv.gz, ../token-metadata.csv.gz, ../state-index.json ; sentinel V4STATE.DONE
"""
import collections
import csv
import gzip
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DONATE_COLUMNS, INIT_COLUMNS, MODIFY_COLUMNS, POOL_MANAGER, POSITION_MANAGER, SENTINEL_DIR, STATE_VIEW, SWAP_COLUMNS,
                    T_DONATE, T_INITIALIZE, T_MODIFY, T_SWAP, Endpoint, PartWriter, RpcError, atomic_write_rows_gz, decode_activity,
                    get_logs_range, log, now_utc, pool_id_of, read_rows_gz, write_sentinel)
from multicall import direct_call, run_multicall
from v4init_collector import decode_chunk as decode_init_chunk

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
WORK = os.path.join(HERE, "work", "v4recent")
STATE = os.path.join(HERE, "state")
PIN = os.path.join(STATE, "v4recent-pin.json")
ACT_BLOCKS = 43200
INIT_BLOCKS = 302400
ACT_CHUNK = 250
INIT_CHUNK = 2000
V4INIT_WAIT_MAX_S = 12 * 3600


def log_endpoints():
    return [
        (Endpoint("publicnode", "https://base-rpc.publicnode.com", max_range=10000, inflight=2), 2, "newest"),
        (Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", max_range=2000, inflight=2), 2, "oldest"),
        (Endpoint("tenderly", "https://gateway.tenderly.co/public/base", max_range=1000, inflight=1), 1, "oldest"),
    ]


def call_endpoints():
    # archive-capable eth_call endpoints (verified: eth_call 300,000 blocks back answered on each)
    return [
        Endpoint("blastapi", "https://base-mainnet.public.blastapi.io", 10, inflight=1),
        Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", 2000, inflight=1),
        Endpoint("base.drpc.org", "https://base.drpc.org", 10, inflight=1),
        Endpoint("tenderly", "https://gateway.tenderly.co/public/base", 1000, inflight=1),
    ]


def load_pin():
    os.makedirs(STATE, exist_ok=True)
    if os.path.exists(PIN):
        return json.load(open(PIN))
    ep = Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", 2000)
    head = int(ep.call_retry("eth_blockNumber", []), 16)
    P = head - 10
    pin = {"pinned_block": P, "pinned_block_source": "eth_blockNumber(%s) - 10 at launch; head was %d" % (ep.url, head), "pinned_at_utc": now_utc(),
           "activity_window": [P - ACT_BLOCKS + 1, P], "initialize_window": [P - INIT_BLOCKS + 1, P], "snapshot_block": P}
    with open(PIN + ".tmp", "w") as f:
        json.dump(pin, f, indent=1)
    os.replace(PIN + ".tmp", PIN)
    return pin


def cpath(kind, frm, to):
    return os.path.join(WORK, "%s_%d_%d.csv.gz" % (kind, frm, to))


def mk_chunks(lo, hi, size):
    out = []
    b = lo
    while b <= hi:
        out.append((b, min(hi, b + size - 1)))
        b += size
    return out


def fetch_act(ep, frm, to):
    logs = get_logs_range(ep, frm, to, [[T_SWAP, T_MODIFY, T_DONATE]])
    rows = []
    seen = set()
    for lg in logs:
        if lg["address"].lower() != POOL_MANAGER:
            raise RpcError("unexpected address", kind="other")
        kind, row = decode_activity(lg)
        k = (int(row[0]), int(row[3]))
        if k in seen:
            continue
        seen.add(k)
        rows.append([kind] + row)
    rows.sort(key=lambda r: (int(r[1]), int(r[4])))
    return rows


def fetch_init(ep, frm, to):
    return decode_init_chunk(get_logs_range(ep, frm, to, [T_INITIALIZE]), frm, to)


def run_log_stage(tasks):
    """tasks: list of (kind, frm, to). Work queue over log endpoints; returns list of missing tasks."""
    eps = log_endpoints()
    todo = collections.deque(sorted([t for t in tasks if not os.path.exists(cpath(*t))], key=lambda t: t[1]))
    lock = threading.Lock()
    fails = collections.Counter()
    MAX_FAILS = 10
    done = [0]

    inflight = [0]

    def worker(ep, side):
        while True:
            with lock:
                if not todo:
                    if inflight[0] == 0:
                        return
                    t = None
                else:
                    t = todo.pop() if side == "newest" else todo.popleft()
                    inflight[0] += 1
            if t is None:
                time.sleep(2)  # other workers still hold chunks that may be requeued
                continue
            kind, frm, to = t
            try:
                rows = fetch_act(ep, frm, to) if kind == "act" else fetch_init(ep, frm, to)
                atomic_write_rows_gz(cpath(*t), rows)
                with lock:
                    done[0] += 1
                    inflight[0] -= 1
            except Exception as e:  # noqa: BLE001
                archive = isinstance(e, RpcError) and e.kind == "archive"
                with lock:
                    inflight[0] -= 1
                    if not archive:
                        fails[t] += 1
                    if fails[t] < MAX_FAILS:
                        (todo.append(t) if side == "newest" else todo.appendleft(t))
                log("chunk fail", ep.name, t, "fails", fails[t], repr(e)[:200])
                if archive:
                    log(ep.name, "reached archive depth limit at block", frm, "- worker stops")
                    return
                time.sleep(5)

    def progress(stop):
        while not stop.wait(60):
            with lock:
                log("progress done", done[0], "queue", len(todo), {ep.name: ep.stats for ep, _, _ in eps})

    stop = threading.Event()
    threading.Thread(target=progress, args=(stop,), daemon=True).start()
    ths = [threading.Thread(target=worker, args=(ep, side)) for ep, n, side in eps for _ in range(n)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    stop.set()
    return [t for t in tasks if not os.path.exists(cpath(*t))]


def assemble_logs(pin, act_tasks, init_tasks):
    for fn in os.listdir(OUT):
        if fn.startswith(("v4-swap-part-", "v4-modify-liquidity-part-", "v4-donate-part-", "v4-initialize-7d-part-")):
            os.remove(os.path.join(OUT, fn))
    ws = {"swap": PartWriter(OUT, "v4-swap", SWAP_COLUMNS), "modify": PartWriter(OUT, "v4-modify-liquidity", MODIFY_COLUMNS),
          "donate": PartWriter(OUT, "v4-donate", DONATE_COLUMNS)}
    counts = collections.Counter()
    for (_, frm, to) in sorted(act_tasks, key=lambda t: t[1]):
        rows = read_rows_gz(cpath("act", frm, to))
        by = collections.defaultdict(list)
        for r in rows:
            by[r[0]].append(r[1:])
        for k, w in ws.items():
            w.write_block_range(by.get(k, []), frm, to)
            counts[k] += len(by.get(k, []))
            w.maybe_rotate()
    parts = {k: w.close() for k, w in ws.items()}
    wi = PartWriter(OUT, "v4-initialize-7d", INIT_COLUMNS)
    n_init = 0
    for (_, frm, to) in sorted(init_tasks, key=lambda t: t[1]):
        rows = read_rows_gz(cpath("init", frm, to))
        wi.write_block_range(rows, frm, to)
        n_init += len(rows)
        wi.maybe_rotate()
    parts["initialize_7d"] = wi.close()
    for k, lst in parts.items():
        for p in lst:
            n = len(read_rows_gz(os.path.join(OUT, p["file"]))) - 1
            if n != p["rows"] or p["bytes"] > 90_000_000:
                raise RuntimeError("part verification failed %s" % p)
    idx = {"pin": pin, "pool_manager": POOL_MANAGER, "topics": {"swap": T_SWAP, "modify_liquidity": T_MODIFY, "donate": T_DONATE, "initialize": T_INITIALIZE},
           "rows": {"swap": counts["swap"], "modify_liquidity": counts["modify"], "donate": counts["donate"], "initialize_7d": n_init},
           "columns": {"swap": SWAP_COLUMNS, "modify_liquidity": MODIFY_COLUMNS, "donate": DONATE_COLUMNS, "initialize_7d": INIT_COLUMNS},
           "parts": parts, "sort": "block_number, log_index ascending", "assembled_utc": now_utc()}
    with open(os.path.join(OUT, "recent-parts.json"), "w") as f:
        json.dump(idx, f, indent=1)
    return idx


# ---------------------------------------------------------------------------------------------------------------- state
def pool_sets(act_tasks, init_tasks):
    active = set()
    init_keys = {}
    for (_, frm, to) in act_tasks:
        for r in read_rows_gz(cpath("act", frm, to)):
            active.add(r[5])
    for (_, frm, to) in init_tasks:
        for r in read_rows_gz(cpath("init", frm, to)):
            init_keys[r[4]] = {"currency0": r[5], "currency1": r[6], "fee_raw": r[7], "tick_spacing": r[8], "hooks": r[9], "init_block": r[0],
                               "key_source": "initialize_log_7d"}
    return active, init_keys


def parallel_batches(batches, fn, threads=3):
    res = [None] * len(batches)
    q = collections.deque(range(len(batches)))
    lock = threading.Lock()
    err = []

    def w():
        while True:
            with lock:
                if not q or err:
                    return
                i = q.popleft()
            try:
                res[i] = fn(batches[i])
            except Exception as e:  # noqa: BLE001
                err.append(e)
                return
    ths = [threading.Thread(target=w) for _ in range(threads)]
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    if err:
        raise err[0]
    return res


def snapshot_state(pools, P, ceps):
    bh = hex(P)
    batches = [pools[i:i + 250] for i in range(0, len(pools), 250)]

    def one(batch):
        calls = []
        for pid in batch:
            calls.append((STATE_VIEW, "0xc815641c" + pid[2:]))
            calls.append((STATE_VIEW, "0xfa6793d5" + pid[2:]))
        r = run_multicall(ceps, calls, bh)
        out = []
        for j, pid in enumerate(batch):
            (ok0, d0), (ok1, d1) = r[2 * j], r[2 * j + 1]
            if not ok0:
                ok0, d0 = direct_call(ceps, STATE_VIEW, calls[2 * j][1], bh)
            if not ok1:
                ok1, d1 = direct_call(ceps, STATE_VIEW, calls[2 * j + 1][1], bh)
            out.append((pid, ok0, d0, ok1, d1))
        return out
    res = parallel_batches(batches, one)
    rows = {}
    for lst in res:
        for pid, ok0, d0, ok1, d1 in lst:
            s0 = ["", "", "", ""]
            if ok0 and len(d0) == 2 + 64 * 4:
                w = [d0[2 + 64 * i: 2 + 64 * (i + 1)] for i in range(4)]
                t = int(w[1], 16)
                t = t - (1 << 256) if t >= 1 << 255 else t
                s0 = [str(int(w[0], 16)), str(t), str(int(w[2], 16)), str(int(w[3], 16))]
            liq = str(int(d1, 16)) if ok1 and len(d1) == 66 else ""
            rows[pid] = ["1" if ok0 else "0"] + s0 + ["1" if ok1 else "0", liq]
    return rows


def posm_keys(pids, P, ceps):
    bh = hex(P)
    out = {}
    batches = [pids[i:i + 300] for i in range(0, len(pids), 300)]

    def one(batch):
        calls = [(POSITION_MANAGER, "0x86b6be7d" + pid[2:52].ljust(64, "0")) for pid in batch]
        r = run_multicall(ceps, calls, bh)
        o = {}
        for pid, (ok, d) in zip(batch, r):
            if ok and len(d) == 2 + 64 * 5:
                w = [d[2 + 64 * i: 2 + 64 * (i + 1)] for i in range(5)]
                c0, c1, hk = "0x" + w[0][-40:], "0x" + w[1][-40:], "0x" + w[4][-40:]
                fee = int(w[2], 16)
                ts = int(w[3], 16)
                ts = ts - (1 << 256) if ts >= 1 << 255 else ts
                if pool_id_of(c0, c1, fee, ts, hk) == pid:
                    o[pid] = {"currency0": c0, "currency1": c1, "fee_raw": str(fee), "tick_spacing": str(ts), "hooks": hk, "init_block": "",
                              "key_source": "position_manager_poolKeys_at_snapshot"}
        return o
    for d in parallel_batches(batches, one):
        out.update(d)
    return out


def v4init_lookup(pids):
    """Look up Initialize rows for pids in the V4INIT final parts (or its work chunks if parts are absent)."""
    want = set(pids)
    found = {}
    idx = os.path.join(OUT, "initialize-parts.json")
    files = []
    if os.path.exists(idx):
        files = [(os.path.join(OUT, p["file"]), True) for p in json.load(open(idx))["parts"]]
    else:
        wd = os.path.join(HERE, "work", "v4init")
        files = [(os.path.join(wd, f), False) for f in sorted(os.listdir(wd)) if f.endswith(".csv.gz")]
    for path, has_header in files:
        with gzip.open(path, "rt", newline="") as f:
            rd = csv.reader(f)
            if has_header:
                next(rd)
            for r in rd:
                if r[4] in want:
                    found[r[4]] = {"currency0": r[5], "currency1": r[6], "fee_raw": r[7], "tick_spacing": r[8], "hooks": r[9], "init_block": r[0],
                                   "key_source": "initialize_log_v4init"}
    return found


def esc(sv):
    return "".join(c if (ord(c) >= 32 and c != "\\" and ord(c) != 127) else "\\x%02x" % ord(c) for c in sv)


def decode_str(d):
    if not d.startswith("0x"):
        return ""
    b = bytes.fromhex(d[2:])
    try:
        if len(b) >= 64:
            off = int.from_bytes(b[0:32], "big")
            ln = int.from_bytes(b[off:off + 32], "big")
            if off + 32 + ln <= len(b):
                return esc(b[off + 32: off + 32 + ln].decode("utf-8", errors="replace"))
        if len(b) == 32:
            return esc(b.rstrip(b"\x00").decode("utf-8", errors="replace"))
    except Exception:  # noqa: BLE001
        return ""
    return ""


def token_metadata(tokens, P, ceps):
    bh = hex(P)
    sels = [("symbol", "0x95d89b41"), ("name", "0x06fdde03"), ("decimals", "0x313ce567"), ("total_supply", "0x18160ddd")]
    batches = [tokens[i:i + 100] for i in range(0, len(tokens), 100)]

    def one(batch):
        calls = [(t, sel) for t in batch for _, sel in sels]
        r = run_multicall(ceps, calls, bh)
        modes = ["multicall"] * len(calls)
        # failed items: re-run once in a multicall of only the failed items (rules out gas starvation by an earlier item),
        # then each still-failing item as a direct eth_call (gas 5,000,000)
        failed = [k for k, (ok, _) in enumerate(r) if not ok]
        if failed:
            r2 = run_multicall(ceps, [calls[k] for k in failed], bh)
            for k, res2 in zip(failed, r2):
                r[k] = res2
                modes[k] = "multicall_retry"
            for k in [k for k in failed if not r[k][0]]:
                r[k] = direct_call(ceps, calls[k][0], calls[k][1], bh)
                modes[k] = "direct"
        out = []
        for i, t in enumerate(batch):
            row = [t]
            for j, (nm, sel) in enumerate(sels):
                ok, d = r[4 * i + j]
                row.append((nm, ok, d, modes[4 * i + j]))
            out.append(row)
        return out
    res = parallel_batches(batches, one)
    rows = []
    for lst in res:
        for row in lst:
            t = row[0]
            vals = {nm: (ok, d, mode) for nm, ok, d, mode in row[1:]}
            o = [t, "0"]
            for nm in ("symbol", "name"):
                ok, d, mode = vals[nm]
                o += ["1" if ok else "0", mode, d if ok else "", "" if ok else d, decode_str(d) if ok else ""]
            for nm in ("decimals", "total_supply"):
                ok, d, mode = vals[nm]
                dec = str(int(d, 16)) if ok and d.startswith("0x") and len(d) == 66 else ""
                o += ["1" if ok else "0", mode, d if ok else "", "" if ok else d, dec]
            rows.append(o)
    return rows


TOKEN_COLUMNS = ["address", "is_native"]
for _nm in ("symbol", "name", "decimals", "total_supply"):
    TOKEN_COLUMNS += [_nm + "_ok", _nm + "_call_mode", _nm + "_return_raw", _nm + "_error", _nm + ("_decoded" if _nm in ("symbol", "name") else "")]
STATE_COLUMNS = ["pool_id", "active_24h", "initialized_7d", "snapshot_block", "slot0_ok", "sqrt_price_x96", "tick", "protocol_fee", "lp_fee", "liquidity_ok", "liquidity"]
KEY_COLUMNS = ["pool_id", "currency0", "currency1", "fee_raw", "tick_spacing", "hooks", "init_block", "key_source"]


def main():
    os.makedirs(WORK, exist_ok=True)
    pin = load_pin()
    P = pin["pinned_block"]
    log("pin", json.dumps(pin))
    a0, a1 = pin["activity_window"]
    i0, i1 = pin["initialize_window"]
    act_tasks = [("act", f, t) for f, t in mk_chunks(a0, a1, ACT_CHUNK)]
    init_tasks = [("init", f, t) for f, t in mk_chunks(i0, i1, INIT_CHUNK)]
    rec_done = os.path.join(SENTINEL_DIR, "V4RECENT.DONE")
    if not os.path.exists(rec_done):
        missing = act_tasks + init_tasks
        for rnd in range(1, 6):
            missing = run_log_stage(act_tasks + init_tasks)
            log("log stage round", rnd, "missing", len(missing))
            if not missing:
                break
            time.sleep(120 * rnd)
        if missing:
            with open(os.path.join(STATE, "v4recent-gaps.json"), "w") as f:
                json.dump({"missing_chunks": missing, "written_utc": now_utc()}, f, indent=1)
            write_sentinel("V4RECENT", False, "missing %d chunks after 5 rounds; see collect/state/v4recent-gaps.json; rerun to resume" % len(missing))
            write_sentinel("V4STATE", False, "not started: V4RECENT log stage incomplete")
            return 1
        idx = assemble_logs(pin, act_tasks, init_tasks)
        write_sentinel("V4RECENT", True, json.dumps({"index": os.path.join(OUT, "recent-parts.json"), "rows": idx["rows"], "pin": pin, "completed_utc": now_utc()}))
        log("V4RECENT done", idx["rows"])

    ceps = call_endpoints()
    active, init_keys = pool_sets(act_tasks, init_tasks)
    pools = sorted(active | set(init_keys))
    log("snapshot pools", len(pools), "active", len(active), "init7d", len(init_keys))
    snap_ck = os.path.join(STATE, "v4state-slot0.json")
    if os.path.exists(snap_ck):
        snap = json.load(open(snap_ck))
    else:
        snap = snapshot_state(pools, P, ceps)
        with open(snap_ck + ".tmp", "w") as f:
            json.dump(snap, f)
        os.replace(snap_ck + ".tmp", snap_ck)
    log("slot0/liquidity rows", len(snap))
    atomic_write_rows_gz(os.path.join(OUT, "state-snapshot.csv.gz"),
                         [[pid, "1" if pid in active else "0", "1" if pid in init_keys else "0", str(P)] + snap[pid] for pid in pools], STATE_COLUMNS)

    keys_ck = os.path.join(STATE, "v4state-keys.json")
    keys = json.load(open(keys_ck)) if os.path.exists(keys_ck) else {}
    keys.update({k: v for k, v in init_keys.items() if k in set(pools)})
    missing = [p for p in pools if p not in keys]
    if missing and not any(v["key_source"] == "position_manager_poolKeys_at_snapshot" for v in keys.values()):
        keys.update(posm_keys(missing, P, ceps))
    with open(keys_ck, "w") as f:
        json.dump(keys, f)
    log("keys resolved", len(keys), "of", len(pools))

    meta_ck = os.path.join(STATE, "v4state-meta.json")
    meta = json.load(open(meta_ck)) if os.path.exists(meta_ck) else {}

    def do_meta():
        toks = sorted({k[c] for k in keys.values() for c in ("currency0", "currency1")} - {"0x0000000000000000000000000000000000000000"} - set(meta))
        if toks:
            for r in token_metadata(toks, P, ceps):
                meta[r[0]] = r
            with open(meta_ck + ".tmp", "w") as f:
                json.dump(meta, f)
            os.replace(meta_ck + ".tmp", meta_ck)
        log("token metadata rows", len(meta))
    do_meta()

    # wait for V4INIT to resolve remaining keys and fill init_block for all
    t0 = time.time()
    v4init_ok = False
    while time.time() - t0 < V4INIT_WAIT_MAX_S:
        if os.path.exists(os.path.join(SENTINEL_DIR, "V4INIT.DONE")):
            v4init_ok = True
            break
        if os.path.exists(os.path.join(SENTINEL_DIR, "V4INIT.FAILED")):
            break
        time.sleep(120)
    log("V4INIT status", "DONE" if v4init_ok else "not done", "; looking up keys")
    need = [p for p in pools if p not in keys or not keys[p].get("init_block")]
    found = v4init_lookup(need)
    for pid, k in found.items():
        prev = keys.get(pid)
        if prev and prev["key_source"].startswith("position_manager"):
            for c in ("currency0", "currency1", "fee_raw", "tick_spacing", "hooks"):
                if prev[c] != k[c]:
                    raise RuntimeError("PositionManager key disagrees with Initialize log for %s" % pid)
        keys[pid] = k
    with open(keys_ck, "w") as f:
        json.dump(keys, f)
    do_meta()
    unresolved = [p for p in pools if p not in keys]
    atomic_write_rows_gz(os.path.join(OUT, "pool-keys-snapshot.csv.gz"),
                         [[p] + [keys[p][c] for c in KEY_COLUMNS[1:]] for p in pools if p in keys] + [[p, "", "", "", "", "", "", "unresolved"] for p in unresolved],
                         KEY_COLUMNS)
    trows = [["0x0000000000000000000000000000000000000000", "1"] + [""] * (len(TOKEN_COLUMNS) - 2)] + [meta[t] for t in sorted(meta)]
    atomic_write_rows_gz(os.path.join(OUT, "token-metadata.csv.gz"), trows, TOKEN_COLUMNS)
    sidx = {"snapshot_block": P, "pin": pin, "pools": len(pools), "pools_active_24h": len(active), "pools_initialized_7d": len(init_keys),
            "keys_resolved": len(pools) - len(unresolved), "keys_unresolved": len(unresolved), "tokens": len(trows),
            "v4init_used": v4init_ok, "files": {"state": "state-snapshot.csv.gz", "keys": "pool-keys-snapshot.csv.gz", "tokens": "token-metadata.csv.gz"},
            "columns": {"state": STATE_COLUMNS, "keys": KEY_COLUMNS, "tokens": TOKEN_COLUMNS}, "call_endpoints": [e.url for e in ceps], "completed_utc": now_utc()}
    with open(os.path.join(OUT, "state-index.json"), "w") as f:
        json.dump(sidx, f, indent=1)
    if unresolved:
        write_sentinel("V4STATE", False, "state + metadata written but %d pool keys unresolved (V4INIT %s); see state-index.json" %
                       (len(unresolved), "DONE" if v4init_ok else "not DONE"))
        return 1
    write_sentinel("V4STATE", True, json.dumps(sidx))
    log("V4STATE done")
    return 0


def smoke():
    """Small end-to-end check on a short window near head; writes nothing under OUT."""
    ep = Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", 2000)
    head = int(ep.call_retry("eth_blockNumber", []), 16)
    P = head - 10
    res = {}
    for e, _, _ in log_endpoints():
        try:
            rows = fetch_act(e, P - 249, P)
            res[e.name] = rows
            log("smoke act", e.name, len(rows), collections.Counter(r[0] for r in rows))
        except Exception as ex:  # noqa: BLE001
            log("smoke act", e.name, "ERROR", repr(ex)[:200])
    names = list(res)
    for n in names[1:]:
        log("compare", names[0], n, "identical" if res[n] == res[names[0]] else "DIFFERENT")
    rows = res[names[0]]
    for k in ("swap", "modify", "donate"):
        ex = [r for r in rows if r[0] == k][:1]
        if ex:
            cols = {"swap": SWAP_COLUMNS, "modify": MODIFY_COLUMNS, "donate": DONATE_COLUMNS}[k]
            log("sample", k, dict(zip(cols, ex[0][1:])))
    ir = fetch_init(log_endpoints()[1][0], P - 1999, P)
    log("smoke init rows", len(ir))
    pools = sorted({r[5] for r in rows} | {r[4] for r in ir})[:30]
    ceps = call_endpoints()
    snap = snapshot_state(pools, P, ceps)
    for pid in pools[:3]:
        log("state", pid, dict(zip(STATE_COLUMNS[4:], snap[pid])))
    keys = {r[4]: r for r in ir}
    pk = posm_keys([p for p in pools if p not in keys], P, ceps)
    log("posm keys resolved", len(pk), "of", len([p for p in pools if p not in keys]))
    for pid, k in list(pk.items())[:2]:
        log("posm key", pid, k)
    toks = sorted({k[c] for k in pk.values() for c in ("currency0", "currency1")} | {r[5] for r in ir[:10]} | {r[6] for r in ir[:10]}
                  | {"0x0000000000000000000000000000000000000001", "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2"}
                  - {"0x0000000000000000000000000000000000000000"})[:40]
    for r in token_metadata(toks, P, ceps)[:40]:
        log("token", dict(zip(TOKEN_COLUMNS, r)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--smoke":
        smoke()
        sys.exit(0)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        if not os.path.exists(os.path.join(SENTINEL_DIR, "V4RECENT.DONE")):
            write_sentinel("V4RECENT", False, "crashed: %r (rerun collect/v4recent_collector.py to resume)" % (e,))
        write_sentinel("V4STATE", False, "crashed: %r (rerun collect/v4recent_collector.py to resume)" % (e,))
        raise
