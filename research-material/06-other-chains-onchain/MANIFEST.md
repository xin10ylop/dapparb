# 06-other-chains-onchain: on-chain raw material for chains other than Base (folder index)

Status: COMPLETE WITH GAPS (finalized 2026-10-01). All 13 collectors of this folder wrote a DONE sentinel and none wrote FAILED (sentinel text below). The last data file in this folder was written at 2026-09-30T22:30Z, before the ~23:00Z container restart of 2026-09-30; no collector of this folder was interrupted or re-run. Gaps (details in the sub-manifests):
* Unichain: 1 documentation URL not retrieved (Wayback Machine copy, HTTP 403).
* BSC: 5 of 28 swap topics not observed in the window (unverified on BSC); 11 of 44 validator MEV RPC entries did not answer `mev_params`; 5 of 92 documentation entries have no page content (network error, HTTP 429, HTTP 404).
* Solana: 1 of 61 Jito tip-floor polls failed (connection reset); for 15 of 600 slots the Jito bundles endpoint answered HTTP 404 "Bundle not found" (stored verbatim); 4 documentation URLs not retrieved.
* Local-only (git-ignored, not in the repository): `bsc/census/raw/` (40 files), `solana/data/raw-slots/` (600 files), `solana/data/jito-bundles-by-slot.parts/` (600 files), `solana/data/prices.parts/` (72 files), `solana/collect/state/pin.json`, and 8 Python bytecode caches in `__pycache__/` directories. How to regenerate each is in the sub-manifest that lists it.

This file was written on 2026-10-01 during finalization; before that the folder had no folder-level MANIFEST.md (`MANIFEST-evm.md` indexes only the five EVM chain directories). The folder holds raw material only: no analysis, estimates or conclusions.

## Contents and manifests

| Directory | Content | Manifest | Status | Files committed | Files local-only |
|---|---|---|---|---:|---:|
| arbitrum/ | Arbitrum One block-level census, 60 min, blocks 510447028-510460284; token metadata and DefiLlama prices; ordering docs; precompile state; Timeboost auction logs | arbitrum/MANIFEST.md | COMPLETE | 67 | 0 |
| optimism/ | OP Mainnet census, 60 min, blocks 157600033-157601832; token/prices; ordering docs | optimism/MANIFEST.md | COMPLETE | 46 | 0 |
| unichain/ | Unichain census, 60 min, blocks 60050483-60054082; token/prices; ordering docs | unichain/MANIFEST.md | COMPLETE WITH GAPS | 50 | 0 |
| ethereum/ | Ethereum mainnet census, 6 h, blocks 26091086-26092877; token/prices | ethereum/MANIFEST.md | COMPLETE | 27 | 0 |
| polygon/ | Polygon PoS census, 60 min, blocks 94729141-94731540; token/prices | polygon/MANIFEST.md | COMPLETE | 27 | 0 |
| (index of the five above) | window table, shared method, Q-ID table, `_shared_collect/` inventory | MANIFEST-evm.md | COMPLETE WITH GAPS | 1 | 0 |
| _shared_collect/ | master copies of the EVM collector scripts | MANIFEST-evm.md | n/a (scripts) | 9 | 1 |
| bsc/ | BSC census, 60 min, blocks 124968311-124976310; builder material, eth_getBlockMevInfo per block, builder and validator registries, validator MEV RPC probe; MEV/PBS docs; DEX landscape | bsc/MANIFEST.md | COMPLETE WITH GAPS | 232 | 40 |
| solana/ | Solana 600 consecutive slots 452084865-452085464 (non-vote txs, DEX txs, Jito tips and bundles, prices); Jito tip-floor polls; API/RPC snapshots; ordering docs; literature | solana/MANIFEST.md | COMPLETE WITH GAPS | 189 (+1 written 2026-10-01) | 1,280 |

Totals as verified on 2026-10-01: 1,969 files as collected, 648 committed and 1,321 local-only (1,008,765,233 bytes local-only). Two documentation files were added on 2026-10-01: this MANIFEST.md and `solana/local-only-inventory.tsv`. The largest committed file is `bsc/census/candidates-001.jsonl.gz` (83,906,821 bytes); no committed file exceeds 90 MB.

Not in this folder: Base (other research-material folders); live engine runs for other chains (research-material/07-other-chains-engine, sentinels ENGINE_DETECT_* and ENGINE_LIVE_*); chains other than the seven above (for example Blast, Linea, zkSync, Scroll, Mantle, Avalanche, Sonic, Sui, Aptos, TON).

## Sentinels (verbatim)

The sentinel files are in `research-material/.sentinels/`, which is git-ignored, so their text is reproduced here (read 2026-10-01).

```
EVM_CENSUS_ARBITRUM.DONE      arbitrum census complete 2026-09-30T21:09:43Z blocks 510447028-510460284 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/arbitrum
EVM_CENSUS_OPTIMISM.DONE      optimism census complete 2026-09-30T21:07:59Z blocks 157600033-157601832 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/optimism
EVM_CENSUS_UNICHAIN.DONE      unichain census complete 2026-09-30T21:07:44Z blocks 60050483-60054082 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/unichain
EVM_CENSUS_ETHEREUM.DONE      ethereum census complete 2026-09-30T21:08:49Z blocks 26091086-26092877 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/ethereum
EVM_CENSUS_POLYGON.DONE       polygon census complete 2026-09-30T21:10:22Z blocks 94729141-94731540 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/polygon
EVM_TOKENPRICES_ARBITRUM.DONE arbitrum token meta + prices done 2026-09-30T21:13:57Z tokens=245
EVM_TOKENPRICES_OPTIMISM.DONE optimism token meta + prices done 2026-09-30T21:13:30Z tokens=215
EVM_TOKENPRICES_UNICHAIN.DONE unichain token meta + prices done 2026-09-30T21:13:03Z tokens=17
EVM_TOKENPRICES_ETHEREUM.DONE ethereum token meta + prices done 2026-09-30T21:20:05Z tokens=3256
EVM_TOKENPRICES_POLYGON.DONE  polygon token meta + prices done 2026-09-30T21:20:50Z tokens=333
BSC_CENSUS.DONE               2026-09-30T21:08:09Z
SOL_SAMPLE.DONE               2026-09-30T21:45:55Z done: {"txs_nonvote_parts":["txs-nonvote-001.csv.gz"],"txs_nonvote_rows":348614,"dex_txs_parts":["dex-txs-001.jsonl.gz","dex-txs-002.jsonl.gz"],"dex_txs_rows":155170,"programs":897,"mints":2853}
SOL_JITO_TIPFLOOR.DONE        2026-09-30T22:31:07.721111Z 60 successful polls (61 total) in /home/user/dapparb/research-material/06-other-chains-onchain/solana/tip-floor.jsonl
```

## Question lines (verbatim)

1. Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet.
2. Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens.
3. Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit.
4. Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured.
5. V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee.
6. BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents.
7. Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions.
8. So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test.

## Question lines served (mapping only)

`<evm>` stands for each of arbitrum/, optimism/, unichain/, ethereum/, polygon/. "EVM census files" = `<evm>/blocks.csv.gz`, `<evm>/txs-001.csv.gz`, `<evm>/reverted-001.csv.gz`, `<evm>/candidates-001.jsonl.gz`, `<evm>/topic0-counts.csv.gz`, `<evm>/swap-topics.csv`, `<evm>/gaps.csv`, `<evm>/window.json`. "EVM token/price files" = `<evm>/tokens-onchain-meta.csv.gz`, `<evm>/prices-defillama-historical.jsonl.gz`, `<evm>/native-price-chart-defillama.json`, `<evm>/token_prices.fetch.json`. "Solana S and D" are the file groups defined in solana/MANIFEST.md. Each sub-manifest has the same mapping for its own files.

| Line | Files |
|---|---|
| 1 | bsc/dex/dex-address-excerpts.txt; bsc/docs/ ids pancakeswap-infinity-addresses, pancakeswap-infinity-overview, pancakeswap-infinity-hooks-md, uniswap-v4-deployments, uniswap-sdk-core-addresses-ts (`<id>.txt` + `raw/<id>.*`); bsc/census/swap-topics.csv, bsc/census/candidates-00*.jsonl.gz |
| 2 | `<evm>/candidates-001.jsonl.gz`, `<evm>/tokens-onchain-meta.csv.gz` |
| 3 | `<evm>/candidates-001.jsonl.gz`, `<evm>/tokens-onchain-meta.csv.gz`; Solana S and D |
| 4 | EVM census files, EVM token/price files, `<evm>/defillama-dexs.json` (+ `.fetch.json`); bsc/census/* (incl. local-only bsc/census/raw/), bsc/dex/*, bsc/docs/ ids with Q4 in bsc/docs/index.csv; Solana S and D, solana/tip-floor.jsonl, solana/snapshots/*, solana/defillama-dexs.json, solana/docs/, solana/docs/literature/ |
| 5 | `<evm>/candidates-001.jsonl.gz`, `<evm>/blocks.csv.gz`, `<evm>/txs-001.csv.gz`; arbitrum/docs/, optimism/docs/, unichain/docs/, arbitrum/arbitrum-chain-state.json, arbitrum/extra-timeboost-auction-logs.jsonl.gz; bsc/census/txs-001.csv.gz, bsc/census/candidates-00*.jsonl.gz, bsc/census/swap-topics.csv, bsc/census/raw/ (local-only), bsc/builder/builder-material-001.jsonl.gz, bsc/dex/dex-address-excerpts.txt, bsc/docs/ ids with Q5; Solana S and D, solana/tip-floor.jsonl, solana/snapshots/jito__* |
| 6 | arbitrum/docs/, arbitrum/arbitrum-chain-state.json, arbitrum/extra-timeboost-auction-logs.jsonl.gz, arbitrum/txs-001.csv.gz; optimism/docs/; unichain/docs/; ethereum/blocks.csv.gz; bsc/census/{window.json, blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-00*.jsonl.gz}, bsc/census/raw/ (local-only), bsc/builder/*, bsc/builders.csv, bsc/validators-onchain.csv, bsc/validator-mev-rpc-probe.jsonl.gz, bsc/docs/excerpts.txt, bsc/docs/ ids with Q6; solana/tip-floor.jsonl, solana/snapshots/jito__*, solana/snapshots/rpc__getVoteAccounts.json.gz, solana/snapshots/rpc__getClusterNodes.json.gz, solana/data/jito-bundles-by-slot.jsonl.gz, solana/slots.csv.gz, solana/docs/ |
| 7 | EVM census files, EVM token/price files; bsc/census/{txs-001.csv.gz, reverted-001.csv.gz, candidates-00*.jsonl.gz, swap-topics.csv, topic0-inventory.csv.gz, topic0-signatures.csv.gz}, bsc/census/raw/ (local-only); Solana S and D, solana/snapshots/defillama__*, solana/defillama-dexs.json, solana/snapshots/jito__kobe.mainnet.jito.network_api_v1_daily_mev_rewards.json.gz, solana/docs/literature/ |
| 8 | EVM census files; Solana S and D |

## Verified inventory (2026-10-01)

Every file in this folder was verified on 2026-10-01 by streaming (peak memory of the check below 100 MB; no data file was modified): `gzip -t` on all 866 .gz files (all pass); CSV files parsed with Python's csv module; every JSONL line and every JSON document parsed (all parse); sha256 of every file (all files are under 100 MB). Per-file tables (file, bytes, rows/lines, sha256, committed or local-only) are in the 'Verified inventory (2026-10-01)' section of each sub-manifest; `_shared_collect/` is in MANIFEST-evm.md; the per-file list of the three large Solana local-only directories is `solana/local-only-inventory.tsv`. All row counts stated by the collectors match the verified counts; the one count the collectors had left open (`solana/tip-floor.jsonl`, 61 lines) is now filled in.

Files in this directory itself:

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| MANIFEST.md | (this file) | documentation | not recorded (written 2026-10-01) | committed |
| MANIFEST-evm.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |

Per directory (as collected, before the 2026-10-01 documentation edits):

| Directory | Committed files | Committed bytes | Local-only files | Local-only bytes | Per-file table |
|---|---:|---:|---:|---:|---|
| arbitrum/ | 67 | 11,582,523 | 0 | 0 | arbitrum/MANIFEST.md |
| optimism/ | 46 | 23,362,553 | 0 | 0 | optimism/MANIFEST.md |
| unichain/ | 50 | 2,783,134 | 0 | 0 | unichain/MANIFEST.md |
| ethereum/ | 27 | 102,301,716 | 0 | 0 | ethereum/MANIFEST.md |
| polygon/ | 27 | 98,412,300 | 0 | 0 | polygon/MANIFEST.md |
| _shared_collect/ | 9 | 93,963 | 1 | 33,356 | MANIFEST-evm.md |
| bsc/ | 232 | 180,048,257 | 40 | 434,972,682 | bsc/MANIFEST.md |
| solana/ | 189 | 182,557,589 | 1,280 | 573,759,195 | solana/MANIFEST.md and solana/local-only-inventory.tsv |
| (this directory) | 1 | 7,264 | 0 | 0 | above |
| total | 648 | 601,149,299 | 1,321 | 1,008,765,233 | |

Local-only files and where their regeneration is described:

| Local-only path | Files | Bytes | Regeneration described in |
|---|---:|---:|---|
| bsc/census/raw/ | 40 | 434,972,682 | bsc/MANIFEST.md, 'Verified inventory (2026-10-01)' (`collect/download.py`; needs an RPC endpoint with history for the window) |
| solana/data/raw-slots/ | 600 | 564,677,263 | solana/MANIFEST.md, 'Verified inventory (2026-10-01)' (`collect/sol_fetch.py` with the reproduced `pin.json`; needs an RPC endpoint with history for the slots) |
| solana/data/jito-bundles-by-slot.parts/ | 600 | 8,577,414 | solana/MANIFEST.md (exact offline rebuild from the committed `data/jito-bundles-by-slot.jsonl.gz`) |
| solana/data/prices.parts/ | 72 | 396,869 | solana/MANIFEST.md (exact offline rebuild from the committed `prices-defillama-historical.jsonl.gz`) |
| solana/collect/state/pin.json | 1 | 551 | solana/MANIFEST.md (content reproduced verbatim) |
| _shared_collect/__pycache__/, solana/collect/__pycache__/ | 8 | 140,454 | MANIFEST-evm.md, solana/MANIFEST.md (Python bytecode caches, recreated on import) |
