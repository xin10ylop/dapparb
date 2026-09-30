#!/usr/bin/env bash
# BSC census pipeline (resumable: every step skips work already done).
#  1. pin_window.py   -> ../census/window.json (kept if it already exists)
#  2. download.py     -> ../census/raw/chunk-*.jsonl.gz (+ gaps.csv / gaps-unrecovered.csv)
#  3. waits for POSTPROCESS.READY (swap-topics.csv finalised by the collecting agent), max 6 h
#  4. postprocess.py  -> ../census/{blocks,txs-*,reverted-*,candidates-*}, ../builder/builder-material-*
#  5. sentinel /home/user/dapparb/research-material/.sentinels/BSC_CENSUS.DONE (or .FAILED with reason)
# Launch: cd <dir>/collect && setsid nohup ./run_census.sh > run_census.log 2>&1 < /dev/null &
set -u
cd "$(dirname "$0")"
SENT=/home/user/dapparb/research-material/.sentinels
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
fail() { echo "$(date -u +%FT%TZ) FAILED: $*"; echo "$*" > "$SENT/BSC_CENSUS.FAILED"; exit 1; }
echo "$(date -u +%FT%TZ) pipeline start pid=$$"
rm -f "$SENT/BSC_CENSUS.FAILED"
python3 pin_window.py || fail "pin_window.py exit $?"
python3 download.py || fail "download.py exit $?"
waited=0
while [ ! -f POSTPROCESS.READY ]; do
  [ $waited -ge 21600 ] && fail "POSTPROCESS.READY not created within 6h (swap-topics.csv not finalised); raw data complete in census/raw"
  sleep 30; waited=$((waited+30))
done
python3 postprocess.py || fail "postprocess.py exit $?"
date -u +%FT%TZ > "$SENT/BSC_CENSUS.DONE"
echo "$(date -u +%FT%TZ) pipeline done"
