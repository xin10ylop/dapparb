# Soneium: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_SONEIUM.DONE  soneium census complete 2026-10-01T04:18:52Z blocks 28844980-28846779 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/soneium
EVM_TOKENPRICES_SONEIUM.DONE  soneium token meta + prices done 2026-10-01T04:24:49Z tokens=31
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
| Chain id | 1868 |
| Block range (inclusive) | 28844980 to 28846779 (1800 blocks) |
| Block timestamps | 1790824711 (2026-10-01T03:18:31Z) to 1790828309 (2026-10-01T04:18:29Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 5 |
| Head at pin time | 28846784 (pinned 2026-10-01T04:18:41Z) |
| Measured block interval | 2.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:18:52Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://soneium-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 4 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://rpc.soneium.org`.
* Requests actually sent (HTTP): {"https://soneium-rpc.publicnode.com": 450}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/soneium` fetched 2026-10-01T04:19:16Z (HTTP 200, 111807 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:24:45Z) on https://soneium-rpc.publicnode.com, https://rpc.soneium.org (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `soneium:`) at ts = [1790824711, 1790826510, 1790828309] (3 requests) and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790824711&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 1868, "window_s": 3600, "end_tag": "latest", "head_margin": 5, "batch": 4, "seg_blocks": 300, "nominal_interval": 2.0, "sentinel": "EVM_CENSUS_SONEIUM", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/soneium/collect
python3 -B make_swap_topics.py soneium .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain soneium --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py soneium ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain soneium --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py soneium .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py soneium ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 1800 | 103698 |
| txs-001.csv.gz | 21002 | 1202837 |
| reverted-001.csv.gz | 106 | 8804 |
| candidates-001.jsonl.gz | 596 | 447791 |
| topic0-counts.csv.gz | 181 | 15625 |
| swap-topics.csv | 22 | 11292 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 31 | 2332 |
| prices-defillama-historical.jsonl.gz | 3 | 1678 |
| native-price-chart-defillama.json | (JSON document) | 747 |
| defillama-dexs.json | (JSON document) | 111807 |
| defillama-dexs.fetch.json | (JSON document) | 138 |
| token_prices.fetch.json | (JSON document) | 544 |
| window.json | (JSON document) | 2597 |
| docs/excerpts.jsonl | 4 | 2419 |

Candidate counts by criterion: A = 481, B = 115. Transactions: 21002; status-0 transactions: 106; distinct topic0 keys: 181; receipts not in the block's transaction list: 0.

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
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/soneium` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xb9e043612d2bcc8c41d8dc7a7b46406bdc71a81363462684390ce1d5d19d73de |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x7fe063d03dcd936d0626d6a9932f4f0f8dc711ba3c14d924dd3b33362ac306ae |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0x7fe063d03dcd936d0626d6a9932f4f0f8dc711ba3c14d924dd3b33362ac306ae |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | yes: 0x2a6eccc52e34af8fc5cbf9ae6c7de6b968082dd1ee10b3261dcb7cd6db8fc15f |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | yes: 0xdfc126522adf9679bdd000b3173b4f5a73f59e6ea1d9c524eeece9e36e81871b |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x995eeb51ea2448a44d33eae0aee6fd40f124762a48952f41bbfef73ad5351250 |
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
| https://docs.soneium.org/docs/builders/faq | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.soneium.org/docs/builders/notices/notice-restriction | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.soneium.org/docs/builders/fees | 200 | 2026-10-01T04:22:48Z |  |
| https://docs.soneium.org/docs/builders/overview | 200 | 2026-10-01T04:22:49Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| soneium-01 | https://docs.soneium.org/docs/builders/faq | 2026-10-01T04:22:46Z | The mempool is private (only visible to the Sequencer), and transactions are executed in priority fee order (highest fee first). |
| soneium-02 | https://docs.soneium.org/docs/builders/notices/notice-restriction | 2026-10-01T04:22:47Z | As part of our compliance efforts, we will transition to an operation that restricts permissionless write-capable RPC paths to the sequencer node. Currently, on ... |
| soneium-03 | https://docs.soneium.org/docs/builders/notices/notice-restriction | 2026-10-01T04:22:47Z | Both testnet (Soneium Minato) and mainnet will limit write requests to the sequencer node to those from compliance-approved RPCs only. |
| soneium-04 | https://docs.soneium.org/docs/builders/notices/notice-restriction | 2026-10-01T04:22:47Z | The start date for restricting write-capable RPC paths on the mainnet has been rescheduled to October 28, 2025. |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 568, 2: 18,632, 126: 1,802.
* `miner` values in blocks.csv.gz (blocks): 0x4200000000000000000000000000000000000011: 1,800.
* Stack: OP Stack chain (Superchain). Gas token: ETH.
* Write access to the sequencer is limited to compliance-approved RPCs (docs/ excerpts soneium-02 to soneium-04). soneium.drpc.org answered eth_blockNumber with 'the method eth_blockNumber does not exist/is not available' during the selection probe (../rpc-receipts-probe-candidates.jsonl.gz) and is not used.

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:24:45Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:16Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:46Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 103,698 | 1,800 rows + header | 56ea5cf9b2f82ac45fa0c389939645d3d685274b8b71b8d157cb4f3be324814b | not ignored |
| candidates-001.jsonl.gz | 447,791 | 596 JSON lines | a311f473810c6257c28d750058afe03dc4506ae1ed797db18d2ca34d81a08622 | not ignored |
| collect/census.log | 2,126 | 9 lines | 6107544a512ff7e460c7c9746d1819718bac809634b0a56e99d96f12fb91d22c | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 133 | 1 line | 56d4ee8d71e92d230d7faaae847ec1ebe315b389dcd499cbb9a9bd300a327b58 | not ignored |
| collect/docs.log | 418 | 4 lines | fe3057e72489b231792f5a1e6463201121d6d4a383902c20bd26759a80dea3b6 | not ignored |
| collect/docs_excerpts_spec.json | 768 | 1 JSON document | d8366b86008ee8395350076821146494e129074f7e78ab456048db19064ffb68 | not ignored |
| collect/docs_urls.txt | 201 | 4 lines | fd099c9b695c73bbadf8b32fc4a377331589cbc39391a1c8c13d37d6375bcd21 | not ignored |
| collect/excerpts.log | 106 | 1 line | 7a77c2b3977f0da21ba6c76601ad9840350a703c1dd2108ede808eafb8273a20 | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.log | 600 | 3 lines | d1a25265a4da2657f17b6854670fa164518047d40310dfdd439d12c40ae75e09 | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 138 | 1 JSON document | 4f1f420207d0c838ac1e64b6ccb8784a10b0af3741f0a3f9046f98da8d612f56 | not ignored |
| defillama-dexs.json | 111,807 | 1 JSON document | f7978fcb09425be60aa492f89fab6fd0f49a69aec50ffe0ee246ad337bce277a | not ignored |
| docs/docs.soneium.org_docs_builders_faq.html.gz | 14,145 | 93 lines (decompressed) | c050a09e843b15986fb5070b333a411c7c27585e30b8ef48ebe912d8cda04cc6 | not ignored |
| docs/docs.soneium.org_docs_builders_faq.txt | 8,055 | 286 lines | 0008ac85b12b952db09ee9d45061c8f4ee85b040059598f5f0441d0fe8eeb3c9 | not ignored |
| docs/docs.soneium.org_docs_builders_fees.html.gz | 9,296 | 30 lines (decompressed) | bd5374025f61c7b32dae6b1f61afd714667fc9ef2533bc04c6a39f2bd23bd269 | not ignored |
| docs/docs.soneium.org_docs_builders_fees.txt | 2,020 | 127 lines | 0e23ee39696e0a446f2cb616e3427656a11b2c210d146800b0558ce72a9276ef | not ignored |
| docs/docs.soneium.org_docs_builders_notices_notice-restriction.html.gz | 10,582 | 72 lines (decompressed) | 7b4abb9c707da371845bc0b0ffc33429fe869e8e95d280aaf6dfe4c9f2f768db | not ignored |
| docs/docs.soneium.org_docs_builders_notices_notice-restriction.txt | 4,599 | 175 lines | b04729de14f135acbc7dd18cd8c2d0443292b453356a9c255a4649d3c05199f6 | not ignored |
| docs/docs.soneium.org_docs_builders_overview.html.gz | 10,663 | 43 lines (decompressed) | 18c6f4fab99cb4d79d008b224b5f9ca5238968a2ccb42667f210bfb924847983 | not ignored |
| docs/docs.soneium.org_docs_builders_overview.txt | 2,946 | 174 lines | 579825ecb62dcfff9026306da184d7c8324218a427710e5715e686b469b9e3cf | not ignored |
| docs/excerpts.jsonl | 2,419 | 4 JSON lines | a549fad0a1430ddc326cb23b4a439c033dd01c7c2d1723a82fef73feebbebb80 | not ignored |
| docs/index.csv | 736 | 4 rows + header | d356ac71903c6f97ac638ff075136fc7d7887298af93cc1eb9c63ce488103074 | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 747 | 1 JSON document | a6627af9621fc0407e009417699afa920f2311f3d1d889aab094db3e8292cae3 | not ignored |
| prices-defillama-historical.jsonl.gz | 1,678 | 3 JSON lines | 377d5af8d753c75e1813b44402541933b6b4b8bd22c79d6777c65c94a8f66ca1 | not ignored |
| reverted-001.csv.gz | 8,804 | 106 rows + header | dd196ee46fd45cf5f83320db4a405a7252bd3cdc700c4dc20d8ca8892c47d9bb | not ignored |
| swap-topics.csv | 11,292 | 22 rows + header | 1fa3187566dcf1fb9f47e097910805742b3ad325331e2dd356e59ddacfcf7ef2 | not ignored |
| token_prices.fetch.json | 544 | 1 JSON document | 5ef4642e417da812160812e01059554378f3fe38e7600eee21a47e3032f2152f | not ignored |
| tokens-onchain-meta.csv.gz | 2,332 | 31 rows + header | 00f039ccd364768837df4d654dff695886bd9171c42e414fb5cbbe2354695bf6 | not ignored |
| topic0-counts.csv.gz | 15,625 | 181 rows + header | 3afe2c5aa1f09b34b913c71fdaf9fb154c47fbfe2c53f92c4ed9c98ba32cba71 | not ignored |
| txs-001.csv.gz | 1,202,837 | 21,002 rows + header | d7938037fe7a481317a80c316506ad321310fb0668445b76e36634877101257d | not ignored |
| window.json | 2,597 | 1 JSON document | d410094c0a60c147542c659905baea9feaa5424062aae717ae41a68a2d6b3569 | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 44 plus this MANIFEST.md. Largest file: 1,202,837 bytes (limit 90 MB).
