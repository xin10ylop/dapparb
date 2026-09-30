#!/usr/bin/env bash
# Round-trip to Base endpoints from this machine (all are Cloudflare-fronted, so this measures the edge hop).
for u in https://mainnet-sequencer.base.org https://mainnet.base.org https://mainnet-preconf.base.org; do
  for i in 1 2 3 4 5; do curl -sS -o /dev/null -w "%{time_connect} %{time_starttransfer}\n" --max-time 5 -X POST -H 'content-type: application/json' --data '{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}' "$u"; done | awk -v u="$u" '{c+=$1; t+=$2; n++} END {printf "%-40s connect %.1fms  first-byte %.1fms (n=%d)\n", u, c/n*1000, t/n*1000, n}'
done
