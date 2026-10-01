# research-material: raw material for the eight question lines

Entry point for the analysis session. Written 2026-10-01 from the folder manifests and a completeness check of the
collection. Paths in this file are relative to `research-material/` unless they start with `bot/` or `docs/` (repository
root).

## 1. Purpose

This folder holds raw material collected on 2026-09-30 and 2026-10-01 for the eight question lines in section 2. The
analysis is left to the reader. Nothing in this README or in the folder manifests interprets the data. It holds no
statistics, findings or rankings, and it does not judge whether any question line is right or wrong. It says what was
collected, where, how, and what is missing.

Some files contain other people's conclusions: papers and docs in `08-sources/`, the earlier session's
`docs/ANALYSIS.md`, and two prose files inside data folders (see section 7.3). Treat these as claims to check, not as data.

How to use it: pick a line in section 3. Open the files listed there. Then read the folder's `MANIFEST.md` for
schemas, methods and the full per-file inventory (bytes, row counts, sha256).

## 2. Question lines (verbatim)

1. 'Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet.'
2. 'Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens.'
3. 'Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit.'
4. 'Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured.'
5. 'V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee.'
6. 'BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents.'
7. 'Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions.'
8. 'So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test.'

Other key schemes used inside the folders:
- `08-sources` uses `Q1-V4GAP`, `Q2-OLDV2`, `Q3-SMALLPOOLS`, `Q4-OTHERCHAINS`, `Q5-V4LAUNCH`, `Q5-CONTEST`, `Q6-BSCORDER`,
  `Q7-CHAINWIDE-METHOD`, `Q7-ARB-4700`, `Q7-BASE-21M`, `Q7-PROFIT-28` and `Q8-V4MEASURE` (field `question_line` in
  `excerpts.jsonl`).
- `06-other-chains-onchain/MANIFEST-evm.md` uses `Q-V4BASE` … `Q-COVERAGE`, plus `Q-GAPS`, which is not one of the eight lines.
- Some manifests note older Q1-Q10 numberings and give the mapping to line numbers. Every manifest now has a "Question lines
  served" table by line number.

## 3. Line-by-line map

Each line is split into claim parts. For each part the map lists the files that hold the material and a coverage note that
describes the material and its limits. Notation:
- "(local-only)" marks files that are not in the repository (section 6).
- `excerpts.jsonl (KEY)` means the records of `08-sources/excerpts.jsonl` with that `question_line` key.
- "§x.y" refers to sections of `docs/ANALYSIS.md`.

### Line 1: Uniswap V4 on Base

**Part: V4 on Base is "the biggest gap" compared with the other unmeasured areas**
- Files: `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/run-times.json`,
  `02-v4-live-test/prior/live-base-all.jsonl.gz`, `02-v4-live-test/prior/dry-all.log.gz`, `04-shallow-pools/live-shallow.jsonl`,
  `04-shallow-pools/live-shallow.log`, `03-v2-older-pairs/pools-part-0001.csv.gz`, `03-v2-older-pairs/census-logs-part-0001.csv.gz`,
  `07-other-chains-engine/engine-detect/arbitrum/`, `07-other-chains-engine/engine-detect/mainnet/`,
  `06-other-chains-onchain/*/candidates-*.jsonl.gz`
- Coverage: This is a comparison, and each gap was collected with a different method and window.
  - V4: one 20-minute dry engine run (2026-10-01 02:36-02:56Z).
  - Shallow pools: one 20-minute dry run at `--min-depth-eth 0.001` (2026-09-30 22:03-22:23Z).
  - Older V2 pairs: a pinned-block snapshot of a random sample plus a 24 h event census, with no engine run.
  - Other chains: single-window on-chain censuses, plus detection-only engine runs without simulation on Arbitrum and Ethereum.

  No common measure across the gaps was collected.

**Part: Clanker and Zora launch new tokens as V4 pools with hooks**
- Files: `01-v4-pools/initialize-compact/pools-part-0001..0008.csv.gz`, `01-v4-pools/initialize-compact/hooks.csv`,
  `01-v4-pools/collect/expand_initialize.py`, `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/hooks.csv`,
  `01-v4-pools/hook-labels-long.csv`, `01-v4-pools/hook-pool-counts-all.csv.gz`, `01-v4-pools/hook-docs/launch-tx-samples-tx.csv.gz`,
  `01-v4-pools/hook-docs/launch-tx-samples-logs.csv.gz`, `01-v4-pools/hook-docs/zora-hook-registry-events.csv`,
  `01-v4-pools/hook-docs/zora-hook-registry-logs.jsonl.gz`, `01-v4-pools/hook-docs/uniswap-hooklist-base.jsonl.gz`,
  `01-v4-pools/hook-docs/blockscout/`, `01-v4-pools/hook-docs/text/` (`clanker.gitbook.io_*`, `docs.zora.co_*`, clanker-devco and
  ourzora sources), `08-sources/texts/clanker-docs-v4*.txt.gz`, `08-sources/texts/zora-docs-coins-hook.txt.gz`,
  `08-sources/texts/clanker-paragraph-v4-1-sniper-tech.txt.gz`, `excerpts.jsonl (Q1-V4GAP)`
- Coverage: Every PoolManager Initialize event from the deployment block 25,350,988 to 52,006,302, plus a 7-day window to
  52,006,432, with the hook address of each pool.
  - Launchpad labels come from docs, registries and Blockscout, applied with a fixed precedence. They exist only for hooks with
    at least 20 pools or another label source (1,198 of 74,887 hook addresses).
  - Launch-tx samples: at most 3 per hook, for 213 hooks.
  - Not collected: a census of launchpad factory or token-creation events.

**Part: "I only had 20 V4 pools"**
- Files: `00-prior-runs/engine-runs/dry-all.log.gz`, `00-prior-runs/engine-runs/dry-all-v0.log.gz`,
  `00-prior-runs/engine-runs/dry-blocks-long5.log.gz`, `00-prior-runs/misc/geckoterminal-top-pools-base.json.gz`,
  `02-v4-live-test/prior/dry-all.log.gz`, `02-v4-live-test/prior/dry-all-v0.log.gz`, `04-shallow-pools/live-shallow.log`,
  `04-shallow-pools/collect/snapshot.log`, `04-shallow-pools/geckoterminal-responses.jsonl.gz`,
  `04-shallow-pools/pools-prefilter.csv.gz` (`is_v4` rows), `07-other-chains-engine/scans/base/*.log.gz`,
  `07-other-chains-engine/scans/base/*.meta.json`
- Coverage: The engine logs record the GeckoTerminal V4 discovery counters: `uniswap v4 candidates` (listed / v4) and
  `uniswap v4 pools discovered` (listed / kept / hooked / outOfUniverse). These counters exist for:
  - the §2.6 runs (2026-09-30 16:37-17:25Z);
  - the §2.5 run, the shallow run and the 07 scans, with their own values.

  GeckoTerminal listings are live at request time and not tied to a block. The raw GeckoTerminal responses seen by the §2.6
  runs were not saved. Only two sets of responses exist: a top-pools page from ~10:41Z (`00-prior-runs/misc/`) and the 04
  snapshot responses from ~22:04Z.

**Part: "The engine supports V4"**
- Files: `02-v4-live-test/MANIFEST.md` (sections "Engine changes" and the loader table), `02-v4-live-test/live-v4.log`,
  `02-v4-live-test/live-v4.jsonl`, `00-prior-runs/engine-runs/live-base-all.jsonl.gz`, `04-shallow-pools/pools-prefilter.csv.gz`
  (`fee_by_dir_*` columns), `04-shallow-pools/cl-ticks-prefilter.csv.gz`
- Coverage: The engine searches only the V4 pools it can price locally (the existing `isPriceable`, described in the 02 loader
  table). These are static-fee pools whose hook has no swap or return-delta permission bits.
  - Dynamic-fee pools and hook-swap-flag pools are counted (`droppedDynamicFee`, `droppedHookSwapFlags`) but not searched.
  - The engine source (`bot/src/pools/v4.ts`, `bot/src/pools/v4file.ts`) is in the repository, not in research-material.

**Part: "It just doesn't list every V4 pool yet"**
- Files: `00-prior-runs/engine-runs/dry-all.log.gz`, `02-v4-live-test/run-times.json`, `02-v4-live-test/live-v4.log`
  (`v4 pools loaded from file`), `02-v4-live-test/initialize-topup.csv.gz`, `02-v4-live-test/initialize-topup.json`,
  `01-v4-pools/initialize-parts.json`, `01-v4-pools/initialize-compact/`
- Coverage: In the earlier session the engine listed V4 pools through GeckoTerminal (`discoverV4Pools`).
  - During this collection, the opt-in flag `--v4-pools` was added (commit `5c1baf2`, 2026-10-01). It loads every Initialize
    event from files, and the V4LIVE run used it.
  - Pools initialized after the top-up pin (block 52,015,481) or during the run are not in that list.

### Line 2: Older V2 pairs

**Part: "I took the newest 6,000" (pairs per V2-style factory)**
- Files: `00-prior-runs/engine-runs/dry-all.log.gz`, `00-prior-runs/engine-runs/dry-all-v0.log.gz`, `03-v2-older-pairs/factories.csv`,
  `03-v2-older-pairs/uniswapv2-sample-indices.csv.gz`, `04-shallow-pools/factory-enumeration.csv.gz`,
  `04-shallow-pools/collect/snapshot.log`, `02-v4-live-test/live-v4.log`
- Coverage: The §2.6 log records the total and enumerated counts per factory (16:55:48-16:55:56Z).
  - 03 rebuilds the enumerated index range from those totals and the newest-first rule in `bot/src/pools/enumerate.ts`. The
    block of each enumeration call was not logged, so it is derived from the log time (±1-2 blocks).
  - 04 has the engine's own newest-6,000 enumeration at block 52,008,246. This is a later pass, not the §2.6 set.

**Part: "of about 3 million Uniswap V2 pairs"**
- Files: `03-v2-older-pairs/factories.csv`, `03-v2-older-pairs/factory-length-history.csv`, `00-prior-runs/engine-runs/dry-all.log.gz`,
  `04-shallow-pools/collect/snapshot.log`, `02-v4-live-test/live-v4.log`, `08-sources/texts/docs-uniswap-v2-deployments.txt.gz`,
  `08-sources/defillama/summary-dexs-uniswap-v2.json.gz`
- Coverage: The UniswapV2 factory's `allPairsLength` on Base was read on-chain at three kinds of block: the pinned block
  52,008,400, the block matching the §2.6 log time, and a 500,000-block grid.
  - Engine logs also give the logged total at other run times: 2026-09-30 16:37Z, 16:55Z and 22:04Z, and 2026-10-01 02:05Z.
  - Base only.

**Part: "Almost all the older ones are abandoned tokens"**
- Files: `03-v2-older-pairs/pools-part-0001.csv.gz` (`sample_group` = `random_sample_older`),
  `03-v2-older-pairs/uniswapv2-sample-indices.csv.gz`, `03-v2-older-pairs/tokens.csv.gz`,
  `03-v2-older-pairs/price-reference-weth-pools.csv.gz`, `03-v2-older-pairs/census-logs-part-0001.csv.gz`,
  `03-v2-older-pairs/activity-pool-hour.csv.gz`, `03-v2-older-pairs/emitters.csv.gz`, `03-v2-older-pairs/buckets.csv`,
  `03-v2-older-pairs/factory-length-history.csv`, `05-base-onchain/data/candidates-*.jsonl.gz`, `05-base-onchain/data/txs-*.csv.gz`,
  `excerpts.jsonl (Q2-OLDV2)`, `08-sources/texts/` (the meme-coin and rug-pull papers listed for line 2 in the 08 MANIFEST)
- Coverage: Older UniswapV2 pairs are a uniform random sample of 60,000 of the 3,057,605 indices below the §2.6 range
  (about 1.96 %).
  - Each pair is read once, at block 52,008,400: reserves, `block_timestamp_last`, LP `totalSupply`, token metadata, and
    direct token/WETH pools on the 11 configured factories.
  - Activity comes from a 24 h census of four V2-style Sync/Swap topics (blocks 51,965,201-52,008,400).
  - The data encodes no definition of "abandoned".
  - Not collected: pair creation times (no PairCreated scan), USD prices, LP-holder or lock data, and the transfer behaviour
    of these tokens.
  - The other V2-style factories are complete at the pinned block.

### Line 3: Pools under 0.1 ETH of liquidity

**Part: the set of pools under 0.1 ETH of liquidity**
- Files: `04-shallow-pools/pools-prefilter.csv.gz`, `04-shallow-pools/pools-pruned-empty.csv.gz`, `04-shallow-pools/prices.csv.gz`,
  `04-shallow-pools/tokens.csv.gz`, `04-shallow-pools/snapshot-meta.json`, `04-shallow-pools/v4-poolmanager-balances.csv.gz`,
  `03-v2-older-pairs/pools-part-0001.csv.gz`, `03-v2-older-pairs/price-reference-weth-pools.csv.gz`,
  `01-v4-pools/state-snapshot.csv.gz`, `01-v4-pools/pool-keys-snapshot.csv.gz`, `02-v4-live-test/live-v4.log`
  (`v4AfterPruneEmpty`, `v4AfterDepthFilter`)
- Coverage: Engine-defined depth (`poolDepthEth` with the anchored price map) is recorded per pool only for the engine
  universe at block 52,008,246. That universe is the newest 6,000 per V2-style factory, all Slipstream pools, the V3 tiers for
  the revealed pairs, and GeckoTerminal-listed V4.
  - The older-V2 sample (03) has raw reserves but no engine depth.
  - V4 pools in 01 have in-range liquidity at block 52,006,432, only for pools active in 24 h or initialized in 7 days.
  - For the V4LIVE run there are only aggregate counters, not per-pool depth.

**Part: "Profit is capped at a slice of a pool's liquidity"**
- Files: `04-shallow-pools/live-shallow.jsonl`, `04-shallow-pools/pools-prefilter.csv.gz`, `04-shallow-pools/cl-ticks-prefilter.csv.gz`,
  `00-prior-runs/engine-runs/live-base-all.jsonl.gz`, `02-v4-live-test/live-v4.jsonl`,
  `08-sources/texts/arxiv-2305.14604-milionis-moallemi-roughgarden-arbitrage-profits-fees.txt.gz`, `excerpts.jsonl (Q3-SMALLPOOLS)`
- Coverage: This is a statement about mechanism. Candidate records give the input size and the predicted and simulated profit
  per route.
  - The pool state in 04 comes from a separate pass at block 52,008,246, not from each candidate's block.
  - Tick data covers only ±3000 ticks around the current tick.

**Part: "so these pay a few dollars at most"**
- Files: `04-shallow-pools/live-shallow.jsonl`, `04-shallow-pools/live-shallow.log`, `04-shallow-pools/run-times.json`,
  `05-base-onchain/data/txs-fw-0001.csv.gz`, `05-base-onchain/data/candidates-fw-0001.jsonl.gz`,
  `05-base-onchain/data/reverted-fw-0001.csv.gz`, `05-base-onchain/blocks.csv.gz`, `03-v2-older-pairs/census-logs-part-0001.csv.gz`
- Coverage: One 20-minute dry run at `--min-depth-eth 0.001`: ready 2026-09-30 22:03:50Z, stop 22:23:51Z, blocks
  ~52,008,242-52,008,842.
  - Pools below 0.001 ETH engine depth, and pools with neither side priced, were not searched.
  - USD values use the engine price map.
  - 05 has receipts for every tx in that window, but logs only for candidate txs.
  - The 03 census overlaps the window only up to block 52,008,400.
  - No repeat windows.

**Part: "They are also where most tokens that block or tax transfers sit"**
- Files: `04-shallow-pools/transfer-probe/transfer-probe.csv.gz`, `04-shallow-pools/transfer-probe/holders.csv.gz`,
  `04-shallow-pools/transfer-probe/probe-batches-raw.jsonl.gz`, `04-shallow-pools/transfer-probe/probe-meta.json`,
  `04-shallow-pools/transfer-probe/collect/src/TransferProbe.sol`, `04-shallow-pools/pools-prefilter.csv.gz`,
  `04-shallow-pools/pools-pruned-empty.csv.gz`, `04-shallow-pools/tokens.csv.gz`, `04-shallow-pools/live-shallow.jsonl` (`sim.error`),
  `00-prior-runs/engine-runs/dry-all.log.gz`, `00-prior-runs/engine-runs/live-base-all.jsonl.gz`, `02-v4-live-test/live-v4.jsonl`,
  `excerpts.jsonl (Q3-SMALLPOOLS)`, `08-sources/texts/arxiv-2309.04700-trapdoor-tokens-uniswap.txt.gz`
- Coverage: The transfer probe simulates one transfer per token at block 52,008,246. The transfer goes from the largest
  non-V4 pool holder to a fresh address, at 1 % and at 0.01 % of the holder's balance.
  - It covers the 33,597 tokens of the shallow-snapshot universe, which includes pools of all depths. 29,703 tokens had a
    holder; the other 3,894 were not probed.
  - Not covered: selling into a pool, `transferFrom` or router paths, tokens of the older V2 pairs (03), and V4 pools outside
    the GeckoTerminal-listed set.
  - Engine simulation reverts exist only for routes the engine selected.

### Line 4: Other chains, live

**Part: "The live search ran only on Base"**
- Files: `00-prior-runs/engine-runs/`, `02-v4-live-test/live-v4.log`, `04-shallow-pools/live-shallow.log`,
  `07-other-chains-engine/engine-detect/arbitrum/`, `07-other-chains-engine/engine-detect/mainnet/`,
  `07-other-chains-engine/collect/engine-blocker-check-arbitrum.log`, `07-other-chains-engine/collect/engine-blocker-check-mainnet.log`,
  `07-other-chains-engine/collect/smoke/selftest-engine-unknown-chain.log`, `07-other-chains-engine/prior-summaries.md`
- Coverage: The earlier session's engine runs (00) are all on Base.
  - New in this collection: 20-minute detection-only runs on Arbitrum (2026-10-01 01:42-02:02Z) and Ethereum (01:41-02:01Z),
    with no `eth_call` simulation.
  - The simulation-based dry run on these chains is blocked without a code change (sentinels `ENGINE_LIVE_*.FAILED`).
  - The engine code accepts only `base`, `arbitrum` and `mainnet`.

**Part: "Block-level scans covered Arbitrum and Ethereum"**
- Files: `00-prior-runs/block-scans/scan-arb.jsonl.gz`, `scan-arb.log.gz`, `scan-arb2.jsonl.gz`, `scan-arb2.log.gz`,
  `scan-mainnet.jsonl.gz`, `scan-mainnet.log.gz`, `scan-base*.gz` (all in `00-prior-runs/block-scans/`),
  `07-other-chains-engine/scans/arbitrum/`, `07-other-chains-engine/scans/mainnet/`, `07-other-chains-engine/scans/base/`,
  `00-prior-runs/research-runs/crosschain.jsonl.gz`
- Coverage: `00-prior-runs/block-scans/` holds the earlier session's raw §2.1 scans (2026-09-30 from ~10:28Z; 12 configured
  tokens on Arbitrum and Ethereum).
  - The flags of each run are in the head of its log.
  - The pairing of `scan-base.jsonl` with run 3 is inferred from file times.

  `07-other-chains-engine/scans/` holds new scans made with the same code: `config` and `top` universes, ~30 minutes each, on
  2026-09-30 22:14-22:49Z and 2026-10-01 01:09-01:48Z. Scans sample heads, not every block, and the Arbitrum and Base runs
  ended on the time cap.

**Part: "BSC, where PancakeSwap is biggest"**
- Files: `06-other-chains-onchain/bsc/dex/defillama-overview-dexs-bsc.json.gz`, `06-other-chains-onchain/bsc/dex/defillama-overview-dexs-bsc.meta.json`,
  `08-sources/defillama/overview-dexs-bsc.json.gz`, `06-other-chains-onchain/bsc/dex/dex-address-excerpts.txt`,
  `06-other-chains-onchain/bsc/docs/pancakeswap-*.txt`, `06-other-chains-onchain/bsc/census/swap-topics.csv`,
  `06-other-chains-onchain/bsc/census/candidates-001.jsonl.gz`, `06-other-chains-onchain/bsc/census/candidates-002.jsonl.gz`,
  `06-other-chains-onchain/bsc/census/topic0-inventory.csv.gz`
- Coverage: DefiLlama DEX volume overviews fetched on 2026-09-30, with daily points through 2026-09-30, and on-chain swap logs
  for one 60-minute window (8,000 blocks).
  - No TVL or liquidity per DEX was collected.
  - Swap topics are matched by topic0 without checking the emitter's factory, and some topic0 values are shared across
    protocols.

**Part: "Solana ... [was] not measured"**
- Files: `06-other-chains-onchain/solana/slots.csv.gz`, `solana/txs-nonvote-001.csv.gz`, `solana/dex-txs-001.jsonl.gz`,
  `solana/dex-txs-002.jsonl.gz`, `solana/jito-tip-transfers.csv.gz`, `solana/data/jito-bundles-by-slot.jsonl.gz`,
  `solana/tip-floor.jsonl`, `solana/snapshots/`, `solana/docs/literature/` (all under `06-other-chains-onchain/`),
  `08-sources/texts/helius-solana-mev-report.txt.gz`, `08-sources/defillama/overview-dexs-solana.json.gz`
- Coverage: New in this collection: 600 consecutive slots (~2 min 39 s, 2026-09-30 21:25:34-21:28:13Z). They hold:
  - non-vote txs, and DEX-program txs (119 program ids);
  - Jito tips and bundles;
  - 61 tip-floor polls over 1 h.

  Not collected: arbitrage identification, profit computation, a live search (the engine is EVM-only) and pool-state
  snapshots. The raw slots are local-only.

**Part: "the other L2s were not measured"**
- Files: `06-other-chains-onchain/optimism/`, `06-other-chains-onchain/unichain/`, `06-other-chains-onchain/polygon/`,
  `06-other-chains-onchain/arbitrum/`, `06-other-chains-onchain/MANIFEST-evm.md`, `excerpts.jsonl (Q4-OTHERCHAINS)`,
  `00-prior-runs/papers-fetched-earlier/optimistic-mev-l2s.txt.gz`
- Coverage: New 60-minute on-chain censuses (2026-09-30 ~20:07-21:07Z) for OP Mainnet, Unichain, Polygon PoS and Arbitrum.
  - Each has receipts for all txs and logs only for candidate txs. The L2s also have ordering docs.
  - No engine runs and no USD profit computation on these chains.
  - Other L2s (Blast, Linea, zkSync, Scroll, Mantle and others) are not covered.

### Line 5: V4 launches, contested flow, the RSR trade

**Part: "V4 launches are the one place a bigger number could appear"**
- Files: `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/run-times.json`, `02-v4-live-test/prior/`,
  `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`, `01-v4-pools/hooks.csv`,
  `05-base-onchain/data/candidates-fw-0003.jsonl.gz`, `00-prior-runs/engine-runs/live-base-all.jsonl.gz`
- Coverage: This part is a forward-looking judgement.
  - The direct measurement is one 20-minute V4LIVE window, which does not search dynamic-fee or hook-swap-flag pools.
  - No run was limited to newly launched pools.
  - Block-level V4 launch activity in 01 covers 24 h only.

**Part: "New launches open large, short-lived price gaps"**
- Files: `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`,
  `01-v4-pools/v4-modify-liquidity-part-0001.csv.gz`, `01-v4-pools/hook-docs/launch-tx-samples-tx.csv.gz`,
  `01-v4-pools/hook-docs/launch-tx-samples-logs.csv.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`, `05-base-onchain/swap-topics.csv`,
  `02-v4-live-test/live-v4.jsonl` (`gapBps`), `excerpts.jsonl (Q5-V4LAUNCH)`, `08-sources/texts/clanker-docs-v4-mev-*.txt.gz`,
  `08-sources/texts/clanker-docs-v4-sniper-auction-v0.txt.gz`, `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.txt.gz`
- Coverage: Complete PoolManager Swap, ModifyLiquidity and Donate events exist only for blocks 51,963,233-52,006,432 (24 h).
  - After that, including the V4LIVE window, V4 swap logs exist only inside 05 candidate txs (criterion A/B).
  - Prices of the same tokens on other venues are available only where candidate-tx logs contain them.
  - Hook-set dynamic fees and anti-snipe state were not collected. The LP fee applied to each swap is in the Swap event.

**Part: "It is also the most fought-over flow on Base"**
- Files: `05-base-onchain/data/txs-*.csv.gz`, `05-base-onchain/data/reverted-*.csv.gz`, `05-base-onchain/blocks.csv.gz`,
  `05-base-onchain/data/candidates-*.jsonl.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`,
  `00-prior-runs/competitor-ledgers/arbers_XDP.json.gz`, `00-prior-runs/competitor-ledgers/arbers_WETHUSDC.json.gz`,
  `excerpts.jsonl (Q5-CONTEST, Q5-V4LAUNCH)`
- Coverage: The 05 census covers Base blocks 51,995,609-52,017,160 (~12 h, 2026-09-30 15:02Z to 2026-10-01 03:01Z). It has
  `tx_index`, `effective_gas_price`, `l1_fee` and `status` for every tx.
  - Priority fee per gas can be derived as `effective_gas_price` minus the block's `base_fee_per_gas`.
  - `maxPriorityFeePerGas`, calldata and traces were not collected outside the 4 RSR blocks.
  - Reverted txs carry no logs, so their target pools are not identified.
  - No mempool, dropped or private txs.
  - Competitor sender lists exist only for two non-V4 pairs (XDP/USDC and WETH/USDC), over 3,000 blocks.

**Part: "The RSR trade" (identification of the episode)**
- Files: `00-prior-runs/engine-runs/live-base-all-v0.jsonl.gz` (record with `block` 51998756), `00-prior-runs/engine-runs/dry-all-v0.log.gz`,
  `02-v4-live-test/prior/live-base-all-v0.jsonl.gz`, `05-base-onchain/rsr-episode/`, `05-base-onchain/data/txs-bf4-0001.csv.gz`,
  `05-base-onchain/data/reverted-bf4-0001.csv.gz`, `05-base-onchain/data/candidates-bf4-0001.jsonl.gz`, `05-base-onchain/blocks.csv.gz`,
  `00-prior-runs/competitor-ledgers/competitor_txs.json.gz`, `00-prior-runs/misc/section-2.6-draft.md`
- Coverage: For blocks 51,998,755-51,998,758 the material holds:
  - full tx objects and all 1,100 receipts;
  - callTracer traces per block, and a trace of tx `0x2310e683…2e77`;
  - pool state at the end of blocks 51,998,754-758 for the Uniswap V3 1 % and Aerodrome V2 WETH/RSR pools.

  The detection record was produced before the anchored-pricing commit `fd8d236`.

**Part: "the winner kept 3%"**
- Files: `05-base-onchain/rsr-episode/receipts.jsonl.gz`, `05-base-onchain/rsr-episode/trace_winner.json`,
  `05-base-onchain/rsr-episode/block_traces.jsonl.gz`, `05-base-onchain/rsr-episode/pool_state.csv`,
  `05-base-onchain/rsr-episode/transactions_by_hash.jsonl.gz`, `05-base-onchain/data/txs-bf4-0001.csv.gz`,
  `00-prior-runs/competitor-ledgers/competitor_pnl.json.gz`, `00-prior-runs/competitor-ledgers/competitor_perblock.json.gz`,
  `00-prior-runs/engine-runs/live-base-all-v0.jsonl.gz`
- Coverage: A single tx. The material holds several possible bases for a percentage:
  - the engine's predicted and simulated profit (detection record);
  - on-chain gross from the WETH Transfer logs and the trace;
  - wallet-level deltas (ledgers).

  `competitor_pnl` counts ERC-20 flows only, without native-ETH payouts. `competitor_perblock` values ETH + WETH + USDC at an
  ETH/USD price of 2,692.47.

**Part: "and paid the rest as priority fee"**
- Files: `05-base-onchain/rsr-episode/blocks_full.jsonl.gz`, `05-base-onchain/rsr-episode/transactions_by_hash.jsonl.gz`,
  `05-base-onchain/rsr-episode/receipts.jsonl.gz`, `05-base-onchain/rsr-episode/headers.jsonl.gz`, `05-base-onchain/blocks.csv.gz`,
  `05-base-onchain/data/txs-bf4-0001.csv.gz`, `00-prior-runs/competitor-ledgers/competitor_pnl.json.gz`,
  `08-sources/texts/docs-base-network-fees.txt.gz`, `08-sources/texts/docs-base-transaction-ordering.txt.gz`,
  `08-sources/texts/docs-base-fees-ordering-lifecycle.txt.gz`, `08-sources/texts/docs-base-eth-maxpriorityfeepergas.txt.gz`
- Coverage: For this tx the material has `baseFeePerGas`, `maxPriorityFeePerGas`, `maxFeePerGas`, `effectiveGasPrice`,
  `gasUsed` and the OP-stack `l1Fee`, so the fee can be split into its components. Any value moved inside the tx is visible
  in `trace_winner.json`. One episode only.

**Part: "The RSR trade shows how contested gaps end" (generalisation from one trade)**
- Files: `00-prior-runs/competitor-ledgers/competitor_txs.json.gz`, `competitor_pnl.json.gz`, `competitor_perblock.json.gz`,
  `ledger_0x778951.json.gz`, `ledger_0x0190f0.json.gz`, `arbers_XDP.json.gz` (all in `00-prior-runs/competitor-ledgers/`),
  `05-base-onchain/data/txs-*.csv.gz`, `05-base-onchain/blocks.csv.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`,
  `excerpts.jsonl (Q5-CONTEST)`
- Coverage: The material holds the sender's last 50 txs over 1.82 h (blocks 51,995,475-51,998,757).
  - Two of the four XDP-bot ledgers were saved (60 txs each); the other two were not.
  - The 05 census gives ~12 h of Base fees for every tx, but no per-tx `maxPriorityFeePerGas` and no traces outside the RSR
    blocks.

### Line 6: BSC ordering

**Part: "BSC has the same ordering problem" (as Base)**
- Files: `06-other-chains-onchain/bsc/census/txs-001.csv.gz`, `bsc/census/blocks.csv.gz`, `bsc/census/candidates-001.jsonl.gz`,
  `bsc/census/candidates-002.jsonl.gz`, `bsc/builder/builder-material-001.jsonl.gz`, `bsc/docs/` (all under
  `06-other-chains-onchain/`), `excerpts.jsonl (Q6-BSCORDER)`, `08-sources/texts/docs-base-transaction-ordering.txt.gz`,
  `05-base-onchain/data/txs-*.csv.gz`
- Coverage: BSC: one 60-minute window (blocks 124,968,311-124,976,310, 2026-09-30 19:56-20:56Z) with `tx_index`, `gas_price`,
  `max_priority_fee_per_gas` and `effective_gas_price` for every tx.
  - The Base material is from separate windows.
  - The ordering rules for both chains come from published docs as fetched on 2026-09-30.

**Part: "Its transaction ordering goes through private block builders"**
- Files: `06-other-chains-onchain/bsc/builder/block-mev-info.csv.gz`, `bsc/builder/block-mev-info-gaps.csv`, `bsc/builders.csv`,
  `bsc/validators-onchain.csv`, `bsc/validator-mev-rpc-probe.jsonl.gz`, `bsc/docs/excerpts.txt`, `bsc/docs/index.csv`,
  `bsc/docs/bep-322.txt`, `bsc/docs/bnbdocs-mev-*.txt` (all under `06-other-chains-onchain/`),
  `08-sources/texts/arxiv-2602.15395-wang-et-al-mev-in-binance-builder.txt.gz`, `08-sources/texts/blocksec-bsc-after-full-pbs.txt.gz`,
  `08-sources/texts/docs-bnbchain-mev-overview.txt.gz`, `08-sources/texts/docs-bnbchain-mev-user-guide.txt.gz`
- Coverage: Builder attribution for all 8,000 window blocks via `eth_getBlockMevInfo`, which returns the winning builder only.
  - The validator set is a snapshot at block 124,979,813, after the window.
  - 33 of 44 validator MEV RPCs answered `mev_params`.
  - The builder registries are as of their fetch-time commits.

**Part: "so a public bot still lands behind the incumbents"**
- Files: `06-other-chains-onchain/bsc/census/txs-001.csv.gz`, `bsc/census/candidates-001.jsonl.gz`, `bsc/census/candidates-002.jsonl.gz`,
  `bsc/census/reverted-001.csv.gz`, `bsc/builder/builder-material-001.jsonl.gz`, `bsc/census/raw/` (local-only),
  `bsc/docs/48club-puissant-*.txt`, `bsc/docs/blockrazor-*.txt` (all under `06-other-chains-onchain/`),
  `08-sources/texts/arxiv-2602.15395-wang-et-al-mev-in-binance-builder.txt.gz`
- Coverage: Only landed txs and their in-block positions.
  - Not collected: mempool data, bundle submissions, losing bids and txs that never landed.
  - There was no BSC engine run and no test submission from a public bot.
  - Full calldata is only in the local-only `bsc/census/raw/`.

### Line 7: Chain-wide studies

**Part: "Chain-wide studies already count every pool"**
- Files: `excerpts.jsonl (Q7-CHAINWIDE-METHOD)`, `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.txt.gz`,
  `08-sources/texts/arxiv-2506.14768-solmaz-et-al-optimistic-mev-l2s.txt.gz`, `08-sources/texts/arxiv-2509.22143-messias-torres-timeboost.txt.gz`,
  `08-sources/texts/arxiv-2607.24172-pahari-messias-torres-there-will-be-spam.txt.gz`,
  `08-sources/texts/arxiv-2405.00138-torres-et-al-rolling-in-the-shadows.txt.gz`, `08-sources/texts/dune-spellbook-*-sql.txt.gz`,
  `08-sources/texts/docs-dune-dex-trades-overview.txt.gz`, `00-prior-runs/papers-fetched-earlier/`
- Coverage: Methodology passages, plus the Dune Spellbook model files that list which DEX projects feed `dex.trades` on Base,
  Arbitrum, Optimism and BNB.
  - The model files are from the main branch at fetch time, with no commit hash.
  - Not collected: the Spellbook history over each study window, and the studies' underlying datasets.

**Part: "On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined"**
- Files: `08-sources/texts/arxiv-2509.22143-messias-torres-timeboost.txt.gz`, `08-sources/texts/arxiv-2509.22143-messias-torres-timeboost.pdf.txt.gz`,
  `08-sources/texts/arxiv-2509.22143v1-messias-torres-timeboost.pdf.txt.gz`, `08-sources/raw/arxiv-2509.22143*`,
  `excerpts.jsonl (Q7-ARB-4700)`, `08-sources/texts/arbitrum-forum-aip-pga-transition-incl-entropy-advisors-post7.txt.gz`,
  `08-sources/texts/arxiv-2511.18328-timeboost-ahead-of-time-auctions.txt.gz`, `08-sources/texts/arxiv-2512.10094-auctioning-time-latency-races.txt.gz`,
  `00-prior-runs/misc/defillama-arbitrum-timeboost.json.gz`, `06-other-chains-onchain/arbitrum/`,
  `07-other-chains-engine/scans/arbitrum/`, `07-other-chains-engine/engine-detect/arbitrum/`, `00-prior-runs/block-scans/scan-arb*.gz`
- Coverage: `docs/ANALYSIS.md` §4.1 names arXiv 2509.22143 as the source. Its MEV-data period is 2025-04-17 to 2025-07-31,
  per the 08 MANIFEST.
  - 08 holds the excerpted totals (Table 3), the per-arbitrage means and the data period. The 08 MANIFEST also lists the search
    terms the collector used to look for per-day wording.
  - The Arbitrum material collected here is from 2026-09-30/10-01: a 1 h census, ~30-minute scans and a 20-minute
    detection-only run. It has no USD profit attribution and no traces.
  - The Timeboost and PGA docs are saved, but which policy was active in the window was not determined.

**Part: "On Base, 4,365 bots made 21.4 million arbitrages over nine months"**
- Files: `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.txt.gz`, `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.pdf.txt.gz`,
  `08-sources/raw/arxiv-2606.00720*`, `excerpts.jsonl (Q7-BASE-21M, Q7-CHAINWIDE-METHOD)`,
  `00-prior-runs/papers-fetched-earlier/arxiv-2606.00720-to-wait-or-to-probe.txt.gz`,
  `08-sources/texts/dune-spellbook-dex-base-base-trades-sql.txt.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`
- Coverage: The paper's data period is 2025-06-01 to 2026-02-28, per the 08 MANIFEST.
  - Its method extends arXiv 2506.14768, which uses Dune `dex.trades` and `dex.raw_pools`.
  - The paper's dataset was not collected.
  - The Base census collected here covers ~12 h in 2026-09/10. It is a log-based candidate filter, not an arbitrage
    classification.

**Part: "and only 28% of those bots were profitable after paying for failed transactions"**
- Files: `08-sources/texts/arxiv-2607.24172-pahari-messias-torres-there-will-be-spam.txt.gz`,
  `08-sources/texts/arxiv-2607.24172-pahari-messias-torres-there-will-be-spam.pdf.txt.gz`, `08-sources/raw/arxiv-2607.24172*`,
  `excerpts.jsonl (Q7-PROFIT-28)`, `08-sources/texts/arxiv-2506.14768-solmaz-et-al-optimistic-mev-l2s.txt.gz`,
  `08-sources/texts/arxiv-2410.19106-zhu-et-al-value-of-revert-protection.txt.gz`, `05-base-onchain/data/reverted-*.csv.gz`,
  `05-base-onchain/data/txs-*.csv.gz`
- Coverage: `docs/ANALYSIS.md` §4.1 names arXiv 2607.24172 as the source of this figure. Per the 08 MANIFEST it is Table 6 of
  that paper, with a data period of 2023-09-01 to 2025-07-31 and its own bot categories.
  - 08 files the 21.4 M / 4,365-bot figures under key Q7-BASE-21M, as arXiv 2606.00720 (data period 2025-06 to 2026-02).
  - Per-bot data was not collected.
  - Material collected here: failed txs and fees per sender in the ~12 h Base census.

### Line 8: Coverage of the search, and measuring full V4 coverage

**Part: "the search went far beyond selected pairs"**
- Files: `00-prior-runs/engine-runs/dry-blocks-long5.log.gz`, `00-prior-runs/engine-runs/dry-all.log.gz`,
  `00-prior-runs/engine-runs/dry-all-v0.log.gz`, `00-prior-runs/block-scans/*.log.gz`, `03-v2-older-pairs/factories.csv`,
  `04-shallow-pools/factory-enumeration.csv.gz`, `04-shallow-pools/pools-prefilter.csv.gz`, `07-other-chains-engine/scans/`
- Coverage: The logs record the universe size of each run: `universe enumerated`, `pool discovery complete`, and the tokens,
  pools and cycles of `searcher ready`. The §2.6 universe consists of:
  - the newest 6,000 pools per V2-style factory;
  - all Slipstream pools;
  - the V3/Pancake tiers per pair;
  - GeckoTerminal-listed V4;

  all with depth ≥ 0.1 ETH.

**Part: "but it did not cover everything"**
- Files: `01-v4-pools/initialize-compact/`, `03-v2-older-pairs/pools-part-0001.csv.gz`, `04-shallow-pools/pools-prefilter.csv.gz`,
  `04-shallow-pools/pools-pruned-empty.csv.gz`, `06-other-chains-onchain/`, `07-other-chains-engine/`
- Coverage: Each folder's "Coverage limits and gaps" section lists what its own collection leaves out.

**Part: full Uniswap V4 coverage on Base is the one gap where the result can't be predicted**
- Files: `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/run-times.json`, `02-v4-live-test/prior/`
- Coverage: A judgement about predictability. V4LIVE is the measurement made for it, in a single window.

**Part: "Measuring it means listing every V4 pool from the pool manager's creation events"**
- Files: `01-v4-pools/initialize-compact/pools-part-0001..0008.csv.gz`, `01-v4-pools/initialize-compact/hooks.csv`,
  `01-v4-pools/initialize-compact/compact-index.json`, `01-v4-pools/initialize-compact/tx-hash-recovery-check.json`,
  `01-v4-pools/collect/expand_initialize.py`, `01-v4-pools/initialize-parts.json`, `01-v4-pools/initialize-part-0001..0022.csv.gz`
  (local-only), `01-v4-pools/collect/v4init_collector.py`, `01-v4-pools/collect/v4init.log`, `01-v4-pools/collect/find_deploy_block.py`,
  `01-v4-pools/collect/find_deploy_block.log`, `01-v4-pools/timestamps-check.csv`, `02-v4-live-test/initialize-topup.csv.gz`,
  `02-v4-live-test/initialize-topup.json`, `02-v4-live-test/collect/topup_initialize.py`,
  `08-sources/texts/docs-uniswap-v4-poolmanager.txt.gz`, `08-sources/texts/uniswap-foundation-how-to-navigate-v4-data.txt.gz`
- Coverage: Initialize events from the PoolManager deployment block (25,350,988) to 52,006,302: 15,333,247 rows, with no
  missing chunks.
  - Blocks 51,704,033-52,006,302 were collected independently by two collectors.
  - A top-up adds blocks up to 52,015,481 (847 rows). Initialize events after 52,015,481 were not collected.
  - The original 22 parts are local-only and can be rebuilt from `initialize-compact/`.

**Part: "and rerunning the same 20-minute live test"**
- Files: `02-v4-live-test/live-v4.log`, `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/run-times.json`,
  `02-v4-live-test/collect/run_v4_live.sh`, `02-v4-live-test/collect/run_v4_live.log`, `02-v4-live-test/collect/verify-startup.log`,
  `02-v4-live-test/attempts/20261001T010337Z-no-blocks/`, `02-v4-live-test/prior/`, `05-base-onchain/data/txs-fw-0002.csv.gz`,
  `05-base-onchain/data/reverted-fw-0001.csv.gz`, `05-base-onchain/data/candidates-fw-0003.jsonl.gz`,
  `05-base-onchain/data/provenance-fw-0001.csv.gz`, `05-base-onchain/blocks.csv.gz`, `05-base-onchain/collect/census_fw.log`,
  `05-base-onchain/integrity.json`
- Coverage: One valid 1,200 s window after `searcher ready`: 2026-10-01 02:36:04-02:56:04Z, blocks 52,016,408-52,017,008,
  516 ticks. The 02 MANIFEST records these differences from the §2.6 reference run:
  - HTTP `eth_blockNumber` polling (`NO_WS=1`) instead of websocket `newHeads`;
  - JSON log format;
  - a different time;
  - engine code `fd8d236` plus two opt-in commits;
  - the non-V4 universe re-enumerated at launch.

  The run used dry mode, with `eth_call` simulation only. An earlier invalid attempt is kept for provenance.

## 4. Folder guide

Each folder has a `MANIFEST.md`, which is the authority for schemas, methods and per-file counts. `06-other-chains-onchain/`
has a folder index plus `MANIFEST-evm.md` and one `MANIFEST.md` per chain directory. Sentinel files are in `.sentinels/`.
That directory is git-ignored, so the manifests quote the sentinel texts. Row counts below are taken from the manifests'
verified inventories. For engine outputs, candidate files and probe results, the counts are only in the manifests.

| Folder | Chains | Window (UTC) | Sentinels | Manifest status |
|---|---|---|---|---|
| `00-prior-runs/` | Base (scans also Arbitrum, Ethereum) | 2026-09-30 ~10:28-17:25Z | none (not a collector) | COMPLETE WITH GAPS |
| `01-v4-pools/` | Base | Initialize: blocks 25,350,988-52,006,302; activity: 51,963,233-52,006,432 | V4INIT, V4RECENT, V4STATE, HOOKLABELS: DONE | COMPLETE WITH GAPS |
| `02-v4-live-test/` | Base | 2026-10-01 02:36:04-02:56:04Z, blocks 52,016,408-52,017,008 | V4LIVE: DONE | COMPLETE |
| `03-v2-older-pairs/` | Base | snapshot block 52,008,400; census 51,965,201-52,008,400 | V2OLD_SNAPSHOT, V2OLD_CENSUS, V2OLD_TOKENS, V2OLD: DONE | COMPLETE |
| `04-shallow-pools/` | Base | live 2026-09-30 22:03:50-22:23:51Z; snapshot block 52,008,246 | SHALLOW_LIVE, SHALLOW_SNAPSHOT, TRANSFER_PROBE: DONE | COMPLETE |
| `05-base-onchain/` | Base | blocks 51,995,609-52,017,160 (2026-09-30 15:02:45Z to 2026-10-01 03:01:07Z) | BASE_CENSUS: DONE | COMPLETE WITH GAPS (manifest not independently verified, section 7.3) |
| `06-other-chains-onchain/` | Arbitrum, OP Mainnet, Unichain, Ethereum, Polygon, BSC, Solana | one window per chain, 2026-09-30 | 13 sentinels, all DONE | COMPLETE WITH GAPS |
| `07-other-chains-engine/` | Arbitrum, Ethereum, Base | 2026-09-30 22:14Z to 2026-10-01 02:02Z | SCANS, ENGINE_DETECT_ARBITRUM, ENGINE_DETECT_MAINNET: DONE; ENGINE_LIVE_ARBITRUM, ENGINE_LIVE_MAINNET: FAILED | COMPLETE WITH GAPS |
| `08-sources/` | (published sources) | fetched 2026-09-30 21:55-22:21Z | SOURCES: DONE | COMPLETE WITH GAPS |

### 00-prior-runs/

Gzip copies of raw outputs from the earlier session on 2026-09-30. The folder holds:
- `engine-runs/`: engine dry-run detection records and logs, all on Base. The runs are:
  - flashblock-source runs, ~12:00-12:27Z;
  - blocks/logs-source attempts, 15:15-16:10Z;
  - the §2.5 reference run, 16:13-16:38Z;
  - the first `--universe all` run, 16:37-16:55Z;
  - the §2.6 run: log 16:55:48-17:25:47Z, records in blocks 51,999,244-51,999,900.
- `block-scans/`: the §2.1 block-boundary scans on Base, Arbitrum and Ethereum, from ~10:28Z. Added on 2026-10-01; see
  section 7.3.
- `competitor-ledgers/`: collected 16:58-17:12Z. It holds the RSR sender's last 50 txs, the senders that swapped on both pools
  of the XDP/USDC pair and of the WETH/USDC pair over 3,000 blocks, and two of the four XDP-bot ledgers.
- `research-runs/`: fee timing, CEX/DEX lead-lag, CEX spreads and cross-chain prices, 15:16-16:15Z (the material behind
  `docs/ANALYSIS.md` §5).
- `papers-fetched-earlier/`: the 8 paper texts read in the earlier session.
- `misc/`: a GeckoTerminal top-pools page (~10:41Z), a PoolManager Initialize log sample (~12:09Z), a DefiLlama Timeboost
  record, and `section-2.6-draft.md` (prose).

The 32 files in `engine-runs/` and `research-runs/` were checked byte-identical to their originals in `bot/data/`. The
schema of the engine detection records is defined in this folder's MANIFEST (section "engine-runs/").

### 01-v4-pools/

- **All Initialize events.** Every Uniswap V4 PoolManager (`0x498581ff…2b2b`) `Initialize` event on Base, from the deployment
  block 25,350,988 (2025-01-21T20:28:43Z) to 52,006,302 (2026-09-30T20:59:11Z). That is 15,333,247 rows and 74,887 distinct
  hook addresses. The repository copy is `initialize-compact/` (8 parts); the 22 original parts are local-only.
- **24 h activity window** (blocks 51,963,233-52,006,432): complete Swap, ModifyLiquidity and Donate events.
- **7-day window** (blocks 51,704,033-52,006,432): Initialize events.
- **State snapshot** at block 52,006,432 (slot0, liquidity, pool keys and token metadata), for pools active in the 24 h
  window or initialized in the 7-day window.
- **Hook labels**: `hooks.csv` (1,198 rows) and `hook-labels-long.csv` (1,388 rows), from launchpad docs, the Zora on-chain
  registry, the Uniswap hooklist and Blockscout, with a fixed precedence. `hook-pool-counts-all.csv.gz` gives the Initialize
  count for every hook address.
- **Launch-tx samples**: 639 txs for 213 hooks, with all their logs.

Collectors ran on 2026-09-30 from 20:59Z. HOOKLABELS was OOM-killed at ~22:07Z and re-run on 2026-10-01 from 01:18Z to 02:09Z.

### 02-v4-live-test/

The V4LIVE run. It used the engine with the §2.6 flags plus `--v4-pools`, which takes every Initialize row from 01 plus a
top-up file (`initialize-topup.csv.gz`, 847 rows, blocks 52,006,303-52,015,481, pinned 2026-10-01 02:05:29Z). The run was in
dry mode with `eth_call` simulation and `NO_WS=1`.

One valid window: `searcher ready` at 02:36:04Z, stop at 02:56:04Z, blocks 52,016,408-52,017,008, 516 ticks. Files:
- `live-v4.jsonl`: detection records, plain JSONL.
- `live-v4.log`: one JSON record per line, including the loader record `v4 pools loaded from file`.
- `run-times.json`: run times, heads and the verbatim counter lines.

Also kept:
- the invalid attempt (`attempts/20261001T010337Z-no-blocks/`);
- the verification startup of 2026-09-30 22:23-22:54Z (`collect/verify-startup.*`);
- `prior/`: copies of the §2.5, first-§2.6 and §2.6 runs.

The MANIFEST documents the two engine commits and the loader counters.

### 03-v2-older-pairs/

Base V2-style factories at the pinned block 52,008,400 (2026-09-30T22:09:07Z).
- **`pools-part-0001.csv.gz`** (125,197 rows):
  - every index of Aerodrome V2, PancakeV2, BaseSwap and SushiV2;
  - for UniswapV2, a uniform random sample of 60,000 indices below the §2.6 range (`random.Random(20260930)`) plus the newest
    6,000 indices at the snapshot block.

  Each row has reserves, `block_timestamp_last`, LP `totalSupply`, and Aerodrome `stable` and fee.
- **Tokens and reference pools**: `tokens.csv.gz` (111,983 rows) and direct token/WETH reference pools on the 11 configured
  factories.
- **Factory lengths**: at the pinned block, at the blocks matching the §2.6 log, and on a 500,000-block grid.
- **24 h census**: four V2-style Sync/Swap topics over blocks 51,965,201-52,008,400, with per-pool-hour aggregates and
  per-emitter reads.

All collectors finished on 2026-09-30 between 22:15Z and 22:24Z.

### 04-shallow-pools/

Three collections:
1. **Live run.** A 20-minute dry engine run with `--min-depth-eth 0.001`; otherwise the §2.6 flags, with GeckoTerminal V4.
   Ready 2026-09-30 22:03:50Z, stop 22:23:51Z, heads 52,008,242-52,008,842. Files: `live-shallow.jsonl`, `live-shallow.log`,
   `run-times.json`.
2. **Pinned-block replay** of the engine's universe build at block 52,008,246, with engine-derived prices and depth per pool.
   Files:
   - `pools-prefilter.csv.gz` (35,734 rows) and `pools-pruned-empty.csv.gz`;
   - `cl-ticks-prefilter.csv.gz`, `prices.csv.gz`, `tokens.csv.gz` (33,597 rows), `factory-enumeration.csv.gz` (38,737 rows);
   - the GeckoTerminal responses.
3. **Transfer-behaviour probe** (`transfer-probe/`). One `transfer` per token is simulated at block 52,008,246 with state
   overrides, at 1 % and 0.01 % of the holder's balance. It covers 33,597 tokens, 29,703 of which have a holder. It ran on
   2026-10-01 from 02:12Z to 02:19Z, in attempt 3; attempts 1 and 2 produced no probe data.

### 05-base-onchain/

A block census of Base blocks 51,995,609-52,017,160: 21,552 consecutive blocks, with 0 missing and 0 parent-hash
mismatches. Files:
- `blocks.csv.gz`: base fee, gas and tx count per block.
- `data/txs-*`: the receipt summary of every tx (`tx_index`, `status`, `gas_used`, `effective_gas_price`, `l1_fee`).
- `data/reverted-*`: every reverted tx.
- `data/candidates-*`: full receipts and logs for the txs that meet a swap-log or multi-token-transfer filter (criterion A
  or B).
- `data/provenance-*`: the endpoint that served each block.

File names carry the stream: `bf`/`bf2`/`bf3`/`bf4` (backfill), `gf1` (gap fill) and `fw` (forward). The range contains the
RSR episode, the shallow-run window and the V4LIVE window; the MANIFEST maps each window to its files.

`rsr-episode/` holds blocks 51,998,755-51,998,758 in more detail: full tx objects, receipts, callTracer traces and pool state.

### 06-other-chains-onchain/

All windows are on 2026-09-30. Transaction counts are the rows of the `txs` file.

| Chain (dir) | Window | Blocks / slots | Transactions file rows |
|---|---|---|---|
| Arbitrum One (`arbitrum/`) | 20:07:21-21:07:20Z | 510,447,028-510,460,284 (13,257) | 62,119 |
| OP Mainnet (`optimism/`) | 20:07:23-21:07:21Z | 157,600,033-157,601,832 (1,800) | 62,920 |
| Unichain (`unichain/`) | 20:07:22-21:07:21Z | 60,050,483-60,054,082 (3,600) | 30,272 |
| Ethereum (`ethereum/`) | 15:06:59-21:06:47Z (6 h) | 26,091,086-26,092,877 (1,792) | 534,635 |
| Polygon PoS (`polygon/`) | 20:07:32-21:07:30Z | 94,729,141-94,731,540 (2,400) | 176,243 |
| BSC (`bsc/`) | 19:56:37-20:56:37Z | 124,968,311-124,976,310 (8,000) | 502,872 |
| Solana (`solana/`) | 21:25:34-21:28:13Z | slots 452,084,865-452,085,464 (600) | 348,614 non-vote (`txs-nonvote-001.csv.gz`) |

Contents by chain group:
- **The five EVM chains** share one layout: `blocks`, `txs`, `reverted`, `candidates` (criterion A/B), `topic0-counts` and
  `swap-topics`, plus token metadata and DefiLlama prices. Arbitrum, OP Mainnet and Unichain also have ordering docs.
  Arbitrum also has its chain state and Timeboost auction logs.
- **BSC** also has:
  - `eth_getBlockMevInfo` for every block;
  - per-block builder material;
  - builder and validator registries (validator snapshot at block 124,979,813);
  - a validator MEV-RPC probe;
  - 92 doc entries;
  - DefiLlama DEX volumes.
- **Solana** also has:
  - DEX-program txs (`dex-txs-00*.jsonl.gz`) and Jito tips and bundles;
  - 61 Jito tip-floor polls (21:30-22:30Z);
  - API snapshots, ordering docs and literature.

The last data write was at 22:30Z on 2026-09-30, and no collector here was interrupted.

### 07-other-chains-engine/

- **Block scans.** The repository's block scanner (`bot/src/research/scan.ts`, unmodified) on Arbitrum, Ethereum and Base, with
  two universes each (`config` and `top`), ~30 minutes per scan. The `config` scans ran on 2026-09-30 from 22:14Z to 22:49Z
  and the `top` scans on 2026-10-01 from 01:09Z to 01:48Z. The scanned block numbers are in `*.blocks.csv.gz`.
- **Detection-only engine runs.** 20 minutes each, with the §2.6 flags plus `--contract ""`, so there is no simulation:
  - Arbitrum: 01:42:43-02:02:43Z;
  - Ethereum: 01:41:20-02:01:21Z.
- **Blocker evidence** for the simulation-based dry run on these chains: `collect/engine-blocker-check-*.log`.
- **Code state** of each run: `*.code-provenance.txt`.
- **`prior-summaries.md`**: verbatim excerpts of `docs/ANALYSIS.md`.

### 08-sources/

Published sources fetched on 2026-09-30 from 21:55Z to 22:21Z:
- `sources.csv`: 92 sources, with provenance and the question-line keys of each.
- `texts/` (123 extracted texts) and `raw/` (157 raw HTTP bodies).
- `excerpts.jsonl`: 206 verbatim excerpts, each with exact character offsets into its text file.
- `searches.csv`: 58 search records.
- `defillama/`: 12 raw DefiLlama DEX-volume responses, with daily points up to 2026-09-30T00:00Z.

The arXiv versions are pinned in `sources.csv` and in the text headers. All 313 files are committed.

## 5. Conventions

**File formats**
- Data is mostly gzip CSV with a header row (`*.csv.gz`) or gzip JSON Lines (`*.jsonl.gz`).
- Large outputs are split into numbered parts (`-part-0001`, `-001`, `-0001`), each at most 90 MB on disk. Most collectors
  rotate at about 85 MB or 85 MiB. The largest committed file is 89,975,717 bytes (`05-base-onchain/data/candidates-bf-0001.jsonl.gz`).
- Some `.gz` files hold several concatenated gzip members: the 05 data parts and `rsr-episode/block_traces.jsonl.gz`. `zcat`
  and Python `gzip` read them whole.
- Some CSVs have quoted fields that contain line breaks, so read them with a CSV parser, not line by line. Examples:
  `04-shallow-pools/tokens.csv.gz`, `01-v4-pools/hook-docs/doc-address-excerpts.csv.gz`, `06-other-chains-onchain/bsc/builders.csv`
  and `bsc/validators-onchain.csv`.
- Engine detection outputs are kept as plain, uncompressed JSONL (`02-v4-live-test/live-v4.jsonl`, `04-shallow-pools/live-shallow.jsonl`),
  because `bot/src/research/analyze.ts` reads plain JSONL.
- Engine logs come in two formats:
  - `00-prior-runs/engine-runs/*.log.gz` and `02-v4-live-test/prior/*.log.gz` are pino-pretty text, with ANSI colour codes and
    multi-line records. `dry-logs.log` and `dry-validate.log` also contain NUL bytes.
  - `02-v4-live-test/live-v4.log`, `04-shallow-pools/live-shallow.log` and the 07 logs have one pino JSON object per line
    (`LOG_JSON=1`), with `time` in epoch ms.
- The manifests' verification passes read every file by streaming. The largest single table is the 8 parts of
  `01-v4-pools/initialize-compact/`, 15,333,247 rows in total.

**Hex and integers**
- Addresses and hashes are lowercase `0x` hex in the collector tables (01, 03, 04 snapshot, 05, 06; BSC except columns or
  objects marked verbatim).
- Engine outputs (detection records and engine logs) keep the engine's checksummed addresses (stated in the 04 MANIFEST for
  `live-shallow.*`).
- Integers are base-10 strings, signed where the Solidity type is signed. Token amounts are raw base units with no decimals
  applied, except where a column says "human units" (the engine's `amountIn`).
- Objects marked "verbatim" keep the node's JSON hex encoding. Examples are the `receipt` sub-objects and `logs` in
  `05-base-onchain/data/candidates-*` (hex lowercased) and the BSC candidates and raw chunks.
- `05-base-onchain/rsr-episode/pool_state.csv` column `derived_decoded_words_base10` reads every 32-byte word as unsigned.
  Signed fields such as the slot0 tick need a two's-complement reinterpretation.
- Columns marked "derived" are deterministic, lossless decodings of raw columns stored next to them.

**Time**
- Base block timestamp: `timestamp = 1686789347 + 2 * block_number` (UTC seconds). It was checked against
  `eth_getBlockByNumber` on 14 blocks (`01-v4-pools/timestamps-check.csv`) and against every 03 census log
  (`census-meta.json`).
- BSC blocks carry `milli_timestamp` (ms). Solana `blockTime` has 1 s resolution.
- Engine detection records: `t` is an ISO UTC time. `00-prior-runs/research-runs` records: `t` is epoch ms.

**Keys and joins**
- Base block number is the common key across 00-05 and 07. The table below lists the Base block anchors.

  | Anchor | Base block(s) |
  |---|---|
  | PoolManager deployment | 25,350,988 |
  | 01 seven-day Initialize window | 51,704,033-52,006,432 |
  | 01 activity window (24 h) | 51,963,233-52,006,432 |
  | 03 census window | 51,965,201-52,008,400 |
  | 05 census range | 51,995,609-52,017,160 |
  | RSR episode | 51,998,755-51,998,758 (detection record at 51,998,756) |
  | §2.6 run detection records | 51,999,244-51,999,900 |
  | 01 V4INIT pin / V4STATE snapshot | 52,006,302 / 52,006,432 |
  | 04 snapshot and transfer probe | 52,008,246 |
  | 04 live run (heads) | 52,008,242-52,008,842 |
  | 03 snapshot | 52,008,400 |
  | 07 Base scans | 52,008,645-52,009,606 (`config`), 52,014,010-52,014,982 (`top`) |
  | 02 top-up pin | 52,015,481 |
  | 02 V4LIVE window | 52,016,408-52,017,008 |

- **V4 pools** are keyed by `pool_id` (bytes32) = `keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks))`.
  - Currency `0x000…000` is native ETH. `fee_raw` 8388608 (0x800000) marks a dynamic fee.
  - The 14 hook permission flags are the low 14 bits of the hook address.
  - `initialize-compact/` stores `hook_id`, a reference into `initialize-compact/hooks.csv`.
  - Engine outputs and the 04 snapshot write a V4 pool as the first 20 bytes of its pool id, and the engine maps native ETH to
    WETH. The 04 snapshot keeps the full id in `v4_pool_id`.
- **Other pools** are keyed by the pool contract address. 03 also keys them by (`factory`, `index`), the factory array index.
- **Tokens** are keyed by contract address. Engine records name the profit token by symbol (`token`) and list pools in hop
  order (`pools`).
- **Transactions** are keyed by `tx_hash`, and by (`block_number`, `tx_index`).
- **Solana** uses slot and signature; validator identity is the `leader` column of `slots.csv.gz`.

**Engine detection-record schema.** See `00-prior-runs/MANIFEST.md`, section "engine-runs/", "Detection record fields". The
fields are `t`, `block`, `fb`, `route`, `pools`, `token`, `amountIn`, `predictedProfitUsd`, `gasUsd`, `netUsd`, `gapBps`, `sim`,
`simNetUsd`, and an optional `blacklisted`. Other places describe the same schema and the log records:
- `02-v4-live-test/MANIFEST.md` (`live-v4.jsonl`, `live-v4.log`, including heartbeat counters);
- `04-shallow-pools/MANIFEST.md` (`live-shallow.jsonl`).

The 07 engine-detect records have no `sim` or `simNetUsd` field.

**Candidate filter (all chain censuses).** Criterion A: at least 2 logs whose topic0 is in that census's `swap-topics.csv`.
Criterion B (only if not A): at least 3 ERC-20 Transfer logs with 3 topics, from at least 2 token contracts. Membership is a
log filter, not a classification. Reverted txs have no logs and appear only in `reverted-*`.

## 6. Local-only data (not in the repository) and how to regenerate it

These paths are git-ignored and exist only on the collection machine:
- `*/collect/work/`, `*/collect/state/`, `__pycache__/`;
- `census/raw/`, `raw-slots/`, `*.parts/`;
- `01-v4-pools/initialize-part-*.csv.gz`;
- `.sentinels/`.

The commands below come from the manifests, which hold the full details and sha256 values.

| Local-only data | Size | How to regenerate (per manifest) |
|---|---|---|
| `01-v4-pools/initialize-part-0001..0022.csv.gz` (original V4 Initialize parts) | 22 files, 1,821,644,422 bytes | See "V4 Initialize originals" below the table |
| `06-other-chains-onchain/bsc/census/raw/chunk-*.jsonl.gz` (verbatim `eth_getBlockByNumber(n,true)` + `eth_getBlockReceipts`, including full calldata) | 40 files, 434,972,682 bytes | `cd 06-other-chains-onchain/bsc/collect && python3 download.py`. It reads the committed `census/window.json`. It needs an endpoint with receipt history for blocks 124,968,311-124,976,310: the dataseed nodes served ~12.5 h of history on 2026-09-30, so edit `DEFAULT_ENDPOINTS` in `rpc.py`. The checksums can differ (per-line `src` field) |
| `06-other-chains-onchain/solana/data/raw-slots/slot-*.json.gz` (verbatim `getBlock`) | 600 files, 564,677,263 bytes | Recreate `solana/collect/state/pin.json` with the exact content given in the Solana MANIFEST, then run `cd solana/collect && python3 -u sol_fetch.py --n 600`. It needs RPC endpoints that still serve slots 452,084,865-452,085,464. The checksums will differ |
| `solana/data/jito-bundles-by-slot.parts/`, `solana/data/prices.parts/` | 600 + 72 files | Exact offline rebuild from the committed `data/jito-bundles-by-slot.jsonl.gz` and `prices-defillama-historical.jsonl.gz` (one-line commands in the Solana MANIFEST) |
| `01-v4-pools/collect/state/`, `collect/work/` | 10 + 13,654 files | Notes R2-R8 in the 01 MANIFEST. The pins come from the `pin` objects of `initialize-parts.json` and `recent-parts.json`. The chunk checkpoints come from re-running the collectors or from splitting the R1 output. The hook candidate lists come from `hook-docs/blockscout/index.jsonl.gz` |
| `02-v4-live-test/collect/state/`, `collect/work/topup*/` | 9 files + 11 chunk files | The top-up chunks hold the rows of `initialize-topup.csv.gz` (and of the smoke test). `run.kv` and `concurrent-engines.jsonl` were written live by the runner. The 02 MANIFEST lists them with sha256 and gives no regeneration command; `run-times.json` is built from `run.kv` |
| `03-v2-older-pairs/collect/state/` | 96 files | R2: census chunks, rebuilt offline from `census-logs-part-0001.csv.gz` and `census-chunks.csv` (script in the 03 MANIFEST). R1: undecoded Multicall3 batch results, re-fetched with `snapshot.py`, `census.py` and `tokens.py` at `--pin 52008400` into a scratch directory. R1 needs archive `eth_call` and address-less `eth_getLogs` |
| `04-shallow-pools/transfer-probe/collect/work/` | 4 files | Copies of committed files (`cp ../holders.csv.gz work/` and `gunzip -c ../probe-batches-raw.jsonl.gz > work/probe-batches.jsonl`). Restore them before re-running `run_probe.py` or `build_table.py` |
| `05-base-onchain/collect/state/` | blocks-parts, checkpoints, config, first-seen, finalize summary, gap lists | Notes R2-R7 in the 05 MANIFEST. Each final checkpoint and the config are printed verbatim in the committed `census_<stream>.log` and `supervisor.log`. `blocks-parts` can be split from `blocks.csv.gz`. `finalize.py` needs these files; do not run it without them |
| `07-other-chains-engine/collect/work/`, `collect/state/` | work JSONL, window files, markers, pids | Notes L1-L4 in the 07 MANIFEST: gunzip the committed JSONL, take `window.json` from `meta.json`, and `touch` the `.done` markers. The pids cannot be regenerated. Without the markers, `run_all.sh` in a fresh checkout re-collects live and overwrites the committed outputs |
| `__pycache__/` (several folders) | bytecode | Recreated when the scripts are imported |
| `.sentinels/` | 32 files | Not regenerable. The manifests quote or describe the sentinels of their folder (03, 04, 06 and 07 quote the texts) |

**V4 Initialize originals.** These are the V4INIT parts in `01-v4-pools/`. The steps are:
1. Run `cd 01-v4-pools/collect && python3 expand_initialize.py > initialize-full.csv`. It needs pycryptodome and gives the same
   27-column header and row order as the originals.
2. `tx_hash` stays empty unless you pass `--rpc <Base RPC URL>`, which costs one
   `eth_getTransactionByBlockNumberAndIndex` call per row.
3. To get the 22-file split, cut the output at the per-part `block_from`/`block_to` in `initialize-parts.json`. The gzip bytes
   and sha256 values will then differ from the originals.
4. Alternatively, re-collect with `v4init_collector.py` after restoring the pin.

The 2026-10-01 check found 0 mismatches over 15,333,247 rows in the 26 columns other than `tx_hash`. Several scripts read
these parts: the 01 hook scripts, and the V4LIVE `--v4-pools` glob, which points at
`01-v4-pools/initialize-part-*.csv.gz`.

## 7. Known gaps, coverage limits and run history

### 7.1 Not collected

These gaps come from the completeness check. "Collectable" means the gap could still be filled by collection. Past live windows
cannot be replayed.

| Line(s) | Not collected | Collectable? | How (as recorded) |
|---|---|---|---|
| 1, 5, 8 | Complete PoolManager Swap, ModifyLiquidity, Donate and Initialize logs for Base blocks 52,006,433-52,017,160 (for Initialize: after 52,015,481). This range covers the shallow-pool and V4LIVE windows. Today the V4 logs there exist only inside 05 candidate txs | yes | `eth_getLogs` on PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b` with the four topic0 values; reuse the logic of `01-v4-pools/collect/v4recent_collector.py` with public endpoints |
| 1 | A census of launchpad factory and token-creation events (Clanker, Zora, Flaunch, Doppler) linking each V4 pool to its launchpad and creation tx | yes | `eth_getLogs` over the factory and deployer addresses found in `01-v4-pools/hook-docs/`, from the deployment block; fill `tx_hash` with `expand_initialize.py --rpc` |
| 1 | Labels for hook addresses below the 20-pool threshold that have no other label source | yes | `01-v4-pools/collect/hook_blockscout.py` on a wider candidate list taken from `hook-pool-counts-all.csv.gz` |
| 1, 8 | The GeckoTerminal V4 listings that the §2.6 runs actually received | no | Listings are live and not block-pinned |
| 1, 3, 8 | A per-pool record of which V4 pools the V4LIVE engine kept after its filters, with their depth. Also tick-level V4 liquidity and hook internal state (dynamic fees, anti-snipe windows) | partly | A pinned-block snapshot in the style of `04-shallow-pools/collect/snapshot.ts` with the `--v4-pools` list, at a block inside the V4LIVE window, plus StateView tick reads and hook getters. This gives state at that block, not the engine's live state |
| 2 | Pair creation blocks and times for the V2-style pairs (no PairCreated scan) | yes | `eth_getLogs` on factory `0x8909dc15e40173ff4699343b6eb8132c65e18ec6` with the PairCreated topic, or a binary search over `allPairsLength` |
| 2 | The full population of older UniswapV2 pairs, and activity beyond 24 h | yes | `03-v2-older-pairs/collect/snapshot.py` over all indices at block 52,008,400; `census.py` over longer windows |
| 2, 3 | USD prices and transfer-behaviour results for tokens of the older V2 pairs (03) and of V4 pools outside the engine universe | yes | DefiLlama coins API (historical); re-run the transfer probe at a pinned block on an archive endpoint |
| 2 | LP-holder and liquidity-lock data for older pairs | yes | LP-token `balanceOf` and Transfer logs per pair |
| 3 | Sell-direction, `transferFrom` and router-path simulations, and a measured tax on swaps | yes | Extend `TransferProbe.sol` to transfer into the pool or call swap/router at block 52,008,246 |
| 3, 5, 8 | Repeated live windows at other times of day and on other days | prospective only | Re-run `04-shallow-pools/collect/run_live_shallow.py` and `02-v4-live-test/collect/run_v4_live.sh` |
| 4 | Live engine searches on BSC, Solana, OP Mainnet, Unichain, Polygon and other L2s; simulation-based dry runs on Arbitrum and Ethereum | no (needs code changes) | `chains.ts`, `client.ts`, `tokens.ts` and `v4.ts` accept only base, arbitrum and mainnet, and the dry-run code override is set only for chain 8453 (07 MANIFEST) |
| 4 | On-chain censuses for other L2s (Blast, Linea, zkSync, Scroll, Mantle, …) | yes | `06-other-chains-onchain/_shared_collect/census.py` against RPCs that serve `eth_getBlockReceipts` |
| 4, 6, 7 | More than one census window per chain (each other-chain census is one window on 2026-09-30; Solana is ~2.6 min) | yes, for new windows | Re-run `census.py`, `bsc/collect/download.py` and `solana/collect/sol_fetch.py`; past windows need endpoints with history |
| 4 | TVL or liquidity per DEX on BSC | yes | DefiLlama `/protocols` and `/protocol/<slug>` |
| 5 | Per-tx `maxPriorityFeePerGas`, calldata and traces for census txs outside the 4 RSR blocks; other contested episodes captured at the depth of `rsr-episode/` | yes | `eth_getBlockByNumber(n,true)` for blocks 51,995,609-52,017,160; `debug_traceBlockByNumber` where served; reuse `05-base-onchain/collect/rsr_episode.py` and `rsr_traces.py` |
| 5 | Base mempool, pending, dropped or private-flow data (losing bids) | no | Txs that never landed cannot be retrieved later |
| 5 | Ledgers of XDP senders `0x000000c557fa9a96d66cd6371abde62d879d0e61` and `0x3be22b314654c396a12c5e8d79abdd65aac3caaf` (computed earlier, not saved) | yes | Recompute from the tx lists in `00-prior-runs/competitor-ledgers/arbers_XDP.json.gz` with archive `eth_getBalance`/`balanceOf`, using the method in the 00 MANIFEST |
| 6 | BSC mempool and bundle-submission data, losing bids, and the inclusion outcome of a public bot's own submissions | no | Builder auctions are not public; an inclusion test needs sending transactions |
| 6 | Full BSC calldata in the repository (it exists only in the local-only `bsc/census/raw/`) | yes | Keep the local files, or re-download with `bsc/collect/download.py` |
| 7 | The datasets or queries behind arXiv 2509.22143, 2606.00720 and 2607.24172, and the Entropy Advisors data behind forum post #7 | partly | Check each paper's data or code availability statement; Dune needs an API key |
| 7 | Dune Spellbook history over each study window, and the commit hash of the saved model files | yes | `git clone https://github.com/duneanalytics/spellbook` and run `git log` on the saved model paths |
| 7 | Own measurements of Arbitrum or Base atomic-arbitrage profit over periods comparable to the studies (own Arbitrum census: 1 h; Base: ~12 h) | partly | Longer `census.py` ranges; USD attribution would also need traces and prices |
| 7 | Provenance-tracked copies of the ESMA TRV MEV risk analysis (1 July 2025) and of Gogol et al., "How to Serve Your Sandwich?" (only the text extractions in `00-prior-runs/papers-fetched-earlier/` exist) | yes | Add them to `08-sources/collect/sources.json` and run `fetch_sources.py --only <slug>` |

Other coverage limits stated in the manifests:
- **Single windows.** Every live engine run (§2.6 reference, shallow, V4LIVE, 07 detection-only) and every census ran once, at
  one time of day. All engine runs are dry: nothing was sent on-chain.
- **Shared public endpoints.** All collection used shared public RPC endpoints. Other collectors ran on the same endpoints at
  the same time; 02 recorded the concurrent engine processes, but not the other collectors.
- **Signature-based swap detection.** Swaps are found by event signature in every census. The unmatched venue types are listed
  in each `swap-topics.csv` and MANIFEST. For example, 05 criterion A misses Ekubo-style anonymous logs, custom hook events
  other than `HookSwap`, and RFQ/aggregator events.
- **05 `swap-topics.csv`** has unfinished topic verification: 1 row still reads `pending`, and 4 rows list failed Blockscout
  windows. This affects only the verification columns, not the census.
- **BSC.** 5 of the 28 swap topics were not observed in the window; 11 of 44 validator MEV RPCs did not answer; 5 of 92 docs
  have no content.
- **Solana.** 1 of 61 tip-floor polls failed; 15 of 600 slots returned HTTP 404 from the Jito bundles endpoint; 4 doc URLs were
  not retrieved; 2,342 of 2,854 requested coins have no DefiLlama price.
- **Unichain.** 1 documentation URL was not retrieved.
- **08.** No x.com posts or Dune dashboards; Spellbook files have no commit hash.
- **One failed Blockscout fetch** was kept unchanged: `01-v4-pools/hook-docs/blockscout/0x7facd8b3…7fc.address.json.gz`.

### 7.2 Run history a reader needs

All times are UTC.

**2026-09-30**
- **Earlier session (~10:28-17:25Z).** Block scans, flashblock runs, the §2.5 and §2.6 runs, competitor ledgers and research
  runs (00).
- **Engine commit `fd8d236` (16:57:59Z)**, anchored pricing. It is the base code of the §2.6 reference run (the run started
  16:55:48Z, `searcher ready` at 17:03:54Z). The first `--universe all` run (16:37-16:55Z), which contains the RSR detection
  record, predates it.
- **Collectors from ~20:53Z.** The other-chain censuses (06; BSC collected from 20:53Z, the EVM windows pinned at 21:07:32Z),
  V4INIT, V4RECENT and V4STATE (01, from 20:59Z), the Base census (05, launched 21:02:45Z), the shallow run (04, launched
  21:53:55Z) and snapshot, the sources (08, 21:55-22:21Z), the scans (07, from 22:14Z) and the V2 snapshot and census (03,
  22:15-22:24Z).
- **Verification startup (22:23:56-22:54:08Z).** A startup with `--v4-pools` using an uncommitted loader version, stopped at
  `searcher ready`.
- **Container restart (~22:58-23:00Z).** All processes died. Effects:
  - The 05 forward stream (`fw`) resumed from its checkpoint at 01:03Z on 2026-10-01 (block 52,009,870), with no block gap.
    After that it read blocks up to ~2 h old and caught up at ~1 block/s.
  - `05-base-onchain/collect/verify_topics.py` was killed and not re-run.
  - The three 07 `top` scans were killed and re-run from scratch from 2026-10-01 01:04:58Z. The interrupted attempts were not
    kept.
  - The first V4LIVE launch had not happened yet.
  - 03, 04 (live run and snapshot), 06 and 08 had already finished.
  - HOOKLABELS (01) had been OOM-killed earlier, at ~22:07Z.

**2026-10-01**
- **Engine commit `5c1baf2` (01:04:41Z):** opt-in flag `--v4-pools`.
- **Invalid V4 attempt.** Runner start 01:03:37Z, `searcher ready` 01:37:18Z, stopped 01:57:18Z. The websocket `newHeads`
  trigger delivered no block, so 0 ticks were processed. It was archived under `02-v4-live-test/attempts/20261001T010337Z-no-blocks/`
  (commit `c61317e`). Its `V4LIVE.DONE` is kept there as `V4LIVE.DONE.invalidated`, and its top-up file (678 rows) is only in
  git history (`665a14a`).
- **HOOKLABELS re-run (01:18-02:09Z).**
- **05 census stop-condition reset.** The invalid `V4LIVE.DONE` triggered the fw stop rule at 01:57:30Z (stop_block 52,015,391).
  The main session then:
  - stopped fw at 02:04:30Z;
  - cleared the stop condition in `fw.ckpt.json` at 02:04:41Z (the removed values are kept in its `notes` and in `census_fw.log`);
  - restarted fw at 02:05:00Z.

  The second detection, after the valid run, came at 02:56:28Z and set stop_block 52,017,160. fw finished at 03:08:41Z, and
  `BASE_CENSUS.DONE` was written at 03:10:56Z.
- **Valid V4LIVE run with `NO_WS=1`.** Runner start 02:05:28Z, top-up pinned 02:05:29Z, engine launched 02:05:32Z. New blocks
  came from HTTP `eth_blockNumber` polling every 500 ms. `searcher ready` at 02:36:04Z, stop at 02:56:04Z.
  - `run-times.json` field `env` records only `LOG_JSON=1`; `NO_WS=1` was inherited from the environment.
- **Engine commit `44f92d5` (02:06:30Z):** opt-in switch `NO_WS=1`. The valid run's engine was started from the working tree
  58 s before this commit was recorded.
  - `git log fd8d236..HEAD -- bot/src` lists only `5c1baf2` and `44f92d5`. Without the flag and the switch the engine behaves
    as before.
- **07 code state.** The `config` scans ran on HEAD `1c1a93f` plus uncommitted `bot/src` edits (the `--v4-pools` work in
  progress); `scan.ts` itself was unmodified. The `top` scans ran at `5c1baf2`. The engine-detect runs ran at HEAD `376519a`,
  whose `bot/src` is identical to the `top` scans'. No 07 run passes `--v4-pools`.
- **Detection-only engine runs (01:41-02:02Z)** on Arbitrum and Ethereum (07).
- **Transfer probe (02:12-02:19Z)**, attempt 3 (04).

### 7.3 Documentation discrepancies to keep in mind (manifests left unchanged)

- **`00-prior-runs/MANIFEST.md` contradicts itself about the block scans.** Gap 4 says the `scan-*` files, `prof.log` and
  `repro.log` were not copied. The later section "block-scans/ (added 2026-10-01)" lists those 16 files as present, and they
  are on disk.
  - Its "Verified inventory" says 53 files and has no rows for `block-scans/`; the folder now holds 69 files.
  - Its "Question lines served" table does not map `block-scans/`, although the block-scans section says those files serve
    lines 4 and 8.
- **`00-prior-runs/MANIFEST.md` says every file except `live-base-all.jsonl` was produced before commit `fd8d236`.** But
  `dry-all.log` is the log of the same anchored §2.6 run (16:55:48-17:25:47Z, with `fd8d236` committed at 16:57:59Z). The 02
  MANIFEST says that reference run used `fd8d236` code.
- **`07-other-chains-engine/MANIFEST.md` says the §2.1 scans did not keep their raw output.** The raw §2.1 scans were found later
  and are in `00-prior-runs/block-scans/`.
- **The same 07 manifest describes `manifest_waiter.sh` as still running until ~09:05Z.** The last line of
  `collect/manifest_waiter.log` is `2026-10-01T02:56:31Z stopped by the main session`.
- **`08-sources/MANIFEST.md` says 08 holds fresh copies of the papers in `00-prior-runs/papers-fetched-earlier/`.** Two of the
  eight are not in `08-sources/sources.csv`: the ESMA TRV MEV risk analysis and Gogol et al., "How to Serve Your Sandwich?".
- **`04-shallow-pools/MANIFEST.md` coverage item 9 says a V4 live-test engine shared the endpoints during both runs.** The 02
  timeline has no V4 engine running during the shallow live run (2026-09-30 21:53:55-22:23:51Z). Only the 04 snapshot
  (22:04-22:49Z) overlaps a V4 engine startup, the verification startup at 22:23:56Z.
- **`05-base-onchain/MANIFEST.md` has uncommitted working-tree changes** against commit `002dc86`, and it was not independently
  verified. Its text has its own "Verified inventory (2026-10-01)" section (~03:18-03:26Z).
- **`01-v4-pools/initialize-compact/compact-index.json` has wrong `bytes` and `sha256` values for all 8 parts.** This is
  documented, and the correct values are in the 01 inventory. `tx-hash-recovery-check.json` was written by a script that is not
  in the folder.
- **02 depends on files outside its own committed content.** These dependencies are documented:
  - The valid run's `--v4-pools` input was the local-only `01-v4-pools/initialize-part-*.csv.gz`.
  - The verification startup ran an uncommitted loader version.
  - `run-times.json` `env` omits `NO_WS=1`.
- **Conclusion-bearing prose sits inside data folders:** `00-prior-runs/misc/section-2.6-draft.md` (the earlier session's
  draft, later inserted into `docs/ANALYSIS.md`) and `07-other-chains-engine/prior-summaries.md` (verbatim `docs/ANALYSIS.md`
  excerpts, including evaluative statements). Both manifests acknowledge this. Treat these files as claims, not data.
- **Two notes in `08-sources/MANIFEST.md` "Coverage limits and gaps" are worded as descriptions of searches** (the per-day text
  search of arXiv 2509.22143, and the search for launch-sniping studies on Base). Read them as search records. The sources
  themselves are in `texts/`.
- **Stray files outside research-material** (noted in the 07 MANIFEST) are still present: `/scan-base-config.log` and
  `/scan-eth-config.log` at the filesystem root, 1,001 bytes each. They hold Node "module not found" output and are not data.

## 8. Related repository context

`docs/ANALYSIS.md` holds the earlier session's own measurements and conclusions. Read it as context and as a source of claims,
not as part of this raw material. The sections that relate to this folder are:
- §2.1, the block-boundary scans (raw files in `00-prior-runs/block-scans/`);
- §2.5, the reference run with the event-driven engine;
- §2.6, the full-factory universe run (raw files in `00-prior-runs/engine-runs/` and `02-v4-live-test/prior/`);
- §4.1, figures from the 2026 measurement literature, with the papers it names (the source texts are in `08-sources/`);
- §5, other arbitrage angles measured on 2026-09-30 (raw files in `00-prior-runs/research-runs/`).

This README does not repeat those conclusions.

The engine is in `bot/`. The code most relevant to the line map:
- `bot/src/main.ts`: run loop and flags;
- `bot/src/pools/v4.ts` and `bot/src/pools/v4file.ts`: V4 discovery, `isPriceable` and the `--v4-pools` loader;
- `bot/src/pools/enumerate.ts`: newest-first factory enumeration;
- `bot/src/arb/depth.ts` and `bot/src/arb/pricing.ts`: `poolDepthEth` and the anchored price map;
- `bot/src/config/chains.ts`: chains, factories and endpoints;
- `bot/src/research/scan.ts`: block scanner;
- `bot/src/research/analyze.ts`: reads the plain-JSONL engine outputs.
