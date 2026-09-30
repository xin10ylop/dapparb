# Arbitrum One: on-chain arbitrage census (raw material)

Status: census COMPLETE (sentinel `.sentinels/EVM_CENSUS_ARBITRUM.DONE`); DefiLlama DEX overview COMPLETE; token metadata + prices COMPLETE (sentinel `.sentinels/EVM_TOKENPRICES_ARBITRUM.DONE`). Ordering docs: COMPLETE (see docs/).

This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.

## Question lines served (mapping only)

Question-line IDs are defined in `../MANIFEST-evm.md` (verbatim user text there).

| File(s) | Question lines |
|---|---|
| blocks.csv.gz, txs-*.csv.gz, reverted-*.csv.gz, candidates-*.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, window.json | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-STUDIES (Arbitrum $4,700/day line) |
| candidates-*.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz base_fee_per_gas + txs effective_gas_price (priority fee per gas = effective_gas_price - base_fee_per_gas, derivable) | Q-V4LAUNCH (priority-fee share line), Q-GAPS |
| candidates-*.jsonl.gz (all pools active in the window, any pool age / size) + tokens-onchain-meta.csv.gz | Q-OLDV2, Q-SMALLPOOLS (as observed on this chain, not Base) |
| docs/ (official ordering documentation), arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz, txs timeboosted column | Q-BSCORDER (comparison material: ordering policy on this chain), Q-V4LAUNCH (priority-fee ordering) |
| tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json | USD valuation inputs for Q-STUDIES / Q-OTHERCHAINS |
| defillama-dexs.json | Q-OTHERCHAINS (which DEXes exist on the chain and their reported volume; for checking swap-topic coverage) |

Not served here: Q-V4BASE (Base only; see the Base directories under research-material/, e.g. 01-v4-pools and 05-base-onchain).

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
* Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana, and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in docs/ANALYSIS.md 4.1) are not collected here.
