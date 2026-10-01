# World Chain: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_WORLDCHAIN.DONE  worldchain census complete 2026-10-01T04:19:51Z blocks 35744536-35746335 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/worldchain
EVM_TOKENPRICES_WORLDCHAIN.DONE  worldchain token meta + prices done 2026-10-01T04:31:41Z tokens=445
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
| Chain id | 480 |
| Block range (inclusive) | 35744536 to 35746335 (1800 blocks) |
| Block timestamps | 1790824711 (2026-10-01T03:18:31Z) to 1790828309 (2026-10-01T04:18:29Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 5 |
| Head at pin time | 35746340 (pinned 2026-10-01T04:18:41Z) |
| Measured block interval | 2.000000 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:19:51Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://worldchain-mainnet.gateway.tenderly.co` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 4 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://480.rpc.thirdweb.com`, `https://sparkling-autumn-dinghy.worldchain-mainnet.quiknode.pro`.
* Requests actually sent (HTTP): {"https://worldchain-mainnet.gateway.tenderly.co": 494}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {"https://worldchain-mainnet.gateway.tenderly.co|retry": 44, "https://worldchain-mainnet.gateway.tenderly.co|item-retry": 176}.
* DefiLlama: `https://api.llama.fi/overview/dexs/world-chain` fetched 2026-10-01T04:19:12Z (HTTP 200, 62435 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:31:04Z) on https://worldchain-mainnet.g.alchemy.com/public, https://480.rpc.thirdweb.com (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `wc:`) at ts = [1790824711, 1790826510, 1790828309] (36 requests) and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790824711&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 480, "window_s": 3600, "end_tag": "latest", "head_margin": 5, "batch": 4, "seg_blocks": 300, "nominal_interval": 2.0, "sentinel": "EVM_CENSUS_WORLDCHAIN", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/worldchain/collect
python3 -B make_swap_topics.py worldchain .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain worldchain --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py world-chain ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain worldchain --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py worldchain .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py worldchain ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 1800 | 104145 |
| txs-001.csv.gz | 27246 | 1712554 |
| reverted-001.csv.gz | 199 | 16392 |
| candidates-001.jsonl.gz | 3654 | 5280681 |
| topic0-counts.csv.gz | 485 | 42630 |
| swap-topics.csv | 22 | 11176 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 445 | 27329 |
| prices-defillama-historical.jsonl.gz | 36 | 13542 |
| native-price-chart-defillama.json | (JSON document) | 747 |
| defillama-dexs.json | (JSON document) | 62435 |
| defillama-dexs.fetch.json | (JSON document) | 141 |
| token_prices.fetch.json | (JSON document) | 567 |
| window.json | (JSON document) | 2835 |
| docs/excerpts.jsonl | 12 | 7788 |

Candidate counts by criterion: A = 769, B = 2885. Transactions: 27246; status-0 transactions: 199; distinct topic0 keys: 485; receipts not in the block's transaction list: 0.

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
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/world-chain` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xcd4556f2fd3a657a1573df2b1a38b6d21c5ac861022a91aa421ef9509192172c |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x67f8e9f6a3d1160fc76c0c3b850bbac90db58f072a4c9eaf857ce7e35faac564 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0x3f25e24cc4272f7cb89b1298cd4571b2c5384021621dfa54b5b07d5a1c40617e |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | no |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | no |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x6b9d27e750726b9b5cfcd11394b49aa20f7846603398989dc00636c1b060a710 |
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
| https://docs.world.org/world-chain/quick-start/features.md | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.world.org/world-chain/developers/fees.md | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.world.org/world-chain/developers/evm-equivalence.md | 200 | 2026-10-01T04:22:47Z |  |
| https://world.org/blog/engineering/introducing-pbh-priority-blockspace-for-humans | 200 | 2026-10-01T04:22:48Z |  |
| https://worldcoin.github.io/world-chain/pbh/overview.html | 200 | 2026-10-01T04:22:49Z |  |
| https://worldcoin.github.io/world-chain/pbh/architecture.html | 200 | 2026-10-01T04:22:49Z |  |
| https://worldcoin.github.io/world-chain/pbh/payload.html | 200 | 2026-10-01T04:22:50Z |  |
| https://worldcoin.github.io/world-chain/pbh/txs.html | 200 | 2026-10-01T04:22:50Z |  |
| https://worldcoin.github.io/world-chain/flashblocks/p2p.html | 200 | 2026-10-01T04:22:51Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| worldchain-01 | https://docs.world.org/world-chain/quick-start/features.md | 2026-10-01T04:22:46Z | PBH enables verified users to execute transactions guaranteeing top of block inclusion, enabling a more frictionless user experience. |
| worldchain-02 | https://worldcoin.github.io/world-chain/pbh/overview.html | 2026-10-01T04:22:49Z | Priority Blockspace for Humans introduces a new transaction ordering policy on World Chain that grants verified World ID holders top-of-block priority, reducing ... |
| worldchain-03 | https://worldcoin.github.io/world-chain/pbh/architecture.html | 2026-10-01T04:22:49Z | The World Chain Builder implements a custom block ordering policy (ie. PBH) to provide priority inclusion for transactions with a valid World ID proof. Note tha ... |
| worldchain-04 | https://worldcoin.github.io/world-chain/pbh/architecture.html | 2026-10-01T04:22:49Z | Each block has a “PBH blockspace capacity”, which determines how many PBH transactions will be included in the block. Blocks on World Chain will always reserve  ... |
| worldchain-05 | https://worldcoin.github.io/world-chain/pbh/architecture.html | 2026-10-01T04:22:49Z | If the amount of pending PBH transactions exceed the PBH blockspace capacity, the remaining PBH transactions will carry over to the next block. PBH transactions ... |
| worldchain-06 | https://worldcoin.github.io/world-chain/pbh/architecture.html | 2026-10-01T04:22:49Z | In the event that the block builder is offline, rollup-boost will fallback to the block built by the default execution client with standard OP Stack ordering ru ... |
| worldchain-07 | https://worldcoin.github.io/world-chain/pbh/architecture.html | 2026-10-01T04:22:49Z | Note that rollup-boost will always fallback to the default execution client’s block in the case that the external builder does not respond in time or returns an ... |
| worldchain-08 | https://worldcoin.github.io/world-chain/pbh/txs.html | 2026-10-01T04:22:50Z | Upon submitting a PBH bundle to the network, the World Chain builder will ensure that all PBH bundles have valid proofs and mark the bundle for priority inclusi ... |
| worldchain-09 | https://world.org/blog/engineering/introducing-pbh-priority-blockspace-for-humans | 2026-10-01T04:22:48Z | When a user sends a transaction to a node, the pending transaction is forwarded to the sequencer and added to the sequencer’s mempool. The sequencer is no diffe ... |
| worldchain-10 | https://world.org/blog/engineering/introducing-pbh-priority-blockspace-for-humans | 2026-10-01T04:22:48Z | Note that transaction ordering within the payload builder is not enforced at the protocol level. A block builder can construct a valid block with any combinatio ... |
| worldchain-11 | https://world.org/blog/engineering/introducing-pbh-priority-blockspace-for-humans | 2026-10-01T04:22:48Z | In order to implement priority blockspace for humans, a World Chain block builder is being developed which ensures that verified human transactions are included ... |
| worldchain-12 | https://worldcoin.github.io/world-chain/flashblocks/p2p.html | 2026-10-01T04:22:51Z | This document is an extension to the original Flashblocks specification, modifying the flashblock propagation mechanism to use a peer-to-peer (P2P) network inst ... |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 678, 2: 24,764, 126: 1,804.
* `miner` values in blocks.csv.gz (blocks): 0x4200000000000000000000000000000000000011: 1,800.
* Stack: OP Stack chain with the World Chain Builder (rollup-boost external block production) and Priority Blockspace for Humans (PBH) ordering policy (docs/ excerpts worldchain-02 to worldchain-07). Gas token: ETH.
* PBH transactions are not flagged in the census files (no PBH-specific column); the PBHEntryPoint contract address was not looked up for this collection. Receipts and logs of candidate txs are stored verbatim; all txs (incl. `to` address) are in txs-001.csv.gz.
* The Alchemy public endpoint (https://worldchain-mainnet.g.alchemy.com/public) answered eth_getBlockReceipts with HTTP 401 'Only core evm requests are allowed.' (../rpc-receipts-probe-candidates.jsonl.gz) and was not used for the census; it was used for the token metadata eth_calls (see 'Token metadata runs').
* Token metadata runs: run 1 (first log line 04:20:23Z, eth_call endpoints Tenderly gateway first) and run 2 (04:25:05Z, thirdweb first) were stopped by the collector before writing output, because those endpoints answered 60-call eth_call batches with HTTP 429 or per-item rate-limit errors (logs: collect/token_prices.attempt1.log, collect/token_prices.attempt2.log). Run 3 (04:30:29Z, Alchemy public first) was started while run 2 was still running and was stopped after it had written tokens-onchain-meta.csv.gz (log: collect/token_prices.attempt3.log). Its partial outputs were deleted. Run 4 (04:30:51Z, Alchemy public first) wrote all files in this directory; its log is collect/token_prices.log. The l2_config.py comment records the endpoint order change. The census itself was not affected.

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:31:04Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:12Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:45Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 104,145 | 1,800 rows + header | 337906680fa67d359f83b6e33b41b2b1bdd8e4c0b8411458fc551467ab3434dc | not ignored |
| candidates-001.jsonl.gz | 5,280,681 | 3,654 JSON lines | 3862b6d7ea2d387be31e33f31db908c7545a1b16b0446d4ebf79b3c268261785 | not ignored |
| collect/census.log | 3,041 | 9 lines | fc4638d976b48b5befb922cb5c773285fb8ca4d0ea48742a4f1af8c8add4441f | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 136 | 1 line | fd50a0963ce057f36396caf26aac813dbf6f3968d4815bb063f40bffb2c63797 | not ignored |
| collect/docs.log | 1,138 | 9 lines | c9b762928b139e7e5696fbb6a7b2fe7077604ca5079e333f887e4c4cc1fe13da | not ignored |
| collect/docs_excerpts_spec.json | 2,550 | 1 JSON document | 84f60e7b0d7b8d6d21a5c6be584036ded4fef143fbfda028111ac9fe5c0ba747 | not ignored |
| collect/docs_urls.txt | 551 | 9 lines | c56923b99aa2078a972b858a8e0e8a468bda341413926e82f36e6402a7f90241 | not ignored |
| collect/excerpts.log | 110 | 1 line | def8061b27eefa528c11fb5a4d65eab788782059142eda3bc8ca79b6a6f541bc | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.attempt1.log | 32 | 1 line | 6c6ea2612ff916422a80bb68ff6ba53a3028dcdb234a9901d50a6fa304d3b595 | not ignored |
| collect/token_prices.attempt2.log | 32 | 1 line | a63646065aa0e0d65e31623de691707a682cfa1152926253dc6a6f99d27ce86f | not ignored |
| collect/token_prices.attempt3.log | 74 | 2 lines | e68bc6c248ef17e9c340f991851ff8b13260df2672393cbfefb17d2c78f21557 | not ignored |
| collect/token_prices.log | 624 | 3 lines | 6904e39edf6e809d6bf4d89259e7189b72e4129a4e256c1e242d7f9e5eaddd9b | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 141 | 1 JSON document | 648e41f12146b31c541288fec87461e7171b3b6d654ad5cc208c9d81ba7e95ad | not ignored |
| defillama-dexs.json | 62,435 | 1 JSON document | 6f4e52e5932421a71f0e362b47e303b15bdebaa6dc683b77c1ee4dd678c8c52e | not ignored |
| docs/docs.world.org_world-chain_developers_evm-equivalence.md.raw.gz | 1,040 | 89 lines (decompressed) | 0a5aa6125c718fed47df5ec5ce6daf75d7aed3dae20d009075ec5b42adad71b4 | not ignored |
| docs/docs.world.org_world-chain_developers_evm-equivalence.md.txt | 3,783 | 95 lines | faf132d1893e3a819c9fb84930c4994156410fe426d12828416815ead8f855e7 | not ignored |
| docs/docs.world.org_world-chain_developers_fees.md.raw.gz | 710 | 15 lines (decompressed) | 86418801bc4bf420bbdd738054dff6c0d794ff5a206fcb208adc5931eca00e0b | not ignored |
| docs/docs.world.org_world-chain_developers_fees.md.txt | 1,642 | 21 lines | 579535f4d1419e955477fa89a21631e6a4db340f00c6d87a82ff5efe4a2ae254 | not ignored |
| docs/docs.world.org_world-chain_quick-start_features.md.raw.gz | 1,455 | 34 lines (decompressed) | 96f521e09312d37cdb33ec865a66424ffc8baa9c11e2f6118d20e537abd44ce9 | not ignored |
| docs/docs.world.org_world-chain_quick-start_features.md.txt | 3,287 | 40 lines | 0b4d2e50c0ac1111ade78e9f6e2696938510faa0938566545a39f1502c4660d1 | not ignored |
| docs/excerpts.jsonl | 7,788 | 12 JSON lines | bc21488c3558d32373d3c8e86e3d15bf1059c48ed76c9cf6b3025fb4f2b371f8 | not ignored |
| docs/index.csv | 1,881 | 9 rows + header | 8df1d029ff4837f67be57df940550051775e77636fbe27ab50ae042f6a96545f | not ignored |
| docs/world.org_blog_engineering_introducing-pbh-priority-blockspace-for-humans.html.gz | 52,319 | 1 line (decompressed) | 2b6ddbc1649583498fa6791632415bc995ffa1a77d326d91f68a6f1a794eec29 | not ignored |
| docs/world.org_blog_engineering_introducing-pbh-priority-blockspace-for-humans.txt | 8,905 | 205 lines | 952c7620b710fe47250ce354909be53a76117a0214df46283575b542df6db7ff | not ignored |
| docs/worldcoin.github.io_world-chain_flashblocks_p2p.html.html.gz | 13,658 | 488 lines (decompressed) | ca6b03a5ba6880b52e5841df97843d503d9e08011b090535e8a754254e5559c9 | not ignored |
| docs/worldcoin.github.io_world-chain_flashblocks_p2p.html.txt | 21,799 | 356 lines | 38abab9ff3d01ddd434a6ef36782a73df6fc9cd10df70d5a330aa2e8b71a9f41 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_architecture.html.html.gz | 7,711 | 427 lines (decompressed) | aed5171a604f37c34512e98318fa62caded1b214d4dc198a2c0aec98e5467774 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_architecture.html.txt | 6,864 | 193 lines | 365c59ddab19d19a62e26a8eedcd99c4fc0053885031d45dac94cac9baa4da49 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_overview.html.html.gz | 5,516 | 243 lines (decompressed) | d48c76cae8d223ccc8b18f1d651c6582362fa9081c7bfa6264540043ae50b355 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_overview.html.txt | 955 | 57 lines | b816d74ffa83fe49d692d1f01d423aab220d10ecc3d1b3a5333eff178b927976 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_payload.html.html.gz | 7,121 | 306 lines (decompressed) | efb7f3770fc29149e84949066704d6c38b5c40bfad7e29daa7835583011a6b31 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_payload.html.txt | 4,786 | 128 lines | 8f432063f4a7f549e9b91df5abae30566965e5026e892b49da79116d37e0abf8 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_txs.html.html.gz | 6,688 | 272 lines (decompressed) | a5fa1a7ce2e18582106985686cfeb8a5044cb842aba42094da9b8baa3d075903 | not ignored |
| docs/worldcoin.github.io_world-chain_pbh_txs.html.txt | 2,706 | 88 lines | 580c64616137c3d18c8750e9803d0a3a177e27ef5ca4e1c90d89df01f74d2c5a | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 747 | 1 JSON document | a6627af9621fc0407e009417699afa920f2311f3d1d889aab094db3e8292cae3 | not ignored |
| prices-defillama-historical.jsonl.gz | 13,542 | 36 JSON lines | c1e85b5dd6fe3633dd32362aed5efc044a2dd2adff5415ecbe1ef53d4560bd9b | not ignored |
| reverted-001.csv.gz | 16,392 | 199 rows + header | 3ef941edf7ae4e7456359722b54b0d696bdd71b556ab67c7fae0e9125c0b4c33 | not ignored |
| swap-topics.csv | 11,176 | 22 rows + header | a803404182be21a37097fec3d8fe3414e44acc61a1119ecad37222485b9bbb86 | not ignored |
| token_prices.fetch.json | 567 | 1 JSON document | 2ef18532817cd2d34fd708134be3f931b09a43fd8f361ec03d9dbe13f75f9bce | not ignored |
| tokens-onchain-meta.csv.gz | 27,329 | 445 rows + header | b813a824bd6459950594e8e38a3a3f33811842fb37124ed40bed77917ea3f838 | not ignored |
| topic0-counts.csv.gz | 42,630 | 485 rows + header | 6dfe3304d6678192a9d5c91d7d0279cf4d5f69bfca278047fa965e4a9acbad22 | not ignored |
| txs-001.csv.gz | 1,712,554 | 27,246 rows + header | feea41b8f18ffcee429145cca48e0b422c5a4173addabad1f080aa66ffbd66bb | not ignored |
| window.json | 2,835 | 1 JSON document | 73ee9641a6d179f875ae0f65d64631c9965e936bc27ea21bd21254e19fb5ddbb | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 57 plus this MANIFEST.md. Largest file: 5,280,681 bytes (limit 90 MB).
