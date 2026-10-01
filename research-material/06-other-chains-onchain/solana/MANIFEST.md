# 06-other-chains-onchain/solana: Solana mainnet consecutive-slot sample, Jito data, ordering docs

STATUS: COMPLETE WITH GAPS (finalized 2026-10-01). Both collectors finished: sentinel `SOL_SAMPLE.DONE` (2026-09-30T21:45:55Z) and sentinel `SOL_JITO_TIPFLOOR.DONE` (2026-09-30T22:31:07Z, "60 successful polls (61 total)"); sentinel files are git-ignored, their text is reproduced in `../MANIFEST.md`. Last data write 2026-09-30T22:30Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)'). Gaps: (a) `tip-floor.jsonl` has 61 polls, of which poll 40 (2026-09-30T22:09:07Z) failed with a connection reset; (b) for 15 of the 600 slots the Jito `bundles/slot` endpoint answered HTTP 404 "Bundle not found" (stored verbatim; listed under Method); (c) 4 documentation URLs were not retrieved (listed under docs/ 'Failed fetches'); (d) `data/raw-slots/` (600 files, 564,677,263 bytes), `data/jito-bundles-by-slot.parts/` (600 files), `data/prices.parts/` (72 files), `collect/state/pin.json` and `collect/__pycache__/` (7 files) are git-ignored and stay local-only, so they are not in the repository.

Status line as written by the collector at about 2026-09-30T21:49Z (superseded; correction 2026-10-01): STATUS: IN PROGRESS. Slot sample, Jito bundles, prices, programs, snapshots and docs are complete (sentinel `SOL_SAMPLE.DONE`, written 2026-09-30T21:45:55Z). The Jito tip-floor poller (`collect/jito_tip_floor.py`, PID 2255) is still running until it has 60 successful polls; it writes the sentinel `SOL_JITO_TIPFLOOR.DONE` (or `.FAILED`). The row count for `tip-floor.jsonl` is filled in once that sentinel exists.

Collected 2026-09-30 (UTC). Raw material only. Nothing in this directory analyzes, estimates or concludes anything. Columns marked "derived" are deterministic, lossless decodings of the raw data, and the raw data is stored next to them.

## Question lines served (mapping only)

Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md`. Restated by line number on 2026-10-01: the collector's table used the Q-IDs of `../MANIFEST-evm.md`, short notes and a ninth ID, Q-GAPS ("Would the gaps change the answer?"), which is not one of the 8 question lines and was dropped.

File groups used in the table:
* S (slot sample): slots.csv.gz, txs-nonvote-001.csv.gz, dex-txs-001.jsonl.gz, dex-txs-002.jsonl.gz, data/raw-slots/ (local-only), program-invocations.csv.gz, jito-tip-transfers.csv.gz, data/jito-bundles-by-slot.jsonl.gz, token-mints-seen.csv.gz, prices-defillama-historical.jsonl.gz, data/slot-leaders.json, data/get-blocks.json, data/integrity-crosscheck.json, data/build-summary.json
* D (definitions used by S): dex-programs.csv, jito-tip-accounts.csv, docs/program-id-sources/

| Line | Files in this directory |
|---|---|
| 1 | none |
| 2 | none |
| 3 | S, D (pool-vault token balances: preTokenBalances / postTokenBalances in dex-txs-00*.jsonl.gz and data/raw-slots/) |
| 4 | S, D, tip-floor.jsonl, snapshots/ (all files), defillama-dexs.json, docs/, docs/literature/ |
| 5 | S, D, tip-floor.jsonl, snapshots/jito__* |
| 6 | tip-floor.jsonl, snapshots/jito__*, data/jito-bundles-by-slot.jsonl.gz, docs/, snapshots/rpc__getVoteAccounts.json.gz, snapshots/rpc__getClusterNodes.json.gz, slots.csv.gz (leader column) |
| 7 | S, D, snapshots/defillama__*, defillama-dexs.json, snapshots/jito__kobe.mainnet.jito.network_api_v1_daily_mev_rewards.json.gz, docs/literature/ |
| 8 | S, D |

Join key (from the collector's table): `snapshots/rpc__getVoteAccounts.json.gz`, `snapshots/rpc__getClusterNodes.json.gz` and `snapshots/jito__kobe*validators*` are keyed by validator identity, which is the value in `slots.csv.gz` column `leader`.

## Window (pinned)

* Pinned at 2026-09-30T21:28:22.95Z to the `finalized` slot at pin time (`getSlot`, api.mainnet-beta.solana.com): **slots 452084865 to 452085464 (600 consecutive slots)**. Source: `collect/state/pin.json` (local-only, git-ignored; its full content is reproduced in 'Verified inventory (2026-10-01)').
* Block times (`blockTime`, 1 s resolution): **2026-09-30T21:25:34Z to 2026-09-30T21:28:13Z**.
* All 600 slots returned a block. `getBlocks(452084865, 452085464, finalized)` lists all 600, and no slot was skipped. For every slot after the first, `parent_slot = slot - 1`.
* Leaders: `getSlotLeaders(452084865, 600)` was fetched at 2026-09-30T21:28:24.61Z. The window has 92 distinct leader identities.
* Totals over the window: 750,426 transactions, of which 401,812 are vote transactions and 348,614 are non-vote. vote_tx_mixed_count is 0 in every slot.

## Method

* `getBlock(slot, {"encoding":"json","maxSupportedTransactionVersion":1,"transactionDetails":"full","rewards":false,"commitment":"finalized"})`.
  * **Deviation from the task spec (maxSupportedTransactionVersion 0):** mainnet blocks in this window contain version-1 transactions. Both endpoints answer version-0 requests with error -32015 ("Transaction version (1) is not supported by the requesting client. Please try the request again with the following configuration parameter: maxSupportedTransactionVersion: 1"). The value 1 is the lowest one accepted. The versions of the stored non-vote txs are: legacy 80,259; v0 139,585; v1 128,770.
* Endpoints:
  * Primary: https://solana-rpc.publicnode.com, 3 workers, at most 3 requests in flight, at least 0.15 s between request starts.
  * Secondary: https://api.mainnet-beta.solana.com, 1 worker, at least 2 s between requests. Its response header `x-ratelimit-method-limit` was 6 for getBlock.
  * On a transient RPC error, 429, 5xx or network error, the fetcher backs off exponentially and fails over to the other endpoint.
  * Original fetch run (from `collect/sol_fetch.log`, line "fetch done" at 21:32:47Z): 600 ok, 0 skipped. publicnode made 476 requests and mainnet-beta 127. There were 0 HTTP 429, 0 5xx, 0 network errors and 0 RPC errors.
  * Slots stored per endpoint: 476 from publicnode and 124 from mainnet-beta (column `slots.csv.gz.endpoint`).
  * The first run's `state/fetch-stats.json` was overwritten by a no-op re-run and then removed. From now on, re-runs append to `state/fetch-stats.jsonl`. (2026-10-01: `collect/state/` contains only `pin.json`; no `fetch-stats.jsonl` exists.)
* Vote tx definition: a transaction whose every top-level instruction invokes `Vote111111111111111111111111111111111111111`. Every other transaction is "non-vote". This includes transactions that mix a Vote instruction with other instructions; `vote_tx_mixed_count` counts those, and it is 0 in this window.
* Known DEX/aggregator programs: `dex-programs.csv`, 119 program ids. A tx is a "dex tx" if any of its top-level or inner instructions (from `meta.innerInstructions`) invokes one of them. Account keys are resolved as `accountKeys` + `meta.loadedAddresses.writable` + `meta.loadedAddresses.readonly`.
* Jito tip detection works in two independent ways:
  * (a) `jito_tip_lamports`: the sum of System Program `Transfer` (discriminator 2) and `TransferWithSeed` (discriminator 11) instructions, top-level or inner, whose destination is one of the 8 tip accounts in `jito-tip-accounts.csv`. The instruction data is base58-decoded.
  * (b) `jito_tip_account_balance_delta_lamports`: the sum of `postBalances - preBalances` over the tip accounts present in the tx's account keys. This also catches lamports credited without a System transfer.
* Compute budget (derived): the top-level ComputeBudget instructions are decoded: SetComputeUnitLimit (2), SetComputeUnitPrice (3, micro-lamports per CU), RequestHeapFrame (1) and SetLoadedAccountsDataSizeLimit (4). Version-1 txs carry `message.transactionConfig` instead (computeUnitLimit, priorityFee, heapSize, loadedAccountsDataSizeLimit), stored verbatim. `solana.com_docs_core_fees.md.txt` in docs/ says that the v1 priority fee is an absolute lamport total.
* Jito bundles per slot: `GET https://bundles.jito.wtf/api/v1/bundles/slot/<slot>` for all 600 slots, with 2 requests in flight and at least 0.25 s spacing. The endpoint ignores `limit` and `offset` query parameters. 585 slots returned HTTP 200 with a list, holding 18,737 bundles and 25,051 bundle tx signatures in total. 15 slots returned HTTP 404 `{"error":"Bundle not found"}`: 452085049-452085051, 452085316-452085319, 452085416-452085419 and 452085448-452085451. These responses are stored verbatim; they are the endpoint's answer, not fetch failures.
* Prices: `GET https://coins.llama.fi/prices/historical/1790803614/<coins>?searchWidth=6h`. The timestamp 1790803614 is the blockTime of the middle ok slot. There were 72 requests of 40 coins each, covering 2,854 coins (`coingecko:solana` plus `solana:<mint>` for the 2,853 mints in `token-mints-seen.csv.gz`). The response bodies contain prices for 512 of those coins. Coins absent from a body got no DefiLlama price; that is not an error.

## Integrity checks (descriptive)

* `data/integrity-crosscheck.json`: slots 452084865, 452085065, 452085265 and 452085464 were re-fetched from the other endpoint. For all 4, `blockhash` and `tx_count` are equal. The non-vote tx JSON is equal once two things are set aside:
  * Number formatting: one server writes whole-number floats such as `uiTokenAmount.uiAmount` as `1150` and the other as `1150.0`.
  * Log truncation: `meta.logMessages` is truncated at a different byte limit on each server, marked by a `Log truncated` line. The tx at index 517 of slot 452084865 and the tx at index 571 of slot 452085065 have logs of different lengths.
  * No other field differs.
* 602 of the 348,614 stored non-vote txs contain a `Log truncated` line (column `log_truncated`). Instructions, inner instructions and balances are not affected by log truncation.
* Row counts: the sum of `slots.nonvote_tx_count` (348,614) equals the rows of `txs-nonvote-001.csv.gz` (348,614). The number of rows with `invokes_known_dex=1` (155,170) equals the lines in `dex-txs-001`+`002` (104,636 + 50,534 = 155,170).
* Tip decoding cross-check against Jito's API: for 18,734 of 18,737 bundles returned by `bundles/slot`, the sum of (a) `jito_tip_lamports` over the bundle's `txSignatures` equals the bundle's `landedTipLamports`. All 25,051 bundle tx signatures are among the stored non-vote txs.

## Files

Row counts exclude header rows. "raw" means a value copied verbatim from the source; "derived" means a deterministic decoding or count computed by `collect/sol_build.py`.

### slots.csv.gz (600 rows)
| column | meaning |
|---|---|
| slot | slot number (raw) |
| status | `ok` (block returned), `skipped` (RPC -32007/-32009), or `missing` (no file) |
| block_time | `blockTime`, unix seconds (raw) |
| blockhash, previous_blockhash, parent_slot, block_height | raw getBlock header fields |
| tx_count | number of transactions in the block (derived: count of `transactions`) |
| vote_tx_count | txs whose every top-level instruction invokes the Vote program (derived) |
| vote_tx_mixed_count | txs with a Vote instruction plus at least one other top-level instruction; these are stored as non-vote (derived) |
| nonvote_tx_count | tx_count - vote_tx_count (derived) |
| leader | slot leader identity pubkey from getSlotLeaders (raw) |
| in_getBlocks_result | 1 if the slot is in the getBlocks result (derived) |
| endpoint, fetched_at_utc | which RPC served the block and when |
| rpc_error | verbatim RPC error for skipped slots (empty otherwise) |

### txs-nonvote-001.csv.gz (348,614 rows): one minimal row per non-vote tx
| column | meaning |
|---|---|
| slot, block_time, index | slot, block time (unix s) and position of the tx in the block's `transactions` array |
| signature | first signature (raw) |
| version | `legacy`, `0` or `1` (raw) |
| err_flag | 1 if `meta.err` is non-null (derived) |
| err_json | `meta.err` verbatim JSON (raw) |
| fee | `meta.fee`, lamports (raw) |
| compute_units_consumed | `meta.computeUnitsConsumed` (raw) |
| cost_units | `meta.costUnits` (raw) |
| num_required_signatures | message header (raw) |
| first_signer | first account key, the fee payer (raw) |
| jito_tip_lamports | sum of System transfers to Jito tip accounts, lamports (derived, method (a)) |
| jito_tip_account_balance_delta_lamports | sum of post-pre balance of tip accounts in the tx, lamports (derived, method (b)) |
| invokes_known_dex | 1 if any program in dex-programs.csv is invoked (derived) |
| known_dex_programs | `;`-joined names from dex-programs.csv, in first-invocation order (derived) |
| program_ids | `;`-joined distinct program ids invoked (top-level and inner), in first-invocation order (derived) |
| n_top_level_ix, n_inner_ix | instruction counts (derived) |
| cb_cu_limit, cb_cu_price_micro_lamports | decoded ComputeBudget SetComputeUnitLimit / SetComputeUnitPrice (derived; empty if absent) |
| tx_config_json | `message.transactionConfig` verbatim for v1 txs (raw) |
| log_truncated | 1 if any `meta.logMessages` line equals `Log truncated` (derived) |

### dex-txs-001.jsonl.gz (104,636 lines), dex-txs-002.jsonl.gz (50,534 lines): one JSON object per non-vote tx invoking a known DEX/aggregator program
| key | meaning |
|---|---|
| slot, block_time, index, signature, version | as above |
| err | `meta.err` verbatim |
| fee, computeUnitsConsumed, costUnits | raw meta fields (lamports / CU) |
| signers | first `numRequiredSignatures` account keys (raw) |
| num_required_signatures | raw |
| invoked_programs | ordered list of `[top_level_ix_index, depth, program_id]`; depth 1 = top-level, >1 = `stackHeight` of the inner instruction (raw stackHeight; ordering = top-level ix followed by its inner ixs as listed in `meta.innerInstructions`) |
| known_dex_programs_invoked | `[[program_id, name], ...]` from dex-programs.csv (derived) |
| preTokenBalances, postTokenBalances | verbatim `meta` arrays (accountIndex, mint, owner, programId, uiTokenAmount{amount (base units, string), decimals, uiAmount, uiAmountString}) |
| signer_balances | `[{account, pre, post}]`: preBalances/postBalances (lamports) for the signer accounts (raw values) |
| jito_tip_transfers | `[{top_ix_index, depth, instruction (transfer / transfer_with_seed), from, to, lamports}]` (derived) |
| jito_tip_lamports, jito_tip_account_balance_delta_lamports | as in txs-nonvote (derived) |
| compute_budget_ix_decoded | `{cu_limit, cu_price_micro_lamports, heap_frame_bytes, loaded_accounts_data_size_limit}` when present (derived) |
| transactionConfig | v1 message transactionConfig verbatim (raw; null for legacy/v0) |
| account_keys_resolved | static keys + loaded writable + loaded readonly (derived ordering per Solana spec; values raw) |
| log_truncated | as above |

The full verbatim transaction (message, instructions with data, `innerInstructions`, `logMessages`, all balances, `loadedAddresses`, etc.) of every non-vote tx is in `data/raw-slots/` (local-only: git-ignored, not in the repository).

### data/raw-slots/slot-<slot>.json.gz (600 files, 540 MB total, each well below 90 MB; local-only: git-ignored, not in the repository)
One gzip JSON object per slot:

`{slot, status, endpoint, fetched_at_utc, header{blockTime, blockhash, previousBlockhash, parentSlot, blockHeight}, other_block_fields{}, tx_count, vote_tx_count, vote_tx_mixed_count, vote_tx_indices_mixed[], nonvote:[{index, tx}]}`

`tx` is the getBlock transaction object verbatim (`{transaction:{signatures, message}, meta, version}`). Vote transactions are not stored; only their count is. These files are also the fetch checkpoint.

### jito-tip-transfers.csv.gz (21,509 rows)
One row per System Program transfer instruction (top-level or inner) into a Jito tip account, from any non-vote tx. Columns:
* slot, index, signature
* top_ix_index, depth
* instruction (`transfer` / `transfer_with_seed`)
* from, to, lamports (derived decoding)
* tx_err_flag

### program-invocations.csv.gz (897 rows)
One row per program id invoked by any non-vote tx in the window. All columns are derived counts over the window:
* program_id
* known_dex_name (empty if the program is not in dex-programs.csv)
* nonvote_txs_invoking
* top_level_invocations
* inner_invocations
* nonvote_txs_invoking_with_err

It lists programs outside `dex-programs.csv` too, so the list can be extended and `sol_build.py` re-run without re-fetching.

### token-mints-seen.csv.gz (2,853 rows)
Columns:
* mint
* decimals
* token_program
* dex_txs_with_balance_entry: the number of dex txs whose pre/post token balances include the mint (derived)

### prices-defillama-historical.jsonl.gz (72 lines)
One line per request:

`{batch, url, timestamp_requested (1790803614), fetched_at_utc, http_status, coins_requested[], body}`

`body` is the DefiLlama response verbatim: `coins{<coin>: {symbol, price (USD), timestamp, confidence, decimals}}`.

### dex-programs.csv (119 rows)
| column | meaning |
|---|---|
| program_id, name | program id and name |
| source_url | URL(s) whose fetched body contains the program id. The bodies are in docs/program-id-sources/ with index.csv (sha256, fetch time) |
| source_kind | `official_docs_or_repo`: Raydium docs; GitHub repos of Orca, Meteora, Phoenix/Ellipsis, OpenBook, pump-fun, Jupiter, OKX, Saber, Manifest, Sanctum; the npm packages of Lifinity and Jupiter served by unpkg. `jupiter_program_id_to_label_api`: https://lite-api.jup.ag/swap/v1/program-id-to-label and https://api.jup.ag/swap/v1/program-id-to-label, which are Jupiter's lists of the venues its router uses; both are stored verbatim. Empty = not found in any source tried |
| id_found_in_source | 1/0 |
| jupiter_label | label in Jupiter's map, if present |
| onchain_exists, onchain_executable, onchain_owner, onchain_checked_slot, onchain_checked_at_utc | `getMultipleAccounts` on api.mainnet-beta.solana.com at 2026-09-30T21:35:27Z. All 119 exist and are executable; the owners are BPFLoaderUpgradeable (118) and BPFLoader2 (1) |
| sources_tried | every URL tried, with HTTP status |

Two rows have `id_found_in_source=0`: `j1o2qRpjcyUwEvwtcfhEQefh773ZgjxcVRry7LDqg5X` (Jupiter Limit Order v2) and `DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH` (DFlow Aggregator v4). Their ids were not found in the fetched official pages; docs.dflow.net returned a proxy 502. Both are executable on-chain and both are used in the dex classification.

### jito-tip-accounts.csv (8 rows)
Source: `getTipAccounts` on https://mainnet.block-engine.jito.wtf/api/v1/getTipAccounts. The verbatim response is in `docs/program-id-sources/jito-block-engine-getTipAccounts.json`. All 8 accounts also appear in https://docs.jito.wtf/lowlatencytxnsend/ and in the jito-docs GitHub markdown (column found_in_docs_urls). The on-chain owner of all 8 is `T1pyyaTNZsKv2WcRAB8oVnk93mLJw2XzjtVYqCsaHqt`.

### tip-floor.jsonl (61 lines: 61 polls, one every 60 s from 2026-09-30T21:30:07Z to 22:30:07Z; 60 with HTTP 200)
One line per poll:

`{poll_no, fetched_at_utc, url, http_status, body}`

`body` is the https://bundles.jito.wtf/api/v1/bundles/tip_floor response verbatim: `[{time, landed_tips_25th/50th/75th/95th/99th_percentile, ema_landed_tips_50th_percentile}]`, with values in SOL. The row count is filled in on completion (sentinel SOL_JITO_TIPFLOOR). Polling started 2 min after the sample window ended (21:28:13Z) and runs for about 60 min (last poll expected around 22:29Z).

Correction 2026-10-01 (the text above was written while polling was running): polling finished with sentinel SOL_JITO_TIPFLOOR.DONE at 2026-09-30T22:31:07Z. The file has 61 lines, poll_no 1 to 61; the last poll was at 22:30:07Z. 60 polls have HTTP 200 and a `body`. Poll 40 (2026-09-30T22:09:07Z) failed with `('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))`; its line has `http_status` null and an `error` field instead of `body`. `collect/jito_tip_floor.pid` (content `2255`) is the PID file of the finished poller; no process is running.

### data/jito-bundles-by-slot.jsonl.gz (600 lines)
One line per slot:

`{slot, url, fetched_at_utc, http_status, body}`

`body` is verbatim: a list of `{bundleId, slot, validator, tippers[], landedTipLamports, landedCu, blockIndex, timestamp, txSignatures[]}`, or `{"error":"Bundle not found"}` with HTTP 404. `data/jito-bundles-by-slot.parts/` is the per-slot checkpoint and holds the same content. (2026-10-01: the parts directory is local-only, git-ignored; verified that each of its 600 files equals one line of the .jsonl.gz without the trailing newline.)

### data/ (other)
* `slot-leaders.json`: getSlotLeaders, verbatim.
* `get-blocks.json`: getBlocks, verbatim.
* `integrity-crosscheck.json`: the cross-endpoint check.
* `build-summary.json`: part files and row counts.
* `prices.parts/`: the prices checkpoint. (2026-10-01: local-only, git-ignored; verified that each of its 72 files equals one line of `../prices-defillama-historical.jsonl.gz` without the trailing newline.)

No `fetch-gaps.csv`, `jito-bundles-gaps.csv` or `prices-gaps.csv` exists, because nothing failed.

### snapshots/ (index.csv lists URL, method, params, fetch time, HTTP status and file)
Verbatim gzip bodies, fetched 2026-09-30T21:40:53Z to 21:41:34Z:
* **DefiLlama:**
  * `overview/dexs/solana`, in default form and in `dataType=dailyVolume` form with the breakdown
  * `overview/aggregators/solana`
  * `overview/fees/solana`
  * `summary/fees/jito-mev-tips`, `summary/fees/jito`
  * `overview/dexs` (all chains)
* **Jito Kobe API:**
  * `mev_rewards`, `daily_mev_rewards`
  * `validators`, `jitosol_validators` (identity_account, vote_account, running_jito, running_bam, mev_commission_bps, ...)
  * `stake_pool_stats`
* **Jito bundles API:** `tip_floor`, plus `recent` with limit=1000, sorted by Time, by Tip over a Day, and by Tip over a Week.
* **Solana RPC:** `getEpochInfo`, `getVoteAccounts` (identity to vote account), `getClusterNodes` (identity to version), `getRecentPerformanceSamples(60)`, `getRecentPrioritizationFees`, `getVersion`.

`defillama-dexs.json` in this directory is the uncompressed verbatim body of https://api.llama.fi/overview/dexs/solana, the same as `snapshots/defillama__api.llama.fi_overview_dexs_solana.json.gz`.

### docs/ (index.csv lists URL, final URL, HTTP status, fetch time and file stem; fetched 2026-09-30T21:43-21:44Z)
Each document is saved as verbatim visible text (`.txt`, headed by URL and fetch time) together with the raw body (`.html.gz` or `.raw.gz`):
* **Jito:**
  * docs.jito.wtf (index; `lowlatencytxnsend`: bundles, auction, tips, tip accounts, sendBundle/sendTransaction)
  * jito-docs `lowlatencytxnsend.md` (GitHub raw)
  * mev-protos `json_rpc/http.md`
  * jito-foundation gitbook `mev` and `on-chain-addresses`
  * jito-solana README
  * bam.dev and bam.dev/blog/introducing-bam
* **Anza:**
  * docs `consensus/leader-rotation`, `validator/tpu`, `proposals/fee_transaction_priority`
  * blog: central scheduler; transaction landing on TPU
* **solana.com** (markdown versions `*.md.txt`, plus the HTML versions):
  * core/fees, fees/fee-structure, fees/compute-budget
  * transactions/versioned-transactions (v1 format), transactions/transaction-pipeline
  * defi/mev-protection (Jito dontfront), defi/stake-weighted-qos
  * references/clusters (public RPC rate limits)
  * rpc/http/getblock, rpc/http/getslotleaders

The HTML versions of solana.com pages (`solana.com_docs_core_fees.txt`, `solana.com_developers_guides_advanced_how-to-use-priority-fees.txt`) are mostly navigation text; the `.md.txt` files hold the page content.

Failed fetches:
* 404: jito-foundation.gitbook.io `mev-payment-and-distribution/how-tips-work` and `searcher-resources/bundles`
* 403: www.jito.network/blog/jito-solana-is-now-open-source
* network error: docs.bam.dev

### docs/literature/ (index.csv)
* **arXiv API listings (raw Atom XML):** 6 queries combining solana with arbitrage, MEV, jito, sandwich or "transaction fees". Queries are in `collect/arxiv_queries.sh` and fetch times in `arxiv-query-solana-arbitrage-mev.fetched_at_utc.txt`.
* **Documents fetched verbatim** (PDF plus extracted text, or HTML plus text):
  * Helius "Solana MEV Report" (www.helius.dev/blog/solana-mev-report)
  * arXiv 2607.28424 "Demystifying Solana Bots: From GitHub Blueprints to On-Chain Fingerprints" (abs + pdf)
  * arXiv 2609.38056 "Active Liquidity On Chain: Evidence from PropAMMs Across Chains" (abs + pdf)
  * arXiv 2609.28115 "No Place to Hide: An Analysis on Protected Order Flow Sandwich Attacks" (abs)
  * IMC'26 "Quantifying the Threat of Sandwiching MEV on Jito" (cnitarot.github.io/papers/imc26_solana.pdf)
  * Extropy "An Analysis of Arbitrage Markets Across Ethereum, Solana, ..." (academy.extropy.io)

## Reproduce

All commands run from `/home/user/dapparb/research-material/06-other-chains-onchain/solana/collect`.

```
python3 programs.py > programs.log 2>&1        # dex-programs.csv, jito-tip-accounts.csv, docs/program-id-sources/
setsid nohup bash sol_pipeline.sh > sol_pipeline.log 2>&1 < /dev/null &
    # = sol_fetch.py --n 600 (pins a NEW window at the current finalized slot unless state/pin.json exists; resumable per slot)
    #   -> jito_bundles.py -> sol_build.py -> prices.py -> sentinel SOL_SAMPLE.DONE/.FAILED
setsid nohup python3 -u jito_tip_floor.py --snapshots 60 --interval 60 > jito_tip_floor.log 2>&1 < /dev/null &
python3 snapshots.py > snapshots.log 2>&1
python3 fetch_docs.py ../docs $(cat docs_urls.txt) > fetch_docs.log 2>&1
python3 fetch_docs.py ../docs/literature $(cat docs_urls_literature.txt) > fetch_docs_literature.log 2>&1
bash arxiv_queries.sh
```

* To rebuild the tables from the stored raw slots only, for example after extending dex-programs.csv, run `python3 sol_build.py`, then `python3 prices.py` (delete `../data/prices.parts/` first if the mint list changed).
* To sample a new window instead of resuming this one, move `state/pin.json`, `../data/raw-slots/`, `../data/slot-leaders.json`, `../data/get-blocks.json`, `../data/integrity-crosscheck.json` and `../data/jito-bundles-by-slot.parts/` aside first.
* `fetch_docs.py` is an identical copy of `../_shared_collect/fetch_docs.py`.

## Coverage limits and gaps

* **One window only:** 600 consecutive slots, 2026-09-30T21:25:34Z to 21:28:13Z, which is about 2 min 39 s of block time. No other time of day, weekday or market condition was sampled. The target of 600 slots was met, and rate limits did not force a smaller sample.
* **maxSupportedTransactionVersion** is 1, not 0 as specified; see Method. With 0, no block of this window can be fetched.
* **Vote transactions** are counted but not stored.
* **logMessages** are as served by the endpoint that served each slot. Servers truncate logs at different byte limits: 602 txs contain `Log truncated`. The endpoint per slot is in `slots.csv.gz`.
* **The DEX classification** depends on `dex-programs.csv`: 119 ids from official docs/repos plus Jupiter's program-id-to-label maps.
  * Programs that are not in that list are not classified as DEX, even if they swap. Examples: private or proprietary bot programs that implement swaps themselves, programs not routed by Jupiter, and launchpads other than those listed.
  * Txs that invoke a listed program only through CPI from a bot program are captured, because inner instructions are included.
  * Every invoked program id with counts is in `program-invocations.csv.gz`, and the per-tx list is in `txs-nonvote-*.csv.gz.program_ids`. Both allow reclassification without re-fetching.
  * `pfeeUxB6jkeY1Hxd7CsFCAjcbHA9rWtchMGdZ6VojVZ` and similar helper programs are not in the list.
* **Two program ids are not confirmed** in an official source (see dex-programs.csv); both are on-chain executables. Lifinity v1/v2 are not in Jupiter's current label maps; they are included from Lifinity's npm SDK.
* **Jito tip detection:**
  * Method (a) only sees System Program transfer instructions to the 8 tip accounts.
  * Method (b) sees any net balance change of a tip account inside the tx. The tip accounts' own sweeps by the tip-payment program could also appear in (b).
  * Tips paid in a separate tx of a bundle are attributed to that separate tx. Bundle membership is in `data/jito-bundles-by-slot.jsonl.gz`.
* **Jito bundles API:** 15 slots answered 404 "Bundle not found" (listed in Method). The endpoint has no documented pagination and ignores limit/offset, so it cannot be verified from this side whether a slot's list is complete.
* **Jito off-chain data is not collected:** submitted-but-not-landed bundles, auction bids and losing tips are not available from public endpoints and are not collected. BAM-specific ordering data is not collected, apart from `running_bam` in the Kobe validators snapshot.
* **No arbitrage identification, profit computation or USD conversion was done.** Prices are raw DefiLlama bodies. 2,342 of 2,854 requested coins have no DefiLlama price at the window timestamp (searchWidth 6h).
* **Pool liquidity** is available only as the token balances of accounts touched by txs in the window. No pool enumeration, pool-state (getAccountInfo/getProgramAccounts) snapshot or per-pool liquidity listing was collected.
* **Solana live search:** no engine run or live opportunity search was done on Solana. The repository engine (bot/) is EVM-only, and nothing under bot/ was touched.
* **Snapshots** (Kobe, DefiLlama, RPC state, recent bundles) were fetched once, at 21:40:53-21:41:34Z, which is about 13 min after the window ended, not during it.
* **Literature** is limited to the arXiv API query results and the 6 documents listed. It is not a systematic literature search. The 6 arXiv API queries returned 2 (solana AND MEV), 5 (solana AND "transaction fees"), 2 (solana AND arbitrage), 0 (solana AND jito), 1 (solana AND sandwich) and 4 (solana-arbitrage-mev) entries; see the Atom files in docs/literature/. (Rewritten 2026-10-01 as entry counts.)
* **Other chains:** BSC and the other EVM chains are in sibling directories (../bsc, ../arbitrum, ../optimism, ../unichain, ../ethereum, ../polygon). No other non-EVM chain (for example Sui, Aptos or TON) was collected.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory, including the local-only files (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document (including each of the 600 raw-slot files and each part file) parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine. The three local-only directories are listed as one row each; their per-file bytes, checks and sha256 are in `local-only-inventory.tsv` (written 2026-10-01, committed).

Result: 1,469 files as collected (189 committed, 1,280 local-only), plus `local-only-inventory.tsv` written during finalization on 2026-10-01 (committed). All 705 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. Largest committed file: dex-txs-001.jsonl.gz (83,894,137 bytes); no committed file exceeds 90 MB.

Counts stated in this manifest compared with the verified counts: all equal except `tip-floor.jsonl`, whose count was not yet stated (now 61 lines; see the correction under tip-floor.jsonl). Checked: slots.csv.gz 600 (all status ok; tx_count sum 750,426, vote 401,812, non-vote 348,614, vote_tx_mixed 0; 92 distinct leaders; endpoint 476 publicnode / 124 mainnet-beta); txs-nonvote-001.csv.gz 348,614 (versions legacy 80,259 / 0 139,585 / 1 128,770; log_truncated 602; invokes_known_dex 155,170); dex-txs-001/002.jsonl.gz 104,636 + 50,534 = 155,170; jito-tip-transfers.csv.gz 21,509; program-invocations.csv.gz 897; token-mints-seen.csv.gz 2,853; prices-defillama-historical.jsonl.gz 72 (2,854 coins requested, 512 present in the bodies); dex-programs.csv 119 (owners 118 BPFLoaderUpgradeable, 1 BPFLoader2; id_found_in_source=0 for 2); jito-tip-accounts.csv 8; data/jito-bundles-by-slot.jsonl.gz 600 (585 HTTP 200 with 18,737 bundles and 25,051 tx signatures, 15 HTTP 404); data/raw-slots/ 600 files.

Local-only files and how to regenerate them:
* `data/jito-bundles-by-slot.parts/<slot>.json` (600 files, 8,577,414 bytes; `.gitignore` rule `research-material/**/*.parts/`): each file is one line of the committed `data/jito-bundles-by-slot.jsonl.gz` without its trailing newline (verified for all 600). Exact offline rebuild (run on 2026-10-01 into a scratch directory; all 600 files came out byte-identical), run in `solana/`: `python3 -c "import gzip,json,os; d='data/jito-bundles-by-slot.parts'; os.makedirs(d,exist_ok=True); [open(os.path.join(d,'%d.json'%json.loads(l)['slot']),'w').write(l.rstrip(chr(10))) for l in gzip.open('data/jito-bundles-by-slot.jsonl.gz','rt')]"`. (Running `collect/jito_bundles.py` instead would re-fetch from the Jito API and rewrite the committed .jsonl.gz.)
* `data/prices.parts/<batch>.json` (72 files, 396,869 bytes; same rule): each file is one line of the committed `prices-defillama-historical.jsonl.gz` without its trailing newline (verified for all 72). Exact offline rebuild (run on 2026-10-01 into a scratch directory; all 72 files came out byte-identical), run in `solana/`: `python3 -c "import gzip,json,os; d='data/prices.parts'; os.makedirs(d,exist_ok=True); [open(os.path.join(d,'%05d.json'%json.loads(l)['batch']),'w').write(l.rstrip(chr(10))) for l in gzip.open('prices-defillama-historical.jsonl.gz','rt')]"`. (Running `collect/prices.py` with the parts missing would re-fetch from DefiLlama and rewrite the committed .jsonl.gz.)
* `collect/state/pin.json` (1 file, 551 bytes; rule `research-material/**/collect/state/`): recreate it with exactly this content and no trailing newline (sha256 in the table below; checked 2026-10-01 that this text hashes to it):

```json
{
 "pinned_at_utc": "2026-09-30T21:28:22.954656Z",
 "finalized_slot_at_pin": 452085464,
 "start_slot": 452084865,
 "end_slot": 452085464,
 "n_slots": 600,
 "getBlock_config": {
  "encoding": "json",
  "maxSupportedTransactionVersion": 1,
  "transactionDetails": "full",
  "rewards": false,
  "commitment": "finalized"
 },
 "endpoints": {
  "primary": "https://solana-rpc.publicnode.com",
  "secondary": "https://api.mainnet-beta.solana.com"
 },
 "vote_tx_definition": "every top-level instruction invokes Vote111111111111111111111111111111111111111"
}
```

* `data/raw-slots/slot-<slot>.json.gz` (600 files, 564,677,263 bytes; rule `research-material/**/raw-slots/`): the verbatim getBlock responses (vote transactions counted, not stored). To re-fetch: recreate `collect/state/pin.json` as above, then `cd solana/collect && python3 -u sol_fetch.py --n 600 > sol_fetch.refetch.log 2>&1` (resumes from the pin; writes only missing `slot-*.json.gz` files and appends to `state/fetch-stats.jsonl`; `data/slot-leaders.json`, `data/get-blocks.json` and `data/integrity-crosscheck.json` already exist and are not rewritten). This needs RPC endpoints that still serve getBlock for slots 452084865-452085464. Re-fetched files carry new `endpoint` / `fetched_at_utc` values and possibly different `logMessages` truncation, so their checksums will differ from `local-only-inventory.tsv`. `sol_build.py` rebuilds the committed tables from these files and is not needed to restore them.
* `collect/__pycache__/*.pyc` (7 files, 107,098 bytes; rules `research-material/**/__pycache__/` and `*.pyc`): Python bytecode caches of the collect/ scripts, recreated automatically when the modules are imported (or `python3 -m py_compile collect/<script>.py`); no collected data depends on them.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| collect/__pycache__/jito_bundles.cpython-311.pyc | 9,971 | compiled Python bytecode | 35c84377397763c2741534187c05c45e10d1776e02a99ccb73428a22ccd17023 | local-only |
| collect/__pycache__/jito_tip_floor.cpython-311.pyc | 5,164 | compiled Python bytecode | 21e24672396d8347fd0d3faa7e36e78cd231780dee574c18cc23b8d54c307f56 | local-only |
| collect/__pycache__/prices.cpython-311.pyc | 7,881 | compiled Python bytecode | 934f28fb390021bb0b0ea395f321b41d633e84772050f717463aea6f665f1f06 | local-only |
| collect/__pycache__/programs.cpython-311.pyc | 19,207 | compiled Python bytecode | a52f57858499e13184ee43d591077a7441d5e2f901136f6f016fa5bef584aede | local-only |
| collect/__pycache__/snapshots.cpython-311.pyc | 8,041 | compiled Python bytecode | 1cd032eba8d27ecbcf40486d3031d50123b8776f530cce26f3b3b44d4dc4ec20 | local-only |
| collect/__pycache__/sol_build.cpython-311.pyc | 26,882 | compiled Python bytecode | 1ed4eec18cc0e20ee3406609797f13b8e6769c2b2d244ad012d21ccc118e2d6d | local-only |
| collect/__pycache__/sol_fetch.cpython-311.pyc | 29,952 | compiled Python bytecode | c5a5ebd12520f9cbf84a4f5cb8cb8c0c017158831ee3f2182bab4bf5b55ba4b5 | local-only |
| collect/arxiv_queries.sh | 909 | 9 lines | bc679a901d6f47ae4272b9909293fce896d5b885d4f65582cf7e0e0e26e69bbc | committed |
| collect/docs_urls.txt | 1,722 | 32 lines | 4ef99bed191a4a16c39385c158b87c8bc9278ec26cd6bf74b656fe600f094870 | committed |
| collect/docs_urls_literature.txt | 338 | 8 lines | fc2a8945b69950ff047b0104e3c08e32a193075d2ee63f03a87f3575a651f8c4 | committed |
| collect/docs_urls_md.txt | 515 | 10 lines | 2b435dc5d5e32ab399b079d141c81a1e3f2bebd92ac53f3e47eba1d6c63e365b | committed |
| collect/fetch_docs.log | 3,511 | 32 lines | 7e551cf18ca30f799aa9158c65568dcf969a87f710b68b8079b6ff5241c08683 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/fetch_docs_literature.log | 807 | 9 lines | 7ee191b42818cb64f6269d66debb958f4f4a6c785ed890a7ee47e08b8d0b3450 | committed |
| collect/jito_bundles.log | 619 | 16 lines | 8e1992773e7bc2928a80ecbd4f4165130490e7709573a9b72b6133eccd7b928b | committed |
| collect/jito_bundles.py | 3,952 | 70 lines | 1b42ef09d17957ce71d4ef08e5e7bc5cfe2f0ac7a4930e532a1d7e06f99aa732 | committed |
| collect/jito_tip_floor.log | 3,216 | 61 lines | e99724fd5a4c194f1b3402f04736141e71eaed9361a6e88de7f52b8e1863ee7c | committed |
| collect/jito_tip_floor.pid | 5 | 1 line | ff31adcf59fdfe09b5ef3e6873d41c398a0912a886c38242d76900ffecd6cb24 | committed |
| collect/jito_tip_floor.py | 2,523 | 44 lines | 11f1c0d88a0cbf321e333e8383b55cbc73575487024d30ebabbf1435df132ff5 | committed |
| collect/prices.log | 3,175 | 72 lines | b7ff4292b8bb91b46704a61cef8642046c6cc196cc05e41b6fc852bba9204359 | committed |
| collect/prices.py | 3,497 | 53 lines | 91987a01351d4aa446f1fa374bd36d32b7313a3daf1fff406e055e46805d1ff2 | committed |
| collect/programs.log | 474 | 2 lines | 68c27d3228cb422bc6373314376b86689d9e405b9eae77fe6efd8c7f8c47622a | committed |
| collect/programs.py | 12,738 | 188 lines | 3b25c26d896d434f0405b4476a5a76077a00b8197d390984e23319337993c4ca | committed |
| collect/snapshots.log | 1,803 | 22 lines | 6e78b4c2083b44fa92a3c07ca1110c0ee276c8964303ee307afbbd0f14819029 | committed |
| collect/snapshots.py | 5,054 | 83 lines | 35d441b46f446ac83c3ae62f09234e1aa598edfc69eb924a7600cab473c3601d | committed |
| collect/sol_build.log | 29 | 1 line | 683568c5f6d13e394cf6d0d96e8d5faac959f4bca78cf938353d07323ad52112 | committed |
| collect/sol_build.py | 12,769 | 176 lines | d9f4760eb03c44e72a97ca9c3c622dc7bec94eb76e3d515a66deab814a8392e8 | committed |
| collect/sol_fetch.log | 14,187 | 41 lines | d177d0a80a9113c88c19c67574e55880dc98c012d237e184442318a9ed38332a | committed |
| collect/sol_fetch.py | 15,520 | 283 lines | e0bfbb2aba42ce7d4e75283b3d4b88243efb3ed9e15a7da131d1cfd00e517e07 | committed |
| collect/sol_pipeline.log | 26 | 1 line | 93a06f52bde378a76bd04d12c4b9731cf9ca755da2372f0372ad590b908b18f0 | committed |
| collect/sol_pipeline.sh | 1,520 | 17 lines | e3faffe743555298f34ea98d2670a6b45acba784c28d2f2edb00608b11cf8247 | committed |
| collect/state/pin.json | 551 | 1 JSON document | 5ccd53405c107f8cc7db66fa7c11df6010f925644054461a719d07b68b35dbd4 | local-only |
| data/build-summary.json | 220 | 1 JSON document | 3e3e460319acac8ccd0aed1e320c863a737b536518d18a1d0ecf31bb227c3e06 | committed |
| data/get-blocks.json | 6,762 | 1 JSON document | 21c4377d8e943f8873dd464f424503d96fbe54b2aba726857b77f9a5feb33799 | committed |
| data/integrity-crosscheck.json | 3,078 | 1 JSON document | dd13ce5b17811cc918484605f6d4d3b2a78b98d011e5762e97e0152cdae789bb | committed |
| data/jito-bundles-by-slot.jsonl.gz | 3,179,438 | 600 JSON lines | 22e535b01c859250481818ebd9b9b87269f6b46f732a12a3a72dfce9c6f0dc00 | committed |
| data/slot-leaders.json | 28,824 | 1 JSON document | ffd7505383d48c07dc905b0585d8ad2df9ec68ec2daf8fc410503869601671e5 | committed |
| defillama-dexs.json | 1,058,337 | 1 JSON document | a9e1c87437b888967014b4a3a1e28025d467551fd9fd4530220a50a857a997ad | committed |
| dex-programs.csv | 36,856 | 119 rows + header | f28cd6ede4bda4f5035506c04da2034b1723ca6e9cec17c0a6c72dc9d65c65d1 | committed |
| dex-txs-001.jsonl.gz | 83,894,137 | 104,636 JSON lines | 362852c61b7b881225b27009ec8bfd52dc11e21f2493c2f2fdeb534784861db7 | committed |
| dex-txs-002.jsonl.gz | 40,111,499 | 50,534 JSON lines | 7ba1ce301cf0161318c67ac0dc5efef12b00fb70f3ec6b8f0267145fa7e71fc8 | committed |
| docs/bam.dev.html.gz | 6,681 | 0 lines (decompressed) | 5aecd4662d84c5235b23e910ccbbff40d29f3641b1f45be0404ed46448025f4f | committed |
| docs/bam.dev.txt | 4,075 | 115 lines | 5015a010a1be5ac4b5da47494ffd01716bb3b710be01cfb3114bd18b4614f0fe | committed |
| docs/bam.dev_blog_introducing-bam.html.gz | 9,998 | 12 lines (decompressed) | 7e4b0bd47022ff39b7590164378efee1383a021b69e77d677281cc8cc72620cc | committed |
| docs/bam.dev_blog_introducing-bam.txt | 12,512 | 126 lines | edb0f7060557c23ceb956993545fc7795de048577ec028e4706df2744107ee61 | committed |
| docs/docs.anza.xyz_consensus_leader-rotation.html.gz | 8,168 | 69 lines (decompressed) | 728a236ff3b3fdbe16dc54ca105b7f4fdc50b21559174528457bf5ac9d04757d | committed |
| docs/docs.anza.xyz_consensus_leader-rotation.txt | 9,439 | 229 lines | 7d0aa21e5535227622344af5083fb1985a2723f37e300213a656ca29e7fc57d8 | committed |
| docs/docs.anza.xyz_proposals_fee_transaction_priority.html.gz | 8,876 | 121 lines (decompressed) | 9299b27be08a0bd458c9e4693616e65d4c644735026578c2c456cb5e91d64187 | committed |
| docs/docs.anza.xyz_proposals_fee_transaction_priority.txt | 10,691 | 428 lines | 4b2d6060f2890a10aa0615bfbe30b173037afa417c5d6dfbb553865f2180db9a | committed |
| docs/docs.anza.xyz_validator_tpu.html.gz | 8,931 | 59 lines (decompressed) | b935db0c183420709198c701366b197a3b0fdb8be80d838a6fb7fafd9b520781 | committed |
| docs/docs.anza.xyz_validator_tpu.txt | 3,424 | 156 lines | 88cd2291c90117fc1ebaafd57a95f2fb925b468edc483ead5f5fd40a7c2f4984 | committed |
| docs/docs.jito.wtf.html.gz | 4,475 | 320 lines (decompressed) | 1a248e05c4c1a01ab71f80def7250fcf4297fa948aa5553ab513cbbfd598e36a | committed |
| docs/docs.jito.wtf.txt | 4,089 | 299 lines | fddcef444e214b831651ec59d18105af3acae23dc93e4bb1fc137155edb5d3e6 | committed |
| docs/docs.jito.wtf_lowlatencytxnsend.html.gz | 18,948 | 1,229 lines (decompressed) | 6d00c8bbcb38367f593aa473b94d7b3980fc47d41bfda2760fef06182301be33 | committed |
| docs/docs.jito.wtf_lowlatencytxnsend.txt | 33,653 | 1,173 lines | 55ddd87152c1fb795757b20e2d26000aee8863c96dc564f549b55bfd781b10bc | committed |
| docs/index.csv | 6,056 | 32 rows + header | 56d73af93410838da24d363e751bfe48909c71a41a0000eea15c9c9476c62f2c | committed |
| docs/jito-foundation.gitbook.io_mev.html.gz | 55,840 | 688 lines (decompressed) | f7ed9bc581149b789b33e33eb683db26f57c319304c0f8e22d9281de22a5828c | committed |
| docs/jito-foundation.gitbook.io_mev.txt | 1,197 | 99 lines | 9cdc86c25b31ffe4447daa423a4870119fbc93a77e82bf26a45254572d8d33db | committed |
| docs/jito-foundation.gitbook.io_mev_mev-payment-and-distribution_on-chain-addresses.html.gz | 63,370 | 703 lines (decompressed) | 1baf049a2c86396d59cb754149434ef9064f25cdfdb4c45f0e0ca6d6f06c3425 | committed |
| docs/jito-foundation.gitbook.io_mev_mev-payment-and-distribution_on-chain-addresses.txt | 2,590 | 139 lines | 5aeb7674d0ed5d588537e28bf403abfbdd05020ab7a93a7d948f3aaaf1260b71 | committed |
| docs/literature/academy.extropy.io_pages_articles_mev-crosschain-analysis-2025.html.html.gz | 12,733 | 435 lines (decompressed) | a4fbcacfa7a3752adb09cabd661c91eb465bbe7dc0bbc37a4239060a929c82f1 | committed |
| docs/literature/academy.extropy.io_pages_articles_mev-crosschain-analysis-2025.html.txt | 24,284 | 400 lines | a7073941ff79e9372694b8c96b10e5c010648635bbc930115ba5362e51587500 | committed |
| docs/literature/arxiv-query-all_solana_AND_all_MEV_.atom.xml | 6,105 | 80 lines | 89c55cbede69e0d0ba629ea38ade5185da9f9e3554306d704d9bc096166cb8e2 | committed |
| docs/literature/arxiv-query-all_solana_AND_all__22transaction_fees_22_.atom.xml | 13,754 | 168 lines | 72fb772ff2b412498d9ac4300a2f9f5c89e9f9379b4103a19324f229eb4eb04f | committed |
| docs/literature/arxiv-query-all_solana_AND_all_arbitrage_.atom.xml | 5,655 | 48 lines | 6329c8d6ceeefa2a202384d273f3e95a9f948800f3a0d10714cae28233bb4a8c | committed |
| docs/literature/arxiv-query-all_solana_AND_all_jito_.atom.xml | 723 | 10 lines | 99d05d991842f8753f35bc980f417c5b23afdd07da7c34d1ba3ae0c3fc698c3a | committed |
| docs/literature/arxiv-query-all_solana_AND_all_sandwich_.atom.xml | 3,364 | 35 lines | d9309809a7556f1d9b779efcad39d18f8f33d92d4d24f22079e07176812f888b | committed |
| docs/literature/arxiv-query-solana-arbitrage-mev.atom.xml | 11,289 | 111 lines | f4dd47374632517573b813437181989bb6cfa79814f5eb2649df7d2de2d34b8a | committed |
| docs/literature/arxiv-query-solana-arbitrage-mev.fetched_at_utc.txt | 42 | 2 lines | 9474f04eb82c1c716c9a2c91c4456cd826dafd4e909e86962a6a1e54331bcaf0 | committed |
| docs/literature/arxiv.org_abs_2607.28424.html.gz | 9,412 | 649 lines (decompressed) | 98054b1cbfec697a8105b0ee948e643e8576e85294909efc4a34be519e792555 | committed |
| docs/literature/arxiv.org_abs_2607.28424.txt | 5,729 | 271 lines | 1180f74f90a18970e1be78c9aa310710254a67a2bf60bcdcdfb58500bfc52712 | committed |
| docs/literature/arxiv.org_abs_2609.28115.html.gz | 9,178 | 624 lines (decompressed) | 955a4e26ac3aaaae577689bef5d7acbf6ac0780202c1c1ca4cea769d8e717d05 | committed |
| docs/literature/arxiv.org_abs_2609.28115.txt | 5,678 | 261 lines | f931359484064afdba10d31912421d616d3e440c2dcaf5c7d8f4a66323aa6c11 | committed |
| docs/literature/arxiv.org_abs_2609.38056.html.gz | 9,042 | 622 lines (decompressed) | b2576d3b2c5fa9c269a0a57404a8564ebb98eac94bffeac29102efdb9f69e8e4 | committed |
| docs/literature/arxiv.org_abs_2609.38056.txt | 5,460 | 259 lines | 49e357ae1ee4f2a77937c980a8656f1002f70340e71d48d8c0ef606bf06b85a3 | committed |
| docs/literature/arxiv.org_pdf_2607.28424.pdf | 1,068,738 | PDF (binary) | dee9a9bbfb6b93b0db2155a1856d02e1baf8aef94d48378324dccc199488e773 | committed |
| docs/literature/arxiv.org_pdf_2607.28424.txt | 111,886 | 2,449 lines | de0f83a7a2dd391b21b60b3b359d977ec2d846682e40328606b7da576558eda1 | committed |
| docs/literature/arxiv.org_pdf_2609.38056.pdf | 1,579,494 | PDF (binary) | 5fceb691c5bafbcf8330c4f67a7ab7ebc81498178bcd852bb24532b72dcd440b | committed |
| docs/literature/arxiv.org_pdf_2609.38056.txt | 74,054 | 2,071 lines | 2c39ee6d8ae5be0b8b325f0700bc1bac796e8bfb6ffce8a57ac1c8b4cbafc7e4 | committed |
| docs/literature/cnitarot.github.io_papers_imc26_solana.pdf | 553,929 | PDF (binary) | 2f5963f2a683ad5b8814c687ef8e694f1ce1d56e2794059660f038cdbff2d685 | committed |
| docs/literature/cnitarot.github.io_papers_imc26_solana.pdf.txt | 43,598 | 838 lines | 19976110b61200abbd6b5c993a34eaa657198c0ae3e73cba003a48ee467a4237 | committed |
| docs/literature/index.csv | 1,223 | 8 rows + header | 3d6a0a5c4b212695befdbb36b70e32caff4d1280e3b8151d806b35e69848211b | committed |
| docs/literature/www.helius.dev_blog_solana-mev-report.html.gz | 101,772 | 644 lines (decompressed) | 85e6880c53f630a50d730637da08e0460d7df3412d0dfc98a0d767ac2329385d | committed |
| docs/literature/www.helius.dev_blog_solana-mev-report.txt | 55,545 | 1,021 lines | 5dae9b034368036fb5b596bca208d7324911cf6ed3cba5c4c3eb6736375bd451 | committed |
| docs/program-id-sources/api.jup.ag_swap_v1_program-id-to-label.body.gz | 4,364 | 0 lines (decompressed) | f850d188ba1226fd93e29ac78f7a8ecae0b7d6ad3dd4f8b76e98ab10130f47df | committed |
| docs/program-id-sources/dev.jup.ag_docs.body.gz | 52,880 | 208 lines (decompressed) | ebac2c74053bd529e3157444f33d9d28d87be2f575eaf912afb7c5b6eaa42c91 | committed |
| docs/program-id-sources/docs.jito.wtf_lowlatencytxnsend.body.gz | 18,948 | 1,229 lines (decompressed) | 6de388bd4450498aa21978a32f019cc091d4c6e525bbb46ef2c8a8cb4dba5d07 | committed |
| docs/program-id-sources/docs.meteora.ag_developer-guides_dbc.body.gz | 46,489 | 187 lines (decompressed) | ce2661886629760070106d8e6951300d409830f65581b8f4377e731140b5cb93 | committed |
| docs/program-id-sources/docs.raydium.io_products_amm-v4.body.gz | 60,472 | 679 lines (decompressed) | 9544a1b199f59c3db115c955ea11bed1bf41c8f4fa5ebd4d951d9264ba7759a0 | committed |
| docs/program-id-sources/docs.raydium.io_products_clmm.body.gz | 59,516 | 676 lines (decompressed) | 0d14d59e037522a6d12d0a1dec0f7c5048b102f53a6c9ab8aa5dde8c1541851b | committed |
| docs/program-id-sources/docs.raydium.io_products_cpmm.body.gz | 58,679 | 676 lines (decompressed) | 849bf24734b87b49989af8a2dcdb447ba27d0abdf6d0ea4b85103caa311c6e95 | committed |
| docs/program-id-sources/docs.raydium.io_products_launchlab.body.gz | 55,555 | 675 lines (decompressed) | c76e08acaf9ca8c9cd24775f269cb5623dd2081611a9a0a4aacaa609836a235c | committed |
| docs/program-id-sources/docs.raydium.io_reference_program-addresses.body.gz | 79,973 | 799 lines (decompressed) | ca5f0e001be08b0f055d2221153e5853c907b2b66de3a710ee13c503ce6f39cf | committed |
| docs/program-id-sources/index.csv | 9,759 | 44 rows + header | b4de11a1afc35a9752e37939c600466a97e29489a734d4fa32bfdabe4f3227cf | committed |
| docs/program-id-sources/jito-block-engine-getTipAccounts.json | 637 | 1 JSON document | 35da1ad09d12193225dcda5f0123d57880c5ae7f9efc7acc316c114d3eea1aaa | committed |
| docs/program-id-sources/lite-api.jup.ag_swap_v1_program-id-to-label.body.gz | 4,331 | 0 lines (decompressed) | 5fdbb12e4d83b19b8fb431f3d9262ed49659a27252cbb24150524000c338b2e6 | committed |
| docs/program-id-sources/pond.dflow.net_introduction.body.gz | 38,125 | 610 lines (decompressed) | 8a918d29158054620beb30aa67c1b5fdf1cb040e8219f29660b024dece311605 | committed |
| docs/program-id-sources/raw.githubusercontent.com_CKS-Systems_manifest_main_README.md.body.gz | 4,547 | 157 lines (decompressed) | e1bc2077a55f74fda9cfaa73f1b557ef72e4fea7605d7854d281f9f7a2c5df99 | committed |
| docs/program-id-sources/raw.githubusercontent.com_Ellipsis-Labs_phoenix-v1_master_README.md.body.gz | 745 | 43 lines (decompressed) | 91524c50c98aabad74b4b5fc8110996a67ea7d43b564ce132207a1246b617478 | committed |
| docs/program-id-sources/raw.githubusercontent.com_Ellipsis-Labs_phoenix-v1_master_src_lib.rs.body.gz | 2,867 | 372 lines (decompressed) | b7e8cc5083089c1398c136f6577c5c8a9612f1e5cf4513a9779fabbe23f23d16 | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_damm-v1-sdk_main_README.md.body.gz | 201 | 12 lines (decompressed) | 95c80bdf7e93bedb32a8745290384cb3933c338418eb6da17538fce6da35c090 | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_damm-v1-sdk_main_programs_dynamic-amm_src_lib.rs.body.gz | 1,706 | 229 lines (decompressed) | f9dc414f9cc6cd6fe81b8183057589cf81c0e7abe13737ce50c6ce62a31fdf4a | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_damm-v2_main_README.md.body.gz | 1,771 | 97 lines (decompressed) | ce1e22e9e97e7979b71095a0ff004aadd7ae65bafa8b844c9edca1b669283dcc | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_damm-v2_main_programs_cp-amm_src_lib.rs.body.gz | 2,082 | 347 lines (decompressed) | c539a63a6fd6a835ea96d14db0be6496dd99d0873cb1a759055101bf5876b1fa | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_dlmm-sdk_main_README.md.body.gz | 149 | 15 lines (decompressed) | 82293770d3f6a8ecd3e64b8acdb1ca022a839370b83e697cf0628f1b506142f3 | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_dynamic-amm-sdk_main_README.md.body.gz | 201 | 12 lines (decompressed) | 92ed767579200064f6d6203fa86aca83fdff283d9f785bb5ecb04941fc1c646b | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_dynamic-amm-sdk_main_programs_dynamic-amm_src_lib.rs.body.gz | 1,706 | 229 lines (decompressed) | 149ffc2575e19d4a6ea666827f2eace5fb837fc3f3ff049a33f5e8ba68b27729 | committed |
| docs/program-id-sources/raw.githubusercontent.com_MeteoraAg_dynamic-bonding-curve_main_programs_dynamic-bonding-curve_src_lib.rs.body.gz | 1,851 | 315 lines (decompressed) | 990258d942f63083b5774fc493b008a4af64be997c56424bb72cc2d882eb7fc2 | committed |
| docs/program-id-sources/raw.githubusercontent.com_igneous-labs_S_master_README.md.body.gz | 1,639 | 127 lines (decompressed) | a260a2a026e426ec6be0a8311ade9455b108f5e885914d7852d4f7e743e2cac0 | committed |
| docs/program-id-sources/raw.githubusercontent.com_jito-labs_jito-docs_main_docs_source_lowlatencytxnsend.md.body.gz | 13,083 | 702 lines (decompressed) | af7f19cff149a4d52b9077872f22d4ae8a33c506e579b3236ecf09b306f27cd3 | committed |
| docs/program-id-sources/raw.githubusercontent.com_jup-ag_instruction-parser_main_README.md.body.gz | 845 | 45 lines (decompressed) | 81e062dbbd742368bc8a14fbfd992ab77c88079b350b5a4837a0fc68dca42d1b | committed |
| docs/program-id-sources/raw.githubusercontent.com_jup-ag_jupiter-cpi_main_README.md.body.gz | 358 | 26 lines (decompressed) | 905bc2c63bf0ac8466787f961a766bff486e72401ccb3486cf56c58560f04dcb | committed |
| docs/program-id-sources/raw.githubusercontent.com_jup-ag_jupiter-cpi_main_src_lib.rs.body.gz | 1,299 | 126 lines (decompressed) | 997b028ccb8aa2def27fdd0b1f6320a5a9bc30da98a161415bb42f5a9ba9a4e6 | committed |
| docs/program-id-sources/raw.githubusercontent.com_okxlabs_Web3-DEX-Router-Solana-V1_main_README.md.body.gz | 3,079 | 324 lines (decompressed) | 1b3c4fec6f453f6f844c1b079d7f65949fd9634afbfeefd4ae82e3999036b94a | committed |
| docs/program-id-sources/raw.githubusercontent.com_openbook-dex_openbook-v2_master_README.md.body.gz | 1,300 | 113 lines (decompressed) | 5d8fb31732110cfb3d17e3e7e10ca00fd430a07e0cc227bb4c698d48329f7c4b | committed |
| docs/program-id-sources/raw.githubusercontent.com_openbook-dex_openbook-v2_master_programs_openbook-v2_src_lib.rs.body.gz | 4,872 | 714 lines (decompressed) | 328b702c1892aca49dcb51880abac1901a87904b5f3b37d4f1a03b9c0aff4631 | committed |
| docs/program-id-sources/raw.githubusercontent.com_openbook-dex_program_master_README.md.body.gz | 1,072 | 69 lines (decompressed) | a291a1b6d701801f72bd017df5e6c383f7580ddc66699bab5d8386cb6c87d477 | committed |
| docs/program-id-sources/raw.githubusercontent.com_orca-so_whirlpools_main_README.md.body.gz | 2,736 | 114 lines (decompressed) | 578989b75d9c04bd6a43c13f4b1d25ec669b31168b74e86dc4b5cd84dfcaa155 | committed |
| docs/program-id-sources/raw.githubusercontent.com_orca-so_whirlpools_main_programs_whirlpool_src_lib.rs.body.gz | 8,286 | 1,337 lines (decompressed) | ff4ffc9c3fb69eaf2f2fcb5b12d47c1afa2ac0529b19febcf01b99a49ef3abdf | committed |
| docs/program-id-sources/raw.githubusercontent.com_pump-fun_pump-public-docs_main_README.md.body.gz | 2,889 | 136 lines (decompressed) | 11b36765c0b5cb35d30b898e2d1500f861aee8c1f74f03ab80d0cf1309582f4a | committed |
| docs/program-id-sources/raw.githubusercontent.com_pump-fun_pump-public-docs_main_idl_pump.json.body.gz | 17,112 | 12,386 lines (decompressed) | a1719e310c2473b03ff2616c8a4ea81d141ac90641cd4398d52556705f6f5df3 | committed |
| docs/program-id-sources/raw.githubusercontent.com_pump-fun_pump-public-docs_main_idl_pump_amm.json.body.gz | 10,579 | 7,680 lines (decompressed) | 3a3e4b62c4d5619c07baaee65f5de36738866ba29ea644e8cfb3254c92076f2d | committed |
| docs/program-id-sources/raw.githubusercontent.com_saber-hq_stable-swap_master_README.md.body.gz | 1,084 | 56 lines (decompressed) | 65cd11c88fdf75ade610783f854a19cdefafbfa8c27d6745d4823fb5eea9aec2 | committed |
| docs/program-id-sources/unpkg.com_jup-ag_dca-sdk_3.0.1_dist_index.js.body.gz | 7,844 | 2,227 lines (decompressed) | 64f319c5f82c35be46f556efe2402b0f1f28dea1bdf75cd9236e76169d4f08d1 | committed |
| docs/program-id-sources/unpkg.com_jup-ag_limit-order-sdk_0.1.10_dist_index.js.body.gz | 4,322 | 1,301 lines (decompressed) | 38c464ed0558e31fac1096a24a0a165ca25a1b2dcff5324262f42055f9e44709 | committed |
| docs/program-id-sources/unpkg.com_lifinity_sdk-v2_2.0.3_lib_network.js.body.gz | 256 | 8 lines (decompressed) | a757b6c00d1936fbf28a5a2867d5773972649582ba27d6897bbb775b3c317ba8 | committed |
| docs/program-id-sources/unpkg.com_lifinity_sdk_0.2.25_lib_network.js.body.gz | 252 | 8 lines (decompressed) | a951899bbc0403245a1a3a0cbfa1967c0c2981638ea2bcbb821d48b4d7fbd31a | committed |
| docs/raw.githubusercontent.com_jito-foundation_jito-solana_master_README.md.raw.gz | 2,047 | 131 lines (decompressed) | 9021022a5b607c48541b2a30db8ae500ad9bfc7519ffa88c6728689af98d53da | committed |
| docs/raw.githubusercontent.com_jito-foundation_jito-solana_master_README.md.txt | 4,605 | 137 lines | b8847e00a7ddfe1d98f0682dcdcec9e50ee9a837e2d1f2b73d373968b1c91868 | committed |
| docs/raw.githubusercontent.com_jito-labs_jito-docs_main_docs_source_lowlatencytxnsend.md.raw.gz | 13,083 | 702 lines (decompressed) | 47f4b3bffe5a883d029f7fef4d39f53cbc89a26275cf3c8fe89c920ecbd6a00c | committed |
| docs/raw.githubusercontent.com_jito-labs_jito-docs_main_docs_source_lowlatencytxnsend.md.txt | 36,395 | 708 lines | 345c8c5bacbcae1a31dd7b6274305153aaeb18beff4838123d7a6c96d146e64a | committed |
| docs/raw.githubusercontent.com_jito-labs_mev-protos_master_json_rpc_http.md.raw.gz | 4,396 | 245 lines (decompressed) | 4dbcb66817f9091d991a054179875c79a7e3d60d20d83214c0d058429602c8cf | committed |
| docs/raw.githubusercontent.com_jito-labs_mev-protos_master_json_rpc_http.md.txt | 10,395 | 251 lines | a6b78df51ff7844b13713289a840f1ed3395140272b11f6f863ece2b38859120 | committed |
| docs/solana.com_developers_guides_advanced_how-to-use-priority-fees.html.gz | 223,343 | 19 lines (decompressed) | 2608e54b66e0cf178fdc7aedd4228fb35a8de8dc11d0d82955bd5890d275cf4e | committed |
| docs/solana.com_developers_guides_advanced_how-to-use-priority-fees.txt | 2,666 | 200 lines | 702614d71849d1c5f3847af501e4864ce686c912f841ef960e87f2c5d902911c | committed |
| docs/solana.com_docs_core_fees.html.gz | 223,184 | 18 lines (decompressed) | fd6aa235d59f1c531728bd8f1c47ff5067def04facf6d2ed998cb261c186f3f5 | committed |
| docs/solana.com_docs_core_fees.md.raw.gz | 1,103 | 52 lines (decompressed) | 7ce4b79af7e10179cb4721be63d17719be4f4718bdb97b29fbec6d920c7b5df0 | committed |
| docs/solana.com_docs_core_fees.md.txt | 3,290 | 58 lines | 5a0b967a8c00bdc13a4ea9c089e97ee8fe9d5d05a94bea6d6ac853d838759c18 | committed |
| docs/solana.com_docs_core_fees.txt | 2,628 | 198 lines | d4cf5f016f7a10699c04b882b79d5dc498c4ca4186c8b1384ee83605238af707 | committed |
| docs/solana.com_docs_core_fees_compute-budget.md.raw.gz | 3,850 | 224 lines (decompressed) | f27f40eadf676339d4111ae137a0fee78dbc79ee8a8037c726ac584ab1f92785 | committed |
| docs/solana.com_docs_core_fees_compute-budget.md.txt | 15,927 | 230 lines | 9266337fe3ba1a0bcb5899573c7fd9e82261d34a7c6fa0d733f948d8313bad33 | committed |
| docs/solana.com_docs_core_fees_fee-structure.md.raw.gz | 4,005 | 323 lines (decompressed) | def134fa560f24843bf7cd5b9d53129d7a32d7e759b8133c20dd1e7e9538249b | committed |
| docs/solana.com_docs_core_fees_fee-structure.md.txt | 13,644 | 329 lines | a5768760ba41c55e22bfcbee944d5f847f37ff87ca9686f7f88852071555fde7 | committed |
| docs/solana.com_docs_core_transactions_transaction-pipeline.md.raw.gz | 6,043 | 302 lines (decompressed) | 1fabd4bbfac46ae80207f208d833b0d69ba5ea9cdac394c5c99af2726e7d67ac | committed |
| docs/solana.com_docs_core_transactions_transaction-pipeline.md.txt | 25,580 | 308 lines | 42d10ffd4ebbbff35300f0af0ebd41883f355893b0f1cf74f60f803ea550080c | committed |
| docs/solana.com_docs_core_transactions_versioned-transactions.md.raw.gz | 5,673 | 324 lines (decompressed) | fe87e07a2e07bef6b4d3ae7fed00e524242379894ff70bf6c00746499257f55d | committed |
| docs/solana.com_docs_core_transactions_versioned-transactions.md.txt | 18,187 | 330 lines | ad7edabf48bf4f2748e5abda46ed924ec2d48e7a314658050564edf3c74814d7 | committed |
| docs/solana.com_docs_defi_mev-protection.md.raw.gz | 4,451 | 322 lines (decompressed) | 9f1d25c2b5b3094756fefa56c0a1a94c7ac81d84bac395742c4a83a4acaaf2ae | committed |
| docs/solana.com_docs_defi_mev-protection.md.txt | 11,613 | 328 lines | 7bfe0624ac50562d3a10cc7815a484f001d859a51439691811b6362e81ccb814 | committed |
| docs/solana.com_docs_defi_stake-weighted-qos.md.raw.gz | 3,081 | 158 lines (decompressed) | c006e2d2f693b1a1d1b2af3fedd253dc111e659935b6fa264d9e4a482320d765 | committed |
| docs/solana.com_docs_defi_stake-weighted-qos.md.txt | 8,119 | 164 lines | c7e5bf35529857730bc91c0d615f876df0c573d930673f0f06f8564413303d2d | committed |
| docs/solana.com_docs_references_clusters.html.gz | 226,233 | 138 lines (decompressed) | 19b557bc3382acb7ee3a7edee090e678bcd7eeb01978eefed58ba166b1ac8d2a | committed |
| docs/solana.com_docs_references_clusters.md.raw.gz | 2,302 | 172 lines (decompressed) | d81b3256e7f62e645bfecfac16e00907539ff3ce63fa7c0184725dbda4b89dc8 | committed |
| docs/solana.com_docs_references_clusters.md.txt | 6,976 | 178 lines | 314cd4e6b97cff6afb39a71af593b227631753ce036f71f38f4bd123f6c68d12 | committed |
| docs/solana.com_docs_references_clusters.txt | 7,524 | 344 lines | 53be6868ea749096be9e5b36c8ffc03bb7bd3fad58c0150aa72176489260f4bc | committed |
| docs/solana.com_docs_rpc_http_getblock.html.gz | 256,169 | 85 lines (decompressed) | a86511ef2ae63f929c8114beef81fa6e0d41816c04562e1b204bc355fcbfc3bd | committed |
| docs/solana.com_docs_rpc_http_getblock.md.raw.gz | 5,602 | 471 lines (decompressed) | 3f9c43973d55be812c26f7279b0d5ccd8eed266f8e853411bb7fcfccd90fb18f | committed |
| docs/solana.com_docs_rpc_http_getblock.md.txt | 22,012 | 477 lines | c7b99d6f3391b2a4bbe4fe4965166390ade3feb2cfb634a58ab159e560016833 | committed |
| docs/solana.com_docs_rpc_http_getblock.txt | 5,685 | 425 lines | 27f156d46968a001ff49fae1cfffacab4dcb397a8302ef2cb74dc8e1341ec54b | committed |
| docs/solana.com_docs_rpc_http_getslotleaders.md.raw.gz | 1,154 | 130 lines (decompressed) | 78455b06b2559d995978a268477d435b3de36a52fe32906b9ca8ff2f72670c13 | committed |
| docs/solana.com_docs_rpc_http_getslotleaders.md.txt | 3,112 | 136 lines | 2ebabc5ebb145a536d42b420b67ea6dc430a83260b04a955be840ae4b9c2123d | committed |
| docs/www.anza.xyz_blog_introducing-the-central-scheduler-an-optional-feature-of-agave-v1-18.html.gz | 37,867 | 432 lines (decompressed) | f8476f62f88bf423c5a508a4622d8ed7b2e131892c9bc07f7cc1139d4c73949e | committed |
| docs/www.anza.xyz_blog_introducing-the-central-scheduler-an-optional-feature-of-agave-v1-18.txt | 7,036 | 156 lines | 468fc39ef179d3955b8402c6e36f0d4d6f0d1e18bd9471272870d7cdd79e095a | committed |
| docs/www.anza.xyz_blog_transaction-landing-on-tpu.html.gz | 51,501 | 432 lines (decompressed) | 948ef0fa6f4a932bc47ae5a318aacaef3d677144b44b9296463390de4ded3c72 | committed |
| docs/www.anza.xyz_blog_transaction-landing-on-tpu.txt | 21,362 | 282 lines | 795f4adf230fa734d834494bc9ea8997f3ec7261d33d207811feb993ca3ee4bc | committed |
| jito-tip-accounts.csv | 3,289 | 8 rows + header | 016ef4b3e0654dd1ff62a6954b41e0a769b8e2bf0ab6c9e4c124c380994c9874 | committed |
| jito-tip-transfers.csv.gz | 1,926,012 | 21,509 rows + header | 8f05db1e6f4a97417952fb99e302735ac3321ee8114bdbf7d5f55485f6d3995f | committed |
| prices-defillama-historical.jsonl.gz | 126,910 | 72 JSON lines | 71537ab7b1c208758d4b203a76b0876c63e33e9e6972100da9a3bb8bf1e0bf96 | committed |
| program-invocations.csv.gz | 34,836 | 897 rows + header | ed87d25961a887b2e1453bc7fc1603c011b5b9de804d154736afff1db5fa9246 | committed |
| slots.csv.gz | 42,722 | 600 rows + header | 45778c796097945f4954fadb27734f227089884ef17198a6361b272b94d58d00 | committed |
| snapshots/defillama__api.llama.fi_overview_aggregators_solana.json.gz | 101,661 | 1 JSON document (gzip) | 20b088a99b05a98c47738bf42ff270254dfb421948c7518f247231bdd05b9b6b | committed |
| snapshots/defillama__api.llama.fi_overview_dexs_excludeTotalDataChart_true_excludeTotalDataChartBreakdown_true.json.gz | 355,460 | 1 JSON document (gzip) | 735745a34bf1d2a39ad9f2e92afeaf2306228d92f058f4fd7c25f939a9a7e8f0 | committed |
| snapshots/defillama__api.llama.fi_overview_dexs_solana.json.gz | 275,128 | 1 JSON document (gzip) | 8cf9cf2cef3272e54faee6d918d1da87680fa3d42cfc94300d88e30407ccde45 | committed |
| snapshots/defillama__api.llama.fi_overview_dexs_solana_excludeTotalDataChart_false_excludeTotalDataChartBreakdown_false_dataType_dailyVolume.json.gz | 277,648 | 1 JSON document (gzip) | 246ae68678a972c5467355ae1068b76ffb0057bde492cee4fb4de7db1860fabc | committed |
| snapshots/defillama__api.llama.fi_overview_fees_solana_excludeTotalDataChart_false_excludeTotalDataChartBreakdown_true.json.gz | 122,188 | 1 JSON document (gzip) | 72ad3b8e17eed2de726358f0ea7269b258ee9517ca0ff54bed70da184b65de8d | committed |
| snapshots/defillama__api.llama.fi_summary_fees_jito-mev-tips_dataType_dailyFees.json.gz | 22,232 | 1 JSON document (gzip) | 0ffa730797f38bf3d492d3a48268306c5a311299d7a8f60f0ad2dcdb59361671 | committed |
| snapshots/defillama__api.llama.fi_summary_fees_jito_dataType_dailyFees.json.gz | 33,090 | 1 JSON document (gzip) | 05b5b2b47fca73b88167f71e79ff8822c049215761301aa623031ee66f99b137 | committed |
| snapshots/index.csv | 3,892 | 22 rows + header | 125956f6a2606e8c787f077bc0eee0cdb7fcfd0f9ba31f1fe6ea3adcf9c197ea | committed |
| snapshots/jito__bundles.jito.wtf_api_v1_bundles_recent_limit_1000_sort_Time_asc_false.json.gz | 171,110 | 1 JSON document (gzip) | ea2b5cef27504829b56687bd3fc8eb47aa1a27f360b73adc7f5379bc85c54387 | committed |
| snapshots/jito__bundles.jito.wtf_api_v1_bundles_recent_limit_1000_sort_Tip_asc_false_timeframe_Day.json.gz | 202,595 | 1 JSON document (gzip) | 2b4a95256f344c3bfae4e931b9616e15f52f24eb15ce65de82b479f8bfeba222 | committed |
| snapshots/jito__bundles.jito.wtf_api_v1_bundles_recent_limit_1000_sort_Tip_asc_false_timeframe_Week.json.gz | 209,837 | 1 JSON document (gzip) | 097c4480e39450839496f47ce52a34b9e34eaed012eeb7309207bab0e08897a4 | committed |
| snapshots/jito__bundles.jito.wtf_api_v1_bundles_tip_floor.json.gz | 157 | 1 JSON document (gzip) | 835d334d1283dff0df0c7a168a49b3a947b812d35ce2a7dd39d0b0b073c8bf7d | committed |
| snapshots/jito__kobe.mainnet.jito.network_api_v1_daily_mev_rewards.json.gz | 45,707 | 1 JSON document (gzip) | b9f25cd06925677702140401fb34bd716f40463428ebc9386deee44628b714a4 | committed |
| snapshots/jito__kobe.mainnet.jito.network_api_v1_jitosol_validators.json.gz | 61,040 | 1 JSON document (gzip) | 4aaa7428486b364811cd620c76dbc2570ff37324905aafe70096d36857bae57f | committed |
| snapshots/jito__kobe.mainnet.jito.network_api_v1_mev_rewards.json.gz | 137 | 1 JSON document (gzip) | 7773eb1d629fa5ec44b9fd1622345a07292e097cfc6d50348310eecadc133875 | committed |
| snapshots/jito__kobe.mainnet.jito.network_api_v1_stake_pool_stats.json.gz | 571 | 1 JSON document (gzip) | c61942042db1bbba10a793045b7b38cdfb98b80d9f2259296e535e6d16bce8f9 | committed |
| snapshots/jito__kobe.mainnet.jito.network_api_v1_validators.json.gz | 55,013 | 1 JSON document (gzip) | 15108f206bbbccf65f6f6693e321cd388c5d2e9c0379f0942053857dd58b1ce0 | committed |
| snapshots/rpc__getClusterNodes.json.gz | 258,763 | 1 JSON document (gzip) | 923b652224aeaa64a63030a1e25d7d0b18ef96be86a5cf41703abd0c43eefbbe | committed |
| snapshots/rpc__getEpochInfo.json.gz | 159 | 1 JSON document (gzip) | d9f6b5bba856afacb78a75a8188ed956955d80210411dc2b1c4ba23284fdfc29 | committed |
| snapshots/rpc__getRecentPerformanceSamples.json.gz | 976 | 1 JSON document (gzip) | b6f46db8536dbc487db3439931c769dacbf35d245a5bf7914c56b3da76a5ee2e | committed |
| snapshots/rpc__getRecentPrioritizationFees.json.gz | 459 | 1 JSON document (gzip) | 710d5c14ecd5f2da4b79437c415af0837b88770f4cf9c070b8c75b3cf2d5fc5e | committed |
| snapshots/rpc__getVersion.json.gz | 98 | 1 JSON document (gzip) | 7ed966ba4dbdbaf6f97cb58e234050704cbc449e1961892e428d86b0ee32654d | committed |
| snapshots/rpc__getVoteAccounts.json.gz | 95,959 | 1 JSON document (gzip) | 060e0c2227c96179bde080ac3b9d9f2ee693d5169349e060ff79767942aaeed5 | committed |
| tip-floor.jsonl | 28,061 | 61 JSON lines | daaa24ccd8aadc244940faa83f65ad72419ce51d840e8e0151f4e3430ff51004 | committed |
| token-mints-seen.csv.gz | 97,803 | 2,853 rows + header | b340c18ace80728c9f9732cb46b69d0ce9cade9b0bd15e9a3551666520b0597b | committed |
| txs-nonvote-001.csv.gz | 43,686,070 | 348,614 rows + header | 3aeafbc031f1293cd7e29f6aa76defd62f4591ac95e42e5d6c3cfef54ee63d1b | committed |
| data/raw-slots/ (slot-452084865.json.gz ... slot-452085464.json.gz) | 564,677,263 (total) | 600 files, 1 JSON document each (all parse); gzip -t ok 600/600 | per file in local-only-inventory.tsv | local-only |
| data/jito-bundles-by-slot.parts/ (452084865.json ... 452085464.json) | 8,577,414 (total) | 600 files, 1 JSON document each (all parse) | per file in local-only-inventory.tsv | local-only |
| data/prices.parts/ (00000.json ... 00071.json) | 396,869 (total) | 72 files, 1 JSON document each (all parse) | per file in local-only-inventory.tsv | local-only |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
| local-only-inventory.tsv | 183,332 | 1,272 rows + header (TSV written 2026-10-01: per-file inventory of the local-only directories above) | 1116d92b6bfe5a755a4f2ed49fb1fa91e71a13c79b7c47db48099e06df6be21a | committed |
