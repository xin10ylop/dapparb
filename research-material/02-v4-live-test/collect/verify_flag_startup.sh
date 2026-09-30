#!/usr/bin/env bash
# Verification of the --v4-pools flag (step 2): run the reference command plus --v4-pools until the engine logs
# 'searcher ready', then stop it by its PID/process group (SIGINT, SIGTERM after 30 s). Output:
#   collect/verify-startup.log (engine log, LOG_JSON=1), collect/verify-startup.jsonl (engine --out; normally empty),
#   collect/verify-startup.times (launch / ready / stop UTC).
# Usage: verify_flag_startup.sh "<v4-pools spec>"
set -u
OUT=/home/user/dapparb/research-material/02-v4-live-test
SPEC="$1"
LOG=$OUT/collect/verify-startup.log
T=$OUT/collect/verify-startup.times
ts() { date -u +%Y-%m-%dT%H:%M:%S.%3NZ; }
cd /home/user/dapparb/bot
echo "launch $(ts) spec=$SPEC" > "$T"
LOG_JSON=1 setsid npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 \
  --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6 --v4-pools "$SPEC" --out "$OUT/collect/verify-startup.jsonl" > "$LOG" 2>&1 < /dev/null &
EPID=$!
echo "pid $EPID pgid $(ps -o pgid= -p $EPID | tr -d ' ')" >> "$T"
until grep -q '"msg":"searcher ready"' "$LOG"; do
  if ! kill -0 "$EPID" 2>/dev/null; then wait "$EPID"; echo "exited_before_ready $(ts) rc=$?" >> "$T"; exit 1; fi
  sleep 2
done
echo "ready_detected $(ts)" >> "$T"
kill -INT -- "-$EPID"
for i in $(seq 1 30); do kill -0 "$EPID" 2>/dev/null || break; sleep 1; done
kill -0 "$EPID" 2>/dev/null && { echo "sigterm $(ts)" >> "$T"; kill -TERM -- "-$EPID"; }
wait "$EPID"; echo "stopped $(ts) rc=$?" >> "$T"
