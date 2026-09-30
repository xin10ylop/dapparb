#!/usr/bin/env python3
"""Detached launcher for the shallow-pool live engine run (SHALLOW_LIVE).

Runs, from /home/user/dapparb/bot:
  npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 \
      --min-depth-eth 0.001 --min-profit-usd 0.01 --top 6 --out <OUT>/live-shallow.jsonl
with stdout+stderr -> <OUT>/live-shallow.log (env LOG_JSON=1: one pino JSON object per line, `time` = epoch ms).

Once the log contains 'searcher ready' it lets the engine run exactly RUN_SECONDS (1200 s) more, then stops it
by process group (SIGINT; SIGTERM after 30 s; SIGKILL after a further 30 s), writes <OUT>/run-times.json and the
sentinel SHALLOW_LIVE.DONE (or SHALLOW_LIVE.FAILED with the reason, e.g. early exit / startup failure).
If startup fails at --min-depth-eth 0.001 for a resource reason (heap OOM, ENOMEM, killed by signal) it retries
exactly once at 0.01, and documents that in run-times.json.

Not resumable by design: a live window cannot be replayed. If run-times.json already has status DONE this script
exits without doing anything; delete run-times.json + sentinels to run a fresh window.
"""
import json, os, re, signal, subprocess, sys, time, urllib.request
from datetime import datetime, timezone

OUT = "/home/user/dapparb/research-material/04-shallow-pools"
BOT = "/home/user/dapparb/bot"
SENT = "/home/user/dapparb/research-material/.sentinels"
NAME = "SHALLOW_LIVE"
RUN_SECONDS = int(os.environ.get("RUN_SECONDS", "1200"))
READY_TIMEOUT = int(os.environ.get("READY_TIMEOUT", str(90 * 60)))
LOG = os.path.join(OUT, "live-shallow.log")
JSONL = os.path.join(OUT, "live-shallow.jsonl")
RT = os.path.join(OUT, "run-times.json")
STATE = os.path.join(OUT, "collect", "run_live_shallow.state.json")
RPC_HEAD = ["https://base-rpc.publicnode.com", "https://base.drpc.org", "https://mainnet.base.org"]
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def say(*a):
    print(now(), *a, flush=True)


def head_block():
    for u in RPC_HEAD:
        try:
            req = urllib.request.Request(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}).encode(),
                                         headers={"content-type": "application/json", "user-agent": "Mozilla/5.0 (X11; Linux x86_64) research-collector"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return {"block": int(json.loads(r.read())["result"], 16), "endpoint": u, "at_utc": now()}
        except Exception as e:  # noqa
            say("head_block failed", u, str(e)[:120])
    return None


def save_state(st):
    tmp = STATE + ".tmp"
    json.dump(st, open(tmp, "w"), indent=1)
    os.replace(tmp, STATE)


def sentinel(ok, reason=""):
    os.makedirs(SENT, exist_ok=True)
    for s in ("DONE", "FAILED"):
        p = os.path.join(SENT, f"{NAME}.{s}")
        if os.path.exists(p):
            os.remove(p)
    with open(os.path.join(SENT, f"{NAME}.{'DONE' if ok else 'FAILED'}"), "w") as f:
        f.write((reason or "ok") + "\n" + now() + "\n")


def read_log_lines():
    try:
        with open(LOG, "r", errors="replace") as f:
            return f.read().splitlines()
    except FileNotFoundError:
        return []


def parse_json_lines(lines):
    out = []
    for ln in lines:
        ln = ANSI.sub("", ln).strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def find_ready(lines):
    for ln in lines:
        if "searcher ready" in ln:
            return ANSI.sub("", ln)
    return None


RESOURCE_PAT = re.compile(r"heap out of memory|JavaScript heap|ENOMEM|Allocation failed|out of memory|Killed|ERR_OUT_OF_RANGE: .*buffer|Invalid string length|Maximum call stack", re.I)


def launch(min_depth, attempt):
    cmd = ["npx", "tsx", "src/main.ts", "--chain", "base", "--mode", "dry", "--source", "logs", "--universe", "all",
           "--max-per-factory", "6000", "--min-depth-eth", str(min_depth), "--min-profit-usd", "0.01", "--top", "6", "--out", JSONL]
    env = dict(os.environ)
    env["LOG_JSON"] = "1"
    mode = "a" if attempt > 1 else "w"
    logf = open(LOG, mode)
    if attempt > 1:
        logf.write(json.dumps({"launcher": "retry", "attempt": attempt, "min_depth_eth": min_depth, "at_utc": now()}) + "\n")
        logf.flush()
    p = subprocess.Popen(cmd, cwd=BOT, stdout=logf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, env=env, start_new_session=True)
    return p, cmd, logf


def stop(p):
    pgid = os.getpgid(p.pid)
    t = now()
    os.killpg(pgid, signal.SIGINT)
    sig = "SIGINT"
    try:
        p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        os.killpg(pgid, signal.SIGTERM)
        sig = "SIGINT,SIGTERM"
        try:
            p.wait(timeout=30)
        except subprocess.TimeoutExpired:
            os.killpg(pgid, signal.SIGKILL)
            sig = "SIGINT,SIGTERM,SIGKILL"
            p.wait(timeout=30)
    # make sure nothing of the group survives (tsx child)
    try:
        os.killpg(pgid, 0)
        time.sleep(2)
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    return t, sig


def blocks_from(objs, jsonl_path):
    hb = [o for o in objs if o.get("msg") == "heartbeat" and "block" in o]
    res = {"heartbeat_count": len(hb),
           "first_heartbeat_block": hb[0]["block"] if hb else None,
           "last_heartbeat_block": hb[-1]["block"] if hb else None,
           "first_heartbeat_ticks": hb[0].get("ticks") if hb else None,
           "last_heartbeat_ticks": hb[-1].get("ticks") if hb else None}
    blocks = []
    for o in objs:
        if isinstance(o.get("block"), int) and o.get("msg") in ("heartbeat", "simulation reverted", "simulated net below threshold", "DRY-RUN: would send", "opportunity (no contract configured; not simulated)"):
            blocks.append(o["block"])
    res["first_block_in_log_records"] = min(blocks) if blocks else None
    res["last_block_in_log_records"] = max(blocks) if blocks else None
    jb = []
    try:
        with open(jsonl_path) as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                    if isinstance(r.get("block"), int) and "route" in r:
                        jb.append(r["block"])
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    res["jsonl_candidate_rows"] = len(jb)
    res["first_block_in_jsonl"] = min(jb) if jb else None
    res["last_block_in_jsonl"] = max(jb) if jb else None
    return res


def main():
    if os.path.exists(RT):
        try:
            if json.load(open(RT)).get("status") == "DONE":
                say("run-times.json already DONE; nothing to do")
                return
        except Exception:
            pass
    rt = {"name": NAME, "status": "RUNNING", "run_seconds_after_ready": RUN_SECONDS, "attempts": [], "log_format": "LOG_JSON=1 (pino JSON lines, time = epoch ms)",
          "cwd": BOT, "out_jsonl": JSONL, "log": LOG, "launcher_pid": os.getpid()}
    depths = [0.001, 0.01]
    for attempt, depth in enumerate(depths, start=1):
        a = {"attempt": attempt, "min_depth_eth": depth, "launch_utc": now(), "head_at_launch": head_block()}
        p, cmd, logf = launch(depth, attempt)
        a["cmd"] = "cd " + BOT + " && LOG_JSON=1 " + " ".join(cmd)
        a["engine_pid"] = p.pid
        rt["attempts"].append(a)
        save_state(rt)
        say("launched", p.pid, a["cmd"])
        t0 = time.time()
        ready_line = None
        while True:
            lines = read_log_lines()
            ready_line = find_ready(lines)
            if ready_line:
                break
            if p.poll() is not None:
                break
            if time.time() - t0 > READY_TIMEOUT:
                break
            time.sleep(1)
        if ready_line:
            a["ready_detected_utc"] = now()
            a["ready_detected_epoch"] = time.time()
            a["searcher_ready_line_verbatim"] = ready_line
            try:
                o = json.loads(ready_line)
                a["ready_log_utc"] = datetime.fromtimestamp(o["time"] / 1000, timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
                a["searcher_ready_counts"] = {k: o.get(k) for k in ("tokens", "pools", "cycles", "minDepthEth", "source", "mode", "contract", "codeOverride")}
            except Exception as e:
                a["ready_parse_error"] = str(e)
            a["head_at_ready"] = head_block()
            save_state(rt)
            say("searcher ready; running", RUN_SECONDS, "s")
            deadline = a["ready_detected_epoch"] + RUN_SECONDS
            early = None
            while time.time() < deadline:
                if p.poll() is not None:
                    early = p.returncode
                    break
                time.sleep(min(2, max(0.05, deadline - time.time())))
            if early is not None:
                a["exit_utc"] = now()
                a["exit_code"] = early
                a["early_exit_seconds_after_ready"] = round(time.time() - a["ready_detected_epoch"], 1)
                a["log_tail"] = [ANSI.sub("", l) for l in read_log_lines()[-40:]]
                rt["status"] = "FAILED"
                rt["reason"] = f"engine exited early (code {early}) {a['early_exit_seconds_after_ready']} s after searcher ready"
                break
            a["head_at_stop"] = head_block()
            a["stop_utc"], a["stop_signals"] = stop(p)
            a["exit_utc"] = now()
            a["exit_code"] = p.returncode
            a["seconds_ready_to_stop"] = round(time.time() - a["ready_detected_epoch"], 1)
            rt["status"] = "DONE"
            break
        # no ready line
        if p.poll() is None:
            a["stop_utc"], a["stop_signals"] = stop(p)
            a["exit_code"] = p.returncode
            rt["status"] = "FAILED"
            rt["reason"] = f"no 'searcher ready' within {READY_TIMEOUT} s"
            a["log_tail"] = [ANSI.sub("", l) for l in read_log_lines()[-40:]]
            break
        a["exit_utc"] = now()
        a["exit_code"] = p.returncode
        tail = [ANSI.sub("", l) for l in read_log_lines()[-60:]]
        a["log_tail"] = tail
        resource = bool(RESOURCE_PAT.search("\n".join(tail))) or (p.returncode is not None and p.returncode < 0) or p.returncode in (134, 137)
        a["startup_failure_resource_related"] = resource
        save_state(rt)
        if resource and attempt == 1:
            say("startup failed for a resource reason; retrying once at 0.01")
            rt["retry_reason"] = "startup at --min-depth-eth 0.001 failed for a resource reason (see attempts[0].log_tail)"
            continue
        rt["status"] = "FAILED"
        rt["reason"] = f"engine exited before 'searcher ready' (code {p.returncode}, resource_related={resource})"
        break
    # blocks
    objs = parse_json_lines(read_log_lines())
    rt["blocks"] = blocks_from(objs, JSONL)
    sd = [o for o in objs if o.get("msg") == "shutting down"]
    rt["shutdown_stats_line"] = sd[-1] if sd else None
    rt["finished_utc"] = now()
    last = rt["attempts"][-1]
    rt["launch_utc"] = rt["attempts"][0]["launch_utc"]
    rt["ready_utc"] = last.get("ready_log_utc") or last.get("ready_detected_utc")
    rt["stop_utc"] = last.get("stop_utc")
    rt["searcher_ready_line_verbatim"] = last.get("searcher_ready_line_verbatim")
    tmp = RT + ".tmp"
    json.dump(rt, open(tmp, "w"), indent=1)
    os.replace(tmp, RT)
    save_state(rt)
    sentinel(rt["status"] == "DONE", rt.get("reason", ""))
    say("finished", rt["status"], rt.get("reason", ""))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sentinel(False, "launcher crashed: " + repr(e)[:500])
        raise
