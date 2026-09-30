# Unichain: on-chain arbitrage census (raw material)

Status: census COMPLETE (sentinel `.sentinels/EVM_CENSUS_UNICHAIN.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_UNICHAIN.DONE`). Ordering docs: COMPLETE (see docs/).

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Question-line IDs are defined in `../MANIFEST-evm.md` (verbatim user text there).

| File(s) | Question lines |
|---|---|
| blocks.csv.gz, txs-*.csv.gz, reverted-*.csv.gz, candidates-*.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, window.json | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-STUDIES |
| candidates-*.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz base_fee_per_gas + txs effective_gas_price (priority fee per gas = effective_gas_price - base_fee_per_gas, derivable) | Q-V4LAUNCH (priority-fee share line), Q-GAPS |
| candidates-*.jsonl.gz (all pools active in the window, any pool age / size) + tokens-onchain-meta.csv.gz | Q-OLDV2, Q-SMALLPOOLS (as observed on this chain, not Base) |
| docs/ (official ordering documentation) | Q-BSCORDER (comparison material: ordering policy on this chain), Q-V4LAUNCH (priority-fee ordering) |
| tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json | USD valuation inputs for Q-STUDIES / Q-OTHERCHAINS |
| defillama-dexs.json | Q-OTHERCHAINS (which DEXes exist on the chain and their reported volume; for checking swap-topic coverage) |

Not served here: Q-V4BASE (Base only; see the Base directories under research-material/, e.g. 01-v4-pools and 05-base-onchain).

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
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana, and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in docs/ANALYSIS.md 4.1) are not collected here.
