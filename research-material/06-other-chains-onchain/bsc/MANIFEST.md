# BSC (BNB Smart Chain) on-chain census, builder material, ordering/MEV docs, DEX landscape

Status: COMPLETE WITH GAPS (finalized 2026-10-01). Gaps: (a) 5 of the 28 swap topics in `census/swap-topics.csv` were not observed in the window and are unverified on BSC; (b) 11 of 44 validator MEV RPC entries did not answer `mev_params`; (c) 5 of the 92 entries in `docs/index.csv` have no page content (blocksmith-docs and blocksmith-send-bundle: network error; uniswap-v4-deployments and uniswap-v3-bnb-deployments: HTTP 429; pancakeswap-infinity-hooks-md: HTTP 404; substitutes are listed in 'Coverage limits and gaps' item 10); (d) `census/raw/` (40 files, 434,972,682 bytes) is git-ignored and stays local-only, so it is not in the repository. Sentinel BSC_CENSUS.DONE exists (the sentinel file is git-ignored; its text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:38Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): COMPLETE (all collectors finished; no process left running). Sentinel: `/home/user/dapparb/research-material/.sentinels/BSC_CENSUS.DONE` (written 2026-09-30T21:08:09Z).

Collected: 2026-09-30, 20:53Z to 21:41Z, by a collection-only agent. This directory contains data and verbatim documents only. It has no analysis and no conclusions.

## Question lines and codes used below

Qn is question line n of the 8 question lines quoted verbatim in `../MANIFEST.md`.

| code | question line (verbatim from the user, shortened) |
|---|---|
| Q1 | "Uniswap V4 on Base. This is the biggest gap. ... only had 20 V4 pools ..." |
| Q2 | "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs ..." |
| Q3 | "Pools under 0.1 ETH of liquidity ..." |
| Q4 | "Other chains, live. The live search ran only on Base ... BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured." |
| Q5 | "V4 launches are the one place a bigger number could appear ... The RSR trade ... the winner kept 3% and paid the rest as priority fee." |
| Q6 | "BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents." |
| Q7 | "Chain-wide studies already count every pool. On Arbitrum ... On Base, 4,365 bots ..." |
| Q8 | "So the search went far beyond selected pairs ... full Uniswap V4 coverage on Base ..." |

## Question lines served (mapping only)

Rewritten 2026-10-01 as a mapping only (the collector's summary sentence above the table was replaced; the file table below is the collector's, with local-only status added).

| Line | Files in this directory |
|---|---|
| 1 (Q1) | `dex/dex-address-excerpts.txt`; docs with Q1 in `docs/index.csv` column question_lines (`<id>.txt` + `raw/<id>.*`): pancakeswap-infinity-addresses, pancakeswap-infinity-overview, pancakeswap-infinity-hooks-md, uniswap-v4-deployments, uniswap-sdk-core-addresses-ts; `census/swap-topics.csv` and `census/candidates-00*.jsonl.gz` (Uniswap V4 PoolManager and PancakeSwap Infinity swap logs) |
| 2 (Q2) | none |
| 3 (Q3) | none |
| 4 (Q4) | `census/window.json`, `census/blocks.csv.gz`, `census/txs-001.csv.gz`, `census/reverted-001.csv.gz`, `census/candidates-001.jsonl.gz`, `census/candidates-002.jsonl.gz`, `census/swap-topics.csv`, `census/topic0-inventory.csv.gz`, `census/topic0-signatures.csv.gz`, `census/postprocess-summary.json`, `census/raw/` (local-only), `dex/defillama-overview-dexs-bsc.json.gz`, `dex/defillama-overview-dexs-bsc.meta.json`, `dex/dex-address-excerpts.txt`; the 36 docs with Q4 in `docs/index.csv` |
| 5 (Q5) | `census/txs-001.csv.gz`, `census/candidates-001.jsonl.gz`, `census/candidates-002.jsonl.gz`, `census/swap-topics.csv`, `census/raw/` (local-only), `builder/builder-material-001.jsonl.gz`, `dex/dex-address-excerpts.txt`; the 18 docs with Q5 in `docs/index.csv` |
| 6 (Q6) | `census/window.json`, `census/blocks.csv.gz`, `census/txs-001.csv.gz`, `census/reverted-001.csv.gz`, `census/candidates-001.jsonl.gz`, `census/candidates-002.jsonl.gz`, `census/raw/` (local-only), `builder/builder-material-001.jsonl.gz`, `builder/block-mev-info.csv.gz`, `builder/block-mev-info-gaps.csv`, `builders.csv`, `validators-onchain.csv`, `validator-mev-rpc-probe.jsonl.gz`, `docs/excerpts.txt`; the 68 docs with Q6 in `docs/index.csv` |
| 7 (Q7) | `census/txs-001.csv.gz`, `census/reverted-001.csv.gz`, `census/candidates-001.jsonl.gz`, `census/candidates-002.jsonl.gz`, `census/swap-topics.csv`, `census/topic0-inventory.csv.gz`, `census/topic0-signatures.csv.gz`, `census/raw/` (local-only) |
| 8 (Q8) | none |

File to question-line map (collector's table):

| path | serves |
|---|---|
| `census/window.json` | Q4, Q6 (window definition and measured block interval) |
| `census/blocks.csv.gz` | Q4, Q6 |
| `census/txs-001.csv.gz` | Q4, Q5, Q6, Q7 |
| `census/reverted-001.csv.gz` | Q4, Q6, Q7 |
| `census/candidates-001.jsonl.gz`, `census/candidates-002.jsonl.gz` | Q4, Q5, Q6, Q7 |
| `census/swap-topics.csv` | Q4, Q5, Q7 (definition of criterion A) |
| `census/topic0-inventory.csv.gz`, `census/topic0-signatures.csv.gz` | Q4, Q7 (lets the swap-topic list be audited or extended) |
| `census/postprocess-summary.json` | metadata for all census files |
| `census/raw/chunk-*.jsonl.gz` (40 files; local-only, git-ignored) | all census questions (lossless source of every derived census file) |
| `builder/builder-material-001.jsonl.gz` | Q6, Q5 |
| `builder/block-mev-info.csv.gz` | Q6 |
| `builders.csv` | Q6 |
| `validators-onchain.csv` | Q6 |
| `validator-mev-rpc-probe.jsonl.gz` | Q6 (validators' published MEV/builder settings) |
| `docs/*.txt`, `docs/raw/*`, `docs/index.csv`, `docs/excerpts.txt` | per `question_lines` column of `docs/index.csv` (Q4/Q5/Q6, some Q1) |
| `dex/defillama-overview-dexs-bsc.json.gz` (+ `.meta.json`) | Q4 |
| `dex/dex-address-excerpts.txt` | Q4, Q1, Q5 |

## Window (census and builder material)

- Chain: BSC mainnet, chain id 56.
- Block range: **124968311 to 124976310 inclusive (8,000 blocks), contiguous, no missing blocks.**
- Chain time: from 2026-09-30T19:56:37.750Z (block 124968311, milliTimestamp 1790798197750) to 2026-09-30T20:56:37.650Z (block 124976310, milliTimestamp 1790801797650).
- Rule: end = min(head over 3 dataseed endpoints) − 30 at pin time 2026-09-30T20:56:55Z. Start = smallest block with milliTimestamp ≥ milliTimestamp(end) − 3,600,000 ms. See `census/window.json`.
- Block interval measured from headers before choosing the range: 450.0 to 450.4 ms per block over spans of 100 to 10,000 blocks. Over the window it is 450.04 ms. The header samples are in `window.json` (`header_samples`, `derived_interval_ms_over_*`). Every block's `milli_timestamp` is in `blocks.csv.gz`.
- Endpoints: bsc-dataseed.bnbchain.org, bsc-dataseed1-4.bnbchain.org, bsc-dataseed1.defibit.io, bsc-dataseed1.ninicoin.io. The collector allows at most 2-3 requests in flight per endpoint, and requests are spread round-robin. bsc-rpc.publicnode.com was configured only as a fallback and served no request. It refuses receipts older than about 9,000 blocks with "Archive requests require a personal token".
- Checks per block: receipts count equals tx count, receipt i hash equals tx i hash, every receipt's blockHash equals the block hash, and every receipt's blockNumber equals the block. All 8,000 blocks passed on the first pass. `gaps.csv` and `gaps-unrecovered.csv` were not created because there were no gaps.

## Reproduce

```
export PATH=/root/.foundry/bin:$PATH REQUESTS_CA_BUNDLE=/root/.ccr/ca-bundle.crt SSL_CERT_FILE=/root/.ccr/ca-bundle.crt
cd /home/user/dapparb/research-material/06-other-chains-onchain/bsc/collect
# census pipeline (pin window -> raw download -> wait for POSTPROCESS.READY -> postprocess -> sentinel).
# census/window.json exists, so the SAME window is reused. Delete it to pin a new "last 60 minutes" window.
# POSTPROCESS.READY exists already (it was created by hand after swap-topics.csv had been verified).
setsid nohup ./run_census.sh > run_census.log 2>&1 < /dev/null &
python3 swap_topics.py            # swap-topics.csv: cast keccak + first matching log in census/raw
python3 postprocess.py            # deterministic; rerun after editing census/swap-topics.csv
python3 lookup_topic_signatures.py  # topic0 -> text signature lookup (api.openchain.xyz)
python3 block_mev_info.py         # eth_getBlockMevInfo for every window block
# repos needed by fetch_docs.py / builders.py / validator_mev_params.py (shallow, public):
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/bnb-chain/bsc-mev-info /home/user/bnb-chain/bsc-mev-info            # commit c6ceebbd4ae3c9b33ce139af5005a73857ae67e3
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/bnb-chain/good-will-alliance /home/user/bnb-chain/good-will-alliance  # commit de8501ff6e7fe9a9b9047859c746894733ec178e
cd /home/user/bnb-chain && GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --filter=blob:none --sparse https://github.com/bnb-chain/bnb-chain.github.io && git -C bnb-chain.github.io sparse-checkout set docs/bnb-smart-chain   # commit 001ecbc1a8e42bcc97c6578b32c237a12784fb2f
GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/four-meme-community/fourmeme-docs /home/user/four-meme-community/fourmeme-docs  # commit 5f7f589b042e4e3b41c2c214d0fe3a81b36725a9
cd /home/user/dapparb/research-material/06-other-chains-onchain/bsc/collect
python3 fetch_docs.py             # all docs; or: python3 fetch_docs.py --only id1,id2 (merges into docs/index.csv)
python3 builders.py               # builders.csv (needs the clones + docs/*.txt)
python3 validators_onchain.py     # validators-onchain.csv (state at head-5 at run time)
python3 validator_mev_params.py   # validator-mev-rpc-probe.jsonl.gz
python3 fetch_dex.py              # dex/*
python3 excerpts.py               # docs/excerpts.txt
```
Logs: `collect/*.log`. Smoke tests before launch used 40 blocks for the downloader and 200 blocks for the postprocessor. Their output went to the scratchpad and was checked by hand.
Re-downloading the same window depends on node history. On 2026-09-30 the dataseed nodes served receipts at least 100,000 blocks back, which is about 12.5 h. The raw chunks are kept here, so the derived files never need to be downloaded again.

Correction 2026-10-01: `census/raw/` is git-ignored (`.gitignore` rule `research-material/**/census/raw/`). The raw chunks exist only on the collection machine and are not in the repository; every file derived from them (census tables, builder material) is committed. How to regenerate the raw chunks is described in 'Verified inventory (2026-10-01)'. `collect/POSTPROCESS.READY` contains the time it was created (2026-09-30T21:06:46Z).

## Schemas

All integers are base-10. Hashes and addresses are lowercase 0x hex, except where a column or object is marked verbatim, which keeps the node's JSON as-is. Empty string means null or absent.

### census/window.json
Pin metadata. Fields: `start_block`, `end_block`, `block_count`, `*_milliTimestamp`, `*_utc`, `heads_seen`, `safety_blocks_behind_head`, `header_samples` (number, timestamp, milliTimestamp, hash, endpoint), and derived ms-per-block values.

### census/blocks.csv.gz: 8,000 rows, one per block
`block_number`; `timestamp` (s); `base_fee_per_gas` (wei; header baseFeePerGas); `gas_used`; `gas_limit`; `tx_count`; `miner` (header coinbase = validator consensus address); `extra_data` (raw hex, verbatim); `milli_timestamp` (BSC header field milliTimestamp, ms); `block_hash`; `parent_hash`; `mix_hash` (verbatim; BEP-520 states the millisecond part is stored in MixDigest); `requests_hash` (verbatim header requestsHash); `size` (bytes); `difficulty`; `nonce`; `blob_gas_used`; `excess_blob_gas`; `parent_beacon_block_root`; `withdrawals_root`; `state_root`; `transactions_root`; `receipts_root`. All columns are raw header fields.

### census/txs-001.csv.gz: 502,872 rows, one per transaction, including BSC system transactions
`block_number`, `tx_index`, `tx_hash`, `from`, `to` (empty for contract creation), `status` (1/0), `gas_used`, `effective_gas_price` (wei; receipt), `type`, `nonce`, `value` (wei), `gas_price` (tx object gasPrice, wei), `max_fee_per_gas`, `max_priority_fee_per_gas` (empty for legacy tx), `gas_limit` (tx gas), `input_selector` (derived: first 4 bytes of input, or the whole input if shorter), `input_len_bytes` (derived), `logs_count` (derived), `contract_address`, `cumulative_gas_used`. The first 8 columns follow the shared census definition. The others come from the tx object or receipt as stated.

### census/reverted-001.csv.gz: 13,864 rows, every status-0 transaction
`block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, logs_count` (shared definition), plus `gas_price, max_priority_fee_per_gas, gas_limit, input_selector (derived), input_len_bytes (derived), nonce, type`.

### census/candidates-00N.jsonl.gz: 59,990 lines in 2 parts (48,094 + 11,896)
One JSON object per transaction meeting:
- **A**: at least 2 logs whose topics[0] is in `census/swap-topics.csv` (28 signatures). **32,557 rows.**
- **B**: not A, at least 3 ERC-20 Transfer logs (topic0 `0xddf252ad...b3ef` with exactly 3 topics, so 4-topic ERC-721 Transfers are excluded) emitted by at least 2 distinct contracts. **27,433 rows.**

No other filter was applied: status 0 and 1 are both included, and there is no value or address filter.

Fields: `block_number`, `tx_index`, `tx_hash`, `from`, `to`, `status` (int), `gas_used` (string), `effective_gas_price` (string, wei), `criterion` ("A"/"B"), `derived_swap_topic_log_count`, `derived_erc20_transfer_log_count`, `derived_erc20_transfer_distinct_emitters`. `receipt_other_fields` holds every receipt field except `logs`, verbatim hex JSON: type, from, to, status, cumulativeGasUsed, logsBloom, transactionHash, contractAddress, gasUsed, blockHash, blockNumber, transactionIndex, effectiveGasPrice. BSC receipts have no L1-fee fields. `tx` holds the verbatim tx object without `input`, blockHash and blockNumber, plus derived `input_selector` and `input_len_bytes`; the full input is in `census/raw` (local-only). `logs` holds ALL logs of the tx verbatim: address, topics, data, blockNumber, transactionHash, transactionIndex, blockHash, blockTimestamp, logIndex, removed.

### census/swap-topics.csv: 28 rows
`topic0` (computed with `cast keccak`), `signature`, `protocol`, `source_url` (event definition source), `verified_example_tx`, `example_emitter`, `example_block`, `verification_note`.
- **Verified:** 23 topics. For each, `verified_example_tx` is the first log in the window with that topic0.
- **Not observed in the window, so unverified on BSC (5):**
  - Balancer V3 Swap `0x0874b2d5...`
  - Curve tricrypto-ng TokenExchange `0x143f1f8e...`
  - Curve TokenExchangeUnderlying `0xd013ca23...`
  - DODO V1 SellBaseToken `0xd8648b6a...`
  - Trader Joe LB v2.1 Swap `0xad7d6f97...`

Groups: baseline signatures from the shared definition; BSC local DEXes (PancakeSwap Infinity CL and Bin, Algebra Integral, DODO V1/V2, Wombat, WOOFi, Maverick V1/V2, iZiSwap, Fluid); and launchpad bonding-curve trade events (Four.meme TokenPurchase/TokenSale, Flap TokenBought/TokenSold).

Notes on individual rows:
- The UniV3-type row also matches Algebra V1 and KyberSwap Elastic, which share the same type list.
- The PancakeSwap StableSwap row shares a topic0 with the Curve uint256 TokenExchange variant.
- The Balancer V2 row's BSC emitter is not the canonical Vault address, and the protocol column says so.

### census/topic0-inventory.csv.gz: 5,207 rows (derived index over all 3,139,184 logs in the window)
`topic0` (`(no-topics)` for anonymous logs), `log_count`, `tx_count`, `distinct_emitters`, `example_block`, `example_tx_hash`, `example_emitter` (first occurrence), `in_swap_topics_csv`, `swap_topics_csv_protocols`.

### census/topic0-signatures.csv.gz: 5,206 rows
`topic0`, `signatures` (all names returned by api.openchain.xyz, '|'-joined, verbatim), `has_verified_contract`, `lookup_source`, `looked_up_at_utc`. 2,709 topics have at least one name, and 0 lookups failed. This is a hash-to-text lookup from a third-party database only.

### census/postprocess-summary.json
Row counts per file and part, missing blocks (none), and the swap-topic set used.

### census/raw/chunk-<first>-<last>.jsonl.gz: 40 files, 200 blocks each, 415 MB (local-only: git-ignored, not in the repository)
One line per block: `{"block": <eth_getBlockByNumber(n,true) verbatim>, "receipts": <eth_getBlockReceipts(n) verbatim>, "src": {"block": endpoint, "receipts": endpoint}}`. This is the lossless source of every census and builder-material file.

### builder/builder-material-001.jsonl.gz: 8,000 lines, one per block
`block_number`, `block_hash`, `timestamp`, `milli_timestamp`, `miner`, `extra_data` (raw hex), `mix_hash`, `requests_hash`, `tx_count`, `gas_used`, `first_txs[]` (first 5 txs) and `last_txs[]` (last 5 txs). The two lists overlap when tx_count < 10.

Each list element holds:
- the verbatim tx object without input: hash, type, from, to, nonce, value, gas, gasPrice, maxFeePerGas and maxPriorityFeePerGas if present, chainId, v/r/s, transactionIndex;
- `position` (0-based index in the block);
- `input_selector` and `input_len_bytes` (derived);
- `receipt_status`, `receipt_gasUsed`, `receipt_effectiveGasPrice` and `receipt_logs_count` from the receipt.

### builder/block-mev-info.csv.gz: 8,000 rows (0 gaps; `block-mev-info-gaps.csv` is header-only)
Result of the bsc-client JSON-RPC method `eth_getBlockMevInfo(block)` from the dataseed endpoints. This is the method used by bnb-chain/bsc `cmd/jsutils/getchainstatus.js` GetMevStatus; see `docs/bsc-getchainstatus-js.txt` and `docs/excerpts.txt`.

Columns: `block_number`, `block_hash`, `miner`, `version`, `builder` (empty if absent), `census_block_hash`, `hash_matches_census` (derived; all 8,000 = 1), `raw_result_json` (verbatim), `endpoint`.

### builders.csv: 144 rows
Columns: `builder_name`, `builder_org_derived` (the TOML section-name prefix, or the comment group in builderMap), `address`, `address_lower`, `rpc`, `website`, `source`, `source_url` (git blob URL at the commit, or doc URL), `git_commit`, `evidence_verbatim` (the exact TOML section, doc lines, or JS line).

Sources:
- (a) bnb-chain/good-will-alliance `mev-info/bsc-mainnet/builder-list.toml` at de8501ff (2025-12-10): 33 rows.
- (b) bnb-chain/bsc-mev-info `mainnet/builder-list.toml` at c6ceebbd (2026-09-17). The file header states it is deprecated and points to (a): 47 rows.
- (c) builder docs that state their own EOA: 48 Club Builder Control EOA and BlockRazor Builder EOA, 2 rows.
- (d) `builderMap` in bnb-chain/bsc `cmd/jsutils/getchainstatus.js` (master at fetch time): 50 BSC-mainnet rows and 12 Chapel-testnet rows.

Addresses repeat across sources on purpose; each row is one piece of evidence.

### validators-onchain.csv: 56 validators (some `details` fields contain newlines; parse as CSV)
State at block 124979813, queried about 26 minutes after the window end, from system contracts StakeHub `0x...2002` and ValidatorSet `0x...1000`.

Columns: `operator_address`, `consensus_address` (this is the `miner` value in headers), `credit_contract`, `moniker`, `identity`, `website`, `details`, `in_validatorset_getValidators`, `in_validatorset_getMiningValidators`, `queried_block`, `stakehub_total_length`.

### validator-mev-rpc-probe.jsonl.gz: 176 lines (44 validator entries × 4 methods)
Every validator MEV RPC listed in bsc-mev-info `mainnet/validator-list.toml` was called with `eth_chainId`, `web3_clientVersion`, `mev_running` and `mev_params`. Responses are stored verbatim in `response_text`; errors are in `error`.

`mev_params` returned a result for 33 of 44 entries. `mev_params` returns ValidatorCommission, BidSimulationLeftOver, NoInterruptLeftOver, MaxBidsPerBuilder, GasCeil, GasPrice, BuilderFeeCeil, BidBlockEnabled and Version. Probed 2026-09-30T21:32:35Z to 21:36:13Z.

### docs/
- `index.csv`: 92 rows. Columns: `id, url, title, publisher, date_stated` (from page metadata, the BEP "created" line, or the repo HEAD commit date for git files; empty if none found), `fetched_at, http_status, question_lines, text_file, raw_file, raw_bytes, raw_sha256, note`.
- `<id>.txt`: a header (URL, final URL, fetched_at, HTTP status, sha256) followed by the full page text. HTML is converted with html2text, which strips markup and does not summarize. Markdown, TOML, Go and JS sources are kept verbatim.
- `raw/`: the untouched response bodies. HTML is stored gzipped.
- `excerpts.txt`: exact consecutive-line excerpts of the passages below, each with source file, URL and line range:
  - hard-fork activation times from bsc `params/config.go`: Lorentz 2025-04-29 05:05 UTC, Maxwell 2025-06-30 02:30, Fermi 2026-01-14 02:30, Osaka/Mendel 2026-04-28 02:30, Pasteur 2026-08-25 02:30, as written in that file;
  - BEP summaries;
  - the builder payment and auction rules;
  - the getchainstatus.js builder-attribution function.

Content covered:
- BNB Chain MEV/PBS docs: rendered pages plus the markdown source at bnb-chain.github.io commit 001ecbc1.
- BEPs: 67, 126, 322, 341, 520, 524, 563, 564, 590, 619, 648, 658, 673, 675 (draft), 718 (draft), and the README index.
- bsc CHANGELOG, `params/config.go`, `getchainstatus.js`, and the bsc-builder README.
- BNB Chain blog posts on MEV, the Good Will Alliance, Maxwell, Fermi, and Osaka/Mendel.
- Builder docs: 48 Club / Puissant (4 pages), BlockRazor (3), bloXroute BSC (2), NodeReal (2), Jetbldr and Flashblock home pages.
- Builder and validator registries.
- PancakeSwap v2, v3 and Infinity address pages.
- Uniswap sdk-core `addresses.ts` (BNB v2/v3/v4 addresses, including v4PoolManagerAddress).
- Four.meme and Flap launchpad docs.

### dex/
- `defillama-overview-dexs-bsc.json.gz`: raw body of https://api.llama.fi/overview/dexs/bsc, gzip only, fetched at the time in `.meta.json`. It contains 181 protocols and top-level keys totalDataChart, totalDataChartBreakdown, breakdown24h/30d, totals, changes and protocols. A second copy from the earlier fetch is at `docs/raw/defillama-overview-dexs-bsc.json.gz`.
- `dex-address-excerpts.txt`: verbatim line ranges covering:
  - PancakeSwap v2 factory and router;
  - PancakeSwap v3 core, periphery and smart router;
  - PancakeSwap Infinity Vault, CLPoolManager, BinPoolManager and periphery;
  - Uniswap sdk-core BNB block, including v4PoolManagerAddress 0x28e2ea09...9e9df;
  - Four.meme TokenManager addresses;
  - Flap BNB Chain contracts.

## Coverage limits and gaps

1. **One window only.** The census covers a single contiguous 60-minute window (8,000 blocks, 2026-09-30 19:56:37Z to 20:56:37Z). No other hour, day or longer period was collected. Time-of-day and day-to-day variation are not sampled.
2. **Swap-topic list is finite.** `swap-topics.csv` has 28 pool-level or launchpad signatures, 5 of them unverified on BSC (listed above). The following event types were deliberately NOT included in criterion A:
   - aggregator and router events, for example KyberSwap `Swapped`, OKX/LiFi/1inch/ParaSwap router events;
   - PMM/RFQ and "prop-AMM" events seen in the window, for example `TesseraTrade`, `PropAMMTrade`, `ElfomoTrade`, `Exchange(address,address,address,uint256,uint256)` on 0x8f10b468..., Bebop, 1inch `OrderFilledRFQ`;
   - prediction-market `OrderFilled`/`OrdersMatched`;
   - unattributed swap-like pool events, for example `Swap(address,address,bool,int128,int128,int16,uint104)` and `Swap(address,address,uint256,uint256,uint256)`.

   Transactions that use these venues appear only through criterion B, or through criterion A if they also emit 2 or more listed swap logs. `topic0-inventory.csv.gz` and `topic0-signatures.csv.gz` hold every topic0 in the window, so criterion A can be widened by editing `swap-topics.csv` and rerunning `postprocess.py`. That rerun is fast and needs no network.
3. **Criterion B has blind spots.** It counts only 3-topic ERC-20 Transfer logs. Native BNB movements emit no logs and are not counted, and neither are WBNB Deposit/Withdrawal events or ERC-1155 transfers.
4. **Calldata is not in candidates or builder material.** Only the selector and length are there; full calldata is in `census/raw` (local-only: git-ignored, not in the repository). No `debug_trace*` or internal-call traces were collected, and public dataseed nodes do not serve them.
5. **No mempool or private-flow data.** Nothing was collected on bundle submissions, losing bids, the builder auction, or transactions that never landed. Only on-chain outcomes are present: inclusion order, gas prices, and transfers to builder addresses, which are visible in candidate logs, builder material and raw data. `eth_getBlockMevInfo` returns only the winning builder per block.
6. **No BSC live engine run.** The Q4 "live search" was not rerun on BSC. This directory is block-level only. Solana and the other L2s are not covered here.
7. **No BSC chain-wide multi-month study (literature) was collected here.** No BSC counterpart to the Q7 Arbitrum and Base figures is included.
8. **The validator snapshot is after the window.** `validators-onchain.csv` is pinned at block 124979813, not inside the window. The validator set can change at epoch boundaries.
9. **11 of 44 validator MEV RPCs did not answer `mev_params`.** For 48Club (proxy error), 9 Legend endpoints (TLS error) and nozti ("validator hostname not found"), errors are recorded verbatim. The probe ran once at a single time.
10. **Docs not retrieved:**
    - Blocksmith docs (docs.blocksmith.org): DNS failure and proxy CONNECT 502. Blocksmith appears only in the deprecated registry, plus the getchainstatus.js entry "txboost(blocksmith)".
    - Uniswap docs pages (v4 deployments, v3 BNB deployments): HTTP 429 on retries. Uniswap `sdks/sdk-core/src/addresses.ts` was used instead.
    - PancakeSwap Infinity hooks page: HTTP 404.
    - Four.meme GitBook "protocol-integration" URL: it returned a different page (OpenFour integration). The four-meme-community/fourmeme-docs repo and the `.md` exports were used instead.
    - Flap `/developers/trade-tokens`: HTTP 404. The GitBook `.md` exports were used instead.
11. **HTML pages are converted text.** They were converted with html2text; navigation text remains. The raw HTML is kept.
12. **Registry and doc versions are as of fetch time.** GWA builder list at commit de8501ff (2025-12-10); bsc-mev-info at c6ceebbd (2026-09-17); BNB docs at 001ecbc1 (2026-09-20); bsc master and BEPs master at fetch time (2026-09-30 about 21:15Z).
13. **Some header fields are recorded but not explained.** `requests_hash` and `mix_hash` are recorded verbatim. No document collected here explains `requestsHash` on BSC. BEP-520 explains the millisecond part of MixDigest.
14. **Endpoint limits met during collection.** publicnode refuses receipts older than about 9k blocks and does not implement `eth_getBlockMevInfo`. bsc.drpc.org returned HTTP 429. The dataseed endpoints return "limit exceeded" for `eth_getLogs` over 1,000 or more blocks. As a result, the 5 unobserved swap topics could not be verified outside the window.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory, including the local-only raw chunks (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line; `builders.csv` and `validators-onchain.csv` have quoted fields that contain newlines, so their physical line counts are larger than their row counts); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 272 files (232 committed, 40 local-only). All 92 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. Largest committed file: census/candidates-001.jsonl.gz (83,906,821 bytes); no committed file exceeds 90 MB.

Counts stated in this manifest compared with the verified counts (all equal, no corrections needed): census/blocks.csv.gz 8,000; census/txs-001.csv.gz 502,872; census/reverted-001.csv.gz 13,864; census/candidates-001/002.jsonl.gz 48,094 + 11,896 = 59,990 (criterion A 26,076 + 6,481 = 32,557; criterion B 22,018 + 5,415 = 27,433); census/swap-topics.csv 28 (23 with verified_example_tx, 5 without); census/topic0-inventory.csv.gz 5,207 (sum of log_count 3,139,184); census/topic0-signatures.csv.gz 5,206 (2,709 with at least one signature); builder/builder-material-001.jsonl.gz 8,000; builder/block-mev-info.csv.gz 8,000 (hash_matches_census = 1 in all rows; block-mev-info-gaps.csv header only); builders.csv 144 (sources 33 + 47 + 2 + 50 + 12); validators-onchain.csv 56 (queried_block 124979813); validator-mev-rpc-probe.jsonl.gz 176 (33 mev_params responses with a result); docs/index.csv 92; dex/defillama-overview-dexs-bsc.json.gz 181 protocols; census/raw/ 40 files with 200 JSON lines each (8,000 blocks).

Local-only files and how to regenerate them: `census/raw/chunk-<first>-<last>.jsonl.gz` (40 files, 434,972,682 bytes; `.gitignore` rule `research-material/**/census/raw/`). They are the verbatim `eth_getBlockByNumber(n,true)` + `eth_getBlockReceipts(n)` responses for the committed window. To regenerate: `cd bsc/collect && python3 download.py` (reads the committed `../census/window.json`, writes `../census/raw/chunk-*.jsonl.gz`; resumable). The endpoints in `collect/rpc.py` (DEFAULT_ENDPOINTS) are public dataseed nodes that on 2026-09-30 served about 12.5 h of receipt history, so a later re-download needs an endpoint with history for blocks 124968311-124976310 (edit DEFAULT_ENDPOINTS). A re-download records its own endpoint in each line's `src` field, so file checksums can differ from the table below even when block and receipt content is the same. `postprocess.py` and `run_census.sh` rewrite the committed derived files and are not needed to restore the raw chunks.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| builder/block-mev-info-gaps.csv | 19 | 0 rows + header | 83b9ab6f2efbc0ce647dc3034c30523b6e93da75e2e0c106c112778be6458467 | committed |
| builder/block-mev-info.csv.gz | 543,427 | 8,000 rows + header | f914ac0359f1bcfe0bc1c3ee8a312d5b1bb19cbd997c87f02df8a02ec92cd473 | committed |
| builder/builder-material-001.jsonl.gz | 17,574,846 | 8,000 JSON lines | 87dc10b2bfecf4fc3aa967ee378512498677d3a26f710a2297bd8f855d2f30e5 | committed |
| builders.csv | 74,740 | 144 rows + header (514 physical lines; quoted fields contain newlines) | 3e546ecd9471d5160e22fe0494d907ff81467ab0e234e01ec256f1f1587e6ebd | committed |
| census/blocks.csv.gz | 3,267,055 | 8,000 rows + header | 91b9a22e83e49fcf513364adb2f7f7e189aec6f36452b09c41d91884be3c4553 | committed |
| census/candidates-001.jsonl.gz | 83,906,821 | 48,094 JSON lines (criterion A 26,076, B 22,018) | bf067a43ad5f443456ae92dc8467530ce2709b4bac425674c46ae703d7bf8f39 | committed |
| census/candidates-002.jsonl.gz | 19,764,948 | 11,896 JSON lines (criterion A 6,481, B 5,415) | c56301f15fb1d3865e4a8b3c46d4bd0556951694c6aa1d9f8faed40efe0ba480 | committed |
| census/postprocess-summary.json | 4,818 | 1 JSON document | 9201294201fced4aba04a4c558136375e7a61b9ee037d59adc2d60913a7ae8fd | committed |
| census/raw/chunk-124968311-124968510.jsonl.gz | 11,089,163 | 200 JSON lines | 8680a2b91f21038483bbb21661e75617d88b700c561931d2f77f7bc7c5c54e4f | local-only |
| census/raw/chunk-124968511-124968710.jsonl.gz | 10,850,564 | 200 JSON lines | a75638ed8bc1e2a98edfd050527a0f28ddf51280798763339f1a5d10d54e18b7 | local-only |
| census/raw/chunk-124968711-124968910.jsonl.gz | 13,385,622 | 200 JSON lines | a8c9323257d5de6e1c21ae7539c24f0ed916e4bac4648772db07eaf1a762d881 | local-only |
| census/raw/chunk-124968911-124969110.jsonl.gz | 12,701,798 | 200 JSON lines | 88e64e0c6f244624d8692d48235a7d45d01eb431608c2925b0d8c36c50ef26d8 | local-only |
| census/raw/chunk-124969111-124969310.jsonl.gz | 11,299,299 | 200 JSON lines | 372385058b1f31ec26f0a0822c4005f0c38c697b76215961f4d14ead8fa500df | local-only |
| census/raw/chunk-124969311-124969510.jsonl.gz | 13,466,600 | 200 JSON lines | db99d71411676f4e7c9464d0bb2b0a524268ce69663308d77e3a91b9d35b22e6 | local-only |
| census/raw/chunk-124969511-124969710.jsonl.gz | 12,710,452 | 200 JSON lines | b254ccb7c3da993d9621ca40dd6e48f95975d45842e7ed6015cda0408991606e | local-only |
| census/raw/chunk-124969711-124969910.jsonl.gz | 11,037,447 | 200 JSON lines | c93be2af2f5bf69cea6ae80437a43f6a4dfa33b6e1b62f040106c131e0da285d | local-only |
| census/raw/chunk-124969911-124970110.jsonl.gz | 10,626,065 | 200 JSON lines | b6caccd36d0a6e9f3423914fef55eac2eecfa8c0388c4ddb246db3a4bde00ca8 | local-only |
| census/raw/chunk-124970111-124970310.jsonl.gz | 10,242,771 | 200 JSON lines | 376e80af6af66be7f311e7d04ae099e52f6fe1e7a39b5cea696439c020d2b43b | local-only |
| census/raw/chunk-124970311-124970510.jsonl.gz | 9,562,035 | 200 JSON lines | 838e099395f7e33f01389576cc8f8155fc928964276fba0f023a7cd03ea77939 | local-only |
| census/raw/chunk-124970511-124970710.jsonl.gz | 10,189,712 | 200 JSON lines | a39bffdc058199d9b108de8095329a06a35c04829c3f0c8d1fc83cab5cb831f8 | local-only |
| census/raw/chunk-124970711-124970910.jsonl.gz | 10,191,746 | 200 JSON lines | 9b0f31344ca6152db9d77830d1c5fb773da2b4797fb0b01789f8327f64bc31cf | local-only |
| census/raw/chunk-124970911-124971110.jsonl.gz | 10,598,778 | 200 JSON lines | ef9a83ad42ae998a30238a7522d030f795b0eb581d1a998e071d49974759f30f | local-only |
| census/raw/chunk-124971111-124971310.jsonl.gz | 9,555,205 | 200 JSON lines | eff788092c574ba2b85410b1ce5a519882c64419341adcec2502aa166a8f01e0 | local-only |
| census/raw/chunk-124971311-124971510.jsonl.gz | 10,463,937 | 200 JSON lines | e8bfb9e823c70b49b6af0314a2381e43b45a987e97d715fe862b035fa736e895 | local-only |
| census/raw/chunk-124971511-124971710.jsonl.gz | 11,253,173 | 200 JSON lines | bfc54ab1b9df13b3ea3a77ef56b8264672001fa2e2040b60aa1af6eae81d3f85 | local-only |
| census/raw/chunk-124971711-124971910.jsonl.gz | 11,159,057 | 200 JSON lines | f0421b21ec488be0dfaac6078b888dc3017fc18c1d324d1952e4173ae5e69a92 | local-only |
| census/raw/chunk-124971911-124972110.jsonl.gz | 9,867,249 | 200 JSON lines | f7c3fb08458eb2d4533de760799fa0377b43d15b5e4e0cd3263f4bd2c94b5a13 | local-only |
| census/raw/chunk-124972111-124972310.jsonl.gz | 10,694,887 | 200 JSON lines | 89c94a52cc587ca5533bed80bf55fc0bfae3201afc04ff84eec0f9ef24fbf398 | local-only |
| census/raw/chunk-124972311-124972510.jsonl.gz | 11,281,509 | 200 JSON lines | c782cfed05172923947788b5723fa9e8f58258ee75caa392be7c736e3df617dd | local-only |
| census/raw/chunk-124972511-124972710.jsonl.gz | 10,637,984 | 200 JSON lines | f40050b3310c6991e19638009fe325878a052efbdaf341a5121de5f9562498b1 | local-only |
| census/raw/chunk-124972711-124972910.jsonl.gz | 11,503,706 | 200 JSON lines | 6c31bab9db07c52413bd48f7dd484d6868ae7aea0d4b210167ea5c8f15b4a1f4 | local-only |
| census/raw/chunk-124972911-124973110.jsonl.gz | 10,258,255 | 200 JSON lines | 42281f617aca352ba50da2fc3ff3cc142a8aafe17e4b5baa77cfeb3b89fcc15c | local-only |
| census/raw/chunk-124973111-124973310.jsonl.gz | 10,216,961 | 200 JSON lines | d3d779fe81db96166170652f5d91cbe80ef632aa2e7fc4a0d6d9bf21b04fbcba | local-only |
| census/raw/chunk-124973311-124973510.jsonl.gz | 10,349,664 | 200 JSON lines | 4c0988370241b6eca76196d6a645f86818f1783e49cc5769d07473b8454fa326 | local-only |
| census/raw/chunk-124973511-124973710.jsonl.gz | 10,508,958 | 200 JSON lines | c429b98b2ca5391029dd8a827e6cfae4b6fdd8f57df18227f58582266b726378 | local-only |
| census/raw/chunk-124973711-124973910.jsonl.gz | 11,476,936 | 200 JSON lines | e870b7532f639177c4a9ea457c96c4dfc2afa0bf78c9993f7c1678e87c46f26e | local-only |
| census/raw/chunk-124973911-124974110.jsonl.gz | 10,978,024 | 200 JSON lines | 0df45c471fb8df987e27484cea194b7bb03d141e3a17869d999e9ff4dcea0bd8 | local-only |
| census/raw/chunk-124974111-124974310.jsonl.gz | 12,070,265 | 200 JSON lines | 0ddae496b21fe75c3238214c3e25d62b1c3c616d8071f1722356ac86be0c3817 | local-only |
| census/raw/chunk-124974311-124974510.jsonl.gz | 10,942,272 | 200 JSON lines | 8e13843cf4c9e484766174e6c661581da3d8370f3218458343985b831d67bde4 | local-only |
| census/raw/chunk-124974511-124974710.jsonl.gz | 9,920,515 | 200 JSON lines | 7c8760795957c2833e1af8a2159449b8f20855afb73749b49acd28261d70a511 | local-only |
| census/raw/chunk-124974711-124974910.jsonl.gz | 10,537,275 | 200 JSON lines | 212c9f870aebe2fabc0571cfb99e1996bad5085c72079a4b38c0f1eeaea9d861 | local-only |
| census/raw/chunk-124974911-124975110.jsonl.gz | 13,112,436 | 200 JSON lines | c94b9b9debc56651b8870e92764ede7e4b693bb84cffc868054ff0e9eadb72eb | local-only |
| census/raw/chunk-124975111-124975310.jsonl.gz | 11,272,706 | 200 JSON lines | 883a99d95897c570f7dc6dfe722d0490186756a14b28af34e88a61c3e656ad82 | local-only |
| census/raw/chunk-124975311-124975510.jsonl.gz | 10,545,706 | 200 JSON lines | 78e0e49f472806f242e3c3ec07d2d86667a117b662f2ec81b6450f8ae571bbdc | local-only |
| census/raw/chunk-124975511-124975710.jsonl.gz | 9,717,011 | 200 JSON lines | 8917116c58aec441b5ccbd0f2ed8fc3648fa2b12561da5c8ef40f79ccc352e78 | local-only |
| census/raw/chunk-124975711-124975910.jsonl.gz | 9,233,117 | 200 JSON lines | f0f889603cb5dcb4aa1db1a4d8e1130765c5606134b80cbc0a2b69740efc62f2 | local-only |
| census/raw/chunk-124975911-124976110.jsonl.gz | 9,671,328 | 200 JSON lines | eb09ed5a3a3f310cb8dcd2304c2c1c203970d098839910dfa045ce83b9bfdb69 | local-only |
| census/raw/chunk-124976111-124976310.jsonl.gz | 9,792,494 | 200 JSON lines | 1701b8b0ae1e9c9c00aec3d717d264548dc8f58614290f7a4efb1a54711d1190 | local-only |
| census/reverted-001.csv.gz | 1,006,022 | 13,864 rows + header | 6d727775a6b8869f7a5f130a6ced6838344f6afee438e12f50a92ec002c95d68 | committed |
| census/swap-topics.csv | 13,157 | 28 rows + header | 913b8fda11c26983338d98a5500b146bd439486f207dce61ba0e890fcc80eaa5 | committed |
| census/topic0-inventory.csv.gz | 398,630 | 5,207 rows + header | 09f92fa91f98430a0566b8bbf32c7c97521e43cb517e139976b4bfd23324d220 | committed |
| census/topic0-signatures.csv.gz | 204,959 | 5,206 rows + header | 9515fb417e8413ce86eb15f7ad8e7483952c429dbfab48c5adffeb023386f022 | committed |
| census/txs-001.csv.gz | 48,453,589 | 502,872 rows + header | d8597ab1c2ae47bf674aea22e8e9f8d99e9e45eefa68afd76cecd70955d102c4 | committed |
| census/window.json | 3,207 | 1 JSON document | 6989d0c147280dcdc8cc1281e5131005f761e05bef04c53ea7d031742ea1ebe9 | committed |
| collect/POSTPROCESS.READY | 21 | 1 line | 014c4f3982f6ec92e223985ff0d9e6d7ea85500abf0c1dc388fe3be7fcc24f7e | committed |
| collect/block_mev_info.log | 457 | 1 line | c9f22a2f98bf08d51524101cb3d767e485de39a81949bb3cea212756eb6ee1f7 | committed |
| collect/block_mev_info.py | 3,176 | 73 lines | 7a586e62e0ac75c5f8e5b1e6b9c1367af04146b965e558210514c2fe63a8c301 | committed |
| collect/builders.py | 6,016 | 124 lines | 9ecd79ceb1611521a204c42a805f45880fc2849fecdc91233c41726a927d68fd | committed |
| collect/download.py | 6,726 | 158 lines | b954d4fe783e97f794c337ee2e4e01aadc594c78ff5b79bf377f802ee8ff31c5 | committed |
| collect/excerpts.py | 3,342 | 60 lines | 8d26dd1e7350c9eaba540efa9b5628ba0b7c8fb56325e57e2ef732b296e3534d | committed |
| collect/fetch_dex.log | 34 | 2 lines | 4a8e8d58e9999a8feefdf3fdae351a2b62674bfe8104f48cb6f8fac479fee758 | committed |
| collect/fetch_dex.py | 5,055 | 99 lines | 86ffad7d1656a99e5fcf8bb68c93c1e338acd30a580e0c7070a92bf554a877b3 | committed |
| collect/fetch_docs.log | 1,834 | 63 lines | 52b0c9538933c5ce799c946e9cfeda333b5f89d89431113a5dbb8ac81a4e96b3 | committed |
| collect/fetch_docs.py | 22,116 | 322 lines | 49c4bb23a9de1d282cfc06ca9d67f9a24ca07c3392d42d8e1ccfb198e11dea36 | committed |
| collect/fetch_docs_extra.log | 348 | 11 lines | 5488679252719543aa4192754dda0bc21b5ab5a97faad3e5cc1e3fbc2d7c8ea5 | committed |
| collect/fetch_docs_extra2.log | 95 | 3 lines | 333c5a66fa3f415126e5c00d172c21cfc9c04c29b5e7caec743a4ecc4582c598 | committed |
| collect/fetch_docs_extra3.log | 46 | 2 lines | 93c03fddd1022620f2e18a458922709e369be7743de768cf1f592a8362e186d3 | committed |
| collect/lookup_topic_signatures.log | 37 | 1 line | 94371b6339b5b2139c98438e70fae2d59e7d829b87f6a60e4a73f5092fd580e9 | committed |
| collect/lookup_topic_signatures.py | 3,444 | 81 lines | 03729e6da3ab6338561f03366c9dac22c17c274c127ab0163d8770715c0530ba | committed |
| collect/pin_window.py | 3,635 | 85 lines | 2cb9e6317cd4c669e55a31dfe830b6be5526b645c75ae451a088ebda16407578 | committed |
| collect/postprocess.py | 15,393 | 318 lines | 7925fe786c53838de451683cf82c332c29beff2967fac0cf4a250593588490b4 | committed |
| collect/rpc.py | 5,724 | 142 lines | 5a89052630ee297922e8711e0869fc143d44d80e8e93248655c9436dfac744f2 | committed |
| collect/run_census.log | 26,646 | 236 lines | 574e4483addd174e7066538a2e04bafd4edda07d1501d7820e9fa192a031a2dc | committed |
| collect/run_census.sh | 1,470 | 25 lines | 07bef2cbc8199f7dfaca81a35d2df988cdb0cd26a905b9d4d2d2ecacc11d5438 | committed |
| collect/swap_topics.log | 3,068 | 28 lines | ecf257f48eb9793c194be81b4d59f4134b3e5f63a49e03fc8e61a615171359e7 | committed |
| collect/swap_topics.py | 9,917 | 146 lines | 7e3f8331f50313ec9b5fc2d3c33f1d4f14701c57ebd41b790fab3ef46d74ca56 | committed |
| collect/validator_mev_params.log | 12 | 1 line | 52cd20e009ab4be3b7e31c0f1b8ac76206c75c801ab9f18c5edf2dadf6182449 | committed |
| collect/validator_mev_params.py | 3,117 | 69 lines | 24f8c67a519644c18a5155a07e9742de81f0a95e5099ac462bb9fd8e9f984add | committed |
| collect/validators_onchain.log | 55 | 1 line | 6003d474eda3f8a2abeee3cb6621efa83fdd0f21d743e4b85a444c2c942e7e91 | committed |
| collect/validators_onchain.py | 3,746 | 78 lines | 9da2e564b3672982dc90185401120033142b5cb84453fedafe073ea4659e4952 | committed |
| dex/defillama-overview-dexs-bsc.json.gz | 620,413 | 1 JSON document (gzip) | 91e1d4e6fb78e662e9bab7c62ae04a4f0176f5a7dbf0be3d931f6b47e61a29cd | committed |
| dex/defillama-overview-dexs-bsc.meta.json | 275 | 1 JSON document | c016a73c46e892b86682b3d2afd865761a924a22a123665d20de21b7e2bfae39 | committed |
| dex/dex-address-excerpts.txt | 13,713 | 239 lines | c16eb4e08dc0641e20a49db29bce0c361098e42c3fcc60f49b5bf46b469602e7 | committed |
| docs/48club-docs-faq.txt | 5,712 | 133 lines | c98942615a0d96ef6d587bc737d6f70b2527ef5e04c506b5a2cbda46fbf4af32 | committed |
| docs/48club-puissant-auction-feed.txt | 9,217 | 258 lines | d133a1774ad7d0b18194563b782e3df1f4bbe7c8598602d5c222733cdd576cf3 | committed |
| docs/48club-puissant-builder.txt | 3,340 | 90 lines | 2df14b160c65cc18e48510d9bdaeb04b3b2c75ee3fce5ff9f8752ff24128f38c | committed |
| docs/48club-puissant-send-bundle.txt | 6,916 | 235 lines | d0562a285753838f16e36e46cd21b6cdca2097a1bf7887ee2d849d294c4235b8 | committed |
| docs/bep-067.txt | 2,511 | 59 lines | 721f4fd266a0265a2435a55c68e2159bb73c79e39fbbc84ee2c69dc0891e18f4 | committed |
| docs/bep-126.txt | 11,176 | 198 lines | 49f2f8063fb3ee97738408fe97bd11c9a352f4bbb204e6ee2dfbbc9acaf7995c | committed |
| docs/bep-322.txt | 19,394 | 474 lines | b3e09339553ee690352f8e7c6554053aecb7d2ad2c34ae37e6b124fac61d3d4b | committed |
| docs/bep-341.txt | 9,154 | 131 lines | afebe9a80bfc23667f046e8cb58705475241696d1aac9ed44df61090b7311226 | committed |
| docs/bep-520.txt | 11,805 | 163 lines | 74dabca46ea0a7c14d24d28d2f070b3bced780f3fedc57a5f975d45dc475944f | committed |
| docs/bep-524.txt | 7,330 | 120 lines | e8b07e04829dbb99a922e34004e4040eadf13c8b37e28c1c268b96c17248873c | committed |
| docs/bep-563.txt | 7,074 | 140 lines | b9179c58aac2518066b006db1d9a6c9e09916644649d213c588214ed787961da | committed |
| docs/bep-564.txt | 5,035 | 107 lines | 6fc4b0faaff17901dd948a938c2aaa4daa1b55fd5986a3898baa2c8a6f80d638 | committed |
| docs/bep-590.txt | 5,034 | 104 lines | dc96760aa5726ad07f9c857b841c0981bf06923280cc9027aa9c38d35699f99c | committed |
| docs/bep-619.txt | 6,642 | 116 lines | 37282a4d974bdd49ee5a69702b58009154c09277915124179341b28a73c89703 | committed |
| docs/bep-648.txt | 4,726 | 82 lines | 54de2349e4ef5a28448f71d0826e5fcd243b0a36da13eae2f92d054eb5a73629 | committed |
| docs/bep-658.txt | 4,929 | 94 lines | 2815e5ac8070f1e0331996c2a493f93dc9c67d0c44586c2b8ea75bb353deb257 | committed |
| docs/bep-673.txt | 2,043 | 57 lines | 51535960ff9fdad25289374344e7f0c4dd5cd44ad4003a9b99386a97f211993f | committed |
| docs/bep-675.txt | 16,500 | 188 lines | db4bfd1a1a05b4708f3f0bd80bf9686583cfb9be0731b040b3d425cebbe491f5 | committed |
| docs/bep-718.txt | 2,031 | 56 lines | 724358d57004a8c55deeb816c85366b038a7bc58cddd7aec013827b766021b1d | committed |
| docs/beps-readme.txt | 14,037 | 146 lines | 1384d8ddc156105526d2e8c5f9e194bc101bc8a970831c69759dfa34f45afb1d | committed |
| docs/blockrazor-bsc-block-builder.txt | 8,228 | 193 lines | b7bfc7b5fbebe3e50bb365db8345a5c7335399d4879d183efe8e478d95544604 | committed |
| docs/blockrazor-call-bundle.txt | 7,694 | 290 lines | 6fcad4a97a197cb23aac7bdbfd0561d3756134f15a0a1b785f1562181a3ddc1e | committed |
| docs/blockrazor-send-bundle.txt | 6,780 | 252 lines | e1d2fbdc267c8f83b5aa2ee16b4f18b9a4f56d21da2eb34edb5484d94ea9b46c | committed |
| docs/blocksmith-docs.txt | 637 | 11 lines | f5c64324e76370777927bbed7f92d317c8215676758cbf870d79bd005898d17b | committed |
| docs/blocksmith-send-bundle.txt | 734 | 11 lines | 3848bbbbd4601d9c4d437c49719ab12bb98d656c2bb36719d59854cf5ae7dac3 | committed |
| docs/blog-exploring-mev-landscape.txt | 17,516 | 350 lines | 0008b2c85ffbe22ca698ba1d74c0871482100dcbafae38f70bc5dc6aa3fbdee0 | committed |
| docs/blog-fermi.txt | 19,472 | 450 lines | ea87fb07cb90d7485e5d7a8c4a4e039fa4c3666947d35fe6d7274726a1e7664b | committed |
| docs/blog-good-will-alliance.txt | 14,517 | 340 lines | 21c2cb85d0d3c9253c0ccc8c72c55dbbee2dde6253a865494fdeed6d0d367e78 | committed |
| docs/blog-infrastructure-levelled-up.txt | 20,198 | 423 lines | 35cbf98039dd315b3d244325baaf53ad15b866a02d433d838b47f15c546fcd2c | committed |
| docs/blog-key-changes-mev-strategy.txt | 17,151 | 360 lines | 22c8c745c64db887ad6bfca3c6882d6eb53a4f3d838e0178dabd6a9774bf48c0 | committed |
| docs/blog-maxwell.txt | 18,855 | 459 lines | e6719ddae6dfd509858ee1e77d7ad53384b5c09145556039b288dc1dd872a51f | committed |
| docs/blog-mev-faqs.txt | 16,101 | 377 lines | 0b51bbe33285d563bb9222a0323dd0da23306536e02ebad03f87f812ddc0b6bb | committed |
| docs/blog-osaka-mendel.txt | 17,593 | 440 lines | 83d83084053d84b7a3ca6736ed717ffee211a307e8379aeb7810a74fb515514b | committed |
| docs/blog-unlocking-mev-guide.txt | 22,604 | 413 lines | e765143db8e5f95af6289f0d59e7839f53db7b2d6698d8d7e2a9650bce87aa6c | committed |
| docs/bloxroute-bsc-bundle-submission.txt | 7,307 | 236 lines | 5f85d1c83745defc95c05f20132c6aa612afaf1abe6fdad208e7914e0892c782 | committed |
| docs/bloxroute-bsc-overview.txt | 5,462 | 167 lines | 0d395a3c086a82246d3865d8d3ca505a15ba10ad0baf50dbbead82c06b714df6 | committed |
| docs/bnbdocs-bsc-introduction.txt | 13,620 | 215 lines | 40848c906fe32d6e873470b75710c1c799ffd90ad960f7891921a8c2693bae45 | committed |
| docs/bnbdocs-bsc-overview.txt | 6,970 | 152 lines | 77627a19b598c85e481b5e04dbde67dc9c7da774b616486c042143168e211c2b | committed |
| docs/bnbdocs-evn-faqs.txt | 5,965 | 153 lines | 94abd90ca3beae50c15aa2a58d0ac2a6f025401b280dc8f1247551d5bcc47f15 | committed |
| docs/bnbdocs-evn-overview.txt | 6,670 | 169 lines | 27556f4b9fe5d07d6d59518fc5025661bcd3171c1b07e9b2beefa32c3cc942c4 | committed |
| docs/bnbdocs-faq-lorentz.txt | 6,565 | 183 lines | fa651685d02f6986f34e9a1a50b3cb9031223f2e37888ea1be4367288f18d54c | committed |
| docs/bnbdocs-mev-builder-integration.txt | 7,835 | 190 lines | de48832ad7fc1f702d5eca2d91dbfda78dbf86d5516bb285489ff4bcf6c44b9f | committed |
| docs/bnbdocs-mev-faqs.txt | 7,759 | 168 lines | a11cdb3d7e812d5b975a807d44960530b6ca5957bf76da9e551d6cdb4c5a22d4 | committed |
| docs/bnbdocs-mev-overview.txt | 8,964 | 179 lines | 962faed85204d22c57d04093e3eb48fc417d8a238ab4e47f065903eba3a84076 | committed |
| docs/bnbdocs-mev-user-guide.txt | 11,116 | 217 lines | 67c6cad8f66bdc5faa1f9972139e17c83a4ffdea454ab5770d3271763cbcd727 | committed |
| docs/bnbdocs-mev-validator-integration.txt | 9,973 | 231 lines | 8ca37256639fe221d3aff34dd305bc9c5c4bc854f9bf8e8eb8cd690eb87aa8ba | committed |
| docs/bnbdocs-src-faq-lorentz-hard-fork-upgrade.txt | 4,345 | 93 lines | e946a8574d4bad5042c6a7fa9f939d6f17ff0a9c5de1ac4167364e6efd33c8c6 | committed |
| docs/bnbdocs-src-introduction.txt | 10,011 | 84 lines | 1dfd5978dc71d40430ec9dda67afc1a6f15f2f28ee1f59620a8c2b1b08b57ab8 | committed |
| docs/bnbdocs-src-overview.txt | 3,572 | 39 lines | 0534194333efb19685e7fbd3033548c296f8713ed93051bebc2ab8001a61b0c4 | committed |
| docs/bnbdocs-src-validator-evn-best-practice.txt | 6,202 | 119 lines | 6c7b6605348df6f43ba8ee5b845fc8b0ec07f932441c303b5edccf86125e1130 | committed |
| docs/bnbdocs-src-validator-evn-faqs.txt | 1,870 | 32 lines | 66a2bf9e4fcb774d384dfbdd263a1c3959d94c7e37c9899a243db8909b5a753f | committed |
| docs/bnbdocs-src-validator-evn-overview.txt | 2,716 | 42 lines | 8a5537330a6d957d293e5deb72500744332f5b48c9f72cfa7c350520bb958c95 | committed |
| docs/bnbdocs-src-validator-mev-builder-integration.txt | 4,040 | 99 lines | a7f7f80babbd5cfaac3a49e768323adb04e140059b1a6ba0f0305eeece62577a | committed |
| docs/bnbdocs-src-validator-mev-faqs.txt | 3,208 | 63 lines | 3c2035fb9c9725f34eb3d5b13f49144f086b1af0a3ace4d5032d5734224a3d4f | committed |
| docs/bnbdocs-src-validator-mev-overview.txt | 5,195 | 105 lines | 162a2c1c902d0b062275ce5a8ed2b8cb77fd1ae2cff68c24e2b5f04dc4d6f6f5 | committed |
| docs/bnbdocs-src-validator-mev-user-guide.txt | 7,803 | 89 lines | 54036f479c7eee96ec8e7ae0fb805158757bc132e8f6a69dea6d19c08839707d | committed |
| docs/bnbdocs-src-validator-mev-validator-integration.txt | 6,053 | 141 lines | cbbe3efa4d3ce9d02b9deb12f66149de2327521fcabf0d2a96f79ece60700f8a | committed |
| docs/bsc-builder-readme.txt | 9,396 | 112 lines | c1ebb554fec2245c390cab962bf0d65dafe5e35121150508c1aa49e358f913b8 | committed |
| docs/bsc-changelog.txt | 135,805 | 1,917 lines | a6e04e0c9cd8465ab295cfd6c2cd2cacfaa394c4e20c0e4d601bfc5048f08810 | committed |
| docs/bsc-getchainstatus-js.txt | 69,549 | 1,198 lines | 3b6dbe23195bf7088d90cb2262d73131ee296dca029ea97c42c4367a18e88eb9 | committed |
| docs/bsc-mev-info-builder-list-toml.txt | 13,123 | 342 lines | c82fda95d09f9ba2ddb27671944e7a4b50bc0c17cab39e9cddb8a413cf0655a8 | committed |
| docs/bsc-mev-info-readme.txt | 1,219 | 25 lines | 492b9d61b582031e89772dae728bc48d9e2387dc6eb71e16f437d79907b615af | committed |
| docs/bsc-mev-info-validator-list-toml.txt | 8,536 | 239 lines | b3a58c44732577359d50fbe1ea27b7ce0f1f14f15d71022340c00bb9d5b043f1 | committed |
| docs/bsc-params-config-go.txt | 90,225 | 2,187 lines | aef92cc024f87406c3fe37bfed8c15b52498e40184eafa2beb0e0a8e4ebeac03 | committed |
| docs/defillama-overview-dexs-bsc.txt | 534 | 11 lines | 973b05f770d67ec5f4c742197b271bd3471c1faa041e13764550fc973c5fbd97 | committed |
| docs/excerpts.txt | 16,978 | 341 lines | e371f5a40a627fa6131ff628d09d9ed6732722c2ad939ad465fb4a8a6bccb2df | committed |
| docs/flap-bonding-curve-md.txt | 5,740 | 69 lines | 44111fdabe9e5d2daeaf94cec8da75483b74fbb2e2fe94c8ea0d49ea9737c161 | committed |
| docs/flap-deployed-addresses-main-md.txt | 9,673 | 114 lines | 0fd93f9bbe82f40511f5ec1e90bdca428fadada712d3ba8c1209adea8ab209f5 | committed |
| docs/flap-deployed-addresses-md.txt | 1,064 | 16 lines | a69fc156348053f3032211e76555ec36daead4969ffb61411e6356f4c2c10b59 | committed |
| docs/flap-docs-home.txt | 2,718 | 61 lines | 64a6a5504e3abbc7a4cbfba913f3196344e401d8b556dee9b799dec50cf62400 | committed |
| docs/flap-migrated-to-dex-md.txt | 4,038 | 36 lines | 34923d806fb018feeec4ffcff977da9b751d209378f0722fb32ee2f7c2b2c8d2 | committed |
| docs/flap-token-migration-md.txt | 3,830 | 59 lines | 8672ca7be848ad2a2041dd5e302d19790bb7cd538c17716598067c0530d98a21 | committed |
| docs/flap-trade-tokens-md.txt | 28,439 | 747 lines | b5c78c77e6422d7471bd1ac6f128190dbc7f66d62e6fb9cbd1d275f8aff4256f | committed |
| docs/flashblock-home.txt | 1,922 | 66 lines | 76347eb53f3f74be749045c2603b724fdc03763ad7e6ad771666df22f2ac90e7 | committed |
| docs/fourmeme-docs-integration-guide.txt | 6,756 | 158 lines | b29b48471a360fbcf92be6503f846ffe63c3e038cb2dedea874467126e47d8c8 | committed |
| docs/fourmeme-docs-itokenmanager2-sol.txt | 6,566 | 160 lines | 5260fa6b1850fed8b59788c831bb8c2e501a9e1e1cfc8da6628d2c813d02e867 | committed |
| docs/fourmeme-docs-trade-guide.txt | 12,870 | 356 lines | 0d36e11b7461983fa1290f8f861845ac3b8a90373814b94ac94fe4a9d82d1a60 | committed |
| docs/fourmeme-how-it-works-md.txt | 2,880 | 55 lines | 7aef3504bc840547f6156143ce06a1daff9010ee6022a63b5d2fa1e8c317746c | committed |
| docs/fourmeme-integration-md.txt | 1,350 | 22 lines | ce6ebcb826007a4bebf39d30eaf59b4bf1a837ec02281c95965c82490cb38e2c | committed |
| docs/fourmeme-protocol-integration.txt | 3,696 | 88 lines | 2da95c7f7e1973421f749b9998cc6dd0205f79adf98bdc29c958249bd0bf4343 | committed |
| docs/gwa-builder-list-toml.txt | 9,228 | 233 lines | 6e1a403a506c1a5d2da22047a8ad2583d5a234c22325a55dc1b45d9fd7f4ec36 | committed |
| docs/gwa-readme.txt | 616 | 12 lines | fe419270005f3f03662a32fe5428ba8e8fc3fd6bd8df1f7cab9f0eb2e38ca39d | committed |
| docs/index.csv | 31,180 | 92 rows + header | 4b216d55d05ec1e8752f99b5ea1ad3bae90eb6297059cdf4a63d7225fd443355 | committed |
| docs/jetbldr-home.txt | 1,633 | 63 lines | 2aaf39c795c0291c9bf0643f40c1348700c8aa07e8a17e05098dbfdb7b3c9db7 | committed |
| docs/nodereal-builder.txt | 7,074 | 192 lines | 9e8b7ad51b7339f993acfbac663275c2e2bb21d8c28a11d6f3d50822980e0bc1 | committed |
| docs/nodereal-bundle-api-marketplace.txt | 7,809 | 232 lines | 8c205dfda4a173e8cac808ed31822afb36aaa63c0e869d27e1e1250de17c21f4 | committed |
| docs/pancakeswap-infinity-addresses.txt | 5,623 | 170 lines | 62e638592e8af21d79882d274dfc18994b6eb531a1f4edf0505c02bb10571eb6 | committed |
| docs/pancakeswap-infinity-hooks-md.txt | 620 | 11 lines | aa14810f1b2263aeb3459df5c20f50b3b62423d0259f54842318f915453e1855 | committed |
| docs/pancakeswap-infinity-overview.txt | 4,850 | 154 lines | 675ccaf528fee7c2667597270d9d7ce1d5b55e81eb8c58483672ffc4eb4e2584 | committed |
| docs/pancakeswap-v2-addresses.txt | 4,770 | 188 lines | 78e63e4527d3511c68707109f6e9a9fb0e562306d0775029886cd468b1f4ff0e | committed |
| docs/pancakeswap-v3-addresses.txt | 6,818 | 200 lines | 08ad801bbb86437843a94c3b3b051039424ad1832757c5b31b827c9b7ba1dbfb | committed |
| docs/raw/48club-docs-faq.html.gz | 65,063 | 689 lines (decompressed) | a59e1cb2facdcdcef2c48d1d900ea8744f22e7758642051eb792c826f1ded3aa | committed |
| docs/raw/48club-puissant-auction-feed.html.gz | 75,726 | 689 lines (decompressed) | b8809178fefe6bfa66e9711e5b9bd060523c39c007cc96b88778e08a1bf51c54 | committed |
| docs/raw/48club-puissant-builder.html.gz | 61,693 | 690 lines (decompressed) | f06e30de68afacd4d8639618715ed3a72d637f21c41e5eb3d14de36eb55df904 | committed |
| docs/raw/48club-puissant-send-bundle.html.gz | 73,061 | 715 lines (decompressed) | 4a9c786efd3ca8c94738720c8f85fabca05895ff45b22243918619ea03c52005 | committed |
| docs/raw/bep-067.md | 2,000 | 48 lines | c15234840a36d952196a739b7258b00352a102192c0b25deda1b77b761dca221 | committed |
| docs/raw/bep-126.md | 10,646 | 187 lines | bb41c568f2bb781b6cc518c602aceb4986c640f757d4d982683902b843119c13 | committed |
| docs/raw/bep-322.md | 18,852 | 463 lines | a736fd904de1809fd60511e216b2f11d48ea3c5c4fd5797a495f894f60b212ad | committed |
| docs/raw/bep-341.md | 8,614 | 120 lines | b77be3885e9557b995ce61ad201440a7151bf28d7bfa10c57d3132475fcee4e2 | committed |
| docs/raw/bep-520.md | 11,263 | 152 lines | 479dfeb7f6c16012abf646bc8f6fa65f72135895b783f8c8090b6693ff0a822d | committed |
| docs/raw/bep-524.md | 6,787 | 109 lines | a92f5c95009e4ea1f97a5bab9698029655f9f1fb408f2824569893ad4b9d8c7b | committed |
| docs/raw/bep-563.md | 6,549 | 129 lines | 3dbe79ce2a579e95476d643e4daa2231d1bc69ae2ccddf404c595232e4847d3c | committed |
| docs/raw/bep-564.md | 4,501 | 96 lines | bd693f0529d24ad863c6b04c6c72ad3f4855b2a7d62c09579db493b2344582a5 | committed |
| docs/raw/bep-590.md | 4,486 | 93 lines | 0504e44500fe675bbb9ec21f9e0752364766def9ac3de399e7c60ad21ae4e053 | committed |
| docs/raw/bep-619.md | 6,097 | 105 lines | 02d9bd32b0c9b73978823d3ba50ae98e40b798a7804ac3bcf40aa96c9b52041c | committed |
| docs/raw/bep-648.md | 4,179 | 71 lines | de32f7d660df272c1098cf76d13de24685225e135ca689d076a26b271b3b924a | committed |
| docs/raw/bep-658.md | 4,404 | 83 lines | e5d3a727461adec6af0dc38735abea3c0fbc0c8bdab302e83a0db8cfd6ce9b5f | committed |
| docs/raw/bep-673.md | 1,523 | 46 lines | 53874d30067be9e0abbdefaf1e2516b372a50cf7c2b74713ccbaa5c8f49fde1c | committed |
| docs/raw/bep-675.md | 15,942 | 177 lines | 1523cd76c85817453bac19041445b30d37991115135dcc984c1391dfb90255fb | committed |
| docs/raw/bep-718.md | 1,504 | 45 lines | a437cc715cad8d71db45dff1608c327741b330690c3c79ca2603ece1e08faed0 | committed |
| docs/raw/beps-readme.md | 13,536 | 135 lines | c5db9afae31d1de9ec030d7211f841535ae632a494e31291295ce650d72f0f6e | committed |
| docs/raw/blockrazor-bsc-block-builder.html.gz | 85,455 | 689 lines (decompressed) | 773bb69352cd3d860591563d8b65ce79b4f54e3006c4a46aa3c9b4681b092def | committed |
| docs/raw/blockrazor-call-bundle.html.gz | 90,207 | 769 lines (decompressed) | 12ab4e3056adee554fc8b5b0338e04c25773e671262a8b547ac284b8550239f5 | committed |
| docs/raw/blockrazor-send-bundle.html.gz | 87,695 | 721 lines (decompressed) | 9579329ff83f1c1dd5f20bfc520a057e9d730789eaa30767db142d17524248ae | committed |
| docs/raw/blocksmith-docs.txt | 227 | 0 lines | d73d278d2eaf89040f480f03d46c3e31f5a9c838de37cfaddd0d1641bb18a78e | committed |
| docs/raw/blocksmith-send-bundle.txt | 257 | 0 lines | d7b61dec985ebaea5a2ac89501167997bec28cbe34b7fa644405457e37dbf503 | committed |
| docs/raw/blog-exploring-mev-landscape.html.gz | 62,066 | 38 lines (decompressed) | cc619675bd25d0fe3bb0af5d6148c92b95d488b1dc6c7581a406236c45a1aa23 | committed |
| docs/raw/blog-fermi.html.gz | 63,829 | 50 lines (decompressed) | 378c0d7d02ca99c04e298aaff5cf9220ffefbcc2f12a25bce10b07d4079ab5e3 | committed |
| docs/raw/blog-good-will-alliance.html.gz | 59,530 | 38 lines (decompressed) | bce6cf44acdd6bff4944a29fbb3d9e916f5975952566c1cca760549343f5f81b | committed |
| docs/raw/blog-infrastructure-levelled-up.html.gz | 65,624 | 54 lines (decompressed) | 3801a305bc6db4f958f08e16956dd2edae9c5fc5ac1726c4bd5e91d08e7c24ce | committed |
| docs/raw/blog-key-changes-mev-strategy.html.gz | 61,755 | 38 lines (decompressed) | 297a2aec2a64f59918abe652febb9b024890fad3630f1ef742eac9142a2ea5e9 | committed |
| docs/raw/blog-maxwell.html.gz | 63,836 | 56 lines (decompressed) | 5f3f796f6ecfe018be5225ec4435386b029cebcf4f8fde4d9ec2ca915e6721bb | committed |
| docs/raw/blog-mev-faqs.html.gz | 63,107 | 46 lines (decompressed) | b2a6280406ec316a7012652b39eaeed49d83bb5de9b53c78c3e888507e99b48b | committed |
| docs/raw/blog-osaka-mendel.html.gz | 62,352 | 60 lines (decompressed) | 509972dd2d99350d92a95a54ed7445780f766bafea45387e799e17d7890e4ec0 | committed |
| docs/raw/blog-unlocking-mev-guide.html.gz | 65,338 | 38 lines (decompressed) | 98b924cc595521fc0d413eaddc130e10a09a94b6f5b161796980a4a7c7a291cd | committed |
| docs/raw/bloxroute-bsc-bundle-submission.html.gz | 84,661 | 768 lines (decompressed) | be7d3598d6417502c65393d8ce26c20b7fbe95d5781104b84c1562b956e687a8 | committed |
| docs/raw/bloxroute-bsc-overview.html.gz | 75,174 | 763 lines (decompressed) | 7fd1ae547adb0b6514bb5e17f90ffc779150ac199c2cee590067807052ecb5b0 | committed |
| docs/raw/bnbdocs-bsc-introduction.html.gz | 15,209 | 3,017 lines (decompressed) | 4f2dedf5b925e06af5cc351f71ab389e5ec03ba8b98736d8c4929b8d501121e7 | committed |
| docs/raw/bnbdocs-bsc-overview.html.gz | 12,654 | 2,920 lines (decompressed) | cee4ea705d82f50e3867ea1ad0a9c223aa03f2835e80b37ea5b320f11768d9ea | committed |
| docs/raw/bnbdocs-evn-faqs.html.gz | 12,047 | 3,087 lines (decompressed) | 1c14cf827817ca10a0e720a9462b6e026e4c8c06bd56fff2482ab8186599817c | committed |
| docs/raw/bnbdocs-evn-overview.html.gz | 12,414 | 3,166 lines (decompressed) | 9c221f49cd1db4743ac684a93aa2f64d6b6b91546a891ae1fe455f7263f3b220 | committed |
| docs/raw/bnbdocs-faq-lorentz.html.gz | 11,998 | 1,511 lines (decompressed) | a21a890b5079458e9b5c93efa7df4e060cef05635941a99a50fcc9d5bdf5c998 | committed |
| docs/raw/bnbdocs-mev-builder-integration.html.gz | 12,842 | 3,139 lines (decompressed) | 7e21688627f512e29d1b10bd9d7d38aa7bdfbde93b88251c9b437d8766d94561 | committed |
| docs/raw/bnbdocs-mev-faqs.html.gz | 12,641 | 3,206 lines (decompressed) | 2d224f5e3d4111a149a37ae8eead0d4ab869223135997e80e4310fd0d565d629 | committed |
| docs/raw/bnbdocs-mev-overview.html.gz | 13,464 | 3,178 lines (decompressed) | ebc4ce66ae1f44a662d7488fd0f83c315e27b5d753669d44ce3fe09a3d243018 | committed |
| docs/raw/bnbdocs-mev-user-guide.html.gz | 14,225 | 3,226 lines (decompressed) | 835039430bf1ab78480b05b04a759d0e7aa0be75a8d939d2f451b15b6143c578 | committed |
| docs/raw/bnbdocs-mev-validator-integration.html.gz | 13,829 | 3,259 lines (decompressed) | a5b4795c934e14bacc2e839a143ccb1d1f42f4d174c2bd7f6726a1069212540b | committed |
| docs/raw/bnbdocs-src-faq-lorentz-hard-fork-upgrade.md | 3,638 | 84 lines | 705091f55234b5773d34141c1301670e8cc6b11ce3d2ef6f358a0672c6b4fea1 | committed |
| docs/raw/bnbdocs-src-introduction.md | 9,355 | 75 lines | 17c76ed02d95a8bca5b38603988d7b930ca3bf6093245a97346ea5d3938b4c6f | committed |
| docs/raw/bnbdocs-src-overview.md | 2,928 | 30 lines | 3bc05b92ceb28fd4a477a70abdc2f217a5073e8e6e52449ffd5a82377e47754f | committed |
| docs/raw/bnbdocs-src-validator-evn-best-practice.md | 5,501 | 110 lines | 4bdf12c4e6e583b8f93fe315ceae073991b3906395e4505036df89165c2e9c10 | committed |
| docs/raw/bnbdocs-src-validator-evn-faqs.md | 1,196 | 23 lines | 2d3d181d6a54c78377241de1880d8e728810ca336ef008b1b543d9335e8fa51b | committed |
| docs/raw/bnbdocs-src-validator-evn-overview.md | 2,030 | 33 lines | 2cdeda1ba4cbda521880bd9997ea1048ae6e43415b503c7262f96fe831310f8c | committed |
| docs/raw/bnbdocs-src-validator-mev-builder-integration.md | 3,321 | 90 lines | ec04a04bc1c01c27fd7006ab5bc4bad77378f3819eb278f915e41d9749564336 | committed |
| docs/raw/bnbdocs-src-validator-mev-faqs.md | 2,534 | 54 lines | 749d2fc208e9e758bf240d2525d11d96d32216d09f6139ecf4b568737622a8ab | committed |
| docs/raw/bnbdocs-src-validator-mev-overview.md | 4,509 | 96 lines | b7c2e0a3e52500583d50d590ebc51730ea5b30c4a40f32e039cd950ac870256f | committed |
| docs/raw/bnbdocs-src-validator-mev-user-guide.md | 7,111 | 80 lines | 821f2930d8178b6ed121c8c3013d3f899c3f23dcd1ca647f36f0a57ca15ea92f | committed |
| docs/raw/bnbdocs-src-validator-mev-validator-integration.md | 5,328 | 132 lines | 281b3749a2fcaa01f1a045c98b59be45b171738545db6616386d33ef689f4fd5 | committed |
| docs/raw/bsc-builder-readme.md | 8,868 | 101 lines | c1707881d644377f8d24abb9e3cdb3fc2e0b1040223f145f7e27810603c06a10 | committed |
| docs/raw/bsc-changelog.md | 135,302 | 1,906 lines | e49b26bcf69cf0f27c92c42f85c83ee4347886919d7d169901c33d2ac7e7e8b5 | committed |
| docs/raw/bsc-getchainstatus-js.txt | 68,937 | 1,187 lines | 3db2d658100a9f526d593032d1f2ac6c06dcd2c590ea90a142cbd227058148c3 | committed |
| docs/raw/bsc-mev-info-builder-list-toml.toml | 12,476 | 333 lines | 81fd1593ad91ebd3e7d89fbb909dc8771d81eaeec67b7f8019cc80b6ff2a389f | committed |
| docs/raw/bsc-mev-info-readme.md | 644 | 16 lines | c441b86abfde86498dee0354f4fa4efea64fc1133c63a5d143e2dc981f3d783b | committed |
| docs/raw/bsc-mev-info-validator-list-toml.toml | 7,908 | 230 lines | 7cebb4797fc6e57b37ee136e72e7675a322420428e82f3ecd33afc77396ced2b | committed |
| docs/raw/bsc-params-config-go.go | 89,674 | 2,176 lines | 016aeda246f200c3076567566aca34374cd8c6bef81de2caee4db8dd98421863 | committed |
| docs/raw/defillama-overview-dexs-bsc.json.gz | 620,413 | 1 JSON document (gzip) | 663df5e55355f4d6405112ddefc4270af1601d574d2f38e74367ee37b5c3e91c | committed |
| docs/raw/flap-bonding-curve-md.md | 5,203 | 58 lines | e3f11dadc5aa4320d654fb70476d4aa87cce762ad8f03f8e56d3ee3be6294257 | committed |
| docs/raw/flap-deployed-addresses-main-md.md | 9,111 | 103 lines | 411483480c2d50a33df0bd0c83175270936c88bf13174af119b426e5089156b4 | committed |
| docs/raw/flap-deployed-addresses-md.md | 442 | 5 lines | 822b1dad3ee3209abb5e8e1b672daeb2becb18958c1ebac22365e6f1f6e11f51 | committed |
| docs/raw/flap-docs-home.html.gz | 65,212 | 689 lines (decompressed) | b19c3e8b6f6345a4e10408cd43f291a8e8bfc7ebfe187a9b6ebced5571a0d74f | committed |
| docs/raw/flap-migrated-to-dex-md.md | 3,501 | 25 lines | 8b73a9e0d144c7f3871dd603119afdec7221f757d4a5fded974817496c18d506 | committed |
| docs/raw/flap-token-migration-md.md | 3,247 | 48 lines | 3a0d3f08dbc112cb4d026d83d6f101fef6dbd277de9f3836140da9762e78fabd | committed |
| docs/raw/flap-trade-tokens-md.md | 27,868 | 736 lines | c6e69bbd60fce2201a7e7fcc4fd69ad1c65856f28fc01b5f4163b39d9399ce08 | committed |
| docs/raw/flashblock-home.html.gz | 11,961 | 0 lines (decompressed) | 2c0133622dbaf4e464979b14bb1645b85f409f09e89519531d979d47e22eeecb | committed |
| docs/raw/fourmeme-docs-integration-guide.md | 6,091 | 149 lines | 2705ed368627be2ec5787499d3e22ebdd800b0d13f9216666f152d5a1395295f | committed |
| docs/raw/fourmeme-docs-itokenmanager2-sol.sol | 5,872 | 151 lines | 14e198b0d519faab343664f8bbfa15e2f40c1db4eb1666917cad6641b3db53a8 | committed |
| docs/raw/fourmeme-docs-trade-guide.md | 12,244 | 347 lines | 68e88061e90ebaf3fed6e8d44eb386995e68c4f489aa03d472f9fdc8f0c4aa29 | committed |
| docs/raw/fourmeme-how-it-works-md.md | 2,357 | 44 lines | a0b9c01e346865b9831b691f5efd26d4544620ed69d1c7c0698ed420a2b57059 | committed |
| docs/raw/fourmeme-integration-md.md | 790 | 11 lines | f2907ff36f8cdfa7dce269fa9cea6ef421135e8e7f2e935e000f925b37100dcb | committed |
| docs/raw/fourmeme-protocol-integration.html.gz | 60,184 | 688 lines (decompressed) | 76e48dd3d5a33b8ebae1812e3bd54a1105b277ffd6a1497e44307a0e8650b06e | committed |
| docs/raw/gwa-builder-list-toml.toml | 8,578 | 224 lines | f3a81677a03feb7a84d77908f44e3ed9008ce0f6fee717b0860ac4d2c26638f7 | committed |
| docs/raw/gwa-readme.md | 26 | 3 lines | 143d63c670c1773e1383e2ae8ac9b923bc5deee97bd3565f877173602284faea | committed |
| docs/raw/jetbldr-home.html.gz | 6,197 | 619 lines (decompressed) | 0257089eb05bb358034680f6405f97165603c8818a32f409d8c99995d5a6204d | committed |
| docs/raw/nodereal-builder.html.gz | 53,991 | 127 lines (decompressed) | 8b28e1df4ab21dd54c183e8b9aeb94f6e6ff12e0e0d9ad7e7e64aa00c3af14d0 | committed |
| docs/raw/nodereal-bundle-api-marketplace.html.gz | 116,658 | 36 lines (decompressed) | 9a5e3df11d7c2f4513063c401b0cfd142e2e21828410fe03d5b6a6885ce2f33a | committed |
| docs/raw/pancakeswap-infinity-addresses.html.gz | 6,826 | 31 lines (decompressed) | e0c13a61b4bcc2ac57f9d6fdeeb9c36b02adb458ec3129aba2c5e90961731b50 | committed |
| docs/raw/pancakeswap-infinity-hooks-md.json | 68 | 1 JSON document | 8bb8fb879d5478fc85c254e03c7f714099ae37aa1d696396d74601c045d0224b | committed |
| docs/raw/pancakeswap-infinity-overview.html.gz | 6,495 | 30 lines (decompressed) | c720d88afc952e5b56f6aa123cb01ff23dda7535beb053e5d7f9a24bc7f4a905 | committed |
| docs/raw/pancakeswap-v2-addresses.html.gz | 6,178 | 33 lines (decompressed) | e1045e51127b43932516e0596845cb134a395b57426458c50f2c7fdadb3f14d7 | committed |
| docs/raw/pancakeswap-v3-addresses.html.gz | 7,359 | 36 lines (decompressed) | 530aff105f8cb91a449f60084431d2f1361b372813b7ea4cc49e700c9dcdabf2 | committed |
| docs/raw/uniswap-sdk-core-addresses-ts.txt | 34,373 | 714 lines | 4dc855f3f4e60406fdaf51e287da995c9434a50194a1dc501d4d8e53158fdb94 | committed |
| docs/raw/uniswap-v3-bnb-deployments.html.gz | 2,249 | 135 lines (decompressed) | 85794031b1973cfb14db1db513b6c92526fb14df9c650b6ea1d97aa28fe119ab | committed |
| docs/raw/uniswap-v4-deployments.html.gz | 2,246 | 135 lines (decompressed) | 0b42542a8cd2cc71abe8411fdd76f62f72b4e642fbc4616af10f0280591cbfa5 | committed |
| docs/uniswap-sdk-core-addresses-ts.txt | 34,976 | 725 lines | 53fd89c595e893e1e13c075f109c38f1539cf43e65a234289588e0901cbf8922 | committed |
| docs/uniswap-v3-bnb-deployments.txt | 1,224 | 30 lines | 164982352dd6e10bf3e2e1b808863fe61075658dba8fb65a64b094a720badd5f | committed |
| docs/uniswap-v4-deployments.txt | 1,164 | 30 lines | a7aa83bbb9ce77a50d88a82107a4cd7cd6552fdd70cbf1284c3ca4c155386230 | committed |
| validator-mev-rpc-probe.jsonl.gz | 3,834 | 176 JSON lines | a84727d8502df1ab2218e850c9932387197f35033f93be5b526a4cfc971206cd | committed |
| validators-onchain.csv | 18,347 | 56 rows + header (59 physical lines; quoted fields contain newlines) | 186cfb252a2c568b85ac307db5e5dd5a85d48fc1aaceb4f78414895d61f8d726 | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
