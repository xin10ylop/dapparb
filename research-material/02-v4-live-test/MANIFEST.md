# 02-v4-live-test: the reference 20-minute live test with every Uniswap V4 pool from PoolManager Initialize events

STATUS: IN PROGRESS. The V4LIVE run is scheduled (detached `collect/run_v4_live.sh`). When it ends it writes
`/home/user/dapparb/research-material/.sentinels/V4LIVE.DONE` (or `V4LIVE.FAILED` with the reason), `run-times.json`,
`live-v4.log` and `live-v4.jsonl`. Row and record counts of those files are not filled in here; a later agent reads them
from the files (see "Collector status").

This directory contains collected data only: engine output, run metadata and copies of earlier runs. It holds no analysis,
rankings or conclusions. No analyzer was run on any output.

- Chain: Base (chain id 8453), 2-second blocks. Block timestamp: `1686789347 + 2 * block_number` (checked in
  `../01-v4-pools/timestamps-check.csv`).
- Uniswap V4 PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b`, StateView `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`,
  Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`, WETH `0x4200000000000000000000000000000000000006`.
- Prepared 2026-09-30 between 22:00Z and 22:45Z.

## Question lines served (mapping only)

Keys (quoted from the user's text):
- Q-V4GAP: "Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet."
- Q-OLDV2: "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens."
- Q-SMALL: "Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit."
- Q-LAUNCH: "V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee."
- Q-BEYOND: "So the search went far beyond selected pairs, but it did not cover everything."
- Q-MEASURE: "The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test."

| File | Q-V4GAP | Q-OLDV2 | Q-SMALL | Q-LAUNCH | Q-BEYOND | Q-MEASURE |
|---|---|---|---|---|---|---|
| `live-v4.log` (engine log of the V4LIVE run, incl. the `v4 pools loaded from file` and `factory enumerated` records) | x | x | x | x | x | x |
| `live-v4.jsonl` (detections of the V4LIVE run) | x | | | x | x | x |
| `run-times.json` (launch/ready/stop times, blocks, verbatim key log lines) | x | | | x | | x |
| `initialize-topup.csv.gz` + `initialize-topup.json` (Initialize events after the V4INIT pin, up to the launch) | x | | | x | | x |
| `collect/verify-startup.log`, `collect/verify-startup.times` (verification startup with the flag, stopped at `searcher ready`) | x | x | x | | x | x |
| `prior/live-base-all.jsonl.gz`, `prior/dry-all.log.gz` (section 2.6 run, V4 from GeckoTerminal) | x | x | x | | x | x |
| `prior/live-base-blocks-long5.jsonl.gz`, `prior/dry-blocks-long5.log.gz` (section 2.5 run) | | | | | x | x |
| `prior/live-base-all-v0.jsonl.gz`, `prior/dry-all-v0.log.gz` (first 2.6 attempt, contains the RSR/WETH detection at block 51998756) | x | | | x | x | x |

Not covered here: other chains, BSC ordering, chain-wide studies (other directories).

## Engine change (the only change under bot/src): opt-in flag `--v4-pools`

Base code: `bot/src` as of commit `fd8d236` (unchanged through HEAD `502dc7b` at preparation time). The section 2.6 run
(`prior/dry-all.log.gz`) used the same code apart from this flag. Without `--v4-pools` the engine behaves as before.

Files touched (`git diff -- bot/src`):
- `bot/src/pools/v4file.ts` (new): `expandV4PoolFiles(spec)`, `loadV4PoolsFromFile(client, cfg, spec, tokens)`, type `V4FileStats`.
- `bot/src/pools/v4.ts`: pool-object construction moved out of `discoverV4Pools` into exported `makeV4Pool(a, poolId, key, t0, t1)`
  (same fields and values); `discoverV4Pools` calls it.
- `bot/src/main.ts`: parses `--v4-pools`; when present, calls `loadV4PoolsFromFile` instead of `discoverV4Pools` (GeckoTerminal),
  appends the added tokens to the universe and to the `symbolOf`/`decimalsOf` maps, and after `filterByDepth` logs one info record
  `v4 pools loaded from file`. The existing `loadStaticMetadata` / `syncPools` / `pruneEmpty` / `buildEthPrices` / `filterByDepth`
  path runs unchanged on the combined pool list.

`--v4-pools` value: comma-separated list of files or globs (`*`/`?` in the file name only); `.csv` or `.csv.gz` with a header row.
Required columns `pool_id, currency0, currency1, fee_raw, tick_spacing, hooks`; `block_number` is used for the block range when
present. This is the schema of `../01-v4-pools/initialize-part-NNNN.csv.gz` (V4INIT) and of `initialize-topup.csv.gz`.

Loader steps (in order) and the counters of the `v4 pools loaded from file` record:

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
| `StateView.getLiquidity(poolId)` for every remaining pool at one pinned block (`client.getBlockNumber()` at that moment), Multicall3 chunks of 300, 4 in flight, failed calls retried once in chunks of 100 | `liquidityChecked`, `liquidityBlock`, `liquidityPositive`, `droppedLiquidityZero`, `droppedLiquidityCallFailed` |
| ERC-20 `decimals()` and `symbol()` for currencies of the remaining pools that are not in the token universe (same calls as the factory enumeration in `enumerate.ts`; symbol cut to 12 characters; failed calls retried once) | `tokensNotInUniverse`, `tokensAdded`, `tokenMetadataFailed`, `droppedTokenMetadataFailed` (pools with a currency whose `decimals()` failed) |
| pool objects built with `makeV4Pool` (poolId, key with checksummed addresses, PoolManager, StateView) | `v4PoolsBuilt` |
| timings | `parseMs`, `liquidityMs`, `metadataMs` |
| existing startup `syncPools(force)` over all pools (V2/V3/Slipstream/V4), read from the existing `syncStats` right after it | `startupSyncPools`, `startupSyncStalePools` (pools whose state calls failed), `startupSyncChunkFailures` |
| after the existing `pruneEmpty` and `filterByDepth(minDepthEth)` | `v4AfterPruneEmpty`, `v4AfterDepthFilter`, `minDepthEth` |

Other fields of that record: `spec` (the flag value). A progress record `v4 pool files parsed; checking liquidity` (files, rowsRead,
priceable, candidates, parseMs) is logged after parsing. Note on the liquidity pre-filter: the engine's `poolDepthEth` is 0 for a
pool with in-range liquidity 0 (`sideAmounts` returns 0/0), so such pools cannot pass `filterByDepth` at any positive threshold.

Checks done during preparation:
- `npx tsc --noEmit -p tsconfig.json` passes.
- Loader on `initialize-part-0022.csv.gz` alone vs an independent Python count of the same file: rows 258,485; dynamic fee 131,518;
  hook swap flags 73,509; priceable 53,458 (123 with a hook); ETH/WETH 3. All equal.
- Loader parse of all 22 V4INIT parts (RPC stubbed): 15,333,247 rows read (equal to `initialize-parts.json` total_rows),
  239,884 priceable, 239,879 after the ETH/WETH drop, 54 s, heap 249 MB.
- Full engine startup with the flag: see "Verification startup" below.

## Files

### `live-v4.log` (V4LIVE engine log)
stdout+stderr of the engine run with `LOG_JSON=1`: one pino JSON object per line (lines not starting with `{` are npm/tsx
output). Common fields: `level` (30 info, 40 warn, 50 error), `time` (epoch ms, UTC), `pid`, `hostname`, `msg`. Records by `msg`:
- `factory enumerated`: `dex`, `total` (factory length), `enumerated` (newest N read, N <= 6000).
- `universe enumerated; resolving every venue per pair`: `enumeratedPools`, `tokens`, `pairs`.
- `pool discovery complete`: `candidates`, `found`.
- `v4 pool files parsed; checking liquidity` and `v4 pools loaded from file`: see the table above.
- `searcher ready`: `tokens`, `pools`, `cycles`, `minDepthEth`, `source`, `mode`, `contract`, `codeOverride`.
- `executor self-check passed (ABI ↔ bytecode consistent)`, `subscribed to newHeads via websocket`.
- `heartbeat` (every 10 ticks): cumulative counters `ticks`, `gross` (candidate cycles found), `net` (candidates above
  `--min-profit-usd` after gas), `simulated`, `simOk`, `sent`, `landed`, `failed`, `profitEth`, `gasSpentEth`, `staleTicks`,
  `logsApplied`, `touchedPools`; and `block`, `fb`, `syncMs`, `searchMs`, `totalMs`, `pools`.
- `DRY-RUN: would send`, `simulation reverted`, `simulated net below threshold`: the detection record (schema under `live-v4.jsonl`).
- `shutting down` (on SIGINT): the cumulative counters.
- `tick failed`, `gas refresh failed`, other warn/error records: as emitted.
The prior runs' logs (`prior/*.log.gz`) have the same records in pino-pretty text form (ANSI colour codes, one field per line).

### `live-v4.jsonl` (V4LIVE `--out`)
One JSON object per detection that reached simulation, same schema as the prior runs: `t` (UTC ISO time written), `block`, `fb`
(0 in logs mode), `route` (hops `IN>OUT@Dex/fee`), `pools` (pool addresses in hop order; a V4 pool appears as the first 20 bytes of
its pool id), `token` (profit token symbol), `amountIn` (human units), `predictedProfitUsd`, `gasUsd`, `netUsd` (engine's local
math), `gapBps`, `sim` (`eth_call` simulation of the executor with a bytecode override: `{profitUsd, gas, ms}` or `{error, ms}`),
optional `simLatest`, `simNetUsd` (present when the simulation succeeded), optional `blacklisted`. USD values use the engine's
token-to-ETH map and the WETH/USDC price at that time. Dry mode: nothing is sent.

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

### `initialize-topup.csv.gz` + `initialize-topup.json`
Initialize events of the PoolManager from block 52,006,303 (V4INIT `block_to` + 1) to `head - 10` at the moment of pinning.
Same 27 columns, decoder and checks as `../01-v4-pools/initialize-part-NNNN.csv.gz` (it imports `../01-v4-pools/collect/common.py`;
see that manifest for the column definitions: block_number, tx_hash, tx_index, log_index, pool_id, currency0, currency1, fee_raw,
tick_spacing, hooks, sqrt_price_x96, tick, dynamic_fee (derived), 14 `hf_*` hook-flag columns (derived)). Every row passed
`pool_id == keccak256(abi.encode(key))`. The JSON holds the pin (from/to block, head at pin, time), rows, sha256, bytes, and the
endpoint that served each 1,000-block chunk. `run_v4_live.sh` re-pins it (`--repin`) right before the launch, so the file on disk
is the one the V4LIVE run used (its rows/range/sha256 are also copied into `run-times.json`). A version pinned at 22:15:19Z
(263 rows, blocks 52,006,303-52,008,576) was used for the verification startup and is replaced by the run.

### `collect/verify-startup.log`, `collect/verify-startup.times`, `collect/verify-startup.jsonl`
The verification startup (step 2): the reference command plus `--v4-pools`, launched with `collect/verify_flag_startup.sh`,
stopped by SIGINT to its process group as soon as `searcher ready` was logged. Same log format as `live-v4.log`.
`.times`: launch / pid / ready_detected / stopped lines (UTC). `.jsonl` is the engine's `--out` (no ticks ran, normally empty).

### `prior/` (gzip copies of `/home/user/dapparb/bot/data/*`, byte-identical after decompression; sources left in place)

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
| section 2.6 (`dry-all`, `live-base-all`) | 16:55:48 / 17:03:54 / 17:25:47 | 51,999,267-51,999,896 (61 heartbeats) | 93, 51,999,244-51,999,900 | `--universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6`, `--source logs`, dry. V4 via GeckoTerminal: `uniswap v4 candidates` listed 223, v4 20; `uniswap v4 pools discovered` kept 10 (hooked 4, outOfUniverse 6). `searcher ready`: tokens 33,533, pools 3,189, cycles 3,608 |
| section 2.5 (`dry-blocks-long5`, `live-base-blocks-long5`) | 16:13:30 / 16:16:10 / 16:38:53 | 51,997,828-51,998,493 (66) | 98, 51,997,812-51,998,481 | GeckoTerminal token universe (`token universe built`: 483 top pools, 249 new tokens), `--source logs`, min depth 0.2 ETH. V4: listed 40, kept 35 (hooked 5). `searcher ready`: tokens 268, pools 657, cycles 2,804 |
| first 2.6 attempt (`dry-all-v0`, `live-base-all-v0`) | 16:37:12 / 16:45:36 / 16:55:43 | 51,998,718-51,998,998 (29) | 36, 51,998,695-51,998,995 | same flags as 2.6; produced before commit `fd8d236` (token prices not yet anchored to deep WETH/USDC pools). `searcher ready`: tokens 33,528, pools 3,282, cycles 3,652 |

Detection-record schema: as `live-v4.jsonl` above (keys present: amountIn, blacklisted, block, fb, gapBps, gasUsd, netUsd, pools,
predictedProfitUsd, route, sim, simNetUsd, t, token).

### `collect/` (scripts, logs, state)
| file | role |
|---|---|
| `run_v4_live.sh` | V4LIVE orchestration (header comment lists every step) |
| `v4live_helper.py` | `head` (eth_blockNumber), `engines` (running `node ... src/main.ts` processes), `finalize` (writes run-times.json) |
| `topup_initialize.py` | Initialize top-up collector (resumable per 1,000-block chunk; gaps -> `state/topup-gaps.json`, exit code 2) |
| `smoke_topup_compare.py`, `topup_smoke.log` | smoke test of the top-up on blocks 52,005,303-52,006,302 (already in V4INIT): 120 rows, identical to the V4INIT rows |
| `verify_flag_startup.sh` | verification startup (see above) |
| `run_v4_live.log` | runner log (timestamps of each step) |
| `topup_initialize.log`, `topup_initialize.verify.log` | top-up logs of the V4LIVE run and of the verification top-up |
| `state/run.kv` | key=value lines written by the runner (input of `finalize`) |
| `state/concurrent-engines.jsonl` | one line per minute during the window: other running `node ... src/main.ts` processes (any chain) |
| `state/topup-pin.json`, `state/topup-gaps.json`, `state/topup-served.json`, `work/topup/` | top-up pin, gaps, endpoint per chunk, chunk checkpoints |
| `state/topup-smoke-*`, `work/topup-smoke/` | the same for the smoke test |

## Reproduce

```
# engine flag (bot/src diff) and typecheck
cd /home/user/dapparb/bot && npx tsc --noEmit -p tsconfig.json
# top-up of Initialize events after the V4INIT pin (writes ../initialize-topup.csv.gz + .json)
cd /home/user/dapparb/research-material/02-v4-live-test/collect
REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 -u topup_initialize.py --repin
# smoke test of the top-up against V4INIT
python3 -u topup_initialize.py --from 52005303 --to 52006302 --out /tmp/smoke-topup.csv.gz
python3 smoke_topup_compare.py /tmp/smoke-topup.csv.gz 52005303 52006302
# verification startup (stops at 'searcher ready')
./verify_flag_startup.sh "/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz,/home/user/dapparb/research-material/02-v4-live-test/initialize-topup.csv.gz"
# the live test (detached; waits for V4INIT.DONE, tops up, waits for other Base engines, runs 20 min after ready)
setsid nohup ./run_v4_live.sh > run_v4_live.log 2>&1 < /dev/null &
# the engine command it runs (from /home/user/dapparb/bot):
LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 \
  --min-profit-usd 0.01 --top 6 \
  --v4-pools '/home/user/dapparb/research-material/01-v4-pools/initialize-part-*.csv.gz,/home/user/dapparb/research-material/02-v4-live-test/initialize-topup.csv.gz' \
  --out /home/user/dapparb/research-material/02-v4-live-test/live-v4.jsonl > live-v4.log 2>&1
```
A new window: delete `.sentinels/V4LIVE.DONE` (and V4LIVE.FAILED) and rerun `run_v4_live.sh`; the previous `live-v4.*`,
`run-times.json`, `state/run.kv` and `state/concurrent-engines.jsonl` are moved to `attempts/<UTC>/` first. A live window cannot
be resumed; the waiting phase and the top-up are simply redone.

Endpoints: the engine uses its configured Base RPC list with viem fallback (`https://base-rpc.publicnode.com`, `https://base.drpc.org`,
`https://base-mainnet.public.blastapi.io`, `https://mainnet.base.org`; websocket `wss://base-rpc.publicnode.com` for new heads;
`eth_getBlockReceipts` per block in logs mode). The top-up uses publicnode, mainnet.base.org, developer-access-mainnet.base.org and
Tenderly (`eth_getLogs`, 1,000-block chunks, 1 request in flight each, bisection on range/size errors).

## Verification startup

(filled in below after the run)

## Time windows and blocks

- V4INIT pool list: Initialize events in blocks 25,350,988-52,006,302 (`../01-v4-pools/initialize-parts.json`, 22 parts,
  15,333,247 rows); plus the top-up from 52,006,303 to the top-up pin (`initialize-topup.json`, `run-times.json.topup`).
- V4LIVE: launch, ready, stop, heads and blocks in `run-times.json` (not known at the time of writing).
- Liquidity pre-filter block: `liquidityBlock` in the `v4 pools loaded from file` record.

## Coverage limits and gaps

- **Pools created after the top-up pin** (head - 10 blocks, taken a few minutes before the launch) and pools created during the
  run are not in the list: the engine's pool set is fixed at startup. The engine also does not re-read the files.
- **Pools the engine cannot price locally are not tracked**: dynamic-fee keys and keys whose hook has a swap flag (existing
  `isPriceable`). They are counted (`droppedDynamicFee`, `droppedHookSwapFlags`), not searched. Per-hook identification of these pools
  (launchpads) is in `../01-v4-pools/hooks.csv`.
- **Liquidity pre-filter**: pools with in-range liquidity 0 at `liquidityBlock` are dropped before the heavy sync (counted). Pools
  whose `getLiquidity` call failed twice are dropped and counted (`droppedLiquidityCallFailed`).
- **ETH/WETH pools** (native ETH against WETH, same token after the engine's native-to-WETH mapping) are dropped and counted.
- **Token metadata**: pools with a currency whose `decimals()` call failed are dropped and counted. Transfer restrictions or taxes are
  not probed at startup (the engine discovers them only through simulation reverts).
- **Startup sync failures** (whole multicall chunks rejected by a public RPC) leave pools with empty state; `pruneEmpty` then removes
  them. Their number is `startupSyncStalePools` (all pool kinds). Failed tick-data calls are not counted by the engine.
- **Depth filter**: pools under `--min-depth-eth 0.1` are not searched in this run; only `v4AfterPruneEmpty` vs `v4AfterDepthFilter`
  are recorded for V4. The shallow-pool run is in `../04-shallow-pools/`.
- **Non-V4 universe**: identical flags to the section 2.6 run, so the newest 6,000 pools per V2-style factory at launch time (not the
  same pools as at 17:00Z); older V2 pairs are not enumerated.
- **Concurrency**: public, shared RPC endpoints. The runner waits up to 60 min while another Base engine process runs and records
  what it saw (`run-times.json.other_engines`, `collect/state/concurrent-engines.jsonl`). Other agents' collectors (not engines)
  use the same endpoints and are not recorded.
- **Log format**: `LOG_JSON=1` (one JSON record per line); the prior runs used pino-pretty text. The records carry the same fields.
- **One window only**: a single 20-minute window at one time of day, dry mode (no transactions; simulation by `eth_call` only).
- **No analyzer** was run; `live-v4.jsonl` and `live-v4.log` are raw engine output.

## Collector status

| name | sentinel | log | status at writing |
|---|---|---|---|
| V4LIVE | `/home/user/dapparb/research-material/.sentinels/V4LIVE.DONE` / `.FAILED` | `collect/run_v4_live.log`, `live-v4.log` | scheduled / running (see below) |
