#!/bin/bash
# HOOKLABELS pipeline, resume after the OOM kill of launch_tx_samples.py (2026-09-30 22:07Z). Run detached on 2026-10-01.
# Step 1 of hooks_pipeline.sh (hook_blockscout.py on state/hooks-candidates-2.txt) had completed (213 addresses, all HTTP 200 in
# ../hook-docs/blockscout/index.jsonl.gz), so this runs only the remaining steps 2 and 3 with the memory-fixed launch_tx_samples.py.
# The sentinel is NOT written as DONE here: HOOKLABELS.DONE is written by hand after the outputs are checked.
# On failure .sentinels/HOOKLABELS.FAILED is rewritten with the new reason.
set -u
cd "$(dirname "$0")"
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
S=/home/user/dapparb/research-material/.sentinels
ulimit -v 3000000   # ~2.9 GB address-space cap per process: fail with MemoryError instead of growing into the shared cgroup
echo "$(date -u +%FT%TZ) resume: launch_tx_samples.py (memory-fixed) state/hooks-candidates-all.txt" >> hooks_pipeline.log
echo "==== $(date -u +%FT%TZ) re-run with memory-fixed launch_tx_samples.py (previous run above was OOM-killed) ====" >> launch_tx_samples.log
python3 -u launch_tx_samples.py state/hooks-candidates-all.txt >> launch_tx_samples.log 2>&1 || { echo "$(date -u +%FT%TZ) launch_tx_samples.py (memory-fixed re-run) failed, see collect/launch_tx_samples.log" > "$S/HOOKLABELS.FAILED"; echo "$(date -u +%FT%TZ) launch_tx_samples.py failed" >> hooks_pipeline.log; exit 1; }
echo "$(date -u +%FT%TZ) resume: build_hooks_csv.py" >> hooks_pipeline.log
python3 -u build_hooks_csv.py > build_hooks_csv.log 2>&1 || { echo "$(date -u +%FT%TZ) build_hooks_csv.py failed (resume run), see collect/build_hooks_csv.log" > "$S/HOOKLABELS.FAILED"; echo "$(date -u +%FT%TZ) build_hooks_csv.py failed" >> hooks_pipeline.log; exit 1; }
echo "$(date -u +%FT%TZ) resume: steps 2-3 finished OK (sentinel written after manual check)" >> hooks_pipeline.log
