#!/usr/bin/env python3
"""
Fills the "Counts" section and the Status line of ../MANIFEST.md from the *.meta.json files, the output files on disk,
collect/gaps.jsonl and the sentinels. Descriptive metadata only. Re-runnable; replaces the text between the COUNTS markers.
Usage: python3 fill_manifest.py
"""
import glob, json, os, datetime, re

D = "/home/user/dapparb/research-material/07-other-chains-engine"
S = "/home/user/dapparb/research-material/.sentinels"
M = os.path.join(D, "MANIFEST.md")
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

sent_names = ["SCANS", "ENGINE_DETECT_ARBITRUM", "ENGINE_DETECT_MAINNET", "ENGINE_LIVE_ARBITRUM", "ENGINE_LIVE_MAINNET"]
sent = {}
for n in sent_names:
    st = "missing"
    for suf in ("DONE", "FAILED"):
        p = os.path.join(S, f"{n}.{suf}")
        if os.path.exists(p):
            st = suf
    sent[n] = st

rows = []
for meta_path in sorted(glob.glob(os.path.join(D, "scans", "*", "*.meta.json")) + glob.glob(os.path.join(D, "engine-detect", "*", "*.meta.json"))):
    m = json.load(open(meta_path))
    rel_dir = os.path.relpath(os.path.dirname(meta_path), D)
    w = m.get("window") or {}
    sr = m.get("searcher_ready") or {}
    lp = m.get("live_pools") or {}
    pools = lp.get("live", sr.get("pools"))
    kind = "engine" if rel_dir.startswith("engine") else "scan"
    if kind == "scan":
        start, end = m.get("first_block_scanned_utc"), m.get("last_block_scanned_utc")
        b0, b1 = m.get("log_block_scanned_first_block"), m.get("log_block_scanned_last_block")
        nlines = m.get("log_block_scanned_lines")
    else:
        start, end = w.get("ready_utc"), w.get("sigint_utc")
        b0, b1 = m.get("jsonl_first_block"), m.get("jsonl_last_block")
        nlines = m.get("log_heartbeat_lines")
    rows.append({
        "dir": rel_dir, "name": m["name"], "kind": kind, "files": ", ".join(m.get("jsonl_files", [])),
        "rows": m.get("jsonl_rows"), "announced": m.get("log_rows_announced_by_block_scanned_lines"), "bad": m.get("jsonl_unparseable_lines"),
        "lines": nlines, "b0": b0, "b1": b1, "start": start, "end": end, "pools": pools,
        "exit": w.get("exit"), "capped": w.get("time_capped"), "summary": m.get("summary_present"),
        "warn": m.get("warn_lines"), "err": m.get("error_lines"),
    })

sizes = []
for p in sorted(glob.glob(os.path.join(D, "scans", "*", "*")) + glob.glob(os.path.join(D, "engine-detect", "*", "*"))):
    sizes.append((os.path.relpath(p, D), os.path.getsize(p)))

gaps = []
gp = os.path.join(D, "collect", "gaps.jsonl")
if os.path.exists(gp):
    gaps = [l.strip() for l in open(gp) if l.strip()]

out = [f"Filled by `collect/fill_manifest.py` at {now}.", "", "Sentinels: " + ", ".join(f"`{k}.{v}`" if v != "missing" else f"`{k}` missing" for k, v in sent.items()), ""]
out.append("| Dir / run | JSONL files | JSONL rows | rows announced in log (scan) | unparseable lines | block-scanned / heartbeat lines | first block | last block | window start (UTC) | window end (UTC) | pools after depth filter | exit | time-capped | SCAN SUMMARY present | warn / error log lines |")
out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    out.append(f"| {r['dir']}/{r['name']} | {r['files']} | {r['rows']} | {r['announced'] if r['announced'] is not None else '-'} | {r['bad']} | {r['lines']} | {r['b0']} | {r['b1']} | {r['start']} | {r['end']} | {r['pools']} | {r['exit'] if r['exit'] is not None else '-'} | {r['capped'] if r['capped'] is not None else '-'} | {r['summary'] if r['kind']=='scan' else '-'} | {r['warn']} / {r['err']} |")
out += ["", "Scan windows: first/last `block scanned` log time. Engine windows: `searcher ready` to SIGINT. Engine block range: first/last block among written rows (empty if no row was written).", ""]
out.append("File sizes (bytes):")
out.append("")
out += [f"- `{p}`: {s}" for p, s in sizes]
out += ["", f"`collect/gaps.jsonl`: {len(gaps)} line(s)" + (":" if gaps else ".")]
out += [f"    {g}" for g in gaps]
block = "\n".join(out)

txt = open(M).read()
txt = re.sub(r"<!-- COUNTS:BEGIN -->.*?<!-- COUNTS:END -->", "<!-- COUNTS:BEGIN -->\n" + block + "\n<!-- COUNTS:END -->", txt, flags=re.S)
pending = [k for k in ("SCANS", "ENGINE_DETECT_ARBITRUM", "ENGINE_DETECT_MAINNET") if sent[k] == "missing"]
failed = [k for k in ("SCANS", "ENGINE_DETECT_ARBITRUM", "ENGINE_DETECT_MAINNET") if sent[k] == "FAILED"]
if pending:
    status = f"Status: IN PROGRESS (counts last refreshed {now}; waiting for sentinels: {', '.join(pending)})."
elif failed:
    status = f"Status: COMPLETE WITH FAILURES ({now}): {', '.join(k + '.FAILED' for k in failed)}; see the sentinel files and collect/gaps.jsonl. ENGINE_LIVE_* are FAILED by design (blocked, see below)."
else:
    status = f"Status: COMPLETE ({now}). All collectors finished; ENGINE_LIVE_ARBITRUM/MAINNET are FAILED by design (simulation blocked without a code change, see below)."
txt = re.sub(r"^Status: .*?(?=\n\n)", status, txt, count=1, flags=re.S | re.M)
open(M, "w").write(txt)
print(status)
