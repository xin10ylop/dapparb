#!/bin/bash
# One block-level scan with the unmodified scanner bot/src/research/scan.ts.
#
# Usage: run_scan.sh <chain> <universe:config|top> <blocks> <cap_minutes> <out_dir> <name> [extra scan.ts flags...]
#
# Sampling (from scan.ts): the loop polls eth_blockNumber; each time the head differs from the last scanned head it
# syncs every pool pinned at that head, searches, prices gas and counts the head as one of --blocks. Heads produced
# while a sync+search is running are not scanned. The loop ends when --blocks distinct heads were scanned.
# Rule used here: --blocks = 30 min / block time + 1 (fewest distinct heads that can span 30 min of chain time), and a
# time cap: SIGTERM <cap_minutes> after the first "block scanned" line if the tool has not finished by then. The
# exit-flush.mjs preload lets queued JSONL rows flush for 5 s before exit (scan.ts is not modified).
set -u
CHAIN=$1; UNIVERSE=$2; BLOCKS=$3; CAP=$4; OUT=$5; NAME=$6; shift 6
EXTRA=("$@")
C=/home/user/dapparb/research-material/07-other-chains-engine/collect
WORK=$C/work; STATE=$C/state; mkdir -p "$WORK" "$STATE" "$OUT"
LOG=$C/$NAME.log
JSONL=$WORK/$NAME.jsonl
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { echo "[run_scan $(ts)] $*" | tee -a "$C/pipeline.log" >&2; }
gap() {
  note "GAP $NAME: $1"
  echo "{\"t\":\"$(ts)\",\"step\":\"$NAME\",\"reason\":$(printf '%s' "$1" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')}" >> "$C/gaps.jsonl"
}
if [ -e "$STATE/$NAME.done" ]; then note "$NAME already done; skipping"; exit 0; fi
ATTEMPT=0
while :; do
  ATTEMPT=$((ATTEMPT + 1))
  rm -f "$JSONL"   # a live window cannot be resumed; an interrupted attempt is redone from scratch
  cd /home/user/dapparb/bot || { gap "cd bot failed"; exit 1; }
  FLAGS=(--chain "$CHAIN" --universe "$UNIVERSE" --blocks "$BLOCKS" --out "$JSONL" "${EXTRA[@]}")
  echo "# $(ts) attempt $ATTEMPT cmd: LOG_JSON=1 ${BASE_RPC_URL:+BASE_RPC_URL=$BASE_RPC_URL }node --import tsx --import $C/exit-flush.mjs src/research/scan.ts ${FLAGS[*]}  (time cap ${CAP} min after first scanned block)" > "$LOG"
  LOG_JSON=1 node --import tsx --import "$C/exit-flush.mjs" src/research/scan.ts "${FLAGS[@]}" >> "$LOG" 2>&1 < /dev/null &
  PID=$!
  echo "$PID" > "$STATE/$NAME.pid"
  note "$NAME attempt $ATTEMPT started pid=$PID flags: ${FLAGS[*]} cap=${CAP}min"
  T0=$(date +%s); FIRST=""; CAPPED=0
  while kill -0 "$PID" 2>/dev/null; do
    if [ -z "$FIRST" ] && grep -q '"msg":"block scanned"' "$LOG"; then FIRST=$(date +%s); note "$NAME first block scanned"; fi
    if [ -z "$FIRST" ] && [ $(( $(date +%s) - T0 )) -gt 3600 ]; then kill -TERM "$PID"; sleep 7; gap "attempt $ATTEMPT: no block scanned within 60 min of start (discovery stalled); killed"; break; fi
    if [ -n "$FIRST" ] && [ $(( $(date +%s) - FIRST )) -ge $(( CAP * 60 )) ]; then
      CAPPED=1; note "$NAME time cap reached; SIGTERM"; kill -TERM "$PID"
      for i in $(seq 1 20); do kill -0 "$PID" 2>/dev/null || break; sleep 1; done
      kill -0 "$PID" 2>/dev/null && kill -KILL "$PID"
      break
    fi
    sleep 5
  done
  wait "$PID" 2>/dev/null; RC=$?
  echo "exit=$RC capped=$CAPPED" >> "$LOG"
  echo "{\"attempt\":$ATTEMPT,\"exit\":$RC,\"time_capped\":$CAPPED,\"cap_minutes\":$CAP,\"blocks_flag\":$BLOCKS,\"first_block_scanned_seen_utc\":\"${FIRST:+$(date -u -d @$FIRST +%Y-%m-%dT%H:%M:%SZ)}\",\"ended_utc\":\"$(ts)\"}" > "$STATE/$NAME.window.json"
  if [ -n "$FIRST" ] && { [ "$RC" = 0 ] || [ "$CAPPED" = 1 ]; }; then break; fi
  gap "attempt $ATTEMPT ended with exit=$RC before completing (see collect/$NAME.attempt$ATTEMPT.log)"
  cp "$LOG" "$C/$NAME.attempt$ATTEMPT.log"
  if [ "$ATTEMPT" -ge 3 ]; then gap "giving up after 3 attempts"; exit 1; fi
  sleep 60
done
python3 "$C/finalize.py" --jsonl "$JSONL" --log "$LOG" --out-dir "$OUT" --name "$NAME" --window "$STATE/$NAME.window.json" || { gap "finalize failed"; exit 1; }
touch "$STATE/$NAME.done"
note "$NAME done (exit=$RC capped=$CAPPED)"
exit 0
