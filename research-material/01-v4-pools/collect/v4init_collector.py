#!/usr/bin/env python3
"""V4INIT: backfill every Uniswap V4 PoolManager Initialize event on Base, from the PoolManager deployment block to a pinned
end block (chain head at first launch, stored in state/v4init-pin.json so reruns resume against the same range).

Method
  * range split into 2,000-block chunks aligned at the deployment block; each chunk fetched with eth_getLogs
    (address = PoolManager, topic0 = Initialize) by a pool of endpoint workers (work-queue, any endpoint may take any chunk);
  * per-endpoint max range, bisection on range/size errors, responses with >= 5,000 logs re-fetched as halves;
  * each decoded log is checked: topic0, data length, block inside requested range, removed == false, and
    pool_id == keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks));
  * completed chunk -> work/v4init/c_<from>_<to>.csv.gz (atomic rename) = checkpoint; rerun skips existing chunks;
  * chunks failing on all endpoints are retried in later rounds; any still failing are written to state/v4init-gaps.json
    and the collector writes V4INIT.FAILED (no DONE, no final parts);
  * when all chunks exist: rows assembled in (block, log_index) order into ../initialize-part-NNNN.csv.gz (<= ~85 MB each,
    rotation only at chunk boundaries), index ../initialize-parts.json, then sentinel V4INIT.DONE.

Usage: python3 v4init_collector.py [--smoke FROM TO]   (smoke mode: fetch one range from every endpoint, compare, print)
"""
import collections
import json
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (INIT_COLUMNS, POOL_MANAGER, POOL_MANAGER_DEPLOY_BLOCK, T_INITIALIZE, Endpoint, PartWriter, RpcError,
                    atomic_write_rows_gz, decode_initialize, get_logs_range, log, now_utc, pool_id_of, read_rows_gz,
                    sha256_file, write_sentinel)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
WORK = os.path.join(HERE, "work", "v4init")
STATE = os.path.join(HERE, "state")
PIN = os.path.join(STATE, "v4init-pin.json")
GAPS = os.path.join(STATE, "v4init-gaps.json")
CHUNK = 2000
NAME = "V4INIT"


def endpoints():
    return [
        # (endpoint, worker threads)
        (Endpoint("mainnet.base.org", "https://mainnet.base.org", max_range=2000, inflight=2), 2),
        (Endpoint("tenderly", "https://gateway.tenderly.co/public/base", max_range=1000, inflight=2), 2),
        (Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", max_range=2000, inflight=1), 1),
        # base.drpc.org not used: at launch (2026-09-30 20:55Z) it answered getLogs only for ranges <= 10 blocks
        # ("You can make eth_getLogs requests with up to a 10 block range" / "ranges over 10000 blocks are not supported on free plan").
    ]


def decode_chunk(logs, frm, to):
    rows = []
    seen = set()
    for lg in logs:
        if lg["address"].lower() != POOL_MANAGER:
            raise RpcError("log from unexpected address %s" % lg["address"], kind="other")
        row = decode_initialize(lg)
        b = int(row[0])
        if not (frm <= b <= to):
            raise RpcError("log block %d outside chunk %d-%d" % (b, frm, to), kind="other")
        pid = pool_id_of(row[5], row[6], row[7], row[8], row[9])
        if pid != row[4]:
            raise RpcError("pool_id mismatch %s != %s" % (pid, row[4]), kind="other")
        k = (b, int(row[3]))
        if k in seen:
            continue  # identical log returned twice by bisection overlap (cannot happen with disjoint ranges; defensive)
        seen.add(k)
        rows.append(row)
    rows.sort(key=lambda r: (int(r[0]), int(r[3])))
    return rows


def chunk_path(frm, to):
    return os.path.join(WORK, "c_%d_%d.csv.gz" % (frm, to))


def load_pin(head_ep):
    os.makedirs(STATE, exist_ok=True)
    if os.path.exists(PIN):
        return json.load(open(PIN))
    head = int(head_ep.call_retry("eth_blockNumber", []), 16)
    pin = {"start_block": POOL_MANAGER_DEPLOY_BLOCK, "end_block": head, "end_block_source": "eth_blockNumber on %s at launch" % head_ep.url,
           "pinned_at_utc": now_utc(), "chunk_size": CHUNK, "topic0": T_INITIALIZE, "address": POOL_MANAGER}
    with open(PIN + ".tmp", "w") as f:
        json.dump(pin, f, indent=1)
    os.replace(PIN + ".tmp", PIN)
    return pin


def smoke(frm, to):
    res = {}
    for ep, _ in endpoints():
        t0 = time.time()
        try:
            logs = get_logs_range(ep, frm, to, [T_INITIALIZE])
            rows = decode_chunk(logs, frm, to)
            res[ep.name] = rows
            log("smoke", ep.name, "rows", len(rows), "secs", round(time.time() - t0, 1))
        except Exception as e:
            log("smoke", ep.name, "ERROR", repr(e)[:200])
    names = list(res)
    for n in names[1:]:
        log("smoke compare", names[0], "vs", n, "identical" if res[n] == res[names[0]] else "DIFFERENT")
    if names:
        for r in res[names[0]][:3]:
            log("sample row", dict(zip(INIT_COLUMNS, r)))


def main():
    os.makedirs(WORK, exist_ok=True)
    eps = endpoints()
    pin = load_pin(eps[0][0])
    start, end = pin["start_block"], pin["end_block"]
    chunks = []
    b = start
    while b <= end:
        chunks.append((b, min(end, b + CHUNK - 1)))
        b += CHUNK
    todo = collections.deque(c for c in chunks if not os.path.exists(chunk_path(*c)))
    log("pin", json.dumps(pin), "chunks total", len(chunks), "todo", len(todo))
    lock = threading.Lock()
    fails = collections.Counter()
    gaps = {}
    done_count = [len(chunks) - len(todo)]
    rows_count = [0]
    stop = threading.Event()
    MAX_FAILS = 12

    inflight = [0]

    def worker(ep):
        pause_until = 0.0
        while not stop.is_set():
            if time.time() < pause_until:
                time.sleep(2)
                continue
            with lock:
                if not todo:
                    if inflight[0] == 0:
                        return
                    c = None
                else:
                    c = todo.popleft()
                    inflight[0] += 1
            if c is None:
                time.sleep(2)  # other workers still hold chunks that may be requeued
                continue
            frm, to = c
            try:
                logs = get_logs_range(ep, frm, to, [T_INITIALIZE])
                rows = decode_chunk(logs, frm, to)
                atomic_write_rows_gz(chunk_path(frm, to), rows)
                with lock:
                    done_count[0] += 1
                    rows_count[0] += len(rows)
                    inflight[0] -= 1
            except Exception as e:  # noqa: BLE001 - every failure is recorded and the chunk requeued
                with lock:
                    inflight[0] -= 1
                    fails[c] += 1
                    n = fails[c]
                    if n >= MAX_FAILS:
                        gaps[c] = "%s: %s" % (ep.name, repr(e)[:300])
                    else:
                        todo.append(c)
                log("chunk fail", ep.name, frm, to, "fails", n, repr(e)[:200])
                if isinstance(e, RpcError) and e.kind == "range" and ep.min_bisect > 1:
                    pause_until = time.time() + 600
                else:
                    time.sleep(5)

    def progress():
        while not stop.is_set():
            time.sleep(60)
            with lock:
                log("progress chunks_done", done_count[0], "/", len(chunks), "rows_this_run", rows_count[0], "queue", len(todo), "gaps", len(gaps),
                    "stats", {ep.name: ep.stats for ep, _ in eps})

    for rnd in range(1, 7):
        threads = [threading.Thread(target=worker, args=(ep,), daemon=True) for ep, n in eps for _ in range(n)]
        pt = threading.Thread(target=progress, daemon=True)
        stop.clear()
        pt.start()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        stop.set()
        missing = [c for c in chunks if not os.path.exists(chunk_path(*c))]
        log("round", rnd, "finished; missing chunks", len(missing))
        if not missing:
            break
        # retry round: reset counters, wait, requeue
        with lock:
            for c in missing:
                fails[c] = 0
                gaps.pop(c, None)
            todo.extend(missing)
        time.sleep(300 * rnd)

    missing = [c for c in chunks if not os.path.exists(chunk_path(*c))]
    if missing:
        with open(GAPS, "w") as f:
            json.dump({"written_utc": now_utc(), "missing_chunks": missing, "last_errors": {"%d-%d" % c: v for c, v in gaps.items()}}, f, indent=1)
        p = write_sentinel(NAME, False, "V4INIT incomplete: %d chunks missing after 6 rounds; see %s; rerun collect/v4init_collector.py to resume\n" % (len(missing), GAPS))
        log("FAILED", p)
        return 1
    if os.path.exists(GAPS):
        os.replace(GAPS, GAPS + ".resolved")

    # assemble
    log("assembling parts")
    for fn in os.listdir(OUT):
        if fn.startswith("initialize-part-") and (fn.endswith(".csv.gz") or fn.endswith(".tmp")):
            os.remove(os.path.join(OUT, fn))
    pw = PartWriter(OUT, "initialize", INIT_COLUMNS, max_bytes=85_000_000)
    total = 0
    prev_key = (-1, -1)
    for (frm, to) in chunks:
        rows = read_rows_gz(chunk_path(frm, to))
        for r in rows:
            k = (int(r[0]), int(r[3]))
            if k <= prev_key:
                raise RuntimeError("ordering violation at %s" % (k,))
            prev_key = k
        pw.write_block_range(rows, frm, to)
        total += len(rows)
        pw.maybe_rotate()
    parts = pw.close()
    # verify parts by re-reading
    vtotal = 0
    for p in parts:
        n = len(read_rows_gz(os.path.join(OUT, p["file"]))) - 1
        if n != p["rows"]:
            raise RuntimeError("part row count mismatch %s %d %d" % (p["file"], n, p["rows"]))
        if p["bytes"] > 90_000_000:
            raise RuntimeError("part too large %s" % p["file"])
        vtotal += n
    assert vtotal == total
    idx = {"dataset": "Uniswap V4 PoolManager Initialize events, Base (chain 8453)", "pool_manager": POOL_MANAGER, "topic0": T_INITIALIZE,
           "block_from": start, "block_to": end, "pin": pin, "total_rows": total, "columns": INIT_COLUMNS, "parts": parts,
           "sort": "block_number, log_index ascending", "assembled_utc": now_utc(), "chunks": len(chunks)}
    ip = os.path.join(OUT, "initialize-parts.json")
    with open(ip + ".tmp", "w") as f:
        json.dump(idx, f, indent=1)
    os.replace(ip + ".tmp", ip)
    p = write_sentinel(NAME, True, json.dumps({"index": ip, "total_rows": total, "parts": len(parts), "block_from": start, "block_to": end,
                                                "completed_utc": now_utc()}))
    log("DONE", p, "rows", total, "parts", len(parts))
    return 0


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "--smoke":
        smoke(int(sys.argv[2]), int(sys.argv[3]))
    else:
        try:
            sys.exit(main())
        except SystemExit:
            raise
        except BaseException as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            write_sentinel(NAME, False, "V4INIT crashed: %r (rerun collect/v4init_collector.py to resume)" % (e,))
            raise
