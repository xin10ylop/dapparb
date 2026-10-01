# Unichain: on-chain arbitrage census (raw material)

Status: COMPLETE WITH GAPS (finalized 2026-10-01). Gap: 1 of the 11 documentation URLs in docs/index.csv was not retrieved (Wayback Machine copy of the former docs.unichain.org advanced-txn page, HTTP 403; body not stored). All collectors for this directory finished: sentinels EVM_CENSUS_UNICHAIN.DONE and EVM_TOKENPRICES_UNICHAIN.DONE (sentinel files are git-ignored; their text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:21Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): census COMPLETE (sentinel `.sentinels/EVM_CENSUS_UNICHAIN.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_UNICHAIN.DONE`). Ordering docs: COMPLETE (see docs/).

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md` (the same lines carry Q-IDs in `../MANIFEST-evm.md`).

| Line | Files in this directory |
|---|---|
| 1 | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 4 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json, defillama-dexs.json, defillama-dexs.fetch.json |
| 5 | candidates-001.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz (base_fee_per_gas), txs-001.csv.gz (effective_gas_price, l1_fee), docs/ |
| 6 | docs/ |
| 7 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json |
| 8 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json |

Correction 2026-10-01: the collector's table in this section used Q-IDs and short notes; it is restated above by line number. The collector also mapped files to a ninth ID, Q-GAPS ("Would the gaps change the answer?"), which is not one of the 8 question lines; those entries were dropped.

## Window (pinned)

| Item | Value |
|---|---|
| Chain id | 130 |
| Block range (inclusive) | 60050483 to 60054082 (3600 blocks) |
| Block timestamps | 1790798842 (2026-09-30T20:07:22Z) to 1790802441 (2026-09-30T21:07:21Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 10 |
| Head at pin time | 60054092 (pinned 2026-09-30T21:07:32Z) |
| Measured block interval | 1.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-09-30T21:07:44Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://unichain-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 8 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://unichain.drpc.org`, `https://mainnet.unichain.org`.
* Requests actually sent (HTTP): {"https://unichain-rpc.publicnode.com": 450}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/unichain` fetched 2026-09-30T21:10:33Z (HTTP 200, 100466 bytes), stored unmodified as defillama-dexs.json.
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-09-30T21:12:59Z) on https://unichain-rpc.publicnode.com, https://unichain.drpc.org. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = [1790798842, 1790800641, 1790802441] and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790798842&span=13&period=5m`.
* Official docs: see docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/unichain/collect
python3 make_swap_topics.py unichain ..            # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 census.py --chain unichain --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 fetch_defillama.py unichain ../defillama-dexs.json > defillama.log 2>&1
python3 token_prices.py --chain unichain --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)
python3 fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 write_manifest.py unichain ..               # regenerates this file from the metadata files
```

Note (2026-10-01): this MANIFEST.md was edited by hand during finalization (status line, 'Question lines served', the 'Verified inventory (2026-10-01)' section and the notes marked 2026-10-01). Re-running write_manifest.py would regenerate the collector's original version without these edits.

Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 3600 | 187562 |
| txs-001.csv.gz | 30272 | 1441318 |
| reverted-001.csv.gz | 123 | 10246 |
| candidates-001.jsonl.gz | 339 | 193589 |
| topic0-counts.csv.gz | 164 | 13057 |
| swap-topics.csv | 22 | 11041 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 17 | 1267 |
| prices-defillama-historical.jsonl.gz | 3 | 1312 |
| native-price-chart-defillama.json | (JSON document) | 749 |
| defillama-dexs.json | (JSON document) | 100466 |
| defillama-dexs.fetch.json | (JSON document) | 139 |
| token_prices.fetch.json | (JSON document) | 548 |
| window.json | (JSON document) | 2639 |

Candidate counts by criterion: A = 170, B = 169. Transactions: 30272; status-0 transactions: 123; distinct topic0 keys: 164.

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

OP-stack: miner is the SequencerFeeVault 0x4200000000000000000000000000000000000011; extra_data carries OP-stack header parameters (not decoded).

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
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | no |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x25bd8c51a73d28ebf29504c5247c34bb1a9165a89c63bc77dc939b8b0c15e406 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | no |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | yes: 0x7b919f6931132ed675db372add805e78bbab6b75aff5372e565beb5465011e4d |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x5a120a1d82b173b4fca9b0d7355ff4c2bbf8d9ad03d1ea05346aa9d6cd0408be |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | no |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | no |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | no |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | no |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | no |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | no |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | no |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | no |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | no |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | no |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | no |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | no |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | no |

### tokens-onchain-meta.csv.gz

One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).

### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json

One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.

### defillama-dexs.json

Raw response of `https://api.llama.fi/overview/dexs/unichain` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.

### docs/

Official documentation on transaction ordering, fetched verbatim. For each URL: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION method, then the full visible text or raw markdown), plus the raw body (`.html.gz`, `.raw.gz` for markdown, or `.pdf`). `index.csv` lists every URL attempted.

| URL | HTTP | fetched (UTC) | note |
|---|---|---|---|
| https://developers.uniswap.org/docs/unichain/technical-information/flashblocks | 200 | 2026-09-30T21:10:51Z |  |
| https://developers.uniswap.org/docs/unichain/technical-information/flashblocks.md | 200 | 2026-09-30T21:10:52Z |  |
| https://developers.uniswap.org/docs/unichain/technical-information/advanced-txn | 200 | 2026-09-30T21:10:52Z |  |
| https://developers.uniswap.org/docs/unichain/technical-information/advanced-txn.md | 200 | 2026-09-30T21:11:03Z |  |
| https://developers.uniswap.org/docs/unichain.md | 200 | 2026-09-30T21:11:03Z |  |
| https://developers.uniswap.org/docs/unichain/technical-information/network-information.md | 200 | 2026-09-30T21:11:07Z |  |
| https://developers.uniswap.org/whitepaper_unichain.pdf | 200 | 2026-09-30T21:11:08Z |  |
| http://web.archive.org/web/20260317122042/https://docs.unichain.org/docs/technical-information/advanced-txn | 403 | 2026-09-30T21:11:08Z | non-2xx response; body not stored |
| https://blog.uniswap.org/rollup-boost-is-live-on-unichain | 200 | 2026-09-30T21:11:08Z |  |
| https://blog.uniswap.org/flashblocks-are-live | 200 | 2026-09-30T21:11:09Z |  |
| https://writings.flashbots.net/introducing-rollup-boost | 200 | 2026-09-30T21:11:09Z |  |

### collect/

census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py (+ docs_urls.txt where used), token_prices.py, run_token_prices_all.sh, write_manifest.py and their logs (census.log, make_swap_topics.log, defillama.log, docs.log, token_prices.log). Identical copies of these scripts are in every sibling chain directory and in ../_shared_collect/.

## Coverage limits and gaps

* Single contiguous window per chain (60 min of chain time ending 2026-09-30T21:07:21Z); one weekday evening (UTC), no other days or times of day.
* Gap blocks (unfetchable after all retries): 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (per the shared definition): transaction input/calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are NOT collected. Priority fee actually paid per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces: internal native-token transfers (e.g. direct payments to the block builder / coinbase on Ethereum, native-ETH legs of Uniswap V4 or WETH unwraps) and revert reasons are not collected.
* Logs are stored only for candidate transactions (criteria A/B). Transactions with a single swap log and fewer than 3 ERC-20 transfers from 2 tokens are in txs-*.csv only (no logs). topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv; the match is on topic0 (plus the Ekubo log0 address rule) with no check of the emitting contract. Venues whose swap events use other signatures are not matched by A (e.g. Ambient/CrocSwap, RFQ/PMM venues such as Hashflow/Bebop/Native, 0x and 1inch limit orders, UniswapX fills, Bancor, Uniswap V1, Maverick V1, Trader Joe LB v2.0, GMX V2, KyberSwap classic, Clipper, Integral); such transactions appear as candidates only if they meet criterion B. A signature not observed in this window is listed with an empty verified_example_tx (not verified on this chain).
* ERC-20 Transfer is identified as topic0 0xddf252ad... with exactly 3 topics; tokens emitting non-standard transfer events and native-token movements are not counted for criterion B.
* Token metadata was read at block tag 'latest' shortly after the window, not at the window blocks. DefiLlama prices are DefiLlama's own aggregates (confidence field included) and are absent for tokens DefiLlama does not price.
* No mempool / pending-transaction data, no private-orderflow or bundle data, no flashblock / preconfirmation-level ordering data (block-level receipts only).
* The DefiLlama DEX overview was fetched once (2026-09-30T21:10:33Z) with default query parameters.
* docs: the former docs.unichain.org pages now redirect to developers.uniswap.org/docs/unichain; the Wayback Machine copy of the former advanced-txn page returned HTTP 403 through the proxy and was not stored (listed in docs/index.csv). Unichain Flashblocks and priority-ordering descriptions are taken from the current developer docs, the Unichain whitepaper PDF and Uniswap/Flashbots blog posts.
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana (separate collector in ../solana), and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) are not collected here.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 50 files (50 committed, 0 local-only). All 16 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. The row counts in 'Files, schemas, row counts' above and the candidate counts by criterion equal the verified counts below (no differences). Largest committed file: txs-001.csv.gz (1,441,318 bytes); no committed file exceeds 90 MB.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 187,562 | 3,600 rows + header | 0b9351db26a1c1aa777e3f06030167a56c36e2636df45d2b68ab2620ca5b93cc | committed |
| candidates-001.jsonl.gz | 193,589 | 339 JSON lines (criterion A 170, B 169) | 1e7cf63916cfab7d773f685b47dd7e17779ec56ba308895278705b789b93a06c | committed |
| collect/census.log | 2,168 | 9 lines | 78e3d798e0abff76b76177913fac27a9ac75700d61bef3d7c49b4b6cce5362f4 | committed |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| collect/defillama.log | 134 | 1 line | 1adf81b1370058b4af4fbaac45fe41f0a69841da3e955646bd42a6ab2d64f75e | committed |
| collect/docs.log | 1,713 | 12 lines | 70db25d311b9ffa71b3894dfd6b4e40a45b892d96faa48d96d73e63ebe93fb14 | committed |
| collect/docs_urls.txt | 785 | 11 lines | 90b5a6ebf2c77530ab033f0840d58d7cb084f63e3f894c022acb3d5edef1b4b4 | committed |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/make_swap_topics.log | 100 | 1 line | 66a2819d2aacd63ab1758d4414ec117a18dd42a8f81e4d755c35644d011a7323 | committed |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| collect/token_prices.log | 604 | 3 lines | bb0241adc6d72c77726f79c5caa630bb0929e927e08ebb01c1ba920f03050f2c | committed |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| defillama-dexs.fetch.json | 139 | 1 JSON document | 0df8c5298334dc8aae667631c52af24aee83f977ed9dc91c8ea74fc4c4378780 | committed |
| defillama-dexs.json | 100,466 | 1 JSON document | 9fcc787a05f0b6f54d81722ff15eecb3d6b744aa261237527bd459d8212b469a | committed |
| docs/blog.uniswap.org_flashblocks-are-live.html.gz | 36,812 | 88 lines (decompressed) | 24e4f279e0a8715545cd43e3fe126cf107f93b786b992d66a5b251e1368675ab | committed |
| docs/blog.uniswap.org_flashblocks-are-live.txt | 4,913 | 181 lines | 7b0c2cd6fb1e6a5ab21512446dfc52c44fc278c2b5e13008f40c384dfa0565ce | committed |
| docs/blog.uniswap.org_rollup-boost-is-live-on-unichain.html.gz | 38,172 | 99 lines (decompressed) | 8e0c1d8aa811fbc4812f670cd40768f1341d1e89f9c405dbb4f81b415d222256 | committed |
| docs/blog.uniswap.org_rollup-boost-is-live-on-unichain.txt | 6,158 | 203 lines | c65e5ab1f10eb7e00ac4a6d4a38fa4973f1e47f0fffc95a370a6d06fc534f9a3 | committed |
| docs/developers.uniswap.org_docs_unichain.md.raw.gz | 2,062 | 89 lines (decompressed) | 2c9f8a88ee79a3a6d1fde51b4ce1cdcdee25a860d20d3c7062f69e19e75698c9 | committed |
| docs/developers.uniswap.org_docs_unichain.md.txt | 6,141 | 95 lines | 4117cd2c66e08103483b6ca2fd2085bd3df68402534077d9c92e9ed791a8f96d | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_advanced-txn.html.gz | 56,531 | 548 lines (decompressed) | b2a2ff8d1ffb09693d225ec8d4455329245ba3f0b527d43a1c405bd7315748c9 | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_advanced-txn.md.raw.gz | 3,208 | 269 lines (decompressed) | 30b9e9858c29384c9deb8be0e46014d07f78dfd30ee5d496c3442d41d8011c1b | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_advanced-txn.md.txt | 10,320 | 275 lines | b167dad53cc4941b999225224f45771cff25a6577d8ae2352cdf9785ff2510df | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_advanced-txn.txt | 11,297 | 468 lines | a6c64d6b2bff306b76ac005fdff3d1e53353a50b0546d8f028bcfb256d513c8d | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_flashblocks.html.gz | 60,861 | 682 lines (decompressed) | e5a7de1fd81177700f485c51b10eefb52e4ea972f849d8c94f129ba5ca2061fc | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_flashblocks.md.raw.gz | 6,339 | 441 lines (decompressed) | c3a4b891e05b3ee7b2df28a91cfb532f8d5e4b16689baceed63c53f42b221fbc | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_flashblocks.md.txt | 20,548 | 447 lines | 005d7b251e0570568196ef18e16c2a196a5e795fffa82b8630b48eefd6b8f315 | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_flashblocks.txt | 20,378 | 617 lines | 53273f3d4b733dbce087943fb9fb329a215cf2316e8f6479776a42d52fc7d883 | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_network-information.md.raw.gz | 515 | 27 lines (decompressed) | d1d5acf722c5806ef20cc476ab178ee9a22c682b6f99d7f0a504069d8c7bdd39 | committed |
| docs/developers.uniswap.org_docs_unichain_technical-information_network-information.md.txt | 2,521 | 33 lines | b7f0b07f645e4589f512961fe0139750f63f652b025cca046c8dd6ccba677725 | committed |
| docs/developers.uniswap.org_whitepaper_unichain.pdf | 381,846 | PDF (binary) | 753ccaef33f5b4e0390107930ec5a94d5ad2eda7efce7f8e0e1d15a52ca4a32a | committed |
| docs/developers.uniswap.org_whitepaper_unichain.pdf.txt | 16,185 | 330 lines | d9138939809a58aa9ddc13c229809558c4e412cff2f4d91456f5fc79d3dffa61 | committed |
| docs/index.csv | 2,653 | 11 rows + header | edd8a618a3c15cc47a27ebee6e3334fc41b13ab82757a3d23d8c0f59f8338301 | committed |
| docs/writings.flashbots.net_introducing-rollup-boost.html.gz | 8,616 | 18 lines (decompressed) | 99d4994f70f9e6f0c2039123b7098cbb5ddd65af04e32aaf9481656abe838b63 | committed |
| docs/writings.flashbots.net_introducing-rollup-boost.txt | 11,971 | 147 lines | 40319b9c47492b82fb211b60376ce3e7d23b903f687ffd3c1a7c2c34faebfb3d | committed |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | committed |
| native-price-chart-defillama.json | 749 | 1 JSON document | b933a0d288c9272f866348094c52fe13f5c8a1d9f1e939036b717697d539b7e2 | committed |
| prices-defillama-historical.jsonl.gz | 1,312 | 3 JSON lines | 8c544eb84ef5c8712fdb43dcc59a07ca36e389438a18dfc9cb3fd9f961453869 | committed |
| reverted-001.csv.gz | 10,246 | 123 rows + header | b51c3b4e36ff067da607576a09aae3f403bd889b25f54edd1ca003028e0c6673 | committed |
| swap-topics.csv | 11,041 | 22 rows + header | 4e3d39ad52f70e3038a1e778fca17f46f0bae2a03738c7f0bb0547bf8daa9ea9 | committed |
| token_prices.fetch.json | 548 | 1 JSON document | 410006901a277e2f0e5b233f9d44c177eb4abff5e7eab0f9c253c1680c4f7b2f | committed |
| tokens-onchain-meta.csv.gz | 1,267 | 17 rows + header | fd1ef944147f06b79c3bd58708febb98235d7486786e9f4a83c0a8c5caf2ca68 | committed |
| topic0-counts.csv.gz | 13,057 | 164 rows + header | 11d3f5262d53ae05ddfecda92573cacd97223a6bbdad7d5c98894201faa87c0f | committed |
| txs-001.csv.gz | 1,441,318 | 30,272 rows + header | dd130c14912ee6ac762fd86ce56292bbb594d108cc0b4701c4468701d3be4906 | committed |
| window.json | 2,639 | 1 JSON document | 8db33fecd45d296475a72ab6ea321e479e14f743d04eb6ec6f52f2890d9c9807 | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
