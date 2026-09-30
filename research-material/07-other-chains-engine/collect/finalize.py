#!/usr/bin/env python3
"""
Packs one finished scan/engine run into the output directory. No analysis: it only copies, compresses, splits,
and extracts log lines into CSV columns (lossless; marked "derived" in MANIFEST.md).

Outputs in --out-dir:
  <name>.jsonl.gz or <name>-part-NNNN.jsonl.gz   raw rows written by the tool (--out file), unchanged, split so
                                                  each gzip file stays <= 85 MB
  <name>.log.gz                                   the tool's raw stdout/stderr (pino JSON lines + plain-text summary)
  <name>.blocks.csv.gz      (scan runs)            derived: one row per "block scanned" log line
  <name>.heartbeats.csv.gz  (engine runs)          derived: one row per "heartbeat" log line
  <name>.meta.json                                 descriptive metadata: row counts, first/last block, times, exit
"""
import argparse, csv, gzip, io, json, os, sys, datetime

ap = argparse.ArgumentParser()
ap.add_argument("--jsonl", required=True)
ap.add_argument("--log", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--name", required=True)
ap.add_argument("--window", default=None)
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
LIMIT = 85 * 1024 * 1024


def utc(ms):
    return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"


# ---- raw JSONL -> gz parts ----
for f in os.listdir(a.out_dir):  # remove parts of an earlier finalize of the same run name
    if f.startswith(a.name + "-part-") or f == a.name + ".jsonl.gz":
        os.remove(os.path.join(a.out_dir, f))
parts, rows, bad_lines = [], 0, 0
first_block = last_block = None
blocks_seen = set()
if os.path.exists(a.jsonl):
    part_idx, raw, gz = 0, None, None

    def open_part(i):
        p = os.path.join(a.out_dir, f"{a.name}-part-{i:04d}.jsonl.gz")
        r = open(p, "wb")
        return p, r, gzip.GzipFile(fileobj=r, mode="wb", compresslevel=6)

    path, raw, gz = open_part(1)
    parts.append(path)
    part_idx = 1
    with open(a.jsonl, "rb") as fin:
        for line in fin:
            if raw.tell() > LIMIT:
                gz.close(); raw.close()
                part_idx += 1
                path, raw, gz = open_part(part_idx)
                parts.append(path)
            gz.write(line)
            rows += 1
            try:
                b = json.loads(line).get("block")
                if isinstance(b, int):
                    blocks_seen.add(b)
                    first_block = b if first_block is None else min(first_block, b)
                    last_block = b if last_block is None else max(last_block, b)
            except Exception:
                bad_lines += 1
    gz.close(); raw.close()
    if len(parts) == 1:  # single part: drop the -part- suffix
        final = os.path.join(a.out_dir, f"{a.name}.jsonl.gz")
        os.replace(parts[0], final)
        parts = [final]

# ---- raw log -> gz copy; derived CSVs from log lines ----
with open(a.log, "rb") as fin, gzip.open(os.path.join(a.out_dir, f"{a.name}.log.gz"), "wb") as fout:
    fout.write(fin.read())

BLOCK_COLS = ["time_ms", "time_utc", "block", "gross", "net", "sumNetUsd", "gasPriceGwei", "txCostUsd", "syncMs", "searchMs"]
blocks_rows, hb_rows, hb_keys = [], [], []
events = {"searcher_ready": None, "live_pools": None, "first_block_scanned_ms": None, "last_block_scanned_ms": None,
          "exit_line": None, "signal_line": None, "summary_present": False, "warn_lines": 0, "error_lines": 0}
with open(a.log, "r", errors="replace") as fin:
    for line in fin:
        s = line.strip()
        if s.startswith("exit=") or s.startswith("# exit"):
            events["exit_line"] = s
        if "[exit-flush]" in s:
            events["signal_line"] = s
        if "SCAN SUMMARY" in s:
            events["summary_present"] = True
        if not s.startswith("{"):
            continue
        try:
            j = json.loads(s)
        except Exception:
            continue
        lvl = j.get("level")
        if lvl == 40:
            events["warn_lines"] += 1
        if lvl is not None and lvl >= 50:
            events["error_lines"] += 1
        m = j.get("msg")
        if m == "block scanned":
            blocks_rows.append([j.get("time"), utc(j["time"]), j.get("block"), j.get("gross"), j.get("net"), j.get("sumNetUsd"),
                                j.get("gasPriceGwei"), j.get("txCostUsd"), j.get("syncMs"), j.get("searchMs")])
            if events["first_block_scanned_ms"] is None:
                events["first_block_scanned_ms"] = j["time"]
            events["last_block_scanned_ms"] = j["time"]
        elif m == "heartbeat":
            d = {k: v for k, v in j.items() if k not in ("level", "pid", "hostname", "msg")}
            for k in d:
                if k not in hb_keys:
                    hb_keys.append(k)
            hb_rows.append(d)
        elif m == "searcher ready":
            events["searcher_ready"] = {k: v for k, v in j.items() if k not in ("level", "pid", "hostname")}
        elif m == "live pools":
            events["live_pools"] = {k: v for k, v in j.items() if k not in ("level", "pid", "hostname")}

if blocks_rows:
    with gzip.open(os.path.join(a.out_dir, f"{a.name}.blocks.csv.gz"), "wt", newline="") as f:
        w = csv.writer(f)
        w.writerow(BLOCK_COLS)
        w.writerows(blocks_rows)
if hb_rows:
    with gzip.open(os.path.join(a.out_dir, f"{a.name}.heartbeats.csv.gz"), "wt", newline="") as f:
        w = csv.writer(f)
        cols = ["time_utc"] + hb_keys
        w.writerow(cols)
        for d in hb_rows:
            w.writerow([utc(d["time"]) if "time" in d else ""] + [d.get(k, "") for k in hb_keys])

meta = {
    "name": a.name,
    "finalized_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "jsonl_files": [os.path.basename(p) for p in parts],
    "jsonl_rows": rows,
    "jsonl_unparseable_lines": bad_lines,
    "jsonl_distinct_blocks": len(blocks_seen),
    "jsonl_first_block": first_block,
    "jsonl_last_block": last_block,
    "log_block_scanned_lines": len(blocks_rows),
    "log_block_scanned_first_block": blocks_rows[0][2] if blocks_rows else None,
    "log_block_scanned_last_block": blocks_rows[-1][2] if blocks_rows else None,
    "log_rows_announced_by_block_scanned_lines": sum((r[3] or 0) for r in blocks_rows) if blocks_rows else None,
    "log_heartbeat_lines": len(hb_rows),
    "first_block_scanned_utc": utc(events["first_block_scanned_ms"]) if events["first_block_scanned_ms"] else None,
    "last_block_scanned_utc": utc(events["last_block_scanned_ms"]) if events["last_block_scanned_ms"] else None,
    **{k: v for k, v in events.items() if k not in ("first_block_scanned_ms", "last_block_scanned_ms")},
}
if a.window and os.path.exists(a.window):
    meta["window"] = json.load(open(a.window))
with open(os.path.join(a.out_dir, f"{a.name}.meta.json"), "w") as f:
    json.dump(meta, f, indent=1)
print(json.dumps({k: meta[k] for k in ("name", "jsonl_rows", "jsonl_distinct_blocks", "log_block_scanned_lines", "log_heartbeat_lines")}))
