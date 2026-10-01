# 01-v4-pools: Uniswap V4 pools on Base (raw material)

STATUS: V4INIT, V4RECENT and V4STATE are COMPLETE (sentinels DONE). HOOKLABELS (item 4 refresh: Blockscout metadata for all hooks
with >= 20 pools, launch-tx samples, rebuild of hooks.csv) is IN PROGRESS. See "Collector status" at the bottom.
UPDATE 2026-10-01 02:09Z: HOOKLABELS is COMPLETE (sentinel HOOKLABELS.DONE). The first run was OOM-killed at 22:07Z; it was re-run
after a memory fix. See section "HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)" at the end of this file.

This directory contains collected data only. It holds no analysis, rankings or conclusions. Columns marked "derived" are
deterministic, lossless decodings of the raw values.

- Chain: Base (chain id 8453), 2-second blocks.
- Uniswap V4 PoolManager: `0x498581ff718922c3f8e6a244956af099b2652b2b`. StateView: `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`.
  V4 PositionManager: `0x7c5f5a4bbd8fd63184577525326123b519429bdc`. Multicall3: `0xca11bde05977b3631167028862be2a173976ca11`.
  Addresses as listed in Uniswap docs, saved in `hook-docs/text/raw.githubusercontent.com_Uniswap_docs_main_content_protocols_v4_deployments.mdx.txt`.
- Collection date: 2026-09-30 UTC (collectors started 20:59Z and 21:03Z).

## Which question lines each file serves (mapping only)

The question lines are quoted from the user's text. The short keys are used in the table below.

- Q-V4GAP: "Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet."
- Q-SMALL: "Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit." (V4 part only)
- Q-LAUNCH: "V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base."
- Q-MEASURE: "The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test."

| File(s) | Q-V4GAP | Q-SMALL | Q-LAUNCH | Q-MEASURE |
|---|---|---|---|---|
| `initialize-part-NNNN.csv.gz` + `initialize-parts.json` (every V4 pool ever created) | x | x | x | x |
| `v4-swap-part-NNNN.csv.gz`, `v4-modify-liquidity-part-NNNN.csv.gz`, `v4-donate-part-NNNN.csv.gz` + `recent-parts.json` (24 h of activity) | x | x | x | x |
| `v4-initialize-7d-part-NNNN.csv.gz` (Initialize events of the last 7 days, same schema as the full set) | x | | x | x |
| `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz`, `token-metadata.csv.gz`, `state-index.json` | x | x | x | x |
| `hooks.csv`, `hook-labels-long.csv`, `hook-pool-counts-all.csv.gz`, `hook-docs/*` (hook and launchpad identification) | x | x | x | x |
| `timestamps-check.csv` (block to time formula check) | x | | x | x |

Nothing here covers the other question lines (older V2 pairs, other chains, BSC ordering, chain-wide studies, the RSR trade).

## Block and time conventions

- Base block timestamp: `timestamp = 1686789347 + 2 * block_number` (UTC seconds). The genesis timestamp 1686789347 was read
  from block 0 (hash `0xf712aa9241cc24369b143cf6dce85f0902a9731e70d66818a3a5845b296c73dd`). The formula was checked against
  `eth_getBlockByNumber` on 14 blocks from 0 to 52006302 (`timestamps-check.csv`, all `equal=1`). No per-row timestamps are stored.
- PoolManager deployment block: 25,350,988 (2025-01-21T20:28:43Z). Method: binary search of `eth_getCode(PoolManager, block)` on
  base.drpc.org, cross-checked on base-mainnet.public.blastapi.io. There is no code at 25,350,987 and code at 25,350,988 on both endpoints.
  The deployment tx is `0x25f482fbd94cdea11b018732e455b8e9a940b933cabde3c0c5dd63ea65e85349`, sent from `0x2179a60856e37dfeaaca0ab043b931fe224b27b6`
  to the CREATE2 deployer `0x4e59b44847b379578588920ca78fbf26c0b4956c` (`collect/find_deploy_block.log`).
- Pinned blocks:
  - V4INIT (all Initialize events): blocks 25,350,988 to **52,006,302** (the head of mainnet.base.org at 2026-09-30T20:59:12Z).
    UTC range: 2025-01-21T20:28:43Z to 2026-09-30T20:59:11Z. Stored in `collect/state/v4init-pin.json`.
  - V4RECENT / V4STATE: pinned block **P = 52,006,432** (head 52,006,442 minus 10 at 2026-09-30T21:03:52Z; `collect/state/v4recent-pin.json`).
    - Activity window: blocks 51,963,233 to 52,006,432 (43,200 blocks), 2026-09-29T21:03:33Z to 2026-09-30T21:03:31Z.
    - 7-day Initialize window: blocks 51,704,033 to 52,006,432 (302,400 blocks), from 2026-09-23T21:03:33Z.
    - State snapshot block: 52,006,432.

## Event topics (topic0 = keccak256 of the signature; computed with `cast keccak` and checked against real logs)

| Event (PoolManager) | topic0 | indexed topics | data words |
|---|---|---|---|
| `Initialize(bytes32 id, address currency0, address currency1, uint24 fee, int24 tickSpacing, address hooks, uint160 sqrtPriceX96, int24 tick)` | `0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438` | id, currency0, currency1 | fee, tickSpacing, hooks, sqrtPriceX96, tick |
| `Swap(bytes32 id, address sender, int128 amount0, int128 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick, uint24 fee)` | `0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f` | id, sender | amount0, amount1, sqrtPriceX96, liquidity, tick, fee |
| `ModifyLiquidity(bytes32 id, address sender, int24 tickLower, int24 tickUpper, int256 liquidityDelta, bytes32 salt)` | `0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec` | id, sender | tickLower, tickUpper, liquidityDelta, salt |
| `Donate(bytes32 id, address sender, uint256 amount0, uint256 amount1)` | `0x29ef05caaff9404b7cb6d1c0e9bbae9eaa7ab2541feba1a9c4248594c08156cb` | id, sender | amount0, amount1 |

Checks applied to every decoded log: topic0 and data length match; `removed == false`; the block is inside the requested range;
and for Initialize, `pool_id == keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks))`, which is the v4-core PoolIdLibrary.
One Initialize log was also decoded with `cast decode-abi` and matched the Python decoder.

## File schemas

General conventions: gzip-compressed CSV with a header row. Addresses and hashes are lowercase 0x-hex. Integers are base-10
strings, signed where the Solidity type is signed. All token amounts are raw base units (no decimals applied). Rows are sorted by
(block_number, log_index). Each part is at most about 85 MB compressed. Parts rotate only at chunk boundaries, so each part covers
a contiguous block range, listed in its index JSON together with its row count and sha256.

### `initialize-part-NNNN.csv.gz` (V4INIT) and `v4-initialize-7d-part-NNNN.csv.gz` (V4RECENT), same columns
| column | meaning |
|---|---|
| block_number | block of the Initialize log (raw) |
| tx_hash | transaction hash (raw) |
| tx_index | transaction index in block (raw) |
| log_index | log index in block (raw) |
| pool_id | PoolId = topic1 (raw) |
| currency0, currency1 | PoolKey currencies = topic2, topic3; `0x000…000` = native ETH (raw) |
| fee_raw | PoolKey fee, uint24 (raw). `8388608` (= 0x800000) marks a dynamic-fee pool; other values are static LP fees in hundredths of a bip (1e-6) |
| tick_spacing | int24 (raw) |
| hooks | hook contract address, `0x000…000` = no hook (raw) |
| sqrt_price_x96 | initial sqrtPriceX96, uint160 (raw) |
| tick | initial tick, int24 (raw) |
| dynamic_fee | derived: `1` if fee_raw == 8388608 else `0` |
| hf_before_initialize … hf_after_remove_liquidity_returns_delta | derived: 14 hook permission flags = bits of the low 14 bits of the `hooks` address, per Uniswap v4-core `src/libraries/Hooks.sol` (saved verbatim: `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_Hooks.sol.gz`). Bit order: before_initialize=bit13, after_initialize=12, before_add_liquidity=11, after_add_liquidity=10, before_remove_liquidity=9, after_remove_liquidity=8, before_swap=7, after_swap=6, before_donate=5, after_donate=4, before_swap_returns_delta=3, after_swap_returns_delta=2, after_add_liquidity_returns_delta=1, after_remove_liquidity_returns_delta=0. Cross-check: flags of hook `0xb476…3044` equal the `flags` object of its Uniswap hooklist entry. |

`initialize-parts.json`: dataset, pin, block_from, block_to, total_rows, columns, and parts[] (file, rows, block_from, block_to, bytes, sha256).

### `v4-swap-part-NNNN.csv.gz`
block_number, tx_hash, tx_index, log_index, pool_id (topic1), sender (topic2), amount0 (int128), amount1 (int128), sqrt_price_x96 (uint160, after the swap),
liquidity (uint128, in range after the swap), tick (int24, after the swap), fee (uint24, the LP fee applied, in 1e-6 units). All raw.
Source references for sign semantics (not re-derived here): the IPoolManager natspec says "amount0 The delta of the currency0
balance of the pool". PoolManager.sol emits `Swap(id, msg.sender, delta.amount0(), delta.amount1(), ...)`, where `delta` is the
BalanceDelta returned to the caller. Both files are saved verbatim in `hook-docs/raw/` and `hook-docs/text/`
(`..._v4-core_main_src_interfaces_IPoolManager.sol`, `..._v4-core_main_src_PoolManager.sol`).

### `v4-modify-liquidity-part-NNNN.csv.gz`
block_number, tx_hash, tx_index, log_index, pool_id, sender, tick_lower (int24), tick_upper (int24), liquidity_delta (int256), salt (bytes32 hex). All raw.

### `v4-donate-part-NNNN.csv.gz`
block_number, tx_hash, tx_index, log_index, pool_id, sender, amount0 (uint256), amount1 (uint256). All raw.

`recent-parts.json`: pin (windows), topics, rows per event type, columns, parts[] per type (file, rows, block_from, block_to, bytes, sha256).

### `state-snapshot.csv.gz` (V4STATE; one row per pool)
Pool set: every pool_id with at least one Swap, ModifyLiquidity or Donate in the activity window, plus every pool_id with an
Initialize in the 7-day window.
| column | meaning |
|---|---|
| pool_id | pool |
| active_24h | 1 if the pool has any Swap/ModifyLiquidity/Donate in the activity window |
| initialized_7d | 1 if the pool's Initialize is in the 7-day window |
| snapshot_block | 52006432 |
| slot0_ok | 1 if `StateView.getSlot0(poolId)` returned 4 words |
| sqrt_price_x96, tick, protocol_fee, lp_fee | derived: decoded return of getSlot0 at snapshot_block (lossless). protocol_fee is the raw uint24. v4-core ProtocolFeeLibrary (saved in hook-docs/raw/) defines `getZeroForOneFee = self & 0xfff` and `getOneForZeroFee = self >> 12`. lp_fee is in 1e-6 units |
| liquidity_ok, liquidity | derived: `StateView.getLiquidity(poolId)` at snapshot_block (uint128, in-range liquidity) |
Method: Multicall3.aggregate3 (allowFailure=true), 250 pools (500 calls) per eth_call, `blockTag = 52006432`. Endpoints tried in
random order: base-mainnet.public.blastapi.io, developer-access-mainnet.base.org, base.drpc.org, gateway.tenderly.co/public/base,
all of which served archive eth_call in probes. Failed items are retried as direct eth_call.
Note: StateView returns zeros (success) for a pool id that does not exist.

### `pool-keys-snapshot.csv.gz` (V4STATE; one row per pool in state-snapshot)
pool_id, currency0, currency1, fee_raw, tick_spacing, hooks, init_block, key_source. Values of key_source:
- `initialize_log_7d`: from the 7-day Initialize logs.
- `initialize_log_v4init`: from the full V4INIT Initialize data.
- `position_manager_poolKeys_at_snapshot`: `PositionManager.poolKeys(bytes25(poolId))` at the snapshot block. It is accepted only
  if keccak256(abi.encode(key)) == pool_id. init_block stays empty unless it is later found in V4INIT.
- `unresolved`: no key was found.

### `token-metadata.csv.gz` (V4STATE; one row per currency appearing in the snapshot pools)
address, is_native (1 only for `0x000…000` = native ETH, whose other columns are empty), then for each of symbol(), name(), decimals(), totalSupply():
`<fn>_ok` (1 = call returned success), `<fn>_call_mode` (`multicall`, or `multicall_retry` = re-run in a multicall of only the
failed items, or `direct` = single eth_call with gas 5,000,000), `<fn>_return_raw` (raw return data hex, empty on failure),
`<fn>_error` (error text for failures), and a derived decoded value: `symbol_decoded` / `name_decoded` (ABI string, or bytes32 string
if the return is exactly 32 bytes; UTF-8 with replacement; control characters and backslash escaped as `\xNN`), `decimals`
(uint from a 32-byte return), `total_supply` (uint256 base-10, raw units). All calls are made at block 52006432.
Note: a Multicall3 low-level call to an address without code returns success with empty return data (`_ok=1`, `_return_raw=0x`).

`state-index.json`: snapshot block, pool and token counts, keys resolved/unresolved, whether V4INIT data was used, endpoints.

### `hooks.csv` (one row per hook address; built by `collect/build_hooks_csv.py`)
Rows: every hook with at least 20 pools in the counted Initialize data, plus every hook in the data that has any label source, plus
`0x000…000` (no hook).
| column | meaning |
|---|---|
| hook_address | hook |
| pool_count_so_far | number of Initialize events with this hook in the data counted when the script ran (see count_source). A later agent recounts from the final data |
| count_block_range | contiguous block range(s) covered by the counted data |
| count_source | `v4init_final` (final parts) or `v4init_work_chunks_partial` |
| first_init_block_in_counted_data, last_init_block_in_counted_data | first and last Initialize block for this hook in the counted data |
| pool_count_7d, count_7d_block_range | the same count over the 7-day window (51704033-52006432) |
| label, label_source_url, label_evidence | the highest-precedence label. Fixed precedence: (1) the launchpad's own docs or repositories (Zora, Clanker, Flaunch, Doppler, Bunni); label = project name + Blockscout contract name, evidence = verbatim document line; (2) Zora on-chain ZoraHookRegistry event; (3) Uniswap hooklist entry (name + description verbatim); (4) third-party code lists (Uniswap routing-api allowlist, KyberSwap dex-lib, Uniswap docs); (5) Blockscout verified contract name |
| n_label_sources | number of label rows for this hook in hook-labels-long.csv |
| blockscout_name, blockscout_is_verified, blockscout_creator_address, blockscout_creation_tx | Blockscout `/api/v2/addresses/<hook>` fields (raw) |
| creation_tx_from, creation_tx_to | from / to of the creation tx (Blockscout `/api/v2/transactions/<tx>`) |
| uniswap_hooklist_name | `hook.name` from Uniswap/hooklist `hooks/base/<address>.json` |
| zora_registry_tag_version | tag:version from ZoraHookRegistered events for this hook |
| hf_* (14 columns) | derived hook permission flags, same definition as above |

### `hook-labels-long.csv`
hook_address, source_kind (`document` / `zora_onchain_registry` / `uniswap_hooklist` / `blockscout`), precedence (1-5 as above), label, source_url, evidence_verbatim.

### `hook-docs/`
| file | content |
|---|---|
| `raw/<slug>.gz` | verbatim HTTP bodies of fetched docs and source files (gzip) |
| `text/<slug>.txt` | text of the same, with url, fetch time and HTTP status in the header. HTML tags are stripped and each link target is appended after its anchor text as ` <href>` |
| `fetch-log.jsonl` | one line per fetch: url, fetched_utc, http_status, bytes, sha256, raw_file, text_file (appended; re-fetches add lines) |
| `doc-address-excerpts.csv.gz` | every line of every HTTP-200 text file that contains a 20-byte hex address: url, fetched_utc, http_status, line_no, address, line_verbatim, context_before_3_lines_verbatim |
| `blockscout/index.jsonl.gz` | one line per address queried on base.blockscout.com API v2: name, is_contract, is_verified, creator, creation tx, creation tx from/to/method/block/timestamp, contract name, compiler, file path, proxy type, implementations |
| `blockscout/<addr>.address.json.gz`, `<addr>.creation_tx.json.gz`, `<addr>.smart_contract.json.gz` | verbatim API responses with url and fetch time. smart_contract includes the verified source and ABI. Besides the hooks, this also holds address and smart-contract responses for every log emitter seen in the launch-tx samples (factories, tokens, lockers and proxy implementations). They were fetched by `launch_tx_samples.py` to resolve event names and are not listed in index.jsonl.gz |
| `uniswap-hooklist-base.jsonl.gz` | all 1,134 `hooks/base/*.json` entries of https://github.com/Uniswap/hooklist at commit `65ef4121419193a5aad9a493d2f4d9710d2f7653` (2026-09-30T16:30:30Z), verbatim JSON with raw URL |
| `zora-hook-registry-logs.jsonl.gz` | all 21 logs of ZoraHookRegistry `0x777777c4c14b133858c3982d41dbf02509fc18d7` (Blockscout getLogs, fromBlock 0 to latest, fetched 2026-09-30 about 21:22Z; count equal to RPC eth_getLogs at the same blocks) |
| `zora-hook-registry-events.csv` | derived: decoded ZoraHookRegistered / ZoraHookRemoved events: block_number, tx_hash, log_index, event, hook, tag, version. topic0 ZoraHookRegistered(address,string,string) = `0xcf4000d2717988c072e9ec433f61ecff44a8bf0ebc5275e6353893a1b268fc5b` |
| `launch-tx-samples-tx.csv.gz` | for each candidate hook, up to 3 sample Initialize txs (earliest, middle, latest in the local data): hook, sample_pool_id, block_number, tx_hash, tx_from, tx_to (the contract called, e.g. a launchpad factory), tx_selector (4 bytes), tx_value_wei, receipt_status, n_logs, hook_pools_in_local_data |
| `launch-tx-samples-logs.csv.gz` | every log emitted by those sample txs: hook, sample_pool_id, block_number, tx_hash, log_index, log_address (emitter), topic0, n_topics, topics (`;`-joined), data, event_resolved_derived (`ContractName:EventSig` if topic0 equals keccak256 of an event in the emitter's, or its proxy implementation's, Blockscout-verified ABI; empty otherwise). This records which factory or deployer contract is called per launch and which events and topics it emits |

Documents fetched (URL list in `collect/fetch_docs.py`, fetch results in `hook-docs/fetch-log.jsonl`): Uniswap v4-core `Hooks.sol`,
`PoolId.sol`, `LPFeeLibrary.sol`, `IPoolManager.sol`, `PoolManager.sol`, `ProtocolFeeLibrary.sol`, and v4-periphery `StateView.sol`; the Uniswap docs v4 deployments page (the docs.uniswap.org HTML returned
HTTP 429, so the GitHub source `Uniswap/docs content/protocols/v4/deployments.mdx` was fetched instead); the Uniswap routing-api
hooks allowlist and the Uniswap hooklist README; Zora docs (llms.txt, hook-registry, hook, factory, architecture,
liquidity-migration, creating-a-coin, coins changelog) and zora-protocol source files; Clanker docs (deployed-contracts,
core-contracts, token-deployments) plus clanker-devco DOCS, v4-contracts README and clanker-sdk `clankers.ts`; Flaunch (flaunch-gitbook
for-aggregators.md, flaunchgg-contracts README, flaunch-sdk `addresses.ts` at a pinned commit); Doppler docs (contract-addresses,
doppler-hooks); Bunni v2 README; KyberSwap dex-lib Flaunch and Clanker hook constants.

## Row counts and parts

| file | rows | block range | notes |
|---|---|---|---|
| `initialize-part-0001..0022.csv.gz` | 15,333,247 total (per-part rows, block ranges, bytes and sha256 in `initialize-parts.json`) | 25,350,988-52,006,302 | 13,328 chunks of 2,000 blocks, 0 missing. The 22 parts cover contiguous block ranges. Largest part: 85.5 MB |
| `v4-swap-part-0001.csv.gz` | 597,414 | 51,963,233-52,006,432 | 51.6 MB |
| `v4-modify-liquidity-part-0001.csv.gz` | 157,066 | 51,963,233-52,006,432 | |
| `v4-donate-part-0001.csv.gz` | 190 | 51,963,233-52,006,432 | |
| `v4-initialize-7d-part-0001.csv.gz` | 29,900 | 51,704,033-52,006,432 | |
| `state-snapshot.csv.gz` | 36,103 pools | block 52,006,432 | 12,117 rows with active_24h=1 and 29,900 with initialized_7d=1 (a pool can have both). slot0_ok=1 and liquidity_ok=1 on all rows |
| `pool-keys-snapshot.csv.gz` | 36,103 | | key_source: 29,900 initialize_log_7d, 6,203 initialize_log_v4init, 0 unresolved |
| `token-metadata.csv.gz` | 27,317 (27,316 ERC-20 addresses + 1 native row) | block 52,006,432 | all 4 calls returned success via the first multicall for all 27,316 addresses |
| `timestamps-check.csv` | 14 | 0-52,006,302 | |
| `hooks.csv` | 1,198 at 22:00Z (rebuilt by the HOOKLABELS pipeline) | counts over 25,350,988-52,006,302 (count_source=v4init_final) and 7d window | |
| `hook-labels-long.csv` | 1,363 at 22:00Z (rebuilt by HOOKLABELS) | | |
| `hook-pool-counts-all.csv.gz` | 74,887 | 25,350,988-52,006,302 | derived count of Initialize rows per hook address in the final V4INIT parts (sum = 15,333,247); columns hook_address, pool_count, first_init_block, last_init_block, count_block_range. Made by `collect/write_hook_pool_counts.py` after V4INIT.DONE |
| `hook-docs/doc-address-excerpts.csv.gz` | 1,766 | | from 37 fetched documents (36 HTTP 200, 1 HTTP 429) |
| `hook-docs/uniswap-hooklist-base.jsonl.gz` | 1,134 | | |
| `hook-docs/zora-hook-registry-events.csv` | 16 (21 raw logs) | | |
| `hook-docs/blockscout/index.jsonl.gz` | 79 addresses at 21:5xZ; HOOKLABELS adds 134 (hooks with >= 20 pools in the final data not yet queried) | | |

Update 2026-10-01: the hooks.csv / hook-labels-long.csv / blockscout counts above are from before the HOOKLABELS re-run. Final counts
(hooks.csv 1,198; hook-labels-long.csv 1,388; index.jsonl.gz 213; launch-tx-samples 639 tx rows and 18,869 log rows) are in the
section "HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)" at the end of this file.

Consistency check: blocks 51,704,033-52,006,302 are fetched independently by V4INIT (mainnet.base.org / Tenderly / developer-access,
2,000-block chunks) and by V4RECENT (publicnode / developer-access / Tenderly, 2,000-block chunks aligned differently). Both give
29,893 Initialize rows, and the two row sets are identical.

## Reproduce

```
cd /home/user/dapparb/research-material/01-v4-pools/collect
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
python3 find_deploy_block.py                 # PoolManager deployment block (binary search eth_getCode)
python3 v4init_collector.py --smoke 37000000 37001999   # optional: compare endpoints on one range
setsid nohup python3 -u v4init_collector.py > v4init.log 2>&1 < /dev/null &      # V4INIT (resumable)
python3 verify_timestamps.py                 # needs state/v4init-pin.json
python3 v4recent_collector.py --smoke        # optional
setsid nohup python3 -u v4recent_collector.py > v4recent.log 2>&1 < /dev/null &  # V4RECENT + V4STATE (resumable)
python3 hook_counts.py > /tmp/hc.json        # per-hook counts in the Initialize data available now (JSON to stdout)
python3 write_hook_pool_counts.py           # -> ../hook-pool-counts-all.csv.gz (after V4INIT.DONE)
python3 hook_blockscout.py <addresses_file>  # Blockscout metadata for hook addresses (one per line)
python3 fetch_docs.py                        # launchpad / Uniswap docs + address excerpts
python3 uniswap_hooklist.py <scratch_clone_dir>
python3 zora_hook_registry.py
./hooks_pipeline.sh                          # hook_blockscout (candidates-2) + launch_tx_samples (candidates-all) + build_hooks_csv
```
To re-pin to a new head, delete `collect/state/*-pin.json` and `collect/work/` (the old pins are kept in this manifest).
Resumability: V4INIT and V4RECENT write one checkpoint file per completed chunk (`collect/work/v4init/c_<from>_<to>.csv.gz`, and
`collect/work/v4recent/{act,init}_<from>_<to>.csv.gz`, no header), and a rerun skips existing chunks. V4STATE checkpoints are
`collect/state/v4state-{slot0,keys,meta}.json`. The work/ files are intermediate and duplicate the final parts. They can be deleted
after the DONE sentinels exist.

Collector internals:
- JSON-RPC client with backoff on HTTP 429/5xx.
- eth_getLogs with a per-endpoint max range. Ranges are bisected on range or size errors, and any response with at least
  5,000 logs is re-fetched as two halves (a guard against silent provider caps).
- Work queue across endpoints. A failed chunk is requeued; after 12 (V4INIT) or 10 (V4RECENT) failures it is recorded as a gap and
  retried in later rounds (up to 6 or 5). Unrecoverable chunks are written to `collect/state/v4init-gaps.json` or
  `v4recent-gaps.json`, and a `.FAILED` sentinel is written. The DONE sentinel is written only after every chunk exists, parts
  are assembled, and part row counts are re-read and verified.

Endpoints used:
- V4INIT eth_getLogs: mainnet.base.org (2,000-block ranges, 2 in flight), gateway.tenderly.co/public/base (1,000, 2 in flight),
  developer-access-mainnet.base.org (2,000, 1 in flight).
- V4RECENT eth_getLogs: base-rpc.publicnode.com (newest chunks until its first archive-depth refusal), developer-access-mainnet.base.org,
  gateway.tenderly.co/public/base.
- Smoke test (`--smoke 37000000 37001999`): mainnet.base.org, Tenderly and developer-access returned identical rows (2,755). The
  V4RECENT smoke test (250 blocks near head) gave identical rows (3,556) on publicnode, developer-access and Tenderly.

## Coverage limits and gaps

- **base.drpc.org not used for getLogs.** On 2026-09-30 about 20:55Z it answered eth_getLogs only for ranges of 10 blocks or less
  ("You can make eth_getLogs requests with up to a 10 block range" / "ranges over 10000 blocks are not supported on free plan").
  It was used only for eth_getCode (deployment block) and as one of the archive eth_call endpoints for V4STATE.
- **base-rpc.publicnode.com** refuses getLogs more than about 10,000 blocks behind head and eth_call more than about 128 blocks behind
  head ("Archive requests require a personal token", HTTP 403). It served only the newest part of the activity window.
- **V4INIT run 1 was restarted.** It ran 20:59:12Z to 21:11:40Z with the same pin, and a drpc worker plus a worker-exit bug were
  fixed. Completed chunk files were kept (resume) and in-flight chunks were refetched. Log: `collect/v4init.run1.log`. V4RECENT was
  restarted in the same way (`collect/v4recent.run1.log`). No data from the first runs was dropped: each chunk file is complete or absent.
- **Pinned heads.** Initialize events after block 52,006,302 are not in `initialize-part-*`. Those up to 52,006,432 are in `v4-initialize-7d-*`.
- **Launch activity is not covered at block level.** The 24 h activity window is one day (2026-09-29T21:03Z to 2026-09-30T21:03Z).
  Earlier Swap/ModifyLiquidity/Donate history was not collected. Pending or mempool transactions and priority fees paid by swaps were not collected.
- **State snapshot scope.** The snapshot covers only pools active in the 24 h window or initialized in the 7-day window, at one
  block. Tick-level liquidity (tick bitmap / ticks) was not collected. Hook contract internal state (fees set by dynamic-fee hooks,
  anti-snipe windows) was not collected, except through the verified sources saved in hook-docs/blockscout/*.smart_contract.json.gz.
- **Token metadata** covers only currencies of the snapshot pools, not every currency in the full Initialize set. Transfer
  restrictions or taxes of tokens were not probed.
- **Hook labels.**
  - Blockscout metadata was fetched only for the candidate lists in `collect/state/`:
    - `hooks-candidates-1.txt` (79): hooks with at least 10 pools in the partial V4INIT data at about 21:05Z (blocks
      25,350,988-34,044,987), plus hooks with at least 5 pools in the 7-day window.
    - `hooks-candidates-2.txt` (134): hooks with at least 20 pools in the final V4INIT data that were not in list 1.
    - `hooks-candidates-all.txt` (213) is the union used for launch-tx samples.
    Hooks with fewer pools are in hooks.csv only if another label source names them. Some hooks are unverified or have no
    creator recorded on Blockscout. Per-hook counts for every hook address in the complete V4INIT data are in `hook-pool-counts-all.csv.gz`
    (74,887 rows including address(0)).
  - Launch-tx samples are at most 3 txs per hook (earliest, middle, latest Initialize). They record which contract each sampled
    launch tx called and which events it emitted. They are not a full census of factory events.
  - The Uniswap hooklist is a third-party-maintained registry (entries by hook teams / Uniswap); it is recorded as is.
  - Doc excerpts are raw lines. An address on a docs page may refer to another chain (context lines kept).
  - Labels in `hooks.csv` follow the fixed precedence above. No manual reclassification was done.
- **docs.uniswap.org** returned HTTP 429. The GitHub source of the same page was saved instead.
- **flaunch-sdk** `main/src/addresses.ts` returned 404. The file at commit `bef27f90b946a63fe3c215a409b487ad38b1c685` was saved instead.

## Collector status

| name | sentinel | log | status at 2026-09-30 ~21:56Z |
|---|---|---|---|
| V4INIT | `/home/user/dapparb/research-material/.sentinels/V4INIT.DONE` | `collect/v4init.log` (and `collect/v4init.run1.log`) | DONE 21:44:30Z, 15,333,247 rows, 22 parts |
| V4RECENT | `.sentinels/V4RECENT.DONE` | `collect/v4recent.log` (and `collect/v4recent.run1.log`) | DONE 21:12:21Z |
| V4STATE | `.sentinels/V4STATE.DONE` | `collect/v4recent.log` | DONE 21:46:25Z |
| HOOKLABELS (item 4 refresh) | `.sentinels/HOOKLABELS.DONE` / `.FAILED` | `collect/hooks_pipeline.log`, `collect/hook_blockscout.log`, `collect/launch_tx_samples.log`, `collect/build_hooks_csv.log` | RUNNING (detached `collect/hooks_pipeline.sh`). When it finishes, `hooks.csv`, `hook-labels-long.csv`, `hook-docs/blockscout/*` and `hook-docs/launch-tx-samples-*.csv.gz` are final; the counts in the table above for those files are then outdated. The next agent re-counts them. |

Update 2026-10-01: the RUNNING status above is outdated. `launch_tx_samples.py` was OOM-killed at 22:07Z and
`.sentinels/HOOKLABELS.FAILED` was written. It was fixed and re-run on 2026-10-01 01:18-02:09Z; the sentinel is now
`HOOKLABELS.DONE`. See section "HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)" at the end of this file.

Files in this directory NOT produced by the collectors described here: `initialize-compact/` (with its own `compact-index.json`),
`collect/compact_initialize.py`, `collect/compact_initialize.log`, `collect/expand_initialize.py`. They appeared at about 21:46-21:57Z,
written by another agent (a compact re-encoding of `initialize-part-*`; according to its log, the pool_id of every row was
recomputed with 0 mismatches). They are not described or maintained by this manifest.

Stable file layout for downstream readers: `initialize-parts.json` lists the V4INIT parts (`initialize-part-NNNN.csv.gz`, NNNN = 0001..0022).
`recent-parts.json` lists the V4RECENT parts, and `state-index.json` lists the V4STATE files.

## HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)

Sentinel: `.sentinels/HOOKLABELS.DONE` (written 2026-10-01T02:09:44Z after the manual checks below; `HOOKLABELS.FAILED` deleted).
Logs: `collect/hooks_pipeline.log`, `collect/launch_tx_samples.log` (lines of the killed run are kept above the `====` separators),
`collect/build_hooks_csv.log`, `collect/verify_launch_tx_selection.log`.

**What failed.** Step 1 of `collect/hooks_pipeline.sh` (`hook_blockscout.py` on `state/hooks-candidates-2.txt`) finished at
2026-09-30 22:01:19Z (`hook-docs/blockscout/index.jsonl.gz`: 213 addresses, all HTTP 200). Step 2 `launch_tx_samples.py` was killed
(SIGKILL, "Killed" in `hooks_pipeline.log`) at about 22:09Z at 6.5 GB RSS, in its Blockscout ABI phase. It had logged
`hooks 213 samples 639` and `txs 639 logs 18869 distinct emitters 1374` and had written no output table. The kill left a truncated
`hook-docs/blockscout/0x111111125421ca6dc452d289314280a0f8842a65.smart_contract.json.gz.tmp` (gzip: unexpected end of file).
Step 3 (`build_hooks_csv.py`) did not run.

**Cause.** The sample selection kept one Python tuple (block_number, log_index, tx_hash, pool_id) for every Initialize row whose hook
is a candidate, plus a set of all their pool-id strings. That is 15,033,116 rows; one hook alone has 8,170,323. Both were
module-level variables, so they stayed in memory until the process exited, at roughly 400 bytes per row.

**Fix** (`collect/launch_tx_samples.py`; the killed version is kept as `collect/launch_tx_samples.oom-version.py.txt`). The sampling
rule, the input files, the output files and their columns are unchanged. Per hook the script still picks the earliest, the middle
(index n//2) and the latest row in (block_number, log_index) order. Before picking, it de-duplicates by pool_id and keeps the first
occurrence. The inputs are still the V4INIT parts listed in `initialize-parts.json`, then `collect/work/v4recent/init_*.csv.gz`.
The selection now streams the inputs three times:
1. Pass 1 stores one 8-byte sort key per row (block_number*2^24 + log_index) in a per-hook `array('q')`. A 2^31-bit bitmap
   (256 MB) is indexed by 31 bits of the pool_id. When a row's bit is already set, the row is recorded as a possible duplicate.
2. Pass 2 is an exact check on full pool_id strings, done only for the possible duplicates. Each occurrence after the first is
   removed from the arrays.
3. Each per-hook array is sorted. All 213 were already in order, and a tie on the key aborts the run. The script then picks the
   keys and reads back their rows (tx_hash, pool_id).

Other changes do not alter values:
- The V4RECENT chunk list is read in sorted file-name order instead of `os.listdir` order. This only decides which copy of an
  identical duplicate row is met first.
- Checkpoints:
  - `collect/state/launch-tx-samples-selection.json` holds the 639 picked rows and the input file list with sizes.
  - `collect/work/launch_tx_cache.jsonl` is an intermediate cache: one line per tx hash with from, to, selector, value, receipt
    status and logs.
- A null RPC result counts as an error and moves on to the fallback endpoint.
- The output tables are written to `.tmp` and then renamed.
- Peak RSS is logged after each phase.

The run used `ulimit -v 3000000`. **Peak RSS of the full run was 424 MB** (ru_maxrss).

**Commands** (in `collect/`, with `REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt`):
```
setsid nohup ./hooks_pipeline_resume.sh &     # runs steps 2 and 3 only (step 1 had completed and was not re-run):
#   python3 -u launch_tx_samples.py state/hooks-candidates-all.txt >> launch_tx_samples.log
#   python3 -u build_hooks_csv.py > build_hooks_csv.log
python3 -u launch_tx_samples.py state/hooks-candidates-all.txt >> launch_tx_samples.log   # 02:08:53Z re-run from checkpoints (see below)
python3 -u verify_launch_tx_selection.py state/hooks-candidates-all.txt > verify_launch_tx_selection.log
```
The resume script does not write `HOOKLABELS.DONE`. It rewrites `HOOKLABELS.FAILED` if a step fails.

**Timeline (UTC, 2026-10-01).**
- Selection: 01:18:24 to 01:20:30.
- Tx and receipt fetch: until 01:24:18. 611 txs were fetched in this run. 15 more had been fetched at 01:17 by a smoke test with
  the same code and were reused from the cache.
- Blockscout ABI phase: until 02:07:01.
- `build_hooks_csv.py`: 02:07:01 to 02:08:11.
- 8 Blockscout responses (5 address, 3 smart_contract, fetched 01:30 to 02:05) were saved with `http_status` -1 (all retries
  failed). The script was re-run from its checkpoints at 02:08:53 with no RPC calls. It re-fetched those 8 (all HTTP 200) and
  rewrote both launch-tx tables at 02:09:00 (tx table 639 rows, logs table 18,869 rows, as before).

**Endpoints.**
- Tx and receipt: `https://gateway.tenderly.co/public/base` first, then `https://mainnet.base.org`. Which endpoint served each tx is
  not recorded.
- Event ABIs: `https://base.blockscout.com/api/v2`.
- No new block pin. The samples come from the Initialize data pinned at 52,006,302 (V4INIT) and 52,006,432 (V4RECENT).

**Checks done by hand.**
- Smoke test on 5 hooks (5, 5, 25, 274 and 631,597 pools). The fixed selection equals the output of the killed version's selection
  code run on the same 5 hooks (15 samples). The full run's tx and log rows for these hooks equal the smoke-test rows.
- Independent selection check with `collect/verify_launch_tx_selection.py`. It uses no bitmap and no sort. Per hook,
  n = the V4INIT count from `state/hook-counts-final.json` plus the V4RECENT rows after block 52,006,302. It takes the 0th, (n//2)-th
  and (n-1)-th row in stream order. Result: 639 of 639 samples equal, 0 mismatches.
- The 12 samples of `0xc8d077444625eb300a427a6dfb2b1dbf9b159040`, `0x9ea932730a7787000042e34390b8e435dd839040`,
  `0xbb7784a4d481184283ed89619a3e3ed143e1adc0` and `0x0469a4bd3724dc86c9542f4694c976da13c450c0` were re-fetched from
  base-mainnet.public.blastapi.io. These fields all match: tx from, to, selector and block; receipt status; number of logs; every log
  address and data. The log at the sampled log_index is emitted by the PoolManager, and its topic1 equals sample_pool_id.
- No `*.tmp` file is left in `hook-docs/`. The stray `.tmp` was deleted, and the AggregationRouterV6 smart_contract response for
  `0x111111125421ca6dc452d289314280a0f8842a65` was re-fetched (2026-10-01T01:24:19Z, HTTP 200). Every `hook-docs/blockscout/*.json.gz`
  passes `gzip -t` and parses.

**Row counts.**

| file | rows | notes |
|---|---|---|
| `hook-docs/launch-tx-samples-tx.csv.gz` | 639 | 213 hooks x 3 samples; 639 distinct sample_pool_id; 626 distinct tx_hash (a tx hash can appear in more than one row); blocks 25,477,714-52,006,386; receipt_status 0x1 on all rows |
| `hook-docs/launch-tx-samples-logs.csv.gz` | 18,869 | equals the sum of n_logs; 1,374 distinct log_address; 14,279 rows with a non-empty event_resolved_derived |
| `hooks.csv` | 1,198 | rebuilt 02:08:11Z (count_source v4init_final, count_block_range 25,350,988-52,006,302); replaces the 22:00Z build |
| `hook-labels-long.csv` | 1,388 | rebuilt 02:08:11Z; replaces the 22:00Z build (1,363) |
| `hook-docs/blockscout/index.jsonl.gz` | 213 | all http_status 200; not changed by the re-run |
| `hook-docs/blockscout/<addr>.*.json.gz` | 2,932 | address 1,859 (1,858 HTTP 200, 1 http_status -1, see below); creation_tx 150; smart_contract 923. 1,549 fetched on 2026-10-01, 1,383 on 2026-09-30 |
| `collect/state/launch-tx-samples-selection.json` | 639 samples | checkpoint, plus selection stats |
| `collect/work/launch_tx_cache.jsonl` | 626 | intermediate cache, one line per tx hash |

**Selection stats** (descriptive):
- 15,033,116 input rows have a candidate hook: 15,016,221 from V4INIT and 16,895 from the V4RECENT chunks.
- The bitmap flagged 69,023 rows as possible duplicates.
- 16,891 rows were dropped as pool_id duplicates. These are V4RECENT rows at or below block 52,006,302, which are the same events
  as in V4INIT.
- 4 rows (4 hooks) after block 52,006,302 come only from V4RECENT.

**Coverage limits.**
- At most 3 samples per hook, and only for the 213 hooks in `state/hooks-candidates-all.txt`. This is not a census of
  factory or launch transactions.
- `hook_pools_in_local_data` counts V4INIT and V4RECENT rows up to block 52,006,432.
- `event_resolved_derived` is filled only when the emitter, or its proxy implementation, was verified on Blockscout at fetch time.
  Blockscout responses were fetched at different times: 2026-09-30 about 21:2x-22:09Z and 2026-10-01 01:17-02:09Z.
- `hook-docs/blockscout/0x7facd8b3a38e873bc338b65f5b7375a242c7e7fc.address.json.gz` (fetched 2026-09-30T21:40:20Z, http_status -1)
  is left over from an earlier run. The current launch-tx tables and candidate lists do not reference it. It was not re-fetched.
