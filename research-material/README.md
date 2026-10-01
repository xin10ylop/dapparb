# research-material: raw material for the eight question lines

Entry point for the analysis session. Written 2026-10-01 from the folder manifests and a completeness check of the
collection. Refreshed 2026-10-01 (~05:40Z) after the gap-fill round (section 7.2 lists what that round added). Paths in this
file are relative to `research-material/` unless they start with `bot/` or `docs/` (repository root).

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
  `excerpts.jsonl`). Since 2026-10-01 it also uses `DATA-AVAILABILITY`, which is not a question line: data and code
  availability passages of the line-7 studies (it serves line 7).
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
  `06-other-chains-onchain/*/candidates-*.jsonl.gz`, `02-v4-live-test/v4universe-pools-prefilter.csv.gz`,
  `02-v4-live-test/v4universe-meta.json`, `08-sources/defillama/protocols-base-dex-*.json.gz`,
  `08-sources/defillama/protocols-base-dex-selection.csv`
- Coverage: This is a comparison, and each gap was collected with a different method and window.
  - V4: one 20-minute dry engine run (2026-10-01 02:36-02:56Z). A per-pool reconstruction of that run's universe at block
    52,015,721 was made afterwards (V4UNIVERSE, 02).
  - Shallow pools: one 20-minute dry run at `--min-depth-eth 0.001` (2026-09-30 22:03-22:23Z).
  - Older V2 pairs: a pinned-block snapshot of a random sample plus a 24 h event census, with no engine run.
  - Other chains: single-window on-chain censuses, plus detection-only engine runs without simulation on Arbitrum and Ethereum.

  No common measure across the gaps was collected. Base-wide DEX context: DefiLlama TVL histories of the 15 Base `Dexs`
  entries selected by `chainTvls.Base` at one `/protocols` snapshot (2026-10-01T04:37:38Z); the values are DefiLlama's
  computation.

**Part: Clanker and Zora launch new tokens as V4 pools with hooks**
- Files: `01-v4-pools/initialize-compact/pools-part-0001..0008.csv.gz`, `01-v4-pools/initialize-compact/hooks.csv`,
  `01-v4-pools/collect/expand_initialize.py`, `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/hooks.csv`,
  `01-v4-pools/hook-labels-long.csv`, `01-v4-pools/hook-pool-counts-all.csv.gz`, `01-v4-pools/hook-docs/launch-tx-samples-tx.csv.gz`,
  `01-v4-pools/hook-docs/launch-tx-samples-logs.csv.gz`, `01-v4-pools/hook-docs/zora-hook-registry-events.csv`,
  `01-v4-pools/hook-docs/zora-hook-registry-logs.jsonl.gz`, `01-v4-pools/hook-docs/uniswap-hooklist-base.jsonl.gz`,
  `01-v4-pools/hook-docs/blockscout/`, `01-v4-pools/hook-docs/text/` (`clanker.gitbook.io_*`, `docs.zora.co_*`, clanker-devco and
  ourzora sources), `08-sources/texts/clanker-docs-v4*.txt.gz`, `08-sources/texts/zora-docs-coins-hook.txt.gz`,
  `08-sources/texts/clanker-paragraph-v4-1-sniper-tech.txt.gz`, `excerpts.jsonl (Q1-V4GAP)`,
  `01-v4-pools/v4-window2-initialize-part-0001.csv.gz`, `01-v4-pools/v4-window2-pool-keys.csv.gz`
- Coverage: Every PoolManager Initialize event from the deployment block 25,350,988 to 52,006,302, plus a 7-day window to
  52,006,432 and window 2 (blocks 52,006,433-52,017,160), with the hook address of each pool.
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
  (`fee_by_dir_*` columns), `04-shallow-pools/cl-ticks-prefilter.csv.gz`, `02-v4-live-test/v4universe-pools-prefilter.csv.gz`
  (`is_v4` rows, `v4_*` key columns), `02-v4-live-test/v4universe-meta.json` (`v4_loader_counts`)
- Coverage: The engine searches only the V4 pools it can price locally (the existing `isPriceable`, described in the 02 loader
  table). These are static-fee pools whose hook has no swap or return-delta permission bits.
  - Dynamic-fee pools and hook-swap-flag pools are counted (`droppedDynamicFee`, `droppedHookSwapFlags`) but not searched.
  - The V4UNIVERSE files list, one row per pool, the V4 pools that the engine's loader kept at block 52,015,721 (a
    reconstruction run after the V4LIVE run, not the live engine's state). Rows dropped by the loader are counted in
    `v4universe-meta.json`, not listed.
  - The engine source (`bot/src/pools/v4.ts`, `bot/src/pools/v4file.ts`) is in the repository, not in research-material.

**Part: "It just doesn't list every V4 pool yet"**
- Files: `00-prior-runs/engine-runs/dry-all.log.gz`, `02-v4-live-test/run-times.json`, `02-v4-live-test/live-v4.log`
  (`v4 pools loaded from file`), `02-v4-live-test/initialize-topup.csv.gz`, `02-v4-live-test/initialize-topup.json`,
  `01-v4-pools/initialize-parts.json`, `01-v4-pools/initialize-compact/`, `01-v4-pools/v4-window2-initialize-part-0001.csv.gz`,
  `02-v4-live-test/v4universe-pools-prefilter.csv.gz`, `02-v4-live-test/v4universe-meta.json`
- Coverage: In the earlier session the engine listed V4 pools through GeckoTerminal (`discoverV4Pools`).
  - During this collection, the opt-in flag `--v4-pools` was added (commit `5c1baf2`, 2026-10-01). It loads every Initialize
    event from files, and the V4LIVE run used it.
  - Pools initialized after the top-up pin (block 52,015,481) or during the run are not in that list. Their Initialize events
    (up to block 52,017,160) are in `v4-window2-initialize-part-0001.csv.gz`.
  - The run logged only aggregate counts of the pools it loaded. The per-pool list in `v4universe-*` is a later
    reconstruction at block 52,015,721; the 02 MANIFEST lists its counts next to the run's logged counts.

### Line 2: Older V2 pairs

**Part: "I took the newest 6,000" (pairs per V2-style factory)**
- Files: `00-prior-runs/engine-runs/dry-all.log.gz`, `00-prior-runs/engine-runs/dry-all-v0.log.gz`, `03-v2-older-pairs/factories.csv`,
  `03-v2-older-pairs/uniswapv2-sample-indices.csv.gz`, `04-shallow-pools/factory-enumeration.csv.gz`,
  `04-shallow-pools/collect/snapshot.log`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/v4universe-pools-prefilter.csv.gz`,
  `02-v4-live-test/v4universe-pools-pruned-empty.csv.gz`, `02-v4-live-test/collect/v4_universe_snapshot.log`
- Coverage: The §2.6 log records the total and enumerated counts per factory (16:55:48-16:55:56Z).
  - 03 rebuilds the enumerated index range from those totals and the newest-first rule in `bot/src/pools/enumerate.ts`. The
    block of each enumeration call was not logged, so it is derived from the log time (±1-2 blocks).
  - 04 has the engine's own newest-6,000 enumeration at block 52,008,246. This is a later pass, not the §2.6 set.
  - 02 V4UNIVERSE has the engine's newest-6,000 enumeration at block 52,015,721, a reconstruction of the V4LIVE run's
    universe. Its factory totals differ from the run's log for UniswapV2 and AerodromeCL3 (02 MANIFEST, "Counts").

**Part: "of about 3 million Uniswap V2 pairs"**
- Files: `03-v2-older-pairs/factories.csv`, `03-v2-older-pairs/factory-length-history.csv`, `00-prior-runs/engine-runs/dry-all.log.gz`,
  `04-shallow-pools/collect/snapshot.log`, `02-v4-live-test/live-v4.log`, `08-sources/texts/docs-uniswap-v2-deployments.txt.gz`,
  `08-sources/defillama/summary-dexs-uniswap-v2.json.gz`, `08-sources/defillama/protocols-base-dex-uniswap-v2.json.gz`,
  `02-v4-live-test/collect/v4_universe_snapshot.log`
- Coverage: The UniswapV2 factory's `allPairsLength` on Base was read on-chain at three kinds of block: the pinned block
  52,008,400, the block matching the §2.6 log time, and a 500,000-block grid.
  - Engine logs also give the logged total at other run times: 2026-09-30 16:37Z, 16:55Z and 22:04Z, and 2026-10-01 02:05Z.
    The V4UNIVERSE log gives it at block 52,015,721.
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
  (`v4AfterPruneEmpty`, `v4AfterDepthFilter`), `02-v4-live-test/v4universe-pools-prefilter.csv.gz` (`engine_depth_eth_derived`,
  `passes_min_depth_0_1_derived`), `02-v4-live-test/v4universe-pools-pruned-empty.csv.gz`, `02-v4-live-test/v4universe-prices.csv.gz`,
  `01-v4-pools/v4-window2-state-snapshot.csv.gz`, `01-v4-pools/v4-window2-pool-keys.csv.gz`, `01-v4-pools/v4-window2-token-metadata.csv.gz`
- Coverage: Engine-defined depth (`poolDepthEth` with the anchored price map) is recorded per pool for two engine universes:
  - at block 52,008,246 (04): the newest 6,000 per V2-style factory, all Slipstream pools, the V3 tiers for the revealed
    pairs, and GeckoTerminal-listed V4;
  - at block 52,015,721 (02 V4UNIVERSE): the same non-V4 rules plus the V4 pools of the `--v4-pools` loader. This is a
    reconstruction of the V4LIVE run's universe, read from an archive node after the run, not the live engine's state.

  Other material:
  - The older-V2 sample (03) has raw reserves but no engine depth.
  - V4 pools in 01 have in-range liquidity at block 52,006,432 (pools active in 24 h or initialized in 7 days) and at block
    52,017,008 (pools with an event in window 2, blocks 52,006,433-52,017,160).
  - The V4LIVE run itself logged only aggregate counters, not per-pool depth.

**Part: "Profit is capped at a slice of a pool's liquidity"**
- Files: `04-shallow-pools/live-shallow.jsonl`, `04-shallow-pools/pools-prefilter.csv.gz`, `04-shallow-pools/cl-ticks-prefilter.csv.gz`,
  `00-prior-runs/engine-runs/live-base-all.jsonl.gz`, `02-v4-live-test/live-v4.jsonl`,
  `08-sources/texts/arxiv-2305.14604-milionis-moallemi-roughgarden-arbitrage-profits-fees.txt.gz`, `excerpts.jsonl (Q3-SMALLPOOLS)`,
  `02-v4-live-test/v4universe-pools-prefilter.csv.gz`
- Coverage: This is a statement about mechanism. Candidate records give the input size and the predicted and simulated profit
  per route.
  - The pool state in 04 comes from a separate pass at block 52,008,246, not from each candidate's block.
  - Tick data covers only ±3000 ticks around the current tick.
  - The V4UNIVERSE pool state (block 52,015,721, before the V4LIVE window) has no tick tables, only per-pool tick counts.

**Part: "so these pay a few dollars at most"**
- Files: `04-shallow-pools/live-shallow.jsonl`, `04-shallow-pools/live-shallow.log`, `04-shallow-pools/run-times.json`,
  `05-base-onchain/data/txs-fw-0001.csv.gz`, `05-base-onchain/data/candidates-fw-0001.jsonl.gz`,
  `05-base-onchain/data/reverted-fw-0001.csv.gz`, `05-base-onchain/blocks.csv.gz`, `03-v2-older-pairs/census-logs-part-0001.csv.gz`,
  `01-v4-pools/v4-window2-swap-part-0001.csv.gz`, `01-v4-pools/v4-window2-modify-liquidity-part-0001.csv.gz`
- Coverage: One 20-minute dry run at `--min-depth-eth 0.001`: ready 2026-09-30 22:03:50Z, stop 22:23:51Z, blocks
  ~52,008,242-52,008,842.
  - Pools below 0.001 ETH engine depth, and pools with neither side priced, were not searched.
  - USD values use the engine price map.
  - 05 has receipts for every tx in that window, but logs only for candidate txs. 01 window 2 has every V4 PoolManager log in
    that window.
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
    the GeckoTerminal-listed set (this includes the V4 tokens that only the V4UNIVERSE universe contains).
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
  `06-other-chains-onchain/bsc/census/topic0-inventory.csv.gz`, `06-other-chains-onchain/bsc/dex/defillama-protocols.json.gz`,
  `bsc/dex/defillama-protocols.meta.json`, `bsc/dex/defillama-protocols-bsc-dex-selection.csv`,
  `bsc/dex/defillama-protocol-bsc-dex-*.json.gz` (15 files), `bsc/dex/defillama-tvl-index.csv`, `bsc/dex/defillama-v2-chains.json.gz`
  (these under `06-other-chains-onchain/`), `08-sources/defillama/protocols-base-dex-*.json.gz` (Base counterpart)
- Coverage: DefiLlama DEX volume overviews fetched on 2026-09-30, with daily points through 2026-09-30, and on-chain swap logs
  for one 60-minute window (8,000 blocks).
  - DefiLlama TVL (added 2026-10-01): one `/protocols` snapshot (2026-10-01T04:37:38Z, 8,440 entries), and the
    `/protocol/<slug>` responses (TVL history, all chains of each protocol) of the 15 `Dexs` entries selected by
    `chainTvls.Binance`. DefiLlama names BNB Smart Chain `Binance`; the filter used that name.
  - The TVL values are DefiLlama's computation and were not checked on-chain. Only category `Dexs`; parent-protocol responses
    were not fetched. No pool-level liquidity was read on BSC.
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
  `06-other-chains-onchain/arbitrum/`, `06-other-chains-onchain/ink/`, `06-other-chains-onchain/mantle/`,
  `06-other-chains-onchain/abstract/`, `06-other-chains-onchain/worldchain/`, `06-other-chains-onchain/zksync/`,
  `06-other-chains-onchain/soneium/`, `06-other-chains-onchain/selection.csv`,
  `06-other-chains-onchain/defillama-overview-dexs-all-chains.json.gz` (+ `.fetch.json`),
  `06-other-chains-onchain/defillama-overview-dexs-candidates.jsonl.gz`, `06-other-chains-onchain/rpc-receipts-probe-candidates.jsonl.gz`,
  `06-other-chains-onchain/MANIFEST-evm.md`, `excerpts.jsonl (Q4-OTHERCHAINS)`,
  `00-prior-runs/papers-fetched-earlier/optimistic-mev-l2s.txt.gz`,
  `08-sources/texts/arxiv-2601.19570-gogol-schneider-gorzny-tessone-sandwich-private-l2-mempools*.txt.gz`,
  `08-sources/texts/esma-trv-2025-maximal-extractable-value-crypto-markets.txt.gz`
- Coverage: New 60-minute on-chain censuses (2026-09-30 ~20:07-21:07Z) for OP Mainnet, Unichain, Polygon PoS and Arbitrum.
  - Added 2026-10-01: 60-minute censuses for six more L2s (Ink, Mantle, Abstract, World Chain, ZKsync Era, Soneium), windows
    2026-10-01 ~03:18-04:18Z. They were chosen from a fixed list of 11 candidates by DefiLlama 24 h DEX volume among chains
    whose public RPC serves `eth_getBlockReceipts` (`selection.csv`). The L2s also have ordering docs with excerpts.
  - Each census has receipts for all txs and logs only for candidate txs. The two sets of windows are from different hours and
    days.
  - No engine runs and no USD profit computation on these chains.
  - Not covered: the candidates that were not selected (Linea, Scroll, Blast, Mode, Taiko) and chains outside the candidate
    list (the saved DefiLlama overview's `allChains` lists every chain DefiLlama tracks; whether each is an L2 was not checked).

### Line 5: V4 launches, contested flow, the RSR trade

**Part: "V4 launches are the one place a bigger number could appear"**
- Files: `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/run-times.json`, `02-v4-live-test/prior/`,
  `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`, `01-v4-pools/hooks.csv`,
  `05-base-onchain/data/candidates-fw-0003.jsonl.gz`, `00-prior-runs/engine-runs/live-base-all.jsonl.gz`,
  `01-v4-pools/v4-window2-initialize-part-0001.csv.gz`, `01-v4-pools/v4-window2-swap-part-0001.csv.gz`,
  `02-v4-live-test/v4universe-pools-prefilter.csv.gz`, `02-v4-live-test/v4universe-meta.json`
- Coverage: This part is a forward-looking judgement.
  - The direct measurement is one 20-minute V4LIVE window, which does not search dynamic-fee or hook-swap-flag pools.
  - No run was limited to newly launched pools.
  - Complete block-level V4 activity in 01 covers blocks 51,963,233-52,017,160 (~30 h): the 24 h window plus window 2, which
    contains the shallow-run and V4LIVE windows.

**Part: "New launches open large, short-lived price gaps"**
- Files: `01-v4-pools/v4-initialize-7d-part-0001.csv.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`,
  `01-v4-pools/v4-modify-liquidity-part-0001.csv.gz`, `01-v4-pools/hook-docs/launch-tx-samples-tx.csv.gz`,
  `01-v4-pools/hook-docs/launch-tx-samples-logs.csv.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`, `05-base-onchain/swap-topics.csv`,
  `02-v4-live-test/live-v4.jsonl` (`gapBps`), `excerpts.jsonl (Q5-V4LAUNCH)`, `08-sources/texts/clanker-docs-v4-mev-*.txt.gz`,
  `08-sources/texts/clanker-docs-v4-sniper-auction-v0.txt.gz`, `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.txt.gz`,
  `01-v4-pools/v4-window2-swap-part-0001.csv.gz`, `01-v4-pools/v4-window2-modify-liquidity-part-0001.csv.gz`,
  `01-v4-pools/v4-window2-donate-part-0001.csv.gz`, `01-v4-pools/v4-window2-initialize-part-0001.csv.gz`,
  `01-v4-pools/v4-window2-state-snapshot.csv.gz`, `01-v4-pools/v4-window2-pool-keys.csv.gz`, `01-v4-pools/v4-window2-token-metadata.csv.gz`
- Coverage: Complete PoolManager Swap, ModifyLiquidity and Donate events exist for blocks 51,963,233-52,006,432 (24 h) and
  52,006,433-52,017,160 (window 2, which includes the V4LIVE window). Both windows also have all Initialize events.
  - Swap, ModifyLiquidity and Donate events before block 51,963,233 or after 52,017,160 were not collected. The 05 census range
    (51,995,609-52,017,160) lies inside the complete window; its candidate txs also carry the logs of other venues.
  - Prices of the same tokens on other venues are available only where candidate-tx logs contain them.
  - Hook-set dynamic fees and anti-snipe state were not collected. The LP fee applied to each swap is in the Swap event.

**Part: "It is also the most fought-over flow on Base"**
- Files: `05-base-onchain/data/txs-*.csv.gz`, `05-base-onchain/data/reverted-*.csv.gz`, `05-base-onchain/blocks.csv.gz`,
  `05-base-onchain/data/candidates-*.jsonl.gz`, `01-v4-pools/v4-swap-part-0001.csv.gz`, `01-v4-pools/v4-window2-swap-part-0001.csv.gz`,
  `00-prior-runs/competitor-ledgers/arbers_XDP.json.gz`, `00-prior-runs/competitor-ledgers/arbers_WETHUSDC.json.gz`,
  `excerpts.jsonl (Q5-CONTEST, Q5-V4LAUNCH)`, `08-sources/texts/esma-trv-2025-maximal-extractable-value-crypto-markets.txt.gz`,
  `08-sources/texts/arxiv-2601.19570-gogol-schneider-gorzny-tessone-sandwich-private-l2-mempools*.txt.gz`
- Coverage: The 05 census covers Base blocks 51,995,609-52,017,160 (~12 h, 2026-09-30 15:02Z to 2026-10-01 03:01Z). It has
  `tx_index`, `effective_gas_price`, `l1_fee` and `status` for every tx.
  - Priority fee per gas can be derived as `effective_gas_price` minus the block's `base_fee_per_gas`.
  - `maxPriorityFeePerGas`, calldata and traces were not collected outside the 4 RSR blocks.
  - Reverted txs carry no logs, so their target pools are not identified.
  - No mempool, dropped or private txs.
  - Competitor sender lists exist only for two non-V4 pairs (XDP/USDC and WETH/USDC), over 3,000 blocks.
  - The V4 Swap files of 01 cover every V4 swap in blocks 51,963,233-52,017,160 and carry `tx_hash` and `tx_index`, the 05 tx
    keys. For window 2 the 01 MANIFEST records that every (`block_number`, `tx_index`) of its logs is in the 05 tx files with
    the same `tx_hash`.

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
  `ledger_0x778951.json.gz`, `ledger_0x0190f0.json.gz`, `arbers_XDP.json.gz`, `ledger_0x000000c5.raw.csv.gz`,
  `ledger_0x3be22b31.raw.csv.gz`, `receipts_0x000000c5.csv.gz`, `receipts_0x3be22b31.csv.gz`, `receipts_0x000000c5.full.jsonl.gz`,
  `receipts_0x3be22b31.full.jsonl.gz` (all in `00-prior-runs/competitor-ledgers/`), `05-base-onchain/data/txs-*.csv.gz`,
  `05-base-onchain/blocks.csv.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`, `excerpts.jsonl (Q5-CONTEST)`
- Coverage: The material holds the sender's last 50 txs over 1.82 h (blocks 51,995,475-51,998,757).
  - Ledgers exist for all four XDP bots, last 60 txs each, in two forms:
    - `0x778951…` and `0x0190f0…`: saved by the earlier session as per-block derived values (`delta_eth`, `fee_eth`,
      `xdp_units_delta`).
    - `0x000000c5…` and `0x3be22b31…`: recomputed on 2026-10-01 as raw balances (ETH, WETH, USDC, XDP of the EOA and its one
      `to` contract at blocks b-1 and b; 928 and 784 rows) plus the 60 + 60 receipts (summary CSV and verbatim JSONL with all
      logs). Balances are per block, not per tx. The earlier session's values for these two senders exist only as summary rows
      in `docs/ANALYSIS.md` §2.6.
  - The 05 census gives ~12 h of Base fees for every tx, but no per-tx `maxPriorityFeePerGas` and no traces outside the RSR
    blocks. The XDP-bot txs lie inside the 05 range.

### Line 6: BSC ordering

**Part: "BSC has the same ordering problem" (as Base)**
- Files: `06-other-chains-onchain/bsc/census/txs-001.csv.gz`, `bsc/census/blocks.csv.gz`, `bsc/census/candidates-001.jsonl.gz`,
  `bsc/census/candidates-002.jsonl.gz`, `bsc/builder/builder-material-001.jsonl.gz`, `bsc/docs/` (all under
  `06-other-chains-onchain/`), `excerpts.jsonl (Q6-BSCORDER)`, `08-sources/texts/docs-base-transaction-ordering.txt.gz`,
  `05-base-onchain/data/txs-*.csv.gz`, `06-other-chains-onchain/{arbitrum,optimism,unichain}/docs/`,
  `06-other-chains-onchain/{ink,mantle,abstract,worldchain,zksync,soneium}/docs/` (with `docs/excerpts.jsonl`)
- Coverage: BSC: one 60-minute window (blocks 124,968,311-124,976,310, 2026-09-30 19:56-20:56Z) with `tx_index`, `gas_price`,
  `max_priority_fee_per_gas` and `effective_gas_price` for every tx.
  - The Base material is from separate windows.
  - The ordering rules for both chains come from published docs as fetched on 2026-09-30.
  - Ordering docs of other chains are in their 06 directories (the six L2s added on 2026-10-01 also have verbatim excerpts).
    The Ink docs site has no page describing its ordering rule.

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
  `08-sources/texts/docs-dune-dex-trades-overview.txt.gz`, `00-prior-runs/papers-fetched-earlier/`, `excerpts.jsonl (DATA-AVAILABILITY)`,
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-*.txt.gz` (5 files) and their `08-sources/raw/` bodies,
  `08-sources/collect/list_repo_wu_oz.log`, `08-sources/texts/esma-trv-2025-maximal-extractable-value-crypto-markets.txt.gz`,
  `08-sources/texts/arxiv-2601.19570-gogol-schneider-gorzny-tessone-sandwich-private-l2-mempools*.txt.gz`
- Coverage: Methodology passages, plus the Dune Spellbook model files that list which DEX projects feed `dex.trades` on Base,
  Arbitrum, Optimism and BNB.
  - The model files are from the main branch at fetch time, with no commit hash.
  - Data availability (added 2026-10-01): the `DATA-AVAILABILITY` excerpts hold the availability passages and repository URLs
    found by a text search of arXiv 2509.22143, 2606.00720 and 2607.24172. The repository named by arXiv 2606.00720
    (`github.com/M1kuW1ll/base_arbitrage_competition`, commit `ea76128d`) is saved file by file: 4 Dune SQL queries and one
    Python classifier, with no README and no data files.
  - Not collected: the Spellbook history over each study window, and the studies' underlying datasets.

**Part: "On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined"**
- Files: `08-sources/texts/arxiv-2509.22143-messias-torres-timeboost.txt.gz`, `08-sources/texts/arxiv-2509.22143-messias-torres-timeboost.pdf.txt.gz`,
  `08-sources/texts/arxiv-2509.22143v1-messias-torres-timeboost.pdf.txt.gz`, `08-sources/raw/arxiv-2509.22143*`,
  `excerpts.jsonl (Q7-ARB-4700)`, `excerpts.jsonl (DATA-AVAILABILITY)` (arXiv 2509.22143 records),
  `08-sources/texts/arbitrum-forum-aip-pga-transition-incl-entropy-advisors-post7.txt.gz`,
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
  - The `DATA-AVAILABILITY` records of arXiv 2509.22143 v2 name the Arbitrum Foundation's Timeboost bid history archive as a
    data source. That archive was not fetched; 06 `arbitrum/` has on-chain Timeboost auction logs for its own 2026-09-30
    window only.

**Part: "On Base, 4,365 bots made 21.4 million arbitrages over nine months"**
- Files: `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.txt.gz`, `08-sources/texts/arxiv-2606.00720-wu-oz-to-wait-or-to-probe.pdf.txt.gz`,
  `08-sources/raw/arxiv-2606.00720*`, `excerpts.jsonl (Q7-BASE-21M, Q7-CHAINWIDE-METHOD, DATA-AVAILABILITY)`,
  `00-prior-runs/papers-fetched-earlier/arxiv-2606.00720-to-wait-or-to-probe.txt.gz`,
  `08-sources/texts/dune-spellbook-dex-base-base-trades-sql.txt.gz`, `05-base-onchain/data/candidates-*.jsonl.gz`,
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-base-atomic-arbitrage-sql.txt.gz`,
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-tx-classifier-subtree-py.txt.gz`,
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-base-pool-commitment-inputs-by-hash-sql.txt.gz`
- Coverage: The paper's data period is 2025-06-01 to 2026-02-28, per the 08 MANIFEST.
  - Its method extends arXiv 2506.14768, which uses Dune `dex.trades` and `dex.raw_pools`.
  - The paper's dataset was not collected. Its repository (saved, commit `ea76128d`) holds the queries and the classifier code
    only. The files name `compute_pool_commitment.py`, `datasets/Base_atomic_arbitrage.csv` and the Dune table
    `dune.rig_ef.result_base_atomic_arbitrage`, none of which is in the repository; the query parameter values used for the
    paper and the query outputs were not collected.
  - The Base census collected here covers ~12 h in 2026-09/10. It is a log-based candidate filter, not an arbitrage
    classification.

**Part: "and only 28% of those bots were profitable after paying for failed transactions"**
- Files: `08-sources/texts/arxiv-2607.24172-pahari-messias-torres-there-will-be-spam.txt.gz`,
  `08-sources/texts/arxiv-2607.24172-pahari-messias-torres-there-will-be-spam.pdf.txt.gz`, `08-sources/raw/arxiv-2607.24172*`,
  `excerpts.jsonl (Q7-PROFIT-28)`, `08-sources/texts/arxiv-2506.14768-solmaz-et-al-optimistic-mev-l2s.txt.gz`,
  `08-sources/texts/arxiv-2410.19106-zhu-et-al-value-of-revert-protection.txt.gz`, `05-base-onchain/data/reverted-*.csv.gz`,
  `05-base-onchain/data/txs-*.csv.gz`, `excerpts.jsonl (DATA-AVAILABILITY)` (arXiv 2607.24172 records),
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-base-bot-spam-weekly-by-bot-sql.txt.gz`,
  `08-sources/texts/github-m1kuw1ll-base-arbitrage-competition-base-bot-spam-weekly-summary-sql.txt.gz`
- Coverage: `docs/ANALYSIS.md` §4.1 names arXiv 2607.24172 as the source of this figure. Per the 08 MANIFEST it is Table 6 of
  that paper, with a data period of 2023-09-01 to 2025-07-31 and its own bot categories.
  - 08 files the 21.4 M / 4,365-bot figures under key Q7-BASE-21M, as arXiv 2606.00720 (data period 2025-06 to 2026-02).
  - The two spam queries are files of the arXiv 2606.00720 repository (08 keys them Q7-PROFIT-28); they read a Dune table
    and were not run.
  - The text search of arXiv 2607.24172 found no passage on releasing the authors' own data or code. Its `DATA-AVAILABILITY`
    records cover third-party datasets and tools it cites, which were not collected.
  - Per-bot data was not collected.
  - Material collected here: failed txs and fees per sender in the ~12 h Base census.

### Line 8: Coverage of the search, and measuring full V4 coverage

**Part: "the search went far beyond selected pairs"**
- Files: `00-prior-runs/engine-runs/dry-blocks-long5.log.gz`, `00-prior-runs/engine-runs/dry-all.log.gz`,
  `00-prior-runs/engine-runs/dry-all-v0.log.gz`, `00-prior-runs/block-scans/*.log.gz`, `03-v2-older-pairs/factories.csv`,
  `04-shallow-pools/factory-enumeration.csv.gz`, `04-shallow-pools/pools-prefilter.csv.gz`, `07-other-chains-engine/scans/`,
  `02-v4-live-test/v4universe-pools-prefilter.csv.gz`, `02-v4-live-test/v4universe-meta.json`
- Coverage: The logs record the universe size of each run: `universe enumerated`, `pool discovery complete`, and the tokens,
  pools and cycles of `searcher ready`. The §2.6 universe consists of:
  - the newest 6,000 pools per V2-style factory;
  - all Slipstream pools;
  - the V3/Pancake tiers per pair;
  - GeckoTerminal-listed V4;

  all with depth ≥ 0.1 ETH. Per-pool lists of an engine universe exist for two later passes: 04 (block 52,008,246, with
  GeckoTerminal V4) and 02 V4UNIVERSE (block 52,015,721, with the `--v4-pools` loader). Neither is the §2.6 set.

**Part: "but it did not cover everything"**
- Files: `01-v4-pools/initialize-compact/`, `03-v2-older-pairs/pools-part-0001.csv.gz`, `04-shallow-pools/pools-prefilter.csv.gz`,
  `04-shallow-pools/pools-pruned-empty.csv.gz`, `06-other-chains-onchain/`, `07-other-chains-engine/`,
  `02-v4-live-test/v4universe-pools-pruned-empty.csv.gz`, `02-v4-live-test/v4universe-meta.json` (`v4_loader_counts`)
- Coverage: Each folder's "Coverage limits and gaps" section lists what its own collection leaves out.

**Part: full Uniswap V4 coverage on Base is the one gap where the result can't be predicted**
- Files: `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/live-v4.log`, `02-v4-live-test/run-times.json`, `02-v4-live-test/prior/`,
  `02-v4-live-test/v4universe-*`, `01-v4-pools/v4-window2-*`
- Coverage: A judgement about predictability. V4LIVE is the measurement made for it, in a single window. Added afterwards:
  every V4 PoolManager log of the V4LIVE window (01 window 2) and a per-pool reconstruction of the run's universe (02
  V4UNIVERSE).

**Part: "Measuring it means listing every V4 pool from the pool manager's creation events"**
- Files: `01-v4-pools/initialize-compact/pools-part-0001..0008.csv.gz`, `01-v4-pools/initialize-compact/hooks.csv`,
  `01-v4-pools/initialize-compact/compact-index.json`, `01-v4-pools/initialize-compact/tx-hash-recovery-check.json`,
  `01-v4-pools/collect/expand_initialize.py`, `01-v4-pools/initialize-parts.json`, `01-v4-pools/initialize-part-0001..0022.csv.gz`
  (local-only), `01-v4-pools/collect/v4init_collector.py`, `01-v4-pools/collect/v4init.log`, `01-v4-pools/collect/find_deploy_block.py`,
  `01-v4-pools/collect/find_deploy_block.log`, `01-v4-pools/timestamps-check.csv`, `02-v4-live-test/initialize-topup.csv.gz`,
  `02-v4-live-test/initialize-topup.json`, `02-v4-live-test/collect/topup_initialize.py`,
  `08-sources/texts/docs-uniswap-v4-poolmanager.txt.gz`, `08-sources/texts/uniswap-foundation-how-to-navigate-v4-data.txt.gz`,
  `01-v4-pools/v4-window2-initialize-part-0001.csv.gz`, `01-v4-pools/v4-window2-parts.json`, `01-v4-pools/collect/v4window2_collector.py`,
  `01-v4-pools/collect/v4window2.log`, `01-v4-pools/collect/v4window2_consistency.log`
- Coverage: Initialize events from the PoolManager deployment block (25,350,988) to 52,006,302: 15,333,247 rows, with no
  missing chunks.
  - Blocks 51,704,033-52,006,302 were collected independently by two collectors.
  - A top-up adds blocks up to 52,015,481 (847 rows). The V4INIT parts plus this top-up are the input the V4LIVE engine
    loaded.
  - Window 2 (V4WINDOW2) adds blocks 52,006,433-52,017,160 (965 rows), each chunk fetched from two endpoints. On the overlap
    with the top-up (blocks 52,006,433-52,015,481) both files hold the same 840 rows. Initialize events after 52,017,160 were
    not collected.
  - The original 22 parts are local-only and can be rebuilt from `initialize-compact/`.

**Part: "and rerunning the same 20-minute live test"**
- Files: `02-v4-live-test/live-v4.log`, `02-v4-live-test/live-v4.jsonl`, `02-v4-live-test/run-times.json`,
  `02-v4-live-test/collect/run_v4_live.sh`, `02-v4-live-test/collect/run_v4_live.log`, `02-v4-live-test/collect/verify-startup.log`,
  `02-v4-live-test/attempts/20261001T010337Z-no-blocks/`, `02-v4-live-test/prior/`, `05-base-onchain/data/txs-fw-0002.csv.gz`,
  `05-base-onchain/data/reverted-fw-0001.csv.gz`, `05-base-onchain/data/candidates-fw-0003.jsonl.gz`,
  `05-base-onchain/data/provenance-fw-0001.csv.gz`, `05-base-onchain/blocks.csv.gz`, `05-base-onchain/collect/census_fw.log`,
  `05-base-onchain/integrity.json`, `02-v4-live-test/v4universe-*`, `02-v4-live-test/collect/v4_universe_snapshot.ts`,
  `02-v4-live-test/collect/v4_universe_snapshot.log`, `01-v4-pools/v4-window2-swap-part-0001.csv.gz`,
  `01-v4-pools/v4-window2-modify-liquidity-part-0001.csv.gz`, `01-v4-pools/v4-window2-state-snapshot.csv.gz`
- Coverage: One valid 1,200 s window after `searcher ready`: 2026-10-01 02:36:04-02:56:04Z, blocks 52,016,408-52,017,008,
  516 ticks. The 02 MANIFEST records these differences from the §2.6 reference run:
  - HTTP `eth_blockNumber` polling (`NO_WS=1`) instead of websocket `newHeads`;
  - JSON log format;
  - a different time;
  - engine code `fd8d236` plus two opt-in commits;
  - the non-V4 universe re-enumerated at launch.

  The run used dry mode, with `eth_call` simulation only. An earlier invalid attempt is kept for provenance.

  Material added after the run:
  - `v4universe-*`: the run's engine universe, one row per pool, rebuilt with the engine's modules at block 52,015,721 (the
    loader's `liquidityHeadAfter`). The live engine read at `latest` over several blocks and kept no per-pool list, so the two
    sets cannot be compared pool by pool; the 02 MANIFEST gives the counts side by side.
  - 01 window 2: every V4 PoolManager log in the run window, and StateView state at block 52,017,008, the last block of the
    window.

## 4. Folder guide

Each folder has a `MANIFEST.md`, which is the authority for schemas, methods and per-file counts. `06-other-chains-onchain/`
has a folder index plus `MANIFEST-evm.md` and one `MANIFEST.md` per chain directory. Sentinel files are in `.sentinels/`.
That directory is git-ignored, so the manifests quote the sentinel texts. Row counts below are taken from the manifests'
verified inventories. For engine outputs, candidate files and probe results, the counts are only in the manifests.

| Folder | Chains | Window (UTC) | Sentinels | Manifest status |
|---|---|---|---|---|
| `00-prior-runs/` | Base (scans also Arbitrum, Ethereum) | 2026-09-30 ~10:28-17:25Z; XDP ledgers recomputed 2026-10-01 04:04-04:06Z (blocks 51,998,273-51,999,354) | none (not a collector) | COMPLETE WITH GAPS |
| `01-v4-pools/` | Base | Initialize: blocks 25,350,988-52,006,302, 7-day window to 52,006,432, window 2 to 52,017,160; activity: 51,963,233-52,006,432 and 52,006,433-52,017,160; snapshots at 52,006,432 and 52,017,008 | V4INIT, V4RECENT, V4STATE, HOOKLABELS, V4WINDOW2: DONE | COMPLETE WITH GAPS |
| `02-v4-live-test/` | Base | 2026-10-01 02:36:04-02:56:04Z, blocks 52,016,408-52,017,008; V4UNIVERSE reconstruction pinned at block 52,015,721 | V4LIVE, V4UNIVERSE: DONE | COMPLETE |
| `03-v2-older-pairs/` | Base | snapshot block 52,008,400; census 51,965,201-52,008,400 | V2OLD_SNAPSHOT, V2OLD_CENSUS, V2OLD_TOKENS, V2OLD: DONE | COMPLETE |
| `04-shallow-pools/` | Base | live 2026-09-30 22:03:50-22:23:51Z; snapshot block 52,008,246 | SHALLOW_LIVE, SHALLOW_SNAPSHOT, TRANSFER_PROBE: DONE | COMPLETE |
| `05-base-onchain/` | Base | blocks 51,995,609-52,017,160 (2026-09-30 15:02:45Z to 2026-10-01 03:01:07Z) | BASE_CENSUS: DONE | COMPLETE WITH GAPS (manifest not independently verified, section 7.3) |
| `06-other-chains-onchain/` | Arbitrum, OP Mainnet, Unichain, Ethereum, Polygon, BSC, Solana; since 2026-10-01 also Ink, Mantle, Abstract, World Chain, ZKsync Era, Soneium | one window per chain: 2026-09-30 for the first seven, 2026-10-01 ~03:18-04:18Z for the six L2s; BSC DefiLlama TVL fetched 2026-10-01 04:37-04:39Z | 25 sentinels, all DONE | COMPLETE WITH GAPS |
| `07-other-chains-engine/` | Arbitrum, Ethereum, Base | 2026-09-30 22:14Z to 2026-10-01 02:02Z | SCANS, ENGINE_DETECT_ARBITRUM, ENGINE_DETECT_MAINNET: DONE; ENGINE_LIVE_ARBITRUM, ENGINE_LIVE_MAINNET: FAILED | COMPLETE WITH GAPS |
| `08-sources/` | (published sources) | fetched 2026-09-30 21:55-22:21Z; additions 2026-10-01 04:34-04:41Z | SOURCES: DONE (counts of 2026-09-30, not rewritten) | COMPLETE WITH GAPS |

### 00-prior-runs/

Gzip copies of raw outputs from the earlier session on 2026-09-30, plus two recomputed XDP-bot ledgers collected on
2026-10-01. The folder holds:
- `engine-runs/`: engine dry-run detection records and logs, all on Base. The runs are:
  - flashblock-source runs, ~12:00-12:27Z;
  - blocks/logs-source attempts, 15:15-16:10Z;
  - the §2.5 reference run, 16:13-16:38Z;
  - the first `--universe all` run, 16:37-16:55Z;
  - the §2.6 run: log 16:55:48-17:25:47Z, records in blocks 51,999,244-51,999,900.
- `block-scans/`: the §2.1 block-boundary scans on Base, Arbitrum and Ethereum, from ~10:28Z (16 files, copied on
  2026-10-01, commit `9c8a37c`). The MANIFEST gives records, distinct blocks and block range per scan file, and the time span
  and token count per log.
- `competitor-ledgers/`: collected 16:58-17:12Z. It holds the RSR sender's last 50 txs, the senders that swapped on both pools
  of the XDP/USDC pair and of the WETH/USDC pair over 3,000 blocks, and two of the four XDP-bot ledgers.
  - Added 2026-10-01 (04:04-04:06Z, `competitor-ledgers/collect/xdp_ledgers.py`): the other two XDP-bot ledgers, recomputed
    for senders `0x000000c5…` and `0x3be22b31…` from their last 60 txs in `arbers_XDP.json.gz`. Files:
    `ledger_0x000000c5.raw.csv.gz` (928 rows) and `ledger_0x3be22b31.raw.csv.gz` (784 rows), with raw balances of ETH, WETH,
    USDC and XDP for the EOA and its `to` contract at blocks b-1 and b; `receipts_*.csv.gz` (60 rows each) and
    `receipts_*.full.jsonl.gz` (60 verbatim receipts each, with logs). Archive reads on blastapi; a spot check against
    Tenderly found 0 mismatches.
- `research-runs/`: fee timing, CEX/DEX lead-lag, CEX spreads and cross-chain prices, 15:16-16:15Z (the material behind
  `docs/ANALYSIS.md` §5).
- `papers-fetched-earlier/`: the 8 paper texts read in the earlier session. Since 2026-10-01 all eight also have fresh,
  provenance-tracked copies in `08-sources/` (file-to-slug map in the 08 MANIFEST).
- `misc/`: a GeckoTerminal top-pools page (~10:41Z), a PoolManager Initialize log sample (~12:09Z), a DefiLlama Timeboost
  record, and `section-2.6-draft.md` (prose; labelled "prior session text, not data" in the MANIFEST).

The 32 files in `engine-runs/` and `research-runs/` and the 16 files in `block-scans/` were checked byte-identical to their
originals in `bot/data/`. The schema of the engine detection records is defined in this folder's MANIFEST (section
"engine-runs/").

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
- **Window 2 (V4WINDOW2)**, blocks 52,006,433-52,017,160 (2026-09-30T21:03:33Z to 2026-10-01T03:01:07Z), from the end of the
  24 h window to the end of the 05 census:
  - complete PoolManager events: `v4-window2-swap-part-0001.csv.gz` (79,124 rows), `v4-window2-modify-liquidity-part-0001.csv.gz`
    (38,952), `v4-window2-donate-part-0001.csv.gz` (15) and `v4-window2-initialize-part-0001.csv.gz` (965), with the same
    columns as their 24 h / 7-day counterparts. Every 1,000-block chunk was fetched from Tenderly and again from
    mainnet.base.org, with identical rows; `v4-window2-parts.json` holds the per-chunk record and the cross-folder checks.
  - a StateView snapshot at block 52,017,008, the last block of the V4LIVE window: `v4-window2-state-snapshot.csv.gz` (4,802
    pools, every pool with an event in window 2; columns 2-3 renamed `active_window2` / `initialized_window2`),
    `v4-window2-pool-keys.csv.gz` (4,802) and `v4-window2-token-metadata.csv.gz` (1,924 currencies not already in
    `token-metadata.csv.gz`; extra column `call_block`). The 6 pools initialized after block 52,017,008 have all-zero state
    rows.

Collectors ran on 2026-09-30 from 20:59Z. HOOKLABELS was OOM-killed at ~22:07Z and re-run on 2026-10-01 from 01:18Z to 02:09Z.
V4WINDOW2 ran on 2026-10-01 from 03:55:24Z to 03:57:28Z.

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

**V4UNIVERSE** (collected 2026-10-01 03:58-04:25Z, after the run): a per-pool reconstruction of the run's engine universe.
`collect/v4_universe_snapshot.ts` calls the engine's own modules in the order of `bot/src/main.ts` for the run's flags, with
every on-chain read pinned at block 52,015,721 (the run's logged `liquidityHeadAfter`) on one archive endpoint. Files:
- `v4universe-pools-prefilter.csv.gz`: 118,168 pools after `pruneEmpty` (82,443 of them V4), with the 43 columns of
  `04-shallow-pools/pools-prefilter.csv.gz`, including `engine_depth_eth_derived` and `passes_min_depth_0_1_derived`. 9 rows
  have quoted line breaks.
- `v4universe-pools-pruned-empty.csv.gz` (10,409 rows, no V4) and `v4universe-prices.csv.gz` (8,814 tokens).
- `v4universe-meta.json`: pin, flags, input files, per-stage counts (`v4_loader_counts` uses the keys of the run's loader
  record), `searcher_ready_equivalent`.
- `v4universe-failed-calls.jsonl.gz` (49 lines) and `v4universe-rpc-errors.jsonl.gz` (0 lines).

It is not output of the live engine; the MANIFEST section "V4UNIVERSE" lists the method deviations, the count differences
from the run's log, and the three out-of-memory attempts before the completed run. Tick tables were not dumped, and dropped
V4 candidates are counted, not listed.

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

`swap-topics.csv` holds the topic0 list of criterion A, with one example log per topic found on Blockscout. Its verification
was re-run on 2026-10-01 (04:41-05:34Z, same pinned head 52,007,824, log `collect/verify_topics_rerun.log`); the census data
files were not touched.

`rsr-episode/` holds blocks 51,998,755-51,998,758 in more detail: full tx objects, receipts, callTracer traces and pool state.

### 06-other-chains-onchain/

The first seven windows are on 2026-09-30. The six L2 windows added by the 2026-10-01 collection are on 2026-10-01. Times
are chain time (UTC). Transaction counts are the rows of the `txs` file.

| Chain (dir) | Window | Blocks / slots | Transactions file rows |
|---|---|---|---|
| Arbitrum One (`arbitrum/`) | 2026-09-30 20:07:21-21:07:20Z | 510,447,028-510,460,284 (13,257) | 62,119 |
| OP Mainnet (`optimism/`) | 2026-09-30 20:07:23-21:07:21Z | 157,600,033-157,601,832 (1,800) | 62,920 |
| Unichain (`unichain/`) | 2026-09-30 20:07:22-21:07:21Z | 60,050,483-60,054,082 (3,600) | 30,272 |
| Ethereum (`ethereum/`) | 2026-09-30 15:06:59-21:06:47Z (6 h) | 26,091,086-26,092,877 (1,792) | 534,635 |
| Polygon PoS (`polygon/`) | 2026-09-30 20:07:32-21:07:30Z | 94,729,141-94,731,540 (2,400) | 176,243 |
| BSC (`bsc/`) | 2026-09-30 19:56:37-20:56:37Z | 124,968,311-124,976,310 (8,000) | 502,872 |
| Solana (`solana/`) | 2026-09-30 21:25:34-21:28:13Z | slots 452,084,865-452,085,464 (600) | 348,614 non-vote (`txs-nonvote-001.csv.gz`) |
| Ink (`ink/`) | 2026-10-01 03:18:30-04:18:29Z | 57,326,299-57,329,898 (3,600) | 23,691 |
| Mantle (`mantle/`) | 2026-10-01 03:18:30-04:18:28Z | 101,347,199-101,348,998 (1,800) | 2,444 |
| Abstract (`abstract/`) | 2026-10-01 03:18:33-04:18:32Z | 86,310,808-86,315,526 (4,719) | 6,416 |
| World Chain (`worldchain/`) | 2026-10-01 03:18:31-04:18:29Z | 35,744,536-35,746,335 (1,800) | 27,246 |
| ZKsync Era (`zksync/`) | 2026-10-01 03:18:09-04:18:08Z | 72,284,916-72,285,498 (583) | 624 |
| Soneium (`soneium/`) | 2026-10-01 03:18:31-04:18:29Z | 28,844,980-28,846,779 (1,800) | 21,002 |

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
  - DefiLlama DEX volumes;
  - DefiLlama TVL (added 2026-10-01): the `/protocols` snapshot (`dex/defillama-protocols.json.gz`, 8,440 entries,
    2026-10-01T04:37:38Z), the 15 selected `/protocol/<slug>` responses (`dex/defillama-protocol-bsc-dex-*.json.gz`), the
    derived selection table (249 rows), a fetch index and DefiLlama's `/v2/chains` list.
- **Solana** also has:
  - DEX-program txs (`dex-txs-00*.jsonl.gz`) and Jito tips and bundles;
  - 61 Jito tip-floor polls (21:30-22:30Z);
  - API snapshots, ordering docs and literature.
- **The six L2s added on 2026-10-01** (Ink, Mantle, Abstract, World Chain, ZKsync Era, Soneium) use the five-chain EVM layout and
  the unmodified shared scripts (run through thin wrappers in `collect/`), plus `docs/` with `docs/excerpts.jsonl` (verbatim
  ordering-doc excerpts with character offsets). Each has its own `MANIFEST.md`. The selection material is at the folder top
  level: `selection.csv` (11 candidates), the DefiLlama all-chains DEX overview, the candidates' per-chain overviews and an
  `eth_getBlockReceipts` probe of their public RPCs. Chain notes recorded in the manifests:
  - ZKsync Era and Abstract: the system contract `0x…800a` emits Transfer-style logs for ETH movements, and criterion B counts
    them like ERC-20 Transfers.
  - ZKsync Era: the 60-minute window holds 583 blocks.
  - World Chain: PBH (priority blockspace) transactions are not flagged in the census; its token step ran four times (endpoint
    rate limits), and only the fourth run wrote the stored files.
  - Ink: the docs site has no page describing the ordering rule.

The 2026-09-30 collections last wrote data at 22:30Z on 2026-09-30, and none was interrupted. The 2026-10-01 additions were
written later: the six L2s from 04:10Z to 04:40Z (12 DONE sentinels, no FAILED sentinel) and the BSC TVL files from 04:37Z to
04:39Z (no sentinel; all requests HTTP 200).

### 07-other-chains-engine/

- **Block scans.** The repository's block scanner (`bot/src/research/scan.ts`, unmodified) on Arbitrum, Ethereum and Base, with
  two universes each (`config` and `top`), ~30 minutes per scan. The `config` scans ran on 2026-09-30 from 22:14Z to 22:49Z
  and the `top` scans on 2026-10-01 from 01:09Z to 01:48Z. The scanned block numbers are in `*.blocks.csv.gz`.
- **Detection-only engine runs.** 20 minutes each, with the §2.6 flags plus `--contract ""`, so there is no simulation:
  - Arbitrum: 01:42:43-02:02:43Z;
  - Ethereum: 01:41:20-02:01:21Z.
- **Blocker evidence** for the simulation-based dry run on these chains: `collect/engine-blocker-check-*.log`.
- **Code state** of each run: `*.code-provenance.txt`.
- **`prior-summaries.md`**: verbatim excerpts of `docs/ANALYSIS.md` (labelled "prior session text, not data" in the MANIFEST).

### 08-sources/

Published sources fetched on 2026-09-30 from 21:55Z to 22:21Z, with additions on 2026-10-01 from 04:34Z to 04:41Z. Counts
after the additions (2026-09-30 counts in brackets):
- `sources.csv`: 99 sources [92], with provenance and the question-line keys of each.
- `texts/` (131 extracted texts [123]) and `raw/` (166 raw HTTP bodies [157]).
- `excerpts.jsonl`: 246 verbatim excerpts [206], each with exact character offsets into its text file.
- `searches.csv`: 66 search records [58].
- `defillama/`: 12 raw DefiLlama DEX-volume responses (daily points up to 2026-09-30T00:00Z) plus 15 Base DEX TVL responses
  and their selection table (added 2026-10-01).

The 2026-10-01 additions:
- the ESMA TRV MEV risk analysis (1 July 2025) and arXiv 2601.19570 (Gogol et al., "How to Serve Your Sandwich?"), which
  before existed only as text extractions in `00-prior-runs/papers-fetched-earlier/`;
- the five files of the repository named by arXiv 2606.00720 (`github.com/M1kuW1ll/base_arbitrage_competition`, pinned to
  commit `ea76128d`; no README);
- 12 `DATA-AVAILABILITY` excerpts from arXiv 2509.22143, 2606.00720 and 2607.24172, plus excerpts of the new sources;
- `defillama/protocols-base-dex-<slug>.json.gz`: `/protocol/<slug>` responses for the 15 Base `Dexs` entries selected by
  `chainTvls.Base` in the `/protocols` snapshot saved under `06-other-chains-onchain/bsc/dex/`, and
  `defillama/protocols-base-dex-selection.csv` (derived, 172 rows).

The arXiv versions are pinned in `sources.csv` and in the text headers. The 313 files of 2026-09-30 are committed; the folder
now holds 351 files. The sentinel `SOURCES.DONE` still carries the 2026-09-30 counts.

## 5. Conventions

**File formats**
- Data is mostly gzip CSV with a header row (`*.csv.gz`) or gzip JSON Lines (`*.jsonl.gz`).
- Large outputs are split into numbered parts (`-part-0001`, `-001`, `-0001`), each at most 90 MB on disk. Most collectors
  rotate at about 85 MB or 85 MiB. The largest committed file is 89,975,717 bytes (`05-base-onchain/data/candidates-bf-0001.jsonl.gz`).
- Some `.gz` files hold several concatenated gzip members: the 05 data parts and `rsr-episode/block_traces.jsonl.gz`. `zcat`
  and Python `gzip` read them whole.
- Some CSVs have quoted fields that contain line breaks, so read them with a CSV parser, not line by line. Examples:
  `04-shallow-pools/tokens.csv.gz`, `01-v4-pools/hook-docs/doc-address-excerpts.csv.gz`, `06-other-chains-onchain/bsc/builders.csv`,
  `bsc/validators-onchain.csv` and `02-v4-live-test/v4universe-pools-prefilter.csv.gz`.
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
  | 00 recomputed XDP-bot ledgers (queried blocks) | 51,998,273-51,999,354 |
  | RSR episode | 51,998,755-51,998,758 (detection record at 51,998,756) |
  | §2.6 run detection records | 51,999,244-51,999,900 |
  | 01 V4INIT pin / V4STATE snapshot | 52,006,302 / 52,006,432 |
  | 01 window 2 (V4WINDOW2) | 52,006,433-52,017,160 |
  | 04 snapshot and transfer probe | 52,008,246 |
  | 04 live run (heads) | 52,008,242-52,008,842 |
  | 03 snapshot | 52,008,400 |
  | 07 Base scans | 52,008,645-52,009,606 (`config`), 52,014,010-52,014,982 (`top`) |
  | 02 top-up pin | 52,015,481 |
  | 02 V4UNIVERSE pin | 52,015,721 |
  | 02 V4LIVE window | 52,016,408-52,017,008 |
  | 01 V4WINDOW2 snapshot | 52,017,008 |

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
| `01-v4-pools/collect/state/`, `collect/work/` | 10 + 13,654 files (before V4WINDOW2) | Notes R2-R8 in the 01 MANIFEST. The pins come from the `pin` objects of `initialize-parts.json` and `recent-parts.json`. The chunk checkpoints come from re-running the collectors or from splitting the R1 output. The hook candidate lists come from `hook-docs/blockscout/index.jsonl.gz` |
| `01-v4-pools/collect/work/v4window2/`, `collect/state/v4window2-*.json` (V4WINDOW2 chunk checkpoints with per-block `blockHash`, cross-check results, run and snapshot state) | 44 files (9,765,136 bytes) + 5 files | Re-run `collect/v4window2_collector.py` (01 MANIFEST, "Reproduce (V4WINDOW2)"). The window is a constant in the script, so it re-fetches the same blocks; the snapshot reads need archive `eth_call` at block 52,017,008 |
| `02-v4-live-test/collect/state/`, `collect/work/topup*/` | 9 files + 11 chunk files | The top-up chunks hold the rows of `initialize-topup.csv.gz` (and of the smoke test). `run.kv` and `concurrent-engines.jsonl` were written live by the runner. The 02 MANIFEST lists them with sha256 and gives no regeneration command; `run-times.json` is built from `run.kv` |
| `02-v4-live-test/collect/work/v4universe/` (V4UNIVERSE checkpoints, including the CL/V4 tick data that the output files do not contain) | 19 files, 38,617,440 bytes | Re-run `collect/run_v4_universe.sh` with the same pin, spec, endpoint and batch size (02 MANIFEST, section "V4UNIVERSE"); it needs the local V4 Initialize originals or a rebuild of them |
| `03-v2-older-pairs/collect/state/` | 96 files | R2: census chunks, rebuilt offline from `census-logs-part-0001.csv.gz` and `census-chunks.csv` (script in the 03 MANIFEST). R1: undecoded Multicall3 batch results, re-fetched with `snapshot.py`, `census.py` and `tokens.py` at `--pin 52008400` into a scratch directory. R1 needs archive `eth_call` and address-less `eth_getLogs` |
| `04-shallow-pools/transfer-probe/collect/work/` | 4 files | Copies of committed files (`cp ../holders.csv.gz work/` and `gunzip -c ../probe-batches-raw.jsonl.gz > work/probe-batches.jsonl`). Restore them before re-running `run_probe.py` or `build_table.py` |
| `05-base-onchain/collect/state/` | blocks-parts, checkpoints, config, first-seen, finalize summary, gap lists | Notes R2-R7 in the 05 MANIFEST. Each final checkpoint and the config are printed verbatim in the committed `census_<stream>.log` and `supervisor.log`. `blocks-parts` can be split from `blocks.csv.gz`. `finalize.py` needs these files; do not run it without them |
| `07-other-chains-engine/collect/work/`, `collect/state/` | work JSONL, window files, markers, pids | Notes L1-L4 in the 07 MANIFEST: gunzip the committed JSONL, take `window.json` from `meta.json`, and `touch` the `.done` markers. The pids cannot be regenerated. Without the markers, `run_all.sh` in a fresh checkout re-collects live and overwrites the committed outputs |
| `__pycache__/` (several folders) | bytecode | Recreated when the scripts are imported |
| `.sentinels/` | 46 files | Not regenerable. The manifests quote or describe the sentinels of their folder (03, 04, 06 and 07 quote the texts) |

**V4 Initialize originals.** These are the V4INIT parts in `01-v4-pools/`. The steps are:
1. Run `cd 01-v4-pools/collect && python3 expand_initialize.py > initialize-full.csv`. It needs pycryptodome and gives the same
   27-column header and row order as the originals.
2. `tx_hash` stays empty unless you pass `--rpc <Base RPC URL>`, which costs one
   `eth_getTransactionByBlockNumberAndIndex` call per row.
3. To get the 22-file split, cut the output at the per-part `block_from`/`block_to` in `initialize-parts.json`. The gzip bytes
   and sha256 values will then differ from the originals.
4. Alternatively, re-collect with `v4init_collector.py` after restoring the pin.

The 2026-10-01 check found 0 mismatches over 15,333,247 rows in the 26 columns other than `tx_hash`. Several scripts read
these parts: the 01 hook scripts, the V4LIVE `--v4-pools` glob, which points at `01-v4-pools/initialize-part-*.csv.gz`, the
V4UNIVERSE spec (the same glob), and the V4WINDOW2 pool-key lookup (which falls back to `initialize-compact/` when the
originals are absent).

**Files added in the 2026-10-01 gap-fill round.** When this README was refreshed (~05:40Z), the new data files, scripts and
logs of that round (section 7.2) were untracked in git but not git-ignored; only the checkpoint directories in the table
above are git-ignored. The result cache of the XDP-ledger collector (`00-prior-runs/competitor-ledgers/collect/state/`) was
deleted after its run, so a re-run fetches everything again.

## 7. Known gaps, coverage limits and run history

### 7.1 Not collected

These gaps come from the completeness check and remain after the gap-fill round of 2026-10-01. The gaps that round filled
were removed from this table; section 7.2 lists what it added. "Collectable" means the gap could still be filled by
collection.

| Line(s) | Not collected | Collectable? | How (as recorded) |
|---|---|---|---|
| 1 | A census of launchpad factory and token-creation events (Clanker, Zora, Flaunch, Doppler) linking each V4 pool to its launchpad and creation tx | yes | `eth_getLogs` over the factory and deployer addresses found in `01-v4-pools/hook-docs/`, from the deployment block; fill `tx_hash` with `expand_initialize.py --rpc` |
| 1 | Labels for hook addresses below the 20-pool threshold that have no other label source | yes | `01-v4-pools/collect/hook_blockscout.py` on a wider candidate list taken from `hook-pool-counts-all.csv.gz` |
| 1, 3, 8 | For the V4LIVE universe: tick-level V4 and CL liquidity, hook internal state (dynamic fees, anti-snipe windows), PoolManager-held balances of V4 currencies, and per-pool lists of the V4 candidates the loader dropped. (Filled in part: V4UNIVERSE lists the kept pools with their engine depth at block 52,015,721.) | partly | V4UNIVERSE fetched the tick data at block 52,015,721 but kept it only in its local-only checkpoints (`02-v4-live-test/collect/work/v4universe/C-sync-*`); the dropped candidates' keys are in the Initialize files. StateView tick reads and hook getters at a pinned block give state at that block, not the engine's live state |
| 2 | Pair creation blocks and times for the V2-style pairs (no PairCreated scan) | yes | `eth_getLogs` on factory `0x8909dc15e40173ff4699343b6eb8132c65e18ec6` with the PairCreated topic, or a binary search over `allPairsLength` |
| 2 | Activity of the older UniswapV2 pairs beyond the 24 h census | yes | `03-v2-older-pairs/collect/census.py` over longer windows |
| 2, 3 | USD prices and transfer-behaviour results for tokens of the older V2 pairs (03) and of V4 pools outside the 04 snapshot universe (this includes the V4 tokens that only the V4UNIVERSE list contains) | yes | DefiLlama coins API (historical); re-run the transfer probe at a pinned block on an archive endpoint |
| 2 | LP-holder and liquidity-lock data for older pairs | yes | LP-token `balanceOf` and Transfer logs per pair |
| 3 | Sell-direction, `transferFrom` and router-path simulations, and a measured tax on swaps | yes | Extend `TransferProbe.sol` to transfer into the pool or call swap/router at block 52,008,246 |
| 3, 5, 8 | Repeated live windows at other times of day and on other days | new windows only | Re-run `04-shallow-pools/collect/run_live_shallow.py` and `02-v4-live-test/collect/run_v4_live.sh` |
| 4 | On-chain censuses for the L2 candidates that were not selected (Linea, Scroll, Blast, Mode, Taiko) and for chains outside the fixed 11-candidate list. (Filled in part: Ink, Mantle, Abstract, World Chain, ZKsync Era and Soneium were added on 2026-10-01.) | yes | `06-other-chains-onchain/collect/census_l2.py` with an entry in `collect/l2_config.py`, against RPCs that serve `eth_getBlockReceipts` (`rpc-receipts-probe-candidates.jsonl.gz` records which endpoints served them for the 11 candidates) |
| 4, 6, 7 | More than one census window per chain (each other-chain census is one window: 2026-09-30 for the first seven chains, 2026-10-01 ~03:18-04:18Z for the six L2s; Solana is ~2.6 min) | yes, for new windows | Re-run `census.py` (`census_l2.py` for the six L2s), `bsc/collect/download.py` and `solana/collect/sol_fetch.py`; past windows need endpoints with history |
| 5 | Per-tx `maxPriorityFeePerGas`, calldata and traces for census txs outside the 4 RSR blocks (this includes the 120 txs of the recomputed XDP-bot ledgers, for which only receipts were read); other contested episodes captured at the depth of `rsr-episode/` | yes | `eth_getBlockByNumber(n,true)` for blocks 51,995,609-52,017,160; `debug_traceBlockByNumber` where served; reuse `05-base-onchain/collect/rsr_episode.py` and `rsr_traces.py` |
| 6 | Full BSC calldata in the repository (it exists only in the local-only `bsc/census/raw/`) | yes | Keep the local files, or re-download with `bsc/collect/download.py` |
| 7 | The datasets behind arXiv 2509.22143, 2606.00720 and 2607.24172, and the Entropy Advisors data behind forum post #7. (Filled in part: the availability statements were searched and excerpted as `DATA-AVAILABILITY`, and the repository named by arXiv 2606.00720 was saved.) Not collected: the outputs and parameter values of that repository's Dune queries, the files it names but does not contain, the Timeboost bid history archive named by arXiv 2509.22143, and the third-party datasets cited by arXiv 2607.24172 | partly | Dune needs an API key to run the saved queries, and their parameter values are not recorded; the bid history access is described at the docs.arbitrum.io URL of arXiv 2509.22143 reference [31]; the Entropy Advisors data was not located |
| 7 | Dune Spellbook history over each study window, and the commit hash of the saved model files | yes | `git clone https://github.com/duneanalytics/spellbook` and run `git log` on the saved model paths |
| 7 | Own measurements of Arbitrum or Base atomic-arbitrage profit over periods comparable to the studies (own Arbitrum census: 1 h; Base: ~12 h) | partly | Longer `census.py` ranges; USD attribution would also need traces and prices |

**Not collectable in this collection:**
- **Live engine runs on chains other than Base.** On BSC, Solana, OP Mainnet, Unichain, Polygon, the six added L2s and others
  the engine does not run at all, and on Arbitrum and Ethereum only detection-only runs (no simulation) were possible. Both
  need engine code changes: `chains.ts`, `client.ts`, `tokens.ts` and `v4.ts` accept only base, arbitrum and mainnet, and the
  dry-run code override is set only for chain 8453 (07 MANIFEST; sentinels `ENGINE_LIVE_*.FAILED`). The engine is EVM-only.
- **Mempool, bundle and losing-bid data.** These are not public: Base pending, dropped or private-flow txs, BSC mempool and
  bundle submissions, builder auction bids, and the inclusion outcome of a public bot's own submissions (which would need
  sending transactions). Txs that never landed cannot be retrieved later.
- **Past GeckoTerminal listings and past live windows.** GeckoTerminal listings are live and not block-pinned, so the V4
  listings the §2.6 runs received cannot be fetched again. Past live windows cannot be replayed: the engines' in-memory state
  during the §2.6, shallow and V4LIVE runs exists only as far as the runs logged it. The 04 snapshot and V4UNIVERSE are later
  pinned-block reconstructions.
- **The full ~3 M UniswapV2 pair population** was sampled, not enumerated: 03 holds 60,000 uniform random indices below the
  §2.6 range plus the newest 6,000. A full read of every index at one pinned block (`03-v2-older-pairs/collect/snapshot.py`)
  was not run.

Other coverage limits stated in the manifests:
- **Single windows.** Every live engine run (§2.6 reference, shallow, V4LIVE, 07 detection-only) and every census ran once, at
  one time of day. All engine runs are dry: nothing was sent on-chain.
- **Shared public endpoints.** All collection used shared public RPC endpoints. Other collectors ran on the same endpoints at
  the same time; 02 recorded the concurrent engine processes, but not the other collectors.
- **Signature-based swap detection.** Swaps are found by event signature in every census. The unmatched venue types are listed
  in each `swap-topics.csv` and MANIFEST. For example, 05 criterion A misses Ekubo-style anonymous logs, custom hook events
  other than `HookSwap`, and RFQ/aggregator events.
- **05 `swap-topics.csv`** topic verification was re-run on 2026-10-01 with the first run's pinned head. 0 rows read `pending`,
  22 rows have a verified example and 4 read "no log found". One of those 4 (Clipper, `0x4be05c8d…`) still has one failed
  Blockscout window (51,507,825-52,007,824, read timeouts in two passes). This affects only the verification columns, not
  the census.
- **V4 PoolManager activity (01).** Swap, ModifyLiquidity and Donate events are complete only for blocks 51,963,233-52,017,160;
  Initialize events are complete from the deployment block to 52,017,160. The window-2 snapshot did not re-query currencies
  already in `token-metadata.csv.gz` (their values are as of block 52,006,432).
- **V4UNIVERSE (02)** is a reconstruction at block 52,015,721, read ~1-2 h after the run from one archive endpoint. It is not
  the live engine's state, and equal counts do not establish identical per-pool sets.
- **Recomputed XDP-bot ledgers (00).** Balances are per block, not per tx, and other txs in the same block can touch the same
  addresses. Only ETH, WETH, USDC and XDP of the EOA and its one `to` contract were read. No tx objects or traces.
- **DefiLlama TVL (BSC and Base).** One `/protocols` snapshot (2026-10-01T04:37:38Z) decides each selection; category `Dexs`
  only; parent-protocol responses were not fetched; the values are DefiLlama's computation. The responses for uniswap-v2,
  uniswap-v3, uniswap-v4 and pancakeswap-amm-v3 are saved in both folders, with identical uncompressed bodies.
- **Six L2s (2026-10-01).** One 60-minute window each, at another hour and day than the 2026-09-30 windows. Chain notes are in
  section 4 (06-other-chains-onchain/).
- **BSC.** 5 of the 28 swap topics were not observed in the window; 11 of 44 validator MEV RPCs did not answer; 5 of 92 docs
  have no content.
- **Solana.** 1 of 61 tip-floor polls failed; 15 of 600 slots returned HTTP 404 from the Jito bundles endpoint; 4 doc URLs were
  not retrieved; 2,342 of 2,854 requested coins have no DefiLlama price.
- **Unichain.** 1 documentation URL was not retrieved.
- **08.** No x.com posts or Dune dashboards; Spellbook files have no commit hash. The Wu & Oz repository files are pinned to
  commit `ea76128d`.
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
  - `05-base-onchain/collect/verify_topics.py` was killed. (It was re-run on 2026-10-01 from 04:41Z, see below.)
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
- **Commit `9c8a37c` (02:57:03Z):** the main session copied the §2.1 block scans to `00-prior-runs/block-scans/` and corrected
  `bytes`/`sha256` in `01-v4-pools/initialize-compact/compact-index.json`.
- **Commit `5119e45` (03:49:45Z):** the first version of this README and the finalized 05 MANIFEST.

**2026-10-01, gap-fill round** (after the completeness check; the files are described in sections 3 and 4):
- **V4WINDOW2 (01), 03:55:24-03:57:28Z.** PoolManager logs for blocks 52,006,433-52,017,160 and the snapshot at block
  52,017,008. Sentinel `V4WINDOW2.DONE`.
- **V4UNIVERSE (02), 03:58:08-04:24:41Z.** Enumeration finished at 04:06:31Z; three attempts then ended with a V8 heap
  out-of-memory error while the V4 files were parsed, and `V4UNIVERSE.FAILED` was written. The relaunch at 04:13:35Z, with a
  memory fix, resumed from the enumeration checkpoint and completed; `.sentinels/` now holds only `V4UNIVERSE.DONE`
  (04:24:40Z). `bot/src` was not changed.
- **XDP-bot ledgers (00), 04:04:37-04:06:38Z,** including the verification pass.
- **Six L2 censuses (06), 04:10-04:40Z.** Windows of chain time ~03:18-04:18Z, pinned at 04:18:40-04:18:42Z; 12 DONE
  sentinels. The World Chain token step ran four times (endpoint rate limits).
- **Papers, data availability and DEX TVL (08 and 06 `bsc/`), 04:34:24-04:41:20Z.** All requests HTTP 200. `SOURCES.DONE`
  was not rewritten.
- **05 `verify_topics.py` re-run, 04:41:16-05:34:26Z,** in three passes with the first run's pinned head 52,007,824. It
  rewrote `swap-topics.csv` (verification columns) and modified `collect/verify_topics.py` (optional `--head`, waiting out
  Blockscout HTTP 429). The first pass was stopped by its operator to add the 429 handling.
- **Manifest fixups (00, 01, 04, 07), ~04:45-05:00Z.** Corrections of statements that no longer matched the files (section
  7.3); no data file changed.
- **This README refresh, ~05:40Z.** None of the gap-fill files had been committed at that time.

### 7.3 Documentation discrepancies to keep in mind

The 2026-10-01 fixups corrected the manifest statements that this section listed before the gap-fill round. Each correction is
a dated note in the manifest, and the earlier wording is kept there:
- `00-prior-runs/MANIFEST.md`: gap 4 no longer says the block scans were not copied; `block-scans/` now has inventory rows
  and question-line rows; the `fd8d236` sentence now also excepts `dry-all.log`.
- `07-other-chains-engine/MANIFEST.md`: the §2.1 scans' raw output is pointed to `00-prior-runs/block-scans/`, and
  `manifest_waiter.sh` is recorded as stopped at 2026-10-01T02:56:31Z.
- `04-shallow-pools/MANIFEST.md`: coverage item 9 has a correction. No V4 engine ran during the shallow live run; the V4
  verification startup overlapped only the 04 snapshot.
- `01-v4-pools/MANIFEST.md`: `compact-index.json` was corrected in commit `9c8a37c` and re-checked against all 8 parts, and
  `tx-hash-recovery-check.json` is described as written by an inline script that was not saved.
- `08-sources/MANIFEST.md`: all eight papers of `00-prior-runs/papers-fetched-earlier/` now have fresh copies in 08 (the ESMA
  analysis and arXiv 2601.19570 were added), with a file-to-slug map.

These remain:
- **`05-base-onchain/MANIFEST.md` was not independently verified.** The version this README first described was committed in
  `5119e45` (2026-10-01 03:49:45Z). Its text has its own "Verified inventory (2026-10-01)" section (~03:18-03:26Z). The
  `verify_topics.py` re-run later added correction notes and an appended section (not committed when this README was
  refreshed).
- **Older counts kept in place.** Several manifests keep their pre-gap-fill counts in the older sections and give the new
  files in dated notes or appended sections: the 00 inventory count of 53 files, the 01 inventory totals, the 06 folder
  totals and the "13 collectors" status line, and the 08 status counts and `SOURCES.DONE` (2026-09-30 counts, not rewritten).
- **`01-v4-pools/MANIFEST.md` marks the V4WINDOW2 files `committed`** in its V4WINDOW2 inventory table. When this README was
  refreshed, `git status` listed them as untracked (not git-ignored). The 00, 02 and 06 (six L2s) manifests mark their
  gap-fill files as untracked, new or not yet committed; the 08 and 06 `bsc/` inventories of the added files give no commit
  status.
- **`00-prior-runs/MANIFEST.md` block-scans table** says "20 tokens" for Base runs 1-3. The logs print `tokens: 20` for run 1
  and `tokens: 19` for runs 2 and 3; the fixup recorded this as a note and left the table row as it was.
- **08 regeneration.** Re-running `08-sources/collect/make_manifest.py` regenerates the 2026-09-30 text and drops every
  hand-written section, including the 2026-10-01 additions. The `DATA-AVAILABILITY` key exists only in `excerpts.jsonl`; the
  `sources.csv` rows of the three papers do not list it.
- **02 depends on files outside its own committed content.** These dependencies are documented:
  - The valid run's `--v4-pools` input was the local-only `01-v4-pools/initialize-part-*.csv.gz`; V4UNIVERSE read the same
    files.
  - The verification startup ran an uncommitted loader version.
  - `run-times.json` `env` omits `NO_WS=1`.
  - V4UNIVERSE replaced keys in viem's in-memory `isAddressCache` with flat copies to bound memory (no returned value
    changes); the installed viem files were not edited.
- **Conclusion-bearing prose sits inside data folders:** `00-prior-runs/misc/section-2.6-draft.md` (the earlier session's
  draft, later inserted into `docs/ANALYSIS.md`) and `07-other-chains-engine/prior-summaries.md` (verbatim `docs/ANALYSIS.md`
  excerpts, including evaluative statements). Both manifests now label them "prior session text, not data". Treat these files
  as claims, not data.
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
