# Abstract: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_ABSTRACT.DONE  abstract census complete 2026-10-01T04:19:21Z blocks 86310808-86315526 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/abstract
EVM_TOKENPRICES_ABSTRACT.DONE  abstract token meta + prices done 2026-10-01T04:20:22Z tokens=24
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
| Chain id | 2741 |
| Block range (inclusive) | 86310808 to 86315526 (4719 blocks) |
| Block timestamps | 1790824713 (2026-10-01T03:18:33Z) to 1790828312 (2026-10-01T04:18:32Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 10 |
| Head at pin time | 86315536 (pinned 2026-10-01T04:18:42Z) |
| Measured block interval | 0.762823 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:19:21Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://api.mainnet.abs.xyz` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 10 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://abstract.drpc.org`.
* Requests actually sent (HTTP): {"https://api.mainnet.abs.xyz": 472}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/abstract` fetched 2026-10-01T04:19:10Z (HTTP 200, 134460 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:20:19Z) on https://api.mainnet.abs.xyz, https://abstract.drpc.org (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `abstract:`) at ts = [1790824713, 1790826512, 1790828312] (3 requests) and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790824713&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 2741, "window_s": 3600, "end_tag": "latest", "head_margin": 10, "batch": 10, "seg_blocks": 600, "nominal_interval": 0.75, "sentinel": "EVM_CENSUS_ABSTRACT", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/abstract/collect
python3 -B make_swap_topics.py abstract .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain abstract --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py abstract ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain abstract --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py abstract .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py abstract ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 4719 | 253818 |
| txs-001.csv.gz | 6416 | 391369 |
| reverted-001.csv.gz | 21 | 2173 |
| candidates-001.jsonl.gz | 385 | 303159 |
| topic0-counts.csv.gz | 177 | 14378 |
| swap-topics.csv | 22 | 11132 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 24 | 1826 |
| prices-defillama-historical.jsonl.gz | 3 | 1489 |
| native-price-chart-defillama.json | (JSON document) | 747 |
| defillama-dexs.json | (JSON document) | 134460 |
| defillama-dexs.fetch.json | (JSON document) | 139 |
| token_prices.fetch.json | (JSON document) | 540 |
| window.json | (JSON document) | 2600 |
| docs/excerpts.jsonl | 5 | 3771 |

Candidate counts by criterion: A = 62, B = 323. Transactions: 6416; status-0 transactions: 21; distinct topic0 keys: 177; receipts not in the block's transaction list: 0.

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
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/abstract` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0x5e41f36034809fcaeec4e45ba12b408eb57b783d80f42849ee38971e9b69a21b |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x90c9f971a5782567664ab17c37334e0f6a9c3b34a59be312ce4331e2b06fb035 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | no |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | yes: 0x1e156d7ca37de43679ec8902002a2ba9013c00429850db3b2296cdbc4960d017 |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | no |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | no |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | no |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | no |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | no |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | no |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | yes: 0xd80fca0e678c8cfcc312bba3596959476c785860171faf498d97cb4735f47043 |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | no |
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
| https://docs.abs.xyz/how-abstract-works/architecture/components/sequencer.md | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.abs.xyz/how-abstract-works/architecture/transaction-lifecycle.md | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.abs.xyz/how-abstract-works/evm-differences/gas-fees.md | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.abs.xyz/how-abstract-works/system-contracts/list-of-system-contracts.md | 200 | 2026-10-01T04:33:14Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| abstract-01 | https://docs.abs.xyz/how-abstract-works/architecture/components/sequencer.md | 2026-10-01T04:22:46Z | The sequencer is composed of several services that work together to receive and process transactions on the L2, organize them into blocks, create transaction ba ... |
| abstract-02 | https://docs.abs.xyz/how-abstract-works/architecture/components/sequencer.md | 2026-10-01T04:22:46Z | Once transactions are received through the RPC API, the sequencer processes them, organizes them into blocks, and ensures they comply with the constraints of th ... |
| abstract-03 | https://docs.abs.xyz/how-abstract-works/architecture/transaction-lifecycle.md | 2026-10-01T04:22:47Z | The transaction is executed and soft confirmation is provided back to the user about the execution of their transaction (i.e. if their transaction succeeded or  ... |
| abstract-04 | https://docs.abs.xyz/how-abstract-works/evm-differences/gas-fees.md | 2026-10-01T04:22:47Z | \| **Fee Composition** \| Entirely onchain, consisting of base fee and priority fee. \| Split between offchain (fixed) and onchain (variable) components. \| |
| abstract-05 | https://docs.abs.xyz/how-abstract-works/system-contracts/list-of-system-contracts.md | 2026-10-01T04:33:14Z | This contract holds the balances of ETH for all accounts on the L2 and updates them whenever other system contracts such as the [Bootloader](/how-abstract-works ... |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 134, 2: 586, 113: 5,696.
* `miner` values in blocks.csv.gz (blocks): 0x0000000000000000000000000000000000000000: 4,719.
* Stack: ZK Stack chain using EraVM (docs/ excerpt abstract-01; docs/ sequencer page links the matter-labs/zksync-era repository). Gas token: ETH.
* Transaction types in txs-001.csv.gz include 113 (= 0x71, EIP-712 transactions). `miner` is 0x0000000000000000000000000000000000000000 and `extra_data` is `0x` in every block. Receipts carry `l1BatchNumber`, `l1BatchTxIndex` and `l2ToL1Logs` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).
* 0x000000000000000000000000000000000000800a is the L2BaseToken system contract, which holds ETH balances (docs/ excerpt abstract-05). It emits logs with topic0 0xddf252ad... and 3 topics. census.py counts them as ERC-20 Transfer logs for criterion B like those of any other emitter (shared definition, unchanged). Their count in candidate txs is in tokens-onchain-meta.csv.gz (column n_transfer_logs_in_candidates); its decimals()/symbol()/name() calls reverted (error columns of that file).

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:33Z to 2026-10-01T04:18:32Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:20:19Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:10Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:44Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 253,818 | 4,719 rows + header | 55832ce665fa40e39d63d29d3d5f92ca9c18e33f0ab74bb93fde1839f020d7fc | not ignored |
| candidates-001.jsonl.gz | 303,159 | 385 JSON lines | b3b444e96116c571b3a4460a18f411a26a277866987a7810ba0ceacace9163f2 | not ignored |
| collect/census.log | 2,414 | 11 lines | 6e68945709fd271a39c43401337b8d474f42ae67a576808a36b35fdab94fdce9 | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 134 | 1 line | 641121de06cd2b7fbc01625a90ca0ab50300d334d38a0cefaec199d0f0babd1b | not ignored |
| collect/docs.log | 632 | 4 lines | 40f225f3acb588904e3a9fde03a26ae39926d16f75e5515ad05222e8d94c3912 | not ignored |
| collect/docs_excerpts_spec.json | 1,118 | 1 JSON document | 00243c1b577929ee2fb9624edd0d245a8d71231d53f0746aa786f71ddcdb13f1 | not ignored |
| collect/docs_urls.txt | 308 | 4 lines | 4f3b4fccd2eb1ffbbe950ec35ebb5c5a493c5f0b92fec083d12eb7af0a2eaeed | not ignored |
| collect/excerpts.log | 107 | 1 line | 21a205c8fc85a5206d0811ac60948396a347b143675517f95d2657a52eda3ccb | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.log | 596 | 3 lines | 2c735ea1c0e713d019b1f7c2b3f4f7156cd4019e6d85ae6564540ef7d805eea6 | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 139 | 1 JSON document | e2e52a2ba59fd495e5723629001dd3d0ab2c447c3349e5102fed3339d9027949 | not ignored |
| defillama-dexs.json | 134,460 | 1 JSON document | 66c2a8422af1322c58943825ee1b57034ad98c5ae0e785e3f30045a3152358b2 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_architecture_components_sequencer.md.raw.gz | 963 | 43 lines (decompressed) | fb92e9ca47935b6a93158ab3eafadca9988861ffff897a95fbcb7e08b606d661 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_architecture_components_sequencer.md.txt | 2,339 | 49 lines | 3adc490e7ea41674de4ba4e4c351358b25be686f5ec6f6a8459cc2f87f6210b2 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_architecture_transaction-lifecycle.md.raw.gz | 1,651 | 69 lines (decompressed) | d08027cba2b0a73aa9618adec51dfe02b39f7fd1135764f630895d901a4c9605 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_architecture_transaction-lifecycle.md.txt | 4,234 | 75 lines | d45e8dd7eb572827be15ebfc0fd53ec984029357255d09bcfba59c7253388dd6 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_evm-differences_gas-fees.md.raw.gz | 2,310 | 126 lines (decompressed) | d6bc07d093c28cf054eb30ba2b8a91d8f66d952c85d17d114618cf6bcf824d38 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_evm-differences_gas-fees.md.txt | 5,534 | 132 lines | 7523c3bd0dc04a0a3b4502df8995e700b423f62d38a5e5f2e80ff14ae3f16a92 | not ignored |
| docs/docs.abs.xyz_how-abstract-works_system-contracts_list-of-system-contracts.md.raw.gz | 3,207 | 269 lines (decompressed) | 56b4c55d5ad4a994da9539d48375a8e5504ffd2ff2bd64ddd9453ebb9fcb9c8a | not ignored |
| docs/docs.abs.xyz_how-abstract-works_system-contracts_list-of-system-contracts.md.txt | 13,074 | 275 lines | f64e5aac8ff7c24753da4cdda046c3b5ec5696fd77b7c63b8582266c859cfdf4 | not ignored |
| docs/excerpts.jsonl | 3,771 | 5 JSON lines | e7b614ee0d019df31aaed4808de21f415f88e48f270664956a540ffc5c35ce6c | not ignored |
| docs/index.csv | 1,057 | 4 rows + header | 7a3efe31333ddc78551ac962e7cc88405de400ffde8eed6ad72c991e29fd94cd | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 747 | 1 JSON document | a6627af9621fc0407e009417699afa920f2311f3d1d889aab094db3e8292cae3 | not ignored |
| prices-defillama-historical.jsonl.gz | 1,489 | 3 JSON lines | 99aa9e7bce35d29b5f3c442be7c030ff534947462a8fc19844e0fa0b98fd07c4 | not ignored |
| reverted-001.csv.gz | 2,173 | 21 rows + header | d709eb343b7cfe13db5de8907cdb511eb1078397a51b5b37db76ba8031b7855a | not ignored |
| swap-topics.csv | 11,132 | 22 rows + header | 7d04d8e4728672cc7f4e8f4b2438893e0052b3ab74a607cf78b1c01cf3aa70f0 | not ignored |
| token_prices.fetch.json | 540 | 1 JSON document | d9dd671e8bee21c3a0fd0a40893c6d9f668bb5ce916b3860c96a0a56a008f4cb | not ignored |
| tokens-onchain-meta.csv.gz | 1,826 | 24 rows + header | 18c5503e92934a2082f498b61be60068ebe44bc44d824d6a68e2fe3bfa4cdc37 | not ignored |
| topic0-counts.csv.gz | 14,378 | 177 rows + header | e5be2a3ed309f87f360b4d14123f8388ee7bd6a940bb28bc65da0ad50e389271 | not ignored |
| txs-001.csv.gz | 391,369 | 6,416 rows + header | f39e9adf96dcc7649c29f422f203a34db5e7694f192f52928e8613eb0d4cf82a | not ignored |
| window.json | 2,600 | 1 JSON document | a606befe23e3df734344f67743433d7d935d2b8b04b06ffff74bf6c8676369e8 | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 44 plus this MANIFEST.md. Largest file: 391,369 bytes (limit 90 MB).
