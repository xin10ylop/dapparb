# 06-other-chains-onchain: on-chain raw material for chains other than Base (folder index)

Status: COMPLETE WITH GAPS (finalized 2026-10-01). All 13 collectors of this folder wrote a DONE sentinel and none wrote FAILED (sentinel text below). The last data file in this folder was written at 2026-09-30T22:30Z, before the ~23:00Z container restart of 2026-09-30; no collector of this folder was interrupted or re-run. Gaps (details in the sub-manifests):
* Unichain: 1 documentation URL not retrieved (Wayback Machine copy, HTTP 403).
* BSC: 5 of 28 swap topics not observed in the window (unverified on BSC); 11 of 44 validator MEV RPC entries did not answer `mev_params`; 5 of 92 documentation entries have no page content (network error, HTTP 429, HTTP 404).
* Solana: 1 of 61 Jito tip-floor polls failed (connection reset); for 15 of 600 slots the Jito bundles endpoint answered HTTP 404 "Bundle not found" (stored verbatim); 4 documentation URLs not retrieved.
* Local-only (git-ignored, not in the repository): `bsc/census/raw/` (40 files), `solana/data/raw-slots/` (600 files), `solana/data/jito-bundles-by-slot.parts/` (600 files), `solana/data/prices.parts/` (72 files), `solana/collect/state/pin.json`, and 8 Python bytecode caches in `__pycache__/` directories. How to regenerate each is in the sub-manifest that lists it.

Correction 2026-10-01 (other-l2-censuses): the statements above about "13 collectors" and "the last data file ... 2026-09-30T22:30Z" describe the folder before 2026-10-01T04:10Z. Between 2026-10-01T04:10Z and 04:40Z the other-l2-censuses collection added six chain directories (ink/, mantle/, abstract/, worldchain/, zksync/, soneium/), five top-level files and `collect/`. It wrote 12 more DONE sentinels and no FAILED sentinel; details are in the section 'Additional L2 censuses (2026-10-01)' at the end of this file. The file counts and totals in this file before that section do not include these files.

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
| ink/ (added 2026-10-01) | Ink census, 60 min, blocks 57326299-57329898; token/prices; ordering docs + excerpts | ink/MANIFEST.md | COMPLETE | 0 (45 files, not yet committed, none git-ignored) | 0 |
| mantle/ (added 2026-10-01) | Mantle census, 60 min, blocks 101347199-101348998; token/prices; ordering docs + excerpts | mantle/MANIFEST.md | COMPLETE | 0 (55 files, not yet committed, none git-ignored) | 0 |
| abstract/ (added 2026-10-01) | Abstract census, 60 min, blocks 86310808-86315526; token/prices; ordering docs + excerpts | abstract/MANIFEST.md | COMPLETE | 0 (45 files, not yet committed, none git-ignored) | 0 |
| worldchain/ (added 2026-10-01) | World Chain census, 60 min, blocks 35744536-35746335; token/prices; ordering (PBH) docs + excerpts | worldchain/MANIFEST.md | COMPLETE | 0 (58 files, not yet committed, none git-ignored) | 0 |
| zksync/ (added 2026-10-01) | ZKsync Era census, 60 min, blocks 72284916-72285498; token/prices; ordering docs + excerpts | zksync/MANIFEST.md | COMPLETE | 0 (53 files, not yet committed, none git-ignored) | 0 |
| soneium/ (added 2026-10-01) | Soneium census, 60 min, blocks 28844980-28846779; token/prices; ordering docs + excerpts | soneium/MANIFEST.md | COMPLETE | 0 (45 files, not yet committed, none git-ignored) | 0 |
| collect/ and 5 top-level files (added 2026-10-01) | L2 selection (selection.csv, DefiLlama all-chains overview, per-chain totals, receipts probe) and the masters of the L2 wrapper scripts | this file, section 'Additional L2 censuses (2026-10-01)' | COMPLETE | 0 (14 files, not yet committed, none git-ignored) | 0 |

Totals as verified on 2026-10-01: 1,969 files as collected, 648 committed and 1,321 local-only (1,008,765,233 bytes local-only). Two documentation files were added on 2026-10-01: this MANIFEST.md and `solana/local-only-inventory.tsv`. The largest committed file is `bsc/census/candidates-001.jsonl.gz` (83,906,821 bytes); no committed file exceeds 90 MB.

Not in this folder: Base (other research-material folders); live engine runs for other chains (research-material/07-other-chains-engine, sentinels ENGINE_DETECT_* and ENGINE_LIVE_*); chains other than the seven above (for example Blast, Linea, zkSync, Scroll, Mantle, Avalanche, Sonic, Sui, Aptos, TON).

Correction 2026-10-01 (other-l2-censuses): zkSync (ZKsync Era, zksync/) and Mantle (mantle/) are now in this folder, together with Ink (ink/), Abstract (abstract/), World Chain (worldchain/) and Soneium (soneium/); see the section 'Additional L2 censuses (2026-10-01)'. Blast, Linea and Scroll were candidates but were not selected (`selection.csv`).

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
| 4 | `selection.csv` (added 2026-10-01) |
| 4 | `defillama-overview-dexs-all-chains.json.gz` (added 2026-10-01) |
| 4 | `defillama-overview-dexs-all-chains.fetch.json` (added 2026-10-01) |
| 4 | `defillama-overview-dexs-candidates.jsonl.gz` (added 2026-10-01) |
| 4 | `rpc-receipts-probe-candidates.jsonl.gz` (added 2026-10-01) |
| 4, 5, 7, 8 | `<l2>/blocks.csv.gz` (added 2026-10-01) |
| 4, 5, 7, 8 | `<l2>/txs-001.csv.gz` (added 2026-10-01) |
| 4, 7, 8 | `<l2>/reverted-001.csv.gz` (added 2026-10-01) |
| 2, 3, 4, 5, 7, 8 | `<l2>/candidates-001.jsonl.gz` (added 2026-10-01) |
| 4, 7, 8 | `<l2>/topic0-counts.csv.gz` (added 2026-10-01) |
| 4, 7, 8 | `<l2>/swap-topics.csv` (added 2026-10-01) |
| 4, 7, 8 | `<l2>/gaps.csv` (added 2026-10-01) |
| 4, 7, 8 | `<l2>/window.json` (added 2026-10-01) |
| 2, 3, 4, 7 | `<l2>/tokens-onchain-meta.csv.gz` (added 2026-10-01) |
| 4, 7 | `<l2>/prices-defillama-historical.jsonl.gz` (added 2026-10-01) |
| 4, 7 | `<l2>/native-price-chart-defillama.json` (added 2026-10-01) |
| 4, 7 | `<l2>/token_prices.fetch.json` (added 2026-10-01) |
| 4 | `<l2>/defillama-dexs.json` (added 2026-10-01) |
| 4 | `<l2>/defillama-dexs.fetch.json` (added 2026-10-01) |
| 5, 6 | `<l2>/docs/` (page texts, raw bodies, index.csv; added 2026-10-01) |
| 5, 6 | `<l2>/docs/excerpts.jsonl` (added 2026-10-01) |
| none | `<l2>/collect/`, `collect/` (scripts and logs; added 2026-10-01) |

Rows marked "added 2026-10-01" were added by the other-l2-censuses collection; there is one row per new file or per file pattern. `<l2>` stands for each of ink/, mantle/, abstract/, worldchain/, zksync/, soneium/. Each `<l2>/MANIFEST.md` has the same mapping for its own files.

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

## Additional L2 censuses (2026-10-01)

Added by the other-l2-censuses collection (2026-10-01, 04:10-04:40Z). It addresses the part of question line 4 that says "the other L2s were not measured". It adds on-chain arbitrage censuses for six further chains, chosen by DefiLlama 24 h DEX volume from a fixed candidate list. Raw material only; nothing below interprets the data.

### Selection (`selection.csv`)

* Candidates (fixed list given to the collector): Linea, Scroll, ZKsync Era, Blast, Mantle, Ink, Soneium, World Chain, Abstract, Taiko, Mode. The collector did not check independently whether each candidate is an Ethereum L2 rollup. Chains outside this list were not considered; the saved overview's `allChains` array lists every chain DefiLlama tracks.
* Volume source: `https://api.llama.fi/overview/dexs?excludeTotalDataChart=true`, fetched 2026-10-01T04:16:42Z (HTTP 200, 19,891,380 bytes uncompressed). It is stored gzip-compressed, unmodified, as `defillama-overview-dexs-all-chains.json.gz`; URL, time, status, size and sha256 of the uncompressed body are in `defillama-overview-dexs-all-chains.fetch.json`. That response has no per-chain total, so `breakdown24h_sum_derived` is the exact (Python Decimal) sum over all protocols of `protocols[].breakdown24h[<chain key>]`.
* Each candidate's per-chain overview `https://api.llama.fi/overview/dexs/<slug>?excludeTotalDataChart=true` was fetched 2-14 s later. Its raw body is in `defillama-overview-dexs-candidates.jsonl.gz` and its `total24h` field is in column `per_chain_total24h`. Ordering by either column gives the same order of the 11 candidates.
* Receipts probe: each candidate's public HTTP JSON-RPC endpoints were called with eth_chainId, eth_blockNumber and eth_getBlockReceipts(head - 5), one JSON line per endpoint in `rpc-receipts-probe-candidates.jsonl.gz`. `receipts_served_derived` = HTTP 200, a list of receipts whose blockNumber equals the probed block, and the expected chain id. All 11 candidates had at least one endpoint that served receipts, so no candidate was skipped for that reason. Endpoints that did not serve them: worldchain-mainnet.g.alchemy.com/public (HTTP 401 'Only core evm requests are allowed.') and worldchain.drpc.org (HTTP 500 at probe time).
* Rule: order by `breakdown24h_sum_derived` (descending) and select the first 6 candidates with at least one endpoint in `receipts_endpoints_ok`.

| rank | chain | breakdown24h_sum_derived (USD) | per_chain_total24h (USD) | selected | dir |
|---:|---|---:|---:|---|---|
| 1 | Ink | 3279882 | 3213379 | true | ink/ |
| 2 | Mantle | 2489796.74 | 2489796.74 | true | mantle/ |
| 3 | Abstract | 1580386 | 1580386 | true | abstract/ |
| 4 | World Chain | 730528.10 | 730528.1 | true | worldchain/ |
| 5 | ZKsync Era | 592483.71 | 592483.71 | true | zksync/ |
| 6 | Soneium | 364761.82 | 364761.82 | true | soneium/ |
| 7 | Linea | 364646.71 | 364646.70999999996 | false |  |
| 8 | Scroll | 354769.56 | 354769.56 | false |  |
| 9 | Blast | 36547.07 | 36547.07 | false |  |
| 10 | Mode | 1547.16 | 1547.16 | false |  |
| 11 | Taiko | 132.59 | 132.59 | false |  |

Columns of selection.csv: volume_rank_derived, defillama_chain (name as in `allChains`), defillama_breakdown24h_key, in_overview_allChains, breakdown24h_sum_derived, breakdown24h_entries_derived (number of protocol entries summed), per_chain_total24h (raw field), per_chain_url, per_chain_fetched_at_utc, chain_id, receipts_endpoints_ok, receipts_endpoints_not_ok (`;`-separated), selected, census_dir. Volumes are written as the decimal strings of the JSON numbers, without rounding.

Fields of `defillama-overview-dexs-candidates.jsonl.gz`: chain, url, fetched_at_utc, http_status, exception, response (raw JSON body). Fields of `rpc-receipts-probe-candidates.jsonl.gz`: chain, expected_chain_id, endpoint, eth_chainId / eth_blockNumber (at_utc, http_status, result or error verbatim), probe_block, eth_getBlockReceipts (at_utc, http_status, error verbatim if any, result_derived = {n_receipts, receipt_block_numbers, receipt_fields_of_first}; the receipts themselves are not stored), chain_id_matches_derived, receipts_served_derived.

### Censuses

Same shared definition and scripts as the five chains in `MANIFEST-evm.md`: eth_getBlockReceipts + eth_getBlockByNumber(block,false) for every block of a contiguous 60-minute window of chain time, criteria A/B, swap-topics from `_shared_collect/swap_signatures.csv` (22 rows on every chain), token metadata + DefiLlama prices, and the per-chain DefiLlama DEX JSON. census.py and token_prices.py are unmodified copies (identical md5). They keep their chain settings in hard-coded dicts, so `collect/census_l2.py` and `collect/token_prices_l2.py` add the entries of `collect/l2_config.py` at run time and call the unmodified `main()`. All six windows were pinned between 2026-10-01T04:18:40Z and 04:18:42Z. Each chain directory's MANIFEST.md has the schemas, endpoints, request and error counts, docs table, excerpts, chain notes, coverage limits and a verified per-file inventory.

| Chain | Dir | Chain id | Window (chain time, UTC) | Blocks | Measured block interval | Txs | Status-0 txs | Candidates A / B | Tokens | Gap blocks | Docs URLs / excerpts |
|---|---|---:|---|---|---:|---:|---:|---|---:|---:|---|
| Ink | ink/ | 57073 | 2026-10-01T03:18:30Z to 2026-10-01T04:18:29Z | 57326299 to 57329898 (3600) | 1.0000 s | 23,691 | 508 | 170 / 228 | 46 | 0 | 4 / 5 |
| Mantle | mantle/ | 5000 | 2026-10-01T03:18:30Z to 2026-10-01T04:18:28Z | 101347199 to 101348998 (1800) | 2.0000 s | 2,444 | 47 | 19 / 19 | 12 | 0 | 9 / 9 |
| Abstract | abstract/ | 2741 | 2026-10-01T03:18:33Z to 2026-10-01T04:18:32Z | 86310808 to 86315526 (4719) | 0.7628 s | 6,416 | 21 | 62 / 323 | 24 | 0 | 4 / 5 |
| World Chain | worldchain/ | 480 | 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z | 35744536 to 35746335 (1800) | 2.0000 s | 27,246 | 199 | 769 / 2885 | 445 | 0 | 9 / 12 |
| ZKsync Era | zksync/ | 324 | 2026-10-01T03:18:09Z to 2026-10-01T04:18:08Z | 72284916 to 72285498 (583) | 6.1838 s | 624 | 22 | 22 / 222 | 24 | 0 | 8 / 7 |
| Soneium | soneium/ | 1868 | 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z | 28844980 to 28846779 (1800) | 2.0000 s | 21,002 | 106 | 481 / 115 | 31 | 0 | 4 / 4 |

Every window: parent-hash breaks 0, blocks missing 0, first/last block hash re-read and matched (window.json `checks`). Every docs URL answered HTTP 200.

### Sentinels (verbatim, read 2026-10-01)

```
EVM_CENSUS_INK.DONE             ink census complete 2026-10-01T04:18:52Z blocks 57326299-57329898 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/ink
EVM_TOKENPRICES_INK.DONE        ink token meta + prices done 2026-10-01T04:20:11Z tokens=46
EVM_CENSUS_MANTLE.DONE          mantle census complete 2026-10-01T04:19:38Z blocks 101347199-101348998 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/mantle
EVM_TOKENPRICES_MANTLE.DONE     mantle token meta + prices done 2026-10-01T04:20:16Z tokens=12
EVM_CENSUS_ABSTRACT.DONE        abstract census complete 2026-10-01T04:19:21Z blocks 86310808-86315526 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/abstract
EVM_TOKENPRICES_ABSTRACT.DONE   abstract token meta + prices done 2026-10-01T04:20:22Z tokens=24
EVM_CENSUS_WORLDCHAIN.DONE      worldchain census complete 2026-10-01T04:19:51Z blocks 35744536-35746335 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/worldchain
EVM_TOKENPRICES_WORLDCHAIN.DONE worldchain token meta + prices done 2026-10-01T04:31:41Z tokens=445
EVM_CENSUS_ZKSYNC.DONE          zksync census complete 2026-10-01T04:18:44Z blocks 72284916-72285498 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/zksync
EVM_TOKENPRICES_ZKSYNC.DONE     zksync token meta + prices done 2026-10-01T04:24:44Z tokens=24
EVM_CENSUS_SONEIUM.DONE         soneium census complete 2026-10-01T04:18:52Z blocks 28844980-28846779 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/soneium
EVM_TOKENPRICES_SONEIUM.DONE    soneium token meta + prices done 2026-10-01T04:24:49Z tokens=31
```

### Commands

```bash
export PATH=/root/.foundry/bin:$PATH
M=/home/user/dapparb/research-material/06-other-chains-onchain
cd $M/collect && python3 -B select_l2_chains.py > select_l2_chains.log 2>&1   # overview, per-chain totals, receipts probe, selection.csv
for c in ink mantle abstract worldchain zksync soneium; do   # per chain (copies of the shared scripts + wrappers in $M/$c/collect/)
  cd $M/$c/collect && python3 -B make_swap_topics.py $c .. > make_swap_topics.log 2>&1
  setsid nohup python3 -B census_l2.py --chain $c --out .. > census.log 2>&1 < /dev/null &
done
# after the censuses: per-chain DefiLlama JSON (fetch_defillama.py <slug>), docs (fetch_docs.py), excerpts (make_doc_excerpts.py), manifest (write_manifest_l2.py)
cd $M/collect && setsid nohup ./run_token_prices_l2.sh > run_token_prices_l2.log 2>&1 < /dev/null &   # token_prices_l2.py for the six chains in sequence
```

Smoke test before launch: census_l2.py `--smoke 25 --seg-blocks 10 --part-limit-mb 0.02` for all six chains in the scratchpad (outputs inspected by hand, not kept).

### Run history and coverage limits (set level)

* One 60-minute window per chain, 2026-10-01 between 03:18Z and 04:18Z (ZKsync Era from 03:18:09Z). The five earlier EVM windows are 2026-09-30 20:07-21:07Z (Ethereum 6 h ending 21:06Z), so the two sets are from different hours and days.
* `collect/run_token_prices_l2.log` holds one line, 'Terminated'. The collector stopped the World Chain token step in that run (endpoint rate limits) and re-ran it separately. The World Chain token metadata step ran four times; only run 4 wrote the stored files (worldchain/MANIFEST.md, chain-specific notes). The census windows were not affected.
* `collect/l2_config.py` was edited twice after the censuses had finished, only in `TOKEN_CFG['worldchain']` (eth_call endpoint order). The census settings (`CENSUS_CHAINS`) used by the runs are the ones in the file and are also stored in each window.json `config`.
* ZKsync Era and Abstract docs: the system-contracts page was fetched in a second fetch_docs.py call (04:33Z), appended to docs/index.csv and docs.log.
* Not collected for these chains: engine runs or live search, block scans with the repository scanner, call traces, mempool or private-orderflow data, flashblock/subblock streams, calldata.
* `research-material/README.md` (outside this folder) was not edited by this collection; its sections on line 4 and on this folder do not mention these six chains.

### Verified inventory of the new top-level files (2026-10-01)

Streamed and parsed as in the sub-manifests (gzip read to the end, JSON/JSONL/CSV parsed, sha256 over the stored bytes). Git column = `git check-ignore` result; nothing was committed by this collection. Per-file inventories of the six chain directories are in their MANIFEST.md files.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| selection.csv | 2,892 | 11 rows + header | b0462c0bf3a6088ca2f70ca666faabad109d293ed5fe8cbe307c8d51e6a4d869 | not ignored |
| defillama-overview-dexs-all-chains.json.gz | 5,057,262 | 1 JSON document (gzip) | a51a7a4e34b354b57c685a9cf4c972a2f5df6004ef4893209c27d8ac86c40807 | not ignored |
| defillama-overview-dexs-all-chains.fetch.json | 363 | 1 JSON document | 8ccee7afa3a72ed48af9f9a425148e4ef4fa2bc7c759d3578b4c06ef33564512 | not ignored |
| defillama-overview-dexs-candidates.jsonl.gz | 566,728 | 11 JSON lines | c6fe09654964caa86e426c2ad51408e2d09272e1ada384931deba7d5c19e91a5 | not ignored |
| rpc-receipts-probe-candidates.jsonl.gz | 1,899 | 33 JSON lines | 22878e83da811b1a9ed7d32cf6f1b75dd7e4635774ff9ae4393b7fd53173154e | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/run_token_prices_l2.log | 11 | 1 line | b4a6c06672677cf0e25ec72bec83beae33305cee4b8087f168962014373b02bb | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/select_l2_chains.log | 3,366 | 46 lines | 850064fb69442a6965f473db12c297d959d5184384f3d34342476c9b1062c6de | not ignored |
| collect/select_l2_chains.py | 11,114 | 200 lines | 778a35f10952f0503e507dde5672d4e3b6832bf7af1e3b9ea40d1757dc94be28 | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |

Six chain directories: 301 files, 15,688,517 bytes in total (each incl. its MANIFEST.md). Largest new file: `defillama-overview-dexs-all-chains.json.gz` (5,057,262 bytes); no new file exceeds 90 MB. No new file is git-ignored.
