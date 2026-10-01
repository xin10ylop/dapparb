# Ink: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_INK.DONE  ink census complete 2026-10-01T04:18:52Z blocks 57326299-57329898 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/ink
EVM_TOKENPRICES_INK.DONE  ink token meta + prices done 2026-10-01T04:20:11Z tokens=46
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
| Chain id | 57073 |
| Block range (inclusive) | 57326299 to 57329898 (3600 blocks) |
| Block timestamps | 1790824710 (2026-10-01T03:18:30Z) to 1790828309 (2026-10-01T04:18:29Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 10 |
| Head at pin time | 57329908 (pinned 2026-10-01T04:18:40Z) |
| Measured block interval | 1.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:18:52Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://ink-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 8 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://rpc-gel.inkonchain.com`, `https://rpc-qnd.inkonchain.com`, `https://ink.drpc.org`.
* Requests actually sent (HTTP): {"https://ink-rpc.publicnode.com": 450}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/ink` fetched 2026-10-01T04:19:05Z (HTTP 200, 114405 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:20:04Z) on https://ink-rpc.publicnode.com, https://rpc-gel.inkonchain.com (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `ink:`) at ts = [1790824710, 1790826509, 1790828309] (6 requests) and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790824710&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 57073, "window_s": 3600, "end_tag": "latest", "head_margin": 10, "batch": 8, "seg_blocks": 600, "nominal_interval": 1.0, "sentinel": "EVM_CENSUS_INK", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/ink/collect
python3 -B make_swap_topics.py ink .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain ink --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py ink ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain ink --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py ink .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py ink ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 3600 | 200525 |
| txs-001.csv.gz | 23691 | 1401072 |
| reverted-001.csv.gz | 508 | 30617 |
| candidates-001.jsonl.gz | 398 | 427619 |
| topic0-counts.csv.gz | 299 | 24571 |
| swap-topics.csv | 22 | 11022 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 46 | 3260 |
| prices-defillama-historical.jsonl.gz | 6 | 2672 |
| native-price-chart-defillama.json | (JSON document) | 747 |
| defillama-dexs.json | (JSON document) | 114405 |
| defillama-dexs.fetch.json | (JSON document) | 134 |
| token_prices.fetch.json | (JSON document) | 543 |
| window.json | (JSON document) | 2657 |
| docs/excerpts.jsonl | 5 | 2646 |

Candidate counts by criterion: A = 170, B = 228. Transactions: 23691; status-0 transactions: 508; distinct topic0 keys: 299; receipts not in the block's transaction list: 0.

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
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/ink` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0x468b07d73dd8b9e9876d0b6384dd6785b9f75a209a874c6659163c9dee7a343d |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x63c344a1775e1383c0c74511d58afae655884b0db97be165a6a009c18cea0223 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | no |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | yes: 0xf6bc691c3cdef6ca20a2cb7c68f17558075af9debf715b719ad0d5e3370f4a2d |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x45b46ddcc8e2e7a295adfa0f754c1520d81994c206611f4d9da228bd5142112e |
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

### docs/ (official documentation on ordering / sequencer)

| URL | HTTP | fetched (UTC) | note |
|---|---|---|---|
| https://docs.inkonchain.com/general/about | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.inkonchain.com/tools/rpc | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.inkonchain.com/useful-information/the-superchain | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.inkonchain.com/general/network-information | 200 | 2026-10-01T04:22:47Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| ink-01 | https://docs.inkonchain.com/tools/rpc | 2026-10-01T04:22:47Z | Subblocks (formerly Flashblocks) are partial blocks that the Ink sequencer streams while it is still building the full block, roughly every 200 ms. They let you ... |
| ink-02 | https://docs.inkonchain.com/tools/rpc | 2026-10-01T04:22:47Z | A pre-confirmation carries the sequencer’s trust assumption, not the protocol’s. It can be revoked under the same conditions that allow the sequencer to reorg u ... |
| ink-03 | https://docs.inkonchain.com/general/about | 2026-10-01T04:22:46Z | * Security : Sequencer-level security to protect users from malicious intents and exploits. |
| ink-04 | https://docs.inkonchain.com/useful-information/the-superchain | 2026-10-01T04:22:47Z | Ink is an OP Chain (Ethereum Layer 2) which is part of the Superchain. |
| ink-05 | https://docs.inkonchain.com/useful-information/the-superchain | 2026-10-01T04:22:47Z | Configuration options for OP Chains Enables OP Chains to configure their data availability provider, sequencer address, etc. |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 409, 2: 19,663, 4: 17, 126: 3,602.
* `miner` values in blocks.csv.gz (blocks): 0x4200000000000000000000000000000000000011: 3,600.
* Stack: OP Stack chain (docs/ excerpt ink-04, 'Ink is an OP Chain (Ethereum Layer 2) which is part of the Superchain.'). Gas token: ETH.
* Ordering-related docs available on docs.inkonchain.com are short; no page describing the sequencer's ordering rule was found in the site map (`https://docs.inkonchain.com/sitemap-0.xml`, 49 URLs, read 2026-10-01). The stored pages are the four listed under docs/. OP Stack ordering docs are stored in ../optimism/docs/.

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:30Z to 2026-10-01T04:18:29Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:20:04Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:05Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:43Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 200,525 | 3,600 rows + header | 12c9c681604ee99526e8ac33127f4fa9922225b9a10f5e3f9f8fef69f45a7288 | not ignored |
| candidates-001.jsonl.gz | 427,619 | 398 JSON lines | 3527b857f55b5c826f1e871d63b8f07013da1897cbb630ca0c3435b9b724ac61 | not ignored |
| collect/census.log | 2,159 | 9 lines | 9251cab5da1ba2b5eb8799d135d214e07ba1a5338619071afe7a086a32ed9788 | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 129 | 1 line | 333b6e4a6ed7956d6dfa3d418ac418c01e898d34e21e1c7b503f6508ceee8cbe | not ignored |
| collect/docs.log | 412 | 4 lines | 6166b9e7612c38eb0ea6d2cf4ed0502470c2e55a6510656318c68d4306989140 | not ignored |
| collect/docs_excerpts_spec.json | 807 | 1 JSON document | 1c21aab4f5c315519cfaef864d336a8b883caa325c4b5a5c01386cb96963bc9a | not ignored |
| collect/docs_urls.txt | 198 | 4 lines | 4696cf0ae1f5e29a723b7abb42b24608f94b3d5e188d31ea481f9b0652a37c47 | not ignored |
| collect/excerpts.log | 102 | 1 line | 66f8b5537c1ba2c742cd4f97d224dc279b7c9692ab6eed3e4d7c43e530e27805 | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.log | 599 | 3 lines | 2b455b6b45e87a017540838f5c6513105c453b2d556f215ddb03af426ff1e2a0 | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 134 | 1 JSON document | 8276844a7eaf646093e4abf7aea1f8060b695e971442d44d8be796b65e484ced | not ignored |
| defillama-dexs.json | 114,405 | 1 JSON document | 4ef1b0edab4831cebb389c725361494482bfd9c69237a3a83e2564305486570b | not ignored |
| docs/docs.inkonchain.com_general_about.html.gz | 8,673 | 29 lines (decompressed) | 8830ad32ac3d0dd6d918b0d5165b996fc366abe9e16b5af70bfecd3c834df227 | not ignored |
| docs/docs.inkonchain.com_general_about.txt | 4,033 | 209 lines | 856f721fc3d8a38ee4805bcdf2b5c3052194b134f9ca6ca533c1fc9f952704e9 | not ignored |
| docs/docs.inkonchain.com_general_network-information.html.gz | 8,251 | 8 lines (decompressed) | 62f3ad204d0ff527830db6cc61d132182de902861c573aab3e56bb702262e0b6 | not ignored |
| docs/docs.inkonchain.com_general_network-information.txt | 2,748 | 193 lines | 7d3b64006f1d5b07d0c1c6f5407f70fd2f44f1315ed79d80a8df7305b98b9c73 | not ignored |
| docs/docs.inkonchain.com_tools_rpc.html.gz | 10,520 | 127 lines (decompressed) | 998f14e9a6e659836708e98eac69998dc8bb51129f68e370f4f85db8748e928f | not ignored |
| docs/docs.inkonchain.com_tools_rpc.txt | 6,241 | 371 lines | 6522ad535cb3e2691856f47286415444237df829d485d80b7768bacd9f591962 | not ignored |
| docs/docs.inkonchain.com_useful-information_the-superchain.html.gz | 9,158 | 27 lines (decompressed) | 2fa20ace698bb321db70e24f1126ae63683cd53baa0fff8a1689a31846cb961b | not ignored |
| docs/docs.inkonchain.com_useful-information_the-superchain.txt | 4,526 | 212 lines | 63f4de86dc79b722c58d2f6349f502ab0c698784cf86ec2d94e84535c5e83677 | not ignored |
| docs/excerpts.jsonl | 2,646 | 5 JSON lines | d696dcf1b42b338b7266d1e9ee52c9c6a7a9e8904a46bb8fa5a1f672c3d2ee3c | not ignored |
| docs/index.csv | 727 | 4 rows + header | 37b79dae44461f370b2ef64e802115a1b3ea7bb39922f055bb264b25fda43426 | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 747 | 1 JSON document | a6627af9621fc0407e009417699afa920f2311f3d1d889aab094db3e8292cae3 | not ignored |
| prices-defillama-historical.jsonl.gz | 2,672 | 6 JSON lines | 9f2d40d3103e3d3918b19ae43d783e7679b6b0fbf3eb0bbe9e698d02f467e50a | not ignored |
| reverted-001.csv.gz | 30,617 | 508 rows + header | cdf588a2ebc581fa3bdb3200b54ae135b407722d7dc167947e19b40a522f9e9e | not ignored |
| swap-topics.csv | 11,022 | 22 rows + header | 9b2481c69d7c8b558e59d6976443d8eff30a8d1a794aefc63723510cd1a25778 | not ignored |
| token_prices.fetch.json | 543 | 1 JSON document | 6d8e2a7385547de0a699eb1d4527f8412bfca4a104a52c496c46303122f60c38 | not ignored |
| tokens-onchain-meta.csv.gz | 3,260 | 46 rows + header | 8fd734833f361a3b2c875e43e8f5b726958668864c03e64d2a1ce72766873c69 | not ignored |
| topic0-counts.csv.gz | 24,571 | 299 rows + header | 2004d72c79cd3ac70805d7d0f2044ea00303f7bd68234ed1b82538d107fac29f | not ignored |
| txs-001.csv.gz | 1,401,072 | 23,691 rows + header | 4e6d6289926182b82dc356dec42a80596fdb02d0d37628cfcc8828006607303d | not ignored |
| window.json | 2,657 | 1 JSON document | fb68c1437b3f5799423021d6993f402f4609a170f87d53da55afb601468c6e3f | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 44 plus this MANIFEST.md. Largest file: 1,401,072 bytes (limit 90 MB).
