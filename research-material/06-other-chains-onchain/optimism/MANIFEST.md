# OP Mainnet (Optimism): on-chain arbitrage census (raw material)

Status: COMPLETE (finalized 2026-10-01). All collectors for this directory finished: sentinels EVM_CENSUS_OPTIMISM.DONE and EVM_TOKENPRICES_OPTIMISM.DONE (sentinel files are git-ignored; their text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:21Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): census COMPLETE (sentinel `.sentinels/EVM_CENSUS_OPTIMISM.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_OPTIMISM.DONE`). Ordering docs: COMPLETE (see docs/).

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
| Chain id | 10 |
| Block range (inclusive) | 157600033 to 157601832 (1800 blocks) |
| Block timestamps | 1790798843 (2026-09-30T20:07:23Z) to 1790802441 (2026-09-30T21:07:21Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 5 |
| Head at pin time | 157601837 (pinned 2026-09-30T21:07:32Z) |
| Measured block interval | 2.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-09-30T21:07:59Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://optimism-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 2 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://optimism.drpc.org`.
* Requests actually sent (HTTP): {"https://optimism-rpc.publicnode.com": 900}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/optimism` fetched 2026-09-30T21:10:31Z (HTTP 200, 847743 bytes), stored unmodified as defillama-dexs.json.
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-09-30T21:13:11Z) on https://optimism-rpc.publicnode.com, https://optimism.drpc.org. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = [1790798843, 1790800642, 1790802441] and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790798843&span=13&period=5m`.
* Official docs: see docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/optimism/collect
python3 make_swap_topics.py optimism ..            # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 census.py --chain optimism --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 fetch_defillama.py optimism ../defillama-dexs.json > defillama.log 2>&1
python3 token_prices.py --chain optimism --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)
python3 fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 write_manifest.py optimism ..               # regenerates this file from the metadata files
```

Note (2026-10-01): this MANIFEST.md was edited by hand during finalization (status line, 'Question lines served', the 'Verified inventory (2026-10-01)' section and the notes marked 2026-10-01). Re-running write_manifest.py would regenerate the collector's original version without these edits.

Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 1800 | 106833 |
| txs-001.csv.gz | 62920 | 3625454 |
| reverted-001.csv.gz | 1196 | 86532 |
| candidates-001.jsonl.gz | 18058 | 18008601 |
| topic0-counts.csv.gz | 714 | 58888 |
| swap-topics.csv | 22 | 12008 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 215 | 13890 |
| prices-defillama-historical.jsonl.gz | 18 | 10025 |
| native-price-chart-defillama.json | (JSON document) | 749 |
| defillama-dexs.json | (JSON document) | 847743 |
| defillama-dexs.fetch.json | (JSON document) | 139 |
| token_prices.fetch.json | (JSON document) | 550 |
| window.json | (JSON document) | 2614 |

Candidate counts by criterion: A = 4914, B = 13144. Transactions: 62920; status-0 transactions: 1196; distinct topic0 keys: 714.

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
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xdc442d705521f332e0190a72ad2f2b83c76f2d466ce79d5904e9b86a5fe76341 |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0xc40d088dfcdfdd82726d9ecf6484b3ededf5164676303e03f52e8a5b84b67f88 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0x6a1ab563b2d0220664a0199757a60e0e3078d991c38627c74e74043e1ec38425 |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | yes: 0xde3657778d786327bdbe364d2536f16a5f71dd404bd86fba8d77fabde82cad6c |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x2c8222435b442952752a929ab34400737b0db5a629f9c5c4afec18feb5059cec |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | yes: 0x8c051e29579bba3737e3adc5f9760335be2e25c59697df3e56cfede8edb9fd7b |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | yes: 0x4278736fb31848a0ba85eb25ab63185609ef159cd4df8398771b04bac2007ea5 |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | yes: 0x17cf59d6a6937697448a218439a56e95ee50d42895e449fb6b8f5e91164bb10b |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | yes: 0xb92cfb2b2943718476b89d83ddbba18685a8e93aacb53dea3a140d96bc160abc |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | yes: 0xea25fa4f6cb016130046501f4efb07db55ffc305dde51a30e2fc363c34c27e00 |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | yes: 0x17cf59d6a6937697448a218439a56e95ee50d42895e449fb6b8f5e91164bb10b |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | no |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | no |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | no |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | yes: 0x666ac9d92128f2a4da995f98448d89a43f4c44b57fa26ad9ca1b0a4c1912be56 |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | no |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | yes: 0x08a5ad2896b2db6f6af399dea65efda9e82a9bc963cf6236b1f60d3a3c705040 |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | no |

### tokens-onchain-meta.csv.gz

One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).

### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json

One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.

### defillama-dexs.json

Raw response of `https://api.llama.fi/overview/dexs/optimism` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.

### docs/

Official documentation on transaction ordering, fetched verbatim. For each URL: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION method, then the full visible text or raw markdown), plus the raw body (`.html.gz`, `.raw.gz` for markdown, or `.pdf`). `index.csv` lists every URL attempted.

| URL | HTTP | fetched (UTC) | note |
|---|---|---|---|
| https://docs.optimism.io/op-stack/transactions/fees | 200 | 2026-09-30T21:11:10Z |  |
| https://docs.optimism.io/op-stack/transactions/transaction-flow | 200 | 2026-09-30T21:11:11Z |  |
| https://docs.optimism.io/op-stack/protocol/differences | 200 | 2026-09-30T21:11:11Z |  |
| https://docs.optimism.io/chain-operators/guides/management/transaction-fees-101 | 200 | 2026-09-30T21:11:12Z |  |
| https://specs.optimism.io/protocol/overview.html | 200 | 2026-09-30T21:11:12Z |  |
| https://optimism.io/blog/flashblocks-deep-dive-250ms-preconfirmations-on-op-mainnet | 200 | 2026-09-30T21:11:13Z |  |
| https://www.optimism.io/blog/optimism-partners-with-flashbots | 200 | 2026-09-30T21:11:14Z |  |
| https://raw.githubusercontent.com/flashbots/rollup-boost/main/specs/flashblocks.md | 200 | 2026-09-30T21:11:15Z |  |

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
* The DefiLlama DEX overview was fetched once (2026-09-30T21:10:31Z) with default query parameters.
* docs: github.com blob pages returned HTTP 403; the rollup-boost flashblocks spec was taken from raw.githubusercontent.com instead.
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana (separate collector in ../solana), and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) are not collected here.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 46 files (46 committed, 0 local-only). All 15 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. The row counts in 'Files, schemas, row counts' above and the candidate counts by criterion equal the verified counts below (no differences). Largest committed file: candidates-001.jsonl.gz (18,008,601 bytes); no committed file exceeds 90 MB.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 106,833 | 1,800 rows + header | 437b57278a25111a9b16896df3262149f1079d448c90a7c650d135a53f2b360d | committed |
| candidates-001.jsonl.gz | 18,008,601 | 18,058 JSON lines (criterion A 4,914, B 13,144) | c11f8f089d4a084af8ae5619765bd102861fbe39d5142afc49c7fd93a9280927 | committed |
| collect/census.log | 2,181 | 9 lines | 3a128afe7390153cd27d17facd452afe3073a14bab92786b0197d5062d50fe77 | committed |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| collect/defillama.log | 134 | 1 line | e7f38b3ca80c9ada23938b1022e39f282fd098f0d82c6fb034a2276ccdd7dbf1 | committed |
| collect/docs.log | 1,086 | 8 lines | b618fb9bd9e789093310759910a3a84845e814017dc03c4a55b8b775613c6785 | committed |
| collect/docs_urls.txt | 529 | 8 lines | 8724566c475932061cdfe25cb0c71af3c9ba9850763d8b13c8cf896cc75c7ba2 | committed |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/make_swap_topics.log | 100 | 1 line | b7c06c2f021eb5cd4ea456e706672915bf4e145e3c1bec7e5016799e0e720796 | committed |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| collect/token_prices.log | 607 | 3 lines | b087a21664f4ea4ce3256532dd31ef8ef5c2b3cfa34814901598d4e3eb7008a9 | committed |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| defillama-dexs.fetch.json | 139 | 1 JSON document | 96fa7e70f5850f2b3cb7304908a90c19ca4b9a43cade9354b137e21dc9396a98 | committed |
| defillama-dexs.json | 847,743 | 1 JSON document | 6155139e8be4b4f954423cec9155457bc1b4e548dc2b7f01fd31b0fef117a986 | committed |
| docs/docs.optimism.io_chain-operators_guides_management_transaction-fees-101.html.gz | 60,118 | 1,654 lines (decompressed) | 07476922ff65a0489faaf981fcd70157aa0c1c7f8f106fcf4baaef63707a53d5 | committed |
| docs/docs.optimism.io_chain-operators_guides_management_transaction-fees-101.txt | 11,892 | 499 lines | 4beaeb73dc13cc18ddf21b8455cfed3dda16de3a1c30a467ab470e1092756047 | committed |
| docs/docs.optimism.io_op-stack_protocol_differences.html.gz | 54,557 | 1,502 lines (decompressed) | 05837d49c9ed01ee6c48af303cfa7df5ff3d33717a1e4525696abac765ad9c15 | committed |
| docs/docs.optimism.io_op-stack_protocol_differences.txt | 8,888 | 300 lines | d7b9239f9187a89986da6a173d1f67958cac9ed7de7857a97411b4fe3e29dfa9 | committed |
| docs/docs.optimism.io_op-stack_transactions_fees.html.gz | 63,972 | 1,642 lines (decompressed) | 266d6b136882cad22206bc5e3244a8c68f91680619e320695804379e9f5be215 | committed |
| docs/docs.optimism.io_op-stack_transactions_fees.txt | 18,468 | 511 lines | 1ce1eac67696918437eacd1cb378747885f463957ecbfa54c844d747531052e1 | committed |
| docs/docs.optimism.io_op-stack_transactions_transaction-flow.html.gz | 56,872 | 1,539 lines (decompressed) | 975d5e2aca1840953c2aaa2157a83b942627122c90f82fbfd9620fb73ecbb0b1 | committed |
| docs/docs.optimism.io_op-stack_transactions_transaction-flow.txt | 7,715 | 314 lines | 38fe3f875d3ff64f43b05c6cc00bd6b9003d9be0fcb8b801164f4ba67c7616b7 | committed |
| docs/index.csv | 1,792 | 8 rows + header | 44ab0a4e87d508d24635196019dfefb0e2b9caa21f87b44fbdfc2fadffa361ae | committed |
| docs/optimism.io_blog_flashblocks-deep-dive-250ms-preconfirmations-on-op-mainnet.html.gz | 31,776 | 0 lines (decompressed) | 5db59befa2978a8187a0590632ac3463d4414cb66bca8f8c54a234b764944097 | committed |
| docs/optimism.io_blog_flashblocks-deep-dive-250ms-preconfirmations-on-op-mainnet.txt | 13,873 | 297 lines | eae242d22f4f05323be93ce6c2563efd1723ad51ffb9430547151566e5f894a6 | committed |
| docs/raw.githubusercontent.com_flashbots_rollup-boost_main_specs_flashblocks.md.raw.gz | 19,365 | 1,071 lines (decompressed) | c2d2f74477dd756a68f4f113c193886a36d26a4d5e12d4a2a65326a90b2aff10 | committed |
| docs/raw.githubusercontent.com_flashbots_rollup-boost_main_specs_flashblocks.md.txt | 61,830 | 1,077 lines | c75c7e42eed20b51f1eae0d47c1a641c07cb2241d95f35dd1b5acb0b68fa0ba3 | committed |
| docs/specs.optimism.io_protocol_overview.html.html.gz | 11,548 | 683 lines (decompressed) | 85070e87aec56e8f761e05d64515f03d082b2800d2d88fcac0a808a8255c4ca0 | committed |
| docs/specs.optimism.io_protocol_overview.html.txt | 26,328 | 552 lines | 7d687ad8a333b35485595a8ef172f81c6983daebc61d0cd18bf36da899955309 | committed |
| docs/www.optimism.io_blog_optimism-partners-with-flashbots.html.gz | 22,270 | 0 lines (decompressed) | 970a8011b9407fd281c29e7d97aff40b8f074f3f8de0a6982dab2ee27d04f375 | committed |
| docs/www.optimism.io_blog_optimism-partners-with-flashbots.txt | 6,852 | 220 lines | bc23760482f2dc770808a8e342f544383d41fa817cae864706f3453c1730621d | committed |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | committed |
| native-price-chart-defillama.json | 749 | 1 JSON document | b933a0d288c9272f866348094c52fe13f5c8a1d9f1e939036b717697d539b7e2 | committed |
| prices-defillama-historical.jsonl.gz | 10,025 | 18 JSON lines | 30c50dad43917d1077e360d142267cbb7317cee97f2e9f4e87cd4d4bb542fd08 | committed |
| reverted-001.csv.gz | 86,532 | 1,196 rows + header | 76b9e0dd7cd2e6f346d261fbcac24a815dc61f67f73e67a75432536c6b6b76a3 | committed |
| swap-topics.csv | 12,008 | 22 rows + header | 442d6982349d70de4fe71793cad2b5f8906020e1eb68e6dd37aa7e7715d4d1d7 | committed |
| token_prices.fetch.json | 550 | 1 JSON document | 6fbff94e7ff243befbc969fc26d4eb405cb9e740f0f65ec4cf9596e7ea39be98 | committed |
| tokens-onchain-meta.csv.gz | 13,890 | 215 rows + header | 4e94d211d462698bc570e0a5eb7125fd4a3abe15d90493d3c94bfbea2515c3b1 | committed |
| topic0-counts.csv.gz | 58,888 | 714 rows + header | ebd9b5abf9033fcf16f97bfd6ca7340f1859f823bc30ec5f536dbe295fc67472 | committed |
| txs-001.csv.gz | 3,625,454 | 62,920 rows + header | 619f2adbd778f0ddb80a890b36fa7c197ff0f13212c6f38d2d2958dbf526f2a4 | committed |
| window.json | 2,614 | 1 JSON document | 2fe9e075769fa2f94101798ad5dc79379d36df9cb143d0eee48f917bf66b1574 | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
