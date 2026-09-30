# BSC (BNB Smart Chain) on-chain census, builder material, ordering/MEV docs, DEX landscape

Status: COMPLETE (all collectors finished; no process left running). Sentinel: `/home/user/dapparb/research-material/.sentinels/BSC_CENSUS.DONE` (written 2026-09-30T21:08:09Z).
Collected: 2026-09-30, 20:53Z to 21:41Z, by a collection-only agent. This directory contains data and verbatim documents only. It has no analysis and no conclusions.

## Question lines and codes used below

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

This directory serves Q4, Q5 and Q6 directly. It serves Q7 as BSC block-level raw data only; no literature was collected here. It serves Q1 only through the BSC Uniswap V4 PoolManager and PancakeSwap Infinity addresses and swap logs. It has nothing for Q2, Q3 or Q8 on Base.

## File to question-line map

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
| `census/raw/chunk-*.jsonl.gz` (40 files) | all census questions (lossless source of every derived census file) |
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

Fields: `block_number`, `tx_index`, `tx_hash`, `from`, `to`, `status` (int), `gas_used` (string), `effective_gas_price` (string, wei), `criterion` ("A"/"B"), `derived_swap_topic_log_count`, `derived_erc20_transfer_log_count`, `derived_erc20_transfer_distinct_emitters`. `receipt_other_fields` holds every receipt field except `logs`, verbatim hex JSON: type, from, to, status, cumulativeGasUsed, logsBloom, transactionHash, contractAddress, gasUsed, blockHash, blockNumber, transactionIndex, effectiveGasPrice. BSC receipts have no L1-fee fields. `tx` holds the verbatim tx object without `input`, blockHash and blockNumber, plus derived `input_selector` and `input_len_bytes`; the full input is in `census/raw`. `logs` holds ALL logs of the tx verbatim: address, topics, data, blockNumber, transactionHash, transactionIndex, blockHash, blockTimestamp, logIndex, removed.

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

### census/raw/chunk-<first>-<last>.jsonl.gz: 40 files, 200 blocks each, 415 MB
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
4. **Calldata is not in candidates or builder material.** Only the selector and length are there; full calldata is in `census/raw`. No `debug_trace*` or internal-call traces were collected, and public dataseed nodes do not serve them.
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
