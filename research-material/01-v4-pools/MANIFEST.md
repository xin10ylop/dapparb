# 01-v4-pools: Uniswap V4 pools on Base (raw material)

STATUS: COMPLETE WITH GAPS (checked 2026-10-01). All five collectors of this folder finished. Their sentinels in
`research-material/.sentinels/` are `V4INIT.DONE`, `V4RECENT.DONE`, `V4STATE.DONE`, `HOOKLABELS.DONE` and `V4WINDOW2.DONE`.
None of them has a `.FAILED` sentinel. The gaps are:
1. **Original Initialize files are local-only.** The 22 original V4INIT files `initialize-part-0001..0022.csv.gz` (1,821,644,422
   bytes) are git-ignored. The repository instead holds the compact copy `initialize-compact/`, and `collect/expand_initialize.py`
   rebuilds the original rows from it. 26 of the 27 columns are rebuilt offline. `tx_hash` is rebuilt only with
   `--rpc <Base RPC URL>`, at one `eth_getTransactionByBlockNumberAndIndex` call per row. See section "`initialize-compact/`".
2. **Wrong `bytes` and `sha256` in `initialize-compact/compact-index.json`.** The values are wrong for all 8 compact parts; the
   row counts are correct. The correct values are in "Verified inventory (2026-10-01)".
   (Corrected 2026-10-01, fixup: no longer a gap. The main session recomputed `bytes` and `sha256` of every part in
   `compact-index.json` on 2026-10-01 (commit 9c8a37c, 02:57:03Z) and fixed `collect/compact_initialize.py` to flush the gzip
   trailer before hashing. Re-checked at ~05:00Z: `bytes` and `sha256` in the index equal `stat` and `sha256sum` of all 8
   `initialize-compact/pools-part-*.csv.gz` files and the inventory rows. See "Fixup (2026-10-01): compact-index.json and
   tx-hash-recovery-check.json" at the end of this file.)
3. **`collect/state/` and `collect/work/` are local-only.** `collect/state/` holds the pins, the V4STATE checkpoints, the hook
   candidate lists and the launch-tx selection checkpoint. `collect/work/` holds the per-chunk checkpoint files and the tx cache.
   Notes R1-R9 in the inventory say how to rebuild each one.
4. **One failed fetch was kept.** `hook-docs/blockscout/0x7facd8b3a38e873bc338b65f5b7375a242c7e7fc.address.json.gz` holds a
   failed fetch (`http_status` -1) and was not re-fetched.
5. **Coverage limits of the collection itself**, all listed in "Coverage limits and gaps": a 24 h activity window, a snapshot
   pool set limited to active and recently initialized pools, pinned end blocks, and no mempool, priority-fee or
   transfer-tax data.

Correction 2026-10-01 (V4WINDOW2, about 04:00Z): the status line above said "All four collectors" and listed four sentinels.
A fifth collector, V4WINDOW2 (`collect/v4window2_collector.py`), was added afterwards; it covers blocks 52,006,433-52,017,160,
the span after the 24 h activity window up to the end of the Base census. Item 5 ("a 24 h activity window") therefore now reads:
a 24 h activity window (51,963,233-52,006,432) plus a second window (52,006,433-52,017,160). See section "V4WINDOW2 (2026-10-01):
PoolManager logs for blocks 52,006,433-52,017,160 and snapshot at block 52,017,008" at the end of this file.

Earlier status lines, kept for provenance:
- First version of this file: "V4INIT, V4RECENT and V4STATE are COMPLETE (sentinels DONE). HOOKLABELS (item 4 refresh:
  Blockscout metadata for all hooks with >= 20 pools, launch-tx samples, rebuild of hooks.csv) is IN PROGRESS."
- UPDATE 2026-10-01 02:09Z: HOOKLABELS is COMPLETE (sentinel HOOKLABELS.DONE). The first run was OOM-killed at 22:07Z; it was
  re-run after a memory fix. See section "HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)" at the end of
  this file.

This directory contains collected data only. It holds no analysis, rankings or conclusions. Columns marked "derived" are
deterministic, lossless decodings of the raw values.

- Chain: Base (chain id 8453), 2-second blocks.
- Uniswap V4 PoolManager: `0x498581ff718922c3f8e6a244956af099b2652b2b`. StateView: `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`.
  V4 PositionManager: `0x7c5f5a4bbd8fd63184577525326123b519429bdc`. Multicall3: `0xca11bde05977b3631167028862be2a173976ca11`.
  These addresses are as listed in the Uniswap docs, saved in `hook-docs/text/raw.githubusercontent.com_Uniswap_docs_main_content_protocols_v4_deployments.mdx.txt`.
- Collection date: 2026-09-30 UTC (collectors started 20:59Z and 21:03Z). The HOOKLABELS re-run took place on 2026-10-01 from
  01:18Z to 02:09Z. The compact copy `initialize-compact/` was written on 2026-09-30 from 21:46Z to 21:57Z.

## Question lines served

This is a mapping only. The numbers are the line numbers of the eight research question lines. The text of the lines this
folder serves is quoted verbatim below the table.

| line | files in this folder |
|---|---|
| 1 | `initialize-compact/pools-part-0001..0008.csv.gz`, `initialize-compact/hooks.csv`, `initialize-compact/compact-index.json`, `initialize-compact/tx-hash-recovery-check.json`, `collect/expand_initialize.py`, `initialize-parts.json` (and the local-only `initialize-part-0001..0022.csv.gz`), `v4-initialize-7d-part-0001.csv.gz`, `v4-swap-part-0001.csv.gz`, `v4-modify-liquidity-part-0001.csv.gz`, `v4-donate-part-0001.csv.gz`, `recent-parts.json`, `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz`, `token-metadata.csv.gz`, `state-index.json`, `hooks.csv`, `hook-labels-long.csv`, `hook-pool-counts-all.csv.gz`, `hook-docs/` (all files), `timestamps-check.csv` |
| 3 (V4 pools only) | `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz`, `token-metadata.csv.gz`, `state-index.json`, `v4-swap-part-0001.csv.gz`, `v4-modify-liquidity-part-0001.csv.gz`, `v4-donate-part-0001.csv.gz`, `recent-parts.json`, `initialize-compact/` (all files) with `collect/expand_initialize.py`, `initialize-parts.json` (and the local-only `initialize-part-0001..0022.csv.gz`), `hooks.csv`, `hook-labels-long.csv`, `hook-pool-counts-all.csv.gz`, `hook-docs/` (all files) |
| 5 | `v4-initialize-7d-part-0001.csv.gz`, `v4-swap-part-0001.csv.gz`, `v4-modify-liquidity-part-0001.csv.gz`, `v4-donate-part-0001.csv.gz`, `recent-parts.json`, `initialize-compact/` (all files) with `collect/expand_initialize.py`, `initialize-parts.json` (and the local-only `initialize-part-0001..0022.csv.gz`), `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz`, `token-metadata.csv.gz`, `state-index.json`, `hooks.csv`, `hook-labels-long.csv`, `hook-pool-counts-all.csv.gz`, `hook-docs/launch-tx-samples-tx.csv.gz`, `hook-docs/launch-tx-samples-logs.csv.gz`, `hook-docs/` (other files), `timestamps-check.csv` |
| 8 | `initialize-compact/` (all files) with `collect/expand_initialize.py`, `initialize-parts.json` (and the local-only `initialize-part-0001..0022.csv.gz`), `collect/v4init_collector.py`, `collect/find_deploy_block.py`, `collect/find_deploy_block.log`, `v4-initialize-7d-part-0001.csv.gz`, `v4-swap-part-0001.csv.gz`, `v4-modify-liquidity-part-0001.csv.gz`, `v4-donate-part-0001.csv.gz`, `recent-parts.json`, `collect/v4recent_collector.py`, `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz`, `token-metadata.csv.gz`, `state-index.json`, `hooks.csv`, `hook-labels-long.csv`, `hook-pool-counts-all.csv.gz`, `hook-docs/` (all files), `timestamps-check.csv` |
| 2, 4, 6, 7 | none |

Additions 2026-10-01 (V4WINDOW2), one row per new file. Each file serves the lines its V4RECENT/V4STATE counterpart serves in
the table above (counterpart in brackets); nothing in V4WINDOW2 serves lines 2, 4, 6 or 7.

| new file | lines | counterpart in the table above |
|---|---|---|
| `v4-window2-swap-part-0001.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `v4-swap-part-0001.csv.gz` |
| `v4-window2-modify-liquidity-part-0001.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `v4-modify-liquidity-part-0001.csv.gz` |
| `v4-window2-donate-part-0001.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `v4-donate-part-0001.csv.gz` |
| `v4-window2-initialize-part-0001.csv.gz` | 1, 5, 8 | `v4-initialize-7d-part-0001.csv.gz` |
| `v4-window2-parts.json` | 1, 3 (V4 pools only), 5, 8 | `recent-parts.json` |
| `v4-window2-state-snapshot.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `state-snapshot.csv.gz` |
| `v4-window2-pool-keys.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `pool-keys-snapshot.csv.gz` |
| `v4-window2-token-metadata.csv.gz` | 1, 3 (V4 pools only), 5, 8 | `token-metadata.csv.gz` |
| `v4-window2-state-index.json` | 1, 3 (V4 pools only), 5, 8 | `state-index.json` |
| `collect/v4window2_collector.py` | 8 | `collect/v4recent_collector.py` |
| `collect/v4window2.log` | 8 | (collector log) |
| `collect/smoke_v4window2.log` | 8 | (smoke-test log) |
| `collect/v4window2_consistency.py` | 8 | (consistency checks, no counterpart) |
| `collect/v4window2_consistency.log` | 8 | (consistency checks, no counterpart) |

Question lines served (verbatim):
- 1: 'Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet.'
- 3: 'Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit.'
- 5: 'V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee.'
- 8: 'So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test.'

Correction 2026-10-01: this section replaces the earlier "Which question lines each file serves (mapping only)" table, which
used the short keys Q-V4GAP (line 1), Q-SMALL (line 3), Q-LAUNCH (line 5) and Q-MEASURE (line 8). Every file-to-line
assignment of that table is kept, and `v4-initialize-7d-part-0001.csv.gz` and `timestamps-check.csv` are still not mapped to
line 3. There are two additions:
- the references to `initialize-part-NNNN.csv.gz` now also point to the committed `initialize-compact/` and `collect/expand_initialize.py`;
- `collect/v4init_collector.py`, `collect/v4recent_collector.py` and `collect/find_deploy_block.py` / `.log` were added for line 8.

The earlier text also said: "Nothing here covers the other question lines (older V2 pairs, other chains, BSC ordering,
chain-wide studies, the RSR trade)."

## Block and time conventions

- Base block timestamp: `timestamp = 1686789347 + 2 * block_number` (UTC seconds). The genesis timestamp 1686789347 was read
  from block 0 (hash `0xf712aa9241cc24369b143cf6dce85f0902a9731e70d66818a3a5845b296c73dd`). The formula was checked against
  `eth_getBlockByNumber` on 14 blocks from 0 to 52006302 (`timestamps-check.csv`, all `equal=1`). No per-row timestamps are stored.
- PoolManager deployment block: 25,350,988 (2025-01-21T20:28:43Z). Method: binary search of `eth_getCode(PoolManager, block)` on
  base.drpc.org, cross-checked on base-mainnet.public.blastapi.io. Both endpoints return no code at 25,350,987 and code at 25,350,988.
  The deployment tx is `0x25f482fbd94cdea11b018732e455b8e9a940b933cabde3c0c5dd63ea65e85349`, sent from `0x2179a60856e37dfeaaca0ab043b931fe224b27b6`
  to the CREATE2 deployer `0x4e59b44847b379578588920ca78fbf26c0b4956c` (`collect/find_deploy_block.log`).
- Pinned blocks:
  - V4INIT (all Initialize events): blocks 25,350,988 to **52,006,302** (the head of mainnet.base.org at 2026-09-30T20:59:12Z).
    UTC range: 2025-01-21T20:28:43Z to 2026-09-30T20:59:11Z. Stored in `collect/state/v4init-pin.json` (local-only). An
    identical copy is the `pin` object of the committed `initialize-parts.json`.
  - V4RECENT / V4STATE: pinned block **P = 52,006,432** (head 52,006,442 minus 10 at 2026-09-30T21:03:52Z). Stored in
    `collect/state/v4recent-pin.json` (local-only). An identical copy is the `pin` object of the committed `recent-parts.json`.
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

Every decoded log passed these checks:
- topic0 and data length match the event;
- `removed == false`;
- the block is inside the requested range;
- for Initialize, `pool_id == keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks))`, which is the v4-core
  PoolIdLibrary.

One Initialize log was also decoded with `cast decode-abi`, and the result matched the Python decoder.

## File schemas

General conventions:
- Files are gzip-compressed CSV with a header row.
- Addresses and hashes are lowercase 0x-hex.
- Integers are base-10 strings, signed where the Solidity type is signed.
- All token amounts are raw base units, with no decimals applied.
- Rows are sorted by (block_number, log_index).
- Each `initialize-part-*` and `v4-*-part-*` file is at most about 85 MB compressed (largest: 85,509,481 bytes). The
  `initialize-compact/pools-part-*` files are at most 89,919,415 bytes.
- `initialize-part-*` and `v4-*-part-*` files rotate only at chunk boundaries, so each part covers a contiguous block range.
  Its index JSON lists that range together with the part's row count and sha256.
- `initialize-compact/pools-part-*` files rotate on size instead, checked every 20,000 rows. A block can therefore be split
  across two compact parts: block 42,970,695 is at the end of pools-part-0006 and at the start of pools-part-0007.

### `initialize-part-NNNN.csv.gz` (V4INIT; local-only, see `initialize-compact/`) and `v4-initialize-7d-part-NNNN.csv.gz` (V4RECENT), same columns
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

`initialize-parts.json` (committed): dataset, pin, block_from, block_to, total_rows, columns, and parts[] (file, rows, block_from,
block_to, bytes, sha256). The parts[] entries describe the local-only originals.

### `initialize-compact/` (committed copy of the V4INIT parts)

Origin: the main research session wrote these files, not this folder's collector agent. It wrote them on 2026-09-30 from 21:46Z
to 21:57Z so that the V4INIT data fits in git:
- `collect/compact_initialize.py` writes the compact copy; its log is `collect/compact_initialize.log`.
- `collect/expand_initialize.py` does the reverse.
- `tx-hash-recovery-check.json` was written at 21:56:49Z. The script that wrote it is not in this folder.
  (Added 2026-10-01, fixup: the main session wrote it with an inline script that was not saved as a file. The script took a
  40-row sample of the original Initialize rows and called `eth_getTransactionByBlockNumberAndIndex(block_number, tx_index)` on
  `https://base-mainnet.public.blastapi.io` for each; the file stores the returned hashes and the counts `checked` 40 /
  `matched` 40.)

Correction 2026-10-01: an earlier version of this manifest said these files "appeared at about 21:46-21:57Z, written by another
agent ... They are not described or maintained by this manifest." They are now described here.

| file | content |
|---|---|
| `pools-part-0001..0008.csv.gz` | one row per row of `initialize-part-*`, in the same order. Columns: block_number, tx_index, log_index, currency0, currency1, fee_raw, tick_spacing, hook_id, sqrt_price_x96, tick. Values are copied unchanged from the originals. hook_id is the `hook_id` of the hook address in `initialize-compact/hooks.csv` |
| `hooks.csv` | hook_id, hooks (address), and the 14 `hf_*` columns copied from the originals. One row per distinct `hooks` address (74,887), numbered in order of first appearance. `compact_initialize.py` aborts if one address carries different flags in two rows |
| `compact-index.json` | source_parts (the 22 originals), total_rows 15,333,247, pool_id_recomputed_mismatches 0, block_logindex_order_violations 0, distinct_hooks 74,887, parts[] (file, rows, block_from, block_to, bytes, sha256), and `rebuild` (text). **The `bytes` and `sha256` values in parts[] are wrong for all 8 parts** (see below). `rows`, `block_from` and `block_to` are correct. *(Corrected 2026-10-01, fixup: since commit 9c8a37c the `bytes` and `sha256` values in parts[] are correct for all 8 parts, re-checked against the files; the file also has a new key `index_correction` describing the recomputation.)* |
| `tx-hash-recovery-check.json` | method (`eth_getTransactionByBlockNumberAndIndex on base-mainnet.public.blastapi.io`), checked 40, matched 40, and rows[] of 40 (block_number, tx_index, tx_hash returned by the RPC) |

The columns left out of the compact copy, and how to rebuild them exactly:
- `pool_id = keccak256(abi.encode(currency0, currency1, uint24 fee_raw, int24 tick_spacing, hooks))`. `compact_initialize.py`
  recomputed it for every row against the original value, with 0 mismatches (`compact_initialize.log`).
- `tx_hash = eth_getTransactionByBlockNumberAndIndex(block_number, tx_index).hash` on Base. This needs an RPC endpoint.
- The `hf_*` flags come from `initialize-compact/hooks.csv`; they depend only on the hook address.
- `dynamic_fee` is `1` if fee_raw == 8388608, else `0`.

Commands (in `collect/`; `expand_initialize.py` needs pycryptodome, `Crypto.Hash.keccak`):
```
python3 expand_initialize.py > initialize-full.csv                                  # 27 columns, tx_hash left empty
python3 expand_initialize.py --rpc https://mainnet.base.org > initialize-full.csv  # also fills tx_hash (one RPC call per row)
python3 -c "import expand_initialize as e; next(e.iter_rows())"                     # iter_rows() streams dicts without a file
python3 compact_initialize.py > compact_initialize.log                              # forward direction: needs the local-only originals, rewrites ../initialize-compact/
```
`expand_initialize.py` writes one CSV with the same 27-column header and row order as `initialize-part-*.csv.gz`. It does not
re-create the 22-file split or the gzip bytes, so the sha256 values in `initialize-parts.json` hold only for the original files.

Checks done on 2026-10-01 (this documentation pass; read-only):
- **Rebuild compared with the originals.** `expand_initialize.iter_rows()` without RPC was streamed side by side with the 22
  original parts. 15,333,247 rows were compared, with 0 rows differing in any of the 26 columns other than `tx_hash`. The
  header and column order are identical.
- **tx_hash spot check.** All 40 `tx_hash` values in `tx-hash-recovery-check.json` equal the `tx_hash` of the original row at the
  same (block_number, tx_index).
- **Cause of the wrong values in `compact-index.json`.**
  - Each compact part on disk is 10 bytes longer than its recorded `bytes`.
  - The recorded `sha256` equals the sha256 of the first `bytes` bytes of the file.
  - The 10 missing bytes are the end of the gzip stream: the 2-byte final deflate block `0300` plus the 8-byte CRC32/ISIZE
    trailer. `compact_initialize.py` hashed each part before the last bytes were flushed to disk.
  - All 8 files pass `gzip -t`, and their row counts equal `compact-index.json`.
  - The correct bytes and sha256 values are in the inventory table.
  - (Added 2026-10-01, fixup: this describes the index as first written. The main session has since recomputed the values in
    `compact-index.json` and fixed `compact_initialize.py`; the index now matches the files.)

### `v4-swap-part-NNNN.csv.gz`
Columns, all raw:
- block_number, tx_hash, tx_index, log_index
- pool_id (topic1), sender (topic2)
- amount0 (int128), amount1 (int128)
- sqrt_price_x96 (uint160, after the swap)
- liquidity (uint128, in range after the swap)
- tick (int24, after the swap)
- fee (uint24, the LP fee applied, in 1e-6 units)

Sources for the sign of amount0 and amount1 (quoted, not re-derived here):
- The IPoolManager natspec says "amount0 The delta of the currency0 balance of the pool".
- PoolManager.sol emits `Swap(id, msg.sender, delta.amount0(), delta.amount1(), ...)`, where `delta` is the BalanceDelta
  returned to the caller.

Both files are saved verbatim in `hook-docs/raw/` and `hook-docs/text/` (`..._v4-core_main_src_interfaces_IPoolManager.sol`,
`..._v4-core_main_src_PoolManager.sol`).

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

Method:
- Multicall3.aggregate3 (allowFailure=true), 250 pools (500 calls) per eth_call, `blockTag = 52006432`.
- Endpoints, tried in random order: base-mainnet.public.blastapi.io, developer-access-mainnet.base.org, base.drpc.org and
  gateway.tenderly.co/public/base. All four served archive eth_call in probes.
- Failed items are retried as direct eth_call.

Note: StateView returns zeros (success) for a pool id that does not exist.

### `pool-keys-snapshot.csv.gz` (V4STATE; one row per pool in state-snapshot)
pool_id, currency0, currency1, fee_raw, tick_spacing, hooks, init_block, key_source. Values of key_source:
- `initialize_log_7d`: from the 7-day Initialize logs.
- `initialize_log_v4init`: from the full V4INIT Initialize data.
- `position_manager_poolKeys_at_snapshot`: `PositionManager.poolKeys(bytes25(poolId))` at the snapshot block. It is accepted only
  if keccak256(abi.encode(key)) == pool_id. init_block stays empty unless it is later found in V4INIT.
- `unresolved`: no key was found.

### `token-metadata.csv.gz` (V4STATE; one row per currency appearing in the snapshot pools)
The first two columns are:
- address
- is_native: 1 only for `0x000…000` (native ETH), whose other columns are empty.

Then come four columns for each of `symbol()`, `name()`, `decimals()` and `totalSupply()`:
- `<fn>_ok`: 1 if the call returned success.
- `<fn>_call_mode`: `multicall`; or `multicall_retry` (re-run in a multicall of only the failed items); or `direct` (a single
  eth_call with gas 5,000,000).
- `<fn>_return_raw`: the raw return data as hex, empty on failure.
- `<fn>_error`: error text for failures.

Each function also has a derived decoded value:
- `symbol_decoded` / `name_decoded`: an ABI string, or a bytes32 string if the return is exactly 32 bytes. UTF-8 with
  replacement; control characters and backslash are escaped as `\xNN`.
- `decimals`: a uint from a 32-byte return.
- `total_supply`: uint256 in base 10, raw units.

All calls are made at block 52006432.
Note: a Multicall3 low-level call to an address without code returns success with empty return data (`_ok=1`, `_return_raw=0x`).

`state-index.json`: snapshot block, pool and token counts, keys resolved/unresolved, whether V4INIT data was used, endpoints.

### `hooks.csv` (one row per hook address; built by `collect/build_hooks_csv.py`)
Rows: every hook with at least 20 pools in the counted Initialize data, plus every hook in the data that has any label source, plus
`0x000…000` (no hook).
| column | meaning |
|---|---|
| hook_address | hook |
| pool_count_so_far | number of Initialize events with this hook in the data counted when the script ran (see count_source). In the final build (2026-10-01 02:08:11Z) every row has count_source `v4init_final` and count_block_range `25350988-52006302`, so the counts cover all of V4INIT (checked 2026-10-01). Correction 2026-10-01: the earlier text "A later agent recounts from the final data" applied to the partial build and was removed |
| count_block_range | contiguous block range(s) covered by the counted data |
| count_source | `v4init_final` (final parts) or `v4init_work_chunks_partial` |
| first_init_block_in_counted_data, last_init_block_in_counted_data | first and last Initialize block for this hook in the counted data |
| pool_count_7d, count_7d_block_range | the same count over the 7-day window (51704033-52006432) |
| label, label_source_url, label_evidence | the label from the source with the highest precedence (see below) |
| n_label_sources | number of label rows for this hook in hook-labels-long.csv |
| blockscout_name, blockscout_is_verified, blockscout_creator_address, blockscout_creation_tx | Blockscout `/api/v2/addresses/<hook>` fields (raw) |
| creation_tx_from, creation_tx_to | from / to of the creation tx (Blockscout `/api/v2/transactions/<tx>`) |
| uniswap_hooklist_name | `hook.name` from Uniswap/hooklist `hooks/base/<address>.json` |
| zora_registry_tag_version | tag:version from ZoraHookRegistered events for this hook |
| hf_* (14 columns) | derived hook permission flags, same definition as above |

Label precedence is fixed, from highest to lowest:
1. The launchpad's own docs or repositories (Zora, Clanker, Flaunch, Doppler, Bunni). The label is the project name plus the
   Blockscout contract name, and the evidence is the verbatim document line.
2. Zora on-chain ZoraHookRegistry event.
3. Uniswap hooklist entry (name and description, verbatim).
4. Third-party code lists (Uniswap routing-api allowlist, KyberSwap dex-lib, Uniswap docs).
5. Blockscout verified contract name.

### `hook-labels-long.csv`
hook_address, source_kind (`document` / `zora_onchain_registry` / `uniswap_hooklist` / `blockscout`), precedence (1-5 as above), label, source_url, evidence_verbatim.

### `hook-docs/`
| file | content |
|---|---|
| `raw/<slug>.gz` | verbatim HTTP bodies of fetched docs and source files (gzip) |
| `text/<slug>.txt` | text of the same, with url, fetch time and HTTP status in the header. HTML tags are stripped and each link target is appended after its anchor text as ` <href>` |
| `fetch-log.jsonl` | one line per fetch: url, fetched_utc, http_status, bytes, sha256, raw_file, text_file (appended; re-fetches add lines). `bytes` and `sha256` are those of the decompressed body. For the last entry of each of the 37 raw files they equal the current `raw/<slug>.gz` content (checked 2026-10-01) |
| `doc-address-excerpts.csv.gz` | every line of every HTTP-200 text file that contains a 20-byte hex address: url, fetched_utc, http_status, line_no, address, line_verbatim, context_before_3_lines_verbatim |
| `blockscout/index.jsonl.gz` | one line per address queried on base.blockscout.com API v2: name, is_contract, is_verified, creator, creation tx, creation tx from/to/method/block/timestamp, contract name, compiler, file path, proxy type, implementations |
| `blockscout/<addr>.address.json.gz`, `<addr>.creation_tx.json.gz`, `<addr>.smart_contract.json.gz` | verbatim API responses with url and fetch time; smart_contract includes the verified source and ABI. Besides the hooks, the folder holds address and smart-contract responses for every log emitter seen in the launch-tx samples (factories, tokens, lockers and proxy implementations). `launch_tx_samples.py` fetched these to resolve event names; they are not listed in index.jsonl.gz |
| `uniswap-hooklist-base.jsonl.gz` | all 1,134 `hooks/base/*.json` entries of https://github.com/Uniswap/hooklist at commit `65ef4121419193a5aad9a493d2f4d9710d2f7653` (2026-09-30T16:30:30Z), verbatim JSON with raw URL |
| `zora-hook-registry-logs.jsonl.gz` | all 21 logs of ZoraHookRegistry `0x777777c4c14b133858c3982d41dbf02509fc18d7` (Blockscout getLogs, fromBlock 0 to latest, fetched 2026-09-30 about 21:22Z). The count equals RPC eth_getLogs over the same blocks |
| `zora-hook-registry-events.csv` | derived: decoded ZoraHookRegistered / ZoraHookRemoved events: block_number, tx_hash, log_index, event, hook, tag, version. topic0 ZoraHookRegistered(address,string,string) = `0xcf4000d2717988c072e9ec433f61ecff44a8bf0ebc5275e6353893a1b268fc5b` |
| `launch-tx-samples-tx.csv.gz` | for each candidate hook, up to 3 sample Initialize txs (earliest, middle, latest in the local data). Columns: hook, sample_pool_id, block_number, tx_hash, tx_from, tx_to (the `to` address of the transaction), tx_selector (4 bytes), tx_value_wei, receipt_status, n_logs, hook_pools_in_local_data |
| `launch-tx-samples-logs.csv.gz` | every log emitted by those sample txs: hook, sample_pool_id, block_number, tx_hash, log_index, log_address (emitter), topic0, n_topics, topics (`;`-joined), data, event_resolved_derived. event_resolved_derived is `ContractName:EventSig` if topic0 equals keccak256 of an event in the Blockscout-verified ABI of the emitter or of its proxy implementation, and empty otherwise. The table records, for each sampled tx, the contract it called and every log it emitted with its emitter, topics and data |

Correction 2026-10-01 (wording only): in the two launch-tx rows above, "tx_to (the contract called, e.g. a launchpad factory)" now
reads "tx_to (the `to` address of the transaction)". The sentence "This records which factory or deployer contract is called per
launch and which events and topics it emits" was likewise reworded to describe the columns only.

Documents fetched (URL list in `collect/fetch_docs.py`, fetch results in `hook-docs/fetch-log.jsonl`):
- Uniswap v4-core `Hooks.sol`, `PoolId.sol`, `LPFeeLibrary.sol`, `IPoolManager.sol`, `PoolManager.sol` and
  `ProtocolFeeLibrary.sol`, and v4-periphery `StateView.sol`.
- The Uniswap docs v4 deployments page. The docs.uniswap.org HTML returned HTTP 429, so the GitHub source
  `Uniswap/docs content/protocols/v4/deployments.mdx` was fetched instead.
- The Uniswap routing-api hooks allowlist and the Uniswap hooklist README.
- Zora docs (llms.txt, hook-registry, hook, factory, architecture, liquidity-migration, creating-a-coin, coins changelog) and
  zora-protocol source files.
- Clanker docs (deployed-contracts, core-contracts, token-deployments), plus the clanker-devco DOCS, the v4-contracts README
  and clanker-sdk `clankers.ts`.
- Flaunch: flaunch-gitbook for-aggregators.md, the flaunchgg-contracts README, and flaunch-sdk `addresses.ts` at a pinned
  commit.
- Doppler docs (contract-addresses, doppler-hooks).
- The Bunni v2 README.
- KyberSwap dex-lib Flaunch and Clanker hook constants.

## Row counts and parts

All counts below were re-checked on 2026-10-01 by streaming the files (see "Verified inventory").

| file | rows | block range | notes |
|---|---|---|---|
| `initialize-part-0001..0022.csv.gz` (local-only) | 15,333,247 total (per-part rows, block ranges, bytes and sha256 in `initialize-parts.json`; all 22 match the files) | 25,350,988-52,006,302 | 13,328 chunks of 2,000 blocks, 0 missing. The 22 parts cover contiguous block ranges. Largest part: 85.5 MB (85,509,481 bytes) |
| `initialize-compact/pools-part-0001..0008.csv.gz` | 15,333,247 total (2,200,000 / 2,260,000 / 2,140,000 / 2,040,000 / 2,000,000 / 2,160,000 / 2,140,000 / 393,247) | 25,352,561-52,006,295 (first and last Initialize block) | committed copy of the row above |
| `initialize-compact/hooks.csv` | 74,887 | | one row per distinct hook address |
| `v4-swap-part-0001.csv.gz` | 597,414 | 51,963,233-52,006,432 | 51.6 MB |
| `v4-modify-liquidity-part-0001.csv.gz` | 157,066 | 51,963,233-52,006,432 | |
| `v4-donate-part-0001.csv.gz` | 190 | 51,963,233-52,006,432 | |
| `v4-initialize-7d-part-0001.csv.gz` | 29,900 | 51,704,033-52,006,432 | |
| `state-snapshot.csv.gz` | 36,103 pools | block 52,006,432 | 12,117 rows with active_24h=1 and 29,900 with initialized_7d=1 (a pool can have both). slot0_ok=1 and liquidity_ok=1 on all rows |
| `pool-keys-snapshot.csv.gz` | 36,103 | | key_source: 29,900 initialize_log_7d, 6,203 initialize_log_v4init, 0 unresolved |
| `token-metadata.csv.gz` | 27,317 (27,316 ERC-20 addresses + 1 native row) | block 52,006,432 | for all 27,316 addresses, all 4 calls returned success via the first multicall (`_call_mode` = `multicall`) |
| `timestamps-check.csv` | 14 | 0-52,006,302 | |
| `hooks.csv` | 1,198 | counts over 25,350,988-52,006,302 (count_source=v4init_final) and the 7d window | final build 2026-10-01 02:08:11Z. The 22:00Z build also had 1,198 rows |
| `hook-labels-long.csv` | 1,388 | | final build 2026-10-01 02:08:11Z. The 22:00Z build had 1,363 rows |
| `hook-pool-counts-all.csv.gz` | 74,887 | 25,350,988-52,006,302 | derived: count of Initialize rows per hook address in the final V4INIT parts (sum = 15,333,247). Columns: hook_address, pool_count, first_init_block, last_init_block, count_block_range. Made by `collect/write_hook_pool_counts.py` after V4INIT.DONE |
| `hook-docs/doc-address-excerpts.csv.gz` | 1,766 (5,299 physical lines; fields contain newlines) | | from 20 distinct URLs. See the correction below |
| `hook-docs/fetch-log.jsonl` | 67 lines | | 63 HTTP 200, 2 HTTP 429, 2 HTTP 404 (re-fetches add lines) |
| `hook-docs/uniswap-hooklist-base.jsonl.gz` | 1,134 | | |
| `hook-docs/zora-hook-registry-events.csv` | 16 (21 raw logs) | | |
| `hook-docs/zora-hook-registry-logs.jsonl.gz` | 21 | | |
| `hook-docs/blockscout/index.jsonl.gz` | 213 addresses | | 79 rows fetched 2026-09-30 21:06:24-21:11:14Z (candidate list 1) and 134 rows fetched 21:54:16-22:01:18Z by HOOKLABELS step 1 (candidate list 2); all http_status 200 |
| `hook-docs/blockscout/<addr>.*.json.gz` | 2,932 files | | see the HOOKLABELS section |
| `hook-docs/launch-tx-samples-tx.csv.gz` | 639 | 25,477,714-52,006,386 | |
| `hook-docs/launch-tx-samples-logs.csv.gz` | 18,869 | | |

Corrections 2026-10-01:
- The previous version of this table gave `hooks.csv` as "1,198 at 22:00Z (rebuilt by the HOOKLABELS pipeline)",
  `hook-labels-long.csv` as "1,363 at 22:00Z", and `blockscout/index.jsonl.gz` as "79 addresses at 21:5xZ; HOOKLABELS adds 134".
  It also carried an "Update 2026-10-01" note pointing to the final counts. The table now shows the final counts directly.
- `doc-address-excerpts.csv.gz` was described as "from 37 fetched documents (36 HTTP 200, 1 HTTP 429)". The last fetch status of
  the 37 documents in `hook-docs/raw/` is 35 HTTP 200, 1 HTTP 429 (`https://docs.uniswap.org/contracts/v4/deployments`) and
  1 HTTP 404 (`https://raw.githubusercontent.com/flayerlabs/flaunch-sdk/main/src/addresses.ts`). The excerpt rows come from
  20 distinct URLs, all HTTP 200.

Consistency check: blocks 51,704,033-52,006,302 were fetched independently by two collectors:
- V4INIT: mainnet.base.org, Tenderly and developer-access, in 2,000-block chunks.
- V4RECENT: publicnode, developer-access and Tenderly, in 2,000-block chunks aligned differently.

Both give 29,893 Initialize rows, and the two row sets are identical.

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
python3 compact_initialize.py > compact_initialize.log   # (main session) initialize-part-* -> ../initialize-compact/
python3 expand_initialize.py [--rpc URL] > initialize-full.csv   # (main session) ../initialize-compact/ -> original rows
```
In a fresh clone, `collect/state/`, `collect/work/` and `initialize-part-*.csv.gz` are absent because they are local-only. Before
re-running against the same pins, write `collect/state/v4init-pin.json` from the `pin` object of `initialize-parts.json`, and
`collect/state/v4recent-pin.json` from the `pin` object of `recent-parts.json`. Both pin files were checked identical to those
objects on 2026-10-01.

Several scripts read the original Initialize parts: `hook_counts.py`, `write_hook_pool_counts.py`, `launch_tx_samples.py`,
`verify_launch_tx_selection.py` and `compact_initialize.py`. Rebuild those parts first with `expand_initialize.py` (note R1).

To re-pin to a new head, delete `collect/state/*-pin.json` and `collect/work/` (the old pins are kept in this manifest).

Resumability:
- V4INIT and V4RECENT write one checkpoint file per completed chunk, with no header, and a rerun skips existing chunks:
  - `collect/work/v4init/c_<from>_<to>.csv.gz`
  - `collect/work/v4recent/{act,init}_<from>_<to>.csv.gz`
- V4STATE checkpoints are `collect/state/v4state-{slot0,keys,meta}.json`.
- The work/ files are intermediate and duplicate the final parts. They can be deleted after the DONE sentinels exist. They are
  git-ignored (local-only).

Collector internals:
- JSON-RPC client with backoff on HTTP 429/5xx.
- eth_getLogs with a per-endpoint max range. Ranges are bisected on range or size errors, and any response with at least
  5,000 logs is re-fetched as two halves (a guard against silent provider caps).
- Work queue across endpoints. A failed chunk is requeued; after 12 (V4INIT) or 10 (V4RECENT) failures it is recorded as a gap and
  retried in later rounds (up to 6 or 5). Unrecoverable chunks are written to `collect/state/v4init-gaps.json` or
  `v4recent-gaps.json`, and a `.FAILED` sentinel is written. Neither gaps file exists (checked 2026-10-01). The DONE sentinel is
  written only after every chunk exists, parts are assembled, and part row counts are re-read and verified.

Endpoints used:
- V4INIT eth_getLogs: mainnet.base.org (2,000-block ranges, 2 in flight), gateway.tenderly.co/public/base (1,000, 2 in flight),
  developer-access-mainnet.base.org (2,000, 1 in flight).
- V4RECENT eth_getLogs: base-rpc.publicnode.com (newest chunks until its first archive-depth refusal), developer-access-mainnet.base.org,
  gateway.tenderly.co/public/base.
- Smoke tests:
  - `--smoke 37000000 37001999`: mainnet.base.org, Tenderly and developer-access returned identical rows (2,755).
  - V4RECENT smoke test (250 blocks near head): publicnode, developer-access and Tenderly returned identical rows (3,556).
    Its log is `collect/smoke_v4recent.log`.

## Coverage limits and gaps

- **base.drpc.org not used for getLogs.** On 2026-09-30 at about 20:55Z it answered eth_getLogs only for ranges of 10 blocks or less
  ("You can make eth_getLogs requests with up to a 10 block range" / "ranges over 10000 blocks are not supported on free plan").
  It was used only for eth_getCode (deployment block) and as one of the archive eth_call endpoints for V4STATE.
- **base-rpc.publicnode.com** refuses getLogs more than about 10,000 blocks behind head and eth_call more than about 128 blocks behind
  head ("Archive requests require a personal token", HTTP 403). It served only the newest part of the activity window.
- **V4INIT run 1 was restarted.**
  - Run 1 ran from 20:59:12Z to 21:11:40Z with the same pin. A drpc worker and a worker-exit bug were then fixed.
  - Completed chunk files were kept (resume), and in-flight chunks were refetched. Log: `collect/v4init.run1.log`.
  - V4RECENT was restarted in the same way (`collect/v4recent.run1.log`).
  - No data from the first runs was dropped: each chunk file is complete or absent.
- **Pinned heads.** Initialize events after block 52,006,302 are not in `initialize-part-*` / `initialize-compact/`. Those up to 52,006,432 are in `v4-initialize-7d-*`.
  Addition 2026-10-01 (V4WINDOW2): those from 52,006,433 to 52,017,160 are in `v4-window2-initialize-part-0001.csv.gz`.
  Initialize events after block 52,017,160 were not collected.
- **Launch activity is covered at block level only for one day.**
  - The 24 h activity window runs from 2026-09-29T21:03Z to 2026-09-30T21:03Z. Earlier Swap/ModifyLiquidity/Donate history was
    not collected.
  - Pending or mempool transactions were not collected, and neither were the priority fees paid by swaps.
  - Correction 2026-10-01 (V4WINDOW2): "only for one day" is no longer accurate. Swap/ModifyLiquidity/Donate logs are now also
    collected for blocks 52,006,433-52,017,160 (2026-09-30T21:03:33Z to 2026-10-01T03:01:07Z) in `v4-window2-*`, so block-level
    activity covers 51,963,233-52,017,160 without a gap. History before 51,963,233 and after 52,017,160 was not collected.
- **State snapshot scope.**
  - The snapshot covers only pools active in the 24 h window or initialized in the 7-day window, at one block.
  - Addition 2026-10-01 (V4WINDOW2): a second snapshot, `v4-window2-state-snapshot.csv.gz`, covers the pools that appear in the
    window-2 logs, at block 52,017,008. See the V4WINDOW2 section for its scope.
  - Tick-level liquidity (tick bitmap / ticks) was not collected.
  - Hook contract internal state (fees set by dynamic-fee hooks, anti-snipe windows) was not collected. The only exception is
    the verified sources saved in hook-docs/blockscout/*.smart_contract.json.gz.
- **Token metadata** covers only currencies of the snapshot pools, not every currency in the full Initialize set. Transfer
  restrictions or taxes of tokens were not probed.
  Addition 2026-10-01 (V4WINDOW2): `v4-window2-token-metadata.csv.gz` adds the currencies of the window-2 pools that are not in
  `token-metadata.csv.gz`. Together, the two files cover every currency of both snapshots.
- **Hook labels.**
  - Blockscout metadata was fetched only for the candidate lists in `collect/state/`. These lists are local-only; note R7 says
    how to rebuild them exactly from the committed `hook-docs/blockscout/index.jsonl.gz`.
    - `hooks-candidates-1.txt` (79): hooks with at least 10 pools in the partial V4INIT data at about 21:05Z (blocks
      25,350,988-34,044,987), plus hooks with at least 5 pools in the 7-day window.
    - `hooks-candidates-2.txt` (134): hooks with at least 20 pools in the final V4INIT data that were not in list 1.
    - `hooks-candidates-all.txt` (213) is the union used for launch-tx samples.
  - Hooks with fewer pools are in hooks.csv only if another label source names them.
  - Some hooks are unverified or have no creator recorded on Blockscout.
  - Per-hook counts for every hook address in the complete V4INIT data are in `hook-pool-counts-all.csv.gz` (74,887 rows,
    including address(0)).
  - Launch-tx samples are at most 3 txs per hook (earliest, middle, latest Initialize). They record which contract each sampled
    launch tx called and which events it emitted. They are not a full census of factory events.
  - The Uniswap hooklist is a registry maintained by a third party (entries by hook teams / Uniswap); it is recorded as is.
  - Doc excerpts are raw lines. An address on a docs page may refer to another chain (context lines kept).
  - Labels in `hooks.csv` follow the fixed precedence above. No manual reclassification was done.
- **docs.uniswap.org** returned HTTP 429. The GitHub source of the same page was saved instead.
- **flaunch-sdk** `main/src/addresses.ts` returned 404. The file at commit `bef27f90b946a63fe3c215a409b487ad38b1c685` was saved instead.
- **Local-only files.** `initialize-part-*.csv.gz`, `collect/state/`, `collect/work/` and `collect/__pycache__/` are
  git-ignored. See the status line at the top and notes R1-R9.

## Collector status

| name | sentinel | log | final status (checked 2026-10-01) |
|---|---|---|---|
| V4INIT | `/home/user/dapparb/research-material/.sentinels/V4INIT.DONE` | `collect/v4init.log` (and `collect/v4init.run1.log`) | DONE 2026-09-30T21:44:30Z, 15,333,247 rows, 22 parts |
| V4RECENT | `.sentinels/V4RECENT.DONE` | `collect/v4recent.log` (and `collect/v4recent.run1.log`) | DONE 2026-09-30T21:12:21Z |
| V4STATE | `.sentinels/V4STATE.DONE` | `collect/v4recent.log` | DONE 2026-09-30T21:46:25Z |
| HOOKLABELS (item 4 refresh) | `.sentinels/HOOKLABELS.DONE` | `collect/hooks_pipeline.log`, `collect/hook_blockscout.log`, `collect/launch_tx_samples.log`, `collect/build_hooks_csv.log`, `collect/verify_launch_tx_selection.log` | DONE 2026-10-01T02:09:44Z, after a re-run. The first run was killed at about 22:07-22:09Z on 2026-09-30, and `HOOKLABELS.FAILED` was written at that time. `hooks.csv`, `hook-labels-long.csv`, `hook-docs/blockscout/*` and `hook-docs/launch-tx-samples-*.csv.gz` are final |
| V4WINDOW2 (row added 2026-10-01) | `.sentinels/V4WINDOW2.DONE` | `collect/v4window2.log`, `collect/smoke_v4window2.log`, `collect/v4window2_consistency.log` | DONE 2026-10-01T03:57:28Z, single run, no restart. Blocks 52,006,433-52,017,160, 11 chunks, 0 gaps. See the V4WINDOW2 section at the end of this file |

Correction 2026-10-01: this table first gave the status at 2026-09-30 ~21:56Z, with HOOKLABELS "RUNNING (detached
`collect/hooks_pipeline.sh`)" and the note "When it finishes ... the counts in the table above for those files are then outdated.
The next agent re-counts them." The re-count has been done, and the counts above are final.

Update 2026-10-01 (kept from the previous version): `launch_tx_samples.py` was OOM-killed at 22:07Z and
`.sentinels/HOOKLABELS.FAILED` was written. It was fixed and re-run on 2026-10-01 01:18-02:09Z; the sentinel is now
`HOOKLABELS.DONE`. See section "HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)" at the end of this file.

Other files in this directory:
- `initialize-compact/`, `collect/compact_initialize.py`, `collect/compact_initialize.log` and `collect/expand_initialize.py`
  were written by the main research session, not by the collectors described here. They are documented in section
  "`initialize-compact/`" above.
- According to `compact_initialize.log`, the pool_id of every row was recomputed with 0 mismatches.
- Correction 2026-10-01: the earlier text said these files were "written by another agent ... not described or maintained by
  this manifest".

Stable file layout for downstream readers:
- `initialize-parts.json` lists the V4INIT parts (`initialize-part-NNNN.csv.gz`, NNNN = 0001..0022). These parts are
  local-only.
- `initialize-compact/compact-index.json` lists the committed compact parts. Take bytes and sha256 from the inventory below, not
  from that file. (Corrected 2026-10-01, fixup: since commit 9c8a37c the bytes and sha256 in that file are correct and equal the
  inventory.)
- `recent-parts.json` lists the V4RECENT parts, and `state-index.json` lists the V4STATE files.
- (Added 2026-10-01, V4WINDOW2) `v4-window2-parts.json` lists the V4WINDOW2 log parts with the per-chunk endpoints, and
  `v4-window2-state-index.json` lists the V4WINDOW2 snapshot files.

## HOOKLABELS re-run 2026-10-01 (memory fix of launch_tx_samples.py)

Sentinel: `.sentinels/HOOKLABELS.DONE` (written 2026-10-01T02:09:44Z after the manual checks below; `HOOKLABELS.FAILED` deleted).
Logs: `collect/hooks_pipeline.log`, `collect/launch_tx_samples.log` (lines of the killed run are kept above the `====` separators),
`collect/build_hooks_csv.log`, `collect/verify_launch_tx_selection.log`.

**What failed.**
- Step 1 of `collect/hooks_pipeline.sh` (`hook_blockscout.py` on `state/hooks-candidates-2.txt`) finished at
  2026-09-30 22:01:19Z (`hook-docs/blockscout/index.jsonl.gz`: 213 addresses, all HTTP 200).
- Step 2, `launch_tx_samples.py`, was killed (SIGKILL, "Killed" in `hooks_pipeline.log`) at about 22:09Z at 6.5 GB RSS, during
  its Blockscout ABI phase.
  - Before the kill it had logged `hooks 213 samples 639` and `txs 639 logs 18869 distinct emitters 1374`. It had written no
    output table.
  - The kill left a truncated `hook-docs/blockscout/0x111111125421ca6dc452d289314280a0f8842a65.smart_contract.json.gz.tmp`
    (gzip: unexpected end of file).
- Step 3 (`build_hooks_csv.py`) did not run.

**Cause.** The sample selection kept one Python tuple (block_number, log_index, tx_hash, pool_id) for every Initialize row whose
hook is a candidate, plus a set of all their pool-id strings. That is 15,033,116 rows; the per-hook counts are in
`hook-pool-counts-all.csv.gz`. Both were module-level variables, so they stayed in memory until the process exited, at roughly
400 bytes per row.
(Edit 2026-10-01: a single-hook row count that was given here was replaced by the pointer to the per-hook count file.)

**Fix** (`collect/launch_tx_samples.py`; the killed version is kept as `collect/launch_tx_samples.oom-version.py.txt`). The sampling
rule, the input files, the output files and their columns are unchanged:
- Per hook the script still picks the earliest, the middle (index n//2) and the latest row in (block_number, log_index) order.
- Before picking, it de-duplicates by pool_id and keeps the first occurrence.
- The inputs are still the V4INIT parts listed in `initialize-parts.json`, then `collect/work/v4recent/init_*.csv.gz`.

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
- 8 Blockscout responses (5 address, 3 smart_contract, fetched 01:30 to 02:05) were saved with `http_status` -1, because all
  retries failed.
- The script was then re-run from its checkpoints at 02:08:53, with no RPC calls. It re-fetched those 8 responses (all HTTP 200)
  and rewrote both launch-tx tables at 02:09:00. The tx table again has 639 rows and the logs table 18,869 rows.

**Endpoints.**
- Tx and receipt: `https://gateway.tenderly.co/public/base` first, then `https://mainnet.base.org`. Which endpoint served each tx is
  not recorded.
- Event ABIs: `https://base.blockscout.com/api/v2`.
- No new block pin. The samples come from the Initialize data pinned at 52,006,302 (V4INIT) and 52,006,432 (V4RECENT).

**Checks done by hand.**
- **Smoke test.** It ran on 5 hooks (5, 5, 25, 274 and 631,597 pools). The fixed selection equals the output of the killed
  version's selection code on the same 5 hooks (15 samples). The full run's tx and log rows for these hooks equal the
  smoke-test rows.
- **Independent selection check** with `collect/verify_launch_tx_selection.py`, which uses no bitmap and no sort.
  - Per hook, n = the V4INIT count from `state/hook-counts-final.json` plus the V4RECENT rows after block 52,006,302.
  - It takes the 0th, (n//2)-th and (n-1)-th row in stream order.
  - Result: 639 of 639 samples equal, 0 mismatches.
- **Re-fetch of 12 samples.** The 12 samples of `0xc8d077444625eb300a427a6dfb2b1dbf9b159040`,
  `0x9ea932730a7787000042e34390b8e435dd839040`, `0xbb7784a4d481184283ed89619a3e3ed143e1adc0` and
  `0x0469a4bd3724dc86c9542f4694c976da13c450c0` were re-fetched from base-mainnet.public.blastapi.io.
  - These fields all match: tx from, to, selector and block; receipt status; number of logs; every log address and data.
  - The log at the sampled log_index is emitted by the PoolManager, and its topic1 equals sample_pool_id.
- **Cleanup of the killed run.** No `*.tmp` file is left in `hook-docs/`. The stray `.tmp` was deleted, and the
  AggregationRouterV6 smart_contract response for `0x111111125421ca6dc452d289314280a0f8842a65` was re-fetched
  (2026-10-01T01:24:19Z, HTTP 200). Every `hook-docs/blockscout/*.json.gz` passes `gzip -t` and parses.

**Row counts.**

| file | rows | notes |
|---|---|---|
| `hook-docs/launch-tx-samples-tx.csv.gz` | 639 | 213 hooks x 3 samples; 639 distinct sample_pool_id; 626 distinct tx_hash (a tx hash can appear in more than one row); blocks 25,477,714-52,006,386; receipt_status 0x1 on all rows |
| `hook-docs/launch-tx-samples-logs.csv.gz` | 18,869 | equals the sum of n_logs; 1,374 distinct log_address; 14,279 rows with a non-empty event_resolved_derived |
| `hooks.csv` | 1,198 | rebuilt 02:08:11Z (count_source v4init_final, count_block_range 25,350,988-52,006,302); replaces the 22:00Z build |
| `hook-labels-long.csv` | 1,388 | rebuilt 02:08:11Z; replaces the 22:00Z build (1,363) |
| `hook-docs/blockscout/index.jsonl.gz` | 213 | all http_status 200; not changed by the re-run |
| `hook-docs/blockscout/<addr>.*.json.gz` | 2,932 | address 1,859 (1,858 HTTP 200, 1 http_status -1, see below); creation_tx 150; smart_contract 923. 1,549 fetched on 2026-10-01, 1,383 on 2026-09-30 |
| `collect/state/launch-tx-samples-selection.json` (local-only) | 639 samples | checkpoint, plus selection stats |
| `collect/work/launch_tx_cache.jsonl` (local-only) | 626 | intermediate cache, one line per tx hash |

All counts in this table were re-checked on 2026-10-01 and match.

**Selection stats** (counts from the selection run):
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

## Verified inventory (2026-10-01)

Note added 2026-10-01 (V4WINDOW2): this inventory was taken before V4WINDOW2 ran. Its file totals (for example "16,767 files")
and tables do not include the V4WINDOW2 files. Those files are listed, with bytes, rows and sha256, in the V4WINDOW2 section at
the end of this file.

**Method.** Every file in the folder was read once by streaming; no data file was modified. For each file the check recorded:
- size in bytes and sha256. Every file is at most 100 MB; the largest is 89,919,415 bytes.
- `gzip -t` for every `.gz` file.
- decompressed line counts.
- CSV records, counted with Python `csv`. The header is excluded, and quoted newlines inside a field are not counted as rows.
- a full parse of every `.json` / `.json.gz` file and of every line of every `.jsonl` / `.jsonl.gz` file.

The verification processes used under 150 MB RSS each, as observed with `ps`.

**Results.**
- **Files.** There are 16,767 files: 3,076 committed (MANIFEST.md included) and 13,691 local-only. The local-only files are
  git-ignored by the repository `.gitignore`: `collect/work/` (13,654 files), `collect/state/` (10),
  `collect/__pycache__/` (5) and `initialize-part-*.csv.gz` (22).
- **Integrity.** `gzip -t`: 16,666 of 16,666 `.gz` files OK. JSON: 2,944 of 2,944 `.json`/`.json.gz` files parse. JSONL: 0 bad
  lines. CSV: 0 rows with a column count different from the header.
- **Size.** No committed file exceeds 90 MB. The largest committed file is `initialize-compact/pools-part-0002.csv.gz`
  (89,919,415 bytes).
- **Index files.**
  - `initialize-parts.json`: rows, bytes and sha256 match all 22 parts; the sum of rows is 15,333,247. The 22 block ranges are
    contiguous over 25,350,988-52,006,302.
  - `recent-parts.json`: rows, bytes and sha256 match all 4 parts.
  - `initialize-compact/compact-index.json`: rows match all 8 parts (sum 15,333,247). Bytes and sha256 match none of them; see
    section "`initialize-compact/`". (Corrected 2026-10-01, fixup: after the main session's recomputation (commit 9c8a37c),
    rows, bytes and sha256 match all 8 parts.)
- **Rebuild.** The rows rebuilt by `collect/expand_initialize.py` equal the 22 originals in all 26 columns other than
  `tx_hash`, with 0 mismatches over 15,333,247 rows. All 40 tx-hash-recovery-check rows match.
- **Work chunks.**
  - `collect/work/v4init/`: 13,328 files (= 13,328 chunks of 2,000 blocks), 15,333,247 lines in total.
  - `collect/work/v4recent/act_*`: 754,670 lines, made of 597,414 `swap`, 157,066 `modify` and 190 `donate` (first column).
  - `collect/work/v4recent/init_*`: 29,900 lines.
- **Counts stated elsewhere in this manifest.** These were re-checked and all match: state-snapshot, pool-keys-snapshot,
  token-metadata, timestamps-check, hooks.csv, hook-labels-long.csv, hook-pool-counts-all.csv.gz (sum 15,333,247),
  uniswap-hooklist, the zora files, blockscout (index and per-kind file counts, http_status), the launch-tx tables, the
  selection checkpoint and the tx cache. The two exceptions are the `doc-address-excerpts` note and the `compact-index.json`
  values, both corrected above.
- **Pins and hook counts.** `collect/state/v4init-pin.json` and `v4recent-pin.json` equal the `pin` objects of
  `initialize-parts.json` and `recent-parts.json`. The `hooks` list of `collect/state/hook-counts-final.json` equals the rows of
  `hook-pool-counts-all.csv.gz`.
- **Hook candidate lists.** `collect/state/hooks-candidates-1.txt` equals the first 79 addresses of
  `hook-docs/blockscout/index.jsonl.gz` in file order. `hooks-candidates-2.txt` equals the remaining 134, and
  `hooks-candidates-all.txt` equals list 1 followed by list 2. The same 213 addresses are the distinct `hook` values of
  `hook-docs/launch-tx-samples-tx.csv.gz`.

**How to regenerate the local-only files** (codes used in the "git" column):
- **R1** `initialize-part-0001..0022.csv.gz`:
  - Run `cd collect && python3 expand_initialize.py --rpc <Base RPC URL> > initialize-full.csv`. This gives the same 27-column
    header and row order; without `--rpc`, `tx_hash` is empty.
  - To get the 22-file split, cut the output at the per-part `block_from`/`block_to` in `initialize-parts.json`. The gzip bytes,
    and so the sha256 values, will differ from the table.
  - Alternative: re-collect with `collect/v4init_collector.py` after restoring the pin (R4). This needs archive eth_getLogs
    endpoints.
- **R2** `collect/work/v4init/c_<from>_<to>.csv.gz`: checkpoint files of `collect/v4init_collector.py`.
  - There is one file per 2,000-block chunk from 25,350,988, with the 27 columns of `initialize-part-*` and no header. The 22
    parts were assembled from them.
  - Regenerate by re-running `v4init_collector.py` with the pin (R4), or by splitting the R1 output into 2,000-block chunks.
- **R3** `collect/work/v4recent/act_<from>_<to>.csv.gz` and `init_<from>_<to>.csv.gz`: checkpoint files of
  `collect/v4recent_collector.py`, with no header.
  - In `act_` files the first column is the event type (`swap`, `modify` or `donate`), followed by that event's columns. They
    were assembled into the `v4-swap/modify-liquidity/donate-part-0001.csv.gz` files.
  - `init_` files have the columns of `v4-initialize-7d-part-0001.csv.gz`.
  - Regenerate by re-running `v4recent_collector.py` with the v4recent pin (R4). This needs archive eth_getLogs for blocks
    51,704,033-52,006,432.
- **R4** `collect/state/v4init-pin.json` and `collect/state/v4recent-pin.json`: write the `pin` object of `initialize-parts.json`
  and of `recent-parts.json` to these paths (JSON, indent 1).
- **R5** `collect/state/v4state-slot0.json`, `v4state-keys.json` and `v4state-meta.json`: checkpoints of the V4STATE phase of
  `collect/v4recent_collector.py`.
  - They hold the getSlot0/getLiquidity results per pool, the pool keys, and the token metadata calls.
  - The committed outputs assembled from them are `state-snapshot.csv.gz`, `pool-keys-snapshot.csv.gz` and
    `token-metadata.csv.gz`.
  - Regenerate by re-running `v4recent_collector.py` with the v4recent pin (R4). This needs archive eth_call at block
    52,006,432.
- **R6** `collect/state/hook-counts-final.json`: run `cd collect && python3 write_hook_pool_counts.py`. It runs `hook_counts.py`
  over the initialize parts, so it needs R1. Its `hooks` list equals the committed `hook-pool-counts-all.csv.gz`.
- **R7** `collect/state/hooks-candidates-1.txt`, `-2.txt` and `-all.txt`: no committed script wrote them. Rebuild them from
  `hook-docs/blockscout/index.jsonl.gz`, writing one lowercase `address` per line with a trailing newline:
  - list 1 = rows 1-79;
  - list 2 = rows 80-213;
  - all = rows 1-213.
- **R8** `collect/state/launch-tx-samples-selection.json` and `collect/work/launch_tx_cache.jsonl`: checkpoints of
  `cd collect && python3 launch_tx_samples.py state/hooks-candidates-all.txt`.
  - That command needs R1, the R3 `init_` chunks and R7.
  - The selected samples are also in the committed `hook-docs/launch-tx-samples-tx.csv.gz` (hook, sample_pool_id,
    block_number, tx_hash), and the fetched tx and receipt fields are in `hook-docs/launch-tx-samples-tx.csv.gz` /
    `-logs.csv.gz`.
- **R9** `collect/__pycache__/*.pyc`: Python bytecode, written automatically when the scripts are imported.

**Top level**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `MANIFEST.md` | (this file) | - | not listed (changes with every edit) | committed |
| `hook-labels-long.csv` | 736,735 | 1,388 rows | `0715a4011d427655c251dab5f08f761eb8b9b324a57e72f5437fc2bae2cfa221` | committed |
| `hook-pool-counts-all.csv.gz` | 2,241,342 | 74,887 rows | `55a5ec729bc9f2f9baa7e8e993b4bb42f600d401dcd2080c447b302947956efa` | committed |
| `hooks.csv` | 823,974 | 1,198 rows | `247e1a1179d09ef623cde58c6a23a959cb07b288f556f52ec52bee8a1fa826eb` | committed |
| `initialize-part-0001.csv.gz` | 85,009,113 | 721,377 rows | `f5f0d101fc86e1738983f085348b67bc0a88f8c094b44e2a32a6d5906bf7e0b6` | local-only (R1) |
| `initialize-part-0002.csv.gz` | 85,344,079 | 761,851 rows | `8e8f5ed5b9d9844c85e5296dc37a00380d573417d79aa0d7364205a05d8c4614` | local-only (R1) |
| `initialize-part-0003.csv.gz` | 85,056,842 | 733,829 rows | `61f29f57528e8f889c3a3194f5cc7f039225a90298dfe40b59c447d741e25345` | local-only (R1) |
| `initialize-part-0004.csv.gz` | 85,213,605 | 727,635 rows | `54277184d3251ce285d608f14821c1f3faf570c0188dc19fa31e6c9a82d62cc5` | local-only (R1) |
| `initialize-part-0005.csv.gz` | 85,017,880 | 720,394 rows | `d44b1e0fb8958a8c52e25a4efdf9ef4cb4534b666ad0665f32e7ea6c8467a176` | local-only (R1) |
| `initialize-part-0006.csv.gz` | 85,054,159 | 711,695 rows | `978ea7cf1bb87d72f329878307284db56bcbb20feaee8444622075655bd163b3` | local-only (R1) |
| `initialize-part-0007.csv.gz` | 85,010,821 | 697,745 rows | `9ac2fb3c6d22f8e11d2e025032aa5030ed3ff9352fa3d3e250ac3ce0e073f422` | local-only (R1) |
| `initialize-part-0008.csv.gz` | 85,118,198 | 701,413 rows | `151be8d964048ac9e56f2af4367f900198bd90648a6d67cb70951c74f110447c` | local-only (R1) |
| `initialize-part-0009.csv.gz` | 85,133,593 | 717,106 rows | `21ae103b74fc70e166a421e34a22c7261188d27b440425999847925e1dbce21b` | local-only (R1) |
| `initialize-part-0010.csv.gz` | 85,311,249 | 687,845 rows | `3c173539d8680b25100708ef5faca593312f443319e30eab2cff80402183d9cb` | local-only (R1) |
| `initialize-part-0011.csv.gz` | 85,441,483 | 694,791 rows | `5d986847ff147bf5251557d62fc0054555579e360370fd776d63c961191c94e3` | local-only (R1) |
| `initialize-part-0012.csv.gz` | 85,509,481 | 698,913 rows | `b11a4b4378e892da54d1e6a167568aa66ad7cb2b8497400cb6b9d2e838ffed2a` | local-only (R1) |
| `initialize-part-0013.csv.gz` | 85,339,980 | 701,283 rows | `a6263174fe90d1b4241c09ddf9856939a6d92c49a079579e7fa299cafbf61167` | local-only (R1) |
| `initialize-part-0014.csv.gz` | 85,383,408 | 723,125 rows | `773cd227f8a279014cd07334337605a626f8897c0f02563dd4ac15f8f6829a47` | local-only (R1) |
| `initialize-part-0015.csv.gz` | 85,127,330 | 753,457 rows | `35614b0ba43d3534289008e29c7b5a35ee94693b074a35cc66e435d68fb3deca` | local-only (R1) |
| `initialize-part-0016.csv.gz` | 85,192,028 | 758,096 rows | `ef15e045de78148ec349148bfc8bb44d86143c8938d0760e99995a8625f33e0a` | local-only (R1) |
| `initialize-part-0017.csv.gz` | 85,117,281 | 727,450 rows | `b3e30bf6fdc1db5278f6e9356a11ff7650564558a1bfbcc72310121de547d197` | local-only (R1) |
| `initialize-part-0018.csv.gz` | 85,177,860 | 737,152 rows | `c197a5e371932197e9b3d5e5a278c2cacc0ec22fbe6fa7111b8ec3e44b41c9ce` | local-only (R1) |
| `initialize-part-0019.csv.gz` | 85,295,070 | 714,746 rows | `b9fe340d9ab7727a86b3f6c61b83adb9f2c4c71708db0dcfeed1270a22f166bc` | local-only (R1) |
| `initialize-part-0020.csv.gz` | 85,143,083 | 704,481 rows | `f7aaed4da4c351e15f63cb65381b9adea5290998516c2f20b05c2291d5167344` | local-only (R1) |
| `initialize-part-0021.csv.gz` | 85,026,983 | 680,378 rows | `2299a50f004522558f54a1f8ccb7459d21320327f0b30dd735f4df92ad9ac4e8` | local-only (R1) |
| `initialize-part-0022.csv.gz` | 32,620,896 | 258,485 rows | `637d473a95abb96b6ac82def9775936c64192d853ad0acccc6bbe8ccd92d8774` | local-only (R1) |
| `initialize-parts.json` | 6,309 | JSON dict, parses | `b10158e05c85f5e23cad0f334ca71e1ba4d8f16fd658c2bee4fcb870345a12f8` | committed |
| `pool-keys-snapshot.csv.gz` | 2,906,803 | 36,103 rows | `209d80c4850b414d3dc64824113712482f6542e92f6d57701634e80fdaa32c39` | committed |
| `recent-parts.json` | 3,163 | JSON dict, parses | `5302661899d4fc3e2a6d01787dcd826392e6457389bc281cac5c289a1df16e11` | committed |
| `state-index.json` | 1,732 | JSON dict, parses | `33f65ed8775e30d1212380ed22888591f7c9ab5d52977e5f06cfddc0b79ac977` | committed |
| `state-snapshot.csv.gz` | 2,198,273 | 36,103 rows | `905bd290851a1f56b007dd878755e9c9a15a236ff1886d540a928b3683999071` | committed |
| `timestamps-check.csv` | 499 | 14 rows | `9235106e424aafe4677930b0b0b951a30e10a218a29619b1f800dcde1143f4e8` | committed |
| `token-metadata.csv.gz` | 1,796,958 | 27,317 rows | `71499fbab951d96fd24c8c5584627f91c8947f7f0049620b20e0cf5f3854fd09` | committed |
| `v4-donate-part-0001.csv.gz` | 12,725 | 190 rows | `6e847c9a83a418a2a86b94cba6c22ec7525e2965a86d15cb227b2f56bf3c6265` | committed |
| `v4-initialize-7d-part-0001.csv.gz` | 3,841,529 | 29,900 rows | `f0a9aafe6b7b45b3dfbdfbdad83cf60493a0bd18c3371b35b270266ba0729137` | committed |
| `v4-modify-liquidity-part-0001.csv.gz` | 5,000,604 | 157,066 rows | `d52959b78f6ad4cf5c7d2f0945648f66cc38c45a4ca4ae18defa8ac089bb5901` | committed |
| `v4-swap-part-0001.csv.gz` | 51,633,065 | 597,414 rows | `327786066248a1971819e859dbfe52acd003960663761f59b58f253105033e1c` | committed |

**initialize-compact/**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `initialize-compact/compact-index.json` | 3,904 | JSON dict, parses; parts[] bytes/sha256 match the 8 part files (re-checked 2026-10-01 fixup). Corrected row: previously 3,645 bytes, sha256 `66608d148888ace7429e49b147906e052496cd6f205373f9c00950b11b3db7f1` (version of commit 7639ca0, before the recomputation) | `494c2463eddcb606123b093a2b23759ec3cfb50f39eb2deb585198df3d11e164` | committed (9c8a37c) |
| `initialize-compact/hooks.csv` | 5,755,540 | 74,887 rows | `0c04c318d0e5266f6b3201eadb4a5048546facd2cebed5ef2c2419ce1850ba15` | committed |
| `initialize-compact/pools-part-0001.csv.gz` | 89,308,775 | 2,200,000 rows | `81245894dd3b38dfd84085e79cdfd81d6991eef91dc4c1e536a9776019e7cec5` | committed |
| `initialize-compact/pools-part-0002.csv.gz` | 89,919,415 | 2,260,000 rows | `304089ca3f14c727a8739820c3f0ed8e0a66c67925e1967a734d2c8602fcfe3a` | committed |
| `initialize-compact/pools-part-0003.csv.gz` | 89,247,340 | 2,140,000 rows | `9cad83cf22d6ae5a52578149360cff06e84e0b446685a093a9ff48362a053d3f` | committed |
| `initialize-compact/pools-part-0004.csv.gz` | 89,215,158 | 2,040,000 rows | `f2874e162b5fd2aa7d9f9d8ef3f66d1a15d39e64057e3cf82ef2e3963a888165` | committed |
| `initialize-compact/pools-part-0005.csv.gz` | 89,511,628 | 2,000,000 rows | `a2ee71767b144c9449b78659e272f40857f54d711bfcebb9c3315069126d6524` | committed |
| `initialize-compact/pools-part-0006.csv.gz` | 89,681,248 | 2,160,000 rows | `036a1d5279484726d028de7f76b574751d6ad2578a144ee60bca1a74e80e5310` | committed |
| `initialize-compact/pools-part-0007.csv.gz` | 89,787,516 | 2,140,000 rows | `5fc6d1936f4c550c945e2acb60e49d6b1873292718e2fb6880df707e7f57161c` | committed |
| `initialize-compact/pools-part-0008.csv.gz` | 16,358,528 | 393,247 rows | `ebf4e018f371358e190949c4a02da0b413d6a2284e825fefe76899b893c6895f` | committed |
| `initialize-compact/tx-hash-recovery-check.json` | 5,924 | JSON dict, parses | `78c4c4c33eb2c296361bfb07ce1474ec450f49a2b083219cbdb67a0c42ce4e9f` | committed |

**hook-docs/ (tables and logs)**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `hook-docs/doc-address-excerpts.csv.gz` | 87,017 | 1,766 rows (5,299 lines; quoted multi-line fields) | `6b9289145ee51f40f48cf704b5d80a1c7a7b26cd5f62595612668afca41355e9` | committed |
| `hook-docs/fetch-log.jsonl` | 31,198 | 67 lines (JSON, all parse) | `d8f5b93ef1cd3d840c5c505c61e2380160c1c499b7908a6db5ac454ff0d3bec6` | committed |
| `hook-docs/launch-tx-samples-logs.csv.gz` | 872,692 | 18,869 rows | `54510c1fbfbd2e3cf648458933082360fb9f175cafdc029ba2dc97ada126139a` | committed |
| `hook-docs/launch-tx-samples-tx.csv.gz` | 76,585 | 639 rows | `2de0eb0f12e85da65077067f95e5cab917e8fc21b560193c183ca5226e942154` | committed |
| `hook-docs/uniswap-hooklist-base.jsonl.gz` | 169,148 | 1,134 lines (JSON, all parse) | `ea827e53d813ba2e1138e574304d1bd5dcbc07636f4b81494fcdcf4e9ea119cb` | committed |
| `hook-docs/zora-hook-registry-events.csv` | 2,565 | 16 rows | `49b263c576febe7f51712a31812ee06d72833dd45835ee40691d4322bb86e013` | committed |
| `hook-docs/zora-hook-registry-logs.jsonl.gz` | 1,564 | 21 lines (JSON, all parse) | `a3e51b3b2b0ab2b0e8bdd14ad1f2eb3f1bed512b4a35825a7c6ad71e0e9c1e74` | committed |

**hook-docs/blockscout/index.jsonl.gz**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `hook-docs/blockscout/index.jsonl.gz` | 23,126 | 213 lines (JSON, all parse) | `f9f28e52763696fb7a4afe2800fbb3584cde37d80b8f3df2542e58d2bf166ad2` | committed |

**hook-docs/raw/**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `hook-docs/raw/clanker.gitbook.io_documentation_general_token-deployments.gz` | 70,016 | 690 lines (decompressed) | `654b7927c530b7986d18c36d0b7d201a671c0d1c7f4692ae7cc55c3f8603ae48` | committed |
| `hook-docs/raw/clanker.gitbook.io_documentation_references_core-contracts.gz` | 63,178 | 690 lines (decompressed) | `e4653ee8b1f6701762bec91f1a4d45b85e63f4536496e32eadfffbe0ac033825` | committed |
| `hook-docs/raw/clanker.gitbook.io_documentation_references_deployed-contracts.gz` | 99,549 | 690 lines (decompressed) | `2bb3b52e26e7b428f1c1bcf2c3276d211fbd341e93b198722706127af30d26da` | committed |
| `hook-docs/raw/docs.doppler.lol_advanced-features_doppler-hooks.gz` | 82,014 | 723 lines (decompressed) | `cbf37a6471ab7f2faf77cdd6f198f31133cb94126f0eb48971729f6f32968e7f` | committed |
| `hook-docs/raw/docs.doppler.lol_reference_contract-addresses.gz` | 186,394 | 722 lines (decompressed) | `70126421e6168dbd9f9aa484717ef07cff1e7ed5a175b9a83268661af6e84d62` | committed |
| `hook-docs/raw/docs.uniswap.org_contracts_v4_deployments.gz` | 2,263 | 136 lines (decompressed) | `e52bfb6733320e3501b286a1ac1f6927c86455a549e8b6d9b8c042f7a9694491` | committed |
| `hook-docs/raw/docs.zora.co_changelogs_coins.gz` | 11,908 | 427 lines (decompressed) | `ae5087ac23d44bd6ea648578100d35f4c3204b265e016c207ba16989301ed1ca` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_architecture.gz` | 16,235 | 92 lines (decompressed) | `738b82c6ce675f2dd2c07a0a67c11273496fd8f26437d89f9b46660f5fc3d7ae` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_creating-a-coin.gz` | 16,382 | 330 lines (decompressed) | `c4f8aff1b97d65adf2225cff0f87c754bd3f6c70ac7ebf31f8bc49f1ea82b882` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_factory.gz` | 16,374 | 330 lines (decompressed) | `a1f7c1e4ecb9992767cfd35c486d41676d1d63605109b3cd2a741db760580c35` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_hook-registry.gz` | 6,714 | 48 lines (decompressed) | `6df6572c64dc1ebce5f07161ad43cf1361c8d6d194b7c8f6ffb9c1b7f5ae8adb` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_hook.gz` | 10,384 | 204 lines (decompressed) | `307bdc29cbccf6ffc3096fc76bc83079bcac47cf6801c14ab96105b11dd9fc5b` | committed |
| `hook-docs/raw/docs.zora.co_coins_contracts_liquidity-migration.gz` | 12,704 | 37 lines (decompressed) | `8d2f31f6584b2f2615f208224211e38da4210d9704b14163cb91ef0fcf0e7770` | committed |
| `hook-docs/raw/docs.zora.co_llms.txt.gz` | 1,716 | 41 lines (decompressed) | `4ed87f0f04b2d851b0f19034332b846b5b1c26a9d9900358f36cc483f68f1850` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Bunniapp_bunni-v2_main_README.md.gz` | 1,473 | 115 lines (decompressed) | `a65c75a0fa231956b86325daf36116ff6d23e67a99b9fb7fe8e740e9e7aabd69` | committed |
| `hook-docs/raw/raw.githubusercontent.com_KyberNetwork_kyberswap-dex-lib_0867b088e490608f731e4e37eaf49ea72e7846b3_pkg_liquidity-source_uniswap_v4_hooks_clanker_constant.go.gz` | 1,364 | 72 lines (decompressed) | `98cc2bee2e3416a2db10761d2cf4689bf0000e0e9fabdfb60e3513cbc350a4ac` | committed |
| `hook-docs/raw/raw.githubusercontent.com_KyberNetwork_kyberswap-dex-lib_0867b088e490608f731e4e37eaf49ea72e7846b3_pkg_liquidity-source_uniswap_v4_hooks_flaunch_constant.go.gz` | 1,346 | 61 lines (decompressed) | `d8ce1b2d93c6900fc5d8e0483ae43f6dafc8aec32d42a8a7f763fb3c9d288b6e` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_docs_main_content_protocols_v4_deployments.mdx.gz` | 6,472 | 327 lines (decompressed) | `aaca6e0ffac81e7ee107372604b0fb03c3eadf8c4eef0a9ee3b237990b25343b` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_hooklist_main_README.md.gz` | 1,254 | 51 lines (decompressed) | `09238e72cecbc0038b0e52f423a7124e87033c1e193125a26fb51c18d4c81b02` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_routing-api_main_lib_util_hooksAddressesAllowlist.ts.gz` | 8,127 | 395 lines (decompressed) | `8ee426dabfdf46088d05435951e029de001e9f15999a3271798a2160e0997751` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_PoolManager.sol.gz` | 3,943 | 395 lines (decompressed) | `8c31b8bdd94d7cce82ce2f44b2d5e22e96a7af1885195724eef6bd18f8ce2190` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_interfaces_IPoolManager.sol.gz` | 3,793 | 217 lines (decompressed) | `200d2b665999982f501e8b22822e7f90b47fe39234a40a9d81e0374d46bfdb43` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_Hooks.sol.gz` | 3,707 | 340 lines (decompressed) | `d74def273766599394a7ac3f740f6d0777edf086fa301b1f2508902c4f645f31` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_LPFeeLibrary.sol.gz` | 1,227 | 79 lines (decompressed) | `c01a35ccad146ae3154e59190396d7020f5018941e23527055529ceb8a82c6c8` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_ProtocolFeeLibrary.sol.gz` | 917 | 47 lines (decompressed) | `297e9e0e1d4ab2be08b9b5d504956cc5012c5641e94d80c996d1847bef1b6f23` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-core_main_src_types_PoolId.sol.gz` | 411 | 17 lines (decompressed) | `e9deaadfe67e7d0dd1b08fa84d6b11952392555f93f02b1b96f760d826139bea` | committed |
| `hook-docs/raw/raw.githubusercontent.com_Uniswap_v4-periphery_main_src_lens_StateView.sol.gz` | 888 | 109 lines (decompressed) | `94cb671ebe513fb450946d590a94355b5be2e3de0692d12957506637858afc52` | committed |
| `hook-docs/raw/raw.githubusercontent.com_clanker-devco_DOCS_main_references_deployed-contracts.md.gz` | 3,252 | 316 lines (decompressed) | `380ea12d0ade38ca03387b37f54f0c47aa728d6fb1f247c642a6088590d8bdc8` | committed |
| `hook-docs/raw/raw.githubusercontent.com_clanker-devco_clanker-sdk_main_src_utils_clankers.ts.gz` | 4,159 | 392 lines (decompressed) | `7f4af6008a63fb2a19eb7009ed81016b2a2b2f451a3fbb6f4578f9159ec5c232` | committed |
| `hook-docs/raw/raw.githubusercontent.com_clanker-devco_v4-contracts_main_README.md.gz` | 3,765 | 176 lines (decompressed) | `69b5a8f49b5ab2e6fb01e44ff2042ac51d80a328b3805b3b2a426b86d8eff39a` | committed |
| `hook-docs/raw/raw.githubusercontent.com_flayerlabs_flaunch-gitbook_main_readme_for-aggregators.md.gz` | 4,017 | 223 lines (decompressed) | `62268518a9011f00fc0619359d82138ad639ec8b338ddeefad0a3c8ea9378402` | committed |
| `hook-docs/raw/raw.githubusercontent.com_flayerlabs_flaunch-sdk_bef27f90b946a63fe3c215a409b487ad38b1c685_src_addresses.ts.gz` | 12,904 | 766 lines (decompressed) | `0e967e00e1d9dc4d01e7327f6464486e140bb58a6e67084979cf8566acb5847a` | committed |
| `hook-docs/raw/raw.githubusercontent.com_flayerlabs_flaunch-sdk_main_src_addresses.ts.gz` | 105 | 1 line (decompressed) | `7e543aa4c6f93936181f45d6acac91297d9c35c14d0c0633f6153865d2a74c0a` | committed |
| `hook-docs/raw/raw.githubusercontent.com_flayerlabs_flaunchgg-contracts_main_README.md.gz` | 8,759 | 153 lines (decompressed) | `a258824326644d6de05d4fd9a8b548102a109423f1fdfa1e70881ad101d9f513` | committed |
| `hook-docs/raw/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins-deployments_.github_PR_TEMPLATE_UPGRADE_INSTRUCTIONS.md.gz` | 2,392 | 140 lines (decompressed) | `8418457edb6874f434100c620bccfefeeb2d990c87f2fe3a090ff9d6ee004350` | committed |
| `hook-docs/raw/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins_src_deployment_ForkedCoinsAddresses.sol.gz` | 1,029 | 54 lines (decompressed) | `9e0fe228ec4120cf25f00cf594a1f62b9383e936cccb84f9b03e668304639b19` | committed |
| `hook-docs/raw/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins_test_LiquidityMigration.t.sol.gz` | 4,695 | 534 lines (decompressed) | `d9a0f7e8eb98c074d269ac97115d43d816292fda5c3920a0177f0fb52b7fdf02` | committed |

**hook-docs/text/**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `hook-docs/text/clanker.gitbook.io_documentation_general_token-deployments.txt` | 5,656 | 77 lines | `cf53cd6d3205ffe3450bf629855214c2d3d0046a77c6cbadf7241732ba969d4d` | committed |
| `hook-docs/text/clanker.gitbook.io_documentation_references_core-contracts.txt` | 3,588 | 60 lines | `2e94812df9b19de318678e67b12b49069d6be8073896129f173b2cbc4b214ee0` | committed |
| `hook-docs/text/clanker.gitbook.io_documentation_references_deployed-contracts.txt` | 11,507 | 343 lines | `248b4d42f9bcee87ade697cd52c94b127e697b7915c05dd7d2e48aa57d3bd8d3` | committed |
| `hook-docs/text/docs.doppler.lol_advanced-features_doppler-hooks.txt` | 4,046 | 78 lines | `d388bced8b5cb3759da2c423923843fcdf997cd1d5f44bfa451aa10974a57988` | committed |
| `hook-docs/text/docs.doppler.lol_reference_contract-addresses.txt` | 46,840 | 684 lines | `622a19f617a9df68eac6a3082e864d489bd593efaf43e964a1784b81eb756dbe` | committed |
| `hook-docs/text/docs.uniswap.org_contracts_v4_deployments.txt` | 940 | 27 lines | `a6cdfba4ab29e3b3aa861ca6072aa403e5ab6427051765ccc7d245415bdab468` | committed |
| `hook-docs/text/docs.zora.co_changelogs_coins.txt` | 21,054 | 426 lines | `1dda3969cb7d764145410498f16bd5ab114bf4fecaefe66bfb5252fa71c5ab56` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_architecture.txt` | 4,656 | 93 lines | `bcde8ce5a6532c8baa2ba88bff5ab30b8404f437108cfde23b1366be1efefe84` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_creating-a-coin.txt` | 14,096 | 360 lines | `767226f001e68a21c017bf8e3d00a23be11a97d26665ffed28fe85a9ebc1845f` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_factory.txt` | 14,088 | 360 lines | `519433f80ac943ad61f46bdd1df96c4fe7d065ac3786be0e01a1732d02416cf9` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_hook-registry.txt` | 3,133 | 71 lines | `14f300c5329dcb3f14523c925c8fcafaf179eee1ef146b3513e07a2dc4246950` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_hook.txt` | 11,340 | 232 lines | `e17532922603157c888ec70370e3fa917e06c4d1a2d42a07571641e8aec7377f` | committed |
| `hook-docs/text/docs.zora.co_coins_contracts_liquidity-migration.txt` | 3,521 | 50 lines | `ebf181d5beb9468c7d35df777320be9b35bb12f7d8c51df6e20f9e6cdcd8d516` | committed |
| `hook-docs/text/docs.zora.co_llms.txt.txt` | 4,537 | 45 lines | `8d9e9dcaaab2c27eba5cf853f0fd1c8684b2168b4bf458039601813f85e7c190` | committed |
| `hook-docs/text/raw.githubusercontent.com_Bunniapp_bunni-v2_main_README.md.txt` | 5,565 | 119 lines | `4d514f1d709c81dd90377d28bc4a257a1fa67812d2fea7b71b513251b48a4dea` | committed |
| `hook-docs/text/raw.githubusercontent.com_KyberNetwork_kyberswap-dex-lib_0867b088e490608f731e4e37eaf49ea72e7846b3_pkg_liquidity-source_uniswap_v4_hooks_clanker_constant.go.txt` | 3,132 | 76 lines | `f0431e7f70f5b865038152cce6dc34ed14ff6cd1695e26248b170b90088fb63d` | committed |
| `hook-docs/text/raw.githubusercontent.com_KyberNetwork_kyberswap-dex-lib_0867b088e490608f731e4e37eaf49ea72e7846b3_pkg_liquidity-source_uniswap_v4_hooks_flaunch_constant.go.txt` | 2,798 | 65 lines | `b06fafa5f1ca0ebc2ab24c45345dba02eeb965ca68dd4d740e73ee836c9401f4` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_docs_main_content_protocols_v4_deployments.mdx.txt` | 54,011 | 331 lines | `a2e43f461248144c8fe07c0cbfe735ce661fba30bd18df37a2aafc76a89b1e7f` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_hooklist_main_README.md.txt` | 2,526 | 55 lines | `4afc061dacfaeaa7cb9c09d9eb60651bcbc939aa8ab0b2aa79869596e0cf0a90` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_routing-api_main_lib_util_hooksAddressesAllowlist.ts.txt` | 24,945 | 399 lines | `1f6086a5f4f7cca3bc12cec64ecf52ec12fc0591377c7f9bc59b938ea7b442fe` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_PoolManager.sol.txt` | 17,751 | 399 lines | `0f60b39dc3077e8b09a4c31ce5424588aaed4e46dc8d104ce12a74bbe165211c` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_interfaces_IPoolManager.sol.txt` | 12,985 | 221 lines | `5852673b416fe14d5d0d82870dc31866ec4557506961f8482b9d964b650f4bc3` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_Hooks.sol.txt` | 16,653 | 344 lines | `fbcd5dfa74ea34bd5496303c3d9098b1991f4782b99301f6cd49fc6a5da019b9` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_LPFeeLibrary.sol.txt` | 3,745 | 83 lines | `a9c746f47b3b03b6aad245628518135e09d326f7e63277c60ce7d7cbdaef9c00` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_libraries_ProtocolFeeLibrary.sol.txt` | 2,268 | 51 lines | `e4ee98b0069d5d044d47876e99015bfc81dbca271b96d4568cd5cec0ee517ace` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-core_main_src_types_PoolId.sol.txt` | 678 | 21 lines | `a2355b5848541aed9f35473e38a3dff9517daead9c7de0d56a2ee25669d439fb` | committed |
| `hook-docs/text/raw.githubusercontent.com_Uniswap_v4-periphery_main_src_lens_StateView.sol.txt` | 3,951 | 113 lines | `3139c570cf5ae668bebf788cd99d7fecd4ff3ac7b9f0aff8124d67ba49851e53` | committed |
| `hook-docs/text/raw.githubusercontent.com_clanker-devco_DOCS_main_references_deployed-contracts.md.txt` | 12,859 | 320 lines | `2a3394481fc401a11e7b8f4cbc8bba7088af9ee6f3fa68a9ac93886ed6b47401` | committed |
| `hook-docs/text/raw.githubusercontent.com_clanker-devco_clanker-sdk_main_src_utils_clankers.ts.txt` | 13,729 | 396 lines | `dbc22a5443855686c2e507771f92e4af6c0f0b74c6d525ae843c94316caf1fda` | committed |
| `hook-docs/text/raw.githubusercontent.com_clanker-devco_v4-contracts_main_README.md.txt` | 12,481 | 180 lines | `9aad7ad68e6706b059b16edc1c22a758a28308452f400a0e59700429dc426259` | committed |
| `hook-docs/text/raw.githubusercontent.com_flayerlabs_flaunch-gitbook_main_readme_for-aggregators.md.txt` | 9,790 | 227 lines | `0ad60bf57fdf0a3552a28343426bb8f8d4dc04996dd0ac181ccb7837f3c0b890` | committed |
| `hook-docs/text/raw.githubusercontent.com_flayerlabs_flaunch-sdk_bef27f90b946a63fe3c215a409b487ad38b1c685_src_addresses.ts.txt` | 38,076 | 770 lines | `77ac892abd2fb8e33cee6980f64690dc27d3c60d4a419429c35fa4d52c700352` | committed |
| `hook-docs/text/raw.githubusercontent.com_flayerlabs_flaunch-sdk_main_src_addresses.ts.txt` | 156 | 5 lines | `65446194a8d1d557af2a6fc783a179cc6e181a10b0f5d73a66e2e28152cf1a0a` | committed |
| `hook-docs/text/raw.githubusercontent.com_flayerlabs_flaunchgg-contracts_main_README.md.txt` | 18,448 | 157 lines | `9351c0b27241103de8e37c900e710eb5234bb415469a65aa05a11c9ec5f1ab03` | committed |
| `hook-docs/text/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins-deployments_.github_PR_TEMPLATE_UPGRADE_INSTRUCTIONS.md.txt` | 6,294 | 144 lines | `af7223679640f7cf5c214d9eb976ec5c08f27fc10a482fdae5ba54e5f0ae252c` | committed |
| `hook-docs/text/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins_src_deployment_ForkedCoinsAddresses.sol.txt` | 2,450 | 58 lines | `7647d27391d895d2f7458b76ac898c7ecf21f478abeb75b882bdffac1f937f19` | committed |
| `hook-docs/text/raw.githubusercontent.com_ourzora_zora-protocol_main_packages_coins_test_LiquidityMigration.t.sol.txt` | 24,730 | 538 lines | `ba90e926ad9e19df5086033af622d86d79b64ad002f35e58acfc5db30f4caf41` | committed |

**collect/ (scripts and logs)**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `collect/build_hooks_csv.log` | 89 | 1 line | `1b643e26f8372633ffa5108f6ca2043f6b09dfae3cda21704406c84c7e69b89b` | committed |
| `collect/build_hooks_csv.py` | 7,405 | 120 lines | `2186f4e99229ef406e28421dde62855e3bed5aab3f41ba1fd670da19601b1746` | committed |
| `collect/common.py` | 16,747 | 407 lines | `d7f5ce6cb625422088bc550155e44a90f6a5e2159aac92c31b170759ffe9241c` | committed |
| `collect/compact_initialize.log` | 1,355 | 16 lines | `4a08cb9791329048a08e1d8d968e60fdecfb498a802f99315f744c5fa619dc32` | committed |
| `collect/compact_initialize.py` | 5,271 | 95 lines | `b99fd2735f02ffc17c76fbb4b65812e4879e306320870a283f02ecd62e71b580` | committed (9c8a37c). Corrected row (2026-10-01 fixup): previously 5,089 bytes, 94 lines, sha256 `f3050bab42c5d49245d55df46bf52baf3658b9f165fa4d1914020dbca4940869`, the version before the gzip-trailer fix |
| `collect/expand_initialize.py` | 2,771 | 43 lines | `2c156b1ac052c24796a463c11fa7a415547955d5e02415959987c55e9619d336` | committed |
| `collect/fetch_docs.log` | 4,182 | 38 lines | `00bc518b3e689d74a799c21094aad388592b9968eb9cd471adf28828b04e2e6d` | committed |
| `collect/fetch_docs.py` | 9,706 | 190 lines | `e0b55391931123ed22d25266e50092dba301568a9ad995938c9c4a832c22a3a9` | committed |
| `collect/find_deploy_block.log` | 601 | 4 lines | `d7547a540685d8cf627e0953ac23d99b80b4182501f76067f4c7051f5a647ede` | committed |
| `collect/find_deploy_block.py` | 2,397 | 46 lines | `7de2ba039befa05df1397d1c46bbf753bcd7ac88b39bc6921469949dc890f587` | committed |
| `collect/hook_blockscout.log` | 24,113 | 213 lines | `b77c8b1e656d1000d6841942248e86319097aa33a5e41eb689336ef561670a9c` | committed |
| `collect/hook_blockscout.py` | 3,667 | 56 lines | `46af86a4db686cf7eb843d93f922b5efa6b87a17edc953a764f341f9cf6876a2` | committed |
| `collect/hook_counts.py` | 1,641 | 30 lines | `8fe1dd8eb5f369163ca181bed2d0c14f4020ce392096a45523fba0c00487d66a` | committed |
| `collect/hooks_pipeline.log` | 573 | 6 lines | `bd5234acc5005e9514a7e324cdb27b857d6e3814b5d880bd210e296fe9c867f1` | committed |
| `collect/hooks_pipeline.sh` | 1,239 | 13 lines | `845c98552813a1da3033269e679a753a83925716fc87e0c9ac29cbf5d31bf7b1` | committed |
| `collect/hooks_pipeline_resume.sh` | 1,925 | 17 lines | `1f29d76aef0ddcd28b2a12419753a9021935939ca7002defb0fb34aabd0d10b4` | committed |
| `collect/launch_tx_samples.log` | 2,935 | 42 lines | `09cd3de3e8ecb8a32bcd2a229184af8a6cd382f532b76a99f868cb4d768d9a16` | committed |
| `collect/launch_tx_samples.oom-version.py.txt` | 6,729 | 146 lines | `8f40917c10aa725d90176bfaa2a005813a6b6707a72f01e0f433c02762b9796a` | committed |
| `collect/launch_tx_samples.py` | 14,908 | 318 lines | `5851988bdfdaaa4c895bf9e2e9fc34f515ea0623cc9132d0f242ebb5879a6314` | committed |
| `collect/multicall.py` | 3,486 | 101 lines | `666651eb3055af42bd8248fa8494ed0b2ba86ae4bc0af1492e36cfc073f039b2` | committed |
| `collect/smoke_v4recent.log` | 37,486 | 46 lines | `e6b5dbc12c753cdcc5d3afc298209123a63c6f174722a727f62482e9d2db268c` | committed |
| `collect/uniswap_hooklist.log` | 87 | 1 line | `895537cf5d722d44c531ca15163c244d14b353c2b0e251111b473cee2a9f361d` | committed |
| `collect/uniswap_hooklist.py` | 1,575 | 21 lines | `08fd32cc46f0bba42bd735ec341f9cc50b0b2e7c92fcaa75e4d6343377cdc95c` | committed |
| `collect/v4init.log` | 7,243 | 28 lines | `fd9c8d0b880e541ad0448246279167e29e87b39c563606513822914bc3c8fbac` | committed |
| `collect/v4init.run1.log` | 4,622 | 15 lines | `daa8f603095dbeda6daa155dc8bde2552a876aff730a1d7e1b0f80404c0fd81e` | committed |
| `collect/v4init_collector.py` | 11,372 | 266 lines | `9510e338bf56f170ab72d3cbe3545738b6fef0c1095200e5fa195f7827c42ec1` | committed |
| `collect/v4recent.log` | 1,415 | 14 lines | `9fe42f798131097c56d61c9048eb75cef49edb149a660211cbba813a09363046` | committed |
| `collect/v4recent.run1.log` | 3,592 | 15 lines | `11c48e7e52cc9f4e0659068f48fef2f65443e43213e5167ca3242850d034f1ac` | committed |
| `collect/v4recent_collector.py` | 26,338 | 579 lines | `b5b99cba3c06b9153584d9d6e4029dacad026d7895446fb1ef264e12a53e98c7` | committed |
| `collect/verify_launch_tx_selection.log` | 125 | 1 line | `3234effcd16095037b52638197ba927d7c851f0074b61c881e654f4a5610c4a9` | committed |
| `collect/verify_launch_tx_selection.py` | 2,572 | 51 lines | `1c50990a7e7cc39811e84c8799cc22ae1f1a7b1e58cc83992b71c25b031b4b6e` | committed |
| `collect/verify_timestamps.log` | 914 | 15 lines | `cd09e801dad8ef94fede4400adeedfe4e22b830361b297fd994b8107531dfa55` | committed |
| `collect/verify_timestamps.py` | 1,463 | 24 lines | `4ee89ad726c4999098d6bee7c9d845dfafd9f81330ca1d256e3eca5b79c2bb78` | committed |
| `collect/write_hook_pool_counts.py` | 1,003 | 14 lines | `a1f02761279648b3c29ae3586aae911d3186423b8373bfda99ecc0f39eec070e` | committed |
| `collect/zora_hook_registry.log` | 3,071 | 18 lines | `ed48eb38606bfb3460a27734535afffedc0a7317475eee52f8ab0235a8bc00f9` | committed |
| `collect/zora_hook_registry.py` | 3,045 | 40 lines | `e98b903ae9f11250f4afa10ba86a4857eea6faaecb03cfcc8b73f5e373c70033` | committed |

**collect/state/**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `collect/state/hook-counts-final.json` | 5,317,589 | JSON dict, parses | `e3a12edb0191c3f5e6602479fc5bd799567ef1305947901e9ce10cc8b617a8fc` | local-only (R6) |
| `collect/state/hooks-candidates-1.txt` | 3,397 | 79 lines | `8c3e557dd61589736fc6b80f07aaad1b8c2277fb358b8727d8d59de52ebb32aa` | local-only (R7) |
| `collect/state/hooks-candidates-2.txt` | 5,762 | 134 lines | `34f55cf17486b899e51d6b0e4e283d3eb32844f965d8b5fa4516a749dbdcf7f1` | local-only (R7) |
| `collect/state/hooks-candidates-all.txt` | 9,159 | 213 lines | `b5a482fa8fdf1ff05870f838320d999e2d50db8480113c86e33695fc7bb30e3f` | local-only (R7) |
| `collect/state/launch-tx-samples-selection.json` | 143,766 | JSON dict, parses | `7c32f2ef6e02c238d7c2acb0e07f6271462e7458344e89fd28fc2112e5a8e870` | local-only (R8) |
| `collect/state/v4init-pin.json` | 332 | JSON dict, parses | `5c1e1efe0162575cd32386ce89e945423cfe1a28c6f656c3a07837de8875254d` | local-only (R4) |
| `collect/state/v4recent-pin.json` | 320 | JSON dict, parses | `38fdc61d6e3cc2c094db15b3c016c607775613179b8e2d6317f04b393c85ace2` | local-only (R4) |
| `collect/state/v4state-keys.json` | 12,576,047 | JSON dict, parses | `9fb374ca3a7e129e00011727204055ee631edf044faa6fb1ca5fac8f9279a462` | local-only (R5) |
| `collect/state/v4state-meta.json` | 21,548,875 | JSON dict, parses | `d8876b5e15b119a6084ee5a504b36f13c0cf08f1b44e35470fb5ab2adc678a9e` | local-only (R5) |
| `collect/state/v4state-slot0.json` | 5,525,752 | JSON dict, parses | `b3e5d55fe3a999d926dfdbf2c841c603c8a07c5b1d1356d100a71bc0465b6c87` | local-only (R5) |

**collect/work/ (single files)**

| file | bytes | rows / lines | sha256 | git |
|---|---|---|---|---|
| `collect/work/launch_tx_cache.jsonl` | 9,152,447 | 626 lines (JSON, all parse) | `c150d640ce968beb355f744db9fe92422d229f6b48f1c8410dc040265833a3d2` | local-only (R8) |

**Grouped directories** (one row per group; "group digest" = `sha256` of the output of `find <dir> -type f -name '<pattern>' | LC_ALL=C sort | xargs sha256sum`, run in `research-material/01-v4-pools/`)

| files (dir, pattern) | count | bytes (total) | rows / lines | group digest | git |
|---|---|---|---|---|---|
| `hook-docs/blockscout/` `0x*.address.json.gz` | 1,859 | 1,192,596 | each file one JSON object (url, fetched_utc, http_status, body); all parse | `89e2cf31f2d2b34c7b137ad6c607e4522a091511e6f1da83493d30172dbd3c79` | committed |
| `hook-docs/blockscout/` `0x*.creation_tx.json.gz` | 150 | 1,532,896 | each file one JSON object; all parse | `edd41a03f8100f263b0b922dad1db4cde71efeb187433d20fe6dbb15752f2154` | committed |
| `hook-docs/blockscout/` `0x*.smart_contract.json.gz` | 923 | 39,321,443 | each file one JSON object; all parse | `8ca43c924e09723fc53aa3b75dde71e8c8e92ab045eada78de999a44fbb4d8c3` | committed |
| `hook-docs/blockscout/` `0x*` | 2,932 | 42,046,935 | all three kinds above together | `2449d10c9766b7a5a37e5556d1b0669a38d27eeda5d8ea85e6b1510e885874b8` | committed |
| `collect/work/v4init/` `c_*.csv.gz` | 13,328 | 1,828,320,373 | 15,333,247 lines in total (no header line in these files) | `a7a249982e43f730e65928d5bbc5daccb0c1aa220d9233b2914f677dcf9ecd5c` | local-only (R2) |
| `collect/work/v4recent/` `act_*.csv.gz` | 173 | 57,021,334 | 754,670 lines in total (no header line in these files) | `4b84ebca4e8b671339d0b7cdfe5df2ca91ac0ea565c2107beead392ff463f394` | local-only (R3) |
| `collect/work/v4recent/` `init_*.csv.gz` | 152 | 3,950,419 | 29,900 lines in total (no header line in these files) | `a6e41003a0a6ee408513c8f7ca1759af443a2b605f582eb7e24f333f0fc16cd6` | local-only (R3) |
| `collect/work/v4recent/` `*` | 325 | 60,971,753 | act + init together | `c17ef81524b3008b1f91bdb3f8e67835737b28ac96b71e1f213753b1dc422e74` | local-only (R3) |
| `collect/__pycache__/` `*.pyc` | 5 | 76,892 | compiled Python bytecode | `794b582c80d3d7d98c896918bbbf804925034d8c8c722b5722fa20628585a4f2` | local-only (R9) |

## V4WINDOW2 (2026-10-01): PoolManager logs for blocks 52,006,433-52,017,160 and snapshot at block 52,017,008

Added by a later collection pass to close a completeness gap: the span after the V4RECENT 24 h activity window, up to the end
of the Base block census, was not covered by any Uniswap V4 log file in this folder. That span contains the shallow-pool live
test and the valid V4 live test (blocks 52,016,408-52,017,008, 2026-10-01T02:36:03Z to 02:56:03Z; see `../02-v4-live-test/`
and `../04-shallow-pools/`). Raw data only; nothing below interprets it.

Sentinel: `.sentinels/V4WINDOW2.DONE` (2026-10-01T03:57:28Z). Script: `collect/v4window2_collector.py`. Logs:
`collect/v4window2.log` (full run), `collect/smoke_v4window2.log` (smoke test), `collect/v4window2_consistency.log`
(read-only checks by `collect/v4window2_consistency.py`). One run from 03:55:24Z to 03:57:28Z, with no restart and no
chunk-level failure. Request-level retries are not logged.

### Window and pinned blocks

| item | value | source |
|---|---|---|
| first block (W0) | 52,006,433 (2026-09-30T21:03:33Z) | `recent-parts.json` `pin.pinned_block` (52,006,432) + 1, so the window starts right after the V4RECENT activity window |
| last block (W1) | 52,017,160 (2026-10-01T03:01:07Z) | `.sentinels/BASE_CENSUS.DONE` `summary.range_last_block` (last block of `../05-base-onchain/`) |
| blocks | 10,728, inclusive | |
| snapshot block (S) | 52,017,008 (2026-10-01T02:56:03Z) | the last block of the valid V4 live test, as specified for this pass |
| chain state at start | head 52,018,788, `finalized` block 52,018,149 (Tenderly, 03:55:24Z); W1 was below the finalized block | `collect/state/v4window2-run.json` (local-only); also the first line of `collect/v4window2.log` |

The window is a constant in the script (no head pin), so a rerun covers the same blocks. Timestamps follow
`timestamp = 1686789347 + 2 * block_number` (see "Block and time conventions").

### Method (logs)

- The window is split into 11 chunks of 1,000 blocks aligned at W0; the last chunk (52,016,433-52,017,160) has 728 blocks.
- Per chunk, two `eth_getLogs` queries with `address` = PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b`:
  - topics `[[Swap, ModifyLiquidity, Donate]]`, sent as 250-block sub-requests (the same 250-block size V4RECENT used);
  - topic0 = Initialize, one request over the whole chunk.
- `common.get_logs_range` is reused unchanged: bisection on range or size errors, any response with at least 5,000 logs
  re-fetched as two halves, every log checked for block inside the requested range and `removed == false`. Counted from the
  output, the largest 250-block sub-range holds 4,004 logs, below the 5,000-log re-fetch threshold. Request-level retries and
  bisections on range errors inside `get_logs_range` are not logged, so the log files cannot show whether any happened.
- Decoding reuses the V4RECENT code unchanged: `common.decode_activity` for Swap/ModifyLiquidity/Donate (with the same
  de-duplication on (block_number, log_index) and the same sort as `v4recent_collector.fetch_act`), and
  `v4init_collector.decode_chunk` for Initialize. decode_chunk checks `pool_id == keccak256(abi.encode(PoolKey))` on every row.
  The output columns are therefore identical to `v4-swap-part-0001.csv.gz`, `v4-modify-liquidity-part-0001.csv.gz`,
  `v4-donate-part-0001.csv.gz` and `v4-initialize-7d-part-0001.csv.gz`.
- Primary endpoint: gateway.tenderly.co/public/base (at most 2 requests in flight). The script falls back to mainnet.base.org,
  then developer-access-mainnet.base.org, if a chunk fails. No fallback was needed: Tenderly served all 11 chunks on the first
  attempt.
- Cross-check: each of the 11 chunks was fetched a second time from mainnet.base.org (2,000-block limit; same 250-block
  sub-requests, at most 2 in flight) and decoded the same way. For all 11 chunks the decoded rows of all four event types were
  identical, and so were the `blockHash` values of every block with a log.
- Smoke test before the run (`collect/smoke_v4window2.log`): blocks 52,016,961-52,017,160 from Tenderly and mainnet.base.org
  gave identical rows (1,186 Swap, 460 ModifyLiquidity, 0 Donate, 6 Initialize) and identical block hashes. One Swap log
  (tx `0x2b0536050759437cc96df0d5b90b6948e0cdcdb121d4ea891c7bc1eb9bcf7f0e`, log index 71) was decoded by hand with
  `cast decode-abi "f(int128,int128,uint160,uint128,int24,uint24)"` from its receipt; all six values equal the decoder output.
- Gaps: none. Every chunk has a primary fetch and an identical cross-check, and the chunks are contiguous from W0 to W1. No
  `collect/state/v4window2-gaps.json` exists; the script writes it, and `V4WINDOW2.FAILED`, only if a chunk is missing or its
  cross-check differs.

Per-chunk endpoints (also in `v4-window2-parts.json` `chunks[]`, with fetch times):

| chunk (blocks) | primary endpoint | Swap | ModifyLiquidity | Donate | Initialize | cross-check endpoint | cross-check |
|---|---|---|---|---|---|---|---|
| 52,006,433-52,007,432 | tenderly | 8,576 | 3,722 | 2 | 109 | mainnet.base.org | identical |
| 52,007,433-52,008,432 | tenderly | 10,398 | 4,312 | 0 | 133 | mainnet.base.org | identical |
| 52,008,433-52,009,432 | tenderly | 9,597 | 3,723 | 2 | 96 | mainnet.base.org | identical |
| 52,009,433-52,010,432 | tenderly | 7,497 | 3,139 | 1 | 70 | mainnet.base.org | identical |
| 52,010,433-52,011,432 | tenderly | 6,199 | 3,233 | 3 | 82 | mainnet.base.org | identical |
| 52,011,433-52,012,432 | tenderly | 6,419 | 3,975 | 3 | 93 | mainnet.base.org | identical |
| 52,012,433-52,013,432 | tenderly | 5,931 | 3,794 | 1 | 68 | mainnet.base.org | identical |
| 52,013,433-52,014,432 | tenderly | 6,409 | 3,829 | 1 | 75 | mainnet.base.org | identical |
| 52,014,433-52,015,432 | tenderly | 6,445 | 3,107 | 1 | 107 | mainnet.base.org | identical |
| 52,015,433-52,016,432 | tenderly | 7,055 | 3,345 | 1 | 75 | mainnet.base.org | identical |
| 52,016,433-52,017,160 | tenderly | 4,598 | 2,773 | 0 | 57 | mainnet.base.org | identical |

### Consistency checks against other folders (descriptive; no data file was changed)

Results are in `v4-window2-parts.json` `census_consistency` and in `collect/v4window2_consistency.log`.
- **Block hashes.** The 10,595 blocks that have at least one of these logs were compared with `block_hash` in
  `../05-base-onchain/blocks.csv.gz`. All 10,595 are equal, 0 differ and 0 are missing from the census.
- **Transactions.** The 58,372 distinct (block_number, tx_index) pairs in the four log files were looked up in
  `../05-base-onchain/data/txs-*.csv.gz`. All 58,372 are present with the same tx_hash, and all have census `status` 1.
- **Initialize top-up of 02-v4-live-test.** On blocks 52,006,433-52,015,481, the overlap with
  `../02-v4-live-test/initialize-topup.csv.gz`, both files hold 840 rows with the same header. The (block_number, log_index)
  sets are the same, and 0 rows differ in any of the 27 columns.
- **Adjacency.** The V4RECENT activity parts end at block 52,006,432 (`recent-parts.json`), and window 2 starts at 52,006,433.
- **Snapshot against the logs.** Pools whose last Swap in the window is at or before block 52,017,008, or that have no Swap but
  were initialized in the window at or before that block, were compared with the `getSlot0` result at 52,017,008. Each pool was
  compared on the `sqrt_price_x96` and `tick` of that last Swap (3,841 pools) or Initialize (602 pools). All 4,443 pools are
  equal on both values, and 0 differ. The other 359 snapshot pools were not compared, because they have no Swap and no
  Initialize in the window at or before S. Their window events at or before S are ModifyLiquidity/Donate only, or all their
  window events come after S; the 6 pools initialized after S are among them.

### Method (snapshot, pool keys, token metadata)

- **Pool set.** Every pool_id in any of the four window-2 log files: 4,802 pools. 4,794 have a Swap, ModifyLiquidity or
  Donate in the window, and 965 have their Initialize in the window. 957 pools have both, 3,837 have only activity and 8 have
  only an Initialize.
- **State.** `v4recent_collector.snapshot_state` is reused unchanged. It calls `StateView.getSlot0(poolId)` and
  `getLiquidity(poolId)` through Multicall3 `aggregate3` (allowFailure, 250 pools = 500 calls per eth_call, 3 parallel
  batches) at blockTag 52,017,008. It tries base-mainnet.public.blastapi.io, developer-access-mainnet.base.org, base.drpc.org
  and gateway.tenderly.co/public/base in random order, with at most 1 request in flight per endpoint. A failed item is retried
  as a direct eth_call. `slot0_ok` = 1 and `liquidity_ok` = 1 on all 4,802 rows. As in V4STATE, the file does not record
  whether a value came from the multicall or from the direct-call retry.
- **Pool keys.** Resolved for all 4,802 pools from Initialize logs only, in this order:
  1. the window-2 Initialize rows (965, `key_source` = `initialize_log_window2`);
  2. `pool-keys-snapshot.csv.gz` (2,305 rows, copied with their `key_source`: 697 `initialize_log_7d`, 1,608 `initialize_log_v4init`);
  3. a streaming scan of the local V4INIT originals `initialize-part-0001..0022.csv.gz` (1,532 rows, `initialize_log_v4init`).
  In a fresh clone, where the originals are absent, the script reads `initialize-compact/` through
  `expand_initialize.iter_rows()` instead. That fallback was checked for import and for its first row, but was not run in full.

  Every key was re-checked with `keccak256(abi.encode(currency0, currency1, fee, tickSpacing, hooks)) == pool_id`. There were
  0 mismatches and 0 unresolved pools.
- **Token metadata.** The 4,802 keys contain 3,676 distinct currencies: native ETH (`0x000…000`), 1,751 addresses already in
  `token-metadata.csv.gz`, and 1,924 new addresses. Only the 1,924 new addresses were queried, with
  `v4recent_collector.token_metadata` unchanged: `symbol()`, `name()`, `decimals()` and `totalSupply()` in Multicall3 batches of
  100 tokens, with a retry multicall of failed items and a direct eth_call for items still failing. The call block was
  52,017,008.

  When all four calls for an address return success with empty return data, the script reads `eth_getCode` at 52,017,008. If
  there is no code at that block, it calls the four functions again at W1 = 52,017,160. This happened for 5 addresses; each had
  no code at 52,017,008 (getCode on blastapi):
  - `0x2929843e25beee024173e0f1d033b2714cc42bdc`
  - `0x349a345b126b9435e949e368b7a3cdfc285e9106`
  - `0x87aa4de41c1ee8a6b6697899137b18456e0f8b07`
  - `0x96588176b8c74fd7f6005f7206bd15ab53446680`
  - `0xe9551896c2b105ca41078da76fbd7590ce70da5a`

  These 5 rows carry `call_block` 52,017,160, and the other 1,919 carry 52,017,008. In the final file all 1,924 x 4 calls have
  `_ok` = 1 and `_call_mode` = `multicall`, and no row has an empty return on all four calls. The file has no native row,
  because the native row is already in `token-metadata.csv.gz`.

### File schemas (V4WINDOW2)

| file | columns |
|---|---|
| `v4-window2-swap-part-NNNN.csv.gz` | identical to `v4-swap-part-NNNN.csv.gz` (12 columns: block_number, tx_hash, tx_index, log_index, pool_id, sender, amount0, amount1, sqrt_price_x96, liquidity, tick, fee); all raw |
| `v4-window2-modify-liquidity-part-NNNN.csv.gz` | identical to `v4-modify-liquidity-part-NNNN.csv.gz` (10 columns); all raw |
| `v4-window2-donate-part-NNNN.csv.gz` | identical to `v4-donate-part-NNNN.csv.gz` (8 columns); all raw |
| `v4-window2-initialize-part-NNNN.csv.gz` | identical to `v4-initialize-7d-part-NNNN.csv.gz` / `initialize-part-NNNN.csv.gz` (27 columns; `dynamic_fee` and the 14 `hf_*` columns are derived as described there) |
| `v4-window2-state-snapshot.csv.gz` | the same 11 columns in the same order as `state-snapshot.csv.gz`, with columns 2 and 3 renamed to fit this window: pool_id, **active_window2** (1 if the pool has any Swap/ModifyLiquidity/Donate in 52,006,433-52,017,160), **initialized_window2** (1 if its Initialize is in 52,006,433-52,017,160), snapshot_block (52017008), slot0_ok, sqrt_price_x96, tick, protocol_fee, lp_fee, liquidity_ok, liquidity. Decoding is as for `state-snapshot.csv.gz` (derived, lossless) |
| `v4-window2-pool-keys.csv.gz` | identical to `pool-keys-snapshot.csv.gz` (pool_id, currency0, currency1, fee_raw, tick_spacing, hooks, init_block, key_source). The key_source values used are `initialize_log_window2` (new: from `v4-window2-initialize-part-0001.csv.gz`), `initialize_log_7d` and `initialize_log_v4init`. `position_manager_poolKeys_at_snapshot` and `unresolved` do not occur. One row per pool of the window-2 snapshot |
| `v4-window2-token-metadata.csv.gz` | the 22 columns of `token-metadata.csv.gz` in the same order and with the same meaning, plus a trailing column **call_block**: the block at which the four calls were made (52017008, or 52017160 for the 5 addresses above). One row per currency of the window-2 pools that is not an address in `token-metadata.csv.gz`; `is_native` is 0 on every row |
| `v4-window2-parts.json` | dataset, pool_manager, window (block_from, block_to, blocks, sources, utc_from, utc_to), topics, rows, columns, parts{swap, modify_liquidity, donate, initialize}[] (file, rows, block_from, block_to, bytes, sha256), chunks[] (from, to, endpoint, endpoint_url, rows, fetched_utc, act_subrequest_blocks 250, init_request_blocks 1000, failed_attempts_before, xcheck_endpoint, xcheck_identical, xcheck_utc), gaps ([]), census_consistency, sort, assembled_utc |
| `v4-window2-state-index.json` | snapshot_block, window, pool counts (pools, pools_active_window2, pools_initialized_window2, pools_initialized_after_snapshot_block), keys (counts per source, unresolved), currency and token counts, token_recall_checks (the 5 getCode results), files, columns, call_endpoints, completed_utc |

General conventions are those of "File schemas" above. Rows are sorted by (block_number, log_index); hex is lowercase 0x;
integers are base-10 strings; amounts are raw base units. Note from the existing schema: StateView returns zeros (success) for a
pool id that does not exist. The 6 pools whose Initialize is in blocks 52,017,009-52,017,160 (after S) have
`sqrt_price_x96` = 0, `tick` = 0, `protocol_fee` = 0, `lp_fee` = 0 and `liquidity` = 0 in the snapshot.

### Row counts and files (V4WINDOW2; each re-read after writing, all `.gz` pass `gzip -t`)

| file | bytes | rows | block range of rows | sha256 | git |
|---|---|---|---|---|---|
| `v4-window2-swap-part-0001.csv.gz` | 7,482,392 | 79,124 | 52,006,433-52,017,160 | `305adfbcd6e41a5cc2df67207857a855d8fc2dd085944d7fb4c6c6050ec55e78` | committed |
| `v4-window2-modify-liquidity-part-0001.csv.gz` | 1,280,950 | 38,952 | 52,006,433-52,017,158 | `c4cb399dbf2ea068bd628abeb2d7af705775c9098b6bda0d1758ecc7620b36ec` | committed |
| `v4-window2-donate-part-0001.csv.gz` | 1,536 | 15 | 52,006,551-52,016,045 | `0fb57f21b3a9657920bcd07c16d36ef79ce7694b8225e630d12d013cd0707d0c` | committed |
| `v4-window2-initialize-part-0001.csv.gz` | 125,083 | 965 | 52,006,449-52,017,133 | `a3dfe58eb20c5b1094927e2c8a9becf8bfa5862b915c74acd399b7cae184c547` | committed |
| `v4-window2-state-snapshot.csv.gz` | 338,960 | 4,802 | block 52,017,008 | `b86d5d9a5d54418d481717aafac9fd9f66f9ca488529a5203c6eb0a5949ae5b3` | committed |
| `v4-window2-pool-keys.csv.gz` | 375,833 | 4,802 | | `3c9f6c9c78d9e56b8323a7958dd4cb45ee5e9e5e700ea73f8f406de4d009bef2` | committed |
| `v4-window2-token-metadata.csv.gz` | 134,007 | 1,924 | blocks 52,017,008 / 52,017,160 | `54cefccc07ca5c7a7726e19b5834ec256d1dc407a1efd2b728499d2d6e6d0e7b` | committed |
| `v4-window2-parts.json` | 9,501 | JSON, parses | | `a2c5104efb7ae41f5df8d95c9144de5cafb64881c0ed45116d3d81105a85d539` | committed |
| `v4-window2-state-index.json` | 2,575 | JSON, parses | | `b51e227b31aab3490eb5e5d3537165bd6f91b8aa544e8191c11399ff53ebd56e` | committed |
| `collect/v4window2_collector.py` | 30,451 | 568 lines | | `3a526b4fa18d922e134d84302a53a3f4a3707ccf1f005aa3a6c5b84fd86d3381` | committed |
| `collect/v4window2_consistency.py` | 4,188 | 87 lines | | `3ef5278bbc2bf08aea07f1b52a09f2c16665692576ca2f11ec4c4094412321fc` | committed |
| `collect/v4window2.log` | 4,576 | 33 lines | | `86bfe5c4de12294c7fd9ef24914fdc8d51e01be930f91923ae5238164e2fdc74` | committed |
| `collect/v4window2_consistency.log` | 653 | 3 lines | | `3bfc386bdb49ef16d596367a08ff905521b795c7151f65424b56f6a26695ecf8` | committed |
| `collect/smoke_v4window2.log` | 3,247 | 9 lines | | `79e4042f3977f87ff0ca58fbd717b74dada6b023b04c7b7383208ef41133d7a5` | committed |
| `collect/work/v4window2/` (`act_*`, `init_*` .csv.gz without header, `meta_*`, `xcheck_*` .json; 11 of each) | 9,765,136 total | 44 files | | | local-only (git-ignored) |
| `collect/state/v4window2-{run,slot0,keys,meta,recall}.json` | | 5 files | | | local-only (git-ignored) |

`collect/work/v4window2/meta_<from>_<to>.json` also stores the `blockHash` of every block with a log in the chunk. That is the
input of the block-hash check above, and it exists only locally; the check's result is in the committed `v4-window2-parts.json`.
Each data file is one part (the largest is 7.5 MB, far below the 85 MB rotation size). The sha256 values in
`v4-window2-parts.json` equal the table above.

### Reproduce (V4WINDOW2)

```
cd /home/user/dapparb/research-material/01-v4-pools/collect
export REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
python3 -u v4window2_collector.py --smoke > smoke_v4window2.log 2>&1      # optional; 200 blocks on both log endpoints + 20-pool snapshot; writes nothing under ..
setsid nohup python3 -u v4window2_collector.py > v4window2.log 2>&1 < /dev/null &   # resumable; skips chunks/checkpoints that exist
python3 v4window2_consistency.py > v4window2_consistency.log             # read-only checks (no RPC)
```
To fetch everything again, delete `collect/work/v4window2/` and `collect/state/v4window2-*.json`. The script refuses to run if
W1 is above the chain's `finalized` block.

### Coverage limits (V4WINDOW2)

- Only blocks 52,006,433-52,017,160. Activity after 52,017,160 and before 51,963,233 was not collected.
- One snapshot block, 52,017,008. Pools initialized after it (6) have all-zero state rows, because StateView returns zeros for
  pools that do not exist yet. Their keys and initial prices are in `v4-window2-initialize-part-0001.csv.gz` and
  `v4-window2-pool-keys.csv.gz`.
- The endpoint that answered each snapshot or metadata multicall batch was not recorded; the same holds for V4STATE.
- Currencies that are already in `token-metadata.csv.gz` were not queried again. Their metadata there is as of block
  52,006,432, and `totalSupply` may have changed since.
- As in V4STATE, nothing else was collected: no tick-level liquidity, no hook internal state, no transfer-tax or transfer-block
  probes, and no mempool data. Per-transaction gas and fee fields for these transactions are in `../05-base-onchain/data/txs-*`
  (the tx check above shows that every transaction of these logs is there).
- base.drpc.org and base-rpc.publicnode.com were not used for getLogs in this pass.

## Fixup (2026-10-01): compact-index.json and tx-hash-recovery-check.json

Manifest-only change by a fixup agent at ~05:00Z on 2026-10-01. No data file was changed and nothing was fetched.

- `initialize-compact/compact-index.json` was corrected by the main session on 2026-10-01 (commit 9c8a37c, 02:57:03Z):
  - `bytes` and `sha256` of every part were recomputed from the files on disk, and a key `index_correction` was added.
  - `collect/compact_initialize.py` was fixed to close the underlying file, which flushes the gzip trailer, before hashing.
  - The data files were not changed.
- Re-check done in this fixup, with Python `hashlib.sha256` and `os.path.getsize` over `initialize-compact/pools-part-0001..0008.csv.gz`:
  - For all 8 parts, `bytes` and `sha256` in `compact-index.json` equal the files on disk and the existing inventory rows.
  - `rows` sum to 15,333,247.
  - Every text in this manifest that said the index values were wrong now carries a correction note: status gap 2, the
    `initialize-compact/` table and "Cause of the wrong values", "Stable file layout", "Index files", and the inventory rows of
    `compact-index.json` and `collect/compact_initialize.py`.
  - New inventory values: `compact-index.json` is 3,904 bytes, sha256 `494c2463eddcb606123b093a2b23759ec3cfb50f39eb2deb585198df3d11e164`.
    `collect/compact_initialize.py` is 5,271 bytes, 95 lines, sha256 `b99fd2735f02ffc17c76fbb4b65812e4879e306320870a283f02ecd62e71b580`.
    Both equal their committed versions in 9c8a37c.
- `initialize-compact/tx-hash-recovery-check.json` (written 2026-09-30 21:56:49Z):
  - The main session wrote it with an inline script, which was not saved as a file.
  - The script took a 40-row sample of (block_number, tx_index) from the original Initialize rows and called
    `eth_getTransactionByBlockNumberAndIndex` on `https://base-mainnet.public.blastapi.io` for each row.
  - The file stores the method string, `checked` 40, `matched` 40 and the 40 returned rows. It does not say how the sample
    was drawn.
  - The 2026-10-01 documentation pass checked all 40 `tx_hash` values against the original rows: 40 of 40 equal.
