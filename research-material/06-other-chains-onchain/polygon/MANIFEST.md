# Polygon PoS: on-chain arbitrage census (raw material)

Status: COMPLETE (finalized 2026-10-01). All collectors for this directory finished: sentinels EVM_CENSUS_POLYGON.DONE and EVM_TOKENPRICES_POLYGON.DONE (sentinel files are git-ignored; their text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:21Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): census COMPLETE (sentinel `.sentinels/EVM_CENSUS_POLYGON.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_POLYGON.DONE`).

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
| 6 | none |
| 7 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json |
| 8 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json |

Correction 2026-10-01: the collector's table in this section used Q-IDs and short notes; it is restated above by line number. The collector also mapped files to a ninth ID, Q-GAPS ("Would the gaps change the answer?"), which is not one of the 8 question lines; those entries were dropped.

## Window (pinned)

| Item | Value |
|---|---|
| Chain id | 137 |
| Block range (inclusive) | 94729141 to 94731540 (2400 blocks) |
| Block timestamps | 1790798852 (2026-09-30T20:07:32Z) to 1790802450 (2026-09-30T21:07:30Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = 'finalized' tag at pin time |
| Head at pin time | 94731541 (pinned 2026-09-30T21:07:32Z) |
| Measured block interval | 1.499792 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-09-30T21:10:22Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://polygon-bor-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 1 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://polygon.drpc.org`.
* Requests actually sent (HTTP): {"https://polygon-bor-rpc.publicnode.com": 2400}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/polygon` fetched 2026-09-30T21:10:35Z (HTTP 200, 1691089 bytes), stored unmodified as defillama-dexs.json.
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-09-30T21:20:21Z) on https://polygon-bor-rpc.publicnode.com, https://polygon.drpc.org. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = [1790798852, 1790800651, 1790802450] and `https://coins.llama.fi/chart/coingecko:polygon-ecosystem-token,coingecko:matic-network,coingecko:ethereum?start=1790798852&span=13&period=5m`.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/polygon/collect
python3 make_swap_topics.py polygon ..            # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 census.py --chain polygon --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 fetch_defillama.py polygon ../defillama-dexs.json > defillama.log 2>&1
python3 token_prices.py --chain polygon --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)
python3 write_manifest.py polygon ..               # regenerates this file from the metadata files
```

Note (2026-10-01): this MANIFEST.md was edited by hand during finalization (status line, 'Question lines served', the 'Verified inventory (2026-10-01)' section and the notes marked 2026-10-01). Re-running write_manifest.py would regenerate the collector's original version without these edits.

Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 2400 | 353211 |
| txs-001.csv.gz | 176243 | 13912584 |
| reverted-001.csv.gz | 7543 | 559821 |
| candidates-001.jsonl.gz | 68443 | 81569130 |
| topic0-counts.csv.gz | 1603 | 138736 |
| swap-topics.csv | 22 | 11929 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 333 | 21896 |
| prices-defillama-historical.jsonl.gz | 27 | 39960 |
| native-price-chart-defillama.json | (JSON document) | 1518 |
| defillama-dexs.json | (JSON document) | 1691089 |
| defillama-dexs.fetch.json | (JSON document) | 139 |
| token_prices.fetch.json | (JSON document) | 609 |
| window.json | (JSON document) | 2640 |

Candidate counts by criterion: A = 3235, B = 65208. Transactions: 176243; status-0 transactions: 7543; distinct topic0 keys: 1603.

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

Polygon Bor: miner is returned as 0x000...000; the block producer's signature is inside extra_data (not decoded).

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
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xfbe12870fd7d53c52d1a0893b8fe33b26161b0084403ac42b444d5d31ee8369d |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x1701a8da8d8127b1f39d1f44f8447fd713f139eee6b88db43bee0483e0972a8a |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | no |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | yes: 0x4446ccdf3022b743b41f13121c47dc1ae676e41b347708d8ab1df9049539f872 |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | no |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x1701a8da8d8127b1f39d1f44f8447fd713f139eee6b88db43bee0483e0972a8a |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | yes: 0x1701a8da8d8127b1f39d1f44f8447fd713f139eee6b88db43bee0483e0972a8a |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | no |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | yes: 0x6b62f450397d6f133fcead0d2936ec5b7d3ba992b957737971016da0d6e5bcda |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | yes: 0x6e4ddfd481c2038a5e66321b5acb071e0fc0537c0b6b92f10696b31a5766e4c4 |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | yes: 0xbdb086776b06418ba68293c891c583512789fbdbc7aeabd8a1a24164501bda1c |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | yes: 0xe644dae0b2f2fe614ad6ef13041398df05a69078b518abce3d3590812edb6292 |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | no |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | no |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | yes: 0x5d1b755fd9a552e961029e6d143b2669eabb04732155599a4118c8f43d32314c |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | yes: 0xf1cca6e0ba478ed28831a05d8f8e713de98a982ad8f7d9f027a89d68a0522289 |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | yes: 0x057a85da10d598e1f2a767c519643ed00b2eee9dd8c89e1b9ea02e093c89d2d0 |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | yes: 0xa8e74b3fabecd7dfdd77b84a840e38cdb4d0b1bdca5a5836e6af95a3ab35b70a |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | no |

### tokens-onchain-meta.csv.gz

One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).

### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json

One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.

### defillama-dexs.json

Raw response of `https://api.llama.fi/overview/dexs/polygon` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.


### collect/

census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py (+ docs_urls.txt where used), token_prices.py, run_token_prices_all.sh, write_manifest.py and their logs (census.log, make_swap_topics.log, defillama.log, docs.log, token_prices.log). Identical copies of these scripts are in every sibling chain directory and in ../_shared_collect/.

## Coverage limits and gaps

* Single contiguous window per chain (60 min of chain time ending 2026-09-30T21:07:30Z); one weekday evening (UTC), no other days or times of day.
* Gap blocks (unfetchable after all retries): 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (per the shared definition): transaction input/calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are NOT collected. Priority fee actually paid per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces: internal native-token transfers (e.g. direct payments to the block builder / coinbase on Ethereum, native-ETH legs of Uniswap V4 or WETH unwraps) and revert reasons are not collected.
* Logs are stored only for candidate transactions (criteria A/B). Transactions with a single swap log and fewer than 3 ERC-20 transfers from 2 tokens are in txs-*.csv only (no logs). topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv; the match is on topic0 (plus the Ekubo log0 address rule) with no check of the emitting contract. Venues whose swap events use other signatures are not matched by A (e.g. Ambient/CrocSwap, RFQ/PMM venues such as Hashflow/Bebop/Native, 0x and 1inch limit orders, UniswapX fills, Bancor, Uniswap V1, Maverick V1, Trader Joe LB v2.0, GMX V2, KyberSwap classic, Clipper, Integral); such transactions appear as candidates only if they meet criterion B. A signature not observed in this window is listed with an empty verified_example_tx (not verified on this chain).
* ERC-20 Transfer is identified as topic0 0xddf252ad... with exactly 3 topics; tokens emitting non-standard transfer events and native-token movements are not counted for criterion B.
* Token metadata was read at block tag 'latest' shortly after the window, not at the window blocks. DefiLlama prices are DefiLlama's own aggregates (confidence field included) and are absent for tokens DefiLlama does not price.
* No mempool / pending-transaction data, no private-orderflow or bundle data, no flashblock / preconfirmation-level ordering data (block-level receipts only).
* The DefiLlama DEX overview was fetched once (2026-09-30T21:10:35Z) with default query parameters.
* Polygon: end block taken from the 'finalized' tag (a few blocks behind head at pin time).
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana (separate collector in ../solana), and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) are not collected here.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 27 files (27 committed, 0 local-only). All 7 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. The row counts in 'Files, schemas, row counts' above and the candidate counts by criterion equal the verified counts below (no differences). Largest committed file: candidates-001.jsonl.gz (81,569,130 bytes); no committed file exceeds 90 MB.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 353,211 | 2,400 rows + header | 8b4596d39cdee33ad93c517a115ec1a8888b182d4ad1f3adab97374e4732ad3e | committed |
| candidates-001.jsonl.gz | 81,569,130 | 68,443 JSON lines (criterion A 3,235, B 65,208) | 578c45e3b685853b974dcb895e3777cb5e8b172093a4dbdc98090577185f2ef5 | committed |
| collect/census.log | 4,059 | 19 lines | 7add01fdbd046c6720c2268507c4bf21c4346f82ee316576b6fa7a60954ed130 | committed |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| collect/defillama.log | 134 | 1 line | 470312e803dac09e7f2f2beb058474e2c9fbd65b412194998287f29dc6262467 | committed |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/make_swap_topics.log | 99 | 1 line | da19a4e7258c1f250ee4528bf12f9d8cb182e3e89778fd47b57497ee583d1e73 | committed |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| collect/token_prices.log | 666 | 3 lines | 2dc70383689e2e2ddb709d29658fd94271f863cf7258d11b1484409109ca4fa6 | committed |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| defillama-dexs.fetch.json | 139 | 1 JSON document | 0463d90bbaedf934e59b61579e805851d140b3525f861a02508c7319392703ec | committed |
| defillama-dexs.json | 1,691,089 | 1 JSON document | 736d043028a65f45579ff4a3f8355a15a6da6c44b3cec1f7b6d0dafcf32c9064 | committed |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | committed |
| native-price-chart-defillama.json | 1,518 | 1 JSON document | 678a491515338c64a47a0ad8b8c51a6afc49ff227eb82d86aadd29c60c1291d7 | committed |
| prices-defillama-historical.jsonl.gz | 39,960 | 27 JSON lines | 9112aed71294ae0049cac4c776f7955eeb6377d83a181a509a4c655d560ce1be | committed |
| reverted-001.csv.gz | 559,821 | 7,543 rows + header | 28dede70fc6530107790afccc9fdca16a7dbe8be366d101191dd919f583b2ffb | committed |
| swap-topics.csv | 11,929 | 22 rows + header | 8fe5f98379d7c2c04a9902b6ddcd4e655553375e0f495a83c0b16d19ee068067 | committed |
| token_prices.fetch.json | 609 | 1 JSON document | 2bcf182962bc562376829b4b58c1c3797ad1e956bcc6ad78e56ee45feaf15cde | committed |
| tokens-onchain-meta.csv.gz | 21,896 | 333 rows + header | ded3e0ad5ce5d37b2cf3174463b89414e4053ec6256f3e02d40406b8d74b12b7 | committed |
| topic0-counts.csv.gz | 138,736 | 1,603 rows + header | 23f3f57c08d4fc1805d25d59e31ab2feb823764309f2f236bd648669377f67ae | committed |
| txs-001.csv.gz | 13,912,584 | 176,243 rows + header | 9de4fbac6dff30c83a6d6df7270c31bdb255b45592663457610ce44be2da3633 | committed |
| window.json | 2,640 | 1 JSON document | 5b462f0b93426e123867d53d571d4c0a773c958c66c4f654460ba391f0124a7d | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
