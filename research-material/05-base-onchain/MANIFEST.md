# 05-base-onchain: raw Base block census + RSR episode

Raw on-chain record of Base (chain id 8453) blocks: every transaction's receipt summary, every reverted transaction, and
full receipts/logs for transactions that match a swap-log / multi-token-transfer filter. It covers a contiguous block range
from about 6 hours before launch, forward through the two concurrent engine test runs (sentinels V4LIVE and SHALLOW_LIVE).
It also holds a one-off raw capture of Base blocks 51998755-51998758 (the "RSR" episode).

This file only maps the data. It contains no findings, rankings or conclusions.

<!-- AUTO-STATUS-BEGIN -->

**Status: COMPLETE** (written by collect/finalize.py at 2026-10-01T03:10:56Z)

```json
{
 "finalized_utc": "2026-10-01T03:10:56Z",
 "range_first_block": 51995609,
 "range_last_block": 52017160,
 "range_first_block_timestamp_utc": "2026-09-30T15:02:45Z",
 "range_last_block_timestamp_utc": "2026-10-01T03:01:07Z",
 "blocks_present": 21552,
 "blocks_expected": 21552,
 "missing_blocks": 0,
 "parent_hash_mismatches": 0,
 "txcount_mismatches": 0,
 "conflicting_duplicate_block_rows": 0,
 "oversize_files": [],
 "fw_stop_reason": "sentinels V4LIVE.* and SHALLOW_LIVE.* both present",
 "fw_stop_detected_utc": "2026-10-01T02:56:28Z",
 "fw_stop_block": 52017160,
 "gf_ran": true
}
```

| file | bytes | rows | min_block | max_block |
|---|---|---|---|---|
| blocks.csv.gz | 1251161 | 21552 | 51995609 | 52017160 |
| data/candidates-bf-0001.jsonl.gz | 89975717 | 76441 | 51995609 | 51998168 |
| data/candidates-bf-0002.jsonl.gz | 13046151 | 10537 | 51998169 | 51998608 |
| data/candidates-bf2-0001.jsonl.gz | 89469113 | 73724 | 52000000 | 52003079 |
| data/candidates-bf2-0002.jsonl.gz | 89615211 | 66992 | 52003080 | 52005799 |
| data/candidates-bf2-0003.jsonl.gz | 14738382 | 10984 | 52005800 | 52006399 |
| data/candidates-bf3-0001.jsonl.gz | 36328805 | 30655 | 51998800 | 51999999 |
| data/candidates-bf4-0001.jsonl.gz | 6054063 | 4782 | 51998609 | 51998799 |
| data/candidates-fw-0001.jsonl.gz | 89487257 | 69820 | 52006400 | 52010049 |
| data/candidates-fw-0002.jsonl.gz | 89390492 | 73318 | 52010050 | 52014129 |
| data/candidates-fw-0003.jsonl.gz | 72296298 | 63910 | 52014130 | 52017160 |
| data/candidates-gf1-0001.jsonl.gz | 48166 | 20 | 51998605 | 51998605 |
| data/provenance-bf-0001.csv.gz | 10500 | 2039 | 51996569 | 51998608 |
| data/provenance-bf2-0001.csv.gz | 35866 | 6400 | 52000000 | 52006399 |
| data/provenance-bf3-0001.csv.gz | 6737 | 1200 | 51998800 | 51999999 |
| data/provenance-bf4-0001.csv.gz | 1125 | 191 | 51998609 | 51998799 |
| data/provenance-fw-0001.csv.gz | 206251 | 10479 | 52006682 | 52017160 |
| data/provenance-gf1-0001.csv.gz | 137 | 1 | 51998605 | 51998605 |
| data/reverted-bf-0001.csv.gz | 5586973 | 75416 | 51995609 | 51998608 |
| data/reverted-bf2-0001.csv.gz | 9526923 | 150436 | 52000000 | 52006399 |
| data/reverted-bf3-0001.csv.gz | 2414348 | 36117 | 51998800 | 51999999 |
| data/reverted-bf4-0001.csv.gz | 391189 | 5828 | 51998609 | 51998799 |
| data/reverted-fw-0001.csv.gz | 15844055 | 249815 | 52006400 | 52017160 |
| data/reverted-gf1-0001.csv.gz | 1246 | 16 | 51998605 | 51998605 |
| data/txs-bf-0001.csv.gz | 68710314 | 849509 | 51995609 | 51998608 |
| data/txs-bf2-0001.csv.gz | 89183753 | 1136687 | 52000000 | 52005559 |
| data/txs-bf2-0002.csv.gz | 11671888 | 152007 | 52005560 | 52006399 |
| data/txs-bf3-0001.csv.gz | 22944030 | 288165 | 51998800 | 51999999 |
| data/txs-bf4-0001.csv.gz | 3502280 | 43633 | 51998609 | 51998799 |
| data/txs-fw-0001.csv.gz | 89187758 | 1132643 | 52006400 | 52012719 |
| data/txs-fw-0002.csv.gz | 62363641 | 810133 | 52012720 | 52017160 |
| data/txs-gf1-0001.csv.gz | 15894 | 185 | 51998605 | 51998605 |

<!-- AUTO-STATUS-END -->

## 1. Which question lines each file serves (mapping only)

The question lines are numbered as they appear in the user's text:

- Q1: "What is still unmeasured:" (heading)
- Q2: Uniswap V4 on Base / Clanker and Zora V4 pools with hooks / only 20 V4 pools
- Q3: Older V2 pairs (newest 6,000 of ~3M)
- Q4: Pools under 0.1 ETH liquidity / tokens that block or tax transfers
- Q5: Other chains, live
- Q6: "Would the gaps change the answer?" (heading)
- Q7: V4 launches / large short-lived gaps / most fought-over flow on Base / RSR trade: winner kept 3%, paid the rest as priority fee
- Q8: BSC ordering through private block builders
- Q9: Chain-wide studies: Arbitrum ~$4,700/day; Base 4,365 bots, 21.4M arbitrages over nine months, 28% profitable after failed transactions
- Q10: Closing: full Uniswap V4 coverage on Base; list every V4 pool from PoolManager creation events and rerun the 20-minute live test

| file(s) | serves |
|---|---|
| `blocks.csv.gz` (after finalize; before that `data/blocks-*-NNNN.csv.gz`) | Q7, Q9, Q10 (block base fee, timestamps, tx counts for ordering/fee context over the census window) |
| `data/txs-*-NNNN.csv.gz` | Q7, Q9, Q10 (every tx: sender, target, position, status, gas, effective gas price, L1 fee) |
| `data/reverted-*-NNNN.csv.gz` | Q7, Q9 (every failed tx included on-chain, with its gas and fees) |
| `data/candidates-*-NNNN.jsonl.gz` | Q2, Q3, Q4, Q7, Q9, Q10 (full receipts and all logs of multi-swap / multi-token txs. The logs include V4 PoolManager Swap logs (pool id in topic1), V2/V3/Aerodrome swap logs (pool address = emitter) and ERC-20 Transfer amounts) |
| `data/provenance-*-NNNN.csv.gz` | provenance only (which endpoint served each block) |
| `swap-topics.csv` | Q2, Q7, Q9 (defines criterion A; one real Base example log per topic) |
| `gaps.csv`, `gaps-final.csv`, `integrity.json`, `data/file_index.csv` | coverage metadata for all of the above |
| `rsr-episode/*` | Q7 (raw blocks, full tx objects, receipts, call traces and pool state around the RSR trade) |
| none | Q5, Q8 (this directory is Base only) |

The forward part of the census (`*-fw-*`) is timed to overlap the engine runs whose sentinels are
`V4LIVE.*` (Q2, Q10) and `SHALLOW_LIVE.*` (Q4). Blocks are aligned by block number and timestamp.

## 2. Sources and endpoints

| use | endpoint | method(s) |
|---|---|---|
| backfill, lower part (`bf`) | https://base.drpc.org (public, free plan) | `eth_getBlockReceipts(n)`, `eth_getBlockByNumber(n,false)`; `eth_getTransactionReceipt` per tx only as fallback |
| backfill, upper parts (`bf2`, `bf3`, `bf4`) | https://gateway.tenderly.co/public/base (<= 3 in-flight), fallback https://base-rpc.publicnode.com (1 in-flight, 1 req/s) | same |
| forward / head-following (`fw`) | https://base-rpc.publicnode.com (<= 2 req/s), fallback https://base.drpc.org (1 in-flight) | same, plus `eth_blockNumber` |
| gap fill (`gf1` at 21:49Z; final `gf` after fw ends, only for blocks still missing) | gateway.tenderly.co/public/base, then base.drpc.org (1 in-flight), then base-rpc.publicnode.com | same |
| topic keccak | `cast keccak` (foundry) | |
| topic verification | https://base.blockscout.com/api (module=logs, action=getLogs, topic0 filter); re-check via `eth_getTransactionReceipt` on gateway.tenderly.co / publicnode / drpc | |
| RSR episode | https://base-mainnet.public.blastapi.io (blocks, txs, eth_call), https://base.drpc.org (receipts, debug traces) | see section 6 |

This collector kept each endpoint at <= 4 in-flight requests (drpc: bf 3, plus 1 for either the fw fallback or the sequential RSR scripts).
The one exception was a ~15 s finalize test at ~21:20Z, when drpc briefly had up to 5 in flight (bf 3 + test 2).

Endpoint notes observed on 2026-09-30:
- base.drpc.org returned HTTP 429 intermittently (bf ran at ~1-2.6 blocks/s). An address-less `eth_getLogs` over 100 blocks succeeded, but 500-, 1,000-,
  5,000- and 9,000-block queries returned "ranges over 10000 blocks are not supported on free plan", and debug_traceBlockByNumber sometimes returned "Request timeout on the free plan".
- base.meowrpc.com serves old receipts but omits fields (no blobGasUsed, daFootprintGasScalar, depositNonce, depositReceiptVersion, l1 scalars), so it was not used.
- For block 52003001, receipts from gateway.tenderly.co and base-rpc.publicnode.com were byte-for-byte identical after JSON parsing.
- base-mainnet.public.blastapi.io rejects `eth_getBlockReceipts` ("Only core evm requests are allowed", HTTP 401).

## 3. Block range, time window, pinned values

- Launch (pinned in `collect/state/config.json`): 2026-09-30T21:02:45Z. Launch head `52006409` (from base-rpc.publicnode.com).
- Backfill: `bf_start = 52006409 - 10800 = 51995609` (timestamp 1790780565 = 2026-09-30T15:02:45Z) through `bf_end = 52006399`.
  The backfill was **not** reduced: the full 6 hours (10,791 blocks) is collected.
  - `bf` (drpc): 51995609-51998608, except block 51998605. `bf4` (tenderly): 51998609-51998799. `bf3` (tenderly): 51998800-51999999.
    `bf2` (tenderly): 52000000-52006399. `gf1` (tenderly): block 51998605. After drpc returned HTTP 429 for 14 attempts, bf wrote
    that block to `gaps.csv`; gf1 re-fetched it at 21:49Z.
  - Stream block counts: bf 2,999 + bf2 6,400 + bf3 1,200 + bf4 191 + gf1 1 = 10,791.
  - The backfill finished at 2026-09-30T21:49Z, 47 minutes after launch. A check at that time found 51995609-52006399 complete,
    with no duplicate block rows and every `parent_hash` equal to the previous `block_hash`.
    - At 21:12Z the range was split into bf and bf2 (`bf_split_note` in config.json).
    - At 21:26Z bf was shortened again and bf3 was added (`bf3_split_note`).
    - At 21:49Z bf was stopped at 51998608, and bf4 plus gap-fill gf1 were run as standalone processes (`bf4_split_note`).
      bf4 is listed in `extra_streams`.
    - All three changes were made because base.drpc.org served 0.07-2.6 blocks/s under HTTP 429.
    - Each change was done by stopping only this collector's own processes and editing the checkpoint `end`. At 21:12Z and 21:26Z
      `supervisor.py` was restarted; at 21:49Z only bf was stopped, and the supervisor restarted it. The streams resumed from their checkpoints (parts are truncated to the checkpointed size on restart, and no truncation was needed).
    - The fw stream was paused for about 15 s at the 21:12Z and 21:26Z restarts; it resumes by block number, so no forward block was skipped.
- Forward: `fw_start = 52006400` (timestamp 1790802147 = 2026-09-30T21:02:27Z) onward. The collector follows the head with a lag of
  10 blocks (20 s).
- Forward stop rule: the stop is detected when (`V4LIVE.DONE` or `V4LIVE.FAILED`) AND (`SHALLOW_LIVE.DONE` or `SHALLOW_LIVE.FAILED`)
  exist in `/home/user/dapparb/research-material/.sentinels/`, or at launch + 7 h (2026-10-01T04:02:45Z), whichever comes first.
  At detection, `stop_block = head - 10 + 150`: a margin of 150 blocks (~5 min) past detection. The detection time, reason and
  stop block are recorded in `collect/state/fw.ckpt.json` (`stop_detected_utc`, `stop_reason`, `stop_block`) and in `integrity.json`.
- Final range: `[51995609, stop_block]`, contiguous. The last block number and its timestamp go into the AUTO-STATUS block and `integrity.json`.

## 4. Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/05-base-onchain/collect
# swap topic list used by the census (static; regenerate topic0 with: cast keccak '<signature>')
cat swap_topics_used.csv
# main census: pins head, runs bf / bf2 / (extra bfN from config.json) / fw, gap fill, finalize, writes sentinel.
# Resumable: re-run the same command. (This run: BF2_BLOCKS equivalent 6400, plus extra_streams bf3/bf4 added to config.json
# at 21:26Z / 21:49Z; bf4 and gf1 were started by hand:)
#   python3 -u census.py --stream bf4 --start 51998609 --end 51998799 --chunk 40 --workers 3
#   echo 51998605 > state/gf1_blocks.txt; python3 -u census.py --stream gf1 --blocks-file state/gf1_blocks.txt --chunk 10 --workers 1
BF2_BLOCKS=6400 setsid nohup python3 -u supervisor.py > supervisor.log 2>&1 < /dev/null &
# topic verification (writes ../swap-topics.csv; finalize.py later adds census_first_seen_* columns)
setsid nohup python3 -u verify_topics.py > verify_topics.log 2>&1 < /dev/null &
# RSR episode (one-off, raw)
python3 rsr_episode.py > rsr_episode.log 2>&1
python3 rsr_traces.py  > rsr_traces.log 2>&1
# finalize can be re-run safely at any time after the streams are done
python3 finalize.py
```

- A fresh run pins a new head, so it collects a different window. To re-collect **this** window, first write `state/config.json`
  with the values listed in section 3 (`launch_head` 52006409, `bf_start` 51995609, `bf_end` 52006399,
  `bf2_start` 52000000, `bf2_end` 52006399, `bf_split_end` 51998608,
  `extra_streams` `[{"name":"bf3","start":51998800,"end":51999999},{"name":"bf4","start":51998609,"end":51998799}]`,
  `fw_start` 52006400, plus the keys the supervisor writes). Then write `state/fw.ckpt.json` as
  `{"stream":"fw","start":52006400,"next":52006400,"stop_block":<final block>,"stop_reason":"reproduction"}`. Then start the supervisor.
- Single streams can also be run by hand, e.g. `python3 census.py --stream bf --start A --end B --chunk 40 --workers 3`.
  The checkpoint goes to `state/bf.ckpt.json`.
- Scripts: `census.py` (per-block fetch, validation, filtering, writing), `supervisor.py` (orchestration, restarts, sentinel),
  `finalize.py` (merge blocks, integrity lists, file index, manifest status), `verify_topics.py`, `rsr_episode.py`, `rsr_traces.py`.
- Logs: `supervisor.log`, `census_{bf,bf2,bf3,bf4,gf1,fw,gf}.log`, `verify_topics.log`, `rsr_episode.log`, `rsr_traces.log`.

### Fetch / validation / write rules (census.py)

- For each block, the collector calls `eth_getBlockByNumber(n,false)` and `eth_getBlockReceipts(n)`. It accepts the block only if:
  the receipt count equals the block's tx count; each receipt's `transactionIndex` equals its position; each receipt's
  `transactionHash` equals the block's tx list at that position; and each receipt's `blockHash` equals the block hash.
  Otherwise it retries.
- Retries use exponential backoff (1 s up to 60 s, plus jitter) on HTTP 429/5xx, network errors, JSON-RPC errors and "not yet available".
  After a size error, or after 6 failed attempts, it switches to per-tx `eth_getTransactionReceipt`.
  After 14 attempts (bf, bf2-bf4) or 16 attempts (fw), the block number is written to `gaps.csv` and the collector moves on.
  The supervisor then re-fetches every block listed in `gaps.csv` in a gap-fill stream (`gf`, 20 attempts, three endpoints).
  Blocks already present in some blocks part are skipped; they are listed in `state/gf.ckpt.json` under `skipped_already_present`.
  Blocks that still fail are listed as `unrecoverable` in `gaps-final.csv`.
- Output is written per chunk (40 blocks for bf and bf2-bf4, up to 30 for fw, 10 for gap fill), as one gzip member appended to the current part file.
  Before a chunk is written, a part that is already >= 85 MiB is closed and the next part number is used.
  So every file stays well below 90 MB.
- The checkpoint (`state/<stream>.ckpt.json`) stores the next block and the byte size of each open part. On restart, parts are
  truncated to the checkpointed size and any newer parts are deleted. So no duplicate or partial rows survive a crash.
- Hex values are lowercased. Integer quantities in the CSVs are base-10 strings. The `receipt` sub-object and the logs in the
  candidates files keep the RPC's hex encoding verbatim (lowercased).

## 5. Per-file schemas

Stream tag in file names: `bf` = backfill via drpc, `bf2`/`bf3`/`bf4` = backfill via tenderly, `gf1` = early gap fill of block 51998605, `fw` = forward/head-following, `gf` = gap fill.
Part numbers `NNNN` start at 0001. Every CSV part starts with its own header row. Each gz file may contain several concatenated
gzip members. `zcat`, Python `gzip`, and pandas `read_csv(compression='gzip')` all read the whole file.

### `blocks.csv.gz` (one row per block; built by finalize.py from `data/blocks-*-NNNN.csv.gz`, which are then moved to `collect/state/blocks-parts/`)

| column | meaning | units | raw/derived |
|---|---|---|---|
| block_number | block number | int | raw (hex->dec) |
| timestamp | block timestamp | unix seconds | raw |
| base_fee_per_gas | `baseFeePerGas` | wei | raw |
| gas_used | block `gasUsed` | gas | raw |
| gas_limit | block `gasLimit` | gas | raw |
| tx_count | number of txs in block (len of `transactions`) | count | raw |
| miner | `miner` (fee recipient) | address | raw |
| block_hash | `hash` | | raw |
| parent_hash | `parentHash` | | raw |

### `data/txs-<stream>-NNNN.csv.gz` (one row per transaction, every tx of every block, including deposit txs)

| column | meaning | units | raw/derived |
|---|---|---|---|
| block_number | | int | raw |
| tx_index | position in block (`transactionIndex`) | int | raw |
| tx_hash | | | raw |
| from | receipt `from` | address | raw |
| to | receipt `to` (empty for contract creation) | address | raw |
| status | 1 success, 0 reverted | | raw |
| gas_used | receipt `gasUsed` | gas | raw |
| effective_gas_price | receipt `effectiveGasPrice` (L2 execution price per gas; 0 for deposit txs) | wei/gas | raw |
| l1_fee | receipt `l1Fee` (OP-stack L1 data fee; empty if absent) | wei | raw |
| tx_type | receipt `type` (`0x0`,`0x1`,`0x2`,`0x4`,`0x7e` deposit, ...) | hex | raw |
| logs_count | number of logs in the receipt | count | derived (len) |
| candidate_criterion | `A`, `B` or empty: whether the tx is in the candidates files, and under which criterion | | derived (rule below) |

Priority fee per gas can be derived later as `effective_gas_price - base_fee_per_gas`, joining on block_number.
The census stores no `maxPriorityFeePerGas`, `maxFeePerGas`, nonce or input; see section 7.

### `data/reverted-<stream>-NNNN.csv.gz` (every tx with status 0)

`block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, l1_fee, logs_count, tx_type`. Meanings and units are as in txs (raw; `logs_count` derived).

### `data/candidates-<stream>-NNNN.jsonl.gz` (one JSON object per line, one line per candidate tx)

Selection rule (derived, deterministic, applied to the tx's receipt logs):
- **A**: at least 2 logs whose `topics[0]` is in `collect/swap_topics_used.csv` (26 topics; the same list is in `swap-topics.csv`).
- **B** (only if not A): at least 3 ERC-20 Transfer logs (`topics[0]` = `0xddf252ad...b3ef` with exactly 3 topics, which excludes
  ERC-721 Transfer with 4 topics), emitted by at least 2 distinct token contracts.
- Reverted txs have no logs, so they never meet A or B. They are all in `reverted-*`.

| key | meaning | raw/derived |
|---|---|---|
| block_number, block_timestamp, tx_index | as above | raw |
| tx_hash, from, to | as above (`to` null for creation) | raw |
| status | 1/0 | raw |
| gas_used, effective_gas_price | base-10 strings | raw |
| criterion | `A` or `B` | derived |
| derived.n_swap_topic_logs | number of logs with topic0 in the swap list | derived |
| derived.n_erc20_transfer_logs | number of 3-topic Transfer logs | derived |
| derived.n_erc20_transfer_token_contracts | distinct emitters of those Transfer logs | derived |
| receipt | every receipt field except `logs`, verbatim (hex strings): type, status, cumulativeGasUsed, logsBloom, transactionHash, transactionIndex, blockHash, blockNumber, gasUsed, effectiveGasPrice, blobGasUsed, from, to, contractAddress, l1GasPrice, l1GasUsed, l1Fee, l1BaseFeeScalar, l1BlobBaseFee, l1BlobBaseFeeScalar, daFootprintGasScalar, depositNonce/depositReceiptVersion (deposits), plus any other field the endpoint returned | raw |
| logs[] | ALL logs of the tx in order: `address`, `topics` (array), `data` (hex), `log_index` (int, block-level logIndex) | raw (log_index hex->int) |

The per-log fields `blockHash`, `blockNumber`, `transactionHash`, `transactionIndex` and `removed` are dropped from `logs[]`
because they repeat the parent object.

### `data/provenance-<stream>-NNNN.csv.gz`

`block_number, endpoint, receipts_method` (`eth_getBlockReceipts` or `eth_getTransactionReceipt per tx`).
This file was introduced at the 21:12Z restart. Blocks written before it have no provenance row:
- bf 51995609-51996568: all from https://base.drpc.org.
- fw 52006400-52006681: all from https://base-rpc.publicnode.com (fw stats showed 0 errors, so no fallback was used).

These ranges are also recorded in `collect/state/config.json` (`pre_provenance`).

### `swap-topics.csv`

| column | meaning |
|---|---|
| topic0 | keccak256 of signature (`cast keccak`) |
| signature | canonical event signature |
| protocol | protocol(s) known to emit it |
| source_url | interface/source where the event is declared |
| verified_example_tx / _block / _emitter / _log_index | newest log returned by Blockscout in the first window where one was found, re-checked in the RPC receipt |
| verification_method | Blockscout window searched, or "no log found" with the windows searched |
| census_first_seen_tx / _block / _emitter | (added by finalize.py) first occurrence of the topic in ANY tx of the census range (from `collect/state/first_seen_*.json`) |

The topic list is identical to `collect/swap_topics_used.csv`, the file census.py loaded at start (26 topics).
The list was fixed before launch and was not changed during the run.
`collect/verify_topics.py` was still running when this manifest was written, and base.blockscout.com was returning HTTP 429
and timeouts. Until that script finishes, `verification_method` reads `pending: ...` (progress in `collect/verify_topics.log`).
If a row ends as "no log found ... failed: <windows>", the Blockscout query failed; it does not mean the search completed with no result.
Re-run `python3 verify_topics.py` to retry. It rewrites the file after every topic, keeps rows that already have an example, and keeps any `census_*` columns.
Search windows: the newest 1k, 16k, 500k and 10M blocks before the pinned head, with 6 tries each.

### `gaps.csv` / `gaps-final.csv` / `integrity.json` / `data/file_index.csv`

- `gaps.csv`: one row per block that exhausted its retries in a stream (`stream, block_number, recorded_utc, reason`). Append-only.
  The file does not exist if no block ever failed.
- `gaps-final.csv`: (finalize) `block_number, final_status (recovered|unrecoverable), failure_events`.
- `integrity.json`: (finalize) range, counts of missing blocks, parent-hash mismatches (`parent_hash(n) != block_hash(n-1)`),
  blocks whose txs-row count differs from `tx_count`, and the lists of those block numbers.
- `data/file_index.csv`: (finalize) `file, bytes, rows (excl. header), min_block, max_block`.

## 6. `rsr-episode/` (one-off, raw)

Context as given in the task (not verified or interpreted here):
- Uniswap V3 1% WETH/RSR pool: `0x11e26bbd1a5547895a50fc39a2d4c0025dec0bda`.
- Aerodrome V2 WETH/RSR pool: `0xd204058452f57464e0e5ab8c3cc9cbcb6b41d4ee`.
- Winning tx: `0x2310e683fe40902529cad07cde417d9062cc857c6052fb905101ce4b6d532e77` (block 51998757, tx index 1),
  from `0xf0523316cf23ef167d874fa030b2214280e38ee6` via contract `0xa05787285256c4ee18d7ed6865de2ddbb949c411`.

| file | content | source |
|---|---|---|
| headers.jsonl.gz | `eth_getBlockByNumber(n,false)` for n = 51998755..51998758, verbatim, one line per block | blastapi |
| blocks_full.jsonl.gz | `eth_getBlockByNumber(n,true)`: header plus full transaction objects (input, nonce, type, maxFeePerGas, maxPriorityFeePerGas, gas, value, accessList, signature), verbatim | blastapi |
| transactions_by_hash.jsonl.gz | `eth_getTransactionByHash` for every tx of the 4 blocks (1,100 lines), verbatim | blastapi (drpc fallback) |
| receipts.jsonl.gz | `eth_getBlockReceipts` for the 4 blocks, one receipt per line (1,100 lines), verbatim including logs | drpc (blastapi refused) |
| block_traces.jsonl.gz | `debug_traceBlockByNumber` with callTracer `{withLog:true}`, one line per block, verbatim result array | drpc |
| trace_winner.json | `debug_traceTransaction` callTracer withLog of the winning tx | drpc |
| pool_state.csv | `eth_call` at the END of blocks 51998754..51998758: V3 pool slot0/liquidity/fee/token0/token1/tickSpacing; Aerodrome pool getReserves/token0/token1/stable/factory; factory getFee(pool,stable). Column `raw_return_hex` is raw. `derived_decoded_words_base10` splits the return data into 32-byte words read as **unsigned** integers, so signed fields (e.g. slot0 tick, int24) need two's-complement reinterpretation | blastapi (archive) |
| errors.csv | calls that failed on an endpoint (4 x blastapi `eth_getBlockReceipts` HTTP 401, then served by drpc) | |
| trace_errors.csv | block-trace failures after retries (header only = none) | |

`block_traces.jsonl.gz` has two gzip members. The first run traced blocks 51998757-51998758, and its lines have no `method` key.
The second run traced 51998755-51998756 after a free-plan timeout, and its lines carry `"method":"debug_traceBlockByNumber"`.
The pool state at the end of block 51998756 is the state before the first tx of block 51998757.

## 7. Coverage limits and gaps

- **Chain**: Base only. Other chains (Q5, Q8) are not in this directory.
- **Window**: only the contiguous range in section 3, about 6 h of backfill plus the forward period up to the stop rule
  (7 h after launch at most). No data older than block 51995609.
- **Head lag**: the forward stream stays 10 blocks behind the head. Blocks are taken as served at fetch time; reorgs after fetch
  are not tracked, but parent-hash linkage is checked in `integrity.json`.
- **Transaction objects not collected in the census**: `eth_getBlockByNumber(n,false)` gives only tx hashes. For census txs there is
  no calldata/input, nonce, value, `maxPriorityFeePerGas` or `maxFeePerGas`, only the receipt's `effectiveGasPrice`.
  Full tx objects exist only for the 4 RSR blocks.
- **No traces in the census**: internal calls are not collected. Reverted txs have no logs, so the census shows only their `to`
  address, not which pools they touched. The RSR blocks have call traces.
- **Not observed**: txs that never landed (dropped, outbid, private/bundle-only), mempool timing, and flashblock (sub-block)
  boundaries. `tx_index` is the final in-block position.
- **Criterion A is limited to the 26 topics in `swap-topics.csv`.** These swap events are not in the list:
  - Ekubo-style anonymous logs (no topic0).
  - Non-standard events from V4 hooks with custom accounting, other than `HookSwap`.
  - Bonding-curve / launchpad trades that do not emit a listed event.
  - RFQ/aggregator-level events (0x, 1inch, UniswapX, Hashflow, Bebop, Odos, KyberSwap, Sushi RouteProcessor).
  - Other DEXes with unlisted signatures.

  Such txs are in the candidates only if they meet criterion B. Listed topics with no Base example are marked "no log found" in `swap-topics.csv`.
- **Criterion B** counts only 3-topic ERC-20 `Transfer` events. It misses native ETH movements (no logs), ERC-1155/721 transfers,
  and tokens with non-standard transfer events.
- **Candidates are a filter, not a classification.** Membership is decided only by the log rule above and says nothing about a tx's
  purpose. A tx with fewer than 2 listed swap logs and fewer than 3 qualifying Transfer logs is not in the candidates files,
  whatever its purpose. All txs remain in `txs-*` for re-filtering by `to`/`from`/position.
- **Receipt field sets depend on the endpoint.** tenderly and publicnode were identical on a tested block. drpc receipts had the same
  key set in the smoke test. meowrpc (fewer fields) was not used. See `provenance-*` for which endpoint served each block.
- **drpc getLogs restriction**: address-less `eth_getLogs` on base.drpc.org was refused for ranges of 500 blocks and more on 2026-09-30 (100 blocks worked). Topic
  verification therefore used the Blockscout API. The first draft of `verify_topics.py` (drpc getLogs) was superseded before any output was kept.
- **Unrecoverable blocks**, if any, are listed in `gaps-final.csv` with the reason. The file is written at finalize.
- **Stop margin**: the forward stream continues ~150 blocks (~5 min) past the moment both engine sentinels are detected.
- If the supervisor fails, `/home/user/dapparb/research-material/.sentinels/BASE_CENSUS.FAILED` holds the reason. The streams resume
  from their checkpoints when `supervisor.py` is re-run.
