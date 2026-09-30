#!/usr/bin/env python3
"""Helper for run_v4_live.sh (V4LIVE). Collect-only: it records times, blocks and verbatim log lines; it does not
evaluate the engine output.

Subcommands:
  head                         print {"block", "endpoint", "at_utc"} (eth_blockNumber, first endpoint that answers)
  engines [--exclude-pgid N] [--base-only]
                               print a JSON list of running engine processes (cmdline matches node ... src/main.ts),
                               excluding process group N (our own engine); --base-only keeps those whose --chain is
                               base (or absent, the engine default)
  finalize                     write ../run-times.json from collect/state/run.kv (key=value lines written by the
                               shell script; last value per key wins) and the engine log ../live-v4.log
"""
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
LOG = os.path.join(OUT, "live-v4.log")
KV = os.path.join(HERE, "state", "run.kv")
RT = os.path.join(OUT, "run-times.json")
RPC_HEAD = ["https://base-rpc.publicnode.com", "https://mainnet.base.org", "https://base.drpc.org"]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
for _v in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
    if not os.environ.get(_v) and os.path.exists("/root/.ccr/ca-bundle.crt"):
        os.environ[_v] = "/root/.ccr/ca-bundle.crt"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def ms_to_utc(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def head():
    import ssl
    ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE")) if os.environ.get("SSL_CERT_FILE") else None
    errs = []
    for u in RPC_HEAD:
        for attempt in range(2):
            try:
                req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                                             headers={"content-type": "application/json", "user-agent": UA})
                with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
                    return {"block": int(json.loads(r.read())["result"], 16), "endpoint": u, "at_utc": now()}
            except Exception as e:  # noqa
                errs.append("%s: %s" % (u, str(e)[:120]))
                time.sleep(2)
    return {"block": None, "endpoint": None, "at_utc": now(), "errors": errs}


def engines(exclude_pgid=None, base_only=False):
    out = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cmd = open("/proc/%s/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode(errors="replace").strip()
            if not re.search(r"\bnode\b.*src/main\.ts", cmd):
                continue
            stat = open("/proc/%s/stat" % pid).read()
            pgid = int(stat.rsplit(")", 1)[1].split()[2])
        except Exception:  # noqa
            continue
        if exclude_pgid is not None and pgid == exclude_pgid:
            continue
        m = re.search(r"--chain\s+(\S+)", cmd)
        chain = m.group(1) if m else "base"
        if base_only and chain != "base":
            continue
        out.append({"pid": int(pid), "pgid": pgid, "chain": chain, "cmd": cmd[:400]})
    return out


def read_kv():
    kv = {}
    try:
        for line in open(KV):
            line = line.rstrip("\n")
            if "=" in line:
                k, v = line.split("=", 1)
                kv[k] = v
    except FileNotFoundError:
        pass
    return kv


def jload(s):
    try:
        return json.loads(s)
    except Exception:  # noqa
        return s


def finalize():
    kv = read_kv()
    recs = []  # (line_no, verbatim, obj)
    non_json = 0
    try:
        with open(LOG, errors="replace") as f:
            for i, line in enumerate(f, 1):
                line = line.rstrip("\n")
                if not line.startswith("{"):
                    if line.strip():
                        non_json += 1
                    continue
                try:
                    recs.append((i, line, json.loads(line)))
                except ValueError:
                    non_json += 1
    except FileNotFoundError:
        pass

    def first(msg):
        for i, line, o in recs:
            if o.get("msg") == msg:
                return i, line, o
        return None

    ready = first("searcher ready")
    v4 = first("v4 pools loaded from file")
    shut = first("shutting down")
    ready_ms = ready[2].get("time") if ready else None
    blocks = [(i, o["block"], o.get("msg"), o.get("time")) for i, _, o in recs
              if isinstance(o.get("block"), (int, float)) and ready_ms is not None and o.get("time", 0) >= ready_ms]
    hb = [(i, line, o) for i, line, o in recs if o.get("msg") == "heartbeat"]
    msg_counts = {}
    for _, _, o in recs:
        m = o.get("msg", "")
        msg_counts[m] = msg_counts.get(m, 0) + 1
    errors = [line for _, line, o in recs if isinstance(o.get("level"), int) and o["level"] >= 50]
    rt = {
        "name": "V4LIVE",
        "status": kv.get("status", "UNKNOWN"),
        "reason": kv.get("reason", ""),
        "written_utc": now(),
        "command": kv.get("cmd"),
        "cwd": kv.get("cwd"),
        "env": kv.get("env"),
        "v4_pools_spec": kv.get("spec"),
        "run_seconds_after_ready": int(kv["run_seconds"]) if kv.get("run_seconds") else None,
        "script_start_utc": kv.get("script_start_utc"),
        "v4init_done_seen_utc": kv.get("v4init_done_seen_utc"),
        "topup": {"status": kv.get("topup_status"), "exit_code": kv.get("topup_exit"), "index": jload(kv.get("topup_index", "null")),
                  "started_utc": kv.get("topup_start_utc"), "finished_utc": kv.get("topup_end_utc")},
        "other_engines": {"waited_seconds": int(kv["other_engines_wait_s"]) if kv.get("other_engines_wait_s") else None,
                          "at_first_check": jload(kv.get("other_engines_first", "null")),
                          "at_launch": jload(kv.get("other_engines_at_launch", "null")),
                          "samples_during_run_file": "collect/state/concurrent-engines.jsonl"},
        "launch_utc": kv.get("launch_utc"),
        "engine_pid": int(kv["engine_pid"]) if kv.get("engine_pid") else None,
        "engine_pgid": int(kv["engine_pgid"]) if kv.get("engine_pgid") else None,
        "head_at_launch": jload(kv.get("head_at_launch", "null")),
        "ready_detected_utc": kv.get("ready_detected_utc"),
        "ready_log_utc": ms_to_utc(ready_ms) if ready_ms else None,
        "head_at_ready": jload(kv.get("head_at_ready", "null")),
        "planned_stop_utc": kv.get("planned_stop_utc"),
        "stop_sigint_utc": kv.get("stop_sigint_utc"),
        "stop_sigterm_utc": kv.get("stop_sigterm_utc"),
        "stop_sigkill_utc": kv.get("stop_sigkill_utc"),
        "engine_exit_utc": kv.get("engine_exit_utc"),
        "engine_exit_code": int(kv["engine_exit_code"]) if kv.get("engine_exit_code", "").lstrip("-").isdigit() else kv.get("engine_exit_code"),
        "head_at_stop": jload(kv.get("head_at_stop", "null")),
        "first_processed_block_in_log": blocks[0][1] if blocks else None,
        "last_processed_block_in_log": blocks[-1][1] if blocks else None,
        "min_block_in_log_after_ready": min(b[1] for b in blocks) if blocks else None,
        "max_block_in_log_after_ready": max(b[1] for b in blocks) if blocks else None,
        "block_fields_note": "blocks come from log records that carry a `block` field (heartbeat every 10 ticks, opportunity/simulation records) written at or after the searcher-ready record; the first ticks after ready are not individually logged by the engine, so head_at_ready / head_at_stop (eth_blockNumber by this script) are recorded as well",
        "searcher_ready_line_verbatim": ready[1] if ready else None,
        "v4_pools_loaded_from_file_line_verbatim": v4[1] if v4 else None,
        "shutting_down_line_verbatim": shut[1] if shut else None,
        "last_heartbeat_line_verbatim": hb[-1][1] if hb else None,
        "log_records": len(recs),
        "log_non_json_lines": non_json,
        "log_record_counts_by_msg": msg_counts,
        "log_error_records_first5_verbatim": errors[:5],
        "log_error_records": len(errors),
        "outputs": {"engine_log": "live-v4.log", "engine_out_jsonl": "live-v4.jsonl"},
    }
    tmp = RT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(rt, f, indent=1)
    os.replace(tmp, RT)
    print(json.dumps({k: rt[k] for k in ("status", "reason", "first_processed_block_in_log", "last_processed_block_in_log", "log_records")}))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "head":
        print(json.dumps(head()))
    elif cmd == "engines":
        ex = int(sys.argv[sys.argv.index("--exclude-pgid") + 1]) if "--exclude-pgid" in sys.argv else None
        print(json.dumps(engines(ex, "--base-only" in sys.argv)))
    elif cmd == "finalize":
        finalize()
    else:
        print(__doc__)
        sys.exit(1)
