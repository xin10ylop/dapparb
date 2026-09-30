#!/bin/bash
# Detection-only live run of the unmodified engine (bot/src/main.ts --mode dry) on a non-Base chain.
#
# Why detection-only: the dry-run SIMULATION path cannot run on arbitrum/mainnet without a code change
# (main.ts:57-60 at git HEAD 1c1a93f loads the executor runtime for state override only when cfg.id === 8453; see MANIFEST.md).
# Passing an empty --contract makes main.ts:55 resolve `contract` to "" (not nullish, so the placeholder default
# is not used), main.ts:122 then creates no Executor, and every candidate goes through main.ts:258-262
# ("opportunity (no contract configured; not simulated)"). This is a command-line parameter only.
#
# Usage: run_engine_detect.sh <chain> <minutes> <out_dir> <name> <sentinel:0|1> [extra main.ts flags...]
# The run is stopped with SIGINT <minutes> after the "searcher ready" log line (main.ts has a SIGINT handler).
# Up to 3 attempts: an attempt that exits before "searcher ready" or before the window ends is logged to gaps.jsonl
# (its log kept as <name>.attemptN.log) and the run is redone from scratch (a live window cannot be resumed).
set -u
CHAIN=$1; MINUTES=$2; OUT=$3; NAME=$4; SENT=$5; shift 5
EXTRA=("$@")
C=/home/user/dapparb/research-material/07-other-chains-engine/collect
S=/home/user/dapparb/research-material/.sentinels
WORK=$C/work; STATE=$C/state; mkdir -p "$WORK" "$STATE" "$OUT"
LOG=$C/$NAME.log
JSONL=$WORK/$NAME.jsonl
SENTNAME=ENGINE_DETECT_$(echo "$CHAIN" | tr a-z A-Z)
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { echo "[run_engine_detect $(ts)] $*" | tee -a "$C/pipeline.log" >&2; }
gap() { note "GAP $NAME: $1"; echo "{\"t\":\"$(ts)\",\"step\":\"$NAME\",\"reason\":$(printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')}" >> "$C/gaps.jsonl"; }
final_fail() { gap "$1"; [ "$SENT" = 1 ] && printf '%s\n' "$1" > "$S/$SENTNAME.FAILED"; exit 1; }
if [ -e "$STATE/$NAME.done" ]; then note "$NAME already done (state/$NAME.done); skipping"; exit 0; fi
cd /home/user/dapparb/bot || final_fail "cd bot failed"
FLAGS=(--chain "$CHAIN" --mode dry --contract "" --out "$JSONL" "${EXTRA[@]}")
ATTEMPT=0
while :; do
  ATTEMPT=$((ATTEMPT + 1))
  rm -f "$JSONL"
  echo "# $(ts) attempt $ATTEMPT cmd: LOG_JSON=1 node --import tsx --import $C/exit-flush.mjs src/main.ts ${FLAGS[*]}  (SIGINT $MINUTES min after 'searcher ready')" > "$LOG"
  bash "$C/provenance.sh" "$OUT/$NAME.code-provenance.txt"
  LOG_JSON=1 node --import tsx --import "$C/exit-flush.mjs" src/main.ts "${FLAGS[@]}" >> "$LOG" 2>&1 < /dev/null &
  PID=$!
  echo "$PID" > "$STATE/$NAME.pid"
  note "$NAME attempt $ATTEMPT started pid=$PID flags: ${FLAGS[*]}"
  T0=$(date +%s); READY=""; REASON=""
  while :; do
    if ! kill -0 "$PID" 2>/dev/null; then
      if [ -z "$READY" ]; then REASON="engine exited before 'searcher ready'"; else REASON="engine exited $(( $(date +%s) - READY )) s into the ${MINUTES}-min window"; fi
      break
    fi
    if [ -z "$READY" ] && grep -q '"msg":"searcher ready"' "$LOG"; then READY=$(date +%s); note "$NAME searcher ready; running $MINUTES min"; fi
    if [ -z "$READY" ] && [ $(( $(date +%s) - T0 )) -gt 3600 ]; then kill -INT "$PID"; sleep 8; kill -KILL "$PID" 2>/dev/null; REASON="no 'searcher ready' within 60 min"; break; fi
    if [ -n "$READY" ] && [ $(( $(date +%s) - READY )) -ge $(( MINUTES * 60 )) ]; then break; fi
    sleep 5
  done
  if [ -z "$REASON" ]; then
    STOP=$(date +%s)
    kill -INT "$PID"
    for i in $(seq 1 30); do kill -0 "$PID" 2>/dev/null || break; sleep 1; done
    kill -0 "$PID" 2>/dev/null && { kill -TERM "$PID"; sleep 6; kill -KILL "$PID" 2>/dev/null; }
    wait "$PID" 2>/dev/null; RC=$?
    echo "exit=$RC" >> "$LOG"
    echo "{\"attempt\":$ATTEMPT,\"ready_utc\":\"$(date -u -d @$READY +%Y-%m-%dT%H:%M:%SZ)\",\"sigint_utc\":\"$(date -u -d @$STOP +%Y-%m-%dT%H:%M:%SZ)\",\"minutes\":$MINUTES,\"exit\":$RC}" > "$STATE/$NAME.window.json"
    break
  fi
  wait "$PID" 2>/dev/null; RC=$?
  echo "exit=$RC" >> "$LOG"
  cp "$LOG" "$C/$NAME.attempt$ATTEMPT.log"
  gap "attempt $ATTEMPT: $REASON (exit=$RC; log collect/$NAME.attempt$ATTEMPT.log)"
  [ "$ATTEMPT" -ge 3 ] && final_fail "giving up after 3 attempts; last: $REASON"
  sleep 60
done
python3 "$C/finalize.py" --jsonl "$JSONL" --log "$LOG" --out-dir "$OUT" --name "$NAME" --window "$STATE/$NAME.window.json" || final_fail "finalize failed"
touch "$STATE/$NAME.done"
note "$NAME done"
[ "$SENT" = 1 ] && { rm -f "$S/$SENTNAME.FAILED"; echo "done $(ts); outputs in $OUT" > "$S/$SENTNAME.DONE"; }
exit 0
