# 00-prior-runs: raw data from the earlier sessions of 2026-09-30

Status: COMPLETE WITH GAPS (static copies; inventory verified 2026-10-01). Gaps:
(Gap 1 removed 2026-10-01: the ledgers of XDP senders 0x000000c557fa9a96d66cd6371abde62d879d0e61 and
0x3be22b314654c396a12c5e8d79abdd65aac3caaf, previously "computed but not saved", were recomputed as raw per-block balance
ledgers plus receipts; see the section "competitor-ledgers/: recomputed XDP-sender ledgers (added 2026-10-01)". The other
gaps keep their numbers.)
2. competitor-ledgers/mine.json holds only `amountIn` and the off-chain value `mine`; the on-chain `getAmountOut` values
   and the pool address are not stored in the file.
3. research-runs: no cextri .jsonl (the original `bot/data/cextri.jsonl` is 0 bytes); only `cextri.log.gz` exists.
4. Earlier-session outputs that exist only in the local, git-ignored `bot/data/` and were NOT copied here:
   `dry-blocks-long3.log` (9 bytes, content `EXIT 143`), `live-base-blocks-long2.jsonl`, `live-base-blocks-long3.jsonl`,
   `live-base-blocks-long4.jsonl` (0 bytes each).
   (Corrected 2026-10-01, block-scans fixup: this item also listed the `scan-*` block-scan files (`scan-base.jsonl`,
   `scan-base-run1..3.log`, `scan-base-run4.jsonl/.log`, `scan-base-longtail.jsonl/.log`, `scan-arb.jsonl/.log`,
   `scan-arb2.jsonl/.log`, `scan-mainnet.jsonl/.log`), `prof.log` and `repro.log` as not copied. That is no longer true:
   all 16 were copied (gzip) to `block-scans/` on 2026-10-01 by the main session, commit 9c8a37c. See the sections
   "block-scans/ (added 2026-10-01 by the main session)" and "Verified inventory (2026-10-01)", and "block-scans/
   fixup (2026-10-01)" at the end of this file.)
   Fresh block scans are in `research-material/07-other-chains-engine/scans/`.

No collector sentinel exists for this folder (it was not produced by a collector). Collected by the main session; files
are gzip copies of what the earlier runs wrote. Descriptions state how each file was produced. They contain no findings.
(Corrected 2026-10-01: six files in competitor-ledgers/ — `ledger_0x000000c5.raw.csv.gz`, `ledger_0x3be22b31.raw.csv.gz`,
`receipts_0x000000c5.csv.gz`, `receipts_0x3be22b31.csv.gz`, `receipts_0x000000c5.full.jsonl.gz`,
`receipts_0x3be22b31.full.jsonl.gz` — are not copies of earlier-run output; they were collected on 2026-10-01 by
`competitor-ledgers/collect/xdp_ledgers.py`, described in the section added at the end of this file.)

All data files are stored gzip-compressed; in the sections below a name without `.gz` (e.g. `live-base.jsonl`) refers
to the `.gz` file in this folder. Verified 2026-10-01: for the 32 files in engine-runs/ and research-runs/, the
decompressed content is byte-identical (sha256) to the original of the same name in `bot/data/`. The originals of
competitor-ledgers/, misc/ and papers-fetched-earlier/ are no longer on disk, so those copies could not be compared.

## Question lines served

Mapping only (question line number → files in this folder).

| Line | Files |
|---|---|
| 1 | engine-runs/dry-all.log.gz, engine-runs/dry-all-v0.log.gz, engine-runs/live-base-all.jsonl.gz, engine-runs/live-base-all-v0.jsonl.gz, engine-runs/dry-blocks-long5.log.gz, misc/geckoterminal-top-pools-base.json.gz, misc/v4-poolmanager-logs-sample.jsonl.gz, misc/section-2.6-draft.md |
| 2 | engine-runs/dry-all.log.gz, engine-runs/dry-all-v0.log.gz, misc/section-2.6-draft.md |
| 3 | engine-runs/dry-all.log.gz, engine-runs/dry-all-v0.log.gz, engine-runs/live-base-all.jsonl.gz, engine-runs/live-base-all-v0.jsonl.gz, misc/section-2.6-draft.md |
| 4 | research-runs/crosschain.jsonl.gz, research-runs/crosschain.log.gz, misc/defillama-arbitrum-timeboost.json.gz, block-scans/scan-arb.jsonl.gz, block-scans/scan-arb.log.gz, block-scans/scan-arb2.jsonl.gz, block-scans/scan-arb2.log.gz, block-scans/scan-mainnet.jsonl.gz, block-scans/scan-mainnet.log.gz, block-scans/scan-base.jsonl.gz, block-scans/scan-base-run1.log.gz, block-scans/scan-base-run2.log.gz, block-scans/scan-base-run3.log.gz, block-scans/scan-base-run4.jsonl.gz, block-scans/scan-base-run4.log.gz, block-scans/scan-base-longtail.jsonl.gz, block-scans/scan-base-longtail.log.gz |
| 5 | engine-runs/live-base-all-v0.jsonl.gz, engine-runs/dry-all-v0.log.gz, competitor-ledgers/competitor_txs.json.gz, competitor-ledgers/competitor_pnl.json.gz, competitor-ledgers/competitor_perblock.json.gz, competitor-ledgers/arbers_XDP.json.gz, competitor-ledgers/arbers_WETHUSDC.json.gz, competitor-ledgers/ledger_0x778951.json.gz, competitor-ledgers/ledger_0x0190f0.json.gz, competitor-ledgers/ledger_0x000000c5.raw.csv.gz, competitor-ledgers/ledger_0x3be22b31.raw.csv.gz, competitor-ledgers/receipts_0x000000c5.csv.gz, competitor-ledgers/receipts_0x3be22b31.csv.gz, competitor-ledgers/receipts_0x000000c5.full.jsonl.gz, competitor-ledgers/receipts_0x3be22b31.full.jsonl.gz, misc/v4-poolmanager-logs-sample.jsonl.gz, misc/section-2.6-draft.md |
| 6 | — (no file in this folder) |
| 7 | papers-fetched-earlier/ (all 8 files), misc/defillama-arbitrum-timeboost.json.gz |
| 8 | engine-runs/dry-all.log.gz, engine-runs/live-base-all.jsonl.gz, engine-runs/dry-all-v0.log.gz, engine-runs/live-base-all-v0.jsonl.gz, engine-runs/dry-blocks-long5.log.gz, engine-runs/live-base-blocks-long5.jsonl.gz, misc/v4-poolmanager-logs-sample.jsonl.gz, misc/section-2.6-draft.md, block-scans/ (all 16 files: the 14 `scan-*` files listed under line 4, plus block-scans/prof.log.gz and block-scans/repro.log.gz) |

Not mapped to a question line: engine-runs/live-base.jsonl.gz, live-base-validate.jsonl.gz, live-base-long.jsonl.gz,
live-base-logs.jsonl.gz, live-base-blocks-long.jsonl.gz, dry-validate.log.gz, dry-long.log.gz, dry-flashblocks-run1.log.gz,
dry-logs.log.gz, dry-blocks-long.log.gz, dry-blocks-long2.log.gz, dry-blocks-long4.log.gz, pipeline.log.gz, arbtest.log.gz,
lev.log.gz; competitor-ledgers/mine.json.gz; research-runs/cexcex.*, cextri.log.gz, feetiming.*, leadlag.*, leadlag-multi.*.

(Corrected 2026-10-01: this section previously quoted question text and described runs; it is now a numbered mapping.)

Files added 2026-10-01 (xdp-ledgers fill), one row per file:

| File | Line |
|---|---|
| competitor-ledgers/ledger_0x000000c5.raw.csv.gz | 5 |
| competitor-ledgers/ledger_0x3be22b31.raw.csv.gz | 5 |
| competitor-ledgers/receipts_0x000000c5.csv.gz | 5 |
| competitor-ledgers/receipts_0x3be22b31.csv.gz | 5 |
| competitor-ledgers/receipts_0x000000c5.full.jsonl.gz | 5 |
| competitor-ledgers/receipts_0x3be22b31.full.jsonl.gz | 5 |
| competitor-ledgers/collect/ (xdp_ledgers.py, verify_xdp_ledgers.py and their logs, token_decimals.log) | — (provenance only) |

Files in block-scans/ (copied 2026-10-01 by the main session, commit 9c8a37c; mapped 2026-10-01 in the block-scans fixup),
one row per file:

| File | Line |
|---|---|
| block-scans/scan-arb.jsonl.gz | 4, 8 |
| block-scans/scan-arb.log.gz | 4, 8 |
| block-scans/scan-arb2.jsonl.gz | 4, 8 |
| block-scans/scan-arb2.log.gz | 4, 8 |
| block-scans/scan-mainnet.jsonl.gz | 4, 8 |
| block-scans/scan-mainnet.log.gz | 4, 8 |
| block-scans/scan-base.jsonl.gz | 4, 8 |
| block-scans/scan-base-run1.log.gz | 4, 8 |
| block-scans/scan-base-run2.log.gz | 4, 8 |
| block-scans/scan-base-run3.log.gz | 4, 8 |
| block-scans/scan-base-run4.jsonl.gz | 4, 8 |
| block-scans/scan-base-run4.log.gz | 4, 8 |
| block-scans/scan-base-longtail.jsonl.gz | 4, 8 |
| block-scans/scan-base-longtail.log.gz | 4, 8 |
| block-scans/prof.log.gz | 8 |
| block-scans/repro.log.gz | 8 |

`misc/section-2.6-draft.md` appears in the rows above as prior session text, not data: prose with conclusions written by
the earlier session (see misc/). (Label added 2026-10-01.)

## engine-runs/

Produced by `bot/src/main.ts` in `--mode dry` on Base (nothing was ever sent on-chain). The `.jsonl.gz` files hold one
JSON object per line. (Corrected 2026-10-01: the `.log.gz` files are not JSON-per-line; `dry-*.log` are pino-pretty
text with ANSI colour codes and multi-line records, each run ending with an `EXIT <code>` line where present;
`dry-logs.log` and `dry-validate.log` contain 2,137 and 136,230 NUL bytes respectively; `arbtest.log` and `lev.log` are
Foundry `forge test` output; `pipeline.log` is TAP output.)

Detection record fields: `t` (UTC ISO time written), `block`, `fb` (flashblock index, 0 in block/logs modes), `route`
(human-readable hops), `pools` (pool addresses in hop order; V4 pools as the first 20 bytes of the pool id), `token`
(start/profit token symbol), `amountIn` (human units of `token`), `predictedProfitUsd`, `gasUsd`, `netUsd` (searcher's
local-math prediction), `gapBps`, `sim` (on-chain `eth_call` simulation of the executor with a bytecode override:
`{profitUsd, gas, ms}` on success or `{error, ms}` on revert), optional `simLatest` (re-simulation at `latest`), `simNetUsd`
(simulated profit minus gas, present only when simulation succeeded). USD values use the engine's token→ETH price map
and the WETH/USDC price at the time. (Added 2026-10-01: some records in live-base-all*.jsonl and live-base-blocks-long*.jsonl
also include a `blacklisted` field; no record in any file of this folder contains `simLatest`.)

Provenance notes (facts about the code version that produced each file):
- Every file except `live-base-all.jsonl` and `dry-all.log` was produced BEFORE commit fd8d236 (anchored pricing). Their
  USD values for long-tail tokens come from the earlier unanchored price map (that map could price a token through any of
  its pools, without the minimum anchor-side depth that fd8d236 added; see misc/section-2.6-draft.md). (Reworded
  2026-10-01.) (Corrected 2026-10-01: the sentence previously excepted only `live-base-all.jsonl`. `dry-all.log` is the
  log of that same anchored-pricing §2.6 run (table below; pino pid 8931 throughout the log). Timestamps: the log's first
  line is 16:55:48 UTC (factory enumeration), its `searcher ready` line 17:03:54, the first record of `live-base-all.jsonl`
  17:04:25; commit fd8d236 has commit time 2026-09-30 16:57:59 UTC, so the log's first ~2 minutes precede that commit time.)
- Files produced before the revert-decoding rewrite show `unknown reason` in `sim.error`; later files show decoded errors
  (`CannotRepay(have,owed)`, `TransferFailed()`, `Error(UniswapV2: K)`, `revert 0xa932492f` = Aerodrome `K()`).

| File | What run | Universe / flags (from its log) |
|---|---|---|
| live-base.jsonl, live-base-validate.jsonl, live-base-long.jsonl (+ dry-validate.log, dry-long.log, dry-flashblocks-run1.log) | Flashblock-source dry runs, ~12:00–12:27 UTC | Long-tail universe; state refreshed through the preconf RPC (its request rate limit is discussed in docs/ANALYSIS.md §2.2–2.3) |
| live-base-logs.jsonl, dry-logs.log | First logs-source attempt, ~15:45 UTC | Short; process stopped |
| live-base-blocks-long.jsonl, dry-blocks-long.log, dry-blocks-long2.log, dry-blocks-long4.log | Blocks/logs-source attempts, 15:15–16:10 UTC (corrected from 15:43–16:10) | Runs 2 and 4 end with `self-check failed` and `EXIT 1`; the run-3 log (`EXIT 143` only) and the empty .jsonl of runs 2–4 were not copied (see Gaps) |
| live-base-blocks-long5.jsonl, dry-blocks-long5.log | §2.5 reference run, ~16:15–16:38 UTC, 22 min | 657 pools, event-driven state from block receipts |
| live-base-all-v0.jsonl, dry-all-v0.log | First `--universe all` run, 16:46–16:55 UTC | `--universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6`; 3,282 pools / 3,652 cycles after the depth filter; unanchored pricing |
| live-base-all.jsonl, dry-all.log | §2.6 run, 17:04–17:25 UTC, 21 min | Same flags, anchored pricing; 3,189 pools / 3,608 cycles |
| pipeline.log, arbtest.log, lev.log | Test logs (fork pipeline test, executor tests, leverage test) | — |

Verified coverage per run (2026-10-01; log span = first/last bracketed timestamp in the log; `searcher ready` values
copied from the log; record span = min/max `t` and `block` in the .jsonl):

| Log | Log span (UTC) | `searcher ready` tokens / pools / cycles / minDepthEth / source | Last `EXIT` line | Paired .jsonl: records, `t` span, block span |
|---|---|---|---|---|
| dry-flashblocks-run1.log | 11:56:49–12:03:35 | 19 / 253 / — / 0.2 / flashblocks | 124 | live-base.jsonl: 596, 12:02:58–12:05:12, 51990216–51990283 |
| dry-validate.log | 12:04:51–12:06:51 | 19 / 253 / — / 0.2 / flashblocks | 124 | live-base-validate.jsonl: 263, 12:05:06–12:06:51, 51990280–51990332 |
| dry-long.log | 12:04:57–12:27:34 | 50 / 342 / — / 0.2 / flashblocks | 143 | live-base-long.jsonl: 436, 12:04:10–12:27:00, 51990252–51990937 |
| dry-blocks-long.log | 15:15:51–15:45:15 | 268 / 587 / — / 0.2 / blocks | none | live-base-blocks-long.jsonl: 22, 15:28:37–15:43:15, 51996385–51996824 |
| dry-logs.log | 15:45:47–15:47:20 | 19 / 258 / 2,180 / 0.2 / logs | 124, then 1 | live-base-logs.jsonl: 4, 15:45:06–15:45:21, 51996879–51996887 |
| dry-blocks-long2.log | 15:48:59–15:54:46 | 268 / 606 / 2,746 / 0.2 / logs | 1 | — |
| dry-blocks-long4.log | 16:10:22–16:10:55 | 268 / 656 / 2,804 / 0.2 / logs | 1 | — |
| dry-blocks-long5.log | 16:13:30–16:38:53 | 268 / 657 / 2,804 / 0.2 / logs | 124 | live-base-blocks-long5.jsonl: 98, 16:16:27–16:38:29, 51997812–51998481 |
| dry-all-v0.log | 16:37:12–16:55:43 | 33,528 / 3,282 / 3,652 / 0.1 / logs | 143 | live-base-all-v0.jsonl: 36, 16:46:07–16:55:37, 51998695–51998995 |
| dry-all.log | 16:55:48–17:25:47 | 33,533 / 3,189 / 3,608 / 0.1 / logs | none | live-base-all.jsonl: 93, 17:04:25–17:25:47, 51999244–51999900 |

The two `--universe all` logs contain per-factory enumeration counts (`factory enumerated`: dex, total, enumerated; 8
lines each), `universe enumerated`, `pool discovery complete`, the GeckoTerminal V4 lines (`uniswap v4 candidates`,
`uniswap v4 pools discovered`), and per-tick heartbeats. Values as printed in each log (corrected 2026-10-01: the
manifest previously gave only the dry-all-v0.log values and attributed them to both logs):

| Log line | dry-all-v0.log | dry-all.log |
|---|---|---|
| `universe enumerated` enumeratedPools / tokens / pairs | 38,673 / 33,528 / 37,262 | 38,678 / 33,533 / 37,267 |
| `pool discovery complete` candidates / found | 1,341,432 / 46,134 | 1,341,612 / 46,134 |
| `geckoterminal pools fetched` requests / pools | 14 / 242 | 14 / 223 |
| `uniswap v4 candidates` listed / v4 | 242 / 20 | 223 / 20 |
| `uniswap v4 pools discovered` listed / kept / keyFailed / unknownKey / hooked / outOfUniverse | 20 / 10 / 0 / 0 / 4 / 6 | 20 / 10 / 0 / 0 / 4 / 6 |

The RSR/WETH detection at block 51998756 referred to in docs/ANALYSIS.md §2.6 is the record with `block` 51998756 in
live-base-all-v0.jsonl (t 2026-09-30T16:47:39.382Z, route `WETH>RSR@UniswapV3/10000 RSR>WETH@Aerodrome`).

## competitor-ledgers/

Collected 16:58–17:12 UTC from Base RPCs (publicnode for recent logs, blastapi for archive `eth_getBalance`/`eth_call`)
and the Blockscout v2 API. ETH/USD used where a USD figure was needed: 2,692.47 (Aerodrome Slipstream WETH/USDC pool
0xb2cc224c1c9fee385f8ad6a55b4d94e92359dc59 at ~16:58 UTC).

| File | Content |
|---|---|
| competitor_txs.json | Blockscout `/api/v2/addresses/0xF0523316Cf23EF167d874Fa030b2214280E38Ee6/transactions?filter=from` response: its last 50 transactions (blocks 51995475–51998757). This address sent tx 0x2310e683fe40902529cad07cde417d9062cc857c6052fb905101ce4b6d532e77 (block 51998757, position 1, to 0xA05787285256C4Ee18d7eD6865De2DDBb949c411), the transaction docs/ANALYSIS.md §2.6 traces after the RSR/WETH detection. (Corrected 2026-10-01: the hash was previously abbreviated as `0x2310e683…2b4`, which does not match.) |
| competitor_pnl.json | `{rows, hours}`; row = [tx_hash, landed, fee_eth (L2 + L1), weth_flow, usdc_flow, gross_eth, other_token_count] from ERC-20 Transfer logs into/out of its three contracts. This method does not see native-ETH payouts. Verified: 50 rows. |
| competitor_perblock.json | Row = [block, tx_count, all_landed, delta_eth, fee_eth, tx_hashes]; delta_eth = change of ETH + WETH + USDC (USDC converted at the ETH/USD above) summed over the EOA and its contracts 0x627E9E10…, 0xA0578728…, 0xfA256106… between block-1 and block. 1,128 archive calls, none missing (as recorded by the collecting session). Verified: 47 rows (blocks 51995475–51998757; `tx_count` sums to 50). |
| arbers_XDP.json | `{sender: [[block, tx_hash, max_priority_fee_gwei, to], …]}` for every tx that emitted a swap on BOTH XDP/USDC pools 0x1ef035205f94c7734827961c438474d089a334a0 (Uniswap V3 0.01 %) and 0x2df380544b88adb3ad0a94100dcc45fd705aae2d (Slipstream) in the 3,000 blocks before ~17:08 UTC. Verified: 1,403 senders, 5,873 rows (5,873 distinct tx hashes), blocks 51996357–51999357. |
| arbers_WETHUSDC.json | Same for WETH/USDC pools 0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38 (Uniswap V3 0.01 %) and 0xb4cb800910b228ed3d0834cf79d697127bbb00e5 (PancakeSwap V3 0.01 %). Verified: 48 senders, 65 rows, blocks 51996390–51999207. |
| ledger_0x778951.json, ledger_0x0190f0.json | Row = [block, delta_eth, fee_eth, xdp_units_delta] for the last 60 txs of senders 0x7789515e58bf00c99f11337bc267db8c30872351 (contract 0x952f339d…) and 0x0190f008a0118f41b43b3ee13b7162590fd925cc (contract 0xcd447b60…); delta_eth = change of ETH + WETH + USDC + XDP (XDP valued at 0.021453 USDC) over EOA + contract between block-1 and block. Verified (added 2026-10-01): one row per distinct block; ledger_0x778951 has 57 rows (blocks 51998995–51999349), ledger_0x0190f0 has 54 rows (blocks 51998915–51999355). |
| mine.json | Off-chain vs on-chain `getAmountOut` comparison for one Aerodrome V2 pool at 4 sizes. (Corrected 2026-10-01: the file holds 4 rows with fields `amountIn` and `mine` only; see Gaps.) |

(Gap removed 2026-10-01. It read: "the ledgers of the other two XDP senders (0x000000c557fa9a96d66cd6371abde62d879d0e61,
0x3be22b314654c396a12c5e8d79abdd65aac3caaf) were computed but not saved; only their summary rows exist, in docs/ANALYSIS.md
§2.6." Raw balance ledgers and receipts for these two senders were recomputed on 2026-10-01; see the section
"competitor-ledgers/: recomputed XDP-sender ledgers (added 2026-10-01)" at the end of this file. The earlier session's saved
values for them still exist only as the summary rows in docs/ANALYSIS.md §2.6.)

## papers-fetched-earlier/

Plain text extracted from the papers fetched earlier in the session (PDF text, not re-checked for extraction errors).
`08-sources/` holds a fresh, provenance-tracked collection; these are kept because they were the texts actually read.
arXiv 2606.00720 (Wu & Öz, "To Wait or To Probe"), arXiv 2501.17335 (Öz et al., cross-chain arbitrage), "Optimistic MEV in
Ethereum Layer 2s" (Solmaz et al.), "Cross-Rollup MEV: Non-Atomic Arbitrage on Layer-2 Blockchains" (Gogol et al.),
"Blockspace Under Pressure" (Wang et al.), "Quantifying the Value of Revert Protection" (Zhu et al.), ESMA TRV risk
analysis on MEV (1 July 2025), "How to Serve Your Sandwich? MEV Attacks in Private L2 Mempools" (Gogol et al.).

## research-runs/

Raw outputs of the non-Base-DEX measurements summarized in docs/ANALYSIS.md §5 (producing scripts in bot/src/research/):
feetiming (Slipstream fee transitions, 209 pools, 1,041 blocks), leadlag (OKX ETH-USDT vs 3 Base pools, 45 min),
leadlag-multi (OKX vs Base long-tail pools, 30 min), cexcex (OKX/Gate/Kraken spreads, 15 min), cextri (log only; the
.jsonl output was empty), crosschain (WETH/USDC Uniswap V3 0.05 % on Base, Arbitrum, Ethereum every 2 s, 450 samples).

Verified 2026-10-01 (record `t` values are epoch ms; spans in UTC on 2026-09-30):
- feetiming.jsonl: 19,211 records, 209 distinct `pool`, 1,041 distinct `block` (51996230–51997530), 15:23:28–16:06:47.
- leadlag.jsonl: 12,076 records (1,349 `src: base`, 10,727 `src: okx`), 15:16:49–16:01:48; Base price keys
  `UniV3/500`, `AeroCL3/50`, `PancakeV3/100`.
- leadlag-multi.jsonl: 4,496 records (901 `src: base`, 3,595 `src: okx`), 15:44:34–16:14:34; 7 Base tokens.
- cexcex.jsonl: 1,538 records, 25 distinct `pair`, venues gate/kraken/okx, 15:59:49–16:14:47.
- crosschain.jsonl: 450 records, 16:00:50–16:15:49.

## misc/

geckoterminal-top-pools-base.json (GeckoTerminal top-pools page for Base, fetched ~10:41 UTC); defillama-arbitrum-timeboost.json
(DefiLlama protocol record); v4-poolmanager-logs-sample.jsonl (raw `eth_getLogs` responses for the Base PoolManager,
~12:09 UTC); section-2.6-draft.md (draft text later inserted into docs/ANALYSIS.md).

Verified 2026-10-01:
- geckoterminal-top-pools-base.json: `data` holds 20 pools (`relationships.dex.data.id`: aerodrome-slipstream-3 8,
  uniswap-v3-base 4, uniswap-v4-base 3, aerodrome-slipstream 3, pancakeswap-v3-base 2).
- defillama-arbitrum-timeboost.json: one object, `name` "Arbitrum Timeboost", `id` 6065, 47 top-level keys.
- v4-poolmanager-logs-sample.jsonl: 6 JSON-RPC responses separated by blank lines (12 lines); 984 log entries in total
  (205, 173, 206, 122, 122, 156), all from address 0x498581ff718922c3f8e6a244956af099b2652b2b with topic0
  0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438 (= keccak256 of
  `Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)`), blocks 51978430–51990415.
- section-2.6-draft.md: 64 lines of prose written by the earlier session (kept unmodified as source material).
  **Label (added 2026-10-01): prior session text, not data.** It is the earlier session's draft prose and contains that
  session's conclusions and evaluative statements. Treat it as claims made by that session, not as measurements; the raw
  files it refers to are the engine-runs/ and competitor-ledgers/ files listed above.

## Verified inventory (2026-10-01)

53 files including this manifest; all 53 are tracked by git (none matches a .gitignore rule), so there are no local-only
files in this folder and nothing needs regenerating. (Corrected 2026-10-01, xdp-ledgers fill: this count and the git
statement describe the folder before that fill. It added 6 data files in competitor-ledgers/ (rows marked "untracked" at
the end of the table below) and 6 files in competitor-ledgers/collect/ (2 scripts, 4 logs). None of them was committed
when this note was written; none matches a .gitignore rule. The block-scans/ files added by the main session are listed
in their own section, not in this table.) (Corrected 2026-10-01, block-scans fixup: the 16 block-scans/ files, committed
in 9c8a37c, are now rows at the end of this table; the count of 53 does not include them.) Every `.gz` passes `gzip -t`; every `.json.gz` parses as one JSON
document; every non-blank line of every `.jsonl.gz` parses as JSON. Largest committed file: 318,740 bytes
(competitor-ledgers/arbers_XDP.json.gz); no file exceeds 90 MB. (Corrected 2026-10-01, block-scans fixup: counting
block-scans/, the largest committed file is block-scans/scan-arb2.jsonl.gz, 1,113,206 bytes; still no file exceeds 90 MB.) Line counts are newline counts of the decompressed
content; the `.json.gz` files are single JSON documents (0 newlines, 1 in mine.json) and are described by their
top-level structure instead.

| File | Bytes (on disk) | Bytes (decompressed) | Rows / lines | sha256 | Git |
|---|---:|---:|---|---|---|
| MANIFEST.md | (this file) | — | — | — (changes with each edit) | committed |
| engine-runs/arbtest.log.gz | 870 | 2,157 | 67 lines | `e8575b46ed34d9f6a7920bf2983c604d15efef3db92b6952c31eaf31a8878342` | committed |
| engine-runs/dry-all-v0.log.gz | 5,365 | 32,891 | 1,384 lines | `ad91602ab99f58b2eb91d7b17b77868705ad733127b5a9c06a1d2ae5349612b8` | committed |
| engine-runs/dry-all.log.gz | 11,268 | 76,763 | 3,143 lines | `dbb4dae5fbb3015603dd5d508755bb1f8e20d2f9c07746db66646029368030c8` | committed |
| engine-runs/dry-blocks-long.log.gz | 4,143 | 30,109 | 1,246 lines | `dd5d5ec7863b41cdcab3e10593db48b750f402cf1dd3f2367f57d3fa11c17e42` | committed |
| engine-runs/dry-blocks-long2.log.gz | 863 | 2,295 | 50 lines | `d427beea0739f5a135b8353d997edbe0ce185afa657f5fc3f4a8451aaccae642` | committed |
| engine-runs/dry-blocks-long4.log.gz | 701 | 1,764 | 41 lines | `6010e601b6da6adf2aad4a717ece73f2187e08c7564b6b557a0e8c5deaf52b70` | committed |
| engine-runs/dry-blocks-long5.log.gz | 11,010 | 79,343 | 3,296 lines | `873d62b28eca17e3975ca747202b71be9714751c956b9504ccb3fe971b78e00e` | committed |
| engine-runs/dry-flashblocks-run1.log.gz | 1,300 | 9,873 | 541 lines | `fbada977e19011bf22f3dd644330d8eb8d49b5f85c26539a05c06badde15731a` | committed |
| engine-runs/dry-logs.log.gz | 971 | 5,228 | 119 lines | `3276b735b4a55cbf0035a59294a9dc9152eaf4f2681fdad9b050233fcce583ec` | committed |
| engine-runs/dry-long.log.gz | 13,253 | 243,678 | 9,154 lines | `d7c618429edc7f8e31ba52316726fc76d954a58f74a7859b50ceb22a29ac7c05` | committed |
| engine-runs/dry-validate.log.gz | 7,889 | 343,559 | 7,465 lines | `c6a3c1369e9171e592e46a48e1dee584b0414252236ea17f9c5119631f698093` | committed |
| engine-runs/lev.log.gz | 520 | 935 | 27 lines | `e6ead047511c1273ebe5ba1fb1e4177a3482d87ff5761c5e7fcc3b487703aab1` | committed |
| engine-runs/live-base-all-v0.jsonl.gz | 2,964 | 14,593 | 36 lines = 36 JSON records | `138f6a42e04e271eaf1ee3867fc4e58b6d64c07ae9b51cdcb34355c1d7dcda77` | committed |
| engine-runs/live-base-all.jsonl.gz | 6,488 | 38,113 | 93 lines = 93 JSON records | `788e9edda03b2291bbbc795bf144ad390198208947819c8eb108258a627280a8` | committed |
| engine-runs/live-base-blocks-long.jsonl.gz | 1,714 | 9,111 | 22 lines = 22 JSON records | `ce0c126bde835bb8aae22cb9a8525f8e1d058ec596eca013a963310e7e6b642e` | committed |
| engine-runs/live-base-blocks-long5.jsonl.gz | 6,156 | 39,339 | 98 lines = 98 JSON records | `641f80afdcc5cfb2f28a30b8a04495c112cd215094b888395c6515ba75673e78` | committed |
| engine-runs/live-base-logs.jsonl.gz | 508 | 1,616 | 4 lines = 4 JSON records | `8f99ed7c7418fd52fafed79acae096bcc789f0f5d66954377fb108993518b86b` | committed |
| engine-runs/live-base-long.jsonl.gz | 7,775 | 176,134 | 436 lines = 436 JSON records | `28c15d31aecc923909dbaedc6d51d59930666e58df1dfb63e81968d3597f561a` | committed |
| engine-runs/live-base-validate.jsonl.gz | 3,537 | 107,147 | 263 lines = 263 JSON records | `e310d3b53b534942605ea960f99525249c8e618ce12f3094b3e0af7cae82ee9a` | committed |
| engine-runs/live-base.jsonl.gz | 6,106 | 255,397 | 596 lines = 596 JSON records | `df32594b671aa7639cca451a76d859ca33319d6de7393daf7e807eda61ee54fa` | committed |
| engine-runs/pipeline.log.gz | 641 | 1,098 | 36 lines | `8e7b959a7265c2960e090f8dffe98586a2845f55787490fe2d3f0afc4a960b6f` | committed |
| competitor-ledgers/arbers_WETHUSDC.json.gz | 4,893 | 11,319 | 1 JSON object: 48 sender keys, 65 rows total | `67219ef5ef0d9fd2034d394d70b0eef616124212f0ce89fd38f217af3c8a7180` | committed |
| competitor-ledgers/arbers_XDP.json.gz | 318,740 | 882,928 | 1 JSON object: 1,403 sender keys, 5,873 rows total | `382ad4ff0ee568bab7822455a0d31f0bc655024c28e35e768631b0ff05ad441a` | committed |
| competitor-ledgers/competitor_perblock.json.gz | 1,481 | 3,921 | 1 JSON array: 47 rows | `d1116713798e46ba532c8215d71094e7ff532c4b1724ff7f37b6abe0773afbf5` | committed |
| competitor-ledgers/competitor_pnl.json.gz | 2,993 | 6,469 | 1 JSON object: `rows` 50, `hours` | `afa4c020595e61216cc947f94ab1baf9440752ee8b6579d090e413f650fab7d9` | committed |
| competitor-ledgers/competitor_txs.json.gz | 13,496 | 125,308 | 1 JSON object: `items` 50, `next_page_params` | `c9c977e42100c6fbf7115d5276e7a8173acd53091cecd28252bc78bc8dfb1f3a` | committed |
| competitor-ledgers/ledger_0x0190f0.json.gz | 1,257 | 3,316 | 1 JSON array: 54 rows | `d671fa949512a4f5c2ddb5a7a868dbc975f2f1b5dcdb2470bae70cec1eda2f31` | committed |
| competitor-ledgers/ledger_0x778951.json.gz | 1,299 | 3,449 | 1 JSON array: 57 rows | `fa75012ebd3501978f1ac2e51ba7a7edab14d78174c4a461469d5f23a27495ae` | committed |
| competitor-ledgers/mine.json.gz | 97 | 162 | 1 JSON array: 4 rows | `ea25d9b133813824df0175cc5ada13ff28e91fe01d278178aca6450bd6f69bfb` | committed |
| research-runs/cexcex.jsonl.gz | 19,394 | 209,796 | 1,538 lines = 1,538 JSON records | `f8a87342edc59d384a6d30af4d7dbc8c6317d4f1adc4fc2a611eca1f72ddb3d9` | committed |
| research-runs/cexcex.log.gz | 1,162 | 6,023 | 47 lines | `e5a1e26f7e99ac1d583cd0f9033b86ba1659868ec36a89f8dacc0c0be7ac401d` | committed |
| research-runs/cextri.log.gz | 365 | 1,186 | 22 lines | `f0bfa29e1cbc070979c6e9bf404a8013554e63e81ce10799745122f53de24f08` | committed |
| research-runs/crosschain.jsonl.gz | 7,341 | 76,430 | 450 lines = 450 JSON records | `8e39fd8e9503d7310c9c29cf40200d91d31deca2ec38981b0649dddffc226707` | committed |
| research-runs/crosschain.log.gz | 488 | 1,974 | 40 lines | `002d9e53a28a280ed9a091983d0da5db4442171ada7f6c1a337e859ae3387b39` | committed |
| research-runs/feetiming.jsonl.gz | 717,996 | 5,208,144 | 19,211 lines = 19,211 JSON records | `2261e671aae3cd3dc31045751907166ef5790a49d0c86c9e5f6164cf211e3283` | committed |
| research-runs/feetiming.log.gz | 854 | 3,961 | 67 lines | `382f00fd75b2d140bd1664076e7ffc7fcdaff973bc19280bb9e4eaa5eaff1763` | committed |
| research-runs/leadlag-multi.jsonl.gz | 51,361 | 1,019,457 | 4,496 lines = 4,496 JSON records | `4ef353926c3c99c92d7da00017fa1ca7ef2828098cba3165383532e6c42881a9` | committed |
| research-runs/leadlag-multi.log.gz | 442 | 896 | 35 lines | `a92fff410022614262c89c2fc393e08a7881b0684fd9d42054bd516ef4e67113` | committed |
| research-runs/leadlag.jsonl.gz | 127,232 | 1,303,026 | 12,076 lines = 12,076 JSON records | `75cdf648848897bba34c30ed561772df4913442f588ab5f4768f2b3a6edd28fd` | committed |
| research-runs/leadlag.log.gz | 328 | 1,456 | 46 lines | `a330b152ff257d02361cf2b7b656db32f96a35d552c33b2781962961248887e2` | committed |
| misc/defillama-arbitrum-timeboost.json.gz | 8,854 | 40,845 | 1 JSON object (47 keys) | `3d2a55cf059130c2cbcf72de71693bb5dfcccf7a8dcba64622e99a681b7a0cc0` | committed |
| misc/geckoterminal-top-pools-base.json.gz | 6,409 | 29,713 | 1 JSON object: `data` 20 pools | `1fe8ab196a0490200529560dd06fe8c7bd6da57e4298ee95d0d0477c54f9ae01` | committed |
| misc/section-2.6-draft.md | 5,142 | — | 64 lines | `34f45cd79c347cd416fb58f52f802a8dd9c1d89f1ed5dd4cf2962803389e830e` | committed |
| misc/v4-poolmanager-logs-sample.jsonl.gz | 183,404 | 945,773 | 12 lines: 6 JSON-RPC responses (984 log entries) + 6 blank lines | `ec374436087b91229307d294cccedd6702dec231caa53e532adfd2c2bfe4bba3` | committed |
| papers-fetched-earlier/arxiv-2501.17335-cross-chain-arbitrage.txt.gz | 36,071 | 93,059 | 2,924 lines | `21c1c91cb1cdcab025643477b3a2cb56e8b69f87e1ce09fcdfcaa670ca6798df` | committed |
| papers-fetched-earlier/arxiv-2606.00720-to-wait-or-to-probe.txt.gz | 41,843 | 125,440 | 2,616 lines | `2ccf984b04cf49de89cc4aeb85174b9a16252a6ae3b7da3376223393bc0c62a2` | committed |
| papers-fetched-earlier/blockspace-under-pressure-spam-mev.txt.gz | 43,936 | 131,238 | 2,769 lines | `95845774788f968ff04afc0f21b6bbb39d15acbe0c373677a64de7bdc50f2dc6` | committed |
| papers-fetched-earlier/cross-rollup-mev-non-atomic-arbitrage.txt.gz | 15,152 | 41,648 | 1,102 lines | `78e9fdc698cc1204be42b808e973af74f99042dfa66b5b0a210d65f2aabe4287` | committed |
| papers-fetched-earlier/esma.txt.gz | 21,879 | 59,621 | 1,667 lines | `4f07da6ba71c5703396a23c3bc6cebdef0c0e3f4edbe555ddb3e1bf9853e7f55` | committed |
| papers-fetched-earlier/optimistic-mev-l2s.txt.gz | 36,966 | 103,229 | 2,429 lines | `8f6eb7d6230915d8e18a12ea72fa1f41c80b1eb157f8ce2c04da01b445994cc2` | committed |
| papers-fetched-earlier/quantifying-value-of-revert-protection.txt.gz | 17,496 | 54,293 | 1,571 lines | `67686f0dc2f1be717a2754bdece83595c5bd3353262a495403b6d1f9c2e2e311` | committed |
| papers-fetched-earlier/sandwich-l2.txt.gz | 17,210 | 44,528 | 1,178 lines | `c26bbe7e2ce7e54c7d64bcc07acc8c86687441d8886f2a4c6ced8faafab6552d` | committed |
| competitor-ledgers/ledger_0x000000c5.raw.csv.gz (added 2026-10-01) | 5,031 | 107,263 | 929 lines = header + 928 rows | `0aebfeb4e76d2f9aafc73d1a89b3095a8a9608452ca2270f2140f90e91edee2e` | untracked |
| competitor-ledgers/ledger_0x3be22b31.raw.csv.gz (added 2026-10-01) | 4,711 | 94,061 | 785 lines = header + 784 rows | `574c7fa70dc01bf0daa043b85ce7d2fbc4a5a79b77161c412b2eb2a9b7813b9f` | untracked |
| competitor-ledgers/receipts_0x000000c5.csv.gz (added 2026-10-01) | 7,606 | 23,003 | 61 lines = header + 60 rows | `036432fb04163fcb6fac96b8ba99b2656d6078a0a722c892d15988ab74555a53` | untracked |
| competitor-ledgers/receipts_0x3be22b31.csv.gz (added 2026-10-01) | 7,367 | 23,458 | 61 lines = header + 60 rows | `678f562b1614428a2c0a8582dd5877307cc888077972458efd0a0fe9976ebf71` | untracked |
| competitor-ledgers/receipts_0x000000c5.full.jsonl.gz (added 2026-10-01) | 18,510 | 293,708 | 60 lines = 60 JSON records | `ed1e39c86a8bb3046b588be3ec25292f894a28cb03c19494a0d4b03d8e73ab43` | untracked |
| competitor-ledgers/receipts_0x3be22b31.full.jsonl.gz (added 2026-10-01) | 17,434 | 293,734 | 60 lines = 60 JSON records | `7f55e6d101895f39af83eac31276074c3cbd3d61d1d9385daa526c29958481ab` | untracked |
| block-scans/prof.log.gz (row added 2026-10-01) | 786 | 2,370 | 34 lines | `d3e79e4deca501aac2b78eb58a6ece730656c64eaba66e7ab017ade33b82c7f3` | committed |
| block-scans/repro.log.gz (row added 2026-10-01) | 2,203 | 7,144 | 64 lines | `04aaf0c6980ad420a3c14ce9d9a461dd110b5019da061819fce8a8d508c968a4` | committed |
| block-scans/scan-arb.jsonl.gz (row added 2026-10-01) | 986,170 | 9,915,782 | 23,277 lines = 23,277 JSON records | `02b6989015b9baae2eaf64308a8f3bc3ca858924ccd153ce6e9215679161491f` | committed |
| block-scans/scan-arb.log.gz (row added 2026-10-01) | 12,778 | 279,859 | 4,256 lines | `9f346802fa0bd7293f7c156f005ee709302ca300c4844e90dbf079f80efdd5e8` | committed |
| block-scans/scan-arb2.jsonl.gz (row added 2026-10-01) | 1,113,206 | 10,106,913 | 22,353 lines = 22,353 JSON records | `27193eba5b6063ec10533d772af019ed9085b873be85345e06e37080d53be5bf` | committed |
| block-scans/scan-arb2.log.gz (row added 2026-10-01) | 8,856 | 190,118 | 2,828 lines | `ef38db6098b5069944d4af0116926ca70df5c426ad397e514930192dc60a5bee` | committed |
| block-scans/scan-base-longtail.jsonl.gz (row added 2026-10-01) | 615,569 | 4,598,217 | 10,115 lines = 10,115 JSON records | `cfa6fb99b3d57edd2a07f3f8b711e9365628ecc6af8c12a3a0e04989d3821780` | committed |
| block-scans/scan-base-longtail.log.gz (row added 2026-10-01) | 4,532 | 59,679 | 887 lines | `deae99add64609ae350ed2c6c7c75ab74afe431bd903a2ad901708a44e3bbbf6` | committed |
| block-scans/scan-base-run1.log.gz (row added 2026-10-01) | 1,086 | 8,981 | 382 lines | `62f96e524bdbf04ae2e6a3cda15231ca2adb6e0e5c471f1c8a33d7a39f6fd2dc` | committed |
| block-scans/scan-base-run2.log.gz (row added 2026-10-01) | 5,303 | 112,389 | 1,712 lines | `c2e5b722a6168189d54f85550471b62f0148b2116fedf70574fd899729eb2b75` | committed |
| block-scans/scan-base-run3.log.gz (row added 2026-10-01) | 3,128 | 56,857 | 874 lines | `8968a42f258efae4352fc1de70e1c76e3de8d091c547161a5d6f5caea803fcf4` | committed |
| block-scans/scan-base-run4.jsonl.gz (row added 2026-10-01) | 278,092 | 2,411,615 | 5,239 lines = 5,239 JSON records | `3ab4601f1ca258f5e62ad8bddd4319aab97283cba8dbf3899c3bcf332fc50a5d` | committed |
| block-scans/scan-base-run4.log.gz (row added 2026-10-01) | 3,488 | 59,026 | 884 lines | `0ae8174146f0a172fc16eda5b81c6d18ee5e7e33f24967272a3ad6bc363c516c` | committed |
| block-scans/scan-base.jsonl.gz (row added 2026-10-01) | 14,231 | 461,946 | 1,173 lines = 1,173 JSON records | `68c57290b5191cf3976d08d7fb2a3cd8bc2271e495226075d17312d50a8dd886` | committed |
| block-scans/scan-mainnet.jsonl.gz (row added 2026-10-01) | 107,631 | 938,054 | 2,071 lines = 2,071 JSON records | `0def6979ae7421439fce7038c0eff247f03b5af00ca8d872ec4e8f6478c69413` | committed |
| block-scans/scan-mainnet.log.gz (row added 2026-10-01) | 2,517 | 21,316 | 316 lines | `d844eb0e9d71b1194fe4d1f8d0b30da16987ced189ecb2192abe24f56fc6853d` | committed |

## block-scans/ (added 2026-10-01 by the main session)

The block-boundary scans summarized in docs/ANALYSIS.md section 2.1, produced on 2026-09-30 by `bot/src/research/scan.ts`
(unmodified code of that time) and found afterwards in the git-ignored `bot/data/`. Gzip copies; nothing else changed.
Serves question line 4 ("Block-level scans covered Arbitrum and Ethereum") and line 8.

| File | Chain | Log start (UTC, from the log) | Content |
|---|---|---|---|
| scan-base-run1.log.gz, scan-base-run2.log.gz, scan-base-run3.log.gz, scan-base.jsonl.gz | base | 10:28 onward | first Base scans (config token list, 20 tokens); scan-base.jsonl holds the rows of run 3 |
| scan-base-run4.log.gz, scan-base-run4.jsonl.gz | base | ~11:5x | Base scan, config universe |
| scan-base-longtail.log.gz, scan-base-longtail.jsonl.gz | base | 11:59 | Base scan, long-tail token universe |
| scan-arb.log.gz, scan-arb.jsonl.gz, scan-arb2.log.gz, scan-arb2.jsonl.gz | arbitrum | 11:59 onward | Arbitrum scans (12 config tokens) |
| scan-mainnet.log.gz, scan-mainnet.jsonl.gz | mainnet | 11:59 | Ethereum scan (12 config tokens) |
| prof.log.gz, repro.log.gz | base | ~11:52 | profiling and reproduction logs from debugging the searcher |

Line counts of the `.jsonl` files: scan-arb 23,277; scan-arb2 22,353; scan-base-longtail 10,115; scan-base-run4 5,239;
scan-base 1,173; scan-mainnet 2,071. Each line is one route evaluated at one block (fields: block, key, token, route, and
the scan's per-route values). The exact flags of each run are in the head of its log. The pairing of scan-base.jsonl with
run 3 is inferred from file modification times (10:49 for both).

## competitor-ledgers/: recomputed XDP-sender ledgers (added 2026-10-01)

Fills former gap 1. Collected 2026-10-01 by `competitor-ledgers/collect/xdp_ledgers.py` (Python 3, requests). Raw values
only: no deltas, fee sums, conversions or USD values were computed.

**Input and selection** (same selection as `ledger_0x778951` / `ledger_0x0190f0`, see the competitor-ledgers/ table):
- Input: `competitor-ledgers/arbers_XDP.json.gz`, keys `0x000000c557fa9a96d66cd6371abde62d879d0e61` (163 rows) and
  `0x3be22b314654c396a12c5e8d79abdd65aac3caaf` (146 rows).
- Per sender: rows sorted by block (stable sort, file order kept within a block), last 60 taken. The cut does not split a
  block: the 61st-from-last row is at block 51,998,229 (0x000000c5) and 51,998,984 (0x3be22b31); the script asserts this.
- Addresses read: the EOA and every distinct `to` of the 60 txs. That is one contract per sender:
  0x0ce14aeebb7ad6625585979f4c1846946e248e02 for 0x000000c5, and 0x08c61873dc64c5131758ae27cb4d84e773d66d82 for 0x3be22b31.
- Assets read: ETH (`eth_getBalance`), and `balanceOf(address)` (selector 0x70a08231, `eth_call`) on
  WETH 0x4200000000000000000000000000000000000006, USDC 0x833589fcd6edb6e08f4c7c32d4f71b54bda02913 and
  XDP 0x07b3d902783c3c12b077508c3b5c00113d1291d0.
- Token `decimals()` at block 51,999,354: WETH 18, USDC 6, XDP 18 (`collect/token_decimals.log`). Recorded as metadata; the
  stored balances are not scaled.
- Blocks: for every distinct block b holding one of the 60 txs, state at block numbers b-1 and b.
- Receipts: `eth_getTransactionReceipt` for each of the 60 txs.

**Endpoint and run.** Endpoint: `https://base-mainnet.public.blastapi.io` (archive), with JSON-RPC batches of at most 25
calls and at most 2 batches in flight. The block parameter is the block number as a hex quantity; the archive state was
read about 11 h after the blocks. Run times (UTC, 2026-10-01):
- smoke test 04:04:37, 12 calls (`collect/smoke_xdp_ledgers.log`);
- full fetch 04:04:37–04:05:19 (`collect/xdp_ledgers.log`): 1,720 distinct calls, 111 HTTP batch requests.
  - The 1,720 calls are 1,600 balance reads plus 120 receipts. The balance reads are 880 for 0x000000c5 and 720 for 0x3be22b31,
    one per distinct (queried block, address, asset).
  - blastapi answered 384 batch items with per-item error 429 ("compute units per second"). Those items were retried with
    backoff until valid.
  - Final check: 0 missing or invalid results. A balance result counts as valid if it is a hex quantity; an `eth_call`
    result must be exactly 32 bytes; a receipt must be non-null.
- 04:05:48: re-run from the local result cache, with no new RPC calls, after the `block_timestamp` column was added. The
  result cache (`collect/state/`) was deleted afterwards, so a new run fetches everything again.

Commands (from `research-material/00-prior-runs/competitor-ledgers/collect/`):
`python3 xdp_ledgers.py --smoke`; `setsid nohup python3 xdp_ledgers.py >> xdp_ledgers.log 2>&1 &`;
`python3 verify_xdp_ledgers.py > verify_xdp_ledgers.log`.

**`ledger_0x000000c5.raw.csv.gz`, `ledger_0x3be22b31.raw.csv.gz`.** One row per (block, block_tag, address, asset). Rows are
ordered by block, then tag (b-1 first), then address (EOA first), then asset (ETH, WETH, USDC, XDP).

| Column | Content |
|---|---|
| block | block b that holds at least one of the 60 selected txs of the sender |
| block_tag | `b-1` or `b` |
| queried_block | block number passed to the RPC call (b-1 or b) |
| address | lowercase address read |
| address_role | `eoa` (the sender) or `to_contract` (a `to` of its selected txs) |
| asset | `ETH`, `WETH`, `USDC` or `XDP` |
| asset_address | token contract; empty for ETH |
| balance | raw balance, base-10 integer string in the asset's smallest unit (wei for ETH and WETH) |

Row counts:
- ledger_0x000000c5: 928 rows = 58 blocks × 2 tags × 2 addresses × 4 assets. Tx blocks 51,998,274–51,999,354; queried
  blocks 51,998,273–51,999,354 (110 distinct).
- ledger_0x3be22b31: 784 rows = 49 blocks × 2 tags × 2 addresses × 4 assets. Tx blocks 51,998,986–51,999,352; queried
  blocks 51,998,985–51,999,352 (90 distinct).
- Where b-1 of one selected block is itself a selected block (6 cases for 0x000000c5, 8 for 0x3be22b31), the same
  (queried block, address, asset) value appears in two rows. It was fetched once.

**`receipts_0x000000c5.csv.gz`, `receipts_0x3be22b31.csv.gz`.** 60 rows each, one per selected tx, ordered by input block.
Integers are base-10 strings converted from the RPC hex quantities. Columns:
- `sender`, `tx_hash`.
- `input_block`: the block given in arbers_XDP.json.
- `block_number`, `block_hash`, `transaction_index`, `from`, `to`, `type`, `status`, `gas_used`, `cumulative_gas_used`,
  `effective_gas_price` (wei), `l1_fee` (wei), `l1_gas_used`, `l1_gas_price`, `l1_base_fee_scalar`, `l1_blob_base_fee`,
  `l1_blob_base_fee_scalar`: receipt fields.
- `block_timestamp` (unix seconds): blastapi returns `blockTimestamp` only inside log entries, so the value comes from the
  receipt's logs. Every selected tx has logs.
- `logs_count`.
- `input_max_priority_fee_gwei`: the third field of the input row, copied verbatim (Python float repr).

Descriptive coverage:
- 0x000000c5: 60 txs in 58 blocks; block timestamps 2026-09-30 16:31:35–17:07:35 UTC; receipt `type` 0 for all; `status` 1
  for all; 2 blocks hold 2 of its txs.
- 0x3be22b31: 60 txs in 49 blocks; 16:55:19–17:07:31 UTC; `type` 2 for all; `status` 1 for all; 9 blocks hold more than one
  of its txs (at most 3).
- For all 120 receipts, block number, `from` and `to` match the input row, and `l1Fee` is present.

**`receipts_0x000000c5.full.jsonl.gz`, `receipts_0x3be22b31.full.jsonl.gz`.** The same 60 + 60 `eth_getTransactionReceipt`
result objects, verbatim. They keep the hex quantities as returned (lowercase), with keys sorted, one per line. They include
`logs` (every log of the tx, e.g. ERC-20 Transfer and pool Swap events), `logsBloom`, `blobGasUsed` and
`daFootprintGasScalar`.

**Verification** (`collect/verify_xdp_ledgers.py`, `collect/verify_xdp_ledgers.log`, 04:06:16–04:06:38 UTC):
- Ledgers: row count equals blocks × 2 × addresses × 4, with no duplicate key; every balance is a non-negative integer
  string; `queried_block` is consistent with `block_tag`.
- Receipts: the 60 tx hashes equal the selection, and no cell is empty.
- Second endpoint: per sender, 20 random ledger rows and 5 receipts (gas_used, effective_gas_price, l1_fee, status,
  block_number) were re-read from `https://gateway.tenderly.co/public/base`, with 0 mismatches.
- Total problems: 0.

**Coverage limits:**
- Balances are block-level state, not per-tx. The difference between b-1 and b includes every selected tx of the sender in
  block b (up to 3) and any other tx in that block that touched these addresses and tokens.
- Only the four assets and only the EOA plus its `to` contract were read. Other tokens, and other addresses such as a
  separate payout address, are not in the ledgers. The full receipts' logs list every token transfer of the selected txs.
- Native-ETH movements are visible only as `eth_getBalance` differences. No traces (internal calls) were collected.
- Not collected: transaction objects (`eth_getTransactionByHash`: value, nonce, fee caps, input data) and block headers
  (base fee).
- The earlier session's ledgers for these two senders (summary rows in docs/ANALYSIS.md §2.6) were not saved, so these
  files cannot be compared with them row by row. The new files use the same selection, addresses and assets as the method
  described for ledger_0x778951 / ledger_0x0190f0, but they store raw balances and receipt fields rather than that
  method's derived `delta_eth`, `fee_eth` and `xdp_units_delta`.

## block-scans/ fixup (2026-10-01)

Manifest-only fix made by a fixup agent on 2026-10-01 (~04:45Z). No data file was created, changed or moved; nothing was
fetched from the network.

What changed in this file:
- Gap 4: the statement that the `scan-*` files, `prof.log` and `repro.log` were not copied was wrong after the main
  session copied them to `block-scans/` (commit 9c8a37c, 2026-10-01T02:57:03Z). The item now says so; the original list is
  kept inside the correction note.
- "Question lines served": block-scans/ added to lines 4 and 8, plus a one-row-per-file table for the 16 files.
- "Verified inventory (2026-10-01)": 16 rows added for block-scans/, and notes on the file count and the largest file.
- engine-runs/ provenance note: `dry-all.log` added to the exception for commit fd8d236 (it is the log of the same run as
  `live-base-all.jsonl`), with the timestamps.
- misc/: `section-2.6-draft.md` labelled "prior session text, not data".

Checks run on the 16 block-scans/ files (commands from `research-material/00-prior-runs/block-scans/`):
- `gzip -t <file>`: all 16 pass.
- `stat -c %s`, `zcat | wc -c`, `zcat | wc -l`, `sha256sum` (of the .gz): values in the inventory rows.
- `zcat <file> | sha256sum` compared with `sha256sum` of the original of the same name in the git-ignored `bot/data/`
  (still on disk): all 16 decompressed copies are byte-identical to their originals. Original modification times
  (2026-09-30 UTC): scan-base-run1.log 10:29:52, scan-base-run2.log 10:39:20, scan-base.jsonl 10:49:32,
  scan-base-run3.log 10:49:33, prof.log 11:52:23, repro.log 11:54:39, scan-base-run4.jsonl/.log 11:59:52,
  scan-base-longtail.jsonl/.log 12:02:28, scan-mainnet.jsonl/.log 12:03:07-12:03:08, scan-arb.jsonl/.log 12:06:57-12:06:58,
  scan-arb2.jsonl/.log 12:15:13.
- `git status`: all 16 are committed (9c8a37c) with no working-tree change.
- Every non-blank line of the 6 `.jsonl.gz` files parses as JSON (0 failures). Every record has the same 11 keys:
  `amountIn`, `block`, `gapBps`, `gas`, `gasEth`, `key`, `netEth`, `profitEth`, `profitToken`, `route`, `token`.

Descriptive metadata (read from the files; no values computed from the scan results):

| File | Records | Distinct `block` values | `block` min-max |
|---|---:|---:|---|
| scan-arb.jsonl.gz | 23,277 | 300 | 510,339,422-510,341,080 |
| scan-arb2.jsonl.gz | 22,353 | 200 | 510,340,911-510,342,914 |
| scan-mainnet.jsonl.gz | 2,071 | 20 | 26,090,150-26,090,169 |
| scan-base.jsonl.gz | 1,173 | 60 | 51,987,924-51,988,011 |
| scan-base-run4.jsonl.gz | 5,239 | 60 | 51,990,047-51,990,122 |
| scan-base-longtail.jsonl.gz | 10,115 | 60 | 51,990,118-51,990,200 |

| Log | First / last bracketed timestamp (UTC, 2026-09-30) | First `discovering pools` line: chain, tokens | `EXIT` line |
|---|---|---|---|
| scan-base-run1.log.gz | 10:28:23-10:29:52 | base, 20 | none |
| scan-base-run2.log.gz | 10:33:35-10:39:20 | base, 19 | none |
| scan-base-run3.log.gz | 10:46:21-10:49:32 | base, 19 | none |
| scan-base-run4.log.gz | 11:57:08-11:59:52 | base, 19 | EXIT 0 |
| scan-base-longtail.log.gz | 11:59:22-12:02:28 | base, 19 | EXIT 0 |
| scan-mainnet.log.gz | 11:59:21-12:03:07 | mainnet, 12 | EXIT 0 |
| scan-arb.log.gz | 11:59:22-12:06:57 | arbitrum, 12 | EXIT 0 |
| scan-arb2.log.gz | 12:05:56-12:15:13 | arbitrum, 12 | EXIT 0 |

- `prof.log.gz`: first line `start 2026-09-30T11:48:25.740Z`, last line `EXIT 124`. `repro.log.gz`: per-size quote
  traces for one SushiV2 / AerodromeCL pool pair (pool state at block 51989959), no timestamps.
- Note on the block-scans/ table above: its row for runs 1-3 says "20 tokens". The `discovering pools` line prints
  `tokens: 20` for run 1 and `tokens: 19` for runs 2 and 3.
