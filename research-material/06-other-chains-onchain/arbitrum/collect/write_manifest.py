#!/usr/bin/env python3
"""Writes <chain_dir>/MANIFEST.md from the collectors' own metadata files (window.json, swap-topics.csv,
docs/index.csv, defillama-dexs.fetch.json, token_prices.fetch.json). Descriptive metadata only.
usage: python3 write_manifest.py <chain> <chain_dir>"""
import csv, glob, gzip, json, os, sys

chain, d = sys.argv[1], os.path.abspath(sys.argv[2])
NAMES = {"arbitrum": "Arbitrum One", "optimism": "OP Mainnet (Optimism)", "unichain": "Unichain",
         "ethereum": "Ethereum mainnet", "polygon": "Polygon PoS"}
SLUG = {"arbitrum": "arbitrum", "optimism": "optimism", "unichain": "unichain", "ethereum": "ethereum", "polygon": "polygon"}
w = json.load(open(os.path.join(d, "window.json")))


def lines(p):
    n = 0
    with gzip.open(p, "rb") as f:
        for _ in f:
            n += 1
    return n


def utc(ts):
    import datetime
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


def size(p):
    return os.path.getsize(os.path.join(d, p)) if os.path.exists(os.path.join(d, p)) else 0


tp = None
if os.path.exists(os.path.join(d, "token_prices.fetch.json")):
    tp = json.load(open(os.path.join(d, "token_prices.fetch.json")))
dl = json.load(open(os.path.join(d, "defillama-dexs.fetch.json"))) if os.path.exists(os.path.join(d, "defillama-dexs.fetch.json")) else None
docs = list(csv.DictReader(open(os.path.join(d, "docs", "index.csv")))) if os.path.exists(os.path.join(d, "docs", "index.csv")) else []
swap = list(csv.DictReader(open(os.path.join(d, "swap-topics.csv"))))
c = w["counts"]
f = w["files"]
status_tp = "COMPLETE" if tp and tp.get("finished_at_utc") else "IN PROGRESS (token_prices.py not finished when this manifest was written; see collect/token_prices.log and .sentinels/EVM_TOKENPRICES_%s.*)" % chain.upper()

L = []
A = L.append
A("# %s: on-chain arbitrage census (raw material)\n" % NAMES[chain])
A("Status: census COMPLETE (sentinel `.sentinels/%s.DONE`); DefiLlama DEX overview %s; token metadata + prices %s (sentinel `.sentinels/EVM_TOKENPRICES_%s.DONE`).%s\n" % (
    w["config"]["sentinel"], "COMPLETE" if dl else "NOT FETCHED", status_tp, chain.upper(),
    " Ordering docs: COMPLETE (see docs/)." if docs else ""))
A("This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.\n")
A("## Question lines served (mapping only)\n")
A("Question-line IDs are defined in `../MANIFEST-evm.md` (verbatim user text there).\n")
A("| File(s) | Question lines |\n|---|---|")
A("| blocks.csv.gz, txs-*.csv.gz, reverted-*.csv.gz, candidates-*.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, window.json | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-STUDIES%s |" % (" (Arbitrum $4,700/day line)" if chain == "arbitrum" else " (failed-transaction cost line; the literature figure for Optimism is quoted in docs/ANALYSIS.md 4.1)" if chain == "optimism" else ""))
A("| candidates-*.jsonl.gz (Uniswap V4 PoolManager Swap logs, topic0 0x40e9cecb...), blocks.csv.gz base_fee_per_gas + txs effective_gas_price (priority fee per gas = effective_gas_price - base_fee_per_gas, derivable) | Q-V4LAUNCH (priority-fee share line), Q-GAPS |")
A("| candidates-*.jsonl.gz (all pools active in the window, any pool age / size) + tokens-onchain-meta.csv.gz | Q-OLDV2, Q-SMALLPOOLS (as observed on this chain, not Base) |")
if chain == "ethereum":
    A("| blocks.csv.gz miner + extra_data (+ extra_data_text_derived builder tag) | Q-BSCORDER (comparison material: Ethereum block builders) |")
if docs:
    A("| docs/ (official ordering documentation)%s | Q-BSCORDER (comparison material: ordering policy on this chain), Q-V4LAUNCH (priority-fee ordering) |" % (", arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz, txs timeboosted column" if chain == "arbitrum" else ""))
A("| tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json | USD valuation inputs for Q-STUDIES / Q-OTHERCHAINS |")
A("| defillama-dexs.json | Q-OTHERCHAINS (which DEXes exist on the chain and their reported volume; for checking swap-topic coverage) |")
A("\nNot served here: Q-V4BASE (Base only; see the Base directories under research-material/, e.g. 01-v4-pools and 05-base-onchain).\n")

A("## Window (pinned)\n")
A("| Item | Value |\n|---|---|")
A("| Chain id | %d |" % w["chain_id"])
A("| Block range (inclusive) | %d to %d (%d blocks) |" % (w["start_block"], w["end_block"], w["n_blocks_in_window"]))
A("| Block timestamps | %d (%s) to %d (%s) |" % (w["start_timestamp"], utc(w["start_timestamp"]), w["end_timestamp"], utc(w["end_timestamp"])))
A("| Window rule | %s; end block = %s |" % (w["window_rule"], "'finalized' tag at pin time" if w["end_tag"] == "finalized" else "eth_blockNumber at pin time minus %d" % w["head_margin"]))
A("| Head at pin time | %d (pinned %s) |" % (w["head_at_pin"], w["pinned_at_utc"]))
A("| Measured block interval | %.6f s = (end_timestamp - start_timestamp) / (end_block - start_block) |" % w["measured_block_interval_s"])
A("| Collection finished | %s |" % w["finalized_at_utc"])
A("| Integrity checks | parent-hash chain breaks: %d; blocks missing from blocks.csv: %d; first/last block hash re-read from RPC after collection and matched: %s; gap blocks: %d |" % (
    len(w["checks"]["parent_hash_breaks_at"]), w["checks"]["n_blocks_missing"],
    all(x.get("match") for x in w["checks"]["canonical_recheck"].values()), c["gap_blocks"]))
A("")

A("## Sources / endpoints\n")
A("* JSON-RPC primary: `%s` (eth_getBlockReceipts + eth_getBlockByNumber(block,false), JSON-RPC batches of %d block(s), <= 4 HTTP requests in flight). Fallback(s), used only after failures/refusals: %s." % (
    w["endpoints"]["primary"], w["config"]["batch"], ", ".join("`%s`" % x for x in w["endpoints"]["fallbacks"])))
A("* Requests actually sent (HTTP): %s. Errors by endpoint/kind (all recovered by retry; `item-*` counts are per block inside a failed batch): %s." % (
    json.dumps(w["rpc_requests_by_endpoint"]), json.dumps(w["rpc_errors_by_endpoint_kind"]) or "{}"))
if dl:
    A("* DefiLlama: `%s` fetched %s (HTTP %s, %d bytes), stored unmodified as defillama-dexs.json." % (dl["url"], dl["fetched_at_utc"], dl["http_status"], dl["bytes"]))
if tp:
    A("* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (%s) on %s. Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` at ts = %s and `%s`." % (
        tp.get("eth_call_time_utc"), ", ".join(tp["rpc"]), tp.get("price_timestamps_requested"), tp.get("native_chart_url")))
if docs:
    A("* Official docs: see docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below.")
A("* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.\n")

A("## Reproduce\n")
A("```bash\nexport PATH=/root/.foundry/bin:$PATH\ncd %s/collect" % d)
A("python3 make_swap_topics.py %s ..            # writes ../swap-topics.csv (topic0 via cast keccak)" % chain)
A("setsid nohup python3 census.py --chain %s --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent" % chain)
A("python3 fetch_defillama.py %s ../defillama-dexs.json > defillama.log 2>&1" % SLUG[chain])
A("python3 token_prices.py --chain %s --out .. > token_prices.log 2>&1        # after the census (reads ../window.json, ../candidates-*)" % chain)
if docs:
    A("python3 fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1")
if chain == "arbitrum":
    A("python3 arbitrum_chain_state.py > arbitrum_chain_state.log 2>&1   # precompile reads at the window blocks")
A("python3 write_manifest.py %s ..               # regenerates this file from the metadata files" % chain)
A("```\n")
A("Re-running census.py with the existing window.json resumes/keeps the same pinned window; deleting window.json and the data files pins a new, later window (the chain head moves, so the exact block range above cannot be re-pinned automatically; to reproduce it exactly, write a window.json with the start/end blocks above and status `in_progress`). The smoke tests (`--smoke N --seg-blocks K --part-limit-mb X`) were run in the scratchpad before launch; their outputs are not part of this directory.\n")

A("## Files, schemas, row counts\n")
A("All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description.\n")
A("| File | Rows (excluding header) | Bytes |\n|---|---|---|")
for k, v in f.items():
    hdr = 0 if k.startswith("candidates") or k.startswith("extra") else 1
    for nm in v["files"]:
        n = lines(os.path.join(d, nm)) - hdr
        A("| %s | %d | %d |" % (nm, n, size(nm)))
A("| topic0-counts.csv.gz | %d | %d |" % (lines(os.path.join(d, "topic0-counts.csv.gz")) - 1, size("topic0-counts.csv.gz")))
A("| swap-topics.csv | %d | %d |" % (len(swap), size("swap-topics.csv")))
A("| gaps.csv | %d | %d |" % (c["gap_blocks"], size("gaps.csv")))
for extra in ["tokens-onchain-meta.csv.gz", "prices-defillama-historical.jsonl.gz"]:
    if os.path.exists(os.path.join(d, extra)):
        A("| %s | %d | %d |" % (extra, lines(os.path.join(d, extra)) - (1 if extra.endswith(".csv.gz") else 0), size(extra)))
for extra in ["native-price-chart-defillama.json", "defillama-dexs.json", "defillama-dexs.fetch.json", "token_prices.fetch.json", "window.json", "arbitrum-chain-state.json"]:
    if os.path.exists(os.path.join(d, extra)):
        A("| %s | (JSON document) | %d |" % (extra, size(extra)))
A("\nCandidate counts by criterion: A = %d, B = %d. Transactions: %d; status-0 transactions: %d; distinct topic0 keys: %d.\n" % (
    c["candidates_A"], c["candidates_B"], c["txs"], c["reverted"], c["distinct_topic0_keys"]))

A("### blocks.csv.gz (one row per block, ascending)\n")
A("| Column | Meaning |\n|---|---|")
A("| block_number | block height (int) |\n| timestamp | block timestamp, unix seconds (1 s resolution) |\n| base_fee_per_gas | baseFeePerGas, wei (base-10 string) |\n| gas_used | gasUsed |\n| gas_limit | gasLimit |\n| tx_count | length of the block's transactions list (eth_getBlockByNumber false) |\n| miner | header miner / fee recipient (raw) |\n| extra_data | header extraData (raw hex) |\n| block_hash | hash |\n| parent_hash | parentHash |\n| receipts_count | number of receipts returned by eth_getBlockReceipts |")
if chain == "ethereum":
    A("| extra_data_text_derived | derived: extra_data bytes decoded as UTF-8 (undecodable bytes as \\x escapes); builder tag |")
if chain == "arbitrum":
    A("\nArbitrum: miner is the constant sequencer address 0xa4b000000000000000000073657175656e636572; extra_data is the header sendRoot field as returned by Nitro.")
if chain == "polygon":
    A("\nPolygon Bor: miner is returned as 0x000...000; the block producer's signature is inside extra_data (not decoded).")
if chain in ("optimism", "unichain"):
    A("\nOP-stack: miner is the SequencerFeeVault 0x4200000000000000000000000000000000000011; extra_data carries OP-stack header parameters (not decoded).")
A("\n### txs-NNN.csv.gz (one row per receipt, ordered by block then tx_index)\n")
A("| Column | Meaning |\n|---|---|")
A("| block_number, tx_index | position |\n| tx_hash | transactionHash |\n| from, to | receipt from/to ('' for contract creation) |\n| status | 1 success, 0 reverted |\n| gas_used | receipt gasUsed |\n| effective_gas_price | receipt effectiveGasPrice, wei |\n| type | transaction type as base-10 integer (0 legacy, 1 access-list, 2 EIP-1559, 3 blob, 4 EIP-7702; chain-specific: Arbitrum 104/105/106 = 0x68/0x69/0x6a internal/retryable/ArbOS, OP-stack 126 = 0x7e deposit, Polygon 127 = 0x7f state-sync) |\n| logs_count | number of logs in the receipt |\n| contract_address | receipt contractAddress |\n| l1_fee | OP-stack receipt l1Fee, wei ('' on other chains) |\n| gas_used_for_l1 | Arbitrum receipt gasUsedForL1 ('' elsewhere) |\n| timeboosted | Arbitrum receipt timeboosted ('' elsewhere) |\n| in_block_tx_list | derived: true if the receipt's hash is in the block's transactions list |")
A("\nFee per tx is derivable as gas_used * effective_gas_price (+ l1_fee on OP-stack; OP-stack operator-fee fields, if any, are only in the candidate receipt sub-objects). Priority fee per gas is derivable as effective_gas_price - base_fee_per_gas of the block.")
A("\n### reverted-NNN.csv.gz (every status-0 transaction)\n")
A("Columns: block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, logs_count (always 0 for reverted txs by EVM semantics), type, l1_fee, gas_used_for_l1, timeboosted; meanings as in txs.\n")
A("### candidates-NNN.jsonl.gz (one JSON object per candidate tx)\n")
A("Criterion A: >= 2 logs whose topic0 is in swap-topics.csv (match_rule topic0), or zero-topic logs emitted by a match_rule=log0_address address (Ekubo Core swaps). Criterion B (only if not A): >= 3 ERC-20 Transfer logs (topic0 0xddf252ad..., exactly 3 topics, i.e. ERC-721 transfers excluded) emitted by >= 2 distinct token contracts. Both criteria count logs regardless of the emitting contract (no pool/factory allow-list).\n")
A("| Field | Meaning |\n|---|---|")
A("| block_number, block_timestamp, tx_index, tx_hash, from, to | as above (block_timestamp joined from the block header) |\n| status | 1 / 0 |\n| gas_used, effective_gas_price | base-10 strings |\n| criterion | 'A' or 'B' |\n| derived.n_logs, derived.n_swap_logs, derived.swap_keys_matched, derived.n_erc20_transfer_logs, derived.n_distinct_transfer_tokens | derived: the counts used to evaluate the criteria (swap_keys_matched lists matched topic0 values or 'log0:<address>') |\n| receipt | every receipt field except logs, verbatim hex as returned by the RPC (incl. logsBloom, cumulativeGasUsed, L1 fee fields, gasUsedForL1, timeboosted, blobGasUsed, ...) |\n| logs | all logs of the tx, verbatim (address, topics, data, logIndex, ...) |")
A("\n### topic0-counts.csv.gz (all logs of all txs in the window, not only candidates)\n")
A("| Column | Meaning |\n|---|---|\n| topic0_or_log0_emitter | topic0, or 'log0:<address>' for zero-topic logs |\n| n_logs | number of logs |\n| n_txs | number of txs with >= 1 such log |\n| n_distinct_emitting_addresses | distinct log.address values |\n| first_example_tx, first_example_block, first_example_log_address | first occurrence in block order |\n| in_known_swap_topics | true if the key is in swap-topics.csv |")
A("\n### swap-topics.csv (KNOWN SWAP TOPICS for this chain)\n")
A("Columns: topic0, signature, protocol, source_url, verified_example_tx (first log with this topic0 in the census window; empty = not observed in the window, i.e. not verified on this chain), match_rule, match_address, verified_example_block, verified_example_log_address, verification_note, topic0_tool.\n")
A("| topic0 / rule | signature | verified in window |\n|---|---|---|")
for r in swap:
    A("| %s | `%s` | %s |" % (r["topic0"] or ("log0 @ " + r["match_address"]), r["signature"], ("yes: " + r["verified_example_tx"]) if r["verified_example_tx"] else "no"))
if chain == "arbitrum":
    A("\n### extra-timeboost-auction-logs.jsonl.gz\n")
    A("Every log emitted in the window by the Timeboost ExpressLaneAuction contract 0x5fcb496a31b7ae91e7c9078ec662bd7a55cd3079 (address from docs/how-to-use-timeboost), one JSON object per log: block_number, block_timestamp, tx_index, tx_hash, from, to, status, log (verbatim). Rows in this window: %d." % c["extra"].get("timeboost-auction-logs", 0))
if chain == "arbitrum":
    A("\n### arbitrum-chain-state.json\n")
    A("Raw eth_call results of Arbitrum precompile getters at the window start block, window end block and 'latest' (collect/arbitrum_chain_state.py): ArbSys(0x64).arbOSVersion(), ArbOwnerPublic(0x6b).getCollectTips(), getScheduledUpgrade(), getNetworkFeeAccount(). Fields per result: at, block_tag, endpoint, call, to, data (selector from `cast sig`), result_raw, error, decoded_derived (ABI words as base-10 / address), arbos_version_derived (= arbOSVersion() - 55, per Nitro precompiles/ArbSys.go line 68 'Nitro starts at version 56'; source stored in docs/). Historical state came from arbitrum-one.public.blastapi.io and arb1.arbitrum.io (arbitrum.drpc.org answered 'Unknown state', publicnode refuses historical calls).")
A("\n### tokens-onchain-meta.csv.gz\n")
A("One row per ERC-20 contract that emitted a Transfer log inside a candidate tx. Columns: token_address, n_transfer_logs_in_candidates, decimals_raw / symbol_raw / name_raw (raw eth_call return data), decimals_error / symbol_error / name_error (RPC error text if the call failed or reverted), call_block_tag ('latest'), call_endpoint, decimals_derived / symbol_derived / name_derived (derived: ABI-decoded uint / string, or bytes32 text for tokens such as MKR).\n")
A("### prices-defillama-historical.jsonl.gz / native-price-chart-defillama.json\n")
A("One JSON line per DefiLlama coins API request: url, fetched_at_utc, http_status, timestamp_requested, response (raw body: coins.<chain>:<address> -> price (USD), decimals, symbol, timestamp of the price point, confidence). Requested at the window start, middle and end timestamps; tokens without a DefiLlama price are simply absent from `response.coins`. native-price-chart-defillama.json is the raw 5-minute chart response for the native gas token(s) across the window.\n")
A("### defillama-dexs.json\n")
A("Raw response of `https://api.llama.fi/overview/dexs/%s` (DefiLlama DEX volume overview: totals, per-protocol list with 24h/7d/30d volumes, chart arrays). Unmodified.\n" % SLUG[chain])
if docs:
    A("### docs/\n")
    A("Official documentation on transaction ordering, fetched verbatim. For each URL: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION method, then the full visible text or raw markdown), plus the raw body (`.html.gz`, `.raw.gz` for markdown, or `.pdf`). `index.csv` lists every URL attempted.\n")
    A("| URL | HTTP | fetched (UTC) | note |\n|---|---|---|---|")
    for r in docs:
        A("| %s | %s | %s | %s |" % (r["url"], r["http_status"], r["fetched_at_utc"], r["note"] or ""))
A("\n### collect/\n")
A("census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py (+ docs_urls.txt where used), token_prices.py, run_token_prices_all.sh, write_manifest.py and their logs (census.log, make_swap_topics.log, defillama.log, docs.log, token_prices.log). Identical copies of these scripts are in every sibling chain directory and in ../_shared_collect/.%s\n" % (" Arbitrum only: arbitrum_chain_state.py (+ arbitrum_chain_state.log)." if chain == "arbitrum" else ""))

A("## Coverage limits and gaps\n")
lim = [
    "Single contiguous window per chain (%s of chain time ending %s); one weekday evening (UTC), no other days or times of day." % (
        "6 h" if w["window_seconds_requested"] == 21600 else "60 min", utc(w["end_timestamp"])),
    "Gap blocks (unfetchable after all retries): %d (gaps.csv). Blocks missing from blocks.csv: %d. Parent-hash breaks: %d." % (
        c["gap_blocks"], w["checks"]["n_blocks_missing"], len(w["checks"]["parent_hash_breaks_at"])),
    "eth_getBlockByNumber was called with hydrated=false (per the shared definition): transaction input/calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are NOT collected. Priority fee actually paid per gas is derivable from effective_gas_price and base_fee_per_gas.",
    "No call traces: internal native-token transfers (e.g. direct payments to the block builder / coinbase on Ethereum, native-ETH legs of Uniswap V4 or WETH unwraps) and revert reasons are not collected.",
    "Logs are stored only for candidate transactions (criteria A/B). Transactions with a single swap log and fewer than 3 ERC-20 transfers from 2 tokens are in txs-*.csv only (no logs). topic0-counts.csv.gz counts logs of all transactions.",
    "Criterion A uses only the signatures in swap-topics.csv; the match is on topic0 (plus the Ekubo log0 address rule) with no check of the emitting contract. Venues whose swap events use other signatures are not matched by A (e.g. Ambient/CrocSwap, RFQ/PMM venues such as Hashflow/Bebop/Native, 0x and 1inch limit orders, UniswapX fills, Bancor, Uniswap V1, Maverick V1, Trader Joe LB v2.0, GMX V2, KyberSwap classic, Clipper, Integral); such transactions appear as candidates only if they meet criterion B. A signature not observed in this window is listed with an empty verified_example_tx (not verified on this chain).",
    "ERC-20 Transfer is identified as topic0 0xddf252ad... with exactly 3 topics; tokens emitting non-standard transfer events and native-token movements are not counted for criterion B.",
    "Token metadata was read at block tag 'latest' shortly after the window, not at the window blocks. DefiLlama prices are DefiLlama's own aggregates (confidence field included) and are absent for tokens DefiLlama does not price.",
    "No mempool / pending-transaction data, no private-orderflow or bundle data, no flashblock / preconfirmation-level ordering data (block-level receipts only).",
    "The DefiLlama DEX overview was fetched once (%s) with default query parameters." % (dl["fetched_at_utc"] if dl else "n/a"),
]
if chain == "arbitrum":
    lim.append("Timeboost: the ExpressLaneAuction contract emitted %d logs in this window (extra-timeboost-auction-logs.jsonl.gz); the receipt field `timeboosted` is captured per tx. docs/ contains the Timeboost pages and the newer PGA (Priority Gas Auction) / Fast Feed pages as published on %s; which policy was active during the window is not determined here." % (
        c["extra"].get("timeboost-auction-logs", 0), docs[0]["fetched_at_utc"][:10] if docs else "n/a"))
    lim.append("Arbitrum requested window is 60 min (~14,400 blocks at 250 ms nominal); the chain produced %d blocks in it. No reduction to 20 min was needed." % w["n_blocks_in_window"])
if chain == "unichain":
    lim.append("docs: the former docs.unichain.org pages now redirect to developers.uniswap.org/docs/unichain; the Wayback Machine copy of the former advanced-txn page returned HTTP 403 through the proxy and was not stored (listed in docs/index.csv). Unichain Flashblocks and priority-ordering descriptions are taken from the current developer docs, the Unichain whitepaper PDF and Uniswap/Flashbots blog posts.")
if chain == "optimism":
    lim.append("docs: github.com blob pages returned HTTP 403; the rollup-boost flashblocks spec was taken from raw.githubusercontent.com instead.")
if chain == "ethereum":
    lim.append("Ethereum: 6 h requested; slots without a block (missed slots) have no row. Builder identity is available only as the header fields miner/extra_data (no relay data, no bid data, no MEV-Boost payload data).")
if chain == "polygon":
    lim.append("Polygon: end block taken from the 'finalized' tag (a few blocks behind head at pin time).")
lim.append("Not collected in this directory: Base (see 05-base-onchain), BSC (separate collector in ../bsc), Solana, and other chains (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, etc.). Literature documents (arXiv papers quoted in docs/ANALYSIS.md 4.1) are not collected here.")
for x in lim:
    A("* " + x)
open(os.path.join(d, "MANIFEST.md"), "w").write("\n".join(L) + "\n")
print("wrote", os.path.join(d, "MANIFEST.md"))
