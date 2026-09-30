# 03-v2-older-pairs: V2-style pools the section 2.6 run did not enumerate, and 24 h of V2-style activity on Base

Raw material only. This file maps the data, says how it was produced, and lists what is missing. It contains no findings,
rankings or conclusions. Every value below that is not a copy of an RPC response is marked **derived**, and each derivation
is deterministic and lossless (a decoded ABI field, a flag computed from an index, or a sum or count of raw event fields).

<!-- AUTO-STATUS-BEGIN -->

**Status: COMPLETE** (filled by `collect/finalize.py` at 2026-09-30T22:24:35Z).

| Component sentinel | State |
|---|---|
| `.sentinels/V2OLD_SNAPSHOT` | DONE |
| `.sentinels/V2OLD_CENSUS` | DONE |
| `.sentinels/V2OLD_TOKENS` | DONE |

Rows in gaps.csv (unrecoverable batches/ranges): 0. Files over 90 MB: none.

| File | Data rows (excl. header) | Bytes | sha256 |
|---|---:|---:|---|
| `activity-pool-hour.csv.gz` | 30921 | 1270678 | `0d5245559cf5e02e…` |
| `buckets.csv` | 24 | 5391 | `cea2da263c7c7424…` |
| `census-chunks.csv` | 87 | 9377 | `32c149c18327c2b8…` |
| `census-crosscheck.csv` | 3 | 309 | `ca0069d5d0985c7e…` |
| `census-logs-part-0001.csv.gz` | 304359 | 29589834 | `6485a7a9fa71a982…` |
| `census-meta.json` |  | 1339 | `e7455c7de4088612…` |
| `emitters.csv.gz` | 4385 | 375763 | `5b4200c6c01c10f8…` |
| `factories.csv` | 8 | 2514 | `5724ffc98b437801…` |
| `factory-length-history.csv` | 840 | 81802 | `757aa59cceec45fa…` |
| `getreserves-abi.csv` | 5 | 2642 | `b31d0d24588d5c2b…` |
| `pools-part-0001.csv.gz` | 125197 | 9340614 | `887bbcf42c613eca…` |
| `price-reference-weth-pools.csv.gz` | 7640 | 583851 | `313adafa3a4f51e0…` |
| `snapshot-meta.json` |  | 962 | `320e66f35a648f1d…` |
| `tokens-meta.json` |  | 287 | `782192e8dc99dafe…` |
| `tokens.csv.gz` | 111983 | 4793479 | `d78f917a5f2af35d…` |
| `topics.csv` | 4 | 2196 | `0326e19622995abc…` |
| `uniswapv2-sample-indices.csv.gz` | 66000 | 222474 | `0eb7a12b2bd99a51…` |

Snapshot rows by factory/sample group: `{"Aerodrome/all_indices": 29601, "BaseSwap/all_indices": 8258, "PancakeV2/all_indices": 15243, "SushiV2/all_indices": 6095, "UniswapV2/newest_6000_at_snapshot": 6000, "UniswapV2/random_sample_older": 60000}`

Census: window 51965201-52008400, log rows 304359 by event `{"sync_uint112": 82788, "swap_univ2": 84002, "sync_uint256": 71714, "swap_aero_v2": 65855}`, activity rows 30921, distinct emitters 4385, missing chunks [].

Tokens: 111983 tokens with metadata; WETH-route set 6862 tokens, 247032 lookups, 7640 pool rows.

Full per-file list with complete sha256: `file-index.csv`.

<!-- AUTO-STATUS-END -->

## Collectors and sentinels

| Collector | Script | Log | Sentinel (in `/home/user/dapparb/research-material/.sentinels/`) |
|---|---|---|---|
| Factory counts + pool snapshot | `collect/snapshot.py` | `collect/snapshot.log` | `V2OLD_SNAPSHOT.DONE` / `.FAILED` |
| 24 h V2-style event census | `collect/census.py` | `collect/census.log` | `V2OLD_CENSUS.DONE` / `.FAILED` |
| Token metadata + WETH-route reference | `collect/tokens.py` (waits for the two above, then runs `finalize.py`) | `collect/tokens.log` | `V2OLD_TOKENS.DONE` / `.FAILED` |
| Overall | `collect/finalize.py` | (stdout in `collect/tokens.log`) | `V2OLD.DONE` / `.FAILED` (DONE only if all three components are DONE, every file reads back and none is over 90 MB) |
| Declared getReserves ABI (one-off) | `collect/abi_shapes.py` | `collect/abi_shapes.log` | none (small, finished) |

Shared code: `collect/rpclib.py` (JSON-RPC client with a per-endpoint in-flight cap, retries, a hand-written Multicall3
`aggregate3` encoder and decoder, lossless return-data decoders, and a resumable batch store).

## 1. Question lines this directory serves (mapping only)

Question lines are numbered in the order they appear in the user's text:

- Q1 "What is still unmeasured:" (heading)
- Q2 Uniswap V4 on Base: Clanker/Zora V4 pools with hooks, "I only had 20 V4 pools"
- Q3 "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens."
- Q4 "Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity … where most tokens that block or tax transfers sit."
- Q5 Other chains, live
- Q6 "Would the gaps change the answer?" (heading)
- Q7 V4 launches / most fought-over flow on Base / RSR trade
- Q8 BSC ordering through private block builders
- Q9 Chain-wide studies (Arbitrum ~$4,700/day; Base 4,365 bots, 21.4 M arbitrages, 28 % profitable)
- Q10 "So the search went far beyond selected pairs, but it did not cover everything." / full V4 coverage re-run

| File(s) | Serves |
|---|---|
| `factories.csv` | Q3 ("newest 6,000 of about 3 million": pair counts at the pinned block, at the §2.6 enumeration block and at the earlier v0 run's block; the index range each run enumerated), Q10 |
| `factory-length-history.csv` | Q3 (pair count of each factory every 500,000 blocks, so a pair index can be placed in time; "older") |
| `uniswapv2-sample-indices.csv.gz` | Q3 (exact index sample, seed, population) |
| `pools-part-0001.csv.gz` | Q3 (every not-enumerated pool of Aerodrome V2, PancakeV2, BaseSwap and SushiV2, plus a 60,000-index random sample of older Uniswap V2 pairs and the newest 6,000 for comparison: tokens, reserves, last-update time `block_timestamp_last`, LP supply), Q4 (reserves of the same pools; Aerodrome stable flag and fee), Q10 |
| `tokens.csv.gz` | Q3, Q4 (symbol, name, decimals and totalSupply of every token in the files above) |
| `price-reference-weth-pools.csv.gz` | Q3, Q4 (raw state of the token/WETH pools of every token that sits in a pool with neither a WETH nor a stablecoin side, so that those reserves can be expressed in ETH) |
| `census-logs-part-0001.csv.gz` | Q3, Q4 (which V2-style pools traded or synced in the 24 h up to the pinned block), Q9 (V2-style Sync/Swap events chain-wide on Base for 24 h, from any address; V2-style topics only), Q10 |
| `activity-pool-hour.csv.gz` | Same as the census logs, aggregated per pool, topic and hour (derived) |
| `emitters.csv.gz` | Q3, Q4, Q9 (identity of every address that emitted one of the four topics: factory(), token0, token1, reserves at the pinned block) |
| `buckets.csv` | Hour-bucket block and time boundaries for `activity-pool-hour.csv.gz` |
| `topics.csv`, `census-crosscheck.csv`, `census-chunks.csv`, `getreserves-abi.csv`, `*-meta.json`, `gaps.csv` (if present), `file-index.csv` | Method, verification and coverage metadata for the files above |
| none | Q2, Q7 (Uniswap V4: see `../01-v4-pools`), Q5, Q8 (other chains: `../06-other-chains-onchain`, `../07-other-chains-engine`), Q9 study figures (`../08-sources`), transfer-blocking/taxing behaviour in Q4 (not collected here; see Coverage limits) |

## 2. Sources and endpoints

All data is from Base mainnet (chain id 8453) through public JSON-RPC, requested with a browser-like User-Agent.

| Use | Endpoint | Notes |
|---|---|---|
| `eth_call` at the pinned block (Multicall3 `aggregate3`) and archive `eth_call` at older blocks | `https://base-mainnet.public.blastapi.io` (primary, ≤ 2 in flight per collector) | Every snapshot and token call in this run was served here. The `endpoint_stats` in `*-meta.json` show that `base.drpc.org`, the fallback, was not needed. |
| same, fallback | `https://base.drpc.org` (1 in flight) | |
| `eth_getLogs`, topic-only filter (no address) | `https://gateway.tenderly.co/public/base` (≤ 1,000 blocks per request; 500 used; 2 in flight) | This endpoint served all 87 chunks (`census-chunks.csv`). |
| same, fallback and cross-check | `https://mainnet.base.org` (≤ 2,000 blocks; 1 in flight, ≥ 1 s spacing) | Used for the 3-chunk cross-check. |
| same, last-resort fallback | `https://base.drpc.org` (only 10 blocks for address-less filters, probed 22:10Z) | Not used |
| not used for logs | `https://base-rpc.publicnode.com` | Rejects address-less `eth_getLogs` with "Please specify an address in your request", probed 22:10Z |
| Block headers for bucket bounds | tenderly, then mainnet.base.org, then drpc | |
| Verified ABIs | `https://base.blockscout.com/api/v2/smart-contracts/<addr>` and `/api/v2/addresses/<addr>` | `getreserves-abi.csv` only |
| Section 2.6 enumeration counts | `research-material/00-prior-runs/engine-runs/dry-all.log.gz` (§2.6 run) and `dry-all-v0.log.gz` (v0 run), lines `factory enumerated` | Copied into `factories.csv` (`s26_*`, `v0_*` columns) |

Contracts: factories exactly as in `bot/src/config/chains.ts` (BASE):
Aerodrome V2 PoolFactory `0x420dd381b31aef6683db6b902084cb0ffece40da`, UniswapV2 `0x8909dc15e40173ff4699343b6eb8132c65e18ec6`,
SushiV2 `0x71524b4f93c58fcbf659783284e38825f0622859`, PancakeV2 `0x02a84c1b3bbd7401a5f7fa98a384ebc70bb5749e`,
BaseSwap `0xfda619b6d20975be80a10332cd39b9a4b0faa8bb`. The Slipstream factories AerodromeCL `0x5e7bb104…809a`, CL3 `0xf8f2eb49…61ef`
and CL2 `0xade65c38…716a` are listed in `factories.csv` for reference only. The V3-style factories are used only for the WETH-route lookups.
Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`, WETH `0x4200000000000000000000000000000000000006`.

## 3. Time window, blocks, pinned snapshot

| Item | Value |
|---|---|
| Pinned snapshot block (all `eth_call` data: factories, pools, emitters, tokens, WETH-route) | **52008400**, hash `0x116f70d59e1c4a45476bc1e787fedab83c0e83f8896e9006610f979f3ef206d5`, timestamp 1790806147 = 2026-09-30T22:09:07Z |
| Census window (`eth_getLogs`) | blocks **51965201 – 52008400** inclusive (43,200 blocks), 2026-09-29T22:09:09Z – 2026-09-30T22:09:07Z |
| Hour buckets | 24 buckets of 1,800 blocks: bucket k = blocks [51965201 + 1800k, 51965201 + 1800k + 1799] (`buckets.csv` has header hashes and timestamps) |
| Base block time | block n has timestamp 1686789347 + 2n. Every census log's `blockTimestamp` agrees with this (`census-meta.json` `log_timestamp_formula_mismatches` = 0). `factories.csv` uses it to turn the §2.6 log times into blocks. |
| Section 2.6 enumeration | log times 16:55:48–16:55:56Z → blocks 51999000–51999004. The v0 run's times 16:37:12–16:37:20Z → blocks 51998442–51998446 |
| Collection run | snapshot 22:15–22:17Z, census 22:17–22:18Z, tokens 22:21–22:24Z (UTC, 2026-09-30) |

## 4. Reproduce

```bash
cd /home/user/dapparb/research-material/03-v2-older-pairs/collect
# snapshot (resumable: state/*.jsonl hold finished batches; rerun the same command to resume)
setsid nohup python3 -u snapshot.py --pin 52008400 > snapshot.log 2>&1 < /dev/null &
# census (resumable: state/census/chunks/<a>_<b>.csv.gz per finished 500-block chunk)
setsid nohup python3 -u census.py --pin 52008400 > census.log 2>&1 < /dev/null &
# tokens + WETH-route (waits for both sentinels, then runs finalize.py)
setsid nohup python3 -u tokens.py > tokens.log 2>&1 < /dev/null &
# one-off: declared getReserves ABI per DEX
python3 abi_shapes.py > abi_shapes.log 2>&1
# only re-fill counts/sha256 in this manifest and the V2OLD sentinel
python3 finalize.py
```

Checkpoints: `collect/state/*.jsonl.gz`, `collect/state/tokens/*.jsonl.gz` and `collect/state/census/*.jsonl.gz` were gzipped after
all collectors finished. Each line is one finished batch `{"b": batch_id, "rows": [[status, returnData_hex, rpc_error], ...]}`,
and the calls are in the order the scripts build them. These are the undecoded Multicall3 results behind every decoded column.
`collect/state/census/chunks/<a>_<b>.csv.gz` are the per-chunk raw log rows (no header, columns as `census-logs-part-*`). To resume
or re-derive from them, gunzip the `.jsonl.gz` files in place first. Without them, the scripts fetch the same pinned block again.

Smoke tests used before the full runs (they write only to scratch, not here):
`snapshot.py --pin 52008400 --smoke 30 --out <scratch> --state <scratch>/state --sentinel none` (300 pools),
`census.py --pin 52008400 --window 3700 --out <scratch> --state <scratch>/state --sentinel none` (8 chunks, cross-check identical),
`tokens.py --out <scratch> --state <scratch>/state --limit 400 --sentinel none --no-wait --no-finalize`.
Requirements: python3 with `requests` and `eth_hash`/pycryptodome (only for the keccak cross-check in `topics.csv`), and
`/root/.foundry/bin/cast` for the second keccak computation. A different pinned block needs an archive `eth_call` endpoint.
`eth_getLogs` needs an endpoint that accepts address-less filters.
To rebuild the Uniswap V2 sample without Python's `random`, use `uniswapv2-sample-indices.csv.gz`.

## 5. Methods

### 5.1 snapshot.py

1. **Factory counts**: `allPoolsLength()` (Aerodrome, Slipstream) or `allPairsLength()` (V2 forks), read with `eth_call` at the
   pinned block. They are also read at the block matching each factory's `factory enumerated` log line of the §2.6 run and of
   the v0 run, and on a grid of every 500,000 blocks from 500,000 to the pinned block (`factory-length-history.csv`).
2. **Index selection** (column `sample_group`):
   - Aerodrome V2, PancakeV2, BaseSwap, SushiV2: `all_indices`, meaning every index in [0, N at the pinned block). This covers
     the indices §2.6 did not enumerate (below its range, and above it for pools created since), and also the §2.6 range itself.
     The derived column `index_vs_s26_range` tells them apart.
   - UniswapV2: `random_sample_older` is 60,000 indices drawn uniformly without replacement from [0, 3,057,605), where
     3,057,605 = 3,063,605 − 6,000 and 3,063,605 is the total the §2.6 run logged. The draw is Python 3.11
     `random.Random(20260930).sample(range(3057605), 60000)`, then sorted. `newest_6000_at_snapshot` is [3,057,708, 3,063,708)
     at the pinned block. It overlaps the §2.6 range [3,057,605, 3,063,605) and also holds the 103 pairs created after §2.6.
3. **Pair addresses**: `allPools(i)` / `allPairs(i)` at the pinned block, 1,000 calls per `aggregate3`.
4. **Pool fields** (100 pools per `aggregate3`): `token0()`, `token1()`, `getReserves()`, `totalSupply()` of the pool's LP
   token, and `stable()` for Aerodrome.
5. **Aerodrome fee**: PoolFactory `getFee(pool, stable)`, called with the pool's own `stable()` result.
6. Every call uses `aggregate3` with `allowFailure = true`. If a whole `aggregate3` reverts, runs out of gas or times out,
   the batch is split in half recursively down to single calls, so every sub-call ends with its own status. HTTP 429, 5xx and
   network errors are retried with exponential backoff and jitter, alternating blastapi and drpc. A batch that still fails goes to `gaps.csv`.

### 5.2 census.py

- Topic-only `eth_getLogs` (no address) with `topics: [[t1, t2, t3, t4]]` in 500-block chunks over the window. The four topic0 values:

  | event label | signature | topic0 |
  |---|---|---|
  | `sync_uint112` | `Sync(uint112,uint112)` (Uniswap V2 style) | `0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1` |
  | `sync_uint256` | `Sync(uint256,uint256)` (Aerodrome/Solidly style) | `0xcf2aa50876cdfbb541206f89af0ee78d44a2abf8d328e37fa4917f982149848a` |
  | `swap_univ2` | `Swap(address,uint256,uint256,uint256,uint256,address)` | `0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822` |
  | `swap_aero_v2` | `Swap(address,address,uint256,uint256,uint256,uint256)` | `0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b` |

  Each topic was computed twice, with `cast keccak "<signature>"` and with Python `eth_hash`. Both are in `topics.csv`, which
  also records a real example log per topic from a pool of the expected factory. For the Sync topics, the example's decoded
  (reserve0, reserve1) was compared with `getReserves()` at the end of that block. For the Swap topics, the check is the topic
  count and data length (`check_result`).
- Validation of every response: each log's block is inside the requested range, its topic0 is one of the four, `removed` is
  false, and no (block, logIndex) repeats. A range error, a size error or a response of 10,000 or more logs (a possible silent
  cap) makes the chunk split in half recursively. Transient errors are retried with backoff and rotated across
  tenderly and mainnet.base.org; drpc is used only for ranges of 10 blocks or fewer.
- Cross-check: the first, middle and last chunks were fetched again from `mainnet.base.org` and compared as sets of
  (block, tx hash, log index, address, topic0, data) (`census-crosscheck.csv`).
- Emitters: every distinct emitting address gets `factory()`, `token0()`, `token1()` and `getReserves()` at the pinned block,
  plus `stable()` for addresses that emitted a Solidly-style topic. All through `aggregate3` with allowFailure.

### 5.3 tokens.py

- Token set: every `token0`/`token1` with status ok in `pools-part-*.csv.gz` and `emitters.csv.gz`, plus WETH and the four
  stablecoins below. Calls: `symbol()`, `name()`, `decimals()`, `totalSupply()` at the pinned block.
- WETH-route set: every token of a pool (snapshot or emitter) whose two sides include neither WETH nor one of
  USDC `0x833589fc…2913`, USDbC `0xd9aaec86…b6ca`, DAI `0x50c57259…b0cb` or USDT `0xfde4c96c…bb2`, plus those four
  stablecoins. For each token, a lookup against WETH on every DEX factory in `bot/src/config/chains.ts`, 36 lookups per token:
  UniswapV2/SushiV2/PancakeV2/BaseSwap `getPair`; Aerodrome `getPool(t, WETH, false|true)`; UniswapV3/SushiV3
  `getPool(t, WETH, 100|500|3000|10000)`; PancakeV3 `getPool(t, WETH, 100|500|2500|10000)`; AerodromeCL/CL2/CL3
  `getPool(t, WETH, 1|10|50|100|200|2000)`. For each non-zero result: V2-style `token0()`, `getReserves()`; V3-style
  `token0()`, `slot0()`, `liquidity()`, `WETH.balanceOf(pool)`, `token.balanceOf(pool)`. Uniswap V4 pools are not looked up.
- Reference for method comparison only (not used by the collectors): the engine's depth filter is `poolDepthEth` in
  `bot/src/arb/depth.ts`, which takes the smaller of the two sides' ETH values using the anchored price map from
  `bot/src/arb/pricing.ts`. The §2.6 run used `--min-depth-eth 0.1`.

## 6. File schemas

General: gzip CSV with a header row, UTF-8, RFC 4180 quoting (the csv module). Addresses and hashes are lowercase 0x-hex.
Integers are base-10 strings. `*_status` values from the Multicall3 decoders:
`ok` (success, decoded); `ok_extra_bytes` (success, more bytes returned than decoded; decoded prefix given);
`empty` (success with 0 bytes returned, e.g. no code at the target); `revert` (the sub-call reverted; revert data is in `failures`);
`baddata` (success but not decodable as the expected type); `batch_error` (even a one-call `aggregate3` failed at RPC level);
`rpc_failed` (batch not collected, listed in `gaps.csv`); `zero_address` (index returned 0x0); `not_called…` (the call did not apply).
A `failures` column holds `fn=status:0x<returned data>[:rpc message]` entries separated by `|`, for every call that was not `ok`.

### factories.csv (one row per factory, 5 V2-style + 3 Slipstream)
`factory_name`, `dex_kind` (from chains.ts), `factory`, `v2_style`, `length_fn`, `snapshot_block`, `n_at_snapshot` (length at
the pinned block), `s26_log_time_utc` (time of the §2.6 `factory enumerated` line), `s26_block_at_log_time` (**derived** from
that time: (ts − 1686789347) / 2), `s26_total_logged` (the `total` in the §2.6 log), `n_onchain_at_s26_block` (length read on
chain at that block), `s26_enumerated_logged`, `s26_enum_index_start` / `s26_enum_index_end_excl` (**derived**: the newest-first
range [total − enumerated, total) that `bot/src/pools/enumerate.ts` reads), the same five `v0_*` columns for the earlier v0
run (16:37Z, dry-all-v0.log.gz), `docs_analysis_text_total` (the number quoted in docs/ANALYSIS.md §2.6, where there is one),
`n_growth_since_s26_derived` (= n_at_snapshot − s26_total_logged), `this_snapshot_index_selection` (text).

### factory-length-history.csv
`block`, `block_timestamp_formula` (**derived**, 1686789347 + 2·block), `factory_name`, `factory`, `length_fn`, `status`
(`empty` = no code yet at that block), `length`. Grid: 500,000, 1,000,000, …, 52,000,000, and 52,008,400.

### uniswapv2-sample-indices.csv.gz
`index`, `group` (`random_sample_older` | `newest_6000_at_snapshot`), `population_start`, `population_end_excl`, `seed`, `method`.

### pools-part-0001.csv.gz (one row per selected factory index)
`snapshot_block`; `factory_name`; `factory`; `dex_kind`; `index` (factory array index); `sample_group` (see 5.1);
`index_vs_s26_range` (**derived**: `below_s26_range` | `in_s26_range` | `above_s26_range`, relative to the §2.6 range in
factories.csv); `pair` + `pair_status`; `token0`, `token1` (+ status); `reserves_status`, `reserves_ret_bytes` (bytes returned
by `getReserves()`); `reserve0`, `reserve1`, `block_timestamp_last` (the three returned 32-byte words as integers, raw units:
token base units and unix seconds); `reserves_extra_hex` (bytes beyond 96, if any); `lp_total_supply` (+ status; pool LP
token `totalSupply()`); `stable` (+ status; Aerodrome only, `true`/`false`); `factory_fee` (+ status; Aerodrome only, raw
`getFee(pool, stable)` return value, in Aerodrome's fee units of 1/10,000); `failures`.
Declared `getReserves()` shapes (`getreserves-abi.csv`, Blockscout-verified ABIs): UniswapV2Pair, SushiSwap UniswapV2Pair,
PancakePair (PancakeV2) and PancakePair (BaseSwap) return `(uint112 _reserve0, uint112 _reserve1, uint32 _blockTimestampLast)`.
The Aerodrome Pool implementation `0xa4e46b4f…6d7` (pools are clones) returns
`(uint256 _reserve0, uint256 _reserve1, uint256 _blockTimestampLast)`. All are ABI-encoded as three 32-byte words (96 bytes).

### tokens.csv.gz (one row per token)
`token`, `snapshot_block`, `in_snapshot_pools` / `in_census_emitters` / `in_weth_route_set` (**derived** membership flags),
`symbol`, `symbol_encoding`, `symbol_raw`, `name`, `name_encoding`, `name_raw`, `decimals` (+ `decimals_status`), `total_supply`
(+ status; raw base units), `failures`. `*_encoding`: `string` (standard ABI string, valid printable UTF-8; `*_raw` empty),
`bytes32` (32-byte right-zero-padded text; `*_raw` holds the 32 bytes), `undecodable` (not an ABI string or bytes32 of printable UTF-8, e.g. text containing newlines or other control
characters; text empty, `*_raw` holds the full return data), or a call status (`revert`, `empty`, …) with any revert data in `*_raw`.

### price-reference-weth-pools.csv.gz (one row per non-zero lookup result, or per failed lookup)
`token`, `snapshot_block`, `venue`, `venue_kind`, `factory`, `lookup_param` (fee / tick spacing / Aerodrome stable flag;
empty for V2 `getPair`), `pool`, `lookup_status`, `pool_token0` (+ status; says which side WETH is on), `reserves_status`, `reserve0`,
`reserve1`, `block_timestamp_last` (V2-style only), `slot0_status`, `slot0_ret_bytes`, `sqrt_price_x96` (slot0 word 0),
`tick` (slot0 word 1 as signed int), `liquidity` (+ status), `weth_balance_of_pool` (+ status), `token_balance_of_pool`
(+ status) (V3-style only; raw base units), `failures`. A (token, venue, param) with no row means the factory returned the zero address.

### census-logs-part-0001.csv.gz (one row per log, sorted by block, log index)
`block_number`, `block_timestamp` (from the RPC's `blockTimestamp` field), `block_hash`, `tx_index`, `tx_hash`, `log_index`,
`address` (emitter), `event` (label from the table in 5.2), `topic0`–`topic3`, `n_topics`, `data` (raw hex), `decode_status`
(`ok` | `layout_mismatch`: topic count or data length differs from the expected layout, so the derived fields stay empty),
**derived** decoded fields: `d_sender`, `d_to` (Swap topics 1 and 2), `d_reserve0`, `d_reserve1` (Sync data words), `d_amount0_in`,
`d_amount1_in`, `d_amount0_out`, `d_amount1_out` (Swap data words, raw token base units).

### activity-pool-hour.csv.gz (**derived** from the census logs, one row per (pool, topic, hour bucket) with ≥ 1 log)
`pool_address`, `event`, `topic0`, `hour_bucket_index` (0–23), `hour_bucket_start_block`, `hour_bucket_end_block`, `count` (logs),
`distinct_tx_count`, `first_block`, `last_block`, `last_log_index`, `last_sync_reserve0` / `last_sync_reserve1` (Sync rows: the
decoded reserves of the last log in the bucket), `sum_amount0_in`, `sum_amount1_in`, `sum_amount0_out`, `sum_amount1_out`
(Swap rows: sums of the decoded amounts over the bucket, raw base units), `layout_mismatch_count`.

### emitters.csv.gz (one row per distinct emitting address in the census)
`address`, `snapshot_block`, `events_seen` (`;`-joined labels), `factory` (+ `factory_status`), `known_factory_name_derived`
(the name if `factory()` equals one of the five V2-style factories above, else empty), `token0`, `token1` (+ status),
`reserves_status`, `reserves_ret_bytes`, `reserve0`, `reserve1`, `block_timestamp_last`, `reserves_extra_hex`, `stable`
(+ status; called only for addresses that emitted `sync_uint256` or `swap_aero_v2`), `failures`.

### buckets.csv
`hour_bucket_index`, `start_block`, `end_block`, `start_timestamp`, `end_timestamp`, `start_utc`, `end_utc`, `start_block_hash`, `end_block_hash`.

### topics.csv
`event`, `signature`, `topic0`, `topic0_cast_keccak`, `topic0_python_keccak`, `example_block`, `example_tx`, `example_log_index`,
`example_emitter`, `emitter_factory_name_derived`, `check` (text), `check_result`, `rows_in_window`.

### census-chunks.csv / census-crosscheck.csv
Chunks: `chunk_start`, `chunk_end`, `log_rows`, `endpoints_used` (JSON: endpoint → logs), `fetch_secs`, `fetched_utc`, `status`.
Cross-check: `chunk_start`, `chunk_end`, `primary_rows`, `check_endpoint`, `check_rows`, `identical_log_sets`, `only_in_primary`, `only_in_check`, `error`.

### getreserves-abi.csv
`factory_name`, `example_pool`, `abi_source_address`, `abi_via`, `contract_name`, `compiler_version`, `getReserves_outputs_json`, `status`, `blockscout_url`.

### snapshot-meta.json, census-meta.json, tokens-meta.json, file-index.csv, gaps.csv
Run metadata (pinned block and hash, seeds, row counts by group, endpoint ok/error counters, start/finish times); per-file
rows, bytes and sha256 (written by finalize.py); unrecoverable batches or ranges (the file exists only if there was at least one).

## 7. Coverage limits and gaps

- **Uniswap V2 is sampled, not complete**: 60,000 of the 3,057,605 indices below the §2.6 range (about 1.96 %), plus the newest 6,000
  at the pinned block. The ~103 indices [3,057,605, 3,057,708) belong to the §2.6 range but fall in neither group, so they were not read.
  All other factories are complete at the pinned block.
- **One pinned block**: reserves, fees, LP supply, token metadata and WETH-route state are single reads at block 52008400. There is no
  time series apart from `block_timestamp_last` (the pool's last reserve update) and the 24 h census.
- **Census scope**: only the four V2-style topics above. Uniswap V3, Slipstream, PancakeV3 and Uniswap V4 events were not collected here
  (V4 is in `../01-v4-pools`). The window is 24 h (43,200 blocks); anything older shows only through `block_timestamp_last`. Topic-only
  filters also catch any contract that emits the same topic. `emitters.csv.gz` identifies them: 42 emitters' `factory()` reverted, and
  416 returned a factory that is not one of the five. Of the Aerodrome-style Swap logs, 31 have 1 topic and 192 data bytes, a different
  layout from the one decoded (`layout_mismatch`); their raw topics and data are kept.
- **Transfer behaviour** (whether a token blocks or taxes transfers, Q4) was **not** collected in this directory. Only ERC-20 metadata was
  read; no transfer or swap simulation was made. (`../04-shallow-pools` records a transfer probe as `TRANSFER_PROBE.FAILED`.)
- **Pricing**: no token prices or USD/ETH conversions are computed here. Pools with a WETH side can be valued from their own reserves. For
  stablecoin-side pools, the Aerodrome WETH/USDC pools are in `pools-part-0001.csv.gz` (for example vAMM `0xcdac0d6c…5c43`). Other pools
  need `price-reference-weth-pools.csv.gz`, which covers only direct token/WETH pools on the 11 configured factories: no multi-hop routes,
  no other DEXes, no Uniswap V4. `../04-shallow-pools/prices.csv.gz` holds the engine's own anchored price map at block 52008246, 154 blocks earlier.
- **Section 2.6 range reconstruction**: the §2.6 index ranges come from the run's log totals and the newest-first rule in
  `bot/src/pools/enumerate.ts`. The on-chain lengths at the matching blocks equal the logged totals (`factories.csv`). The exact block of
  each enumeration `eth_call` was not logged, so the block is derived from the log time (±1–2 blocks).
- **Endpoints**: every `eth_call` was served by blastapi and every log chunk by tenderly. Only three chunks were independently cross-checked
  against a second provider.
- **Not collected**: pair creation blocks or times (no `PairCreated` scan; `factory-length-history.csv` is the only index-to-time material),
  per-pool bytecode, and LP-holder or liquidity-lock data.
- Unrecoverable batches or ranges, if any, are in `gaps.csv`. The auto-status block above gives the count after the run.

## 8. Related material elsewhere in research-material/ (pointers only)

- `../00-prior-runs/engine-runs/dry-all.log.gz`, `dry-all-v0.log.gz`: source of the §2.6 enumeration counts.
- `../04-shallow-pools/`: pools under 0.1 ETH as seen by the engine (`factory-enumeration.csv.gz` there is the engine's own newest-6,000 enumeration).
- `../05-base-onchain/`: full-block census (all transactions and receipts of swap-bearing transactions) for 51995609 onward. It overlaps the last ~12,800 blocks of this census window.
