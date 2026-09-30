#!/bin/bash
# SOL_SAMPLE pipeline: raw fetch (resumable) -> Jito bundles per slot (resumable) -> build tables -> DefiLlama prices.
# Writes /home/user/dapparb/research-material/.sentinels/SOL_SAMPLE.DONE or SOL_SAMPLE.FAILED (with reason).
# usage: cd <this dir> && setsid nohup bash sol_pipeline.sh > sol_pipeline.log 2>&1 < /dev/null &
cd "$(dirname "$0")"
S=/home/user/dapparb/research-material/.sentinels/SOL_SAMPLE
fail() { echo "$(date -u +%FT%TZ) FAILED: $1"; echo "$(date -u +%FT%TZ) $1" > "$S.FAILED"; exit 1; }
# wait for any separately launched instance of the step scripts to finish (avoid duplicate requests)
while pgrep -f "python3 -u sol_fetch.py" > /dev/null || pgrep -f "python3 -u jito_bundles.py" > /dev/null; do sleep 10; done
python3 -u sol_fetch.py --n 600 >> sol_fetch.log 2>&1 || fail "sol_fetch.py exit $? (see sol_fetch.log, ../data/fetch-gaps.csv)"
python3 -u jito_bundles.py >> jito_bundles.log 2>&1 || fail "jito_bundles.py exit $? (see jito_bundles.log, ../data/jito-bundles-gaps.csv)"
[ -s ../dex-programs.csv ] && [ -s ../jito-tip-accounts.csv ] || python3 -u programs.py >> programs.log 2>&1 || fail "programs.py exit $? (see programs.log)"
python3 -u sol_build.py > sol_build.log 2>&1 || fail "sol_build.py exit $? (see sol_build.log)"
python3 -u prices.py > prices.log 2>&1 || fail "prices.py exit $? (see prices.log, ../data/prices-gaps.csv)"
rm -f "$S.FAILED"
echo "$(date -u +%FT%TZ) done: $(cat ../data/build-summary.json | tr -d '\n ')" > "$S.DONE"
echo "$(date -u +%FT%TZ) DONE"
