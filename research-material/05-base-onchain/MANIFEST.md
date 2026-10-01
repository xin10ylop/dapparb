# 05-base-onchain: raw Base block census + RSR episode

Raw on-chain record of Base (chain id 8453) blocks 51995609-52017160 (21,552 consecutive blocks, block timestamps
2026-09-30T15:02:45Z to 2026-10-01T03:01:07Z). It holds every transaction's receipt summary, every reverted transaction, and
full receipts/logs for the transactions that match a swap-log / multi-token-transfer filter. The range starts 10,800 blocks
(6 hours) before the collector launch at 2026-09-30T21:02:45Z (backfill). It then follows the head from the launch to stop
block 52017160. That stop block was set when the end of the valid V4 live test was detected: head 52017020 at 02:56:28Z,
minus the 10-block lag, plus a 150-block margin. The range contains the RSR episode (blocks 51998755-51998758), the
shallow-pool live test (blocks 52008242-~52008842) and the valid V4 live test (blocks 52016408-52017008); see "Time windows
inside the range". The folder also holds a one-off raw capture of blocks 51998755-51998758 with full transaction objects,
call traces and pool state (`rsr-episode/`).

This file only maps the data. It contains no findings, rankings or conclusions. The only checks run on the files are the
integrity checks listed under "Verified inventory (2026-10-01)".

**Status: COMPLETE WITH GAPS** (set 2026-10-01 after every file in this folder was re-verified).

- Block census: complete. Sentinel `/home/user/dapparb/research-material/.sentinels/BASE_CENSUS.DONE` (`finished_utc`
  2026-10-01T03:10:56Z); no `BASE_CENSUS.FAILED` exists. `integrity.json`: range 51995609-52017160, 21,552 of 21,552 blocks
  present, 0 missing blocks, 0 parent-hash mismatches, 0 tx-count mismatches, 0 conflicting duplicate block rows, no oversize
  files. `gaps-final.csv`: one block (51998605) failed in stream `bf` (HTTP 429) and is `recovered` (re-fetched by `gf1`);
  no row is `unrecoverable`. No file in this folder exceeds 90 MB. The largest is `data/candidates-bf-0001.jsonl.gz`
  (89,975,717 bytes).
- The forward stream (`fw`) was interrupted twice and both times resumed from its checkpoint with no block gap:
  1. The container restart: all processes died at ~22:58Z on 2026-09-30, and the supervisor was restarted at 01:03Z on
     2026-10-01.
  2. The main session stopped it at ~02:04Z on 2026-10-01 to clear a stop condition set by an invalid `V4LIVE.DONE`.

  See "Run history".
- Gap (topic-verification metadata, not block data): `collect/verify_topics.py` searches Blockscout for one example log per
  swap topic. It started at 2026-09-30T21:50:36Z, died in the container restart (last log line 22:58:08Z), and was not
  re-run.
  - In `swap-topics.csv`, the row for topic0 `0xa4228e1eb11eb9b31069d9ed20e7af9a010ca1a02d4855cee54e08e188fcc32c`
    (`Swap(address,address,int256,int256)`) still reads `pending: collect/verify_topics.py running`.
  - 4 rows list Blockscout windows under `failed:` in `verification_method`.
  - The `census_first_seen_*` columns are not affected. `finalize.py` writes them from the census itself.

  To retry, run `python3 verify_topics.py` in `collect/` (section 5). It was not re-run during finalization because it
  rewrites `swap-topics.csv` and data files were not modified.

  *Corrected 2026-10-01 (fixup, ~05:35Z):* the three sub-items above are no longer true. `verify_topics.py` was re-run on
  2026-10-01 from 04:41:16Z to 05:34:26Z with the same pinned head (`--head 52007824`); log `collect/verify_topics_rerun.log`.
  See the section "verify_topics.py re-run (2026-10-01)" at the end of this file.
  - `swap-topics.csv` now has no `pending` row: 22 rows have a verified example and 4 rows read "no log found".
  - The SmarDex row `0xa4228e1e…` now has a verified example.
  - Only 1 row still lists a failed window: Clipper `Swapped(address,address,address,uint256,uint256,bytes)`
    (`0x4be05c8d…`), window 51507825-52007824. That window got 12 read timeouts of 120 s over two runs. The other three
    windows of that row, including the enclosing 10M window 42007825-52007824, were answered "No logs found".
  - The remaining gap is this one failed window, in topic-verification metadata only.

*Provenance of this file:* first written 2026-09-30 while the collectors were running. `collect/finalize.py` rewrote the
AUTO-STATUS block at 2026-10-01T03:10:56Z, and that version was committed in `002dc86` (2026-10-01T03:14:08Z). This version
(2026-10-01) adds the status line above and these sections: "Run history", "Time windows inside the range", the
question-line mapping by line number (section 1), and "Verified inventory (2026-10-01)". The text of sections 2-7 is kept,
with the changes listed under "Corrections made on 2026-10-01".

`collect/finalize.py` wrote the block below. Re-running `finalize.py` rewrites this block, `blocks.csv.gz`,
`integrity.json`, `gaps-final.csv`, `data/file_index.csv`, the `census_first_seen_*` columns of `swap-topics.csv` and
`collect/state/finalize_summary.json`; see section 4 for its local-only inputs. The status word in the block covers the
block census only. On 2026-10-01 every byte size, row count and min/max block number in the block was re-checked against
the files, and all 32 rows match.

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

## Run history (UTC)

Sources: `collect/supervisor.log`, `collect/census_<stream>.log`, `collect/verify_topics.log`, `collect/state/*.ckpt.json`
(local-only; each final checkpoint is also printed verbatim in the `stream done` line of the committed `census_<stream>.log`),
and the sentinels in `/home/user/dapparb/research-material/.sentinels/`.

| time (UTC) | event | record |
|---|---|---|
| 2026-09-30T21:02:45Z | Supervisor pins launch head 52006409 (base-rpc.publicnode.com) and starts `bf` (51995609-52006399) and `fw` (from 52006400) | supervisor.log |
| 21:12:17Z | Backfill split: `bf2` (52000000-52006399) added; supervisor restarted | supervisor.log; `bf_split_note` in config.json |
| 21:25:37Z | bf2 finished | supervisor.log |
| 21:26:04Z | `bf3` (51998800-51999999) added; supervisor restarted | supervisor.log; `bf3_split_note` |
| 21:28:44Z | bf3 finished | supervisor.log |
| 21:46:46Z | bf writes block 51998605 to `gaps.csv` after 14 attempts (HTTP 429 from base.drpc.org) | census_bf.log, gaps.csv |
| 21:48:54Z-21:49:34Z | bf stopped (rc -15), restarted by the supervisor with end 51998608, finished. `bf4` (51998609-51998799) and `gf1` (block 51998605) were run by hand and finished at 21:49:25Z and 21:49:01Z | supervisor.log, census_bf4.log, census_gf1.log; `bf4_split_note` |
| 21:50:36Z | `verify_topics.py` started (Blockscout head pinned 52007824) | verify_topics.log |
| ~22:58Z | Container restart: all processes died (supervisor, fw, verify_topics.py). Last fw progress line: 22:57:50Z. fw checkpoint `next` = 52009870, so the last block written was 52009869 (timestamp 22:58:05Z). Last verify_topics.log line: 22:58:08Z | census_fw.log, supervisor.log, verify_topics.log |
| 2026-10-01T04:41:16Z-05:34:26Z | (row added 2026-10-01, fixup) `verify_topics.py --head 52007824` re-run in three passes (04:41:16Z, stopped by the fixup agent ~04:45Z to add rate-limit handling; 04:45:52Z-05:17:17Z; 05:17:27Z-05:34:26Z). No `pending` row left; 1 window still failed. Details in "verify_topics.py re-run (2026-10-01)" | verify_topics_rerun.log |
| 2026-10-01T01:03:10Z | Supervisor restarted. bf, bf2, bf3 and bf4 log `stream already done`. fw resumes from checkpoint `next` = 52009870 (first progress line after the restart, 01:04:13Z: `next=52009930` after 60 blocks). No census log has a `truncated` or `removed stale part` line | supervisor.log, census_*.log |
| 01:57:19.654Z | `V4LIVE.DONE` written by a V4 live attempt that processed no blocks. It is now kept as `../02-v4-live-test/attempts/20261001T010337Z-no-blocks/V4LIVE.DONE.invalidated` | ../02-v4-live-test/attempts/20261001T010337Z-no-blocks/ATTEMPT-NOTE.md |
| 01:57:30Z | fw detects the stop condition (`V4LIVE.*` and `SHALLOW_LIVE.*` both present): head 52015251, `stop_block` 52015391 | census_fw.log |
| 02:04:30Z | Main session stops fw (`fw exited rc -15 restart 1`). Last progress line before it: 02:04:07Z `next=52013410` | supervisor.log, census_fw.log |
| 02:04:41Z | Stop condition cleared in `state/fw.ckpt.json`: `stop_block`, `stop_reason`, `stop_detected_utc` and `stop_detected_head` moved into `notes[0].removed` with an explanatory note. The same event is logged in supervisor.log, which also says that the invalid V4LIVE.DONE was archived in `02-v4-live-test/attempts/` | fw.ckpt.json `notes`, supervisor.log |
| 02:05:00Z | Supervisor restarts fw from its checkpoint (first progress line after the restart, 02:06:01Z: `next=52013470` after 60 blocks) | supervisor.log, census_fw.log |
| 02:56:05.719Z | Valid `V4LIVE.DONE` written (V4 live test stopped at 02:56:04Z) | .sentinels/V4LIVE.DONE, ../02-v4-live-test/run-times.json |
| 02:56:28Z | fw detects the stop condition: head 52017020, `stop_block` 52017160 (= 52017020 - 10 + 150) | census_fw.log, fw.ckpt.json, integrity.json |
| 03:08:41Z | fw reaches `stop_block` and finishes (`next` 52017161) | census_fw.log |
| 03:09:00Z-03:09:10Z | Gap-fill stream `gf` for `gaps.csv`: block 51998605 already present, so it is skipped (`skipped_already_present`); 0 blocks fetched | census_gf.log, gf.ckpt.json |
| 03:10:56Z | `finalize.py` ran; supervisor wrote `BASE_CENSUS.DONE` | supervisor.log, .sentinels/BASE_CENSUS.DONE |

When blocks were fetched (from the progress lines in `census_fw.log`; this affects only when a block was read, not which
blocks are present):
- Until the container restart, fw stayed 10 blocks behind the head.
- From 01:03Z it started with blocks about 2 h old (block 52009870, timestamp 22:58:07Z) and caught up at ~1 block/s
  (`blocks/s=0.98`).
- Blocks of the shallow-pool live test window (52008242-52008842) were fetched before the restart, at the 10-block lag:
  progress `next=52008234` at 22:03:57Z and `next=52008847` at 22:24:22Z.
- Blocks of the valid V4 live test window (52016408-52017008, timestamps 02:36:03Z-02:56:03Z) were fetched between ~02:56Z
  and ~03:06Z: progress `next=52016410` at 02:55:57Z and `next=52017010` at 03:06:07Z.
- The last block (52017160, timestamp 03:01:07Z) was written at 03:08:41Z.

## Time windows inside the range

Block timestamps are taken from `blocks.csv.gz`. The census files that hold each window are found from the min/max block
numbers in `data/file_index.csv`.

| window | blocks | block timestamps (UTC) | where the block numbers come from | census files holding these blocks |
|---|---|---|---|---|
| RSR episode | 51998755-51998758 | 2026-09-30T16:47:37Z-16:47:43Z | task context (section 6) | `blocks.csv.gz`, `data/txs-bf4-0001.csv.gz`, `data/reverted-bf4-0001.csv.gz`, `data/candidates-bf4-0001.jsonl.gz`, `data/provenance-bf4-0001.csv.gz`; plus the separate capture `rsr-episode/*` |
| Shallow-pool live test (SHALLOW_LIVE, attempt 1, `--min-depth-eth 0.001`) | 52008242-~52008842 (`head_at_ready` to `head_at_stop`) | 2026-09-30T22:03:51Z-22:23:51Z | `../04-shallow-pools/run-times.json` | `blocks.csv.gz`, `data/txs-fw-0001.csv.gz`, `data/reverted-fw-0001.csv.gz`, `data/candidates-fw-0001.jsonl.gz`, `data/provenance-fw-0001.csv.gz` |
| Invalid V4 live attempt | none processed (searcher ready 01:37:18Z, sentinel 01:57:19Z) | 2026-10-01T01:37Z-01:57Z | `../02-v4-live-test/attempts/20261001T010337Z-no-blocks/` | the blocks of that period are in `data/*-fw-*` like every other block |
| Valid V4 live test (V4LIVE, V4 pools from PoolManager Initialize files via `--v4-pools`, `NO_WS=1`) | 52016408-52017008 (first/last processed block in its log) | 2026-10-01T02:36:03Z-02:56:03Z | `../02-v4-live-test/run-times.json` | `blocks.csv.gz`, `data/txs-fw-0002.csv.gz`, `data/reverted-fw-0001.csv.gz`, `data/candidates-fw-0003.jsonl.gz`, `data/provenance-fw-0001.csv.gz` |

## 1. Question lines served (mapping only)

Line numbers refer to the eight research question lines as given on 2026-10-01. Their text, verbatim:
- 1: 'Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet.'
- 2: 'Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens.'
- 3: 'Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit.'
- 4: 'Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured.'
- 5: 'V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee.'
- 6: 'BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents.'
- 7: 'Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions.'
- 8: 'So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test.'

| line | files in this folder |
|---|---|
| 1 | `data/candidates-*.jsonl.gz` (all logs of candidate txs, including V4 PoolManager `Swap` logs with the pool id in `topics[1]`, and `HookSwap` logs); `swap-topics.csv` (the V4 topics used by criterion A); the census files for the valid V4 live test window: `data/txs-fw-0002.csv.gz`, `data/reverted-fw-0001.csv.gz`, `data/candidates-fw-0003.jsonl.gz`, `data/provenance-fw-0001.csv.gz`, `blocks.csv.gz` |
| 2 | `data/candidates-*.jsonl.gz` (V2-style `Swap` logs, pool address = log `address`; ERC-20 `Transfer` logs); `data/txs-*.csv.gz`; `swap-topics.csv`. This folder has no list of V2 pairs; the main material for this line is in `../03-v2-older-pairs/` |
| 3 | `data/candidates-*.jsonl.gz` (all logs, including ERC-20 `Transfer` amounts); `data/txs-*.csv.gz`, `data/reverted-*.csv.gz`; the census files for the shallow-pool live test window: `data/txs-fw-0001.csv.gz`, `data/reverted-fw-0001.csv.gz`, `data/candidates-fw-0001.jsonl.gz`, `data/provenance-fw-0001.csv.gz`, `blocks.csv.gz`. The main material for this line is in `../04-shallow-pools/` |
| 4 | none (this folder is Base only; other chains are in `../06-other-chains-onchain/` and `../07-other-chains-engine/`) |
| 5 | `rsr-episode/*` (all files: headers, full tx objects with `maxPriorityFeePerGas`/`maxFeePerGas`, receipts with logs, call traces, pool state); the census files that hold blocks 51998755-51998758: `data/txs-bf4-0001.csv.gz`, `data/reverted-bf4-0001.csv.gz`, `data/candidates-bf4-0001.jsonl.gz`, `data/provenance-bf4-0001.csv.gz`, `blocks.csv.gz`; for the whole range, `data/candidates-*.jsonl.gz` (V4 `Swap` / `HookSwap` logs), `data/txs-*.csv.gz` (`effective_gas_price`, `tx_index`, `status`, `l1_fee`), `blocks.csv.gz` (`base_fee_per_gas`), `data/reverted-*.csv.gz`; `swap-topics.csv` |
| 6 | none (no BSC data in this folder; BSC material is in `../06-other-chains-onchain/bsc/`) |
| 7 | `blocks.csv.gz`, `data/txs-*.csv.gz`, `data/reverted-*.csv.gz`, `data/candidates-*.jsonl.gz`, `swap-topics.csv`. These cover Base only, for the 21,552 blocks of this range; the periods of the cited studies and Arbitrum are not in this folder |
| 8 | The same files as line 1, plus the run records that align the census with the valid V4 live test: `collect/supervisor.log`, `collect/census_fw.log`, `integrity.json` (`fw_stop_*`) and `collect/state/fw.ckpt.json` (local-only; `notes` holds the cleared stop condition) |

Coverage and provenance files for every line above: `gaps.csv`, `gaps-final.csv`, `integrity.json`, `data/file_index.csv`,
`data/provenance-*.csv.gz`, `collect/*.py`, `collect/*.log`, `collect/swap_topics_used.csv`, `collect/state/` (local-only).

Files added or rewritten 2026-10-01 by the verify_topics.py re-run (fixup), one row per file:

| file | line |
|---|---|
| `swap-topics.csv` (rewritten; same rows and columns) | 1, 2, 5, 7 (as above) |
| `collect/verify_topics_rerun.log` (new) | provenance of `swap-topics.csv` for lines 1, 2, 5, 7 |
| `collect/verify_topics.py` (modified) | provenance of `swap-topics.csv` for lines 1, 2, 5, 7 |

The forward part of the census (`*-fw-*`) was timed to overlap the engine runs whose sentinels are `V4LIVE.*` (lines 1, 5,
8) and `SHALLOW_LIVE.*` (line 3). The census and the engine runs can be aligned by block number and timestamp.

Correction 2026-10-01: this section replaces the earlier table with keys Q1-Q10, where Q1 ("What is still unmeasured:") and
Q6 ("Would the gaps change the answer?") were headings. Old to new: Q2 = line 1, Q3 = line 2, Q4 = line 3, Q5 = line 4,
Q7 = line 5, Q8 = line 6, Q9 = line 7, Q10 = line 8. Every earlier file assignment is kept. The census files of the three
time windows were added for lines 1, 3, 5 and 8, and the run records for line 8.

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
The endpoints and limits were the same after the 01:03Z restart (the fw stream ran with the same arguments).

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
  10 blocks (20 s). The fw stream holds 10,761 blocks (52006400-52017160). Backfill plus forward: 10,791 + 10,761 = 21,552 blocks.
- Forward interruptions (details in "Run history"):
  - From ~22:58Z (2026-09-30) to 01:03Z (2026-10-01) no process of this collector ran, because of the container restart. At
    01:03Z fw resumed at its checkpoint, block 52009870. The last block written before the restart was 52009869.
  - From 02:04:30Z to 02:05:00Z fw was stopped by the main session to clear the stop condition, and resumed at its
    checkpoint, block 52013410.
  - Neither interruption left a block gap (`integrity.json`: 0 missing, 0 parent-hash mismatches).
- Forward stop rule: the stop is detected when (`V4LIVE.DONE` or `V4LIVE.FAILED`) AND (`SHALLOW_LIVE.DONE` or `SHALLOW_LIVE.FAILED`)
  exist in `/home/user/dapparb/research-material/.sentinels/`, or at launch + 7 h (2026-10-01T04:02:45Z), whichever comes first.
  At detection, `stop_block = head - 10 + 150`: a margin of 150 blocks (~5 min) past detection. The detection time, reason and
  stop block are recorded in `collect/state/fw.ckpt.json` (`stop_detected_utc`, `stop_reason`, `stop_block`) and in `integrity.json`.
  - First detection, 2026-10-01T01:57:30Z (head 52015251, stop_block 52015391). The `V4LIVE.DONE` that triggered it came from
    a V4 live attempt that processed no blocks. At 02:04:41Z the stop condition was removed from `state/fw.ckpt.json`, before
    fw reached block 52015391. The removed values and the reason are in that checkpoint's `notes` (and in the committed
    `census_fw.log` `stream done` line) and in `collect/supervisor.log`.
  - Second detection (the one in effect), 2026-10-01T02:56:28Z, after the valid V4 live test wrote `V4LIVE.DONE` at
    02:56:05.719Z: head 52017020, stop_block 52017160. `SHALLOW_LIVE.DONE` had existed since 2026-09-30T22:23:51Z.
- Final range: `[51995609, 52017160]`, contiguous. The last block's timestamp is 1790823667 = 2026-10-01T03:01:07Z
  (AUTO-STATUS block and `integrity.json`).

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
# (added 2026-10-01) re-run with the first run's pinned head; resumable, keeps finished rows and the census_* columns:
setsid nohup python3 -u verify_topics.py --head 52007824 >> verify_topics_rerun.log 2>&1 < /dev/null &
# RSR episode (one-off, raw)
python3 rsr_episode.py > rsr_episode.log 2>&1
python3 rsr_traces.py  > rsr_traces.log 2>&1
# finalize (re-runnable after the streams are done; needs the local-only collect/state/, see below)
python3 finalize.py
```

- A fresh run pins a new head, so it collects a different window. To re-collect **this** window, first write `state/config.json`
  with the values listed in section 3 (`launch_head` 52006409, `bf_start` 51995609, `bf_end` 52006399,
  `bf2_start` 52000000, `bf2_end` 52006399, `bf_split_end` 51998608,
  `extra_streams` `[{"name":"bf3","start":51998800,"end":51999999},{"name":"bf4","start":51998609,"end":51998799}]`,
  `fw_start` 52006400, plus the keys the supervisor writes). The full content of the `config.json` used is printed verbatim in
  the committed `supervisor.log` line `2026-10-01T01:03:10Z resuming with config {...}`. Then write `state/fw.ckpt.json` as
  `{"stream":"fw","start":52006400,"next":52006400,"stop_block":52017160,"stop_reason":"reproduction"}`. Then start the supervisor.
- Single streams can also be run by hand, e.g. `python3 census.py --stream bf --start A --end B --chunk 40 --workers 3`.
  The checkpoint goes to `state/bf.ckpt.json`.
- After the container restart, the supervisor was restarted at 2026-10-01T01:03:10Z with the same script, which appended to
  `supervisor.log`. Every stream resumed from its checkpoint in `state/`.
- `finalize.py` reads `state/config.json`, `state/*.ckpt.json` and `state/first_seen_*.json`. It rebuilds `../blocks.csv.gz` from
  `data/blocks-*` and `state/blocks-parts/blocks-*` (all local-only after finalize). On a checkout without these local-only
  files, do not run it: it needs them to rebuild `blocks.csv.gz` and the integrity lists.
- Scripts: `census.py` (per-block fetch, validation, filtering, writing), `supervisor.py` (orchestration, restarts, sentinel),
  `finalize.py` (merge blocks, integrity lists, file index, manifest status), `verify_topics.py`, `rsr_episode.py`, `rsr_traces.py`.
- Logs: `supervisor.log`, `census_{bf,bf2,bf3,bf4,gf1,fw,gf}.log`, `verify_topics.log`, `rsr_episode.log`, `rsr_traces.log`.
  (Added 2026-10-01: `verify_topics_rerun.log`, the log of the 2026-10-01 re-run of `verify_topics.py`.)
  `rsr_traces.log` holds only the output of the second trace run (blocks 51998755-51998756); see section 6.

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
  Before a chunk is written, a part that is already >= 85 MiB (89,128,960 bytes) is closed and the next part number is used.
  A part can therefore exceed 85 MiB by up to one chunk. The largest part is 89,975,717 bytes (`data/candidates-bf-0001.jsonl.gz`),
  and every file is below 90 MB.
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
because they repeat the parent object. (Checked 2026-10-01: every line of every candidates file has exactly the 13 top-level
keys `block_number, block_timestamp, criterion, derived, effective_gas_price, from, gas_used, logs, receipt, status, to,
tx_hash, tx_index`, and every log object has exactly `address, data, log_index, topics`.)

### `data/provenance-<stream>-NNNN.csv.gz`

`block_number, endpoint, receipts_method` (`eth_getBlockReceipts` or `eth_getTransactionReceipt per tx`).
This file was introduced at the 21:12Z restart. Blocks written before it have no provenance row:
- bf 51995609-51996568: all from https://base.drpc.org.
- fw 52006400-52006681: all from https://base-rpc.publicnode.com (fw stats showed 0 errors, so no fallback was used).

These ranges are also recorded in `collect/state/config.json` (`pre_provenance`). Every block from 52006682 on, including the
blocks fetched after both restarts, has a provenance row (`provenance-fw-0001.csv.gz`: 10,479 rows, 52006682-52017160).

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
`collect/verify_topics.py` (started 2026-09-30T21:50:36Z, Blockscout head pinned at 52007824) was killed by the container
restart at ~22:58Z (last log line 22:58:08Z, a Blockscout HTTP 429 retry for topic `0xa4228e1e...`) and was not re-run.
base.blockscout.com was returning HTTP 429 and timeouts while it ran. Its state in the file as committed:
- The row for `0xa4228e1eb11eb9b31069d9ed20e7af9a010ca1a02d4855cee54e08e188fcc32c` still reads
  `pending: collect/verify_topics.py running`.
- If a row ends as "no log found ... failed: <windows>", the Blockscout query for those windows failed. It does not mean the
  search finished with no result (4 rows contain `failed:`).

Re-run `python3 verify_topics.py` to retry. It rewrites the file after every topic, keeps rows that already have an example,
and keeps any `census_*` columns.

*Corrected 2026-10-01 (fixup):* "was not re-run" and the state listed above describe the file before 2026-10-01T04:41Z.
- The script was re-run with `--head 52007824`, so the windows are the same as in the first run. Since then:
  - no row is `pending`;
  - 22 rows have `verified_example_*`;
  - 4 rows read "no log found".
- Of the 4 "no log found" rows, 3 searched all 4 windows: `0xd013ca23…`, `0x29872dc2…` and `0xefce4460…`. The fourth,
  `0x4be05c8d…` (Clipper), has `failed: 51507825-52007824 failed`.
- Changes to the script: an optional `--head` argument; a wait on Blockscout's `x-ratelimit-reset` header after HTTP 429; and
  resume now also keeps rows whose "no log found" search covered all 4 windows of the same head.
- Details are in "verify_topics.py re-run (2026-10-01)".
Search windows: the newest 1k, 16k, 500k and 10M blocks before the pinned head, with 6 tries each.

### `gaps.csv` / `gaps-final.csv` / `integrity.json` / `data/file_index.csv`

- `gaps.csv`: one row per block that exhausted its retries in a stream (`stream, block_number, recorded_utc, reason`). Append-only.
  The file does not exist if no block ever failed. In this run it has 1 row (bf, 51998605).
- `gaps-final.csv`: (finalize) `block_number, final_status (recovered|unrecoverable), failure_events`. 1 row: 51998605, `recovered`.
- `integrity.json`: (finalize) range, counts of missing blocks, parent-hash mismatches (`parent_hash(n) != block_hash(n-1)`),
  blocks whose txs-row count differs from `tx_count`, and the lists of those block numbers (all three lists empty).
- `data/file_index.csv`: (finalize) `file, bytes, rows (excl. header), min_block, max_block`.

## 6. `rsr-episode/` (one-off, raw)

Context as given in the task (not verified or interpreted here):
- Uniswap V3 1% WETH/RSR pool: `0x11e26bbd1a5547895a50fc39a2d4c0025dec0bda`.
- Aerodrome V2 WETH/RSR pool: `0xd204058452f57464e0e5ab8c3cc9cbcb6b41d4ee`.
- Tx named in the task as the winning tx: `0x2310e683fe40902529cad07cde417d9062cc857c6052fb905101ce4b6d532e77` (block 51998757, tx index 1),
  from `0xf0523316cf23ef167d874fa030b2214280e38ee6` via contract `0xa05787285256c4ee18d7ed6865de2ddbb949c411`.

| file | content | source |
|---|---|---|
| headers.jsonl.gz | `eth_getBlockByNumber(n,false)` for n = 51998755..51998758, verbatim, one line per block | blastapi |
| blocks_full.jsonl.gz | `eth_getBlockByNumber(n,true)`: header plus full transaction objects (input, nonce, type, maxFeePerGas, maxPriorityFeePerGas, gas, value, accessList, signature), verbatim | blastapi |
| transactions_by_hash.jsonl.gz | `eth_getTransactionByHash` for every tx of the 4 blocks (1,100 lines), verbatim | blastapi (drpc fallback) |
| receipts.jsonl.gz | `eth_getBlockReceipts` for the 4 blocks, one receipt per line (1,100 lines), verbatim including logs | drpc (blastapi refused) |
| block_traces.jsonl.gz | `debug_traceBlockByNumber` with callTracer `{withLog:true}`, one line per block, verbatim result array | drpc |
| trace_winner.json | `debug_traceTransaction` callTracer withLog of the tx named above | drpc |
| pool_state.csv | `eth_call` at the END of blocks 51998754..51998758: V3 pool slot0/liquidity/fee/token0/token1/tickSpacing; Aerodrome pool getReserves/token0/token1/stable/factory; factory getFee(pool,stable). Column `raw_return_hex` is raw. `derived_decoded_words_base10` splits the return data into 32-byte words read as **unsigned** integers, so signed fields (e.g. slot0 tick, int24) need two's-complement reinterpretation | blastapi (archive) |
| errors.csv | calls that failed on an endpoint (4 x blastapi `eth_getBlockReceipts` HTTP 401, then served by drpc) | |
| trace_errors.csv | block-trace failures after retries (header only = none) | |

`block_traces.jsonl.gz` has two gzip members (confirmed 2026-10-01). The first run traced blocks 51998757-51998758, and its
lines have no `method` key. The second run traced 51998755-51998756 after a free-plan timeout, and its lines carry
`"method":"debug_traceBlockByNumber"`. `collect/rsr_traces.log` holds only the second run's output.
The pool state at the end of block 51998756 is the state before the first tx of block 51998757.
These four blocks are also in the census (stream `bf4`), with the census fields only (no tx objects, no traces).

## 7. Coverage limits and gaps

- **Chain**: Base only. Other chains (lines 4 and 6) are not in this folder.
- **Window**: only the contiguous range 51995609-52017160 (2026-09-30T15:02:45Z to 2026-10-01T03:01:07Z): 6 h of backfill plus
  the forward period up to stop block 52017160. There is no data older than block 51995609 and none newer than block 52017160.
- **Head lag / fetch time**: until the container restart the forward stream stayed 10 blocks behind the head. After the
  01:03Z restart it fetched blocks that were up to ~2 h old and caught up at ~1 block/s, so it was still behind the head at
  the end. Details are under "Run history". Blocks are taken as served at fetch time. Reorgs after fetch are not tracked,
  but parent-hash linkage is checked in `integrity.json` (0 mismatches).
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
- **Topic verification incomplete**: see the status line and section 5 (`verify_topics.py` stopped by the container restart;
  1 row `pending`, 4 rows with failed Blockscout windows). This affects only the `verified_example_*` / `verification_method`
  columns of `swap-topics.csv`, not the census or the candidate filter.
  *Corrected 2026-10-01 (fixup):* after the 2026-10-01 re-run, 0 rows are `pending`, and 1 row has a failed Blockscout window:
  `0x4be05c8d…` (Clipper), window 51507825-52007824, 12 read timeouts of 120 s. The enclosing window 42007825-52007824 of
  the same row was answered "No logs found".
- **Criterion B** counts only 3-topic ERC-20 `Transfer` events. It misses native ETH movements (no logs), ERC-1155/721 transfers,
  and tokens with non-standard transfer events.
- **Candidates are a filter, not a classification.** Membership is decided only by the log rule above and says nothing about a tx's
  purpose. A tx with fewer than 2 listed swap logs and fewer than 3 qualifying Transfer logs is not in the candidates files,
  whatever its purpose. All txs remain in `txs-*` for re-filtering by `to`/`from`/position.
- **Receipt field sets depend on the endpoint.** tenderly and publicnode were identical on a tested block. drpc receipts had the same
  key set in the smoke test. meowrpc (fewer fields) was not used. See `provenance-*` for which endpoint served each block.
- **drpc getLogs restriction**: address-less `eth_getLogs` on base.drpc.org was refused for ranges of 500 blocks and more on 2026-09-30 (100 blocks worked). Topic
  verification therefore used the Blockscout API. The first draft of `verify_topics.py` (drpc getLogs) was superseded before any output was kept.
- **Unrecoverable blocks**: none. `gaps-final.csv` lists the one failed block (51998605) as `recovered`.
- **Stop margin**: the forward stream continued 150 blocks past the head minus lag at the moment both engine sentinels were
  detected (02:56:28Z), to block 52017160.
- If the supervisor fails, `/home/user/dapparb/research-material/.sentinels/BASE_CENSUS.FAILED` holds the reason. No such file
  exists for this run. The streams resume from their checkpoints when `supervisor.py` is re-run.
- **Local-only state**: `collect/state/` and `collect/__pycache__/` are git-ignored. How to regenerate each file is listed
  under "Verified inventory (2026-10-01)".

## Verified inventory (2026-10-01)

Checked on 2026-10-01 between ~03:18Z and ~03:26Z, over every file in this folder (recursive, 89 files). (Fixup 2026-10-01:
the verify_topics.py re-run changed `swap-topics.csv` and `collect/verify_topics.py` and added `collect/verify_topics_rerun.log`.
These three have "row added 2026-10-01 fixup" rows in the table below, so the folder now holds 90 files.) Method:
- Lines: newline count, streamed. For `.gz` files it counts the decompressed content. CSV line counts include the header.
  "(+1 unterminated)" marks a file whose last line has no trailing newline.
- Every `.gz` file passed `gzip -t` and a full streamed decompression.
- **Every** line of every `.jsonl.gz` file parses as JSON, 0 failures. For the 11 candidates files that is 481,183 lines, all
  parsed, which is more than the required sample of 1,000 per file. Every `.json` file parses.
- Every CSV (plain or gzipped) parses with Python `csv`. All rows have the header's field count, and no part has a repeated
  header row.
- The data rows, byte sizes and min/max block numbers of the 32 files in `data/file_index.csv` match the files.
- The rows of the 6 local-only `collect/state/blocks-parts/*` files (21,552 in total) are, as a set, identical to the rows of
  `blocks.csv.gz` (21,552 rows, sorted, one per block).
- The largest file is `data/candidates-bf-0001.jsonl.gz` (89,975,717 bytes). No file exceeds 90 MB.
- sha256 is given for every file.

"committed" means tracked in git; `git status` was clean for this folder before this manifest update (HEAD `002dc86`).
"local-only" means git-ignored (`research-material/**/collect/state/`, `research-material/**/__pycache__/`), and the R-codes
below the table say how to regenerate each local-only file.

| file | bytes | lines | sha256 | git |
|---|---|---|---|---|
| `MANIFEST.md` | (this file) | | | committed (earlier version) |
| `blocks.csv.gz` | 1251161 | 21553 | `c7ad84d421261b34ed61f796c6947ef2ffee71e1f6fcd8222a4dd2708cd2f914` | committed |
| `gaps-final.csv` | 146 | 2 | `27578f5d5b0eee2fd94dba9e83624e9ad9844c2d05de4cabb014e8c763519149` | committed |
| `gaps.csv` | 156 | 2 | `9cf6fe12a88d0b5792fca384139ea17ce1e062a5538d9226c597da927a1aebac` | committed |
| `integrity.json` | 711 | 22 (+1 unterminated) | `68ce55941f6efc1cce52d56bcc122484333f33ce78b690aae5172eb4eb8a7da8` | committed |
| `swap-topics.csv` | 15298 | 27 | `bf81ba61d0203b055a56b1b95f4e7ead174c011acc55ea86d9c86813c40a2052` | committed |
| `swap-topics.csv` (row added 2026-10-01 fixup; supersedes the row above, which is the committed version, after the verify_topics.py re-run) | 15513 | 27 | `ec713da5c98a68f28ad25e723c9223d8a08ef8438eb71e2b43c122b6fd9f082b` | modified, not committed |
| `data/candidates-bf-0001.jsonl.gz` | 89975717 | 76441 | `88f1240a70a2891a51248291fa4fd5339f5472115f50c4d644ea0e837d101e4c` | committed |
| `data/candidates-bf-0002.jsonl.gz` | 13046151 | 10537 | `c5fb4456259e6260c0f7d1ba5e1580246a90be06cc354b89482de79fec8a611d` | committed |
| `data/candidates-bf2-0001.jsonl.gz` | 89469113 | 73724 | `0d86edcb15a274c7eb6e87525aa3ac3aad3bceea29ae8165b6d3789d7dc6ae9d` | committed |
| `data/candidates-bf2-0002.jsonl.gz` | 89615211 | 66992 | `eabf57c18fea0c9272712e399b146cd4ec91779c9ee0c49da40b7747a842fc45` | committed |
| `data/candidates-bf2-0003.jsonl.gz` | 14738382 | 10984 | `a9f402e832791c1dd9aa980535f56a8e0fc0d649bb615d8798af2ca0c75a7e36` | committed |
| `data/candidates-bf3-0001.jsonl.gz` | 36328805 | 30655 | `fbf765737280d4ce51840c5cfd862ca568a3ab91704bda397e2ed4e98af58447` | committed |
| `data/candidates-bf4-0001.jsonl.gz` | 6054063 | 4782 | `f5216b11a211c744c0547b31ed520b73c37158d74f20eb4951b80bb8f76afbbc` | committed |
| `data/candidates-fw-0001.jsonl.gz` | 89487257 | 69820 | `b3576bc5ca3b42111f077d31732fced55f8c62472a4444804244f1ac2b7cd901` | committed |
| `data/candidates-fw-0002.jsonl.gz` | 89390492 | 73318 | `327936d77aecf3b26de75f30165b5316707a6a5695db203db04c62cbfe847760` | committed |
| `data/candidates-fw-0003.jsonl.gz` | 72296298 | 63910 | `45f3db6274882f502957d7da512ea39bfb57ccf0e614bfe33eaad7d941d06b08` | committed |
| `data/candidates-gf1-0001.jsonl.gz` | 48166 | 20 | `130a9a20b27134ed07512b674d47ce2158c28ff44b54374c03dde809a403dbb8` | committed |
| `data/file_index.csv` | 2025 | 33 | `4bbdaace5575bc7c8801db149f16cce4824570d0476fa6add895c486e23d91ec` | committed |
| `data/provenance-bf-0001.csv.gz` | 10500 | 2040 | `36669629dc631683f19a1209c1e96672bf46d95002d8154f1ab915cf5d9de16e` | committed |
| `data/provenance-bf2-0001.csv.gz` | 35866 | 6401 | `e01e6b9a563d918a8249cc7a2f400b642cb7e54c592dbf2bfaf00957fd718120` | committed |
| `data/provenance-bf3-0001.csv.gz` | 6737 | 1201 | `f760567915bfe2aec65b90bccef7bc82a67d1f471cb5ae7fb03bd7725dc165fe` | committed |
| `data/provenance-bf4-0001.csv.gz` | 1125 | 192 | `faf7e56cd23b6b48203cfe28238b6ccfb145291f8fb74a56a28c690ca90357e9` | committed |
| `data/provenance-fw-0001.csv.gz` | 206251 | 10480 | `a50d171fd431811b3c6006ebca417768d51441007f5f775a4f4d754e208d1d32` | committed |
| `data/provenance-gf1-0001.csv.gz` | 137 | 2 | `f79a55a159411224e4ce3a833273e8b90e98557759f609e192a76136245076d1` | committed |
| `data/reverted-bf-0001.csv.gz` | 5586973 | 75417 | `3f9dac57487895b3eb6430540cb06a445fc9233efc659661362bc72479b87572` | committed |
| `data/reverted-bf2-0001.csv.gz` | 9526923 | 150437 | `cbf5ae16b304fb4cb0a979fd489de5c551a7c09dfdaa30738dc00fcbcf3f1ad3` | committed |
| `data/reverted-bf3-0001.csv.gz` | 2414348 | 36118 | `919f515dd151076bdd5b1be39e2a2bd55fa0a6935695c86063eb25f3a5e3e3a9` | committed |
| `data/reverted-bf4-0001.csv.gz` | 391189 | 5829 | `1b0f2c2d19f93ffcce24c2b7e6b2513f6f014ce989daa830830ae0c5c7e6f5c4` | committed |
| `data/reverted-fw-0001.csv.gz` | 15844055 | 249816 | `ee684f63574cc0bd0ad8691907f61c9c3818cca6e96ffd05209d0a931c2bab5a` | committed |
| `data/reverted-gf1-0001.csv.gz` | 1246 | 17 | `368f23b45797e3fee574aa2d45e9b54cf90cac990aaf3d98815b6e83641b1b15` | committed |
| `data/txs-bf-0001.csv.gz` | 68710314 | 849510 | `1f7efa3a370cf82881fffa6df1b1a2d05e4856b41889f7135b3f21c3d9845cd4` | committed |
| `data/txs-bf2-0001.csv.gz` | 89183753 | 1136688 | `abba7f9226763d1498dd6fddb30714e509b39c19dfb1f8a61042f081a20b0554` | committed |
| `data/txs-bf2-0002.csv.gz` | 11671888 | 152008 | `6ea1daf3d1456bbfad1bb05090a3e920524e74a1479789c8087c3c824c878c34` | committed |
| `data/txs-bf3-0001.csv.gz` | 22944030 | 288166 | `8040229b924c29542d9be986e191eeea3315be3ec189cb7843aed1976297dcbc` | committed |
| `data/txs-bf4-0001.csv.gz` | 3502280 | 43634 | `2a48addecfcd11c36bcb3b0eb2728bdbfe46cdb05cfb754aa7a053d3b0268c18` | committed |
| `data/txs-fw-0001.csv.gz` | 89187758 | 1132644 | `dd11ee470cb843ee9551cf3c3a26a367c459d0a0dbeffc87fdee57bf6683169d` | committed |
| `data/txs-fw-0002.csv.gz` | 62363641 | 810134 | `a7de741a1ab00f1fec49b285b80045fdfd97de26f8cea4a6ec572797ec157b08` | committed |
| `data/txs-gf1-0001.csv.gz` | 15894 | 186 | `8aca8614c45858006b81117ea0c001c1fcceb5336cd1ee1c4693d6c4926d8128` | committed |
| `rsr-episode/block_traces.jsonl.gz` | 1104899 | 4 | `f59c51d5d4455ae1705aee7275e2459b6951a8fa1a46f230761fe4bf7c25c448` | committed |
| `rsr-episode/blocks_full.jsonl.gz` | 355962 | 4 | `5e47c27b6222af3c26d94618264f5b14e7631a33681022c266f0a7e09d0e273d` | committed |
| `rsr-episode/errors.csv` | 535 | 5 | `9209852deea8d4ccbcbff964f7878209dd19bc2bb33dd42bbc0da0f4b083271b` | committed |
| `rsr-episode/headers.jsonl.gz` | 45337 | 4 | `0a6f10b861370ee146538ad52f5086bed3e335868c31beac5949d627390ac5c5` | committed |
| `rsr-episode/pool_state.csv` | 14050 | 61 | `6b112495715138c9da1f2315150fb7579968e392b4920d6dd389d04fcd8290b4` | committed |
| `rsr-episode/receipts.jsonl.gz` | 365792 | 1100 | `07d57c92271385e3d578a1c72487be004f787dad2bdc40a347439c61a6dcb26a` | committed |
| `rsr-episode/trace_errors.csv` | 25 | 1 | `b4418de419ecec62d40b0194712859559ae9e00b5702307b9de02205e9952dfb` | committed |
| `rsr-episode/trace_winner.json` | 13038 | 0 (+1 unterminated) | `dcef5e82de43f0dab58e7a92eff6df593e8b95d0566b94edd18cc43379e53c09` | committed |
| `rsr-episode/transactions_by_hash.jsonl.gz` | 352294 | 1100 | `cf9168bcd675cebe165687c334b01c8846bdba1c8e47ed267d536713cbcc73ff` | committed |
| `collect/census.py` | 19637 | 458 | `ebb2589b8ee8134a443ab8d5265fbefadd0503ac0f2ee8b5f89c8d4964d2c9b5` | committed |
| `collect/census_bf.log` | 4961 | 28 | `a74545c4f097f1003319099ebe95db583acac7f7411ec774ae2554901ca16ccc` | committed |
| `collect/census_bf2.log` | 2720 | 15 | `3c38b808a99e55dda59352b355c5312a9b7e853e36ad21a215763200c3a40a30` | committed |
| `collect/census_bf3.log` | 874 | 4 | `c27ddb566410c87747799d97144fb3f6c309e25500d40d4e4da66b3051014668` | committed |
| `collect/census_bf4.log` | 537 | 2 | `5f9868e7749a36eafb03b001330a6809a012e7837418769b838facb1428fc3ab` | committed |
| `collect/census_fw.log` | 42128 | 239 | `9af6891227f11d3a22aa05879553f25582ec60088a304bdd04b196457c869495` | committed |
| `collect/census_gf.log` | 481 | 1 | `bab8ddaece6d0fe963f964c2d92717bc823be96adbf137761d9cd904446cf713` | committed |
| `collect/census_gf1.log` | 542 | 1 | `4c75cd658781b2a73f20922d202ee02c462943ef5e3e684f0870a0b03ca466ca` | committed |
| `collect/finalize.py` | 8587 | 166 | `a7a4724ab246efa9ab2faaf2b79463f73b842dc0df7687aba1734fa321d802d2` | committed |
| `collect/rsr_episode.log` | 135 | 5 | `1672304f5723307a2ee7d75ad9ee15fc116661a6826125a07a730f2226619c17` | committed |
| `collect/rsr_episode.py` | 6556 | 124 | `cd90fedbc8de2b318eb3ace0697792da88cf381797fe210186be102572d87d5f` | committed |
| `collect/rsr_traces.log` | 40 | 2 | `440b6c69a74e80e362e79f37369934482ffc52a7729f062bfa4587f628d57cd9` | committed |
| `collect/rsr_traces.py` | 3441 | 54 | `4c605ff231079f0b5bf907d5ab7ee009d08da0c194dfc3a315c569caf2b352d0` | committed |
| `collect/supervisor.log` | 8077 | 54 | `53adf264d272f9c44603fff7df82236dee74be41620e8b51b40ee264e42ee56a` | committed |
| `collect/supervisor.py` | 7145 | 161 | `51923ce9a6b8b8891ae034e6a66d774ac8dfa86f8436eea2082946706539430e` | committed |
| `collect/swap_topics_used.csv` | 6708 | 27 | `6feaa987f672ad4a2f4f99d4b10402e804c1ba500e0d6a9d9563ce98095466c1` | committed |
| `collect/verify_topics.log` | 12624 | 110 | `2e4dcc3896ab354584cb127395c84059de01c928c37d30a1e510675913274f51` | committed |
| `collect/verify_topics.py` | 7121 | 148 | `7cf02f5874bed38d197e82fe1fcf6a74c59c35b24d4c93f4ea1bf17cd85a262b` | committed |
| `collect/verify_topics.py` (row added 2026-10-01 fixup; supersedes the row above, which is the committed version) | 9185 | 173 | `088f3eb9ded666c89e4d8461796e68f0247f4e546ffedf6224fa0b3d98497031` | modified, not committed |
| `collect/verify_topics_rerun.log` (row added 2026-10-01 fixup) | 13829 | 100 | `9bc2e0e4df4f71e59c639642ed65ea75f57d8a5e00a770510300557b73c4165a` | new, not committed |
| `collect/__pycache__/census.cpython-311.pyc` | 38360 | n/a (binary) | `2cfdf6a21c5d8cf56d5b13aef8003ef56e892ecc25b5aff041bfaf5191f9fc91` | local-only (R1) |
| `collect/state/bf.ckpt.json` | 537 | 35 (+1 unterminated) | `ef1cfcbd91d461bc1c193816fb30bc15d74ff2a0562154f4978119a08432fb5e` | local-only (R3) |
| `collect/state/bf2.ckpt.json` | 553 | 36 (+1 unterminated) | `4790a19ac400c4037eeeef8a99f23887c5587c4769ab20e804abfa3dfa105cf8` | local-only (R3) |
| `collect/state/bf3.ckpt.json` | 539 | 35 (+1 unterminated) | `54d994bc56582b193accb9442d643c56bed97ed67cadac7eed6eb22a37b109a3` | local-only (R3) |
| `collect/state/bf4.ckpt.json` | 535 | 35 (+1 unterminated) | `37a506d0332feacffde95781d9077b5c94e57d252b28650741d2bfc241783571` | local-only (R3) |
| `collect/state/blocks-parts/blocks-bf-0001.csv.gz` | 181028 | 3000 | `3640a1b45aeca3ac8bbe11c54ed2bdd61213293ed60f3a640a0628ef9c3d941e` | local-only (R2) |
| `collect/state/blocks-parts/blocks-bf2-0001.csv.gz` | 384225 | 6401 | `0310884942523406d5543debfe0f8ea1cdfdfcc80fcfd3eec17343da3aa5b780` | local-only (R2) |
| `collect/state/blocks-parts/blocks-bf3-0001.csv.gz` | 72414 | 1201 | `318f80b45e0e0167b68e738f17fc8aae356e22e7b087491fd5c972879508da21` | local-only (R2) |
| `collect/state/blocks-parts/blocks-bf4-0001.csv.gz` | 11640 | 192 | `71e38c41a13654dcab8287f23507104f40d95878130c0ebef4a0c50f36dc14df` | local-only (R2) |
| `collect/state/blocks-parts/blocks-fw-0001.csv.gz` | 811704 | 10762 | `4d9d00f85a497ef0197bb2c854cf79d96b73d410171fcf979e91f8eef339ab2e` | local-only (R2) |
| `collect/state/blocks-parts/blocks-gf1-0001.csv.gz` | 242 | 2 | `549128c6d9dc6b5e614a01285702ddbc71b7e649a1a88f4e3521c79337ca1242` | local-only (R2) |
| `collect/state/config.json` | 1792 | 45 (+1 unterminated) | `7a32acd2c1f97075379582f4e0e2f9c08ffceab203341ebd6ecd8ae176fbd906` | local-only (R5) |
| `collect/state/finalize_summary.json` | 587 | 17 (+1 unterminated) | `7e894277c353842d62ce2af62d597a50ee9accc124d0dce7f21dc6d6c02f29d5` | local-only (R6) |
| `collect/state/first_seen_bf.json` | 5414 | 111 (+1 unterminated) | `2034383491bd61ca87880bc3ace9750c8bf0b938cfb626e4eba96fec22a3d914` | local-only (R4) |
| `collect/state/first_seen_bf2.json` | 5168 | 106 (+1 unterminated) | `224333f7e589b2ff9702f8f43fc158aded1ea93400afd0ddf92d293b4233133a` | local-only (R4) |
| `collect/state/first_seen_bf3.json` | 4676 | 96 (+1 unterminated) | `6bd087f83938ec287490e5b9d587760aeb882367b0543e7147ea060680f340a0` | local-only (R4) |
| `collect/state/first_seen_bf4.json` | 4184 | 86 (+1 unterminated) | `418f910873febd38291bd3c1a1328769fd324f775156aeef7c2b778040885999` | local-only (R4) |
| `collect/state/first_seen_fw.json` | 5414 | 111 (+1 unterminated) | `16df91caaf54905082a91bd1a5bb26175646850c7a3da8f05d3e2de3afa1270c` | local-only (R4) |
| `collect/state/first_seen_gf1.json` | 986 | 21 (+1 unterminated) | `f3358cf81e6aae3b1e73d14094c34e10f2bf1ab160f2e34a378ebdf9ac834b53` | local-only (R4) |
| `collect/state/fw.ckpt.json` | 1248 | 52 (+1 unterminated) | `18c290bf619357fae0a76baabbf1059da98ec188514c4a28dc27fc9a9a7575c3` | local-only (R3) |
| `collect/state/gf.ckpt.json` | 537 | 41 (+1 unterminated) | `64e0e2128501bf5e94f267706617c6e249f1e8f825a683d580957bce4b7805ec` | local-only (R3) |
| `collect/state/gf1.ckpt.json` | 598 | 42 (+1 unterminated) | `9645cf3a9415ad8b9c382ff9d72f6993a1d3b0d2ed97d886c7cfca6c7a1283fc` | local-only (R3) |
| `collect/state/gf1_blocks.txt` | 9 | 1 | `5be90859b87c357def1b9a2c7bb61ed47a407d175a5a6d7d6729995205a80e96` | local-only (R7) |
| `collect/state/gf_blocks.txt` | 9 | 1 | `5be90859b87c357def1b9a2c7bb61ed47a407d175a5a6d7d6729995205a80e96` | local-only (R7) |

How to regenerate the local-only files (all in `collect/`):
- **R1** `__pycache__/census.cpython-311.pyc`: Python 3.11 bytecode cache of `census.py`, written by the interpreter on import
  (file time 2026-09-30T21:11Z). Not data. Regenerate with `python3 -c 'import census'`.
- **R2** `state/blocks-parts/blocks-<stream>-0001.csv.gz`: the per-stream block rows that `census.py` wrote to `data/` and
  `finalize.py` moved here. Their rows, taken together, are identical to the rows of the committed `blocks.csv.gz` (checked
  above). To regenerate, either re-run `census.py --stream <s>` over the stream's range (section 3), or split `blocks.csv.gz` by
  the stream ranges: bf 51995609-51998608 without 51998605, gf1 51998605, bf4 51998609-51998799, bf3 51998800-51999999,
  bf2 52000000-52006399, fw 52006400-52017160. The split gives the same rows, but the gzip member layout differs, so the sha256
  differs. `finalize.py` needs these files (section 4).
- **R3** `state/<stream>.ckpt.json` (bf, bf2, bf3, bf4, fw, gf, gf1): written by `census.py`. The final content of each is
  printed verbatim (as a Python dict) in the `stream done <stream> {...}` line of the committed `census_<stream>.log`. This
  was checked on 2026-10-01 to be equal to each file. The fw line includes `notes` with the cleared stop condition. To
  regenerate, write the dict from that line as JSON.
- **R4** `state/first_seen_<stream>.json`: written by `census.py`. For each listed swap topic it holds the first occurrence
  seen in that stream. The earliest occurrence over all streams is in the committed `swap-topics.csv` (`census_first_seen_*`).
  Regenerate by re-running the stream over its range.
- **R5** `state/config.json`: written by `supervisor.py` at the first start, then edited by hand at 21:12Z, 21:26Z and 21:49Z
  (the `*_split_note` keys). Its full content is printed verbatim (as a Python dict) in the committed `supervisor.log` line
  `2026-10-01T01:03:10Z resuming with config {...}`, which was checked to be equal to the file. Regenerate by writing that
  dict as JSON.
- **R6** `state/finalize_summary.json`: written by `finalize.py`. It is equal to the `summary` object of the committed
  `integrity.json` (checked). Regenerate with `python3 finalize.py`, which needs R2, R3 and R5.
- **R7** `state/gf1_blocks.txt`, `state/gf_blocks.txt`: block list for the gap-fill streams, content `51998605` plus a newline.
  `gf1_blocks.txt` was written by hand (section 4) and `gf_blocks.txt` by `supervisor.py` from `gaps.csv`. Regenerate with
  `echo 51998605 > state/gf1_blocks.txt` (and the same for `gf_blocks.txt`).

## Corrections made on 2026-10-01 (summary)

- Status: a status line was added at the top: COMPLETE WITH GAPS. The block census is complete; the gap is the unfinished
  topic verification in `swap-topics.csv`. The AUTO-STATUS block written by `finalize.py` is kept unchanged, and its status
  word covers the block census only.
- Facts added: the container restart (~22:58Z, restart 01:03Z, fw resumed at 52009870 with no gap); the invalid
  `V4LIVE.DONE` and the cleared first stop condition (01:57:30Z, stop_block 52015391, cleared 02:04:41Z); the valid stop at
  02:56:28Z (stop_block 52017160); the final range, block counts and time windows; when blocks were fetched after the restart.
- Question-line keys Q1-Q10 replaced by line numbers 1-8 (section 1). The old-to-new map is given there, and the earlier file
  assignments are kept.
- Section 1: the table cell "block base fee, timestamps, tx counts for ordering/fee context" was replaced by a list of files
  and fields.
- Section 4: "finalize can be re-run safely at any time after the streams are done" was qualified: it needs the local-only
  `collect/state/`. The reproduction `stop_block` is filled in (52017160). The note on the 01:03Z restart was added.
- Section 5: "So every file stays well below 90 MB" was corrected. A part can exceed 85 MiB by up to one chunk, and the largest
  file is 89,975,717 bytes, below 90 MB.
- Section 5: "`collect/verify_topics.py` was still running when this manifest was written" was replaced by its actual end:
  killed at ~22:58Z, not re-run.
- Section 6: "Winning tx" is now "Tx named in the task as the winning tx", and `trace_winner.json` is described the same way.
- Section 7: "Window ... (7 h after launch at most)" now gives the actual end block. "The forward stream stays 10 blocks
  behind the head" now covers the catch-up after the restart. "Unrecoverable blocks, if any" now reads none.
- Added the "Verified inventory (2026-10-01)" table, with regeneration notes for the local-only files.

## verify_topics.py re-run (2026-10-01)

Done by a fixup agent to finish the topic verification that the container restart interrupted. It rewrote
`swap-topics.csv`, which this task allowed. No census data file was touched.

**Method and endpoints.** The method is the one in the docstring of `collect/verify_topics.py`:
- Blockscout `https://base.blockscout.com/api?module=logs&action=getLogs&fromBlock=..&toBlock=..&topic0=..` over the newest
  1k, 16k, 500k and 10M blocks before the pinned head. One request in flight, 3 s pause before each request, 120 s timeout.
- The newest returned log is re-checked in `eth_getTransactionReceipt` on `https://gateway.tenderly.co/public/base`
  (fallbacks publicnode, drpc; no fallback was needed).

**Pinned head**: 52007824, the same head as the first run (2026-09-30T21:50:36Z), passed as `--head 52007824`. All 26 rows
therefore use the same windows: 52006825-52007824, 51991825-52007824, 51507825-52007824 and 42007825-52007824.

**Script changes** (`collect/verify_topics.py`, before the first pass and between passes 1 and 2; the committed version is the
"committed" inventory row):
1. Optional `--head N`. Without it the head is live `eth_blockNumber - 20`, as before.
2. HTTP 429 handling. Blockscout's 429 answers carry `x-ratelimit-limit: 10` and `x-ratelimit-reset` (ms until the quota
   resets). Such a 429 is now waited out (reset + 5 s, at most 1,800 s), up to 8 times per window, without using one of the 6
   tries.
3. Resume also keeps rows whose "no log found" search covered all 4 windows of the same head with no failed window. Rows with
   a verified example were already kept.
The output format and the `census_*` column handling are unchanged.

**Passes** (all logged in `collect/verify_topics_rerun.log`, appended; the first run's `collect/verify_topics.log` is unchanged):

| pass | UTC (2026-10-01) | what happened |
|---|---|---|
| 1 | 04:41:16Z-~04:45Z | Original 429 handling, plus `--head` and the old resume rule. Re-searched `0xd013ca23…` (4 windows, no log), `0x0fe977d6…` (example found in the 1k window) and `0x29872dc2…` (4 windows, no log, same as before). Then 6 HTTP 429 retries for `0xefce4460…` window 1. The process (pid 5779, started by the fixup agent) was stopped with SIGTERM to add the 429 handling. The rows already written were kept |
| 2 | 04:45:52Z-05:17:17Z | pid 7539. `0xefce4460…`: 4 windows, no log. `0x4be05c8d…`: one 429 wait of 805 s (`x-ratelimit-reset` 799,631 ms). Window 51507825-52007824 then failed after 6 read timeouts (120 s each); the 1k, 16k and 10M windows answered "No logs found". `0xa4228e1e…`: example found in the 16k window |
| 3 | 05:17:27Z-05:34:26Z | pid 10794, retry of the row with a failed window. `0x4be05c8d…` window 51507825-52007824 failed again (6 read timeouts); the other 3 windows again "No logs found". The row is unchanged from pass 2 |

**Rows changed in `swap-topics.csv`** (the other 21 rows are byte-identical; header and the `census_first_seen_*` columns
unchanged):

| topic0 | signature | before | after |
|---|---|---|---|
| `0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b` | TokenExchangeUnderlying(address,int128,uint256,int128,uint256) | no log found; 2 windows failed | no log found; all 4 windows searched |
| `0x0fe977d619f8172f7fdbe8bb8928ef80952817d96936509f67d66346bc4cd10f` | Swap(address,address,uint24,bool,uint256,uint256,int24) | no log found; all 4 windows failed | example tx `0xa36abbf2414ccdf99bc33d0ea0accd3ab1f696b1fe0fd278dcafd5da5a16ec36`, block 52007512, emitter `0xdb5d62f06eecef0da7506e0700c2f03c57016de5`, log index 172 (window 52006825-52007824) |
| `0xefce44603748d0427b3ebdff9018999a004811d9cfe45e6bbf7357b2547bae50` | Swap(bytes32,address,uint24,bytes32,uint24,uint16) | no log found; 2 windows failed | no log found; all 4 windows searched |
| `0x4be05c8d54f5e056ab2cfa033e9f582057001268c3e28561bb999d35d2c8f2c8` | Swapped(address,address,address,uint256,uint256,bytes) | no log found; all 4 windows failed | no log found; windows 52006825-52007824, 51991825-52007824 and 42007825-52007824 searched; **failed: 51507825-52007824** |
| `0xa4228e1eb11eb9b31069d9ed20e7af9a010ca1a02d4855cee54e08e188fcc32c` | Swap(address,address,int256,int256) | `pending: collect/verify_topics.py running` | example tx `0x3081b246b4f9e204eb5bbc3ad84d3c92388ab9b99eea9ca37db505c66847e588`, block 51997691, emitter `0x01b7c0d053eb4b8862c69172ac06a7653d83641f`, log index 715 (window 51991825-52007824) |

`0x29872dc2…` was searched again in pass 1 with the same result: no log found, all 4 windows searched. Its row text is
unchanged.

**Result**: 26 rows (27 lines with the header).
- 0 rows `pending`.
- 22 rows with `verified_example_*`.
- 4 rows "no log found". 3 of them searched all 4 windows. One (`0x4be05c8d…`) has a failed window.

**Hand check**: the two new examples were re-read from tenderly with `eth_getTransactionReceipt`:
- `0x3081b246…`: block 51997691, status 1, log 715 at `0x01b7c0d0…` with topic0 `0xa4228e1e…`;
- `0xa36abbf2…`: block 52007512, status 1, log 172 at `0xdb5d62f0…` with topic0 `0x0fe977d6…`.

**Command** (from `collect/`): `setsid nohup python3 -u verify_topics.py --head 52007824 >> verify_topics_rerun.log 2>&1 < /dev/null &`.
The run is resumable: running it again re-queries only the `0x4be05c8d…` row.

**Coverage limits**:
- The Blockscout window 51507825-52007824 for `0x4be05c8d…` (Clipper) could not be read: 12 read timeouts over passes 2 and
  3. The enclosing 10M window 42007825-52007824 was answered "No logs found" in both passes.
- As before, an example is the newest log in the first window that has one. "No log found" covers only the 4 windows, not
  blocks before 42007825.
- Blockscout's limit observed in the headers: `x-ratelimit-limit` 10, with a reset of up to ~15 min.
- New and changed files are not committed: `swap-topics.csv` and `collect/verify_topics.py` are modified,
  `collect/verify_topics_rerun.log` is new. Their sizes and sha256 are in the "row added 2026-10-01 fixup" rows of the inventory.
