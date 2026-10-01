#!/usr/bin/env python3
"""Writes <chain_dir>/MANIFEST.md for one of the six L2 censuses added on 2026-10-01 (other-l2-censuses), from the
collectors' own metadata files (window.json, swap-topics.csv, docs/index.csv, docs/excerpts.jsonl,
defillama-dexs.fetch.json, token_prices.fetch.json, the sentinel files) plus a verified inventory of every file in
the directory (streamed: gzip read to the end, CSV parsed, JSON/JSONL parsed, sha256). Descriptive metadata only.
usage: python3 write_manifest_l2.py <chain> <chain_dir>
"""
import csv, datetime, gzip, hashlib, io, json, os, subprocess, sys

chain, d = sys.argv[1], os.path.abspath(sys.argv[2])
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l2_config  # noqa: E402
SENT = "/home/user/dapparb/research-material/.sentinels"
REPO = "/home/user/dapparb"
NAMES = {"ink": "Ink", "mantle": "Mantle", "abstract": "Abstract", "worldchain": "World Chain", "zksync": "ZKsync Era",
         "soneium": "Soneium"}
SLUG = {"ink": "ink", "mantle": "mantle", "abstract": "abstract", "worldchain": "world-chain", "zksync": "zksync-era",
        "soneium": "soneium"}
# descriptive, chain-specific notes (observations from the stored files and the stored docs; no interpretation)
NOTES = {
    "ink": [
        "Stack: OP Stack chain (docs/ excerpt ink-04, 'Ink is an OP Chain (Ethereum Layer 2) which is part of the Superchain.'). Gas token: ETH.",
        "Ordering-related docs available on docs.inkonchain.com are short; no page describing the sequencer's ordering rule was found in the site map (`https://docs.inkonchain.com/sitemap-0.xml`, 49 URLs, read 2026-10-01). The stored pages are the four listed under docs/. OP Stack ordering docs are stored in ../optimism/docs/.",
    ],
    "mantle": [
        "Stack: Mantle v2 (OP Stack based; docs/ excerpts mantle-01 to mantle-09). Gas token: MNT. `base_fee_per_gas`, `effective_gas_price` and `l1_fee` are in MNT wei; the native-token chart was requested for `coingecko:mantle`.",
        "Receipts carry, in addition to the OP Stack fields, `tokenRatio`, `operatorFeeConstant` and `operatorFeeScalar` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).",
        "`l1_fee` is empty for the type-126 (0x7e deposit) rows of txs-001.csv.gz (the RPC returns no l1Fee for them).",
    ],
    "abstract": [
        "Stack: ZK Stack chain using EraVM (docs/ excerpt abstract-01; docs/ sequencer page links the matter-labs/zksync-era repository). Gas token: ETH.",
        "Transaction types in txs-001.csv.gz include 113 (= 0x71, EIP-712 transactions). `miner` is 0x0000000000000000000000000000000000000000 and `extra_data` is `0x` in every block. Receipts carry `l1BatchNumber`, `l1BatchTxIndex` and `l2ToL1Logs` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).",
        "0x000000000000000000000000000000000000800a is the L2BaseToken system contract, which holds ETH balances (docs/ excerpt abstract-05). It emits logs with topic0 0xddf252ad... and 3 topics. census.py counts them as ERC-20 Transfer logs for criterion B like those of any other emitter (shared definition, unchanged). Their count in candidate txs is in tokens-onchain-meta.csv.gz (column n_transfer_logs_in_candidates); its decimals()/symbol()/name() calls reverted (error columns of that file).",
    ],
    "worldchain": [
        "Stack: OP Stack chain with the World Chain Builder (rollup-boost external block production) and Priority Blockspace for Humans (PBH) ordering policy (docs/ excerpts worldchain-02 to worldchain-07). Gas token: ETH.",
        "PBH transactions are not flagged in the census files (no PBH-specific column); the PBHEntryPoint contract address was not looked up for this collection. Receipts and logs of candidate txs are stored verbatim; all txs (incl. `to` address) are in txs-001.csv.gz.",
        "The Alchemy public endpoint (https://worldchain-mainnet.g.alchemy.com/public) answered eth_getBlockReceipts with HTTP 401 'Only core evm requests are allowed.' (../rpc-receipts-probe-candidates.jsonl.gz) and was not used for the census; it was used for the token metadata eth_calls (see 'Token metadata runs').",
    ],
    "zksync": [
        "Stack: ZKsync Era (EraVM) (docs/ excerpts zksync-01 to zksync-07). Gas token: ETH.",
        "Transaction types in txs-001.csv.gz include 113 (= 0x71, EIP-712) and 255 (= 0xff, L1->L2 priority transactions). `miner` is 0x0000000000000000000000000000000000000000 and `extra_data` is `0x` in every block. Receipts carry `l1BatchNumber`, `l1BatchTxIndex` and `l2ToL1Logs` (kept verbatim in the `receipt` object of candidates-001.jsonl.gz only).",
        "0x000000000000000000000000000000000000800a is the L2BaseToken system contract, which holds ETH balances (docs/ excerpt zksync-07). It emits logs with topic0 0xddf252ad... and 3 topics. census.py counts them as ERC-20 Transfer logs for criterion B like those of any other emitter (shared definition, unchanged). Their count in candidate txs is in tokens-onchain-meta.csv.gz (column n_transfer_logs_in_candidates); its decimals()/symbol()/name() calls reverted (error columns of that file).",
        "Measured block interval in this window: about 6.18 s, so the 60-minute window holds 583 blocks. The docs page stored as docs/docs.zksync.io_zksync-protocol_era-vm_transactions_blocks.txt states 1 second (excerpt zksync-05). The window rule is by timestamp, as for every chain.",
    ],
    "soneium": [
        "Stack: OP Stack chain (Superchain). Gas token: ETH.",
        "Write access to the sequencer is limited to compliance-approved RPCs (docs/ excerpts soneium-02 to soneium-04). soneium.drpc.org answered eth_blockNumber with 'the method eth_blockNumber does not exist/is not available' during the selection probe (../rpc-receipts-probe-candidates.jsonl.gz) and is not used.",
    ],
}

w = json.load(open(os.path.join(d, "window.json")))
c = w["counts"]
swap = list(csv.DictReader(open(os.path.join(d, "swap-topics.csv"))))
docs = list(csv.DictReader(open(os.path.join(d, "docs", "index.csv"))))
exc = [json.loads(l) for l in open(os.path.join(d, "docs", "excerpts.jsonl"), encoding="utf-8")]
dl = json.load(open(os.path.join(d, "defillama-dexs.fetch.json")))
tp = json.load(open(os.path.join(d, "token_prices.fetch.json")))
sent_c = open(os.path.join(SENT, w["config"]["sentinel"] + ".DONE")).read().strip()
sent_t = open(os.path.join(SENT, "EVM_TOKENPRICES_%s.DONE" % chain.upper())).read().strip()


def utc(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def gzrows(p):
    with gzip.open(p, "rt", encoding="utf-8", newline="") as f:
        return sum(1 for _ in f)


def describe(rel):
    """rows/lines description for the inventory; raises on parse errors"""
    p = os.path.join(d, rel)
    if rel.endswith(".csv.gz"):
        with gzip.open(p, "rt", encoding="utf-8", newline="") as f:
            r = csv.reader(f); hdr = next(r); n = 0
            for row in r:
                if len(row) != len(hdr):
                    raise SystemExit("field count mismatch in %s" % rel)
                n += 1
        return "%s rows + header" % format(n, ",")
    if rel.endswith(".jsonl.gz"):
        n = 0
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                json.loads(line); n += 1
        return "%s JSON line%s" % (format(n, ","), "" if n == 1 else "s")
    if rel.endswith(".jsonl"):
        n = 0
        for line in open(p, encoding="utf-8"):
            json.loads(line); n += 1
        return "%s JSON line%s" % (format(n, ","), "" if n == 1 else "s")
    if rel.endswith(".json"):
        json.load(open(p, encoding="utf-8"))
        return "1 JSON document"
    if rel.endswith(".csv"):
        with open(p, newline="", encoding="utf-8") as f:
            r = csv.reader(f); hdr = next(r); n = 0
            for row in r:
                if len(row) != len(hdr):
                    raise SystemExit("field count mismatch in %s" % rel)
                n += 1
        return "%s rows + header" % format(n, ",")
    if rel.endswith(".gz"):
        n = gzrows(p)
        return "%s line%s (decompressed)" % (format(n, ","), "" if n == 1 else "s")
    if os.path.getsize(p) == 0:
        return "empty (0 bytes)"
    with open(p, "rb") as f:
        n = f.read().count(b"\n")
    return "%s line%s" % (format(n, ","), "" if n == 1 else "s")


def ignored(rel):
    r = subprocess.run(["git", "-C", REPO, "check-ignore", "-q", os.path.join(d, rel)])
    return r.returncode == 0


L = []
A = L.append
A("# %s: on-chain arbitrage census (raw material)\n" % NAMES[chain])
A("Added 2026-10-01 by the other-l2-censuses collection. It extends the five EVM censuses in this folder (index: `../MANIFEST-evm.md`). The chain was selected by 24 h DEX volume from DefiLlama, as recorded in `../selection.csv` (see `../MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)').\n")
A("Status: COMPLETE. Sentinels (git-ignored, text reproduced verbatim):\n")
A("```\n%s.DONE  %s\nEVM_TOKENPRICES_%s.DONE  %s\n```\n" % (w["config"]["sentinel"], sent_c, chain.upper(), sent_t))
A("This directory holds collected data only. Nothing here is an analysis, estimate or conclusion.\n")

A("## Question lines served (mapping only)\n")
A("Line numbers refer to the 8 question lines quoted verbatim in `../MANIFEST.md` and `research-material/README.md` section 2.\n")
census = "blocks.csv.gz, txs-001.csv.gz, reverted-001.csv.gz, candidates-001.jsonl.gz, topic0-counts.csv.gz, swap-topics.csv, gaps.csv, window.json"
tok = "tokens-onchain-meta.csv.gz, prices-defillama-historical.jsonl.gz, native-price-chart-defillama.json, token_prices.fetch.json"
A("| Line | Files in this directory |\n|---|---|")
A("| 1 | none |")
A("| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |")
A("| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz |")
A("| 4 | %s, %s, defillama-dexs.json, defillama-dexs.fetch.json |" % (census, tok))
A("| 5 | candidates-001.jsonl.gz (swap logs; Uniswap V4 PoolManager topic0 0x40e9cecb... where observed, see swap-topics.csv), blocks.csv.gz (base_fee_per_gas), txs-001.csv.gz (effective_gas_price), docs/ (incl. docs/excerpts.jsonl) |")
A("| 6 | docs/ (incl. docs/excerpts.jsonl) |")
A("| 7 | %s, %s |" % (census, tok))
A("| 8 | %s |" % census)
A("\n`collect/` holds scripts and logs and is not mapped to a question line.\n")

A("## Window (pinned)\n")
A("| Item | Value |\n|---|---|")
A("| Chain id | %d |" % w["chain_id"])
A("| Block range (inclusive) | %d to %d (%d blocks) |" % (w["start_block"], w["end_block"], w["n_blocks_in_window"]))
A("| Block timestamps | %d (%s) to %d (%s) |" % (w["start_timestamp"], utc(w["start_timestamp"]), w["end_timestamp"], utc(w["end_timestamp"])))
A("| Window rule | %s; end block = eth_blockNumber at pin time minus %d |" % (w["window_rule"], w["head_margin"]))
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
    json.dumps(w["rpc_requests_by_endpoint"]), json.dumps(w["rpc_errors_by_endpoint_kind"])))
A("* DefiLlama: `%s` fetched %s (HTTP %s, %d bytes), stored unmodified as defillama-dexs.json (same default query parameters as the five earlier chains)." % (dl["url"], dl["fetched_at_utc"], dl["http_status"], dl["bytes"]))
A("* Token metadata: eth_call decimals()/symbol()/name() at block tag `latest` (%s) on %s (first endpoint first; the endpoint actually used per token is in column call_endpoint). Prices: `https://coins.llama.fi/prices/historical/<ts>/<coins>` (coin prefix `%s:`) at ts = %s (%d requests) and `%s` (HTTP %s)." % (
    tp.get("eth_call_time_utc"), ", ".join(tp["rpc"]), l2_config.TOKEN_CFG[chain]["llama"],
    tp.get("price_timestamps_requested"), tp.get("defillama_requests"), tp.get("native_chart_url"), tp.get("native_chart_http_status")))
A("* Official docs: docs/index.csv (URL, final URL, HTTP status, UTC fetch time) and the table below; verbatim excerpts in docs/excerpts.jsonl.")
A("* Swap-event signatures: collect/swap_signatures.csv (source code URL per signature); topic0 computed with `cast keccak` (foundry) by collect/make_swap_topics.py.\n")

A("## Method and scripts\n")
A("The shared method of the five earlier EVM censuses is reused unchanged. `collect/census.py`, `make_swap_topics.py`, `swap_signatures.csv`, `fetch_defillama.py`, `fetch_docs.py` and `token_prices.py` are byte-identical copies of `../_shared_collect/` (same md5).")
A("census.py and token_prices.py keep their chain settings in hard-coded dicts. The two wrappers add this chain's settings at run time and then call the unmodified `main()`: `collect/census_l2.py` adds `l2_config.CENSUS_CHAINS` to `census.CHAINS`, and `collect/token_prices_l2.py` adds `l2_config.TOKEN_CFG` to `token_prices.CFG`.")
A("The masters of l2_config.py, census_l2.py, token_prices_l2.py, run_token_prices_l2.sh, make_doc_excerpts.py and write_manifest_l2.py are in `../collect/`; the copies here are identical. Census configuration of this chain (from window.json `config`): %s.\n" % json.dumps(w["config"]))

A("## Reproduce\n")
A("```bash\nexport PATH=/root/.foundry/bin:$PATH\ncd %s/collect" % d)
A("python3 -B make_swap_topics.py %s .. > make_swap_topics.log 2>&1       # writes ../swap-topics.csv (topic0 via cast keccak)" % chain)
A("setsid nohup python3 -B census_l2.py --chain %s --out .. > census.log 2>&1 < /dev/null &   # resumable; pins a NEW window if ../window.json is absent" % chain)
A("python3 -B fetch_defillama.py %s ../defillama-dexs.json > defillama.log 2>&1" % SLUG[chain])
A("python3 -B token_prices_l2.py --chain %s --out .. > token_prices.log 2>&1   # after the census; the six chains were run in sequence by ../collect/run_token_prices_l2.sh" % chain)
A("python3 -B fetch_docs.py ../docs $(cat docs_urls.txt) > docs.log 2>&1")
A("python3 -B make_doc_excerpts.py %s .. > excerpts.log 2>&1              # docs/excerpts.jsonl from collect/docs_excerpts_spec.json" % chain)
A("python3 -B write_manifest_l2.py %s ..                                  # regenerates this file" % chain)
A("```\n")
A("Re-running census_l2.py with the existing window.json keeps the pinned window (status `complete` -> nothing to do). Deleting window.json and the data files pins a new, later window. The smoke test (`--smoke 25 --seg-blocks 10 --part-limit-mb 0.02`, all six chains, 2026-10-01T04:18Z) ran in the scratchpad; its outputs are not part of this directory.\n")

A("## Files, schemas, row counts\n")
A("All hex values are lowercase 0x-prefixed. Wei amounts and other integers that can exceed 2^53 are base-10 strings. `derived` = deterministic transformation of the raw fields, marked in the column name or description. Column definitions are identical to the five earlier chains (full text in `../arbitrum/MANIFEST.md`); they are repeated briefly here.\n")
A("| File | Rows (excluding header) | Bytes |\n|---|---|---|")
for k, v in w["files"].items():
    hdr = 0 if k.startswith("candidates") else 1
    for nm in v["files"]:
        A("| %s | %d | %d |" % (nm, gzrows(os.path.join(d, nm)) - hdr, os.path.getsize(os.path.join(d, nm))))
A("| topic0-counts.csv.gz | %d | %d |" % (gzrows(os.path.join(d, "topic0-counts.csv.gz")) - 1, os.path.getsize(os.path.join(d, "topic0-counts.csv.gz"))))
A("| swap-topics.csv | %d | %d |" % (len(swap), os.path.getsize(os.path.join(d, "swap-topics.csv"))))
A("| gaps.csv | %d | %d |" % (c["gap_blocks"], os.path.getsize(os.path.join(d, "gaps.csv"))))
A("| tokens-onchain-meta.csv.gz | %d | %d |" % (gzrows(os.path.join(d, "tokens-onchain-meta.csv.gz")) - 1, os.path.getsize(os.path.join(d, "tokens-onchain-meta.csv.gz"))))
A("| prices-defillama-historical.jsonl.gz | %d | %d |" % (gzrows(os.path.join(d, "prices-defillama-historical.jsonl.gz")), os.path.getsize(os.path.join(d, "prices-defillama-historical.jsonl.gz"))))
for x in ["native-price-chart-defillama.json", "defillama-dexs.json", "defillama-dexs.fetch.json", "token_prices.fetch.json", "window.json"]:
    A("| %s | (JSON document) | %d |" % (x, os.path.getsize(os.path.join(d, x))))
A("| docs/excerpts.jsonl | %d | %d |" % (len(exc), os.path.getsize(os.path.join(d, "docs", "excerpts.jsonl"))))
A("\nCandidate counts by criterion: A = %d, B = %d. Transactions: %d; status-0 transactions: %d; distinct topic0 keys: %d; receipts not in the block's transaction list: %d.\n" % (
    c["candidates_A"], c["candidates_B"], c["txs"], c["reverted"], c["distinct_topic0_keys"], c["receipts_not_in_block_tx_list"]))
A("* **blocks.csv.gz** (one row per block, ascending): block_number, timestamp (unix s), base_fee_per_gas (wei), gas_used, gas_limit, tx_count (length of the block's transactions list), miner, extra_data (raw hex), block_hash, parent_hash, receipts_count (receipts returned by eth_getBlockReceipts).")
A("* **txs-001.csv.gz** (one row per receipt, by block then tx_index): block_number, tx_index, tx_hash, from, to, status (1/0), gas_used, effective_gas_price (wei), type (base-10 integer), logs_count, contract_address, l1_fee (OP-stack receipt l1Fee, wei; '' where absent), gas_used_for_l1 / timeboosted (Arbitrum only; '' here), in_block_tx_list (derived: receipt hash is in the block's transactions list).")
A("* **reverted-001.csv.gz**: every status-0 transaction; block_number, tx_index, tx_hash, from, to, gas_used, effective_gas_price, logs_count, type, l1_fee, gas_used_for_l1, timeboosted.")
A("* **candidates-001.jsonl.gz** (one JSON object per candidate tx). Criterion A: >= 2 logs whose topic0 is in swap-topics.csv (or zero-topic logs from a match_rule=log0_address address). Criterion B (only if not A): >= 3 logs with topic0 0xddf252ad... and exactly 3 topics, emitted by >= 2 distinct contracts. No pool/factory allow-list. Fields: block_number, block_timestamp, tx_index, tx_hash, from, to, status, gas_used, effective_gas_price, criterion, derived {n_logs, n_swap_logs, swap_keys_matched, n_erc20_transfer_logs, n_distinct_transfer_tokens}, receipt (every receipt field except logs, verbatim), logs (all logs of the tx, verbatim).")
A("* **topic0-counts.csv.gz** (logs of all txs in the window): topic0_or_log0_emitter, n_logs, n_txs, n_distinct_emitting_addresses, first_example_tx, first_example_block, first_example_log_address, in_known_swap_topics.")
A("* **swap-topics.csv**: topic0, signature, protocol, source_url, verified_example_tx (first log with this topic0 in the window; empty = not observed, i.e. not verified on this chain), match_rule, match_address, verified_example_block, verified_example_log_address, verification_note, topic0_tool.")
A("* **gaps.csv**: block_number, reason (header only = no gap).")
A("* **window.json**: pinned window, config, endpoints, counts, files, integrity checks, request and error counts.")
A("* **tokens-onchain-meta.csv.gz**: one row per contract that emitted a Transfer log (topic0 0xddf252ad..., 3 topics) inside a candidate tx: token_address, n_transfer_logs_in_candidates, decimals_raw, symbol_raw, name_raw, decimals_error, symbol_error, name_error, call_block_tag ('latest'), call_endpoint, decimals_derived, symbol_derived, name_derived.")
A("* **prices-defillama-historical.jsonl.gz**: one JSON line per DefiLlama coins request (url, fetched_at_utc, http_status, timestamp_requested, response = raw body) at the window start, middle and end timestamps. **native-price-chart-defillama.json**: raw 5-minute chart of the native gas token across the window. **token_prices.fetch.json**: run metadata.")
A("* **defillama-dexs.json**: raw response of `%s` (unmodified); **defillama-dexs.fetch.json**: URL, UTC fetch time, HTTP status, bytes." % dl["url"])
A("* **docs/**: `<stem>.txt` (header with SOURCE_URL, FINAL_URL, HTTP_STATUS, FETCHED_AT_UTC, EXTRACTION, then the full visible text or raw markdown) plus the raw body (`.html.gz`, or `.raw.gz` for markdown); `index.csv` lists every URL attempted. **docs/excerpts.jsonl**: verbatim excerpts on transaction ordering / sequencing / fees cut from the `.txt` files by collect/make_doc_excerpts.py (fields excerpt_id, source_url, final_url, http_status, fetched_at_utc, text_file, char_start, char_end, start_anchor_occurrences, text; spans are re-read from the file and checked).\n")

A("### swap-topics.csv (verification in this window)\n")
A("| topic0 / rule | signature | verified in window |\n|---|---|---|")
for r in swap:
    k = r["topic0"] if r["match_rule"] == "topic0" else "log0 @ " + r["match_address"]
    A("| %s | `%s` | %s |" % (k, r["signature"], ("yes: " + r["verified_example_tx"]) if r["verified_example_tx"] else "no"))
A("")

A("### docs/ (official documentation on ordering / sequencer)\n")
A("| URL | HTTP | fetched (UTC) | note |\n|---|---|---|---|")
for r in docs:
    A("| %s | %s | %s | %s |" % (r["url"], r["http_status"], r["fetched_at_utc"], r["note"]))
A("\nExcerpts (docs/excerpts.jsonl; first 160 characters shown here, full text in the file):\n")
A("| id | source URL | fetched (UTC) | text (start) |\n|---|---|---|---|")
for x in exc:
    t = " ".join(x["text"].split())
    A("| %s | %s | %s | %s |" % (x["excerpt_id"], x["source_url"], x["fetched_at_utc"], (t[:160] + (" ..." if len(t) > 160 else "")).replace("|", "\\|")))
A("")

A("## Chain-specific notes (descriptive)\n")
types, miners = {}, {}
with gzip.open(os.path.join(d, "txs-001.csv.gz"), "rt", newline="") as f:
    for r in csv.DictReader(f):
        types[r["type"]] = types.get(r["type"], 0) + 1
with gzip.open(os.path.join(d, "blocks.csv.gz"), "rt", newline="") as f:
    for r in csv.DictReader(f):
        miners[r["miner"]] = miners.get(r["miner"], 0) + 1
A("* Transaction `type` values in txs-001.csv.gz (rows): %s." % ", ".join("%s: %s" % (k, format(v, ",")) for k, v in sorted(types.items(), key=lambda kv: int(kv[0]))))
A("* `miner` values in blocks.csv.gz (blocks): %s." % ", ".join("%s: %s" % (k, format(v, ",")) for k, v in miners.items()))
for n in NOTES[chain]:
    A("* " + n)
if chain == "worldchain":
    A("* Token metadata runs: run 1 (first log line 04:20:23Z, eth_call endpoints Tenderly gateway first) and run 2 (04:25:05Z, thirdweb first) were stopped by the collector before writing output, because those endpoints answered 60-call eth_call batches with HTTP 429 or per-item rate-limit errors (logs: collect/token_prices.attempt1.log, collect/token_prices.attempt2.log). Run 3 (04:30:29Z, Alchemy public first) was started while run 2 was still running and was stopped after it had written tokens-onchain-meta.csv.gz (log: collect/token_prices.attempt3.log). Its partial outputs were deleted. Run 4 (04:30:51Z, Alchemy public first) wrote all files in this directory; its log is collect/token_prices.log. The l2_config.py comment records the endpoint order change. The census itself was not affected.")
A("")

A("## Coverage limits and gaps\n")
A("* Single contiguous window: 60 min of chain time, %s to %s. The five earlier EVM chains' windows are 2026-09-30 20:07-21:07Z (Ethereum 15:06-21:06Z), so this window is from a different hour of the day; no other days or times of day." % (utc(w["start_timestamp"]), utc(w["end_timestamp"])))
A("* Gap blocks: %d (gaps.csv). Blocks missing from blocks.csv: %d. Parent-hash breaks: %d." % (c["gap_blocks"], w["checks"]["n_blocks_missing"], len(w["checks"]["parent_hash_breaks_at"])))
A("* eth_getBlockByNumber was called with hydrated=false (shared definition): calldata, value, nonce, gas limit, maxFeePerGas and maxPriorityFeePerGas are not collected. Priority fee per gas is derivable from effective_gas_price and base_fee_per_gas.")
A("* No call traces (internal native-token transfers, revert reasons), no mempool / pending / private-orderflow data, no flashblock / subblock / preconfirmation-level ordering data (block-level receipts only).")
A("* Logs are stored only for candidate transactions (criteria A/B); topic0-counts.csv.gz counts logs of all transactions.")
A("* Criterion A uses only the signatures in swap-topics.csv (topic0 match, no check of the emitting contract). Venues with other swap-event signatures are matched only via criterion B (see the list of unmatched venue types in `../arbitrum/MANIFEST.md`). The swap-signature list was not extended for this chain; a signature not observed in this window has an empty verified_example_tx. Which DEXes DefiLlama lists for this chain is in defillama-dexs.json.")
A("* ERC-20 Transfer = topic0 0xddf252ad... with exactly 3 topics; native-token movements are not counted, except where the chain emits such logs from a system contract (see chain notes).")
A("* Token metadata read at block tag 'latest' after the window (%s), not at the window blocks. DefiLlama prices are DefiLlama's own aggregates and are absent for tokens it does not price." % tp.get("eth_call_time_utc"))
A("* DefiLlama per-chain DEX overview fetched once (%s), default query parameters." % dl["fetched_at_utc"])
A("* Docs: only the URLs in docs/index.csv were fetched; the excerpts in docs/excerpts.jsonl are a selection of passages from those pages, and the full page texts are stored next to them.")
A("")

# verified inventory
A("## Verified inventory (%s)\n" % datetime.datetime.utcnow().strftime("%Y-%m-%d"))
A("Generated by collect/write_manifest_l2.py at %s by streaming every file in this directory (no data file modified). Checks: every .gz file read to the end; CSV parsed (rows exclude the header; every record has as many fields as the header); every JSON document and JSONL line parsed; sha256 over the stored bytes. Git column: result of `git check-ignore` (nothing was committed by this collection): 'not ignored' = will be included when the folder is committed; 'ignored' = local-only.\n" % datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
A("| File | Bytes | Rows / lines | sha256 | Git |\n|---|---:|---|---|---|")
files = []
for root, dirs, fs in os.walk(d):
    dirs[:] = sorted(x for x in dirs if x != "__pycache__")
    for fn in sorted(fs):
        rel = os.path.relpath(os.path.join(root, fn), d)
        if rel == "MANIFEST.md":
            continue
        files.append(rel)
big = 0
for rel in sorted(files):
    p = os.path.join(d, rel)
    sz = os.path.getsize(p)
    big = max(big, sz)
    A("| %s | %s | %s | %s | %s |" % (rel, format(sz, ","), describe(rel), sha(p), "ignored" if ignored(rel) else "not ignored"))
A("| MANIFEST.md | (this file) | documentation | not recorded | %s |" % ("ignored" if ignored("MANIFEST.md") else "not ignored"))
A("\nFiles: %d plus this MANIFEST.md. Largest file: %s bytes (limit 90 MB)." % (len(files), format(big, ",")))
if big > 90 * 1024 * 1024:
    raise SystemExit("file over 90 MB")
open(os.path.join(d, "MANIFEST.md"), "w").write("\n".join(L) + "\n")
print("wrote", os.path.join(d, "MANIFEST.md"), "files", len(files))
