#!/bin/bash
# Master pipeline for 07-other-chains-engine. Re-runnable: finished steps leave collect/state/<name>.done and are
# skipped on a re-run; an unfinished live step is redone from scratch (a live window cannot be resumed).
#
# Launch (detached):
#   cd /home/user/dapparb/research-material/07-other-chains-engine/collect && setsid nohup bash run_all.sh > run_all.log 2>&1 < /dev/null &
#
# Per chain, steps run in sequence so that one chain's RPC endpoint never serves two of these processes at once
# (each process keeps <= 4 requests in flight: multicallChunked concurrency 4). The three chains run in parallel.
set -u
C=/home/user/dapparb/research-material/07-other-chains-engine/collect
D=/home/user/dapparb/research-material/07-other-chains-engine
S=/home/user/dapparb/research-material/.sentinels
STATE=$C/state; mkdir -p "$STATE"
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { echo "[run_all $(ts)] $*" | tee -a "$C/pipeline.log"; }
echo $$ > "$STATE/run_all.pid"

# --blocks = 30 min / block time + 1; time cap 31 min after the first scanned block (see run_scan.sh)
ENGINE_FLAGS=(--source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6)

scans_finished() {  # called by each chain when its scans are finished; the last one writes the SCANS sentinel
  touch "$STATE/scans-$1.finished"
  (
    flock 9
    for c in arbitrum mainnet base; do [ -e "$STATE/scans-$c.finished" ] || exit 0; done
    missing=""
    for n in scan-arbitrum-config scan-arbitrum-top scan-mainnet-config scan-mainnet-top scan-base-config scan-base-top; do
      [ -e "$STATE/$n.done" ] || missing="$missing $n"
    done
    if [ -z "$missing" ]; then echo "all 6 scans finished $(ts); outputs in $D/scans" > "$S/SCANS.DONE"; rm -f "$S/SCANS.FAILED"
    else echo "scans not completed:$missing (see $C/gaps.jsonl and collect/<name>.log)" > "$S/SCANS.FAILED"; fi
    note "SCANS sentinel written"
  ) 9> "$STATE/scans.lock"
}

arbitrum() {
  bash "$C/run_scan.sh" arbitrum config 7201 31 "$D/scans/arbitrum" scan-arbitrum-config
  bash "$C/run_scan.sh" arbitrum top 7201 31 "$D/scans/arbitrum" scan-arbitrum-top
  scans_finished arbitrum
  bash "$C/run_engine_detect.sh" arbitrum 20 "$D/engine-detect/arbitrum" engine-detect-arbitrum 1 "${ENGINE_FLAGS[@]}"
}
mainnet() {
  bash "$C/run_scan.sh" mainnet config 151 31 "$D/scans/mainnet" scan-mainnet-config
  bash "$C/run_scan.sh" mainnet top 151 31 "$D/scans/mainnet" scan-mainnet-top
  scans_finished mainnet
  bash "$C/run_engine_detect.sh" mainnet 20 "$D/engine-detect/mainnet" engine-detect-mainnet 1 "${ENGINE_FLAGS[@]}"
}
base() {
  # base-rpc.publicnode.com and base.drpc.org are reserved for the Base census collectors; this scan reads through
  # base.meowrpc.com (scan.ts's fallback list still contains base.drpc.org, blastapi and mainnet.base.org after it).
  export BASE_RPC_URL=https://base.meowrpc.com
  bash "$C/run_scan.sh" base config 901 31 "$D/scans/base" scan-base-config
  bash "$C/run_scan.sh" base top 901 31 "$D/scans/base" scan-base-top
  scans_finished base
}

note "pipeline start"
arbitrum & A=$!
mainnet & M=$!
base & B=$!
wait $A $M $B
note "pipeline end"
