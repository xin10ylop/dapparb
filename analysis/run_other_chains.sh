#!/bin/bash
# Classifier over each other-chain census. V4 chains pass their PoolManager and the pool keys fetched by
# v4keys_fetch.py (PositionManager.poolKeys) so V4 Swap deltas and native ETH are accounted for.
R=/home/user/dapparb/research-material/06-other-chains-onchain
run() { # name census_dir weth native_usd pool_manager
  mkdir -p chains/$1
  K=(); [ -n "$5" ] && K=(--v4-init v4keys/$1.csv.gz)
  python3 -u arb_census.py --census $2 --chain $1 --out chains/$1 --weth $3 --pool-manager "$5" "${K[@]}" --prices prices/$1.csv --native-usd $4 > chains/$1/run.log 2>&1
  echo "$(date -u +%FT%TZ) $1 exit $?" >> chains/progress.log
}
mkdir -p chains
run arbitrum   $R/arbitrum   0x82af49447d8a07e3bd95bd0d56f35241523fbab1 2677.8167 0x360e68faccca8ca495c1b759fd9eee466db9fb32
run optimism   $R/optimism   0x4200000000000000000000000000000000000006 2677.8167 0x9a13f98cb987694c9f086b1f5eb990eea8264ec3
run unichain   $R/unichain   0x4200000000000000000000000000000000000006 2677.8167 0x1f98400000000000000000000000000000000004
run ethereum   $R/ethereum   0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2 2679.9075 0x000000000004444c5dc75cb358380d2e3de08a90
run polygon    $R/polygon    0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270 0.1118    0x67366782805870060151383f4bbff9dab53e5cd6
run ink        $R/ink        0x4200000000000000000000000000000000000006 2690.9298 0x360e68faccca8ca495c1b759fd9eee466db9fb32
run mantle     $R/mantle     0x78c1b0c915c4faa5fffa6cabf0219da63d7f4cb8 0.6938    ''
run abstract   $R/abstract   0x3439153eb7af838ad19d56e1571fbd09333c2809 2690.9298 ''
run worldchain $R/worldchain 0x4200000000000000000000000000000000000006 2690.9298 0xb1860d529182ac3bc1f51fa2abd56662b7d13f33
run zksync     $R/zksync     0x5aea5775959fbc2557cc8789bc1bf90a239d9a91 2690.9555 ''
run soneium    $R/soneium    0x4200000000000000000000000000000000000006 2690.9298 0x360e68faccca8ca495c1b759fd9eee466db9fb32
run bsc        $R/bsc/census 0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c 766.4748  0x28e2ea090877bf75740558f6bfb36a5ffee9e9df
echo "$(date -u +%FT%TZ) all done" >> chains/progress.log
