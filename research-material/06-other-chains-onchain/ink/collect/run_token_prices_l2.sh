#!/bin/bash
# Runs token_prices_l2.py (= unmodified token_prices.py + l2_config.TOKEN_CFG) for the six added L2 chains one after
# another (keeps <= 1 in-flight request to coins.llama.fi). Added 2026-10-01.
B=/home/user/dapparb/research-material/06-other-chains-onchain
for c in ink mantle abstract worldchain zksync soneium; do
  cd $B/$c/collect && python3 -B token_prices_l2.py --chain $c --out $B/$c > token_prices.log 2>&1
done
