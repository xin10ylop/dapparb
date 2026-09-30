#!/usr/bin/env bash
# V4LIVE: the reference 20-minute live test (docs/ANALYSIS.md section 2.6 command) with every Uniswap V4 pool listed
# from PoolManager Initialize events (--v4-pools) instead of the GeckoTerminal top listings. Collect-only: raw engine
# output, no analyzer.
#
# Steps
#  1. Wait for /home/user/dapparb/research-material/.sentinels/V4INIT.DONE (poll 60 s; after 6 h -> V4LIVE.FAILED).
#     V4INIT.FAILED -> V4LIVE.FAILED.
#  2. Top-up: Initialize events from the V4INIT pin + 1 to head - 10 (collect/topup_initialize.py ->
#     ../initialize-topup.csv.gz). If it fails, the run continues with the V4INIT parts only and records that.
#  3. Wait (poll 30 s, at most WAIT_OTHER_ENGINES_MAX s, default 3600) while another Base engine (node ... src/main.ts,
#     --chain base) is running, so the two runs do not share the public RPC endpoints; recorded in run-times.json.
#  4. Launch, in its own process group, from /home/user/dapparb/bot:
#       LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 \
#         --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6 --v4-pools "<V4INIT parts>,<top-up>" \
#         --out ../live-v4.jsonl        (stdout+stderr -> ../live-v4.log; LOG_JSON=1 = one pino JSON object per line)
#  5. When the log has 'searcher ready', let it run RUN_SECONDS (1200) more, counted from the ready record's time;
#     then SIGINT to the process group, SIGTERM after 30 s, SIGKILL after a further 30 s.
#  6. Write ../run-times.json (collect/v4live_helper.py finalize) and the sentinel V4LIVE.DONE, or V4LIVE.FAILED with
#     the reason (V4INIT failed/timeout, engine exited before ready or during the window, ready timeout).
# A live window cannot be replayed: if V4LIVE.DONE exists the script exits. On a rerun after an interrupted attempt,
# earlier live-v4.* / run-times.json are moved to attempts/<UTC>/ first.
set -u
OUT=/home/user/dapparb/research-material/02-v4-live-test
COL=$OUT/collect
BOT=/home/user/dapparb/bot
SENT=/home/user/dapparb/research-material/.sentinels
V4DIR=/home/user/dapparb/research-material/01-v4-pools
NAME=V4LIVE
RUN_SECONDS=${RUN_SECONDS:-1200}
WAIT_V4INIT_MAX=${WAIT_V4INIT_MAX:-21600}
WAIT_OTHER_ENGINES_MAX=${WAIT_OTHER_ENGINES_MAX:-3600}
READY_TIMEOUT=${READY_TIMEOUT:-9000}
KV=$COL/state/run.kv
LOG=$OUT/live-v4.log
JSONL=$OUT/live-v4.jsonl
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
export PATH=/root/.foundry/bin:$PATH

ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
say() { echo "$(ts) $*"; }
kv() { printf '%s=%s\n' "$1" "$2" >> "$KV"; }
sentinel() { # $1 = DONE|FAILED, $2 = text
  mkdir -p "$SENT"; rm -f "$SENT/$NAME.DONE" "$SENT/$NAME.FAILED"
  printf '%s\n%s\n' "$2" "$(ts)" > "$SENT/$NAME.$1.tmp" && mv "$SENT/$NAME.$1.tmp" "$SENT/$NAME.$1"
}
finalize() { python3 "$COL/v4live_helper.py" finalize; }
fail() {
  say "FAILED: $1"; kv status FAILED; kv reason "$1"; finalize; sentinel FAILED "$1"; exit 1
}
EPID=""
stop_engine() { # SIGINT to the group, SIGTERM after 30 s, SIGKILL after 30 s more
  [ -z "$EPID" ] && return
  if kill -0 "$EPID" 2>/dev/null; then kv stop_sigint_utc "$(ts)"; kill -INT -- "-$EPID" 2>/dev/null; fi
  for i in $(seq 1 30); do kill -0 "$EPID" 2>/dev/null || break; sleep 1; done
  if kill -0 "$EPID" 2>/dev/null; then kv stop_sigterm_utc "$(ts)"; kill -TERM -- "-$EPID" 2>/dev/null; fi
  for i in $(seq 1 30); do kill -0 "$EPID" 2>/dev/null || break; sleep 1; done
  if kill -0 "$EPID" 2>/dev/null; then kv stop_sigkill_utc "$(ts)"; kill -KILL -- "-$EPID" 2>/dev/null; fi
  wait "$EPID" 2>/dev/null; local rc=$?
  kv engine_exit_utc "$(ts)"; kv engine_exit_code "$rc"
}
trap 'say "runner received a signal; stopping engine"; stop_engine; fail "runner interrupted by a signal"' INT TERM

mkdir -p "$COL/state"
if [ -f "$SENT/$NAME.DONE" ]; then say "$NAME.DONE exists; nothing to do (delete it and run-times.json for a new window)"; exit 0; fi
if [ -e "$LOG" ] || [ -e "$JSONL" ] || [ -e "$OUT/run-times.json" ] || [ -e "$KV" ]; then
  A="$OUT/attempts/$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$A"
  for f in "$LOG" "$JSONL" "$OUT/run-times.json" "$KV" "$COL/state/concurrent-engines.jsonl"; do [ -e "$f" ] && mv "$f" "$A/"; done
  say "earlier attempt files moved to $A"
fi
rm -f "$SENT/$NAME.FAILED"
kv status RUNNING
kv script_start_utc "$(ts)"
kv run_seconds "$RUN_SECONDS"

# 1) wait for V4INIT
waited=0
while [ ! -f "$SENT/V4INIT.DONE" ]; do
  [ -f "$SENT/V4INIT.FAILED" ] && fail "V4INIT.FAILED: $(head -c 300 "$SENT/V4INIT.FAILED" | tr '\n' ' ')"
  [ "$waited" -ge "$WAIT_V4INIT_MAX" ] && fail "V4INIT.DONE did not appear within $WAIT_V4INIT_MAX s"
  sleep 60; waited=$((waited + 60))
done
kv v4init_done_seen_utc "$(ts)"
say "V4INIT.DONE present"

# 2) top-up of Initialize events after the V4INIT pin
kv topup_start_utc "$(ts)"
python3 -u "$COL/topup_initialize.py" --repin >> "$COL/topup_initialize.log" 2>&1
trc=$?
kv topup_end_utc "$(ts)"; kv topup_exit "$trc"
SPEC="$V4DIR/initialize-part-*.csv.gz"
if [ "$trc" -eq 0 ] && [ -f "$OUT/initialize-topup.csv.gz" ]; then
  SPEC="$SPEC,$OUT/initialize-topup.csv.gz"; kv topup_status ok
  kv topup_index "$(python3 -c "import json;d=json.load(open('$OUT/initialize-topup.json'));print(json.dumps({k:d[k] for k in ('rows','block_from','block_to','sha256')}))")"
else
  kv topup_status "failed (exit $trc); run uses the V4INIT parts only; see collect/topup_initialize.log and collect/state/topup-gaps.json"
fi
say "v4 pools spec: $SPEC"

# 3) do not overlap another Base engine run
first="$(python3 "$COL/v4live_helper.py" engines --base-only)"; kv other_engines_first "$first"
w=0
while [ "$(python3 "$COL/v4live_helper.py" engines --base-only)" != "[]" ] && [ "$w" -lt "$WAIT_OTHER_ENGINES_MAX" ]; do
  sleep 30; w=$((w + 30))
done
kv other_engines_wait_s "$w"
kv other_engines_at_launch "$(python3 "$COL/v4live_helper.py" engines --base-only)"
say "other Base engines wait: $w s"

# 4) launch
CMD="LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6 --v4-pools '$SPEC' --out $JSONL"
kv cmd "$CMD"; kv cwd "$BOT"; kv env "LOG_JSON=1"; kv spec "$SPEC"
kv head_at_launch "$(python3 "$COL/v4live_helper.py" head)"
cd "$BOT" || fail "cannot cd to $BOT"
LOG_JSON=1 setsid npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 \
  --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6 --v4-pools "$SPEC" --out "$JSONL" > "$LOG" 2>&1 < /dev/null &
EPID=$!
kv launch_utc "$(ts)"; kv engine_pid "$EPID"
sleep 2
PG="$(ps -o pgid= -p "$EPID" 2>/dev/null | tr -d ' ')"; kv engine_pgid "${PG:-}"
[ -n "$PG" ] && [ "$PG" != "$EPID" ] && say "WARNING: engine pgid $PG != pid $EPID"
say "engine launched pid=$EPID pgid=$PG"

# 5) wait for 'searcher ready'
t0=$(date +%s)
until grep -q '"msg":"searcher ready"' "$LOG" 2>/dev/null; do
  if ! kill -0 "$EPID" 2>/dev/null; then
    wait "$EPID"; rc=$?; kv engine_exit_utc "$(ts)"; kv engine_exit_code "$rc"
    fail "engine exited before 'searcher ready' (exit code $rc)"
  fi
  if [ $(( $(date +%s) - t0 )) -ge "$READY_TIMEOUT" ]; then stop_engine; fail "no 'searcher ready' within $READY_TIMEOUT s"; fi
  sleep 2
done
kv ready_detected_utc "$(ts)"
kv head_at_ready "$(python3 "$COL/v4live_helper.py" head)"
ready_ms="$(grep -m1 '"msg":"searcher ready"' "$LOG" | python3 -c 'import json,sys; print(json.loads(sys.stdin.readline())["time"])')"
stop_at=$(( ready_ms / 1000 + RUN_SECONDS ))
kv planned_stop_utc "$(date -u -d "@$stop_at" +%Y-%m-%dT%H:%M:%SZ)"
say "searcher ready (log time ${ready_ms} ms); stopping at $(date -u -d "@$stop_at" +%H:%M:%SZ)"
last_sample=0
while [ "$(date +%s)" -lt "$stop_at" ]; do
  if ! kill -0 "$EPID" 2>/dev/null; then
    wait "$EPID"; rc=$?; kv engine_exit_utc "$(ts)"; kv engine_exit_code "$rc"; kv head_at_stop "$(python3 "$COL/v4live_helper.py" head)"
    fail "engine exited during the ${RUN_SECONDS}-second window (exit code $rc)"
  fi
  if [ $(( $(date +%s) - last_sample )) -ge 60 ]; then
    printf '{"at_utc":"%s","engines":%s}\n' "$(ts)" "$(python3 "$COL/v4live_helper.py" engines --exclude-pgid "$EPID")" >> "$COL/state/concurrent-engines.jsonl"
    last_sample=$(date +%s)
  fi
  sleep 1
done

# 6) stop and record
kv head_at_stop "$(python3 "$COL/v4live_helper.py" head)"
stop_engine
trap - INT TERM
kv status DONE
kv reason "ok"
finalize
if grep -q '"msg":"v4 pools loaded from file"' "$LOG"; then
  sentinel DONE "ok: ran ${RUN_SECONDS} s after searcher ready; see $OUT/run-times.json"
else
  kv status FAILED; kv reason "log has no 'v4 pools loaded from file' record"; finalize
  sentinel FAILED "log has no 'v4 pools loaded from file' record"
fi
say "finished"
