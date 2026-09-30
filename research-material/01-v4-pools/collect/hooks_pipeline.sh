#!/bin/bash
# HOOKLABELS pipeline (item 4, run detached): Blockscout metadata for hooks with >= 20 pools in the final V4INIT data
# (state/hooks-candidates-2.txt; candidates-1 was fetched earlier), launch-tx samples for all candidates, then hooks.csv.
# Sentinel: /home/user/dapparb/research-material/.sentinels/HOOKLABELS.DONE (or .FAILED)
set -u
cd "$(dirname "$0")"
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
S=/home/user/dapparb/research-material/.sentinels
rm -f "$S/HOOKLABELS.DONE" "$S/HOOKLABELS.FAILED"
python3 -u hook_blockscout.py state/hooks-candidates-2.txt >> hook_blockscout.log 2>&1 || { echo "hook_blockscout.py failed, see collect/hook_blockscout.log" > "$S/HOOKLABELS.FAILED"; exit 1; }
python3 -u launch_tx_samples.py state/hooks-candidates-all.txt > launch_tx_samples.log 2>&1 || { echo "launch_tx_samples.py failed, see collect/launch_tx_samples.log" > "$S/HOOKLABELS.FAILED"; exit 1; }
python3 -u build_hooks_csv.py > build_hooks_csv.log 2>&1 || { echo "build_hooks_csv.py failed, see collect/build_hooks_csv.log" > "$S/HOOKLABELS.FAILED"; exit 1; }
echo "{\"hooks_csv\": \"../hooks.csv\", \"completed_utc\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > "$S/HOOKLABELS.DONE"
