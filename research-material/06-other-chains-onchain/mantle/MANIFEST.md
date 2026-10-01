# Mantle: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_MANTLE.DONE  mantle census complete 2026-10-01T04:19:38Z blocks 101347199-101348998 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/mantle
EVM_TOKENPRICES_MANTLE.DONE  mantle token meta + prices done 2026-10-01T04:20:16Z tokens=12
```

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md` and `research-material/README.md` section 2.

| Line | Files in this directory |
|---|---|
| 1 | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 4 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json, defillama-dexs.json, defillama-dexs.fetch.json |
| 5 | candidates-001.jsonl.gz (swap logs; Uniswap V4 PoolManager topic0 0x40e9cecb... where observed, see swap-topics.csv), blocks.csv.gz (base_fee_per_gas), txs-001.csv.gz (effective_gas_price), docs/ (incl. docs/excerpts.jsonl) |
| 6 | docs/ (incl. docs/excerpts.jsonl) |
| 7 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json |
| 8 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json |

`collect/` holds scripts and logs and is not mapped to a question line.

## Window (pinned)

| Item | Value |
|---|---|
| Chain id | 5000 |
| Block range (inclusive) | 101347199 to 101348998 (1800 blocks) |
| Block timestamps | 1790824710 (2026-10-01T03:18:30Z) to 1790828308 (2026-10-01T04:18:28Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 5 |
| Head at pin time | 101349003 (pinned 2026-10-01T04:18:41Z) |
| Measured block interval | 2.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:19:38Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://mantle-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 10 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://rpc.mantle.xyz`, `https://mantle.drpc.org`.
* Requests actually sent (HTTP): {"https://mantle-rpc.publicnode.com": 215, "https://mantle.drpc.org": 2}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {"https://mantle-rpc.publicnode.com|retry": 17, "https://mantle-rpc.publicnode.com|item-retry": 170, "https://mantle.drpc.org|retry": 2, "https://mantle.drpc.org|item-retry": 20}.
* DefiLlama: `https://api.llama.fi/overview/dexs/mantle` fetched 2026-10-01T04:19:07Z (HTTP 200, 379615 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:20:12Z) on https://mantle-rpc.publicnode.com, https://rpc.mantle.xyz (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `mantle:`) at ts = [1790824710, 1790826509, 1790828308] (3 requests) and `https://coins.llama.fi/chart/coingecko:mantle?start=1790824710&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 5000, "window_s": 3600, "end_tag": "latest", "head_margin": 5, "batch": 10, "seg_blocks": 300, "nominal_interval": 2.0, "sentinel": "EVM_CENSUS_MANTLE", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/mantle/collect
python3 -B make_swap_topics.py mantle .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain mantle --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py mantle ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain mantle --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py mantle .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py mantle ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 1800 | 93060 |
| txs-001.csv.gz | 2444 | 129708 |
| reverted-001.csv.gz | 47 | 4057 |
| candidates-001.jsonl.gz | 38 | 29509 |
| topic0-counts.csv.gz | 88 | 7193 |
| swap-topics.csv | 22 | 11136 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 12 | 954 |
| prices-defillama-historical.jsonl.gz | 3 | 1066 |
| native-price-chart-defillama.json | (JSON document) | 12 |
| defillama-dexs.json | (JSON document) | 379615 |
| defillama-dexs.fetch.json | (JSON document) | 137 |
| token_prices.fetch.json | (JSON document) | 539 |
| window.json | (JSON document) | 2836 |
| docs/excerpts.jsonl | 9 | 7700 |

Candidate counts by criterion: A = 19, B = 19. Transactions: 2444; status-0 transactions: 47; distinct topic0 keys: 88; receipts not in the block's transaction list: 0.

* **blocks.csv.gz** (one row per block, ascending): block_number, timestamp (unix s), base_fee_per_gas (wei), gas_used, gas_limit, tx_count (length of the block's transactions list), miner, extra_data (raw hex), block_hash, parent_hash, receipts_count (receipts returned by eth_getBlockReceipts).
* **txs-001.csv.gz** (one row per receipt, by block then tx_index): block_number, tx_index, tx_hash, from, to, status (1/0), gas_used, effective_gas_price (wei), type (base-10 integer), logs_count, contract_address, l1_fee (OP-stack receipt l1Fee, wei; '' where absent), gas_used_for_l1 / timeboosted (Arbitrum only; '' here), in_block_tx_list (derived: receipt hash is in the block's transactions list).
* **reverted-001.csv.gz**: every status-0 transaction; block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, logs_count, type, l1_fee, gas_used_for_l1, timeboosted.
* **candidates-001.jsonl.gz** (one JSON object per candidate tx). Criterion A: >= 2 logs whose topic0 is in swap-topics.csv (or zero-topic logs from a match_rule=log0_address address). Criterion B (only if not A): >= 3 logs with topic0 0xddf252ad... and exactly 3 topics, emitted by >= 2 distinct contracts. No pool/factory allow-list. Fields: block_number, block_timestamp, tx_index, tx_hash, from, to, status, gas_used, effective_gas_price, criterion, derived {n_logs, n_swap_logs, swap_keys_matched, n_erc20_transfer_logs, n_distinct_transfer_tokens}, receipt (every receipt field except logs, verbatim), logs (all logs of the tx, verbatim).
* **topic0-counts.csv.gz** (logs of all txs in the window): topic0_or_log0_emitter, n_logs, n_txs, n_distinct_emitting_addresses, first_example_tx, first_example_block, first_example_log_address, in_known_swap_topics.
* **swap-topics.csv**: topic0, signature, protocol, source_url, verified_example_tx (first log with this topic0 in the window; empty = not observed, i.e. not verified on this chain), match_rule, match_address, verified_example_block, verified_example_log_address, verification_note, topic0_tool.
* **gaps.csv**: block_number, reason (header only = no gap).
* **window.json**: pinned window, config, endpoints, counts, files, integrity checks, request and error counts.
* **tokens-onchain-meta.csv.gz**: one row per contract that emitted a Transfer log (topic0 0xddf252ad..., 3 topics) inside a candidate tx: token_address, n_transfer_logs_in_candidates, decimals_raw, symbol_raw, name_raw, decimals_error, symbol_error, name_error, call_block_tag ('latest'), call_endpoint, decimals_derived, symbol_derived, name_derived.
* **prices-defillama-historical.jsonl.gz**: one JSON line per DefiLlama coins request (url, fetched_at_utc, http_status, timestamp_requested, response = raw body) at the window start, middle and end timestamps. **native-price-chart-defillama.json**: raw 5-minute chart of the native gas token across the window. **token_prices.fetch.json**: run metadata.
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/mantle` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0x77060c4e3fac5cc84494081a081e9d101ef41ebad7fbd13ff38a079b2296077e |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0xa5985ef83aabb0f843b60af1ff51def10dcbc1c8bfd2c8300d84bb60e15ea127 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0x0488fc95995625c96d594c229e914c0f2a6ef822c3f57f648ba035c05e1bf1c4 |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | no |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | no |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | no |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | no |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | no |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | no |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | no |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | no |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | yes: 0x0488fc95995625c96d594c229e914c0f2a6ef822c3f57f648ba035c05e1bf1c4 |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | no |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | no |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | no |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | no |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | no |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | no |

### docs/ (official documentation on ordering / sequencer)

| URL | HTTP | fetched (UTC) | note |
|---|---|---|---|
| https://docs.mantle.xyz/network/system-information/architecture.md | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.mantle.xyz/network/system-information/fee-mechanism.md | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.mantle.xyz/network/system-information/fee-mechanism/eip-1559-support.md | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.mantle.xyz/network/system-information/fee-mechanism/fee-model-handbook-after-arsia.md | 200 | 2026-10-01T04:22:48Z |  |
| https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment.md | 200 | 2026-10-01T04:22:48Z |  |
| https://docs.mantle.xyz/network/system-information/off-chain-system/node-introduction.md | 200 | 2026-10-01T04:22:49Z |  |
| https://docs.mantle.xyz/network/for-node-operators/network-roles.md | 200 | 2026-10-01T04:22:49Z |  |
| https://docs.mantle.xyz/network/system-information/transaction-lifecycle.md | 200 | 2026-10-01T04:22:50Z |  |
| https://docs.mantle.xyz/network/system-information/risk-management/forced-transaction-inclusion.md | 200 | 2026-10-01T04:22:51Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| mantle-01 | https://docs.mantle.xyz/network/system-information/architecture.md | 2026-10-01T04:22:46Z | 1. Users send signed transactions to Mantle through RPC nodes, which forward them to the sequencer for processing. 2. The sequencer orders incoming transactions ... |
| mantle-02 | https://docs.mantle.xyz/network/system-information/architecture.md | 2026-10-01T04:22:46Z | In Mantle v2, a transaction pool structure similar to Ethereum's mempool is introduced for the temporary storage of transactions until they are included in a bl ... |
| mantle-03 | https://docs.mantle.xyz/network/system-information/fee-mechanism.md | 2026-10-01T04:22:47Z | * **For** [**EIP-1559 transaction types**](/network/more/glossary.md#eip-1559-transaction), L2 gasPrice is affected by the `GasTipCap` parameter, which is a par ... |
| mantle-04 | https://docs.mantle.xyz/network/system-information/fee-mechanism.md | 2026-10-01T04:22:47Z | The ordering of transactions is influenced by various factors. Here are examples illustrating the role of `GasTipCap` and transaction submission order: 1. Suppo ... |
| mantle-05 | https://docs.mantle.xyz/network/system-information/fee-mechanism/eip-1559-support.md | 2026-10-01T04:22:47Z | Mantle v2 Tectonic, in an effort to further reduce fees, chose the [FIFO](https://en.wikipedia.org/wiki/FIFO) method of transaction sequencing to minimize the i ... |
| mantle-06 | https://docs.mantle.xyz/network/system-information/fee-mechanism/fee-model-handbook-after-arsia.md | 2026-10-01T04:22:48Z | With the Arsia upgrade, Mantle restores a full EIP-1559 execution fee model. The L2 base fee responds dynamically to block utilization, while priority fees are  ... |
| mantle-07 | https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment.md | 2026-10-01T04:22:48Z | 3. **Dynamic EIP-1559 parameters** -- The base fee is no longer a fixed value. Arsia enables the sequencer to adjust EIP-1559 curve parameters (denominator, ela ... |
| mantle-08 | https://docs.mantle.xyz/network/for-node-operators/network-roles.md | 2026-10-01T04:22:49Z | are responsible for sequentially packing transactions into layer-2 blocks, providing a deterministic order for transactions. Currently, Sequencer nodes are not  ... |
| mantle-09 | https://docs.mantle.xyz/network/system-information/risk-management/forced-transaction-inclusion.md | 2026-10-01T04:22:51Z | When the transaction is submitted on L1, it will be processed on a First Come, First Served (FCFS) basis, along with some [inclusion rules](https://docs.optimis ... |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 423, 2: 213, 4: 8, 126: 1,800.
* `miner` values in blocks.csv.gz (blocks): 0x4200000000000000000000000000000000000011: 1,800.
* Stack: Mantle v2 (OP Stack based; docs/ excerpts mantle-01 to mantle-09). Gas token: MNT. `base_fee_per_gas`, `effective_gas_price` and `l1_fee` are in MNT wei; the native-token chart was requested for `coingecko:mantle`.
* Receipts carry, in addition to the OP Stack fields, `tokenRatio`, `operatorFeeConstant` and `operatorFeeScalar` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).
* `l1_fee` is empty for the type-126 (0x7e deposit) rows of txs-001.csv.gz (the RPC returns no l1Fee for them).

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:30Z to 2026-10-01T04:18:28Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:20:12Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:07Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:44Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 93,060 | 1,800 rows + header | dffe08dacb33a91f0e244c719b4074fc301f75429e6f19cb2cd3300f887bf7fc | not ignored |
| candidates-001.jsonl.gz | 29,509 | 38 JSON lines | 7604c0406529932d5941aecb186d194cf70980163a2df65fb73128c9186a78e4 | not ignored |
| collect/census.log | 3,045 | 9 lines | d8798c9e30d5a18585f32f9c816afbb8f0b3598f41147d8105e750ec78eae234 | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 132 | 1 line | d6c16336f343f7191bafa64466b76bebb7a4b9c39c7bfdbc83ccdc1d79f859a6 | not ignored |
| collect/docs.log | 1,584 | 9 lines | 2d269843c7ace8ca94f7d9400e0f414ca0dff19f26cfa38196494e6e36644aee | not ignored |
| collect/docs_excerpts_spec.json | 2,098 | 1 JSON document | 8dfd1a0855ed5926edd0137ab71ea5b19cb2236445266a4f2d523ea88c4a091d | not ignored |
| collect/docs_urls.txt | 774 | 9 lines | 5342992eb79ca7321b5ed404c3c6728eaec9a0396629dafe87ff93ff471b2e69 | not ignored |
| collect/excerpts.log | 105 | 1 line | b25c411379f7ae77921b185b4af0bbe069c814a2dadff9444efea2a7fa9b3a75 | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.log | 595 | 3 lines | 47ef459743ace10beda3040ddf698254412b2c294d051a3efac94b6ae450e526 | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 137 | 1 JSON document | f2f6b2a57b788b4cccfc31a62b1f750d08713271b73a711a9262dfb7e125948a | not ignored |
| defillama-dexs.json | 379,615 | 1 JSON document | 801d89f05ebde4491e46f28ef10b9ae1800625244b67a50bea4ef0d9922bc691 | not ignored |
| docs/docs.mantle.xyz_network_for-node-operators_network-roles.md.raw.gz | 1,238 | 34 lines (decompressed) | 7ce4bea3af68c474ec31042858b72d724f2915e3d4ec1418b74e29829e852999 | not ignored |
| docs/docs.mantle.xyz_network_for-node-operators_network-roles.md.txt | 3,868 | 40 lines | 98e164f0f2864a428d41a202e35736cb1b1da104b71b604bca89eb267cfc1c07 | not ignored |
| docs/docs.mantle.xyz_network_introduction_updated-notices_arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment.md.raw.gz | 2,912 | 91 lines (decompressed) | 8dc2f2b3475f0b36d65785737c50fc163055c2d31e6b63fbd26d26cf0f8fb76b | not ignored |
| docs/docs.mantle.xyz_network_introduction_updated-notices_arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment.md.txt | 7,312 | 97 lines | ea76405e4882344305634f84d6eb4e3fac36e271feb081b8fae5280862759236 | not ignored |
| docs/docs.mantle.xyz_network_system-information_architecture.md.raw.gz | 1,650 | 26 lines (decompressed) | 2ae445657a69326833b9ec337e7fb4330943a78fc68c700fbd9bb2454fd9e76e | not ignored |
| docs/docs.mantle.xyz_network_system-information_architecture.md.txt | 3,880 | 32 lines | 49b2e6bac948fa700c95c9571eb8e10f1f0cded8607d1ea4e1cd9e3494b982a0 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism.md.raw.gz | 4,601 | 151 lines (decompressed) | 26b001a32b4d498ea2240329ba84f67b58aea5cc8b58f3481fbc677cf7b030d3 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism.md.txt | 14,059 | 157 lines | 5ce403bf9d36ce11bc5706b11699b65641d6a4def60057527aa05627c65e28c5 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism_eip-1559-support.md.raw.gz | 1,794 | 34 lines (decompressed) | 69b2cdec2fc53eb936518566de562a988fd0493538771c7f82ae391aae37f0c8 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism_eip-1559-support.md.txt | 4,512 | 40 lines | bcd844a85d718ac962c32418b94a6393e4698d45295129d85521a7277666ce42 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism_fee-model-handbook-after-arsia.md.raw.gz | 4,921 | 142 lines (decompressed) | 4b4e6d143fb3d9f44a31c471af428b02f8134ac5ba01f32134dc918405c52189 | not ignored |
| docs/docs.mantle.xyz_network_system-information_fee-mechanism_fee-model-handbook-after-arsia.md.txt | 14,483 | 148 lines | ff2a36a988a04e2c40a9a1b1556821054c6ba02f030a05f7d1748300d26c4d0f | not ignored |
| docs/docs.mantle.xyz_network_system-information_off-chain-system_node-introduction.md.raw.gz | 1,335 | 58 lines (decompressed) | 8d3256df2d47ae8573c1d8d780d7e60f82406600c6e61c052c555223ff74c116 | not ignored |
| docs/docs.mantle.xyz_network_system-information_off-chain-system_node-introduction.md.txt | 4,289 | 64 lines | 35cb52ec94de0dadf56a6b12b4b547ee4e98c0f0eafb524d7a4076b0c2b2b4ea | not ignored |
| docs/docs.mantle.xyz_network_system-information_risk-management_forced-transaction-inclusion.md.raw.gz | 1,427 | 25 lines (decompressed) | f71c5fb07033390178370224dd4fb23b2f2b2366d07f56f3c28e815dd5ebaa4c | not ignored |
| docs/docs.mantle.xyz_network_system-information_risk-management_forced-transaction-inclusion.md.txt | 4,062 | 31 lines | 31e468b23fc547c3c53709b3f36b3c2146a23943bbd5f8f40beb81457dc604a2 | not ignored |
| docs/docs.mantle.xyz_network_system-information_transaction-lifecycle.md.raw.gz | 1,995 | 47 lines (decompressed) | 87634ec98e9cec274f53969a17f8159a4e198c20d03bdd4a7967426abc79c8a9 | not ignored |
| docs/docs.mantle.xyz_network_system-information_transaction-lifecycle.md.txt | 4,920 | 53 lines | 52b681d205aed218516905081f58e5f224c1a152a6c1b86e67fda6c8a3ca04c9 | not ignored |
| docs/excerpts.jsonl | 7,700 | 9 JSON lines | 7f0d01a36b2ff8219179bc1e1c46bf9a6de1648245ff5414a751050508cd093f | not ignored |
| docs/index.csv | 2,550 | 9 rows + header | b0463b75720349c9b40676a7b561b8077fd98445dd1a95f705500871973e4279 | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 12 | 1 JSON document | 1502993ba9216cef597f89ad89349018d3a751d37d6c1ef81ebf29460ce48785 | not ignored |
| prices-defillama-historical.jsonl.gz | 1,066 | 3 JSON lines | 89c63a75cb893514085339d1ab1939d52e4d33d635ce85ec03ae1f00ad70578f | not ignored |
| reverted-001.csv.gz | 4,057 | 47 rows + header | 65b4ea35048469f231e89bc30619117cb5f50f07684a43eb9911325621955309 | not ignored |
| swap-topics.csv | 11,136 | 22 rows + header | d3a123ac258cec6ebed2f0849c7716c904d6ba461e77c1b8ef28c2ac6a4237e9 | not ignored |
| token_prices.fetch.json | 539 | 1 JSON document | b5b3d9d616f3d6095b9b0ee9b7f4287420eeae4a0c1d0dd43c582b9b04af9d61 | not ignored |
| tokens-onchain-meta.csv.gz | 954 | 12 rows + header | b915456d9b0c78cb8400016ad1d505f35171203bfd139ba89b9a6f9ace01f580 | not ignored |
| topic0-counts.csv.gz | 7,193 | 88 rows + header | 95cfec089616fcf33d431dfac68437ef3a4151b87080232ea465ba4014ccd9ce | not ignored |
| txs-001.csv.gz | 129,708 | 2,444 rows + header | 045a88df677426d064a4e30aea8bf67ed2e9e00c9c9ed49aaf8742c0dd3c8fbb | not ignored |
| window.json | 2,836 | 1 JSON document | 319712a9c62002ece84c39f38138af1790e7d4890830d17571c84aa74fcba9a4 | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 54 plus this MANIFEST.md. Largest file: 379,615 bytes (limit 90 MB).
