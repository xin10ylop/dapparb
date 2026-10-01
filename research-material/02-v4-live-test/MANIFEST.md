# 02-v4-live-test: the reference 20-minute live test with every Uniswap V4 pool from PoolManager Initialize events

STATUS: COMPLETE (2026-10-01). One valid 20-minute V4LIVE window ran on 2026-10-01: runner start 02:05:28Z, engine
`searcher ready` 02:36:04Z, stop 02:56:04Z, blocks 52,016,408-52,017,008 in the log, sentinel
`/home/user/dapparb/research-material/.sentinels/V4LIVE.DONE` written 02:56:05Z. It ran with `NO_WS=1` (HTTP block-number
polling instead of the websocket; see "Method of the valid run"). An earlier attempt (01:03:37Z) processed no block; it is kept,
marked invalid, under `attempts/20261001T010337Z-no-blocks/`. Inventory verified 2026-10-01 (see "Verified inventory").
(Correction 2026-10-01: this line said "IN PROGRESS. The V4LIVE run is scheduled ... Row and record counts of those files are
not filled in here". The run has finished and the counts are filled in below.)

This directory contains collected data only: engine output, run metadata and copies of earlier runs. It holds no analysis,
rankings or conclusions. No analyzer was run on any output.

- Chain: Base (chain id 8453), 2-second blocks. Block timestamp: `1686789347 + 2 * block_number` (checked in
  `../01-v4-pools/timestamps-check.csv`).
- Uniswap V4 PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b`, StateView `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`,
  Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`, WETH `0x4200000000000000000000000000000000000006`.
- Prepared 2026-09-30 between 22:00Z and 22:45Z.

## Question lines served (mapping only)

Line numbers are the eight research question lines as given on 2026-10-01. This folder serves lines 1, 5 and 8. Their text,
verbatim:
- 1: 'Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet.'
- 5: 'V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee.'
- 8: 'So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test.'

| line | files in this folder |
|---|---|
| 1 | `live-v4.log`, `live-v4.jsonl`, `run-times.json`, `initialize-topup.csv.gz`, `initialize-topup.json`, `collect/verify-startup.log`, `collect/verify-startup.times`, `prior/live-base-all.jsonl.gz`, `prior/dry-all.log.gz`, `prior/live-base-all-v0.jsonl.gz`, `prior/dry-all-v0.log.gz`, `attempts/20261001T010337Z-no-blocks/` (all files; invalid attempt, provenance only) |
| 5 | `live-v4.log`, `live-v4.jsonl`, `run-times.json`, `initialize-topup.csv.gz`, `initialize-topup.json`, `prior/live-base-all-v0.jsonl.gz`, `prior/dry-all-v0.log.gz` (first 2.6 attempt; contains the RSR/WETH detection record at block 51,998,756) |
| 8 | `live-v4.log`, `live-v4.jsonl`, `run-times.json`, `initialize-topup.csv.gz`, `initialize-topup.json`, `collect/verify-startup.log`, `collect/verify-startup.times`, all six `prior/*.gz` files, `collect/run_v4_live.sh`, `collect/run_v4_live.log`, `collect/topup_initialize.py`, `collect/topup_initialize.log`, `collect/v4live_helper.py`, `collect/state/concurrent-engines.jsonl` (local-only), `attempts/20261001T010337Z-no-blocks/` (all files; invalid attempt, provenance only) |
| 2, 3 (incidental) | `live-v4.log` (`factory enumerated` records with each V2-style factory's total length; `v4AfterPruneEmpty` / `v4AfterDepthFilter`), `collect/verify-startup.log` (same records), `collect/verify-startup.times`, `prior/live-base-all.jsonl.gz`, `prior/dry-all.log.gz`. The main material for these lines is in `../03-v2-older-pairs/` and `../04-shallow-pools/`. |
| 4, 6, 7 | none |

Method and provenance files for all lines above: `collect/*.py`, `collect/*.sh`, `collect/*.log`, `collect/state/` and
`collect/work/` (local-only).

Correction 2026-10-01: this section replaces the earlier table with keys Q-V4GAP (= line 1), Q-OLDV2 (= line 2), Q-SMALL
(= line 3), Q-LAUNCH (= line 5), Q-BEYOND and Q-MEASURE (= line 8). Every earlier file-to-key assignment is kept under the
corresponding line number (Q-OLDV2 and Q-SMALL as "2, 3 (incidental)"); the earlier table also mapped `prior/live-base-all-v0.jsonl.gz`
/ `prior/dry-all-v0.log.gz` and `prior/live-base-all.jsonl.gz` / `prior/dry-all.log.gz` to Q-V4GAP/Q-BEYOND/Q-MEASURE, and
`prior/live-base-blocks-long5.jsonl.gz` / `prior/dry-blocks-long5.log.gz` to Q-BEYOND/Q-MEASURE, which is kept above. The
attempt folder and the `collect/` method files are additions. The earlier text also said: "Not covered here: other chains, BSC
ordering, chain-wide studies (other directories)."

## Run history (UTC)

| time | event | source |
|---|---|---|
| 2026-09-30 22:13:00Z | top-up smoke test on blocks 52,005,303-52,006,302 (already in V4INIT): 120 rows, identical to the V4INIT rows | `collect/topup_smoke.log` |
| 2026-09-30 22:15:19Z | top-up pinned for the verification startup: 263 rows, blocks 52,006,303-52,008,576 | `collect/topup_initialize.verify.log` |
| 2026-09-30 22:23:56Z-22:54:08Z | verification startup with `--v4-pools` (stopped at `searcher ready`) | `collect/verify-startup.*` |
| 2026-09-30 ~23:00Z | container restart; the first `run_v4_live.sh` launch had not happened yet | main session record |
| 2026-10-01 01:03:37Z | runner start (attempt); top-up re-pinned 01:03:38Z: 678 rows, blocks 52,006,303-52,013,625 | `collect/run_v4_live.attempt-20261001T010337Z.log`, `collect/topup_initialize.log` |
| 01:03:43Z | attempt engine launched (pid 614) | same |
| 01:04:41Z | commit `5c1baf2` (`--v4-pools` flag) | git |
| 01:37:18.753Z | attempt `searcher ready`; then `subscribed to newHeads via websocket` | `attempts/20261001T010337Z-no-blocks/live-v4.log` |
| 01:57:18.599Z-01:57:19.654Z | attempt stopped (SIGINT, exit code 130); `shutting down` record with `ticks: 0`; V4LIVE.DONE written | same; kept as `V4LIVE.DONE.invalidated` |
| 02:05:28.887Z | runner start (valid run), `NO_WS=1` in the environment | `collect/run_v4_live.log`, `collect/state/run.kv` |
| 02:05:29Z-02:05:31Z | top-up re-pinned: 847 rows, blocks 52,006,303-52,015,481 (head at pin 52,015,491) | `collect/topup_initialize.log`, `initialize-topup.json` |
| 02:05:32.677Z | engine launched (runner pid/pgid 31767; the engine's node process logs pid 31793) | `run-times.json` |
| 02:06:30Z / 02:06:31Z | commits `44f92d5` (`NO_WS=1`) and `c61317e` (attempt archived) | git |
| 02:36:04.248Z | `searcher ready` (detected by the runner 02:36:05.838Z) | `live-v4.log`, `run-times.json` |
| 02:36:04.476Z | `polling eth_blockNumber over HTTP (no websocket)`, `everyMs: 500` | `live-v4.log` |
| 02:56:04.663Z | SIGINT to the engine's process group (planned stop 02:56:04Z = ready + 1,200 s) | `run-times.json` |
| 02:56:05.670Z | engine exit, code 130 (SIGINT); no SIGTERM/SIGKILL needed | `run-times.json` |
| 02:56:05.719Z | `.sentinels/V4LIVE.DONE`: "ok: ran 1200 s after searcher ready" | sentinel |
| 02:57:39Z | commit `fe44401` (valid run outputs) | git |

## Method of the valid run (V4LIVE, runner start 2026-10-01T02:05:28Z)

- Engine command (cwd `/home/user/dapparb/bot`), verbatim from `run-times.json`:
  `LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6 --v4-pools '/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz,/home/user/dapparb/research-material/02-v4-live-test/initialize-topup.csv.gz' --out /home/user/dapparb/research-material/02-v4-live-test/live-v4.jsonl`
- Environment of the engine process: `LOG_JSON=1` and `NO_WS=1`. `run-times.json` field `env` records only `LOG_JSON=1`:
  `run_v4_live.sh` writes that literal string to `state/run.kv` (`kv env "LOG_JSON=1"`); `NO_WS=1` was inherited from the
  environment the runner was started in. The log confirms the trigger: it has the record
  `polling eth_blockNumber over HTTP (no websocket)` (`everyMs: 500`) and no `subscribed to newHeads via websocket` record.
  For Base the engine configuration always has a websocket URL (`bot/src/config/chains.ts`: `BASE_WS_URL` or
  `wss://base-rpc.publicnode.com`), so `main.ts` takes the polling branch only when `makeWsClient` returns null, i.e. with `NO_WS=1`.
- Block trigger: `eth_blockNumber` over HTTP every 500 ms (`max(150, blockTimeMs / 4)`, Base `blockTimeMs` 2000); a tick runs
  when the number changes. In `--source logs` mode each tick reads that block's receipts (`eth_getBlockReceipts`) as before.
- Engine code: `bot/src` at commit `44f92d5` (= HEAD for `bot/src` at 2026-10-01). Changes against the base commit `fd8d236`
  are exactly the two opt-in commits `5c1baf2` (`--v4-pools`) and `44f92d5` (`NO_WS=1`); see "Engine changes". The engine was
  started from the working tree at 02:05:32Z, 58 s before `44f92d5` was recorded at 02:06:30Z; the `everyMs` polling record above
  is emitted only by code added in that commit.
- V4 pool list: the 22 V4INIT parts (`../01-v4-pools/initialize-part-0001..0022.csv.gz`, 15,333,247 rows, blocks
  25,350,988-52,006,302 by pin) plus `initialize-topup.csv.gz` as now on disk (847 rows, blocks 52,006,303-52,015,481 by pin,
  sha256 `5c73fd6c...0871203`, pinned 02:05:29Z; equal to `run-times.json.topup.index`).
- Other Base engines: none at the first check and at launch (waited 0 s). `collect/state/concurrent-engines.jsonl` has 20
  samples during the window (02:36:06Z-02:55:06Z), each with an empty engine list (any chain).
- Duration: 1,200 s counted from the `searcher ready` record's own time; stop by SIGINT to the process group.

Recorded values (from `live-v4.log` and `run-times.json`; values only, no interpretation):

| item | value |
|---|---|
| `searcher ready` (02:36:04.248Z) | tokens 75,007; pools 11,779; cycles 9,512; minDepthEth 0.1; source logs; mode dry; codeOverride true |
| `v4 pools loaded from file` (02:36:04.207Z) | files 23; rowsRead 15,334,094 (indexRowMismatches 0); blockMin 25,352,561; blockMax 52,015,467; priceable 240,087 (hookless 238,606, with hook 1,481); droppedDynamicFee 3,359,021; droppedHookSwapFlags 11,734,986; droppedMalformed 0; droppedDuplicatePoolId 0; droppedPoolIdMismatch 0; droppedSameTokenAfterNativeMapping 5; liquidityChecked 240,082 between heads 52,015,682 and 52,015,721; liquidityPositive 82,443; droppedLiquidityZero 157,639; droppedLiquidityCallFailed 0; tokensAdded 41,402; tokenMetadataFailed 0; v4PoolsBuilt 82,443; startupSyncPools 128,576; startupSyncStalePools 0; startupSyncChunkFailures 0; v4AfterPruneEmpty 82,443; v4AfterDepthFilter 8,612; parseMs 45,372; liquidityMs 79,020; metadataMs 37,096 |
| non-V4 universe (`factory enumerated`, 02:05:34Z-02:05:43Z) | AerodromeCL total 3,648 / enumerated 3,648; AerodromeCL3 2,840 / 2,840; AerodromeCL2 2,260 / 2,260; Aerodrome 29,603 / 6,000; UniswapV2 3,063,783 / 6,000; SushiV2 6,095 / 6,000; PancakeV2 15,243 / 6,000; BaseSwap 8,258 / 6,000. `universe enumerated`: enumeratedPools 38,748, tokens 33,605, pairs 37,338. `pool discovery complete`: candidates 1,344,168, found 46,133 |
| heads (`eth_blockNumber`, publicnode) | at launch 52,015,492 (02:05:32.662Z); at ready 52,016,409 (02:36:06.327Z); at stop 52,017,008 (02:56:04.649Z) |
| blocks in the log after ready | first 52,016,408, last 52,017,008 (`first/last_processed_block_in_log`) |
| ticks | 516 (`shutting down` record); 51 heartbeats (ticks 10-510, blocks 52,016,460-52,017,002); staleTicks 0 |
| log | 120 JSON records, 0 non-JSON lines, 0 error-level records, 0 `block-number poll failed` records; per-message counts in `run-times.json.log_record_counts_by_msg` |
| `live-v4.jsonl` | 51 records; `block` 52,016,408-52,017,008; `t` 02:37:32.321Z-02:56:04.299Z |
| full counter lines | `run-times.json`: `searcher_ready_line_verbatim`, `v4_pools_loaded_from_file_line_verbatim`, `shutting_down_line_verbatim`, `last_heartbeat_line_verbatim` |

Method differences against the section 2.6 reference run (`prior/dry-all.log.gz`, `prior/live-base-all.jsonl.gz`, 2026-09-30
16:55:48Z-17:25:47Z; stated as differences only):
- Block trigger: the reference run used the websocket `newHeads` subscription (its log has `subscribed to newHeads via websocket`);
  this run used HTTP `eth_blockNumber` polling every 500 ms.
- V4 pool source: the reference run used the GeckoTerminal listing (`discoverV4Pools`); this run used `--v4-pools` with every
  Initialize event up to block 52,015,481.
- Log format: `LOG_JSON=1` (one JSON record per line) here; pino-pretty text in the reference run.
- Time: a different 20-minute window (2026-10-01 02:36:04Z-02:56:04Z vs 2026-09-30 17:03:54Z-17:25:47Z); the non-V4 universe is
  the newest 6,000 pools per V2-style factory at each launch time.
- Engine code: `fd8d236` for the reference run; `fd8d236` plus the two opt-in commits `5c1baf2` and `44f92d5` here.
All other flags are identical (apart from the `--out` path).

The Base on-chain census in `../05-base-onchain` covers these blocks: its forward stream (`fw`, from block 52,006,400) was kept
running through this window (its stop condition, triggered by the attempt's V4LIVE.DONE at 01:57:30Z, was cleared at 02:04:41Z;
note in `../05-base-onchain/collect/state/fw.ckpt.json`). After the valid run's V4LIVE.DONE it set `stop_block` 52,017,160
(02:56:28Z), which is above the last block of this run, 52,017,008. At 03:06:07Z its checkpoint `next` was 52,017,010, i.e. the
stream had passed block 52,017,008. Its final range and any per-block gaps are recorded by that folder's `finalize.py` (its
manifest, `integrity.json`, `gaps-final.csv`).

## Invalid attempt (runner start 2026-10-01T01:03:37Z)

Files: `attempts/20261001T010337Z-no-blocks/` (`ATTEMPT-NOTE.md`, `live-v4.log`, `live-v4.jsonl` (empty), `run-times.json`,
`run_v4_live.log`, `V4LIVE.DONE.invalidated`), `collect/run_v4_live.attempt-20261001T010337Z.log` (byte-identical to the
attempt folder's `run_v4_live.log`), `collect/state/run.attempt-20261001T010337Z.kv` (local-only), and lines 1-20 of
`collect/state/concurrent-engines.jsonl` (local-only; samples 01:37:19Z-01:56:20Z).
- Same command and flags as the valid run, with the websocket trigger (no `NO_WS`). Top-up used: 678 rows, blocks
  52,006,303-52,013,625, sha256 `172f97ee781f1603ab1b2837d155aa84dd5ffa4a7d473958b466b29f73fdcff6`. That file is no longer in the
  working tree (overwritten by the valid run's re-pin); it is in git at commit `665a14a` (`initialize-topup.csv.gz` / `.json`).
- `searcher ready` 01:37:18.753Z (tokens 75,009, pools 11,779, cycles 9,494), then `subscribed to newHeads via websocket`; no
  heartbeat during 1,200 s; `shutting down` with `ticks: 0`, `logsApplied: 0`, `touchedPools: 0`; 18 log records.
- Details and the observed websocket facts: `attempts/20261001T010337Z-no-blocks/ATTEMPT-NOTE.md`.
- The attempt files were moved by hand before the relaunch (commit `c61317e`); the runner's own move step therefore did not run
  (the valid run's `collect/run_v4_live.log` has no "earlier attempt files moved" line), and `collect/state/concurrent-engines.jsonl`
  was not moved: it holds the samples of both windows (20 + 20 lines).
- During the attempt window the concurrent-engine samples list the detection-only engines of `../07-other-chains-engine`
  (`--chain mainnet` first in the 01:40Z sample, `--chain arbitrum` first in the 01:42Z sample); no Base engine.

## Engine changes (`bot/src`): opt-in flag `--v4-pools` (commit `5c1baf2`) and opt-in switch `NO_WS=1` (commit `44f92d5`)

Base code: `bot/src` as of commit `fd8d236` (unchanged through HEAD `502dc7b` at preparation time). The section 2.6 run
(`prior/dry-all.log.gz`) used the same code apart from these two opt-in changes. Without `--v4-pools` and without `NO_WS=1`
the engine behaves as before. `git log fd8d236..HEAD -- bot/src` lists only `5c1baf2` and `44f92d5`.
(Correction 2026-10-01: the heading said "the only change under bot/src: opt-in flag `--v4-pools`". The `NO_WS=1` switch was
added afterwards for the repeated run.)

Files touched by `5c1baf2` (committed 2026-10-01T01:04:41Z):
- `bot/src/pools/v4file.ts` (new): `expandV4PoolFiles(spec)`, `loadV4PoolsFromFile(client, cfg, spec, tokens)`, type `V4FileStats`.
- `bot/src/pools/v4.ts`: pool-object construction moved out of `discoverV4Pools` into exported `makeV4Pool(a, poolId, key, t0, t1)`
  (same fields and values); `discoverV4Pools` calls it.
- `bot/src/main.ts`: parses `--v4-pools`; when present, calls `loadV4PoolsFromFile` instead of `discoverV4Pools` (GeckoTerminal),
  appends the added tokens to the universe and to the `symbolOf`/`decimalsOf` maps, and after `filterByDepth` logs one info record
  `v4 pools loaded from file`. The existing `loadStaticMetadata` / `syncPools` / `pruneEmpty` / `buildEthPrices` / `filterByDepth`
  path runs unchanged on the combined pool list.

Files touched by `44f92d5` (committed 2026-10-01T02:06:30Z):
- `bot/src/util/client.ts`: `makeWsClient` returns null when `process.env.NO_WS === "1"`.
- `bot/src/main.ts`: with no websocket client, the existing `setInterval` `eth_blockNumber` poll runs (interval
  `max(150, blockTimeMs / 4)`); the poll callback now catches RPC errors and logs a warn record `block-number poll failed`
  (previously an unhandled rejection), and one info record `polling eth_blockNumber over HTTP (no websocket)` (`everyMs`) is
  logged when the poll starts. With a websocket client (default) nothing changes.

`--v4-pools` value: comma-separated list of files or globs (`*`/`?` in the file name only); `.csv` or `.csv.gz` with a header row.
Required columns `pool_id, currency0, currency1, fee_raw, tick_spacing, hooks`; `block_number` is used for the block range when
present. This is the schema of `../01-v4-pools/initialize-part-NNNN.csv.gz` (V4INIT) and of `initialize-topup.csv.gz`.

Loader steps (in order) and the counters of the `v4 pools loaded from file` record (as committed in `5c1baf2`):

| step | counters |
|---|---|
| read every data row of every file (a missing required column or unreadable gzip aborts startup) | `files`, `rowsRead`, `rowsPerFile[]` (`file`, `rows`, and `indexRows` = the part's row count in a sibling `initialize-parts.json` when one exists), `indexRowMismatches`, `blockMin`, `blockMax` |
| rows with a column count different from the header, or unparsable fee / tick spacing / hook address | `droppedMalformed` |
| existing `isPriceable(key)` (v4.ts) is false: `fee_raw == 0x800000` (dynamic fee) | `droppedDynamicFee` |
| existing `isPriceable(key)` is false for a static-fee key: hook address with any of the before_swap (bit 7), after_swap (bit 6), before_swap_returns_delta (bit 3), after_swap_returns_delta (bit 2) flags | `droppedHookSwapFlags` |
| second row with the same pool_id (among priceable rows only) | `droppedDuplicatePoolId` |
| `pool_id != keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks))` (existing `poolIdOf`) | `droppedPoolIdMismatch` |
| rows passing the checks above | `priceable` = `priceableHookless` + `priceableWithHook` |
| currency `0x0` (native ETH) mapped to WETH as `discoverV4Pools` does; pools where both sides are then WETH (ETH/WETH) | `droppedSameTokenAfterNativeMapping` |
| `StateView.getLiquidity(poolId)` for every remaining pool at block tag `latest` (not pinned: public nodes refuse `eth_call` far behind head and the pass takes minutes); `client.getBlockNumber()` is read before and after the pass; Multicall3 chunks of 300, 4 in flight, failed calls retried once in chunks of 100 | `liquidityChecked`, `liquidityHeadBefore`, `liquidityHeadAfter`, `liquidityPositive`, `droppedLiquidityZero`, `droppedLiquidityCallFailed` |
| ERC-20 `decimals()` and `symbol()` for currencies of the remaining pools that are not in the token universe (same calls as the factory enumeration in `enumerate.ts`; symbol cut to 12 characters; failed calls retried once) | `tokensNotInUniverse`, `tokensAdded`, `tokenMetadataFailed`, `droppedTokenMetadataFailed` (pools with a currency whose `decimals()` failed) |
| pool objects built with `makeV4Pool` (poolId, key with checksummed addresses, PoolManager, StateView) | `v4PoolsBuilt` |
| timings | `parseMs`, `liquidityMs`, `metadataMs` |
| existing startup `syncPools(force)` over all pools (V2/V3/Slipstream/V4), read from the existing `syncStats` right after it | `startupSyncPools`, `startupSyncStalePools` (pools whose state calls failed), `startupSyncChunkFailures` |
| after the existing `pruneEmpty` and `filterByDepth(minDepthEth)` | `v4AfterPruneEmpty`, `v4AfterDepthFilter`, `minDepthEth` |

Other fields of that record: `spec` (the flag value). Progress records logged before it: `v4 pool files parsed; checking liquidity`
(files, rowsRead, priceable, candidates, parseMs), `v4 pool liquidity checked; fetching token metadata` (liquidityHeadBefore,
liquidityHeadAfter, liquidityChecked, liquidityPositive, droppedLiquidityZero, droppedLiquidityCallFailed, liquidityMs) and
`v4 pools built; starting the engine's startup sync` (tokensNotInUniverse, tokensAdded, tokenMetadataFailed, v4PoolsBuilt,
metadataMs). Note on the liquidity pre-filter: the engine's `poolDepthEth` is 0 for a pool with in-range liquidity 0
(`sideAmounts` returns 0/0), so such pools cannot pass `filterByDepth` at any positive threshold.
(Correction 2026-10-01: this table said the liquidity check ran "at one pinned block (`client.getBlockNumber()` at that moment)"
with counter `liquidityBlock`, and listed only the first progress record. That described the uncommitted loader version used by
the verification startup on 2026-09-30, whose log has `liquidityBlock`; the committed version `5c1baf2`, used by the attempt and
by the valid run, is described above.)

Checks done during preparation:
- `npx tsc --noEmit -p tsconfig.json` passes.
- Loader on `initialize-part-0022.csv.gz` alone vs an independent Python count of the same file: rows 258,485; dynamic fee 131,518;
  hook swap flags 73,509; priceable 53,458 (123 with a hook); ETH/WETH 3. All equal.
- Loader parse of all 22 V4INIT parts (RPC stubbed): 15,333,247 rows read (equal to `initialize-parts.json` total_rows),
  239,884 priceable, 239,879 after the ETH/WETH drop, 54 s, heap 249 MB. Independent Python count over the same 22 parts:
  rows 15,333,247; dynamic fee 3,358,756; static fee with hook swap flags 11,734,607; priceable 239,884 (1,481 with a hook);
  ETH/WETH 5; remaining 239,879. Equal.
- Full engine startup with the flag: see "Verification startup" below.
- `NO_WS=1`: per the commit message of `44f92d5`, a 4-minute smoke run with `NO_WS=1` processed 70 blocks (its output is not
  kept in this folder).

## Files

### `live-v4.log` (V4LIVE engine log)
stdout+stderr of the engine run with `LOG_JSON=1`: one pino JSON object per line (lines not starting with `{` are npm/tsx
output; there are none in this run). Common fields: `level` (30 info, 40 warn, 50 error), `time` (epoch ms, UTC), `pid`,
`hostname`, `msg`. Records by `msg`:
- `factory enumerated`: `dex`, `total` (factory length), `enumerated` (newest N read, N <= 6000).
- `universe enumerated; resolving every venue per pair`: `enumeratedPools`, `tokens`, `pairs`.
- `pool discovery complete`: `candidates`, `found`.
- `v4 pool files parsed; checking liquidity`, `v4 pool liquidity checked; fetching token metadata`,
  `v4 pools built; starting the engine's startup sync` and `v4 pools loaded from file`: see the loader table above.
- `searcher ready`: `tokens`, `pools`, `cycles`, `minDepthEth`, `source`, `mode`, `contract`, `codeOverride`.
- `executor self-check passed (ABI ↔ bytecode consistent)`; block trigger record: `polling eth_blockNumber over HTTP (no websocket)`
  (`everyMs`) in this run (`subscribed to newHeads via websocket` in the attempt, the verification startup and the prior runs).
- `heartbeat` (every 10 ticks): cumulative counters `ticks`, `gross` (candidate cycles found), `net` (candidates above
  `--min-profit-usd` after gas), `simulated`, `simOk`, `sent`, `landed`, `failed`, `profitEth`, `gasSpentEth`, `staleTicks`,
  `logsApplied`, `touchedPools`; and `block`, `fb`, `syncMs`, `searchMs`, `totalMs`, `pools`.
- `DRY-RUN: would send`, `simulation reverted`, `simulated net below threshold`: the detection record (schema under `live-v4.jsonl`).
- `shutting down` (on SIGINT): the cumulative counters.
- `tick failed`, `gas refresh failed`, `block-number poll failed`, other warn/error records: as emitted (none in this run).
The prior runs' logs (`prior/*.log.gz`) have the same records in pino-pretty text form (ANSI colour codes, one field per line).
(Correction 2026-10-01: the list named only `subscribed to newHeads via websocket` as the trigger record and only the first
loader progress record.)

### `live-v4.jsonl` (V4LIVE `--out`)
One JSON object per detection that reached simulation, same schema as the prior runs: `t` (UTC ISO time written), `block`, `fb`
(0 in logs mode), `route` (hops `IN>OUT@Dex/fee`), `pools` (pool addresses in hop order; a V4 pool appears as the first 20 bytes of
its pool id), `token` (profit token symbol), `amountIn` (human units), `predictedProfitUsd`, `gasUsd`, `netUsd` (engine's local
math), `gapBps`, `sim` (`eth_call` simulation of the executor with a bytecode override: `{profitUsd, gas, ms}` or `{error, ms}`),
optional `simLatest`, `simNetUsd` (present when the simulation succeeded), optional `blacklisted`. USD values use the engine's
token-to-ETH map and the WETH/USDC price at that time. Dry mode: nothing is sent. Keys present in this file: amountIn,
blacklisted, block, fb, gapBps, gasUsd, netUsd, pools, predictedProfitUsd, route, sim, simNetUsd, t, token.
Kept as plain JSONL (not gzipped): `bot/src/research/analyze.ts` reads plain JSONL (`fs.readFileSync(file, "utf8")`).

### `run-times.json` (written by `collect/v4live_helper.py finalize`)
`status` (DONE / FAILED / RUNNING), `reason`, `command`, `cwd`, `env`, `v4_pools_spec`, `run_seconds_after_ready` (1200),
`script_start_utc`, `v4init_done_seen_utc`, `topup` (status, exit code, rows/block range/sha256 of the top-up, start/end),
`other_engines` (seconds waited for other Base engine processes, the process lists at the first check and at launch; samples during
the run in `collect/state/concurrent-engines.jsonl`), `launch_utc`, `engine_pid`, `engine_pgid`, `head_at_launch` /
`head_at_ready` / `head_at_stop` (`eth_blockNumber`: block, endpoint, time), `ready_detected_utc` (when the script saw the line),
`ready_log_utc` (the record's own time), `planned_stop_utc` (= ready_log_utc + 1200 s), `stop_sigint_utc`, `stop_sigterm_utc`,
`stop_sigkill_utc` (only the signals that were needed), `engine_exit_utc`, `engine_exit_code`, `first_processed_block_in_log` /
`last_processed_block_in_log` (first/last `block` value in log order among records at or after the ready record),
`min_block_in_log_after_ready` / `max_block_in_log_after_ready`, `searcher_ready_line_verbatim`,
`v4_pools_loaded_from_file_line_verbatim`, `shutting_down_line_verbatim`, `last_heartbeat_line_verbatim`, `log_records`,
`log_non_json_lines`, `log_record_counts_by_msg`, `log_error_records`, `log_error_records_first5_verbatim`.
The engine logs a block per tick only in heartbeats (every 10th tick) and detection records, hence the head_at_* fields.
Value notes: `env` is `LOG_JSON=1` only; the engine process also had `NO_WS=1` (see "Method of the valid run"). `engine_pid` /
`engine_pgid` (31767) are the process the runner started (`setsid npx ...`); the node process that writes the log has pid 31793.
`engine_exit_code` 130 = exit on SIGINT.

### `initialize-topup.csv.gz` + `initialize-topup.json`
Initialize events of the PoolManager from block 52,006,303 (V4INIT `block_to` + 1) to `head - 10` at the moment of pinning.
Same 27 columns, decoder and checks as `../01-v4-pools/initialize-part-NNNN.csv.gz` (it imports `../01-v4-pools/collect/common.py`;
see that manifest for the column definitions: block_number, tx_hash, tx_index, log_index, pool_id, currency0, currency1, fee_raw,
tick_spacing, hooks, sqrt_price_x96, tick, dynamic_fee (derived), 14 `hf_*` hook-flag columns (derived)). Every row passed
`pool_id == keccak256(abi.encode(key))`. The JSON holds the pin (from/to block, head at pin, time), rows, sha256, bytes, and the
endpoint that served each 1,000-block chunk. `run_v4_live.sh` re-pins it (`--repin`) right before the launch, so the file on disk
is the one the valid V4LIVE run used: pinned 2026-10-01T02:05:29Z, head at pin 52,015,491, blocks 52,006,303-52,015,481,
847 rows (848 lines with the header; `block_number` values 52,006,334-52,015,467), 10 chunks, 0 gaps, all chunks served by
publicnode. Its rows/range/sha256 are also in `run-times.json.topup`.
Earlier versions (not in the working tree; in git history): pinned 2026-09-30T22:15:19Z, 263 rows, blocks 52,006,303-52,008,576
(used by the verification startup; commit `5a2040a`); pinned 2026-10-01T01:03:38Z, 678 rows, blocks 52,006,303-52,013,625 (used by
the invalid attempt; commit `665a14a`). `endpoint_per_chunk` in the JSON (copied from `collect/state/topup-served.json`) also lists
the last partial chunks of those earlier pins (`52008303_52008576`, `52013303_52013625`).

### `collect/verify-startup.log`, `collect/verify-startup.times`, `collect/verify-startup.jsonl`
The verification startup (step 2): the reference command plus `--v4-pools`, launched with `collect/verify_flag_startup.sh`,
stopped by SIGINT to its process group as soon as `searcher ready` was logged. Same log format as `live-v4.log`.
`.times`: launch / pid / ready_detected / stopped lines (UTC). `.jsonl` is the engine's `--out`: 0 bytes. The engine logged
one tick before it stopped (`shutting down` with `ticks: 1`).
(Correction 2026-10-01: this said "no ticks ran".)
`collect/verify_flag_startup.runner.log` is the (empty, 0 bytes) stdout/stderr of the script.

### `attempts/20261001T010337Z-no-blocks/`
The invalid attempt; see "Invalid attempt". Same file formats as the top-level files of the same names.

### `prior/` (gzip copies of `/home/user/dapparb/bot/data/*`, byte-identical after decompression; sources left in place)

Re-checked 2026-10-01: the sha256 of each decompressed copy equals the source sha256 below, and each source file is still present
with that sha256.

| file | source bytes | source lines | source sha256 | source mtime (UTC) |
|---|---|---|---|---|
| `live-base-all.jsonl.gz` | 38,113 | 93 | `ec635eb5ab0c6ed92e7e61377aa9133db6a7ca0d1e4323c0bd92492b86f15e62` | 17:25:47 |
| `dry-all.log.gz` | 76,763 | 3,143 | `4010cabee45adb2ca78daa2fa795b58aca220daedf125c1956b6e49ac91647df` | 17:25:48 |
| `live-base-blocks-long5.jsonl.gz` | 39,339 | 98 | `85ca35184791692588f7da819971808dab1ac91617182c7e119233db6459ecee` | 16:38:29 |
| `dry-blocks-long5.log.gz` | 79,343 | 3,296 | `38c067fc100409859793ef3935988b9925e3dc5542681130ff5af274c6b238ee` | 16:39:02 |
| `live-base-all-v0.jsonl.gz` | 14,593 | 36 | `d2b4ce63fe2f4afa2c0e259740c7396698cab5df2d867dc625a2bf45c842131b` | 16:55:45 |
| `dry-all-v0.log.gz` | 32,891 | 1,384 | `5145297ec13896a8917c114462532e53cfc54c76bab07925eb088e6151d697cd` | 16:55:45 |

Run descriptions (from the logs themselves; provenance as in `../00-prior-runs/MANIFEST.md`):

| run | log first / ready / last record (UTC, 2026-09-30) | blocks in heartbeats | jsonl records, block range | flags and pool set (from the log) |
|---|---|---|---|---|
| section 2.6 (`dry-all`, `live-base-all`) | 16:55:48 / 17:03:54 / 17:25:47 | 51,999,267-51,999,896 (61 heartbeats) | 93, 51,999,244-51,999,900 | `--universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6`, `--source logs`, dry, websocket `newHeads` trigger. V4 via GeckoTerminal: `uniswap v4 candidates` listed 223, v4 20; `uniswap v4 pools discovered` kept 10 (hooked 4, outOfUniverse 6). `searcher ready`: tokens 33,533, pools 3,189, cycles 3,608 |
| section 2.5 (`dry-blocks-long5`, `live-base-blocks-long5`) | 16:13:30 / 16:16:10 / 16:38:53 | 51,997,828-51,998,493 (66) | 98, 51,997,812-51,998,481 | GeckoTerminal token universe (`token universe built`: 483 top pools, 249 new tokens), `--source logs`, min depth 0.2 ETH, websocket trigger. V4: listed 40, kept 35 (hooked 5). `searcher ready`: tokens 268, pools 657, cycles 2,804 |
| first 2.6 attempt (`dry-all-v0`, `live-base-all-v0`) | 16:37:12 / 16:45:36 / 16:55:43 | 51,998,718-51,998,998 (29) | 36, 51,998,695-51,998,995 | same flags as 2.6, websocket trigger; produced before commit `fd8d236` (token prices not yet anchored to deep WETH/USDC pools). `searcher ready`: tokens 33,528, pools 3,282, cycles 3,652 |

Detection-record schema: as `live-v4.jsonl` above (keys present: amountIn, blacklisted, block, fb, gapBps, gasUsd, netUsd, pools,
predictedProfitUsd, route, sim, simNetUsd, t, token).

### `collect/` (scripts, logs, state)
| file | role |
|---|---|
| `run_v4_live.sh` | V4LIVE orchestration (header comment lists every step) |
| `v4live_helper.py` | `head` (eth_blockNumber), `engines` (running `node ... src/main.ts` processes), `finalize` (writes run-times.json) |
| `topup_initialize.py` | Initialize top-up collector (resumable per 1,000-block chunk; gaps -> `state/topup-gaps.json`, exit code 2) |
| `smoke_topup_compare.py`, `topup_smoke.log` | smoke test of the top-up on blocks 52,005,303-52,006,302 (already in V4INIT): 120 rows, identical to the V4INIT rows |
| `verify_flag_startup.sh`, `verify_flag_startup.runner.log` | verification startup (see above); the runner log is empty |
| `run_v4_live.log` | runner log of the valid run (timestamps of each step) |
| `run_v4_live.attempt-20261001T010337Z.log` | runner log of the invalid attempt (same bytes as `attempts/20261001T010337Z-no-blocks/run_v4_live.log`) |
| `topup_initialize.log` | top-up log: the attempt's pin (01:03:38Z, 678 rows) and the valid run's pin (02:05:29Z, 847 rows), appended |
| `topup_initialize.verify.log` | top-up log of the verification top-up (22:15:19Z, 263 rows) |
| `state/run.kv` (local-only) | key=value lines written by the runner for the valid run (input of `finalize`) |
| `state/run.attempt-20261001T010337Z.kv` (local-only) | the same for the invalid attempt |
| `state/concurrent-engines.jsonl` (local-only) | one line per minute during each window: other running `node ... src/main.ts` processes (any chain); lines 1-20 attempt window, lines 21-40 valid window |
| `state/topup-pin.json`, `state/topup-gaps.json`, `state/topup-served.json`, `work/topup/` (local-only) | top-up pin, gaps, endpoint per chunk, chunk checkpoints (the 10 chunk files of the 02:05:29Z pin; together 847 rows) |
| `state/topup-smoke-*`, `work/topup-smoke/` (local-only) | the same for the smoke test |

## Reproduce

```
# engine changes (bot/src diff fd8d236..44f92d5) and typecheck
cd /home/user/dapparb/bot && npx tsc --noEmit -p tsconfig.json
# top-up of Initialize events after the V4INIT pin (writes ../initialize-topup.csv.gz + .json)
cd /home/user/dapparb/research-material/02-v4-live-test/collect
REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 -u topup_initialize.py --repin
# smoke test of the top-up against V4INIT
python3 -u topup_initialize.py --from 52005303 --to 52006302 --out /tmp/smoke-topup.csv.gz
python3 smoke_topup_compare.py /tmp/smoke-topup.csv.gz 52005303 52006302
# verification startup (stops at 'searcher ready')
./verify_flag_startup.sh "/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz,/home/user/dapparb/research-material/02-v4-live-test/initialize-topup.csv.gz"
# the live test as run for the valid window (detached; waits for V4INIT.DONE, tops up, waits for other Base engines,
# runs 20 min after ready). NO_WS=1 is inherited by the engine (HTTP eth_blockNumber polling instead of the websocket).
NO_WS=1 setsid nohup ./run_v4_live.sh > run_v4_live.log 2>&1 < /dev/null &
# the engine command it runs (from /home/user/dapparb/bot):
LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 \
  --min-profit-usd 0.01 --top 6 \
  --v4-pools '/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz,/home/user/dapparb/research-material/02-v4-live-test/initialize-topup.csv.gz' \
  --out /home/user/dapparb/research-material/02-v4-live-test/live-v4.jsonl > live-v4.log 2>&1
```
A new window: delete `.sentinels/V4LIVE.DONE` (and V4LIVE.FAILED) and rerun `run_v4_live.sh`; if `live-v4.*`, `run-times.json`
or `state/run.kv` exist, the script moves them and `state/concurrent-engines.jsonl` to `attempts/<UTC>/` first. A live window
cannot be resumed; the waiting phase and the top-up are simply redone. (For the valid run the attempt files had been moved by hand
before the relaunch; see "Invalid attempt".) Without `NO_WS=1` the engine uses the websocket trigger, which delivered no
block during the attempt (see the attempt note).

Endpoints: the engine uses its configured Base RPC list with viem fallback (`https://base-rpc.publicnode.com`, `https://base.drpc.org`,
`https://base-mainnet.public.blastapi.io`, `https://mainnet.base.org`; `eth_getBlockReceipts` per block in logs mode). New
blocks: in the valid run `eth_blockNumber` over that HTTP client every 500 ms (`NO_WS=1`); in the attempt, the verification
startup and the prior runs the websocket `wss://base-rpc.publicnode.com` (`newHeads`). The top-up uses publicnode,
mainnet.base.org, developer-access-mainnet.base.org and Tenderly (`eth_getLogs`, 1,000-block chunks, 1 request in flight each,
bisection on range/size errors); every chunk of the three pins in this folder was served by publicnode.
(Correction 2026-10-01: the endpoint text named only the websocket for new heads.)

## Verification startup

(Correction 2026-10-01: this section said "(filled in below after the run)".)

Files: `collect/verify-startup.log` (16 JSON records), `collect/verify-startup.times`, `collect/verify-startup.jsonl` (0 bytes).
- Launched 2026-09-30T22:23:56.186Z by `collect/verify_flag_startup.sh` (pid/pgid 28764; the node process logs pid 28793), with
  the V4INIT parts plus the top-up pinned 22:15:19Z (263 rows). `searcher ready` record 22:54:06.595Z, detected 22:54:07.664Z;
  stopped 22:54:08.671Z (rc 0, SIGINT only). Trigger: `subscribed to newHeads via websocket`.
- Loader version: an uncommitted working-tree version that preceded `5c1baf2`. Its `v4 pools loaded from file` record has the
  field `liquidityBlock` (52,009,038; one pinned block) instead of `liquidityHeadBefore`/`liquidityHeadAfter`, and the log has
  only the first loader progress record. The exact source of that version is not in git.
- `v4 pools loaded from file`: files 23; rowsRead 15,333,510 (indexRowMismatches 0); blockMin 25,352,561; blockMax 52,008,566;
  priceable 239,934 (hookless 238,453, with hook 1,481); droppedDynamicFee 3,358,826; droppedHookSwapFlags 11,734,750;
  droppedSameTokenAfterNativeMapping 5; liquidityChecked 239,929; liquidityPositive 82,445; droppedLiquidityZero 157,484;
  droppedLiquidityCallFailed 0; tokensAdded 41,395; tokenMetadataFailed 0; v4PoolsBuilt 82,445; startupSyncPools 128,579;
  startupSyncStalePools 0; startupSyncChunkFailures 0; v4AfterPruneEmpty 82,445; v4AfterDepthFilter 8,616; parseMs 51,839;
  liquidityMs 105,249; metadataMs 35,963.
- `searcher ready`: tokens 74,993; pools 11,777; cycles 9,488. `shutting down`: ticks 1.

## Time windows and blocks

- V4INIT pool list: Initialize events in blocks 25,350,988-52,006,302 (`../01-v4-pools/initialize-parts.json`, 22 parts,
  15,333,247 rows); plus the top-up 52,006,303-52,015,481 (847 rows, pinned 2026-10-01T02:05:29Z; `initialize-topup.json`,
  `run-times.json.topup`). Row block range across all 23 files as read by the loader: 25,352,561-52,015,467.
- Valid V4LIVE run: engine launch 2026-10-01T02:05:32.677Z (head 52,015,492); `searcher ready` 02:36:04.248Z (head 52,016,409 at
  02:36:06Z); stop 02:56:04.663Z (head 52,017,008); blocks in the log after ready 52,016,408-52,017,008; 516 ticks.
- Liquidity pre-filter: `StateView.getLiquidity` at `latest` between heads 52,015,682 and 52,015,721 (`liquidityHeadBefore` /
  `liquidityHeadAfter` in the `v4 pools loaded from file` record).
- Invalid attempt: launch 01:03:41.575Z (head 52,013,637); `searcher ready` 01:37:18.753Z (head 52,014,646); stop 01:57:18.599Z
  (head 52,015,245); no block processed.
(Correction 2026-10-01: this section said "launch, ready, stop, heads and blocks in `run-times.json` (not known at the time of
writing)" and gave `liquidityBlock` as the pre-filter block.)

## Coverage limits and gaps

- **Pools created after the top-up pin** (head - 10 blocks; pin at 02:05:29Z, block 52,015,481; `searcher ready` followed at
  02:36:04Z, head 52,016,409) and pools created during the run are not in the list: the engine's pool
  set is fixed at startup. The engine also does not re-read the files.
- **Pools the engine cannot price locally are not tracked**: dynamic-fee keys and keys whose hook has a swap flag (existing
  `isPriceable`). They are counted (`droppedDynamicFee`, `droppedHookSwapFlags`), not searched. Per-hook identification of these pools
  (launchpads) is in `../01-v4-pools/hooks.csv`.
- **Liquidity pre-filter**: pools with in-range liquidity 0 at the time of the check (block tag `latest`, heads 52,015,682-52,015,721)
  are dropped before the heavy sync (counted). Pools whose `getLiquidity` call failed twice are dropped and counted
  (`droppedLiquidityCallFailed`).
- **ETH/WETH pools** (native ETH against WETH, same token after the engine's native-to-WETH mapping) are dropped and counted.
- **Token metadata**: pools with a currency whose `decimals()` call failed are dropped and counted. Transfer restrictions or taxes are
  not probed at startup (the engine discovers them only through simulation reverts).
- **Startup sync failures** (whole multicall chunks rejected by a public RPC) leave pools with empty state; `pruneEmpty` then removes
  them. Their number is `startupSyncStalePools` (all pool kinds). Failed tick-data calls are not counted by the engine.
- **Depth filter**: pools under `--min-depth-eth 0.1` are not searched in this run; only `v4AfterPruneEmpty` vs `v4AfterDepthFilter`
  are recorded for V4. The shallow-pool run is in `../04-shallow-pools/`.
- **Non-V4 universe**: identical flags to the section 2.6 run, so the newest 6,000 pools per V2-style factory at launch time (not the
  same pools as at 17:00Z); older V2 pairs are not enumerated.
- **Block trigger**: HTTP `eth_blockNumber` polling every 500 ms (`NO_WS=1`), while the section 2.6 reference run used the websocket
  `newHeads` subscription. The engine logs a block number per tick only in heartbeats (every 10th tick) and detection records.
- **Concurrency**: public, shared RPC endpoints. The runner waits up to 60 min while another Base engine process runs and records
  what it saw (`run-times.json.other_engines`, `collect/state/concurrent-engines.jsonl`). Other agents' collectors (not engines)
  use the same endpoints and are not recorded.
- **Log format**: `LOG_JSON=1` (one JSON record per line); the prior runs used pino-pretty text. The records carry the same fields.
- **One window only**: a single 20-minute window at one time of day, dry mode (no transactions; simulation by `eth_call` only).
- **No analyzer** was run; `live-v4.jsonl` and `live-v4.log` are raw engine output.
- **Provenance caveats** (documented, no data missing): `run-times.json.env` omits `NO_WS=1`; the engine of the valid run (and of
  the attempt) was started from the working tree shortly before the corresponding commit was recorded; the verification startup
  ran an uncommitted earlier loader version; the attempt's top-up file is only in git history (`665a14a`).

## Collector status

| name | sentinel | log | status |
|---|---|---|---|
| V4LIVE | `/home/user/dapparb/research-material/.sentinels/V4LIVE.DONE` ("ok: ran 1200 s after searcher ready", 2026-10-01T02:56:05.719Z) | `collect/run_v4_live.log`, `live-v4.log` | DONE (valid run, `NO_WS=1`); the attempt's earlier DONE sentinel is kept as `attempts/20261001T010337Z-no-blocks/V4LIVE.DONE.invalidated` |

(Correction 2026-10-01: the status column said "scheduled / running".)

## Verified inventory (2026-10-01)

Checked 2026-10-01 ~03:00Z over every file in this folder (recursive). Lines: newline count, streamed; for `.gz` files, of the
decompressed content (CSV line counts include the header). Every `.gz` file passed `gzip -t` and a full streamed decompression.
Every `.json` file parses; every line of every `.jsonl` / `.jsonl.gz` file and of `live-v4.log`, the attempt's `live-v4.log` and
`collect/verify-startup.log` parses as JSON (0 failures). The largest committed file is `initialize-topup.csv.gz` (109,006 bytes);
no committed file exceeds 90 MB. sha256 is given for every file (all are <= 100 MB). "local-only" = git-ignored
(`research-material/**/collect/work/`, `research-material/**/collect/state/`); everything else is committed (`git status` was clean
for this folder before this manifest update).

| file | bytes | lines | sha256 | git |
|---|---|---|---|---|
| `MANIFEST.md` | (this file) | | | committed (earlier version) |
| `initialize-topup.csv.gz` | 109006 | 848 | `5c73fd6c8ea1dbb5cc4e95d5550fc9985026eaa5a377b85165cbf4eaf0871203` | committed |
| `initialize-topup.json` | 2009 | 67 | `1e2ab220d0085b852e51b21b74f8b0cc21a2aee9a1bc82d467a6a086b86c0b42` | committed |
| `live-v4.jsonl` | 20988 | 51 | `b050d2d59cdf32dcc33e2da3a8868da10d6db63c39685affd51063b28cb0693d` | committed |
| `live-v4.log` | 48337 | 120 | `5dc52202c07351f6cd0a19bb88aab3e5cd59f198253b96103eaf35bfef48c26e` | committed |
| `run-times.json` | 7658 | 90 | `01c2481d02439035fea5ac5e858f65f492b9581cc3eedd405715d5c2da355e00` | committed |
| `attempts/20261001T010337Z-no-blocks/ATTEMPT-NOTE.md` | 1438 | 19 | `e1fdc82c87310ff26a960bc86a6f4fec3813ea743c7ba77ec639cb3566e4b85e` | committed |
| `attempts/20261001T010337Z-no-blocks/V4LIVE.DONE.invalidated` | 134 | 2 | `ef327a3b7f4772e646383828bbe6f63a48e724fd2d5f75941b5bc479a5c544f5` | committed |
| `attempts/20261001T010337Z-no-blocks/live-v4.jsonl` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `attempts/20261001T010337Z-no-blocks/live-v4.log` | 5685 | 18 | `92d5925924fc705909f35ca818bea74ee07f1488fac4acca8b67e5aa678ee622` | committed |
| `attempts/20261001T010337Z-no-blocks/run-times.json` | 7103 | 86 | `004129c7f837cda34a8ded8b660d1c0f88c48866979919a445dc7316c7cedea7` | committed |
| `attempts/20261001T010337Z-no-blocks/run_v4_live.log` | 602 | 7 | `f070da43b2dc4ca996253d9207f85b45c057ad56db1ec34d15ca2ecc983016c3` | committed |
| `collect/run_v4_live.attempt-20261001T010337Z.log` | 602 | 7 | `f070da43b2dc4ca996253d9207f85b45c057ad56db1ec34d15ca2ecc983016c3` | committed |
| `collect/run_v4_live.log` | 615 | 7 | `7e142c91829a717061db399384683d6ef63891c5b31027b53b760d46101340f5` | committed |
| `collect/run_v4_live.sh` | 8751 | 166 | `00acbc08585183a9eef1578e7a5ca3ab08cb17d1fbbfbfac12458e09dfac7cc2` | committed |
| `collect/smoke_topup_compare.py` | 792 | 13 | `61fd7660d678b29f5075e17fd27e5f3c829161981e5772b37e6df3dde7c251d2` | committed |
| `collect/topup_initialize.log` | 2261 | 22 | `0a7ff1f6848cc8de707fe6fe0a52df953aaa17f0944890b40c0c1b3702ee8d34` | committed |
| `collect/topup_initialize.py` | 8426 | 189 | `515357031129922f0be2236132dd8744ad8fb0bca67e9aae04d7316f2c24598e` | committed |
| `collect/topup_initialize.verify.log` | 722 | 5 | `b6390e75b54e1cc7db384d19d0080ca427e07366d5e20fafa108c68cd5ef1397` | committed |
| `collect/topup_smoke.log` | 609 | 3 | `2601e0e20d7bed5885a1d7f4d6842198c6a381b6b8c8410018f88b36201f31d5` | committed |
| `collect/v4live_helper.py` | 9360 | 205 | `06cd83c448f68d3fcd651fbf97d181db2f06fe4355cc91f49f224a7dd69fd727` | committed |
| `collect/verify-startup.jsonl` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `collect/verify-startup.log` | 5129 | 16 | `c85be39d501e200c231c1a2cc32af6d8725fb3bc6f25a822023bfb91526b9c58` | committed |
| `collect/verify-startup.times` | 287 | 4 | `1c9ffe9bf7b757842c34b3cbe75068bc460b7141862e143635cf89a4c2803a3d` | committed |
| `collect/verify_flag_startup.runner.log` | 0 | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `collect/verify_flag_startup.sh` | 1493 | 27 | `1ce0e4ab2aeb150b4838006b251625ba1528712b13b7c606e6cdc3e264331410` | committed |
| `collect/state/concurrent-engines.jsonl` | 15779 | 40 | `7a249a31e118f6ca7ff9fdd67820ad6076acd009dbda8642c6316aad0472b9d2` | local-only |
| `collect/state/run.attempt-20261001T010337Z.kv` | 1679 | 29 | `546dfa52d7fb722e722e0e4f05ed62c9e0b8709769ad95528bc44a8c2891904f` | local-only |
| `collect/state/run.kv` | 1683 | 29 | `4f066639bbef3f2237c4180d8956c93caefde8a3042dc856b7f98312c2d2dacf` | local-only |
| `collect/state/topup-gaps.json` | 439 | 14 | `707b9d9d97c852fd16ab1b2b6ff726ab322d43336e631dc435dc2eeeede0e15f` | local-only |
| `collect/state/topup-pin.json` | 364 | 10 | `bc7e2ea2e2c8141b304651a58f6eb5434f10a70e5eb3221040e7f07409235d99` | local-only |
| `collect/state/topup-served.json` | 434 | 13 | `a432aedf460b7b1902b4765a843b33c7e5e2092570d8216a4fde6575689f4568` | local-only |
| `collect/state/topup-smoke-gaps.json` | 416 | 14 | `87a2bcbc9de1d73c9c329f4945452e2420e714f6f95c0dbdc35adca6fecf91ab` | local-only |
| `collect/state/topup-smoke-pin.json` | 341 | 10 | `83b5c45f548127b027315123b2acfb089d5d1191885105d0abee8b5b6b0d3f78` | local-only |
| `collect/state/topup-smoke-served.json` | 38 | 2 | `c73969a0ff5d65fe59979ee90b898d49721d3f5ccad098ea3df16d427c327358` | local-only |
| `collect/work/topup/c_52006303_52007302.csv.gz` | 13180 | 97 | `391b6dde97b6d3086f47d640546dd36bd76cb8e4d6ee6f7b07438d5d6f8be36c` | local-only |
| `collect/work/topup/c_52007303_52008302.csv.gz` | 18573 | 143 | `15b2573fbc791b4a9b0425ac511909bdfc2e5e77f353d3695f19cd2557b6c8d6` | local-only |
| `collect/work/topup/c_52008303_52009302.csv.gz` | 12228 | 94 | `5af06b23a5748f013dcfb0d847d1cebd6d9d72c53a76d29c820f2ccbdcac6a88` | local-only |
| `collect/work/topup/c_52009303_52010302.csv.gz` | 10575 | 76 | `a1bbc5dafa7f7675e627d015aaa64fcb0261a81cda73d87ca675568da8ea5ed9` | local-only |
| `collect/work/topup/c_52010303_52011302.csv.gz` | 11326 | 82 | `13da977f35717847efeb873353ee4e7933acf57f747ba970d1b3919c08390c78` | local-only |
| `collect/work/topup/c_52011303_52012302.csv.gz` | 12505 | 92 | `c6fd7388d363d758df68fa2538b496a58fa70e4e68bfb7de08a57969e7a9bd20` | local-only |
| `collect/work/topup/c_52012303_52013302.csv.gz` | 9807 | 72 | `ae0068f31e65eed38fd501e96e56e6ac167f01bc132eb99404af095d02f47f2a` | local-only |
| `collect/work/topup/c_52013303_52014302.csv.gz` | 9315 | 68 | `296c728bdbce6e113480b807c380fe0c7829a2ef60e8d6a7819580790228fc01` | local-only |
| `collect/work/topup/c_52014303_52015302.csv.gz` | 13862 | 103 | `99ba975d7269599697e5cb8537cc4a6c84e84009b99a33454b8068c5197b0013` | local-only |
| `collect/work/topup/c_52015303_52015481.csv.gz` | 2987 | 20 | `9940b54de2a1a0eba9d38972e5ac5edb2518615bef9c16c61ff38648f54e8712` | local-only |
| `collect/work/topup-smoke/c_52005303_52006302.csv.gz` | 15836 | 120 | `41066750a2d851e6527aa52d3fc2a7e74139a129bdfece586f161280ef262474` | local-only |
| `prior/dry-all-v0.log.gz` | 5365 | 1384 | `ad91602ab99f58b2eb91d7b17b77868705ad733127b5a9c06a1d2ae5349612b8` | committed |
| `prior/dry-all.log.gz` | 11268 | 3143 | `dbb4dae5fbb3015603dd5d508755bb1f8e20d2f9c07746db66646029368030c8` | committed |
| `prior/dry-blocks-long5.log.gz` | 11010 | 3296 | `873d62b28eca17e3975ca747202b71be9714751c956b9504ccb3fe971b78e00e` | committed |
| `prior/live-base-all-v0.jsonl.gz` | 2964 | 36 | `138f6a42e04e271eaf1ee3867fc4e58b6d64c07ae9b51cdcb34355c1d7dcda77` | committed |
| `prior/live-base-all.jsonl.gz` | 6488 | 93 | `788e9edda03b2291bbbc795bf144ad390198208947819c8eb108258a627280a8` | committed |
| `prior/live-base-blocks-long5.jsonl.gz` | 6156 | 98 | `641f80afdcc5cfb2f28a30b8a04495c112cd215094b888395c6515ba75673e78` | committed |

The `collect/work/topup/` chunk files have no header line (data rows only); their line counts sum to 847, equal to the data
rows of `initialize-topup.csv.gz`. `topup_initialize.py --repin` deletes every chunk file before pinning, so only the chunks of the
02:05:29Z pin are present.

## Corrections made on 2026-10-01 (summary)

- Status: "IN PROGRESS / scheduled" -> COMPLETE; collector status "scheduled / running" -> DONE.
- Question-line keys replaced by line numbers 1-8; mapping kept (see that section).
- Engine changes: two opt-in commits (`5c1baf2`, `44f92d5`), not one; `NO_WS=1` described.
- Liquidity pre-filter: block tag `latest` with `liquidityHeadBefore` / `liquidityHeadAfter` (committed code), not one pinned block
  `liquidityBlock` (uncommitted version used only by the verification startup); two more loader progress records listed.
- `collect/verify-startup.jsonl`: the engine ran one tick before the stop (not "no ticks").
- Top-up: the file on disk is the 02:05:29Z pin (847 rows); the 678-row 01:03:38Z pin belonged to the invalid attempt.
- Verification startup, time windows and blocks, endpoints, reproduce command and the `collect/` table filled in or updated.
