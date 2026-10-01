#!/bin/bash
# Refreshes the Counts section of ../MANIFEST.md every 5 min; exits after the final refresh once the sentinels
# SCANS, ENGINE_DETECT_ARBITRUM and ENGINE_DETECT_MAINNET exist (DONE or FAILED), or after 8 h.
S=/home/user/dapparb/research-material/.sentinels
C=/home/user/dapparb/research-material/07-other-chains-engine/collect
T0=$(date +%s)
have() { ls $S/$1.DONE $S/$1.FAILED >/dev/null 2>&1; }
while :; do
  if have SCANS && have ENGINE_DETECT_ARBITRUM && have ENGINE_DETECT_MAINNET; then
    python3 $C/fill_manifest.py; echo "final fill $(date -u +%FT%TZ)"; exit 0
  fi
  python3 $C/fill_manifest.py
  [ $(( $(date +%s) - T0 )) -gt 28800 ] && { echo "waiter timed out after 8 h $(date -u +%FT%TZ)"; exit 1; }
  sleep 300
done
