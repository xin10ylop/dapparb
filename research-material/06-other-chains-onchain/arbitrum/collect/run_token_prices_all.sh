#!/bin/bash
# Runs token_prices.py for the five chains one after another (keeps <= 1 in-flight request to coins.llama.fi).
B=/home/user/dapparb/research-material/06-other-chains-onchain
for c in unichain optimism arbitrum ethereum polygon; do
  cd $B/$c/collect && python3 token_prices.py --chain $c --out $B/$c > token_prices.log 2>&1
done
