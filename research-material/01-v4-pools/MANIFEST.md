# 01-v4-pools: Uniswap V4 pools on Base (raw material)

STATUS: IN PROGRESS (see "Collector status" at the bottom; counts marked TBD are filled in when the sentinels exist)

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
| `hooks.csv`, `hook-labels-long.csv`, `hook-docs/*` (hook and launchpad identification) | x | x | x | x |
| `timestamps-check.csv` (block to time formula check) | x | | x | x |

Nothing here covers the other question lines (older V2 pairs, other chains, BSC ordering, chain-wide studies, the RSR trade).

## Block and time conventions

- Base block timestamp: `timestamp = 1686789347 + 2 * block_number` (UTC seconds). The genesis timestamp 1686789347 was read
  from block 0 (hash `0xf712aa9241cc24369b143cf6dce85f0902a9731e70d66818a3a5845b296c73dd`). The formula was checked against
  `eth_getBlockByNumber` on 15 blocks from 0 to 52006302 (`timestamps-check.csv`, all `equal=1`). No per-row timestamps are stored.
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
v4-core IPoolManager sign convention: amounts are from the swapper's side, negative = paid in by the swapper, positive = received
(the interface file is saved verbatim in hook-docs/raw/).

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
| sqrt_price_x96, tick, protocol_fee, lp_fee | derived: decoded return of getSlot0 at snapshot_block (lossless). protocol_fee is the raw uint24 (two 12-bit values packed as in v4-core: lower 12 bits zeroForOne, upper 12 bits oneForZero). lp_fee is in 1e-6 units |
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
| `blockscout/<addr>.address.json.gz`, `<addr>.creation_tx.json.gz`, `<addr>.smart_contract.json.gz` | verbatim API responses with url and fetch time. smart_contract includes the verified source and ABI |
| `uniswap-hooklist-base.jsonl.gz` | all 1,134 `hooks/base/*.json` entries of https://github.com/Uniswap/hooklist at commit `65ef4121419193a5aad9a493d2f4d9710d2f7653` (2026-09-30T16:30:30Z), verbatim JSON with raw URL |
| `zora-hook-registry-logs.jsonl.gz` | all 21 logs of ZoraHookRegistry `0x777777c4c14b133858c3982d41dbf02509fc18d7` (Blockscout getLogs, fromBlock 0 to latest, fetched 2026-09-30 about 21:22Z; count equal to RPC eth_getLogs at the same blocks) |
| `zora-hook-registry-events.csv` | derived: decoded ZoraHookRegistered / ZoraHookRemoved events: block_number, tx_hash, log_index, event, hook, tag, version. topic0 ZoraHookRegistered(address,string,string) = `0xcf4000d2717988c072e9ec433f61ecff44a8bf0ebc5275e6353893a1b268fc5b` |
| `launch-tx-samples-tx.csv.gz` | for each candidate hook, up to 3 sample Initialize txs (earliest, middle, latest in the local data): hook, sample_pool_id, block_number, tx_hash, tx_from, tx_to (the contract called, e.g. a launchpad factory), tx_selector (4 bytes), tx_value_wei, receipt_status, n_logs, hook_pools_in_local_data |
| `launch-tx-samples-logs.csv.gz` | every log emitted by those sample txs: hook, sample_pool_id, block_number, tx_hash, log_index, log_address (emitter), topic0, n_topics, topics (`;`-joined), data, event_resolved_derived (`ContractName:EventSig` if topic0 equals keccak256 of an event in the emitter's, or its proxy implementation's, Blockscout-verified ABI; empty otherwise). This records which factory or deployer contract is called per launch and which events and topics it emits |

Documents fetched (URL list in `collect/fetch_docs.py`, fetch results in `hook-docs/fetch-log.jsonl`): Uniswap v4-core `Hooks.sol`,
`PoolId.sol`, `LPFeeLibrary.sol`, `IPoolManager.sol`; the Uniswap docs v4 deployments page (the docs.uniswap.org HTML returned
HTTP 429, so the GitHub source `Uniswap/docs content/protocols/v4/deployments.mdx` was fetched instead); the Uniswap routing-api
hooks allowlist and the Uniswap hooklist README; Zora docs (llms.txt, hook-registry, hook, factory, architecture,
liquidity-migration, creating-a-coin, coins changelog) and zora-protocol source files; Clanker docs (deployed-contracts,
core-contracts, token-deployments) plus clanker-devco DOCS, v4-contracts README and clanker-sdk `clankers.ts`; Flaunch (flaunch-gitbook
for-aggregators.md, flaunchgg-contracts README, flaunch-sdk `addresses.ts` at a pinned commit); Doppler docs (contract-addresses,
doppler-hooks); Bunni v2 README; KyberSwap dex-lib Flaunch and Clanker hook constants.

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
python3 hook_counts.py > /tmp/hc.json        # per-hook counts in the Initialize data available now
python3 hook_blockscout.py <addresses_file>  # Blockscout metadata for hook addresses (one per line)
python3 fetch_docs.py                        # launchpad / Uniswap docs + address excerpts
python3 uniswap_hooklist.py <scratch_clone_dir>
python3 zora_hook_registry.py
python3 launch_tx_samples.py state/hooks-candidates-1.txt
python3 build_hooks_csv.py
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
  - Blockscout metadata was fetched only for the candidate list in `collect/state/hooks-candidates-*.txt` (hooks with at least 10
    pools in the partial V4INIT data at about 21:05Z, plus hooks with at least 5 pools in the 7-day window). Some hooks are unverified or have no creator recorded on Blockscout.
  - The Uniswap hooklist is a third-party-maintained registry (entries by hook teams / Uniswap); it is recorded as is.
  - Doc excerpts are raw lines. An address on a docs page may refer to another chain (context lines kept).
  - Labels in `hooks.csv` follow the fixed precedence above. No manual reclassification was done.
- **docs.uniswap.org** returned HTTP 429. The GitHub source of the same page was saved instead.
- **flaunch-sdk** `main/src/addresses.ts` returned 404. The file at commit `bef27f90b946a63fe3c215a409b487ad38b1c685` was saved instead.

## Collector status
(filled in below)
