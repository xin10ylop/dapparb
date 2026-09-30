# 06-other-chains-onchain/solana: Solana mainnet consecutive-slot sample, Jito data, ordering docs

STATUS: IN PROGRESS. Slot sample, Jito bundles, prices, programs, snapshots and docs are complete (sentinel `SOL_SAMPLE.DONE`, written 2026-09-30T21:45:55Z). The Jito tip-floor poller (`collect/jito_tip_floor.py`, PID 2255) is still running until it has 60 successful polls; it writes the sentinel `SOL_JITO_TIPFLOOR.DONE` (or `.FAILED`). The row count for `tip-floor.jsonl` is filled in once that sentinel exists.

Collected 2026-09-30 (UTC). Raw material only. Nothing in this directory analyzes, estimates or concludes anything. Columns marked "derived" are deterministic, lossless decodings of the raw data, and the raw data is stored next to them.

## Question lines this directory serves (mapping only)

IDs are the same as in `../MANIFEST-evm.md`.

| File / group | Question lines |
|---|---|
| slots.csv.gz, txs-nonvote-*.csv.gz, dex-txs-*.jsonl.gz, data/raw-slots/, program-invocations.csv.gz, jito-tip-transfers.csv.gz, data/jito-bundles-by-slot.jsonl.gz, token-mints-seen.csv.gz, prices-defillama-historical.jsonl.gz | Q-OTHERCHAINS ("Solana ... not measured"), Q-GAPS, Q-COVERAGE, Q-V4LAUNCH (Solana analogues: launch programs pump.fun bonding curve, PumpSwap, Meteora DBC, Raydium LaunchLab; per-transaction priority fees and Jito tips paid), Q-SMALLPOOLS (per-transaction pre/post token balances of the pool vault accounts each tx touched), Q-STUDIES (failed-transaction fees: `err`, `fee` for every non-vote tx) |
| dex-programs.csv, jito-tip-accounts.csv, docs/program-id-sources/ | definitions used by all of the above |
| tip-floor.jsonl, snapshots/jito__*, data/jito-bundles-by-slot.jsonl.gz | Q-OTHERCHAINS, Q-V4LAUNCH (tip auction levels), Q-BSCORDER (Solana comparison: bundle auction / block-engine ordering) |
| docs/ (Jito, BAM, Anza, solana.com) | Q-BSCORDER (Solana comparison: leader-based ordering, Jito block engine auction, BAM, priority fees, stake-weighted QoS), Q-OTHERCHAINS |
| snapshots/defillama__*, defillama-dexs.json, snapshots/jito__kobe*daily_mev_rewards* | Q-STUDIES (chain-wide totals: DEX volume, fees, Jito MEV tips by day), Q-OTHERCHAINS |
| docs/literature/ | Q-STUDIES (published Solana MEV/arbitrage/bot measurements), Q-OTHERCHAINS |
| snapshots/rpc__getVoteAccounts, rpc__getClusterNodes, jito__kobe*validators* | Q-BSCORDER (which leaders run Jito-Solana / BAM, keyed by identity, which joins to `slots.csv.gz.leader`) |

Q-V4BASE and Q-OLDV2 are not served here: they concern Base and EVM V2 pairs only.

## Window (pinned)

* Pinned at 2026-09-30T21:28:22.95Z to the `finalized` slot at pin time (`getSlot`, api.mainnet-beta.solana.com): **slots 452084865 to 452085464 (600 consecutive slots)**. Source: `collect/state/pin.json`.
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
  * The first run's `state/fetch-stats.json` was overwritten by a no-op re-run and then removed. From now on, re-runs append to `state/fetch-stats.jsonl`.
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

The full verbatim transaction (message, instructions with data, `innerInstructions`, `logMessages`, all balances, `loadedAddresses`, etc.) of every non-vote tx is in `data/raw-slots/`.

### data/raw-slots/slot-<slot>.json.gz (600 files, 540 MB total, each well below 90 MB)
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

### tip-floor.jsonl (IN PROGRESS: 60 successful polls targeted, one every 60 s from 2026-09-30T21:30:07Z)
One line per poll:

`{poll_no, fetched_at_utc, url, http_status, body}`

`body` is the https://bundles.jito.wtf/api/v1/bundles/tip_floor response verbatim: `[{time, landed_tips_25th/50th/75th/95th/99th_percentile, ema_landed_tips_50th_percentile}]`, with values in SOL. The row count is filled in on completion (sentinel SOL_JITO_TIPFLOOR). Polling started 2 min after the sample window ended (21:28:13Z) and runs for about 60 min (last poll expected around 22:29Z).

### data/jito-bundles-by-slot.jsonl.gz (600 lines)
One line per slot:

`{slot, url, fetched_at_utc, http_status, body}`

`body` is verbatim: a list of `{bundleId, slot, validator, tippers[], landedTipLamports, landedCu, blockIndex, timestamp, txSignatures[]}`, or `{"error":"Bundle not found"}` with HTTP 404. `data/jito-bundles-by-slot.parts/` is the per-slot checkpoint and holds the same content.

### data/ (other)
* `slot-leaders.json`: getSlotLeaders, verbatim.
* `get-blocks.json`: getBlocks, verbatim.
* `integrity-crosscheck.json`: the cross-endpoint check.
* `build-summary.json`: part files and row counts.
* `prices.parts/`: the prices checkpoint.

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
* **Literature** is limited to the arXiv API query results and the 6 documents listed. It is not a systematic literature search. The arXiv API returned few results for these queries.
* **Other chains:** BSC and the other EVM chains are in sibling directories. No other non-EVM chain (for example Sui, Aptos or TON) was collected.
