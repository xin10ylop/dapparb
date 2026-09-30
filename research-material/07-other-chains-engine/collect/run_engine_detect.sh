#!/bin/bash
# Detection-only live run of the unmodified engine (bot/src/main.ts --mode dry) on a non-Base chain.
#
# Why detection-only: the dry-run SIMULATION path cannot run on arbitrum/mainnet without a code change
# (main.ts:57-59 loads the executor runtime for state override only when cfg.id === 8453; see MANIFEST.md).
# Passing an empty --contract makes main.ts:55 resolve `contract` to "" (not nullish, so the placeholder default
# is not used), main.ts:122 then creates no Executor, and every candidate goes through main.ts:258-262
# ("opportunity (no contract configured; not simulated)"). This is a command-line parameter only.
#
# Usage: run_engine_detect.sh <chain> <minutes> <out_dir> <name> [sentinel:0|1] [extra main.ts flags...]
# The run is stopped with SIGINT <minutes> after the "searcher ready" log line (main.ts has a SIGINT handler).
set -u
CHAIN=$1; MINUTES=$2; OUT=$3; NAME=$4; SENT=${5:-1}; shift 5 || shift $#
EXTRA=("$@")
C=/home/user/dapparb/research-material/07-other-chains-engine/collect
S=/home/user/dapparb/research-material/.sentinels
WORK=$C/work; STATE=$C/state; mkdir -p "$WORK" "$STATE" "$OUT"
LOG=$C/$NAME.log
JSONL=$WORK/$NAME.jsonl
SENTNAME=ENGINE_DETECT_$(echo "$CHAIN" | tr a-z A-Z)
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { echo "[run_engine_detect $(ts)] $*" | tee -a "$C/pipeline.log" >&2; }
fail() {
  note "FAILED $NAME: $1"
  echo "{\"t\":\"$(ts)\",\"step\":\"$NAME\",\"reason\":$(printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')}" >> "$C/gaps.jsonl"
  [ "$SENT" = 1 ] && printf '%s\n' "$1" > "$S/$SENTNAME.FAILED"
  exit 1
}
if [ -e "$STATE/$NAME.done" ]; then note "$NAME already done (state/$NAME.done); skipping"; exit 0; fi
rm -f "$JSONL"   # a live window cannot be resumed; an interrupted run is redone from scratch
cd /home/user/dapparb/bot || fail "cd bot failed"
FLAGS=(--chain "$CHAIN" --mode dry --contract "" --out "$JSONL" "${EXTRA[@]}")
echo "# $(ts) cmd: LOG_JSON=1 node --import tsx --import $C/exit-flush.mjs src/main.ts ${FLAGS[*]}" > "$LOG"
bash "$C/provenance.sh" "$OUT/$NAME.code-provenance.txt"
LOG_JSON=1 node --import tsx --import "$C/exit-flush.mjs" src/main.ts "${FLAGS[@]}" >> "$LOG" 2>&1 < /dev/null &
PID=$!
echo "$PID" > "$STATE/$NAME.pid"
note "$NAME started pid=$PID flags: ${FLAGS[*]}"
# wait for "searcher ready" (discovery can take a while for --universe all), max 60 min
T0=$(date +%s)
until grep -q '"msg":"searcher ready"' "$LOG"; do
  kill -0 "$PID" 2>/dev/null || fail "engine exited before 'searcher ready' (see collect/$NAME.log)"
  [ $(( $(date +%s) - T0 )) -gt 3600 ] && { kill -INT "$PID"; fail "no 'searcher ready' within 60 min"; }
  sleep 5
done
READY=$(date +%s)
note "$NAME searcher ready; running $MINUTES min"
echo "{\"ready_utc\":\"$(date -u -d @$READY +%Y-%m-%dT%H:%M:%SZ)\"}" > "$STATE/$NAME.window.json"
while [ $(( $(date +%s) - READY )) -lt $(( MINUTES * 60 )) ]; do
  kill -0 "$PID" 2>/dev/null || fail "engine exited during the window after $(( $(date +%s) - READY )) s (see collect/$NAME.log)"
  sleep 5
done
STOP=$(date +%s)
kill -INT "$PID"
for i in $(seq 1 30); do kill -0 "$PID" 2>/dev/null || break; sleep 1; done
kill -0 "$PID" 2>/dev/null && { kill -TERM "$PID"; sleep 6; }
echo "{\"ready_utc\":\"$(date -u -d @$READY +%Y-%m-%dT%H:%M:%SZ)\",\"sigint_utc\":\"$(date -u -d @$STOP +%Y-%m-%dT%H:%M:%SZ)\",\"minutes\":$MINUTES}" > "$STATE/$NAME.window.json"
# finalize: gzip the raw JSONL (split if > 85 MB) and a gzip copy of the raw log next to it
python3 "$C/finalize.py" --jsonl "$JSONL" --log "$LOG" --out-dir "$OUT" --name "$NAME" --window "$STATE/$NAME.window.json" || fail "finalize failed"
touch "$STATE/$NAME.done"
note "$NAME done"
[ "$SENT" = 1 ] && echo "done $(ts); outputs in $OUT" > "$S/$SENTNAME.DONE"
exit 0
