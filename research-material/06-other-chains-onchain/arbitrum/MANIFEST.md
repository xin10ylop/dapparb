# Arbitrum One: on-chain arbitrage census (raw material)

Status: COMPLETE (finalized 2026-10-01). All collectors for this directory finished: sentinels EVM_CENSUS_ARBITRUM.DONE and EVM_TOKENPRICES_ARBITRUM.DONE (sentinel files are git-ignored; their text is reproduced in `../MANIFEST.md`). Last data write 2026-09-30T21:21Z, before the ~23:00Z container restart of 2026-09-30; nothing in this directory was interrupted or re-run. Every file was re-verified on 2026-10-01 (section 'Verified inventory (2026-10-01)').

Collector's status line (kept as written): census COMPLETE (sentinel `.sentinels/EVM_CENSUS_ARBITRUM.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_ARBITRUM.DONE`). Ordering docs: COMPLETE (see docs/).

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md` (the same lines carry Q-IDs in `../MANIFEST-evm.md`).

| Line | Files in this directory |
|---|---|
| 1 | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |
| 4 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json, defillama-dexs.json, defillama-dexs.fetch.json |
| 5 | candidates-001.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz (base_fee_per_gas), txs-001.csv.gz (effective_gas_price, timeboosted), docs/, arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz |
| 6 | docs/, arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz, txs-001.csv.gz (timeboosted column) |
| 7 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json, tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json |
| 8 | blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json |

Correction 2026-10-01: the collector's table in this section used Q-IDs and short notes; it is restated above by line number. The collector also mapped files to a ninth ID, Q-GAPS ("Would the gaps change the answer?"), which is not one of the 8 question lines; those entries were dropped.

## Window (pinned)

| Item | Value |
|---|---|
| Chain id | 42161 |
| Block range (inclusive) | 510447028 to 510460284 (13257 blocks) |
| Block timestamps | 1790798841 (2026-09-30T20:07:21Z) to 1790802440 (2026-09-30T21:07:20Z) |
| Window rule | all blocks with timestamp in (end_timestamp - 3600 s, end_timestamp]; end block = eth_blockNumber at pin time minus 40 |
| Head at pin time | 510460324 (pinned 2026-09-30T21:07:32Z) |
| Measured block interval | 0.271500 s = (end_timestamp - start_timestamp) / (end_block - start_block) |
| Collection finished | 2026-09-30T21:09:43Z |
| Integrity checks | parent-hash chain breaks: 0; blocks missing from blocks.csv: 0; first/last block hash re-read from RPC after collection and matched: True; gap blocks: 0 |

## Sources / endpoints

* JSON-RPC primary: `https://arbitrum-one-rpc.publicnode.com` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of 20 block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: `https://arbitrum.drpc.org`.
* Requests actually sent (HTTP): {"https://arbitrum-one-rpc.publicnode.com": 729}. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): {"https://arbitrum-one-rpc.publicnode.com|retry": 66, "https://arbitrum-one-rpc.publicnode.com|item-retry": 1320}.
* DefiLlama: `https://api.llama.fi/overview/dexs/arbitrum` fetched 2026-09-30T21:10:31Z (HTTP 200, 2008705 bytes), stored unmodified as defillama-dexs.json.
* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (2026-09-30T21:13:37Z) on https://arbitrum-one-rpc.publicnode.com, https://arbitrum.drpc.org. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = [1790798841, 1790800640, 1790802440] and `https://coins.llama.fi/chart/coingecko:ethereum?start=1790798841&span=13&period=5m`.
* Official docs: see docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below.
* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.

## Reproduce

```bash
export PATH=/root/.foundry/bin:$PATH
cd /home/user/dapparb/research-material/06-other-chains-onchain/arbitrum/collect
python3 make_swap_topics.py arbitrum ..            # writes ../swap-topics.csv (topic0 via cast keccak)
setsid nohup python3 census.py --chain arbitrum --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent
python3 fetch_defillama.py arbitrum ../defillama-dexs.json > defillama.log 2>&1
python3 token_prices.py --chain arbitrum --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)
python3 fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1
python3 arbitrum_chain_state.py > arbitrum_chain_state.log 2>&1   # precompile reads at the window blocks
python3 write_manifest.py arbitrum ..               # regenerates this file from the metadata files
```

Note (2026-10-01): this MANIFEST.md was edited by hand during finalization (status line, 'Question lines served', the 'Verified inventory (2026-10-01)' section and the notes marked 2026-10-01). Re-running write_manifest.py would regenerate the collector's original version without these edits.

Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.

## Files, schemas, row counts

All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.

| File | Rows (excluding header) | Bytes |
|---|---|---|
| blocks.csv.gz | 13257 | 770291 |
| txs-001.csv.gz | 62119 | 4321791 |
| reverted-001.csv.gz | 4683 | 270010 |
| candidates-001.jsonl.gz | 2474 | 3388317 |
| extra-timeboost-auction-logs.jsonl.gz | 0 | 860 |
| topic0-counts.csv.gz | 1652 | 139609 |
| swap-topics.csv | 22 | 12284 |
| gaps.csv | 0 | 20 |
| tokens-onchain-meta.csv.gz | 245 | 16261 |
| prices-defillama-historical.jsonl.gz | 21 | 24105 |
| native-price-chart-defillama.json | (JSON document) | 749 |
| defillama-dexs.json | (JSON document) | 2008705 |
| defillama-dexs.fetch.json | (JSON document) | 140 |
| token_prices.fetch.json | (JSON document) | 554 |
| window.json | (JSON document) | 3067 |
| arbitrum-chain-state.json | (JSON document) | 6920 |

Candidate counts by criterion: A = 667, B = 1807. Transactions: 62119; status-0 transactions: 4683; distinct topic0 keys: 1652.

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

Arbitrum: miner is the constant sequencer address 0xa4b000000000000000000073657175656e636572; extra_data is the header sendRoot field as returned by Nitro.

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
| 0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822 | `Swap(address,uint256,uint256,uint256,uint256,address)` | yes: 0xb13df865ca7b6183b8d1bf8b78423c18aa8b4ff95ceeace31c4ff2d9a483bd4f |
| 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67 | `Swap(address,address,int256,int256,uint160,uint128,int24)` | yes: 0xfe77d0fea88289617996bd0d3034891727329cf0d7934e3d2e964105c8d19a14 |
| 0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)` | yes: 0x767724178c72cae5ca04d937050e193ce28e6ae4c9a776aebdcec0e70a983b62 |
| 0x121cb44ee54098b1a04743c487e7460d8dd429b27f88b1f4d4767396e1a59f79 | `Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)` | yes: 0xe79665a7a10a843ccf6596617aef5cbb4404464005ac12e0bb1548a35546523c |
| 0xb3e2773606abfd36b5bd91394b3a54d1398336c65005baf7bf7a05efeffaf75b | `Swap(address,address,uint256,uint256,uint256,uint256)` | no |
| 0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` | yes: 0x13bbffbfdf2a36ab5c4fd67174440a5c866d1a1f9e5c39f3d116155c813df188 |
| 0x04206ad2b7c0f463bff3dd4f33c5735b0f2957a351e4f79763a4fa9e775dd237 | `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)` | no |
| 0x3e8aae37f890eb1f9d63dd4d2062f3f0be757848a0f0760e4f3e53dad556e861 | `Swap(bytes32,address,int128,int128,uint24,uint24,uint16)` | no |
| 0x2170c741c41531aec20e7c107c24eecfdd15e69c9bb0a8dd37b1840b9e0b207b | `Swap(bytes32,address,address,uint256,uint256)` | yes: 0x3f78bb1661d8ff95df8ae8f44e1ce5345f79eaa35904cef0ecb59ac29d6bf3fb |
| 0x0874b2d545cb271cdbda4e093020c452328b24af12382ed62c4d00f5c26709db | `Swap(address,address,address,uint256,uint256,uint256,uint256)` | yes: 0xce85f20d09103a008ee6f589ee62fa0c6a5d438f8d21e6e0cd20b14501d8c1c9 |
| 0x8b3e96f2b889fa771c53c981b40daf005f63f637f1869f707052d15a3dd97140 | `TokenExchange(address,int128,uint256,int128,uint256)` | yes: 0x39e9da19c6ba81942eaf82d11414704e86809329f746049070fbd6ddd83063c7 |
| 0xd013ca23e77a65003c2c659c5442c00c805371b7fc1ebd4c206c41d1536bd90b | `TokenExchangeUnderlying(address,int128,uint256,int128,uint256)` | no |
| 0xb2e76ae99761dc136e598d4a629bb347eccb9532a5f8bbd72e18467c3c34cc98 | `TokenExchange(address,uint256,uint256,uint256,uint256)` | yes: 0x8254506eac2977325ad9d36ab2280074227add4c2f7bb80ec8ef725b4bb5ad61 |
| 0x143f1f8e861fbdeddd5b46e844b7d3ac7b86a122f36e8c463859ee6811b1f29c | `TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)` | yes: 0xb439eec68de0030ab7d8ea382c5e8930954467b4fbe5d73543841ba4542b9e0e |
| 0xad7d6f97abf51ce18e17a38f4d70e975be9c0708474987bb3e26ad21bd93ca70 | `Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)` | yes: 0x8254506eac2977325ad9d36ab2280074227add4c2f7bb80ec8ef725b4bb5ad61 |
| 0x103ed084e94a44c8f5f6ba8e3011507c41063177e29949083c439777d8d63f60 | `PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)` | yes: 0x11052dddc4e3f804033f165e8e1f88a1e62c23a31f9714095d52419495744141 |
| 0xdc004dbca4ef9c966218431ee5d9133d337ad018dd5b5c5493722803f75c64f7 | `Swap(bool,uint256,uint256,address)` | yes: 0xaf3cbce4f37878bfe5a53ed40bf5cb2da99176a54ca359144ec301e374064e3e |
| 0x0e8e403c2d36126272b08c75823e988381d9dc47f2f0a9a080d95f891d95c469 | `WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)` | yes: 0x0ee1cc82dff575e97caa2d5d74f42662f638e583b4457e29f6e841ebe12359f8 |
| 0xc2c0245e056d5fb095f04cd6373bc770802ebd1e6c918eb78fdef843cdb37b0f | `DODOSwap(address,address,uint256,uint256,address,address)` | yes: 0x24f39ee8399ee66ca70c70d03f88cd09eff08b3dd172aff992a2511de86a7f4c |
| 0xcd3829a3813dc3cdd188fd3d01dcf3268c16be2fdd2dd21d0665418816e46062 | `Swap(address,address,address,uint256,uint256)` | yes: 0x400e8653993974884e28c1d57e1c01c15c6b872b2559561d8e1dfaea3bf7fadf |
| 0x54787c404bb33c88e86f4baf88183a3b0141d0a848e6a9f7a13b66ae3a9b73d1 | `Swap(address,address,address,uint256,uint256,address)` | no |
| log0 @ 0x00000000000014aa86c5d3c41765bb24e11bd701 | `(anonymous log0, 116-byte data: locker, poolId, balanceUpdate, stateAfter)` | no |

### extra-timeboost-auction-logs.jsonl.gz

Every log emitted in the window by the Timeboost ExpressLaneAuction contract 0x5fcb496a31b7ae91e7c9078ec662bd7a55cd3079 (address from docs/how-to-use-timeboost), one JSON object per log: block_number, block_timestamp, tx_index, tx_hash, from, to, status, log (verbatim). Rows in this window: 0.

### arbitrum-chain-state.json

Raw eth_call results of Arbitrum precompile getters at the window start block, window end block and 'latest' (collect/arbitrum_chain_state.py): ArbSys(0x64).arbOSVersion(), ArbOwnerPublic(0x6b).getCollectTips(), getScheduledUpgrade(), getNetworkFeeAccount(). Fields per result: at, block_tag, endpoint, call, to, data (selector from `cast sig`), result_raw, error, decoded_derived (ABI words as base-10 / address), arbos_version_derived (= arbOSVersion() - 55, per Nitro precompiles/ArbSys.go line 68 'Nitro starts at version 56'; source stored in docs/). Historical state came from arbitrum-one.public.blastapi.io and arb1.arbitrum.io (arbitrum.drpc.org answered 'Unknown state', publicnode refuses historical calls).

### tokens-onchain-meta.csv.gz

One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).

### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json

One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.

### defillama-dexs.json

Raw response of `https://api.llama.fi/overview/dexs/arbitrum` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.

### docs/

Official documentation on transaction ordering, fetched verbatim. For each URL: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION method, then the full visible text or raw markdown), plus the raw body (`.html.gz`, `.raw.gz` for markdown, or `.pdf`). `index.csv` lists every URL attempted.

| URL | HTTP | fetched (UTC) | note |
|---|---|---|---|
| https://docs.arbitrum.io/how-arbitrum-works/timeboost/gentle-introduction | 200 | 2026-09-30T21:11:16Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/timeboost/gentle-introduction.md | 200 | 2026-09-30T21:11:16Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/timeboost/how-to-use-timeboost | 200 | 2026-09-30T21:11:17Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/timeboost/how-to-use-timeboost.md | 200 | 2026-09-30T21:11:17Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/timeboost/timeboost-faq.md | 200 | 2026-09-30T21:11:18Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/deep-dives/sequencer.md | 200 | 2026-09-30T21:11:18Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/deep-dives/sequencer-transaction-flow.md | 200 | 2026-09-30T21:11:19Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/priority-gas-auction/pga | 200 | 2026-09-30T21:11:19Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/priority-gas-auction/pga.md | 200 | 2026-09-30T21:11:20Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/priority-gas-auction/fast-feed.md | 200 | 2026-09-30T21:11:20Z |  |
| https://docs.arbitrum.io/how-arbitrum-works/priority-gas-auction/use-fast-feed.md | 200 | 2026-09-30T21:11:21Z |  |
| https://docs.arbitrum.io/launch-arbitrum-chain/chain-config/sequencer/pga.md | 200 | 2026-09-30T21:11:21Z |  |
| https://docs.arbitrum.io/launch-arbitrum-chain/chain-config/sequencer/timeboost.md | 200 | 2026-09-30T21:11:22Z |  |
| https://docs.arbitrum.io/launch-arbitrum-chain/chain-config/costs/priority-fees.md | 200 | 2026-09-30T21:11:23Z |  |
| https://docs.arbitrum.io/arbitrum-essentials/precompiles/reference.md | 200 | 2026-09-30T21:18:33Z |  |
| https://raw.githubusercontent.com/OffchainLabs/nitro/v3.11.3/precompiles/ArbSys.go | 200 | 2026-09-30T21:18:34Z |  |

### collect/

census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py (+ docs_urls.txt where used), token_prices.py, run_token_prices_all.sh, write_manifest.py and their logs (census.log, make_swap_topics.log, defillama.log, docs.log, token_prices.log). Identical copies of these scripts are in every sibling chain directory and in ../_shared_collect/. Arbitrum only: arbitrum_chain_state.py (+ arbitrum_chain_state.log).

## Coverage limits and gaps

* Single contiguous window per chain (60 min of chain time ending 2026-09-30T21:07:20Z); one weekday evening (UTC), no other days or times of day.
* Gap blocks (unfetchable after all retries): 0 (gaps.csv). Blocks missing from blocks.csv: 0. Parent-hash breaks: 0.
* eth_getBlockByNumber was called with hydrated=false (per the shared definition): transaction input/calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are NOT collected. Priority fee actually paid per gas is derivable from effective_gas_price and base_fee_per_gas.
* No call traces: internal native-token transfers (e.g. direct payments to the block builder / coinbase on Ethereum, native-ETH legs of Uniswap V4 or WETH unwraps) and revert reasons are not collected.
* Logs are stored only for candidate transactions (criteria A/B). Transactions with a single swap log and fewer than 3 ERC-20 transfers from 2 tokens are in txs-*.csv only (no logs). topic0-counts.csv.gz counts logs of all transactions.
* Criterion A uses only the signatures in swap-topics.csv; the match is on topic0 (plus the Ekubo log0 address rule) with no check of the emitting contract. Venues whose swap events use other signatures are not matched by A (e.g. Ambient/CrocSwap, RFQ/PMM venues such as Hashflow/Bebop/Native, 0x and 1inch limit orders, UniswapX fills, Bancor, Uniswap V1, Maverick V1, Trader Joe LB v2.0, GMX V2, KyberSwap classic, Clipper, Integral); such transactions appear as candidates only if they meet criterion B. A signature not observed in this window is listed with an empty verified_example_tx (not verified on this chain).
* ERC-20 Transfer is identified as topic0 0xddf252ad... with exactly 3 topics; tokens emitting non-standard transfer events and native-token movements are not counted for criterion B.
* Token metadata was read at block tag 'latest' shortly after the window, not at the window blocks. DefiLlama prices are DefiLlama's own aggregates (confidence field included) and are absent for tokens DefiLlama does not price.
* No mempool / pending-transaction data, no private-orderflow or bundle data, no flashblock / preconfirmation-level ordering data (block-level receipts only).
* The DefiLlama DEX overview was fetched once (2026-09-30T21:10:31Z) with default query parameters.
* Timeboost: the ExpressLaneAuction contract emitted 0 logs in this window (extra-timeboost-auction-logs.jsonl.gz); the receipt field `timeboosted` is captured per tx. docs/ contains the Timeboost pages and the newer PGA (Priority Gas Auction) / Fast Feed pages as published on 2026-09-30; which policy was active during the window is not determined here.
* Arbitrum requested window is 60 min (~14,400 blocks at 250 ms nominal); the chain produced 13257 blocks in it. No reduction to 20 min was needed.
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana (separate collector in ../solana), and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) are not collected here.

## Verified inventory (2026-10-01)

Verified on 2026-10-01 by streaming every file in this directory (no data file was modified). Checks: `gzip -t` on every .gz file; CSV files parsed with Python's csv module (rows exclude the header line); every JSONL line and every JSON document parsed with Python's json module; sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 67 files (67 committed, 0 local-only). All 24 .gz files pass `gzip -t`; every JSON document and JSONL line parses; every CSV record has as many fields as its header. The row counts in 'Files, schemas, row counts' above and the candidate counts by criterion equal the verified counts below (no differences). Largest committed file: txs-001.csv.gz (4,321,791 bytes); no committed file exceeds 90 MB.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| arbitrum-chain-state.json | 6,920 | 1 JSON document | eef9f984a1876d44ffa58cc64e341fffa93ca266f1ab838535c3da9d7d021cc7 | committed |
| blocks.csv.gz | 770,291 | 13,257 rows + header | 62a2152c993d9a779140e9c580a0756a90630e76430fb55b1d13427e95becf1d | committed |
| candidates-001.jsonl.gz | 3,388,317 | 2,474 JSON lines (criterion A 667, B 1,807) | aea7aa0b4a7c0be6db209e557cb949512cd7eb2ef4dc8647fbcf179eb97abbab | committed |
| collect/arbitrum_chain_state.log | 6,921 | 225 lines | dbd14e932aed5a02caaffa1a185ee33511c0756798fe591f687be4f39af85fa0 | committed |
| collect/arbitrum_chain_state.py | 3,639 | 51 lines | b0612b4085f5d32b1b4997113a566f350e9e308fa842974ee043dd4b9bd0785a | committed |
| collect/census.log | 4,999 | 17 lines | 688a6bf96c454f340fa269cd9a1bacdd18289d453b8fcb745f59308ebb7a1eb6 | committed |
| collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| collect/defillama.log | 135 | 1 line | 3daed94cb0585c08d52173235bd39faa1a35b25a15fea31d98e3f5fabb2813d5 | committed |
| collect/docs.log | 2,514 | 16 lines | e7a2291c353d6290b4a8b208084941e031a5ea520bcd9dd61eb5192099f152ad | committed |
| collect/docs_urls.txt | 1,225 | 16 lines | f32c3406972c3ae91c24f7b33a1f225c774ae5d125281ff2299b2256421d77a7 | committed |
| collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| collect/make_swap_topics.log | 100 | 1 line | 724de39a7f73cbf69c4f3a081f7147c150795110b33b287109df40b4de793138 | committed |
| collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| collect/run_token_prices_all.log | 0 | empty (0 bytes) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | committed |
| collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| collect/token_prices.log | 611 | 3 lines | 87640b77dce4b82717b3539160b1da49351b77af5193d8ad5215a61f90255c6f | committed |
| collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| defillama-dexs.fetch.json | 140 | 1 JSON document | 75d052dea913688e9de15cefb5e025a6b7ac271110c7ed52d457587c3e1f8139 | committed |
| defillama-dexs.json | 2,008,705 | 1 JSON document | 4fc70dee322a65402c750d47eea2a081d0a179408410ec065ea457c4c25edd89 | committed |
| docs/docs.arbitrum.io_arbitrum-essentials_precompiles_reference.md.raw.gz | 13,503 | 425 lines (decompressed) | 40422fb37b7082758969e8de410d6817688924aaf9e0d0e6075ff3e977213c37 | committed |
| docs/docs.arbitrum.io_arbitrum-essentials_precompiles_reference.md.txt | 131,836 | 431 lines | 39f97813f8a999eda627430a4ba15c7478ce286e5ab5d96b643bdb7f6ddec6b8 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_deep-dives_sequencer-transaction-flow.md.raw.gz | 6,929 | 158 lines (decompressed) | 5d42c9f71207a557a3b3b26b05dd53673cd18f4891cffb153fb0d00743e45708 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_deep-dives_sequencer-transaction-flow.md.txt | 21,103 | 164 lines | debbc7b09998c591aaee8a28be13be8ec47c2e7569dc658956c0808ada55ffde | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_deep-dives_sequencer.md.raw.gz | 5,320 | 118 lines (decompressed) | 3875ea85cb409d190d5585e2869772ab99a9ecbba785bb36118a2100c9679fe7 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_deep-dives_sequencer.md.txt | 13,931 | 124 lines | f0d7db5e4928003d47dd15f2e065a2932655ba369487a5d9c03dfac4c0d7e69b | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_fast-feed.md.raw.gz | 3,738 | 122 lines (decompressed) | 764a767377389d8a22fc002c37ed4ac0dab248baf20b107f521928bfa067eb23 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_fast-feed.md.txt | 10,353 | 128 lines | 9c8117a5e74a6f981a6e2f32c72ab86f8cb5614bf2c377cd0b02e4ed27092125 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_pga.html.gz | 11,286 | 115 lines (decompressed) | 4047b5dacf5998093d2f8d42815443d4fc8c6b6dd74cabeb38f6776b4ea087c4 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_pga.md.raw.gz | 4,167 | 147 lines (decompressed) | d5ac9c073c73a60f95f53cf72cd1ebb64980ae2f36bc3240b1302c3b714683e9 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_pga.md.txt | 10,851 | 153 lines | 32fb38818cc0ea408f18183f6dba1563a2d1ca5408c531926901961bb80d6df7 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_pga.txt | 11,288 | 284 lines | e92d89cb1bc6f0286e55eaa143f1593593878f9a03d22275655537f17d412452 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_use-fast-feed.md.raw.gz | 6,462 | 369 lines (decompressed) | cc81eb4cfe7eaac33ca87703372d088abe140c422d664acfb04f1bf080dcbc0c | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_priority-gas-auction_use-fast-feed.md.txt | 20,492 | 375 lines | 07355874848dad597e718efd3ca141fcf744eb7a27ce6184f6d566759e2f9521 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_gentle-introduction.html.gz | 27,261 | 74 lines (decompressed) | 30e8dbfb4994a96092e0c545400978cbdba0a14cbda0abe9b85b93be63de4ebe | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_gentle-introduction.md.raw.gz | 3,861 | 83 lines (decompressed) | 15fbce2c5484ffdfdaa228dc5937a064c7702ceca3dc3954f1229d783016a36d | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_gentle-introduction.md.txt | 10,153 | 89 lines | 6ef7284ff9b2342d7a6500495efff10ad2d7752c454d5e93bdd6227bf4212cd5 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_gentle-introduction.txt | 11,310 | 212 lines | f6a7542ca8d1e1d125ebe7ddf7671850c68ef9b2ffba9bbb0698903016274404 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_how-to-use-timeboost.html.gz | 20,170 | 160 lines (decompressed) | 810e7c7c09ab3ac3017ba6f2025d9974eb42f037ec5426f87e8b5630322ebddd | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_how-to-use-timeboost.md.raw.gz | 8,260 | 747 lines (decompressed) | 405751e0dc72a8971bbff7aec02635a22a170b10e83782aa6cfaaf50f5d660ed | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_how-to-use-timeboost.md.txt | 31,845 | 753 lines | 27a17badb6c83021e26816203d5fe148a40a494195045e721017a722ea047f75 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_how-to-use-timeboost.txt | 27,221 | 811 lines | 59aa3d69adb92ee199d473860306a6f76de196e0f31ed4605e517247e0fdafa7 | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_timeboost-faq.md.raw.gz | 6,712 | 153 lines (decompressed) | d1217f01847c471153d8a5068223dd5bc5ef0e9d67662d3b83e86d84efdf13ba | committed |
| docs/docs.arbitrum.io_how-arbitrum-works_timeboost_timeboost-faq.md.txt | 18,511 | 159 lines | 9169915a4b2ba16a9b0e05cdc66f433067e1b04fa126c7d656ed1517337a675f | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_costs_priority-fees.md.raw.gz | 1,404 | 61 lines (decompressed) | 99e9333e588e5480ba98e7ce9cb67c23ed0c84fab79d5a90ed8a84b8f1799112 | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_costs_priority-fees.md.txt | 3,456 | 67 lines | 26681f5f66b6269fa1ecabb72187ada0405d62eaa331945b24526a6dc9aee41b | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_sequencer_pga.md.raw.gz | 1,956 | 99 lines (decompressed) | e780e8eeb9eaf4096830c1cfb09fbc9eaa0bcb3589411251aae32f6c80743fd4 | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_sequencer_pga.md.txt | 4,976 | 105 lines | 130814c1f3505754fe82bcdef44d24987c13da7f904c7e2347ef86fe3222ecf4 | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_sequencer_timeboost.md.raw.gz | 6,126 | 325 lines (decompressed) | 03d6e925ddd8ce52a7cbd6881272799cd04d8052fe8f6bc68a7f594e69179f19 | committed |
| docs/docs.arbitrum.io_launch-arbitrum-chain_chain-config_sequencer_timeboost.md.txt | 20,013 | 331 lines | a4ca60dbbf104fe3477602148e4c74a45aa000d8220e1765533fb0b13ba61dd4 | committed |
| docs/index.csv | 4,036 | 16 rows + header | 00fb3f58a2a4b9853b3826b9fc47d17932ca2d889ebe647a0b981a5ebecd3d2f | committed |
| docs/raw.githubusercontent.com_OffchainLabs_nitro_v3.11.3_precompiles_ArbSys.go.raw.gz | 2,677 | 246 lines (decompressed) | c6a6a1df2a54cd8f479ec495c4b4e4d83c2e854cedd93b9157c0826c51e80e1b | committed |
| docs/raw.githubusercontent.com_OffchainLabs_nitro_v3.11.3_precompiles_ArbSys.go.txt | 8,652 | 252 lines | 35a619fbbbbb538eb2746d0089dba2d0810d91f237579daf391bcc6f96224a07 | committed |
| extra-timeboost-auction-logs.jsonl.gz | 860 | 0 JSON lines | 9c81718bd8581eb291adfedff986bd57694033b5614f04b5ad801a4c3050eef7 | committed |
| gaps.csv | 20 | 0 rows + header | 592ba1730f5d491364d8a9f4874a83533e4aecf1fde0f9e4e3e3792b36cd36f1 | committed |
| native-price-chart-defillama.json | 749 | 1 JSON document | b933a0d288c9272f866348094c52fe13f5c8a1d9f1e939036b717697d539b7e2 | committed |
| prices-defillama-historical.jsonl.gz | 24,105 | 21 JSON lines | 280256ad657738cccc7cc2b2863df1529fb2d2725e29fe63c65a28f2f34b05b4 | committed |
| reverted-001.csv.gz | 270,010 | 4,683 rows + header | a80a774626f8c1091877c0c32bfc3a5242f2feb24492d19d9b5ce1f7a98a909b | committed |
| swap-topics.csv | 12,284 | 22 rows + header | 5d28afdde7a05cf0d14693a99e29793dc6f12d312a497401e8ca8b59ddfa2c86 | committed |
| token_prices.fetch.json | 554 | 1 JSON document | ed4dcb9c0f58b0addc67f9784b77a0aaf7d260e1dfa10e073628843a6a25a93a | committed |
| tokens-onchain-meta.csv.gz | 16,261 | 245 rows + header | 0eca5d51d732c77f5adb0919dc4945f5cb4b20f1b60356405451a8988e74c284 | committed |
| topic0-counts.csv.gz | 139,609 | 1,652 rows + header | 36b4c887a299c44f554afc454ac32f968667ee52394e2f204e11e90dbbbd9cc6 | committed |
| txs-001.csv.gz | 4,321,791 | 62,119 rows + header | 24158cab0eee777364b98fdf6ee2918c25160c367aeaae09043c6d828498f0f0 | committed |
| window.json | 3,067 | 1 JSON document | 71abded65f4a568563d387ff075a831d451aa79db5282217fff525f73368f817 | committed |
| MANIFEST.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |
