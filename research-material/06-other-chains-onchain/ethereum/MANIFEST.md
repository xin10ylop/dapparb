# Ethereum mainnet: on-chain arbitrage census (raw material)

Status: COMPLETE (finalized 2026-10-01). All collectors for this directory finished: sentinels EVM_CENSUS_ETHEREUM.DONE and EVM_TOKENPRICES_ETHEREUM.DONE (sentinel files are git-ignored; their text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:21Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): census COMPLETE (sentinel `.sentinels/EVM_CENSUS_ETHEREUM.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_ETHEREUM.DONE`).

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md` (the same lines carry Q-IDs in `../MANIFEST-evm.md`).

| Line | Files in this directory |
|---|---|
| 1 | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 4 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json, defillama-dexs.json, defillama-dexs.fetch.json |
| 5 | candidates-001.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz (base_fee_per_gas), txs-001.csv.gz (effective_gas_price) |
| 6 | blocks.csv.gz (miner, extra_data, extra_data_text_derived) |
| 7 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json |
| 8 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json |

Correction 2026-10-01: the collector's table in this section used Q-IDs and short notes; it is restated above by line number. The collector also mapped files to a ninth ID, Q-GAPS ("Would the gaps change the answer?"), which is not one of the 8 question lines; those entries were dropped.

## Window (pinned)

| Item | Value |
|---|---|
| Chain id | 1 |
| Block range (inclusive) | 26091086 to 26092877 (1792 blocks) |
| Block timestamps | 1790780819 (2026-09-30T15:06:59Z) to 1790802407 (2026-09-30T21:06:47Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 21600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 3 |
| Head at pin time | 26092880 (pinned 2026-09-30T21:07:32Z) |
| Measured block interval | 12.053601 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-09-30T21:08:49Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://ethereum-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 1 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://eth.drpc.org`.
* Requests actually sent (HTTP): {"https://ethereum-rpc.publicnode.com": 1792}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/ethereum` fetched 2026-09-30T21:10:34Z (HTTP 200, 2110354 bytes), stored unmodified as defillama-dexs.json.
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-09-30T21:15:59Z) on https://ethereum-rpc.publicnode.com, https://eth.drpc.org. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = [1790780819, 1790791613, 1790802407] and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790780819&span=73&period=5m`.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/ethereum/collect
python3 make_swap_topics.py ethereum ..            # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 census.py --chain ethereum --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 fetch_defillama.py ethereum ../defillama-dexs.json > defillama.log 2>&1
python3 token_prices.py --chain ethereum --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)
python3 write_manifest.py ethereum ..               # regenerates this file from the metadata files
```

Note (2026-10-01): this MANIFEST.md was edited by hand during finalization (status line, 'Question lines served', the 'Verified inventory (2026-10-01)' section and the notes marked 2026-10-01). Re-running write_manifest.py would regenerate the collector's original version without these edits.

Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 1792 | 136801 |
| txs-001.csv.gz | 534635 | 44623765 |
| reverted-001.csv.gz | 7153 | 501788 |
| candidates-001.jsonl.gz | 42750 | 53682812 |
| topic0-counts.csv.gz | 5424 | 495656 |
| swap-topics.csv | 23 | 12805 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 3256 | 227585 |
| prices-defillama-historical.jsonl.gz | 246 | 393291 |
| native-price-chart-defillama.json | (JSON document) | 3634 |
| defillama-dexs.json | (JSON document) | 2110354 |
| defillama-dexs.fetch.json | (JSON document) | 140 |
| token_prices.fetch.json | (JSON document) | 547 |
| window.json | (JSON document) | 2625 |

Candidate counts by criterion: A = 19288, B = 23462. Transactions: 534635; status-0 transactions: 7153; distinct topic0 keys: 5424.

### blocks.csv.gz (one row per block, ascending)

| Column | Meaning |
|---|---|
| block_number | block height (int) |
| timestamp | block timestamp, unix seconds (1 s resolution) |
| base_fee_per_gas | baseFeePerGas, wei (base-10 string) |
| gas_used | gasUsed |
| gas_limit | gasLimit |
| tx_count | length of the block's transactions list (eth_getBlockByNumber false) |
| miner | header miner / fee recipient (raw) |
| extra_data | header extraData (raw hex) |
| block_hash | hash |
| parent_hash | parentHash |
| receipts_count | number of receipts returned by eth_getBlockReceipts |
| extra_data_text_derived | derived: extra_data bytes decoded as UTF-8 (undecodable bytes as \x escapes); builder tag |

### txs-NNN.csv.gz (one row per receipt, ordered by block then tx_index)

| Column | Meaning |
|---|---|
| block_number, tx_index | position |
| tx_hash | transactionHash |
| from, to | receipt from/to ('' for contract creation) |
| status | 1 success, 0 reverted |
| gas_used | receipt gasUsed |
| effective_gas_price | receipt effectiveGasPrice, wei |
| type | transaction type as base-10 integer (0 legacy, 1 access-list, 2 EIP-1559, 3 blob, 4 EIP-7702; chain-specific: Arbitrum 104/105/106 = 0x68/0x69/0x6a internal/retryable/ArbOS, OP-stack 126 = 0x7e deposit, Polygon 127 = 0x7f state-sync) |
| logs_count | number of logs in the receipt |
| contract_address | receipt contractAddress |
| l1_fee | OP-stack receipt l1Fee, wei ('' on other chains) |
| gas_used_for_l1 | Arbitrum receipt gasUsedForL1 ('' elsewhere) |
| timeboosted | Arbitrum receipt timeboosted ('' elsewhere) |
| in_block_tx_list | derived: true if the receipt's hash is in the block's transactions list |

Fee per tx is derivable as gas_used * effective_gas_price (+ l1_fee on OP-stack; OP-stack operator-fee fields, if any, are only in the candidate receipt sub-objects). Priority fee per gas is derivable as effective_gas_price - base_fee_per_gas of the block.

### reverted-NNN.csv.gz (every status-0 transaction)

Columns: block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, logs_count (always 0 for reverted txs by EVM semantics), type, l1_fee, gas_used_for_l1, timeboosted; meanings as in txs.

### candidates-NNN.jsonl.gz (one JSON object per candidate tx)

Criterion A: >= 2 logs whose topic0 is in swap-topics.csv (match_rule topic0), or zero-topic logs emitted by a match_rule=log0_address address (Ekubo Core swaps). Criterion B (only if not A): >= 3 ERC-20 Transfer logs (topic0 0xddf252ad..., exactly 3 topics, i.e. ERC-721 transfers excluded) emitted by >= 2 distinct token contracts. Both criteria count logs regardless of the emitting contract (no pool/factory allow-list).

| Field | Meaning |
|---|---|
| block_number, block_timestamp, tx_index, tx_hash, from, to | as above (block_timestamp joined from the block header) |
| status | 1 / 0 |
| gas_used, effective_gas_price | base-10 strings |
| criterion | 'A' or 'B' |
| derived.n_logs, derived.n_swap_logs, derived.swap_keys_matched, derived.n_erc20_transfer_logs, derived.n_distinct_transfer_tokens | derived: the counts used to evaluate the criteria (swap_keys_matched lists matched topic0 values or 'log0:<address>') |
| receipt | every receipt field except logs, verbatim hex as returned by the RPC (incl. logsBloom, cumulativeGasUsed, L1 fee fields, gasUsedForL1, timeboosted, blobGasUsed, ...) |
| logs | all logs of the tx, verbatim (address, topics, data, logIndex, ...) |

### topic0-counts.csv.gz (all logs of all txs in the window, not only candidates)

| Column | Meaning |
|---|---|
| topic0_or_log0_emitter | topic0, or 'log0:<address>' for zero-topic logs |
| n_logs | number of logs |
| n_txs | number of txs with >= 1 such log |
| n_distinct_emitting_addresses | distinct log.address values |
| first_example_tx, first_example_block, first_example_log_address | first occurrence in block order |
| in_known_swap_topics | true if the key is in swap-topics.csv |

### swap-topics.csv (KNOWN SWAP TOPICS for this chain)

Columns: topic0, signature, protocol, source_url, verified_example_tx (first log with this topic0 in the census window; empty = not observed in the window, i.e. not verified on this chain), match_rule, match_address, verified_example_block, verified_example_log_address, verification_note, topic0_tool.

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xe4bccf5318d880b77950d7669b5896638ff618bdaea0e1cc2aa14f63e4fd8367 |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0xe4bccf5318d880b77950d7669b5896638ff618bdaea0e1cc2aa14f63e4fd8367 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0xd0aafd18c43ad3ddf528c4f2eb78f2d1231c7a13f8112dd6692ad6b8dca266df |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | yes: 0x89ab72aa77e245b3901a0c57c00ee13fde8ed37d8f2dc66d4c73cdf53d6230e4 |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | no |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0xe1b6429e2a96e3dd2f0c9ebfd1bc146856ddbfe326eeba47d49dcfa4da6bb84f |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | yes: 0x8079a7bfb30107e92396fb6dfe325562daa165037b1bb0ebc7e4e46c12005ecf |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | yes: 0x7cddf17a39e6add1713d51d3cf9337eab08f1fb9bc7190ff2a89b31a7d98babf |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | yes: 0x7254ece6471b5e3d096cc42d4c6d61bae4434f8e48061a7c328a2ce023b2623a |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | yes: 0x6cd286c0fce4ba224f875c7e994fe7f1a62a0903cc1a429652d5f06e9493e1b8 |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | yes: 0x2dd74d1ff80d5c2bda265a7bc51befe55576eab91f8546686634fcaa541a6911 |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | yes: 0x7254ece6471b5e3d096cc42d4c6d61bae4434f8e48061a7c328a2ce023b2623a |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | no |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | yes: 0xcc3bdb1387a75f427771e6b577d96d0942313d356f2ca3db1943d9caba4a7564 |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | yes: 0xaa0a570da1d13d642e03ea0f0d4cbf92d2040d9bd97634d8adbdd50b216aa7e7 |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | no |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | yes: 0x8de35ce69be84897dd0609b11af8e1925dc94930b03cb34e577a4c1961f5fca1 |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | yes: 0x9109e55d3f53fdd15ec3ebc90f6a8ed1fbc1f90d4b4bb14e71a7b7d79f27864d |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | yes: 0x7cddf17a39e6add1713d51d3cf9337eab08f1fb9bc7190ff2a89b31a7d98babf |
| log0 @ 0xe0e0e08a6a4b9dc7bd67bcb7aade5cf48157d444 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | yes: 0x60b7d56135769a794a3f9e96fbb1b3d8110dfd8f09d90ae4f8a014238740a08f |

### tokens-onchain-meta.csv.gz

One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).

### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json

One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.

### defillama-dexs.json

Raw response of `https://api.llama.fi/overview/dexs/ethereum` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.


### collect/

census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py (+ docs_urls.txt where used), token_prices.py, run_token_prices_all.sh, write_manifest.py and their logs (census.log, make_swap_topics.log, defillama.log, docs.log, token_prices.log). Identical copies of these scripts are in every sibling chain directory and in ../_shared_collect/.

## Coverage limits and gaps

* Single contiguous window per chain (6 h of chain time ending 2026-09-30T21:06:47Z); one weekday evening (UTC), no other days or times of day.
* Gap blocks (unfetchable after all retries): 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (per the shared definition): transaction input/calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are NOT collected. Priority fee actually paid per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces: internal native-token transfers (e.g. direct payments to the block builder / coinbase on Ethereum, native-ETH legs of Uniswap V4 or WETH unwraps) and revert reasons are not collected.
* Logs are stored only for candidate transactions (criteria A/B). Transactions with a single swap log and fewer than 3 ERC-20 transfers from 2 tokens are in txs-*.csv only (no logs). topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv; the match is on topic0 (plus the Ekubo log0 address rule) with no check of the emitting contract. Venues whose swap events use other signatures are not matched by A (e.g. Ambient/CrocSwap, RFQ/PMM venues such as Hashflow/Bebop/Native, 0x and 1inch limit orders, UniswapX fills, Bancor, Uniswap V1, Maverick V1, Trader Joe LB v2.0, GMX V2, KyberSwap classic, Clipper, Integral); such transactions appear as candidates only if they meet criterion B. A signature not observed in this window is listed with an empty verified_example_tx (not verified on this chain).
* ERC-20 Transfer is identified as topic0 0xddf252ad... with exactly 3 topics; tokens emitting non-standard transfer events and native-token movements are not counted for criterion B.
* Token metadata was read at block tag 'latest' shortly after the window, not at the window blocks. DefiLlama prices are DefiLlama's own aggregates (confidence field included) and are absent for tokens DefiLlama does not price.
* No mempool / pending-transaction data, no private-orderflow or bundle data, no flashblock / preconfirmation-level ordering data (block-level receipts only).
* The DefiLlama DEX overview was fetched once (2026-09-30T21:10:34Z) with default query parameters.
* Ethereum: 6 h requested; slots without a block (missed slots) have no row. Builder identity is available only as the header fields miner/extra_data (no relay data, no bid data, no MEV-Boost payload data).
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana (separate collector in ../solana), and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) are not collected here.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 27 files (27 committed, 0 local-only). All 7 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. The row counts in 'Files, schemas, row counts' above and the candidate counts by criterion equal the verified counts below (no differences). Largest committed file: candidates-001.jsonl.gz (53,682,812 bytes); no committed file exceeds 90 MB.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 136,801 | 1,792 rows + header | 88b4012175986fa23ad05077a13a27b55c2555574e6401b650bc2936dc6b2085 | committed |
| candidates-001.jsonl.gz | 53,682,812 | 42,750 JSON lines (criterion A 19,288, B 23,462) | e206ae9803bd0e08b06e05197b0b09fb714d90ca0438bd239bbfe438c602e544 | committed |
| collect/census.log | 4,372 | 21 lines | 1d9a715d2cb5c3b44edbb808cf75c4258657a078c207f50d345474c7ddf78885 | committed |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| collect/defillama.log | 135 | 1 line | 9e1863e5c29141856f8c4c91b7ba81e19fc010a3bbfeb823920168cae4411bf9 | committed |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/make_swap_topics.log | 100 | 1 line | 2480bf00cb1cc96be80d23ae8d422bd9e7282ac33b68b054739ba23b55f21dad | committed |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| collect/token_prices.log | 605 | 3 lines | a588cfc40dc6b894497b5ea7cf9dd3586be913ebe7fb1a83b6ce1a2cf8d13dfb | committed |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| defillama-dexs.fetch.json | 140 | 1 JSON document | bd87f12689431952aa57817cc0ed1dd8ce8ed1fada241da7817d8a17118db17b | committed |
| defillama-dexs.json | 2,110,354 | 1 JSON document | e1b3f5768279fdeab670674aec81e6d792d6d07741dd7854a662af650b17302b | committed |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | committed |
| native-price-chart-defillama.json | 3,634 | 1 JSON document | e53918f5351d3c9f69c5a32de636ad23a9501a7f063f41a5862b2bffa8f86a42 | committed |
| prices-defillama-historical.jsonl.gz | 393,291 | 246 JSON lines | 3a635bf40de5c58050bf3ceafd050f3b311da1d628a48a8615cfd637f1feb205 | committed |
| reverted-001.csv.gz | 501,788 | 7,153 rows + header | 4db6cbf62c474179bec70c3b5ef3b52d2ae4d98522f9b9d938d6924016d9f162 | committed |
| swap-topics.csv | 12,805 | 23 rows + header | 95efd4d16a585de9007316494047ce24198908bf43e2d95b9312226a2acd3d20 | committed |
| token_prices.fetch.json | 547 | 1 JSON document | 6dbcac10243763a77aacde76f669e0180f66aea2fd6ed048d8aa001707c5c750 | committed |
| tokens-onchain-meta.csv.gz | 227,585 | 3,256 rows + header | 13af8f8a529a15fba9282099327b4a6f7c950ec5464b1b617d79a9b0457c8d5f | committed |
| topic0-counts.csv.gz | 495,656 | 5,424 rows + header | a312857197361fdcc17f293711005e76726ddd620bdc8620187b216a0163d931 | committed |
| txs-001.csv.gz | 44,623,765 | 534,635 rows + header | 7e3ebc80ed1332370e7925f4d7026dc52fff27740a6099c71684ddf186d48ee5 | committed |
| window.json | 2,625 | 1 JSON document | 9427fd6fd52c3dd672182ded1ee026853bcdc24ce8f99dde6250a9726fefe10c | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
