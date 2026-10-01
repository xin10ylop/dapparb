# 04-shallow-pools — MANIFEST

**Status: IN PROGRESS** (written 2026-09-30 ~22:06 UTC while collectors were running; the counts marked
`TBD` are filled in by a later agent from `run-times.json`, `snapshot-meta.json` and the sentinels).

This directory has raw material only. It contains no analysis, rankings or conclusions.

| Collector | Sentinel | Status at writing |
|---|---|---|
| Live engine run, shallow pools (step 3) | `.sentinels/SHALLOW_LIVE.DONE` / `.FAILED` | running (ready 22:03:50Z, scheduled stop ~22:23:51Z) |
| Pinned-block universe snapshot (step 1) | `.sentinels/SHALLOW_SNAPSHOT.DONE` / `.FAILED` | running (pinned block 52008246) |
| Transfer-behaviour probe (step 2) | `.sentinels/TRANSFER_PROBE.FAILED` | **not collected** (see Coverage limits) |

## Question lines served (mapping only)

| File(s) | Question line(s) |
|---|---|
| `live-shallow.jsonl`, `live-shallow.log`, `run-times.json` | "Pools under 0.1 ETH of liquidity…"; "…rerunning the same 20-minute live test" (same engine and flags as §2.6, except `--min-depth-eth 0.001`) |
| `pools-prefilter.csv.gz`, `pools-pruned-empty.csv.gz`, `cl-ticks-prefilter.csv.gz`, `prices.csv.gz`, `tokens.csv.gz` | "Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity…"; "So the search went far beyond selected pairs, but it did not cover everything" |
| `factory-enumeration.csv.gz`, `snapshot-meta.json` (`fn_stats`, factory totals in `collect/snapshot.log`) | "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs" |
| `geckoterminal-responses.jsonl.gz`, V4 rows in `pools-*.csv.gz`, `v4-poolmanager-balances.csv.gz` | "Uniswap V4 on Base… I only had 20 V4 pools… It just doesn't list every V4 pool yet" (this directory only has the GeckoTerminal-listed V4 set the engine uses; the full V4 pool list is in `../01-v4-pools`) |
| `live-shallow.jsonl` field `sim.error` | "They are also where most tokens that block or tax transfers sit" (only the engine's own simulation reverts; the dedicated transfer probe was not collected) |

## Sources and endpoints

- Base mainnet (chain id 8453) JSON-RPC via the engine's own client (`bot/src/util/client.ts` `makeHttpClient`):
  viem `fallback([base-rpc.publicnode.com, base.drpc.org, base-mainnet.public.blastapi.io, mainnet.base.org], rank=false)`.
  The live engine also uses `wss://base-rpc.publicnode.com` for newHeads.
- GeckoTerminal API v2 (`api.geckoterminal.com/api/v2/networks/base/...`) via `bot/src/research/tokens.ts` `fetchTopPools(cfg, 2)`
  (network top pages 1-2 plus page 1 of each DEX listing in `GT_DEXES`), which `discoverV4Pools` uses for the V4 candidates.
- Contracts: DEX factories/tiers from `bot/src/config/chains.ts` (BASE), V4 PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b`,
  StateView `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`, PositionManager `0x7c5f5a4bbd8fd63184577525326123b519429bdc`,
  Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`.

## Reproduce

No foundry tools are needed. Engine code under bot/src is unmodified.

```bash
# Step 3: live run (detached; waits for 'searcher ready', runs 1200 s more, stops by process group SIGINT->SIGTERM->SIGKILL)
cd /home/user/dapparb/research-material/04-shallow-pools/collect && setsid nohup python3 -u run_live_shallow.py > run_live_shallow.log 2>&1 < /dev/null &
#   the engine command it runs:
#   cd /home/user/dapparb/bot && LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all \
#     --max-per-factory 6000 --min-depth-eth 0.001 --min-profit-usd 0.01 --top 6 \
#     --out /home/user/dapparb/research-material/04-shallow-pools/live-shallow.jsonl  > live-shallow.log 2>&1
#   (LOG_JSON=1 only switches pino output from pino-pretty to one JSON object per line; engine behaviour is unchanged.)
#   Not resumable: a live window cannot be replayed. The launcher exits immediately if run-times.json has status DONE.

# Step 1: snapshot (detached)
cd /home/user/dapparb/research-material/04-shallow-pools/collect && setsid nohup ./run_snapshot.sh > run_snapshot.log 2>&1 < /dev/null &
#   which runs: cd /home/user/dapparb/bot && LOG_JSON=1 npx tsx ../research-material/04-shallow-pools/collect/snapshot.ts > collect/snapshot.log
#   Re-run at the same block: ./run_snapshot.sh --pin 52008246   (needs an endpoint that serves eth_call at that block;
#   publicnode only serves recent blocks, drpc/blastapi serve archive eth_call)
#   Smoke test used before the full run: --max-per-factory 25 --sentinel none --out <scratch dir>
```

## Time window, blocks, pinned snapshot

| Item | Value |
|---|---|
| Live run launch | 2026-09-30T21:53:55.034Z (engine pid 4747, launcher pid 4722) |
| Live run 'searcher ready' | 2026-09-30T22:03:50.413Z (log `time` 1790805830413); detected by launcher 22:03:51.69Z |
| Live run stop | scheduled 1200 s after detection (~22:23:51Z); exact value in `run-times.json` `stop_utc` |
| Live run first/last processed block | `run-times.json` → `blocks` (TBD) |
| Snapshot pinned block | **52008246** (head 52008249 at 22:04:05Z minus 3); timestamp/hash in `snapshot-meta.json` |
| Snapshot wall-clock | started 2026-09-30T22:04:05Z; end in `snapshot-meta.json` `finished_utc` (TBD) |

The live run's universe was built from its own reads at `latest` during 21:53:55–22:03:50Z (roughly blocks 52007950–52008240;
first ready-time block visible in the log is 52008242). The snapshot is a separate, later pass at one pinned block,
so the two pool sets are not identical.

### `searcher ready` line (live run, verbatim)

```
{"level":30,"time":1790805830413,"pid":4747,"hostname":"vm","tokens":33595,"pools":5234,"cycles":6422,"minDepthEth":0.001,"source":"logs","mode":"dry","contract":"0x00000000000000000000000000000000000a4BB0","codeOverride":true,"msg":"searcher ready"}
```

## Files and schemas

Hex is lowercase `0x…` in snapshot files. The engine's own outputs (`live-shallow.*`) keep the engine's checksummed
addresses. Big integers are base-10 strings. "derived" = computed deterministically from raw columns or by engine functions.

### Live run (step 3)

**`live-shallow.jsonl`** — as written by the engine (`bot/src/main.ts`), one JSON object per candidate the engine acted on
(top 6 per tick after the `--min-profit-usd 0.01` predicted-net filter, one per pool per tick). Plain JSONL (not gzipped) so that
`bot/src/research/analyze.ts` can read it directly. Rows: TBD.

| Field | Meaning |
|---|---|
| `t` | ISO UTC wall-clock time of the record |
| `block` | block number that triggered the tick |
| `fb` | flashblock index (always 0 with `--source logs`) |
| `route` | engine's route label `TOKENIN>TOKENOUT@DEX[/tier] ...` |
| `pools` | pool addresses per hop (V4: first 20 bytes of the poolId) |
| `token` | symbol of the start/profit token |
| `amountIn` | input amount, token units (decimal string) |
| `predictedProfitUsd`, `gasUsd`, `netUsd` | engine's off-chain prediction (USD via engine price map; gas = estimate × gas price + L1 fee) |
| `gapBps` | engine's price-gap measure for the route |
| `sim` | `eth_call` simulation of the executor with code override: `{profitUsd, gas, ms}` on success or `{error, ms}` on revert |
| `simNetUsd` | simulated profit minus gas at simulated gasUsed (present when `sim` succeeded) |
| `blacklisted` | true when the route/token was parked after 3 reverts |

**`live-shallow.log`** — engine stdout/stderr, pino JSON lines (`time` = epoch ms, `msg` = message). Messages include
`factory enumerated`, `pool discovery complete`, `geckoterminal request failed`, `uniswap v4 pools discovered`, `searcher ready`,
`heartbeat` (every 10 ticks: `ticks, gross, net, simulated, simOk, …, block, syncMs, searchMs, totalMs, pools`), the per-candidate
records (same fields as the JSONL), `shutting down` (final stats on SIGINT). Lines: TBD.

**`run-times.json`** — written by `collect/run_live_shallow.py` at the end: `status` (DONE/FAILED), `reason`, `launch_utc`, `ready_utc`
(from the log line's `time`), `stop_utc` (time the SIGINT was sent), `attempts[]` (per attempt: `min_depth_eth`, `cmd`, `engine_pid`,
`head_at_launch`/`head_at_ready`/`head_at_stop` = eth_blockNumber read by the launcher, `ready_detected_utc`, `searcher_ready_line_verbatim`,
`searcher_ready_counts`, `stop_signals`, `exit_code`, `seconds_ready_to_stop`, `log_tail` on failure), `retry_reason` if the 0.01 retry
was used, `blocks` (`first/last_heartbeat_block`, `first/last_block_in_log_records`, `first/last_block_in_jsonl`, `jsonl_candidate_rows`,
`heartbeat_count`), `shutdown_stats_line` (the engine's final `shutting down` object).

`collect/run_live_shallow.state.json` is the launcher's checkpoint (same structure, updated during the run).

### Snapshot (step 1)

Sequence reproduced with the engine modules imported unchanged (`collect/snapshot.ts`), in main.ts order:
`enumerateUniverse(maxPerFactory 6000)` → tokens = cfg.tokens ∪ enumerated tokens → `discoverV4Pools(tokens, pages=2)` →
`loadStaticMetadata` → `syncPools(force, blockNumber=PIN)` → `pruneEmpty` → `buildEthPrices(kept)` → `poolDepthEth` /
`filterByDepth(kept, prices, 0.1)`.
**Pinning:** the script wraps the engine's own viem client in a Proxy that adds `blockNumber = PIN` to every `multicall` and
`readContract` that does not name a block (the engine's enumerate/discover/static-metadata reads default to `latest`), and returns PIN from
`getBlockNumber`. All on-chain reads of the sequence are therefore at block 52008246. The same Proxy retries transient RPC errors
(HTTP 429/5xx, timeouts, rate-limit messages) up to 7 attempts with exponential backoff (2 s → 60 s) before the engine's own
chunk bisection sees the error, and records every per-call failure. `globalThis.fetch` is wrapped only to keep the raw GeckoTerminal
responses. GeckoTerminal data is live at request time (not pinnable).

Extra reads not in the engine sequence (all at PIN): `balanceOf(pool)` for each non-V4 pool's two tokens; `balanceOf(PoolManager)` for
each V4 currency and `eth_getBalance(PoolManager)`; `name()` and `totalSupply()` for every token; a re-read of `getReserves` /
`slot0`+`liquidity` (V4: StateView `getSlot0`+`getLiquidity`) for every pruned pool.

**`pools-prefilter.csv.gz`** — every pool after `pruneEmpty` (the set the depth filter sees). One row per pool. Rows: TBD.
**`pools-pruned-empty.csv.gz`** — every pool removed by `pruneEmpty`; same columns plus `recheck_*`. Rows: TBD.

| Column | Meaning |
|---|---|
| `pool_address` | pool address; for V4 the engine's synthetic address = first 20 bytes of the poolId |
| `v4_pool_id` | V4 poolId (bytes32), empty otherwise |
| `dex` | engine DEX name (UniswapV3, AerodromeCL, AerodromeCL2, AerodromeCL3, PancakeV3, SushiV3, Aerodrome, UniswapV2, SushiV2, PancakeV2, BaseSwap, UniswapV4) |
| `kind` | engine kind: univ2, aero-v2, univ3, aero-cl, pancake-v3 (V4 pools are `univ3` in the engine) |
| `is_v4` | true/false |
| `token0`, `token1` | engine token addresses (V4 native ETH is mapped by the engine to WETH) |
| `sym0`, `sym1`, `dec0`, `dec1` | engine symbol (sliced to 12 chars by enumerate.ts) and decimals |
| `v4_currency0`, `v4_currency1`, `v4_fee_raw`, `v4_tick_spacing`, `v4_hooks` | raw V4 PoolKey from PositionManager.poolKeys (currency 0x000…0 = native ETH; fee 8388608 = dynamic-fee flag) |
| `v2_fee_bps` | V2-style fee: univ2 from chains.ts `feeBps`; aero-v2 from factory `getFee(pool, stable)` (Aerodrome units as the engine stores them) |
| `aero_stable` | aero-v2 stable flag (false for univ2) |
| `reserve0`, `reserve1` | V2 `getReserves` at PIN, raw token units |
| `cl_tier` | CL factory key: fee (univ3/pancake/V4) or tickSpacing (aero-cl) |
| `sqrt_price_x96`, `tick`, `liquidity` | CL slot0 / in-range liquidity at PIN (V4 via StateView) |
| `fee_pips` | CL fee in 1e-6 units as the engine holds it (aero-cl: `fee()` at PIN; V4: lpFee from getSlot0) |
| `tick_spacing` | CL tick spacing |
| `fee_by_dir_zero_for_one`, `fee_by_dir_one_for_zero` | V4 only: engine's effective fee per direction including protocol fee (pips) |
| `cl_word_range_min/max`, `cl_bitmap_words_fetched`, `cl_initialized_ticks_fetched` | tick-bitmap word window fetched by `syncPools(force)` (±3000 ticks + 1 word) and number of initialized ticks found in it |
| `state_block` | engine `pool.block` after sync (PIN when any state call succeeded, 0 otherwise) |
| `token0_balance_of_pool`, `token1_balance_of_pool`, `token*_balance_ok` | extra read: ERC-20 `balanceOf(pool)` at PIN (empty for V4) |
| `engine_price_eth_token0_derived`, `engine_price_eth_token1_derived` | derived: `buildEthPrices` value (ETH per whole token); empty = unpriced |
| `side_amt0_derived`, `side_amt1_derived` | derived: engine `sideAmounts` (human units; V2 real reserves, CL virtual reserves L/√P and L·√P) |
| `engine_depth_eth_derived` | derived: engine `poolDepthEth` |
| `passes_min_depth_0_1_derived` | derived: membership in engine `filterByDepth(kept, prices, 0.1)` (empty in the pruned file) |
| `recheck_reserves_ok`, `recheck_reserve0/1`, `recheck_slot0_ok`, `recheck_sqrt_price_x96`, `recheck_tick`, `recheck_liquidity_ok`, `recheck_liquidity` | pruned file only: independent re-read at PIN |

**`cl-ticks-prefilter.csv.gz`** — tick data exactly as fetched by `syncPools(force)` for CL pools in the prefilter set.
Columns: `pool_address`, `v4_pool_id`, `tick`, `liquidity_net` (signed, raw), `liquidity_gross` (raw). Rows: TBD.

**`prices.csv.gz`** — full engine price map. Columns: `token`, `symbol`, `decimals`, `engine_price_eth_derived` (ETH per whole token,
from `buildEthPrices` over the prefilter pools; anchor rule `MIN_ANCHOR_ETH` = 0.05), `is_weth`, `is_usdc`. Rows: TBD.

**`tokens.csv.gz`** — every token in the engine token list or in any snapshot pool. Columns: `token`, `symbol_engine`,
`decimals_engine`, `in_cfg_tokens`, `in_enumerated_tokens`, `name`, `name_ok`, `total_supply` (raw), `total_supply_ok`,
`n_prefilter_pools_derived`, `n_pruned_pools_derived`, `engine_price_eth_derived`. Rows: TBD.

**`enumerated-token-meta-calls.csv.gz`** — raw `decimals()`/`symbol()` results that `enumerateUniverse` requested for tokens of
factory-enumerated pools (tokens with `decimals_ok=false` are dropped by the engine). Columns: `token`, `decimals_ok`, `decimals`,
`symbol_ok`, `symbol`. Rows: TBD.

**`factory-enumeration.csv.gz`** — raw factory enumeration (`allPools(i)` / `allPairs(i)` for the newest `min(length, 6000)` indices of
each enumerable factory) with the `token0()`/`token1()` results. Columns: `factory`, `dex`, `index`, `pool_address`, `call_ok`, `token0`,
`token1`, `token0_ok`, `token1_ok`, `in_discovered_pools_derived` (the address is among the pools `discoverPools` found by resolving every
venue per pair). Factory lengths at PIN are in `collect/snapshot.log` (`factory enumerated` lines: `total`, `enumerated`). Rows: TBD.

**`v4-poolmanager-balances.csv.gz`** — extra read: `balanceOf(PoolManager)` at PIN for each V4 currency in the snapshot, plus a row for
token `0x000…0` = PoolManager native ETH balance (`eth_getBalance`). Columns: `holder`, `token`, `balance`, `balance_ok`.

**`geckoterminal-responses.jsonl.gz`** — every GeckoTerminal request made during the snapshot: `{t, url, status, body}` (body = raw JSON text;
`status` null + `error` on network failure). The engine retries a 429 once after 15 s and then skips that page.

**`snapshot-failed-calls.jsonl.gz`** — every individual multicall sub-call with status failure: `{stage, fn, address, args, err}`.
**`snapshot-rpc-errors.jsonl.gz`** — every RPC-level error seen by the retry wrapper: `{t, stage, what, attempt, err}`.

**`snapshot-meta.json`** — pinned block (number, timestamp, hash), head at start/end, per-stage timings and counts, `syncStats`,
`fn_stats` (calls/ok/fail per function name), `chunk_throws_after_retries`, `chunk_throws_by_stage`, `failed_calls_by_stage`, file list
with row counts and byte sizes.

### Collector code and logs (`collect/`)

`run_live_shallow.py` (launcher), `run_live_shallow.log`, `run_live_shallow.state.json`; `snapshot.ts`, `run_snapshot.sh`,
`run_snapshot.log`, `snapshot.log` (script progress lines + engine pino JSON lines).

## Coverage limits and gaps

1. **Transfer-behaviour probe (step 2) not collected.** No per-token transfer simulation data exists here;
   `.sentinels/TRANSFER_PROBE.FAILED` records this.
   → Attempt 2 (2026-10-01): see section "Transfer-behaviour probe (attempt 2, 2026-10-01)" at the end of this file. The only transfer-related signal in this directory is the engine's own
   simulation outcome per candidate (`sim.error` in `live-shallow.jsonl`, e.g. decoded `TransferFailed` reverts), which only covers routes
   the engine selected.
2. **V4 coverage is the engine's GeckoTerminal-listed set only** (network top pages 1-2 + page 1 per DEX listing; hooked pools with
   swap-permission bits or dynamic fee and pools outside the token universe are dropped by `discoverV4Pools`). The live run's log shows
   `listed 20, kept 10, hooked 2, outOfUniverse 8`; the snapshot's counts are in `collect/snapshot.log`. The full V4 pool list is in `../01-v4-pools`.
3. **Newest 6,000 per V2-style factory** (`--max-per-factory 6000`): e.g. UniswapV2 `allPairsLength` 3,063,708 at the snapshot's block, of
   which indices 3,057,708-3,063,707 were enumerated; Aerodrome V2 6,000 of 29,601; PancakeV2 6,000 of 15,243; BaseSwap 6,000 of 8,258;
   SushiV2 6,000 of 6,095. Slipstream factories were enumerated in full. V3-style pools (UniswapV3, PancakeV3, SushiV3) are only found by
   resolving every configured tier for token pairs revealed by the enumerated pools, not by factory enumeration.
4. **GeckoTerminal rate limiting.** The live run's startup logged `geckoterminal request failed` (HTTP 429) for the `aerodrome-base` listing
   page; per the engine's code that page was skipped. The snapshot's GT statuses are in `geckoterminal-responses.jsonl.gz`.
5. **Live run vs snapshot are different pool sets and times** (see Time window). The live run's depth filter was 0.001 ETH; pools with engine
   depth < 0.001 ETH and unpriced-both-sides pools (depth 0) were not in its search set.
6. **Tick data window**: CL tick data covers only the engine's fetched window (±3000 ticks around the current tick plus one bitmap word on
   each side); ticks outside it are not in `cl-ticks-prefilter.csv.gz`.
7. **Pruned-pool recheck** is a separate read at the same block, not the engine's own sync result.
8. **Engine RPC failures during the live run** (if any) appear only as `tick failed` / `gas refresh failed` lines in `live-shallow.log`;
   the engine does not record skipped blocks explicitly. Blocks with no heartbeat/candidate line are not listed individually.
9. **Concurrency**: another agent's engine run (V4 live test) and several collectors shared the same public endpoints during both runs.
10. Only Base was collected here; no other chains.


## Transfer-behaviour probe (attempt 2, 2026-10-01)

**Status: NOT COMPLETED.** `.sentinels/TRANSFER_PROBE.FAILED` was rewritten with this attempt's reason. No `transfer-probe.csv.gz`
or `probe-meta.json` exists. No RPC calls were made in this attempt.

What exists (directory `transfer-probe/`):

| File | Content |
|---|---|
| `transfer-probe/collect/select_holders.py` | holder selection script (offline, reads only the snapshot files in this directory) |
| `transfer-probe/collect/work/holders.csv.gz` | holder selection output, one row per token in `tokens.csv.gz` (33,597 rows + header) |

Holder selection method (deterministic, no RPC): for each token, among non-V4 rows of `pools-prefilter.csv.gz` and
`pools-pruned-empty.csv.gz` with `token*_balance_ok == true`, the pool with the largest `token*_balance_of_pool` (block 52008246);
tie-break lowest pool address. `kind` univ2/aero-v2 -> `v2`; univ3/aero-cl/pancake-v3 -> `cl`. Fallback to the V4 PoolManager
`0x498581ff718922c3f8e6a244956af099b2652b2b` from `v4-poolmanager-balances.csv.gz` only when no pool had a positive balance.
Command: `cd transfer-probe/collect && python3 select_holders.py`.

`holders.csv.gz` columns: `token`, `symbol` (tokens.csv `symbol_engine`), `decimals` (`decimals_engine`), `holder`, `holder_kind`
(v2|cl|v4_poolmanager, empty = none), `holder_dex`, `holder_balance_snapshot` (raw, base-10), `holder_source_file`,
`n_pools_with_balance_ok`, `n_pools_positive_balance` (counts of snapshot pool rows for that token).

Row counts by `holder_kind`: v2 24,700; cl 5,003; v4_poolmanager 0; none (no positive balance in any snapshot pool or the
PoolManager file) 3,894. Unique holder addresses: 29,478.

Not collected: the per-token eth_call transfer probe (step 2 of the task: probe contract, batcher, state-override calls at
block 52008246) and its outputs. The attempt stopped before the probe contract was written.
