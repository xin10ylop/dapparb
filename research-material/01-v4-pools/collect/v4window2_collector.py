#!/usr/bin/env python3
"""V4WINDOW2: Uniswap V4 PoolManager logs on Base for the span after the V4RECENT 24 h window up to the end of the Base census,
plus a StateView snapshot and ERC-20 metadata for the pools seen in that span.

Fixed window (no head pin): blocks W0 = 52,006,433 (V4RECENT pinned block 52,006,432 + 1) to W1 = 52,017,160 (last block of the
05-base-onchain census, .sentinels/BASE_CENSUS.DONE `range_last_block`), inclusive. Snapshot block S = 52,017,008.

Stage A (logs): 1,000-block chunks aligned at W0 (the last chunk is shorter). Per chunk:
  * Swap / ModifyLiquidity / Donate: eth_getLogs(address = PoolManager, topics = [[Swap, ModifyLiquidity, Donate]]) in 250-block
    sub-requests; Initialize: eth_getLogs(topic0 = Initialize) over the whole chunk.
  * get_logs_range() from common.py (bisection on range/size errors, any response with >= 5,000 logs re-fetched as halves,
    block-in-range and removed == false checks). Decoding: common.decode_activity / v4init_collector.decode_chunk, i.e. the same
    code as v4recent_collector.py (same dedup by (block, log_index) and (block, log_index) sort). Initialize rows are checked
    pool_id == keccak256(abi.encode(PoolKey)).
  * primary endpoint gateway.tenderly.co/public/base; on failure mainnet.base.org, then developer-access-mainnet.base.org.
    The endpoint that served each chunk is recorded in work/v4window2/meta_<from>_<to>.json and in ../v4-window2-parts.json.
  * every chunk is fetched a second time from a different endpoint (mainnet.base.org, or Tenderly when mainnet.base.org was the
    primary; developer-access as fallback) and the decoded rows are compared (xcheck_<from>_<to>.json).
  * blockHash of every returned log is kept per block and compared with block_hash in ../../05-base-onchain/blocks.csv.gz; every
    (block_number, tx_index, tx_hash) is looked up in ../../05-base-onchain/data/txs-fw-*.csv.gz.
  -> ../v4-window2-{swap,modify-liquidity,donate,initialize}-part-NNNN.csv.gz, ../v4-window2-parts.json
Stage B (snapshot): pool set = every pool_id in the Stage-A rows (all four event types). StateView.getSlot0 / getLiquidity at S
  via Multicall3 (v4recent_collector.snapshot_state, unchanged). PoolKeys: window Initialize logs, else pool-keys-snapshot.csv.gz,
  else the V4INIT Initialize rows (initialize-part-*.csv.gz, or initialize-compact/ via expand_initialize.iter_rows when the
  originals are absent); every key is re-checked with keccak256(abi.encode(key)) == pool_id.
  ERC-20 symbol/name/decimals/totalSupply (v4recent_collector.token_metadata, unchanged) at S for every non-native currency of
  those pools that is not already an address in ../token-metadata.csv.gz. A currency whose four calls all return success with
  empty data and that has no code at S (eth_getCode) is called again at W1; the block used is in column call_block.
  -> ../v4-window2-state-snapshot.csv.gz, ../v4-window2-pool-keys.csv.gz, ../v4-window2-token-metadata.csv.gz,
     ../v4-window2-state-index.json ; sentinel .sentinels/V4WINDOW2.DONE (or .FAILED)

Resumable: chunk files, meta and xcheck files in work/v4window2/ and state/v4window2-*.json are checkpoints; a rerun skips them.
Usage: python3 v4window2_collector.py [--smoke]   (smoke: one 200-block range on both log endpoints + 20-pool snapshot, writes nothing under ..)
"""
import collections
import csv
import glob
import gzip
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DONATE_COLUMNS, INIT_COLUMNS, MODIFY_COLUMNS, POOL_MANAGER, SENTINEL_DIR, SWAP_COLUMNS, T_DONATE, T_INITIALIZE,
                    T_MODIFY, T_SWAP, Endpoint, PartWriter, RpcError, atomic_write_rows_gz, decode_activity, get_logs_range, log,
                    now_utc, pool_id_of, read_rows_gz, write_sentinel)
from v4init_collector import decode_chunk as decode_init_chunk
from v4recent_collector import KEY_COLUMNS, TOKEN_COLUMNS, call_endpoints, mk_chunks, snapshot_state, token_metadata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
RM = os.path.dirname(OUT)
WORK = os.path.join(HERE, "work", "v4window2")
STATE = os.path.join(HERE, "state")
NAME = "V4WINDOW2"

W0 = 52006433          # recent-parts.json pin.pinned_block (52006432) + 1
W1 = 52017160          # .sentinels/BASE_CENSUS.DONE summary.range_last_block
S = 52017008           # snapshot block (end of the V4 live test, 02-v4-live-test)
CHUNK = 1000
ACT_SUB = 250
NATIVE = "0x0000000000000000000000000000000000000000"

STATE_COLUMNS_W2 = ["pool_id", "active_window2", "initialized_window2", "snapshot_block", "slot0_ok", "sqrt_price_x96", "tick",
                    "protocol_fee", "lp_fee", "liquidity_ok", "liquidity"]
TOKEN_COLUMNS_W2 = TOKEN_COLUMNS + ["call_block"]

EP_DEFS = {
    "tenderly": ("https://gateway.tenderly.co/public/base", 1000),
    "mainnet.base.org": ("https://mainnet.base.org", 2000),
    "developer-access-mainnet.base.org": ("https://developer-access-mainnet.base.org", 2000),
}
PRIMARY_ORDER = ["tenderly", "mainnet.base.org", "developer-access-mainnet.base.org"]


class EpPair:
    """Two Endpoint objects for one URL: act (250-block sub-requests) and init (whole chunk); one shared in-flight limit."""

    def __init__(self, name):
        url, mx = EP_DEFS[name]
        self.name, self.url = name, url
        self.act = Endpoint(name, url, max_range=ACT_SUB, inflight=2)
        self.init = Endpoint(name, url, max_range=min(mx, CHUNK), inflight=2)
        self.init.sem = self.act.sem  # <= 2 in flight per endpoint for this process


_EPS = {}


def ep(name):
    if name not in _EPS:
        _EPS[name] = EpPair(name)
    return _EPS[name]


def fetch_chunk(e, frm, to):
    """Returns (act_rows, init_rows, block_hashes) for [frm, to] from endpoint pair e.
    act rows: [kind] + row, decoded exactly as v4recent_collector.fetch_act; init rows: v4init_collector.decode_chunk."""
    logs = get_logs_range(e.act, frm, to, [[T_SWAP, T_MODIFY, T_DONATE]])
    bh = {}

    def keep_hash(lg):
        b = int(lg["blockNumber"], 16)
        h = lg["blockHash"].lower()
        if bh.setdefault(b, h) != h:
            raise RpcError("two blockHash values for block %d in one response set" % b, kind="other")
    rows = []
    seen = set()
    for lg in logs:
        if lg["address"].lower() != POOL_MANAGER:
            raise RpcError("unexpected address", kind="other")
        keep_hash(lg)
        kind, row = decode_activity(lg)
        k = (int(row[0]), int(row[3]))
        if k in seen:
            continue
        seen.add(k)
        rows.append([kind] + row)
    rows.sort(key=lambda r: (int(r[1]), int(r[4])))
    ilogs = get_logs_range(e.init, frm, to, [T_INITIALIZE])
    for lg in ilogs:
        keep_hash(lg)
    irows = decode_init_chunk(ilogs, frm, to)
    return rows, irows, bh


def cpath(kind, frm, to):
    return os.path.join(WORK, "%s_%d_%d.csv.gz" % (kind, frm, to))


def mpath(kind, frm, to):
    return os.path.join(WORK, "%s_%d_%d.json" % (kind, frm, to))


def write_json(path, obj):
    with open(path + ".tmp", "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
    os.replace(path + ".tmp", path)


def counts_of(act, init):
    c = collections.Counter(r[0] for r in act)
    return {"swap": c["swap"], "modify_liquidity": c["modify"], "donate": c["donate"], "initialize": len(init)}


def primary_chunk(frm, to):
    if os.path.exists(mpath("meta", frm, to)):
        return True
    errors = []
    for name in PRIMARY_ORDER:
        e = ep(name)
        t0 = time.time()
        try:
            act, init, bh = fetch_chunk(e, frm, to)
        except Exception as ex:  # noqa: BLE001
            errors.append({"endpoint": name, "error": repr(ex)[:300], "utc": now_utc()})
            log("primary fail", name, frm, to, repr(ex)[:200])
            continue
        atomic_write_rows_gz(cpath("act", frm, to), act)
        atomic_write_rows_gz(cpath("init", frm, to), init)
        write_json(mpath("meta", frm, to), {"from": frm, "to": to, "endpoint": name, "endpoint_url": e.url,
                                            "act_subrequest_blocks": e.act.max_range, "init_request_blocks": e.init.max_range,
                                            "rows": counts_of(act, init), "fetched_utc": now_utc(), "seconds": round(time.time() - t0, 1),
                                            "failed_attempts_before": errors,
                                            "block_hashes": {str(b): h for b, h in sorted(bh.items())}})
        log("chunk", frm, to, name, counts_of(act, init), "%.1fs" % (time.time() - t0))
        return True
    log("chunk FAILED on all endpoints", frm, to)
    return False


def xcheck_chunk(frm, to):
    if os.path.exists(mpath("xcheck", frm, to)):
        return json.load(open(mpath("xcheck", frm, to)))["identical"]
    meta = json.load(open(mpath("meta", frm, to)))
    order = [n for n in ["mainnet.base.org", "tenderly", "developer-access-mainnet.base.org"] if n != meta["endpoint"]]
    act = read_rows_gz(cpath("act", frm, to))
    init = read_rows_gz(cpath("init", frm, to))
    errors = []
    for name in order:
        e = ep(name)
        try:
            act2, init2, bh2 = fetch_chunk(e, frm, to)
        except Exception as ex:  # noqa: BLE001
            errors.append({"endpoint": name, "error": repr(ex)[:300], "utc": now_utc()})
            log("xcheck fail", name, frm, to, repr(ex)[:200])
            continue
        bh1 = meta["block_hashes"]
        same_act = act2 == act
        same_init = init2 == init
        same_bh = {str(b): h for b, h in bh2.items()} == bh1
        res = {"from": frm, "to": to, "primary_endpoint": meta["endpoint"], "xcheck_endpoint": name, "xcheck_url": e.url,
               "primary_rows": counts_of(act, init), "xcheck_rows": counts_of(act2, init2),
               "identical_activity_rows": same_act, "identical_initialize_rows": same_init, "identical_block_hashes": same_bh,
               "identical": same_act and same_init and same_bh, "checked_utc": now_utc(), "failed_attempts_before": errors}
        if not res["identical"]:
            s1 = set(map(tuple, act)) | set(map(tuple, init))
            s2 = set(map(tuple, act2)) | set(map(tuple, init2))
            res["only_primary_sample"] = [list(x) for x in sorted(s1 - s2)[:20]]
            res["only_xcheck_sample"] = [list(x) for x in sorted(s2 - s1)[:20]]
            res["only_primary_count"] = len(s1 - s2)
            res["only_xcheck_count"] = len(s2 - s1)
        write_json(mpath("xcheck", frm, to), res)
        log("xcheck", frm, to, meta["endpoint"], "vs", name, "identical" if res["identical"] else "DIFFERENT", res["xcheck_rows"])
        return res["identical"]
    log("xcheck FAILED on all endpoints", frm, to)
    return None


def run_pool(fn, tasks, workers=2):
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda t: fn(*t), tasks))


# ------------------------------------------------------------------------------------------------------------- census checks
def census_checks(chunks):
    """Compare log blockHashes with 05-base-onchain/blocks.csv.gz and tx hashes with 05-base-onchain/data/txs-*.csv.gz."""
    bh = {}
    for (frm, to) in chunks:
        for b, h in json.load(open(mpath("meta", frm, to)))["block_hashes"].items():
            bh[int(b)] = h
    want_tx = {}
    for (frm, to) in chunks:
        for r in read_rows_gz(cpath("act", frm, to)):
            want_tx[(int(r[1]), int(r[3]))] = r[2]
        for r in read_rows_gz(cpath("init", frm, to)):
            want_tx[(int(r[0]), int(r[2]))] = r[1]
    res = {"blocks_with_logs": len(bh), "txs_with_logs": len(want_tx)}
    bpath = os.path.join(RM, "05-base-onchain", "blocks.csv.gz")
    if os.path.exists(bpath):
        match = mism = 0
        mism_list = []
        with gzip.open(bpath, "rt", newline="") as f:
            for d in csv.DictReader(f):
                b = int(d["block_number"])
                if b in bh:
                    if bh[b] == d["block_hash"].lower():
                        match += 1
                    else:
                        mism += 1
                        mism_list.append(b)
        res.update({"census_blocks_file": "05-base-onchain/blocks.csv.gz", "block_hash_equal": match, "block_hash_different": mism,
                    "block_hash_different_blocks": mism_list[:50], "blocks_not_in_census": len(bh) - match - mism})
    tx_files = sorted(glob.glob(os.path.join(RM, "05-base-onchain", "data", "txs-*.csv.gz")))
    if tx_files:
        match = mism = st0 = 0
        found = set()
        for p in tx_files:
            with gzip.open(p, "rt", newline="") as f:
                rd = csv.reader(f)
                hdr = next(rd)
                ib, ii, ih, ist = hdr.index("block_number"), hdr.index("tx_index"), hdr.index("tx_hash"), hdr.index("status")
                for r in rd:
                    b = int(r[ib])
                    if b < W0 or b > W1:
                        continue
                    k = (b, int(r[ii]))
                    if k in want_tx and k not in found:
                        found.add(k)
                        if want_tx[k] == r[ih].lower():
                            match += 1
                        else:
                            mism += 1
                        if r[ist] != "1":
                            st0 += 1
        res.update({"census_tx_files": [os.path.relpath(p, RM) for p in tx_files], "tx_hash_equal": match, "tx_hash_different": mism,
                    "txs_not_in_census": len(want_tx) - match - mism, "txs_with_census_status_not_1": st0})
    return res


# ------------------------------------------------------------------------------------------------------------- assemble
def assemble(chunks, metas, xchecks, census):
    for fn in os.listdir(OUT):
        if fn.startswith("v4-window2-") and "-part-" in fn:
            os.remove(os.path.join(OUT, fn))
    ws = {"swap": PartWriter(OUT, "v4-window2-swap", SWAP_COLUMNS), "modify": PartWriter(OUT, "v4-window2-modify-liquidity", MODIFY_COLUMNS),
          "donate": PartWriter(OUT, "v4-window2-donate", DONATE_COLUMNS)}
    wi = PartWriter(OUT, "v4-window2-initialize", INIT_COLUMNS)
    counts = collections.Counter()
    for (frm, to) in chunks:
        by = collections.defaultdict(list)
        for r in read_rows_gz(cpath("act", frm, to)):
            by[r[0]].append(r[1:])
        for k, w in ws.items():
            w.write_block_range(by.get(k, []), frm, to)
            counts[k] += len(by.get(k, []))
            w.maybe_rotate()
        ir = read_rows_gz(cpath("init", frm, to))
        wi.write_block_range(ir, frm, to)
        counts["initialize"] += len(ir)
        wi.maybe_rotate()
    parts = {k: w.close() for k, w in ws.items()}
    parts["initialize"] = wi.close()
    for k, lst in parts.items():
        for p in lst:
            rows = read_rows_gz(os.path.join(OUT, p["file"]))
            if len(rows) - 1 != p["rows"] or p["bytes"] > 90_000_000:
                raise RuntimeError("part verification failed %s" % p)
            hdr = {"swap": SWAP_COLUMNS, "modify": MODIFY_COLUMNS, "donate": DONATE_COLUMNS, "initialize": INIT_COLUMNS}[k]
            if rows[0] != hdr:
                raise RuntimeError("header mismatch %s" % p["file"])
            keys = [(int(r[0]), int(r[3])) for r in rows[1:]]
            if keys != sorted(keys) or len(set(keys)) != len(keys):
                raise RuntimeError("order/duplicate check failed %s" % p["file"])
    chunk_table = []
    for (frm, to) in chunks:
        m, x = metas[(frm, to)], xchecks[(frm, to)]
        chunk_table.append({"from": frm, "to": to, "endpoint": m["endpoint"], "endpoint_url": m["endpoint_url"], "rows": m["rows"],
                            "fetched_utc": m["fetched_utc"], "act_subrequest_blocks": m["act_subrequest_blocks"],
                            "init_request_blocks": m["init_request_blocks"], "failed_attempts_before": len(m["failed_attempts_before"]),
                            "xcheck_endpoint": x["xcheck_endpoint"], "xcheck_identical": x["identical"], "xcheck_utc": x["checked_utc"]})
    idx = {"dataset": "Uniswap V4 PoolManager Swap / ModifyLiquidity / Donate / Initialize logs, Base (chain 8453), window 2",
           "pool_manager": POOL_MANAGER,
           "window": {"block_from": W0, "block_to": W1, "blocks": W1 - W0 + 1,
                      "block_from_source": "recent-parts.json pin.pinned_block (52006432) + 1",
                      "block_to_source": ".sentinels/BASE_CENSUS.DONE summary.range_last_block",
                      "utc_from": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(1686789347 + 2 * W0)),
                      "utc_to": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(1686789347 + 2 * W1))},
           "topics": {"swap": T_SWAP, "modify_liquidity": T_MODIFY, "donate": T_DONATE, "initialize": T_INITIALIZE},
           "rows": {"swap": counts["swap"], "modify_liquidity": counts["modify"], "donate": counts["donate"], "initialize": counts["initialize"]},
           "columns": {"swap": SWAP_COLUMNS, "modify_liquidity": MODIFY_COLUMNS, "donate": DONATE_COLUMNS, "initialize": INIT_COLUMNS},
           "parts": {"swap": parts["swap"], "modify_liquidity": parts["modify"], "donate": parts["donate"], "initialize": parts["initialize"]},
           "chunks": chunk_table, "gaps": [], "census_consistency": census,
           "sort": "block_number, log_index ascending", "assembled_utc": now_utc()}
    write_json(os.path.join(OUT, "v4-window2-parts.json"), idx)
    return idx


# ------------------------------------------------------------------------------------------------------------- snapshot
def resolve_keys(pools, init_rows):
    want = set(pools)
    keys = {}
    for r in init_rows:
        if r[4] in want:
            keys[r[4]] = {"currency0": r[5], "currency1": r[6], "fee_raw": r[7], "tick_spacing": r[8], "hooks": r[9], "init_block": r[0],
                          "key_source": "initialize_log_window2"}
    with gzip.open(os.path.join(OUT, "pool-keys-snapshot.csv.gz"), "rt", newline="") as f:
        for d in csv.DictReader(f):
            if d["pool_id"] in want and d["pool_id"] not in keys and d["key_source"].startswith("initialize_log"):
                keys[d["pool_id"]] = {c: d[c] for c in KEY_COLUMNS[1:]}
    n_snap = len(keys)
    need = want - set(keys)
    src = None
    if need:
        idx = os.path.join(OUT, "initialize-parts.json")
        files = [os.path.join(OUT, p["file"]) for p in json.load(open(idx))["parts"]]
        if all(os.path.exists(p) for p in files):
            src = "initialize-part-0001..0022.csv.gz"
            for p in files:
                with gzip.open(p, "rt", newline="") as f:
                    rd = csv.reader(f)
                    next(rd)
                    for r in rd:
                        if r[4] in need:
                            keys[r[4]] = {"currency0": r[5], "currency1": r[6], "fee_raw": r[7], "tick_spacing": r[8], "hooks": r[9],
                                          "init_block": r[0], "key_source": "initialize_log_v4init"}
        else:
            src = "initialize-compact/ via expand_initialize.iter_rows"
            from expand_initialize import iter_rows
            for d in iter_rows():
                if d["pool_id"] in need:
                    keys[d["pool_id"]] = {"currency0": d["currency0"], "currency1": d["currency1"], "fee_raw": d["fee_raw"],
                                          "tick_spacing": d["tick_spacing"], "hooks": d["hooks"], "init_block": d["block_number"],
                                          "key_source": "initialize_log_v4init"}
    for pid, k in keys.items():
        if pool_id_of(k["currency0"], k["currency1"], k["fee_raw"], k["tick_spacing"], k["hooks"]) != pid:
            raise RuntimeError("PoolKey hash mismatch for %s" % pid)
    return keys, {"from_window2_initialize": sum(1 for k in keys.values() if k["key_source"] == "initialize_log_window2"),
                  "from_pool_keys_snapshot": n_snap - sum(1 for k in keys.values() if k["key_source"] == "initialize_log_window2"),
                  "from_v4init_scan": len(keys) - n_snap, "v4init_scan_source": src, "unresolved": len(want - set(keys))}


def no_code_at(ceps, addr, block):
    """eth_getCode(addr, block) == '0x' on the first answering endpoint; returns (bool, endpoint)."""
    last = None
    for attempt in range(4):
        for e in ceps:
            try:
                return e.call("eth_getCode", [addr, hex(block)], timeout=60) in ("0x", "0x0"), e.name
            except RpcError as ex:
                last = ex
                time.sleep(1 + attempt)
    raise last


def snapshot(pools, active, initialized, init_rows):
    os.makedirs(STATE, exist_ok=True)
    ceps = call_endpoints()
    snap_ck = os.path.join(STATE, "v4window2-slot0.json")
    if os.path.exists(snap_ck):
        snap = json.load(open(snap_ck))
    else:
        snap = snapshot_state(pools, S, ceps)
        write_json(snap_ck, snap)
    if set(snap) != set(pools):
        raise RuntimeError("snapshot pool set mismatch")
    atomic_write_rows_gz(os.path.join(OUT, "v4-window2-state-snapshot.csv.gz"),
                         [[pid, "1" if pid in active else "0", "1" if pid in initialized else "0", str(S)] + snap[pid] for pid in pools],
                         STATE_COLUMNS_W2)
    log("snapshot rows", len(snap))

    keys_ck = os.path.join(STATE, "v4window2-keys.json")
    if os.path.exists(keys_ck):
        ck = json.load(open(keys_ck))
        keys, kstats = ck["keys"], ck["stats"]
    else:
        keys, kstats = resolve_keys(pools, init_rows)
        write_json(keys_ck, {"keys": keys, "stats": kstats})
    unresolved = [p for p in pools if p not in keys]
    atomic_write_rows_gz(os.path.join(OUT, "v4-window2-pool-keys.csv.gz"),
                         [[p] + [keys[p][c] for c in KEY_COLUMNS[1:]] for p in pools if p in keys]
                         + [[p, "", "", "", "", "", "", "unresolved"] for p in unresolved], KEY_COLUMNS)
    log("keys", kstats)

    existing = set()
    with gzip.open(os.path.join(OUT, "token-metadata.csv.gz"), "rt", newline="") as f:
        rd = csv.reader(f)
        next(rd)
        for r in rd:
            existing.add(r[0])
    cur = {k[c] for k in keys.values() for c in ("currency0", "currency1")}
    toks = sorted(cur - {NATIVE} - existing)
    log("currencies", len(cur), "already in token-metadata.csv.gz", len(cur & existing), "new", len(toks))
    meta_ck = os.path.join(STATE, "v4window2-meta.json")
    meta = json.load(open(meta_ck)) if os.path.exists(meta_ck) else {}
    todo = [t for t in toks if t not in meta]
    if todo:
        for r in token_metadata(todo, S, ceps):
            meta[r[0]] = r + [str(S)]
        write_json(meta_ck, meta)
    # currencies whose 4 calls at S all returned success with empty data: check code at S; if none, call again at W1
    recall = {}
    rc_ck = os.path.join(STATE, "v4window2-recall.json")
    if os.path.exists(rc_ck):
        recall = json.load(open(rc_ck))
    for t in toks:
        r = meta[t]
        if r[-1] != str(S) or t in recall:
            continue
        empty = all(r[2 + 5 * j] == "1" and r[4 + 5 * j] == "0x" for j in range(4))
        if not empty:
            continue
        nocode, en = no_code_at(ceps, t, S)
        recall[t] = {"no_code_at_snapshot": nocode, "getcode_endpoint": en}
        if nocode:
            meta[t] = token_metadata([t], W1, ceps)[0] + [str(W1)]
        write_json(meta_ck, meta)
        write_json(rc_ck, recall)
    rows = [meta[t] for t in toks]
    atomic_write_rows_gz(os.path.join(OUT, "v4-window2-token-metadata.csv.gz"), rows, TOKEN_COLUMNS_W2)
    log("token rows", len(rows), "recalled at W1", sum(1 for v in recall.values() if v["no_code_at_snapshot"]))
    sidx = {"snapshot_block": S, "snapshot_block_source": "end of the valid V4 live test (02-v4-live-test), as specified for this task",
            "window": [W0, W1], "pools": len(pools), "pools_active_window2": len(active), "pools_initialized_window2": len(initialized),
            "pools_initialized_after_snapshot_block": len({r[4] for r in init_rows if int(r[0]) > S}),
            "keys": kstats, "currencies_total": len(cur), "currencies_native": int(NATIVE in cur),
            "currencies_already_in_token_metadata": len((cur - {NATIVE}) & existing), "tokens_new": len(toks),
            "tokens_called_at_snapshot_block": sum(1 for t in toks if meta[t][-1] == str(S)),
            "tokens_called_at_window_end_block": sum(1 for t in toks if meta[t][-1] == str(W1)),
            "token_recall_checks": recall,
            "files": {"state": "v4-window2-state-snapshot.csv.gz", "keys": "v4-window2-pool-keys.csv.gz", "tokens": "v4-window2-token-metadata.csv.gz"},
            "columns": {"state": STATE_COLUMNS_W2, "keys": KEY_COLUMNS, "tokens": TOKEN_COLUMNS_W2},
            "call_endpoints": [e.url for e in ceps], "completed_utc": now_utc()}
    write_json(os.path.join(OUT, "v4-window2-state-index.json"), sidx)
    return sidx, unresolved


# ------------------------------------------------------------------------------------------------------------- main
def main():
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(STATE, exist_ok=True)
    chunks = mk_chunks(W0, W1, CHUNK)
    if chunks[0][0] != W0 or chunks[-1][1] != W1 or any(chunks[i][1] + 1 != chunks[i + 1][0] for i in range(len(chunks) - 1)):
        raise RuntimeError("chunking error")
    head = ep("tenderly").act.call_retry("eth_blockNumber", [])
    fin = ep("tenderly").act.call_retry("eth_getBlockByNumber", ["finalized", False])
    log("window", W0, W1, "chunks", len(chunks), "head", int(head, 16), "finalized", int(fin["number"], 16))
    write_json(os.path.join(STATE, "v4window2-run.json"), {"window": [W0, W1], "snapshot_block": S, "chunks": len(chunks),
                                                           "head_at_start": int(head, 16), "finalized_at_start": int(fin["number"], 16),
                                                           "head_endpoint": EP_DEFS["tenderly"][0], "started_utc": now_utc()})
    if int(fin["number"], 16) < W1:
        raise RuntimeError("window end is not finalized yet")
    missing = chunks
    for rnd in range(1, 6):
        run_pool(primary_chunk, [c for c in chunks if not os.path.exists(mpath("meta", *c))])
        missing = [c for c in chunks if not os.path.exists(mpath("meta", *c))]
        log("primary round", rnd, "missing", len(missing))
        if not missing:
            break
        time.sleep(60 * rnd)
    bad = []
    if not missing:
        for rnd in range(1, 6):
            res = run_pool(xcheck_chunk, [c for c in chunks if not os.path.exists(mpath("xcheck", *c))])
            left = [c for c in chunks if not os.path.exists(mpath("xcheck", *c))]
            log("xcheck round", rnd, "unchecked", len(left))
            if not left:
                break
            time.sleep(60 * rnd)
        bad = [c for c in chunks if not os.path.exists(mpath("xcheck", *c)) or not json.load(open(mpath("xcheck", *c)))["identical"]]
    if missing or bad:
        write_json(os.path.join(STATE, "v4window2-gaps.json"), {"missing_chunks": missing, "xcheck_failed_or_different": bad, "written_utc": now_utc()})
        write_sentinel(NAME, False, "missing %d chunks, %d chunks not cross-checked or different; see collect/state/v4window2-gaps.json; "
                                    "rerun collect/v4window2_collector.py" % (len(missing), len(bad)))
        return 1
    metas = {c: json.load(open(mpath("meta", *c))) for c in chunks}
    xchecks = {c: json.load(open(mpath("xcheck", *c))) for c in chunks}
    census = census_checks(chunks)
    log("census checks", json.dumps(census)[:600])
    idx = assemble(chunks, metas, xchecks, census)
    log("logs assembled", idx["rows"])

    active, init_rows = set(), []
    for c in chunks:
        for r in read_rows_gz(cpath("act", *c)):
            active.add(r[5])
        init_rows += read_rows_gz(cpath("init", *c))
    initialized = {r[4] for r in init_rows}
    pools = sorted(active | initialized)
    log("pools", len(pools), "active", len(active), "initialized", len(initialized))
    sidx, unresolved = snapshot(pools, active, initialized, init_rows)
    if unresolved:
        write_sentinel(NAME, False, "logs + snapshot written but %d pool keys unresolved; see v4-window2-state-index.json" % len(unresolved))
        return 1
    write_sentinel(NAME, True, json.dumps({"logs_index": os.path.join(OUT, "v4-window2-parts.json"), "rows": idx["rows"],
                                           "window": [W0, W1], "chunks": len(chunks), "gaps": 0,
                                           "state_index": os.path.join(OUT, "v4-window2-state-index.json"), "snapshot_block": S,
                                           "pools": sidx["pools"], "tokens_new": sidx["tokens_new"], "completed_utc": now_utc()}))
    log(NAME, "DONE")
    return 0


def smoke():
    frm, to = W1 - 199, W1
    res = {}
    for name in ("tenderly", "mainnet.base.org"):
        act, init, bh = fetch_chunk(ep(name), frm, to)
        res[name] = (act, init, bh)
        log("smoke", name, frm, to, counts_of(act, init), "blocks with logs", len(bh))
    a, b = res["tenderly"], res["mainnet.base.org"]
    log("smoke compare act", a[0] == b[0], "init", a[1] == b[1], "hashes", a[2] == b[2])
    for k, cols in (("swap", SWAP_COLUMNS), ("modify", MODIFY_COLUMNS), ("donate", DONATE_COLUMNS)):
        ex = [r for r in a[0] if r[0] == k][:1]
        if ex:
            log("sample", k, dict(zip(cols, ex[0][1:])))
    if a[1]:
        log("sample init", dict(zip(INIT_COLUMNS, a[1][0])))
    pools = sorted({r[5] for r in a[0]} | {r[4] for r in a[1]})[:20]
    snap = snapshot_state(pools, S, call_endpoints())
    for pid in pools[:3]:
        log("state", pid, dict(zip(STATE_COLUMNS_W2[4:], snap[pid])))


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
        write_sentinel(NAME, False, "crashed: %r (rerun collect/v4window2_collector.py to resume)" % (e,))
        raise
