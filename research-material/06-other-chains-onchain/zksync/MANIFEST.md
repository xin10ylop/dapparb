# ZKsync Era: on-chain arbitrage census (raw material)

Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').

Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):

```
EVM_CENSUS_ZKSYNC.DONE  zksync census complete 2026-10-01T04:18:44Z blocks 72284916-72285498 gap_blocks=0 dir=/home/user/dapparb/research-material/06-other-chains-onchain/zksync
EVM_TOKENPRICES_ZKSYNC.DONE  zksync token meta + prices done 2026-10-01T04:24:44Z tokens=24
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
| Chain id | 324 |
| Block range (inclusive) | 72284916 to 72285498 (583 blocks) |
| Block timestamps | 1790824689 (2026-10-01T03:18:09Z) to 1790828288 (2026-10-01T04:18:08Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 5 |
| Head at pin time | 72285503 (pinned 2026-10-01T04:18:41Z) |
| Measured block interval | 6.183849 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-10-01T04:18:44Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://mainnet.era.zksync.io` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 10 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://zksync.drpc.org`.
* Requests actually sent (HTTP): {"https://mainnet.era.zksync.io": 59}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {}.
* DefiLlama: `https://api.llama.fi/overview/dexs/zksync-era` fetched 2026-10-01T04:19:14Z (HTTP 200, 462732 bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains).
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-10-01T04:24:41Z) on https://mainnet.era.zksync.io, https://zksync.drpc.org (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `era:`) at ts = [1790824689, 1790826488, 1790828288] (3 requests) and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790824689&span=13&period=5m` (HTTP 200).
* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Method and scripts

The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).
census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.
The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): {"chain_id": 324, "window_s": 3600, "end_tag": "latest", "head_margin": 5, "batch": 10, "seg_blocks": 200, "nominal_interval": 6.0, "sentinel": "EVM_CENSUS_ZKSYNC", "extra_logs": {}, "extra_data_text": false}.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/zksync/collect
python3 -B make_swap_topics.py zksync .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 -B census_l2.py --chain zksync --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 -B fetch_defillama.py zksync-era ../defillama-dexs.json > defillama.log 2>&1
python3 -B token_prices_l2.py --chain zksync --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh
python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 -B make_doc_excerpts.py zksync .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json
python3 -B write_manifest_l2.py zksync ..                                  # regenerates this file
```

Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 583 | 31866 |
| txs-001.csv.gz | 624 | 43791 |
| reverted-001.csv.gz | 22 | 1540 |
| candidates-001.jsonl.gz | 244 | 130156 |
| topic0-counts.csv.gz | 108 | 8783 |
| swap-topics.csv | 22 | 10997 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 24 | 1858 |
| prices-defillama-historical.jsonl.gz | 3 | 1699 |
| native-price-chart-defillama.json | (JSON document) | 749 |
| defillama-dexs.json | (JSON document) | 462732 |
| defillama-dexs.fetch.json | (JSON document) | 141 |
| token_prices.fetch.json | (JSON document) | 538 |
| window.json | (JSON document) | 2584 |
| docs/excerpts.jsonl | 7 | 4548 |

Candidate counts by criterion: A = 22, B = 222. Transactions: 624; status-0 transactions: 22; distinct topic0 keys: 108; receipts not in the block's transaction list: 0.

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
* **defillama-dexs.json**: raw response of `https://api.llama.fi/overview/dexs/zksync-era` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes.
* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).

### swap-topics.csv (verification in this window)

| topic0 / rule | signature | verified in window |
|---|---|---|
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0x131ceafcd8d3bb1f75dca5214a5d8b4579f6aa9538cfb126396918cbfd880bba |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0x3ab953608918c40d19b792b8e858c1da247d9472df2300ac7b4acabefa23b826 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0xf59555b9f12dc3a6f7a14dc7148abc03ad296a58ccd65315d410777ac2c84ef3 |
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
| https://docs.zksync.io/zksync-network/zksync-era | 200 | 2026-10-01T04:22:46Z |  |
| https://docs.zksync.io/zksync-protocol/era-vm/transactions/transaction-lifecycle | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.zksync.io/zksync-protocol/era-vm/transactions/blocks | 200 | 2026-10-01T04:22:47Z |  |
| https://docs.zksync.io/zksync-protocol/era-vm/contracts/bootloader | 200 | 2026-10-01T04:22:48Z |  |
| https://docs.zksync.io/zksync-protocol/era-vm/transactions/fee-model | 200 | 2026-10-01T04:22:48Z |  |
| https://docs.zksync.io/zk-stack/components/server | 200 | 2026-10-01T04:22:49Z |  |
| https://docs.zksync.io/zksync-network/zksync-os | 200 | 2026-10-01T04:22:49Z |  |
| https://docs.zksync.io/zksync-protocol/era-vm/contracts/system-contracts | 200 | 2026-10-01T04:33:13Z |  |

Excerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):

| id | source URL | fetched (UTC) | text (start) |
|---|---|---|---|
| zksync-01 | https://docs.zksync.io/zksync-network/zksync-era | 2026-10-01T04:22:46Z | * Sequencer — Orders and executes transactions off-chain to produce state updates. |
| zksync-02 | https://docs.zksync.io/zksync-protocol/era-vm/transactions/transaction-lifecycle | 2026-10-01T04:22:47Z | Users submit their transactions to the sequencer, whose role is to collect and execute these transactions using the L2 Virtual Machine, EraVM. The sequencer als ... |
| zksync-03 | https://docs.zksync.io/zksync-protocol/era-vm/transactions/transaction-lifecycle | 2026-10-01T04:22:47Z | The sequencer collects transactions into blocks and, to enhance user experience, ensures quick soft confirmations through small block sizes. |
| zksync-04 | https://docs.zksync.io/zksync-protocol/era-vm/transactions/transaction-lifecycle | 2026-10-01T04:22:47Z | * maxPriorityFeePerGas : Recommended to be set to 0 for ZKsync transactions. ZKsync Chains do not have a concept of priority fees; therefore, the maxPriorityFee ... |
| zksync-05 | https://docs.zksync.io/zksync-protocol/era-vm/transactions/blocks | 2026-10-01T04:22:47Z | While L2 blocks are crucial, their importance will increase with the transition to a decentralized sequencer. Currently, they serve mainly as a compatibility fe ... |
| zksync-06 | https://docs.zksync.io/zk-stack/components/server | 2026-10-01T04:22:49Z | maintain Layer 2 (L2) state, and manage the order of incoming transactions. |
| zksync-07 | https://docs.zksync.io/zksync-protocol/era-vm/contracts/system-contracts | 2026-10-01T04:33:13Z | L2BaseToken Address: 0x000000000000000000000000000000000000800a MsgValueSimulator Address: 0x0000000000000000000000000000000000008009 Unlike Ethereum, EraVM doe ... |

## Chain-specific notes (descriptive)

* Transaction `type` values in txs-001.csv.gz (rows): 0: 338, 2: 186, 113: 98, 255: 2.
* `miner` values in blocks.csv.gz (blocks): 0x0000000000000000000000000000000000000000: 583.
* Stack: ZKsync Era (EraVM) (docs/ excerpts zksync-01 to zksync-07). Gas token: ETH.
* Transaction types in txs-001.csv.gz include 113 (= 0x71, EIP-712) and 255 (= 0xff, L1->L2 priority transactions). `miner` is 0x0000000000000000000000000000000000000000 and `extra_data` is `0x` in every block. Receipts carry `l1BatchNumber`, `l1BatchTxIndex` and `l2ToL1Logs` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).
* 0x000000000000000000000000000000000000800a is the L2BaseToken system contract, which holds ETH balances (docs/ excerpt zksync-07). It emits logs with topic0 0xddf252ad... and 3 topics. census.py counts them as ERC-20 Transfer logs for criterion B like those of any other emitter (shared definition, unchanged). Their count in candidate txs is in tokens-onchain-meta.csv.gz (column n_transfer_logs_in_candidates); its decimals()/symbol()/name() calls reverted (error columns of that file).
* Measured block interval in this window: about 6.18 s, so the 60-minute window holds 583 blocks. The docs page stored as docs/docs.zksync.io_zksync-protocol_era-vm_transactions_blocks.txt states 1 second (excerpt zksync-05). The window rule is by timestamp, as for every chain.

## Coverage limits and gaps

* Single contiguous window: 60 min of chain time, 2026-10-01T03:18:09Z to 2026-10-01T04:18:08Z. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day.
* Gap blocks: 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).
* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.
* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).
* Token metadata read at block tag 'latest' after the window (2026-10-01T04:24:41Z), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price.
* DefiLlama per-chain DEX overview fetched once (2026-10-01T04:19:14Z), default query parameters.
* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.

## Verified inventory (2026-10-01)

Generated by collect/write_manifest_l2.py at 2026-10-01T04:35:45Z by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| blocks.csv.gz | 31,866 | 583 rows + header | 606f569362b4a7fc453e8e69e6b75824da5d4fe0d74abff8de8eb6de8b5b8cd3 | not ignored |
| candidates-001.jsonl.gz | 130,156 | 244 JSON lines | d94072237e63844446212ebadbb62ed630ac0b8bea14de555cd7c337d1bf587f | not ignored |
| collect/census.log | 1,583 | 6 lines | 3450f9263116490db33f47dab2a6606b475ff47316281d1143127e21ef03f7ab | not ignored |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | not ignored |
| collect/census_l2.py | 795 | 21 lines | e2efb5a4959c7374bca844ccb37b373040c02ddf9e07308c0f82aba00da5a55c | not ignored |
| collect/defillama.log | 136 | 1 line | f6f704f6788a6107984126958f8d6e96fa09a9892fb933c4cf91dc10921c0adc | not ignored |
| collect/docs.log | 1,038 | 8 lines | cb4b015f674d6fc84eec694e2dd619d0730a9c6273b17f163d119e9786ef9468 | not ignored |
| collect/docs_excerpts_spec.json | 1,648 | 1 JSON document | c90564d119ca023bd7b7fae89f7790e252feeabcc7772da92e9a42b564b4ff0f | not ignored |
| collect/docs_urls.txt | 503 | 8 lines | 03b3c0f5a77cef17a7178ea2a9956e4f24a456eaceb218fb4e33322b4b990720 | not ignored |
| collect/excerpts.log | 105 | 1 line | 71f9c1b861b01f6e584ad0eb0dad347790da905e67ebb481d14104148660aef0 | not ignored |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | not ignored |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | not ignored |
| collect/l2_config.py | 4,659 | 60 lines | d1e10e918809ca4c395d3b0fdd75547488f584ab73b3a52d357a3482bd2edb83 | not ignored |
| collect/make_doc_excerpts.py | 2,448 | 41 lines | 87fbff40dd76129668a4cfdc0d8d91bccdf1c5b42772591c81f9cd4239a31054 | not ignored |
| collect/make_swap_topics.log | 33 | 1 line | de9393c0f91f1f650434a95aeffecb6a12ca7744c05fa142e0f2cfc7ff7f0a11 | not ignored |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | not ignored |
| collect/run_token_prices_l2.sh | 433 | 7 lines | 8dbd0fe40e1dd416cc39c2ec7abacbe62ab279489f0e50a6bc1869bfd1a60867 | not ignored |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | not ignored |
| collect/token_prices.log | 594 | 3 lines | 8efd2cb19d17ab20e7604016e876cdde72d91e266257580ed1a0ae8d6aec3e51 | not ignored |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | not ignored |
| collect/token_prices_l2.py | 802 | 21 lines | 395d8986c4e14ebd2974a7162b30c3f225f10353fa1cb0da2b14f75699df7185 | not ignored |
| collect/write_manifest_l2.py | 27,922 | 294 lines | 90e7daa9c5f2a79c0bae3bdd8075ee16536e00ddd0eb6fc5013ec96519145ef0 | not ignored |
| defillama-dexs.fetch.json | 141 | 1 JSON document | 0525f742f8fa1833eeb148c380a574aa58184aee7a511cb6b64ec13d0fe93814 | not ignored |
| defillama-dexs.json | 462,732 | 1 JSON document | 4d39a1ee00d6becf82065781d9d6a37984d45ebcf218b95f15e8d8565520c6d2 | not ignored |
| docs/docs.zksync.io_zk-stack_components_server.html.gz | 49,643 | 221 lines (decompressed) | 3d506bea63dcbadcc9d956d774a53fac5e886da7014f972f178520eaa64fdb45 | not ignored |
| docs/docs.zksync.io_zk-stack_components_server.txt | 3,563 | 184 lines | d17d360712a60635b6b92fe95104256f764fafa69b1090dbe4247ffef641a336 | not ignored |
| docs/docs.zksync.io_zksync-network_zksync-era.html.gz | 52,611 | 225 lines (decompressed) | 71d3003b2273e9739db3b29196914d29c4c4b473deffd1256c396e86e0938fdb | not ignored |
| docs/docs.zksync.io_zksync-network_zksync-era.txt | 4,853 | 204 lines | fe4b523c2bcf7c52c308e693b0e13c5ec48bea1a59b6a0ee0f8c126d97f5f6a1 | not ignored |
| docs/docs.zksync.io_zksync-network_zksync-os.html.gz | 54,575 | 226 lines (decompressed) | 804e84df116f684049c1e63594d8b07c185d24a8499c73e7c2f0f0108750700c | not ignored |
| docs/docs.zksync.io_zksync-network_zksync-os.txt | 6,000 | 262 lines | cb41469e11c0a03f2ff206d53f769409f84ef6d7def5059bb59181d4707878dc | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_contracts_bootloader.html.gz | 74,840 | 367 lines (decompressed) | 6ea31e4d2f28ad8727d79f202717ae974c2888d322f152f975c7b653b1b6f6d3 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_contracts_bootloader.txt | 22,428 | 601 lines | 296cfad59abc83912625f1c952fc10d243540a2c28efeeffe7c60521cad2fc71 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_contracts_system-contracts.html.gz | 74,144 | 328 lines (decompressed) | ec262edaa9f83fbe83164911cf4f339b85d9270b911d1dbf437d338b7b202fb3 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_contracts_system-contracts.txt | 22,948 | 573 lines | fe4fad57a07006d78c6d1f59798b2168876792e796e725381e4348eaab11b025 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_blocks.html.gz | 64,428 | 267 lines (decompressed) | 1c53b365d7ce0a67d1af55b89cc23d1829ef0f009fd0c1cef70da41f083fde02 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_blocks.txt | 14,195 | 404 lines | 857769be8d5f10cfbcd888c5762fee49edc8807008b99450085daf9498046442 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_fee-model.html.gz | 56,734 | 246 lines (decompressed) | 8fcc74dbc7e1a9fd8d7703e06e507a280dc9da81d2c24cd6cf9f0a72b304b585 | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_fee-model.txt | 8,964 | 285 lines | 0b576ebf728e72808d504ff4ae0413caabe28712f97833d465d56a1e343b314c | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_transaction-lifecycle.html.gz | 62,330 | 252 lines (decompressed) | ec0c219f0f194e577c7cf1dc16eecef766006dcf585c32dff859a89d91a610af | not ignored |
| docs/docs.zksync.io_zksync-protocol_era-vm_transactions_transaction-lifecycle.txt | 9,684 | 362 lines | 49b1a1c310feb3d9cbb3c1a60f1dadbb0d0ef5ca8cf8e535156684e7c74d94ce | not ignored |
| docs/excerpts.jsonl | 4,548 | 7 JSON lines | 650751a66a9163f5f7669f7f94ec8d1d26a07eb43a026c5515230fb31d606484 | not ignored |
| docs/index.csv | 1,718 | 8 rows + header | ae84f495ab2668ae92b4049709d9d7ddcb0b6f164f1173f91e5f92d523df28cc | not ignored |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | not ignored |
| native-price-chart-defillama.json | 749 | 1 JSON document | 4dd5867fdd75a12d8d36d3d506a61dacf8bd28f0f09b720c332a3078fc7ba3b0 | not ignored |
| prices-defillama-historical.jsonl.gz | 1,699 | 3 JSON lines | 952c075ebdd027004f87b2c11d13290b43eb4ff13e92e2b43940977e162a3c1c | not ignored |
| reverted-001.csv.gz | 1,540 | 22 rows + header | 89e3c89c1baa72513e2751c5ad0f17ac4285073e67bcac40926115f4c113de43 | not ignored |
| swap-topics.csv | 10,997 | 22 rows + header | 370eca42697e3d063356bfbdc16e04d6c1df3a776644fc478b3a60e600a4553a | not ignored |
| token_prices.fetch.json | 538 | 1 JSON document | 2e7d19362553ebef8228edda01933d3d6de4cddea48f40ac944a94fe664b79fd | not ignored |
| tokens-onchain-meta.csv.gz | 1,858 | 24 rows + header | 26ecd1623d79bff78351cae36a9bcd82c92396a4c1379c9aa6a6527d00434ce7 | not ignored |
| topic0-counts.csv.gz | 8,783 | 108 rows + header | 458018c82057d78d5f6308d200d6665214e0ab14c5cf5a541e238d1464590564 | not ignored |
| txs-001.csv.gz | 43,791 | 624 rows + header | d7a64d5a54b678ee431c03550ce8c18509bf6ab7c74b69f1a095c03e4c21dd00 | not ignored |
| window.json | 2,584 | 1 JSON document | c55ba19e6d0b600015fea88faeb30149fcba11745da105fb2ae84c208a4a5334 | not ignored |
| MANIFEST.md | (this file) | documentation | not recorded | not ignored |

Files: 52 plus this MANIFEST.md. Largest file: 462,732 bytes (limit 90 MB).
