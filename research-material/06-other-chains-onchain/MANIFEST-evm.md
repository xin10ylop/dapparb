# 06-other-chains-onchain: EVM on-chain arbitrage census index (Arbitrum, Optimism, Unichain, Ethereum, Polygon)

Status: COMPLETE WITH GAPS (finalized 2026-10-01). All 10 EVM sentinels are DONE (EVM_CENSUS_* and EVM_TOKENPRICES_* for arbitrum, optimism, unichain, ethereum, polygon; sentinel files are git-ignored, their text is reproduced in `MANIFEST.md`). All census windows have 0 gap blocks. Gap: 1 documentation URL for Unichain was not retrieved (Wayback Machine copy, HTTP 403; see unichain/MANIFEST.md). Every file was re-verified on 2026-10-01; per-file inventories are in each chain's MANIFEST.md, and the inventory of `_shared_collect/` is at the end of this file.

Collected 2026-09-30 (UTC). Raw material only: no analysis, estimates or conclusions anywhere in these directories. Each chain directory has its own MANIFEST.md with schemas, row counts, endpoints, reproduction commands and a 'Coverage limits and gaps' section.

`bsc/` and `solana/` in this parent directory are produced by separate collectors with their own manifests and are not indexed here (correction 2026-10-01: the collector's text named only `bsc/`). The folder-level index is `MANIFEST.md`.

Correction 2026-10-01 (other-l2-censuses): this index now also covers six L2 census directories added on 2026-10-01: ink/, mantle/, abstract/, worldchain/, zksync/ and soneium/. Their rows are at the end of the Index table, and the section 'Additional L2 chains (2026-10-01)' at the end of this file has their question-line mapping and method notes. They have 12 more DONE sentinels (EVM_CENSUS_* and EVM_TOKENPRICES_* for the six chains). The title, the status line and the sections up to 'Verified inventory (2026-10-01)' were written for the first five chains and are otherwise unchanged.

## Question-line IDs (verbatim user text)

Column "Line" (added 2026-10-01) is the number of the line in the list of 8 question lines in `MANIFEST.md`.

| Line | ID | Question line |
|---|---|---|
| 1 | Q-V4BASE | Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet. |
| 2 | Q-OLDV2 | Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens. |
| 3 | Q-SMALLPOOLS | Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit. |
| 4 | Q-OTHERCHAINS | Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured. |
| (none) | Q-GAPS | Would the gaps change the answer? (used by the collectors; not one of the 8 question lines, so no files are mapped to it below) |
| 5 | Q-V4LAUNCH | V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee. |
| 6 | Q-BSCORDER | BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents. |
| 7 | Q-STUDIES | Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions. |
| 8 | Q-COVERAGE | So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test. |

## Question lines served (mapping only)

Restated by line number on 2026-10-01 (the collector's table used Q-IDs, short notes and Q-GAPS). File lists per line are in each chain's MANIFEST.md, section 'Question lines served'.

| Line | arbitrum/ | optimism/ | unichain/ | ethereum/ | polygon/ |
|---|---|---|---|---|---|
| 1 | none | none | none | none | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz | same | same | same | same |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz | same | same | same | same |
| 4 | census files (blocks, txs-001, reverted-001, candidates-001, topic0-counts, swap-topics, gaps, window), token/price files, defillama-dexs.json | same | same | same | same |
| 5 | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz, docs/, arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz, docs/ | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz, docs/ | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz |
| 6 | docs/, arbitrum-chain-state.json, extra-timeboost-auction-logs.jsonl.gz, txs-001.csv.gz | docs/ | docs/ | blocks.csv.gz | none |
| 7 | census files, token/price files | same | same | same | same |
| 8 | census files | same | same | same | same |

`_shared_collect/` holds scripts only and is not mapped to a question line.

## Index

| Chain | Dir | Window (chain time, UTC) | Blocks | Measured block interval | Sentinel | Status |
|---|---|---|---|---|---|---|
| Arbitrum One | arbitrum/ | 60 min: 2026-09-30T20:07:21Z to 2026-09-30T21:07:20Z | 510447028 to 510460284 (13257) | 0.2715 s | EVM_CENSUS_ARBITRUM (DONE); EVM_TOKENPRICES_ARBITRUM (DONE) | census complete |
| OP Mainnet | optimism/ | 60 min: 2026-09-30T20:07:23Z to 2026-09-30T21:07:21Z | 157600033 to 157601832 (1800) | 2.0000 s | EVM_CENSUS_OPTIMISM (DONE); EVM_TOKENPRICES_OPTIMISM (DONE) | census complete |
| Unichain | unichain/ | 60 min: 2026-09-30T20:07:22Z to 2026-09-30T21:07:21Z | 60050483 to 60054082 (3600) | 1.0000 s | EVM_CENSUS_UNICHAIN (DONE); EVM_TOKENPRICES_UNICHAIN (DONE) | census complete |
| Ethereum mainnet | ethereum/ | 6 h: 2026-09-30T15:06:59Z to 2026-09-30T21:06:47Z | 26091086 to 26092877 (1792) | 12.0536 s | EVM_CENSUS_ETHEREUM (DONE); EVM_TOKENPRICES_ETHEREUM (DONE) | census complete |
| Polygon PoS | polygon/ | 60 min: 2026-09-30T20:07:32Z to 2026-09-30T21:07:30Z | 94729141 to 94731540 (2400) | 1.4998 s | EVM_CENSUS_POLYGON (DONE); EVM_TOKENPRICES_POLYGON (DONE) | census complete |
| Ink (added 2026-10-01) | ink/ | 60 min: 2026-10-01T03:18:30Z to 2026-10-01T04:18:29Z | 57326299 to 57329898 (3600) | 1.0000 s | EVM_CENSUS_INK (DONE); EVM_TOKENPRICES_INK (DONE) | census complete |
| Mantle (added 2026-10-01) | mantle/ | 60 min: 2026-10-01T03:18:30Z to 2026-10-01T04:18:28Z | 101347199 to 101348998 (1800) | 2.0000 s | EVM_CENSUS_MANTLE (DONE); EVM_TOKENPRICES_MANTLE (DONE) | census complete |
| Abstract (added 2026-10-01) | abstract/ | 60 min: 2026-10-01T03:18:33Z to 2026-10-01T04:18:32Z | 86310808 to 86315526 (4719) | 0.7628 s | EVM_CENSUS_ABSTRACT (DONE); EVM_TOKENPRICES_ABSTRACT (DONE) | census complete |
| World Chain (added 2026-10-01) | worldchain/ | 60 min: 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z | 35744536 to 35746335 (1800) | 2.0000 s | EVM_CENSUS_WORLDCHAIN (DONE); EVM_TOKENPRICES_WORLDCHAIN (DONE) | census complete |
| ZKsync Era (added 2026-10-01) | zksync/ | 60 min: 2026-10-01T03:18:09Z to 2026-10-01T04:18:08Z | 72284916 to 72285498 (583) | 6.1838 s | EVM_CENSUS_ZKSYNC (DONE); EVM_TOKENPRICES_ZKSYNC (DONE) | census complete |
| Soneium (added 2026-10-01) | soneium/ | 60 min: 2026-10-01T03:18:31Z to 2026-10-01T04:18:29Z | 28844980 to 28846779 (1800) | 2.0000 s | EVM_CENSUS_SONEIUM (DONE); EVM_TOKENPRICES_SONEIUM (DONE) | census complete |

## Per-chain contents (same layout in every chain directory)

* `blocks.csv.gz`, `txs-NNN.csv.gz`, `reverted-NNN.csv.gz`, `candidates-NNN.jsonl.gz`: the on-chain arbitrage census per the shared definition (eth_getBlockReceipts + eth_getBlockByNumber(block,false) for every block of the window).
* `topic0-counts.csv.gz`: per-topic0 log/tx counts over all transactions of the window (lets the reader see event signatures that are not in the known swap-topic list).
* `swap-topics.csv`: KNOWN SWAP TOPICS (topic0 via `cast keccak`, source URL, first example log in the window = on-chain verification; empty = not observed/verified).
* `window.json`: pinned window, endpoints, request/error counts, integrity checks, measured block interval.
* `tokens-onchain-meta.csv.gz`, `prices-defillama-historical.jsonl.gz`, `native-price-chart-defillama.json`: token decimals/symbols and DefiLlama USD reference prices for tokens seen in candidates.
* `defillama-dexs.json`: raw https://api.llama.fi/overview/dexs/<chain>.
* `docs/` (arbitrum, optimism, unichain only): official transaction-ordering documentation, verbatim text + raw bodies + index.csv with URL and fetch time. (Correction 2026-10-01: the six chains added on 2026-10-01 also have `docs/`, plus `docs/excerpts.jsonl` with verbatim excerpts; "only" refers to the first five chains.)
* `collect/`: the collector scripts and their logs. `_shared_collect/` in this parent holds the master copies of the same scripts (identical md5) plus write_manifest_evm.py, which generated this file. (Checked 2026-10-01: census.py, fetch_defillama.py, fetch_docs.py, make_swap_topics.py, run_token_prices_all.sh, swap_signatures.csv, token_prices.py and write_manifest.py have identical md5 in `_shared_collect/` and in all five chain `collect/` directories; `solana/collect/fetch_docs.py` is also identical. This file was edited by hand on 2026-10-01; re-running write_manifest_evm.py would regenerate the collector's version without these edits.)

## Shared method notes

* Endpoints: publicnode (primary) for every chain; drpc public endpoints (and mainnet.unichain.org for Unichain) as fallbacks; <= 4 HTTP requests in flight per endpoint; JSON-RPC batching of several blocks per HTTP request on the L2s.
* Window end: head minus a small margin at pin time (Polygon: 'finalized' tag); window start: first block with timestamp > end_timestamp - window length. All five windows were pinned at 2026-09-30T21:07:32Z and end within 2026-09-30T21:06:47Z-21:07:30Z chain time.
* Candidate criteria and all schemas: see each chain's MANIFEST.md.

## Coverage limits and gaps (set level)

* One window per chain, same evening (UTC); no repetition across days/times.
* No calldata, no traces (internal transfers, coinbase payments, revert reasons), no mempool/private-orderflow/bundle data, no flashblock-level ordering data for any chain.
* Swap detection is signature-based (see each swap-topics.csv and the list of unmatched venue types in each chain's MANIFEST.md).
* Chains not in this set: Base (other directories), BSC (bsc/, separate collector), Solana (solana/, separate collector; correction 2026-10-01: the collector's text did not point to it), and all other L2s/L1s (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, Sonic, ...). (Correction 2026-10-01: zkSync (ZKsync Era, zksync/) and Mantle (mantle/) are now in this set, together with Ink, Abstract, World Chain and Soneium; Blast, Linea and Scroll remain outside it. See 'Additional L2 chains (2026-10-01)'.)
* Literature on the EVM chains (arXiv papers quoted in the repository file docs/ANALYSIS.md, section 4.1) is not collected in these EVM directories. Solana literature is in solana/docs/literature/.

## Verified inventory (2026-10-01)

Scope of this section: the files of `_shared_collect/` (the files of the five chain directories are inventoried in their own MANIFEST.md). Verified on 2026-10-01 by streaming every file (no file was modified): line counts, CSV parsed with Python's csv module (rows exclude the header line), sha256 over the stored bytes. Git column: "committed" = tracked in git, present in the repository; "local-only" = git-ignored by the repository .gitignore, present only on the collection machine.

Result: 10 files in `_shared_collect/` (9 committed, 1 local-only). No .gz or JSON data files are in `_shared_collect/`. No committed file exceeds 90 MB.

Local-only file and how to regenerate it: `_shared_collect/__pycache__/write_manifest.cpython-311.pyc` is a Python bytecode cache (ignored by the .gitignore rules `research-material/**/__pycache__/` and `*.pyc`). Python recreates it automatically when write_manifest.py is imported, or explicitly with `python3 -m py_compile _shared_collect/write_manifest.py`; no collected data depends on it.

| File | Bytes | Rows / lines | sha256 | Git |
|---|---:|---|---|---|
| _shared_collect/__pycache__/write_manifest.cpython-311.pyc | 33,356 | compiled Python bytecode | e29b581af6f4afa6507ecc6e37d91a297511cb7d4e2e3ad49965ba0fad1cd905 | local-only |
| _shared_collect/census.py | 36,822 | 755 lines | 09bc97c21245f6581c128ad39bc0f7188de8fefd78ec346477f76b123657bcc8 | committed |
| _shared_collect/fetch_defillama.py | 1,196 | 22 lines | b28baddf42a3dbcbcba4826e1763ce8b3465c5e9e016115d1937ce18d7edc4c4 | committed |
| _shared_collect/fetch_docs.py | 4,605 | 82 lines | b4160b7cf24fbbf964717cec8e31f5c28929931a49492e7ee1599d928907a19e | committed |
| _shared_collect/make_swap_topics.py | 2,471 | 57 lines | adc672fd85b8f6866d636fa8d9d3953d492324fcec668dd0ba502be213b2ad0b | committed |
| _shared_collect/run_token_prices_all.sh | 341 | 6 lines | af70ff24229b97ba4dfc11602b4315d6aecdcc8825e55cbee91766bcaaab05a2 | committed |
| _shared_collect/swap_signatures.csv | 5,882 | 23 rows + header | d72b5d53ca5949425a3a5a124f39955cbc26bf74f45b82f92cac63e6a2410e8b | committed |
| _shared_collect/token_prices.py | 10,937 | 212 lines | 379e78b34354c129b3f64be81f24aa33bd6ec7614039172e7e9ab0a7138cba6c | committed |
| _shared_collect/write_manifest.py | 23,378 | 204 lines | 3684ce234e6cb758ab382ea50c0130c407e92959833184d1e424143e9cb41970 | committed |
| _shared_collect/write_manifest_evm.py | 8,331 | 78 lines | 83d8d4cbea12a33dd8fa77eabcbfa17b22c0d445c31552e0a7c3636677bab4f5 | committed |
| MANIFEST-evm.md | (changes when edited) | documentation | not recorded (edited 2026-10-01) | committed |

## Additional L2 chains (2026-10-01)

Added by the other-l2-censuses collection on 2026-10-01. Six chain directories follow the same layout and shared definition as the five chains above: ink/, mantle/, abstract/, worldchain/, zksync/ and soneium/. Their Index rows are at the end of the Index table. How they were chosen (DefiLlama 24 h DEX volume among 11 candidate L2s whose public RPC serves eth_getBlockReceipts) is in `selection.csv` and in `MANIFEST.md`, section 'Additional L2 censuses (2026-10-01)'. That section also has the sentinel texts, commands and the inventory of the new top-level files. Each chain directory's MANIFEST.md has its schemas, endpoints, docs, excerpts, chain-specific notes, coverage limits and verified per-file inventory.

### Method differences from the five chains above (descriptive)

* Same scripts: census.py, make_swap_topics.py, swap_signatures.csv, fetch_defillama.py, fetch_docs.py and token_prices.py in each `<chain>/collect/` are byte-identical to `_shared_collect/` (md5 checked 2026-10-01). Because census.py and token_prices.py hold chain settings in hard-coded dicts, the new chains are run through two wrappers that add the settings at run time and call the unmodified `main()`: `collect/census_l2.py` and `collect/token_prices_l2.py`, with settings in `collect/l2_config.py`. Masters are in `collect/` in this directory; copies in each chain's `collect/` are identical.
* Windows: 60 min each, pinned 2026-10-01T04:18:40-04:18:42Z, ending between 04:18:08Z and 04:18:32Z chain time. The five chains above were pinned 2026-09-30T21:07:32Z.
* Endpoints (primary): ink-rpc.publicnode.com, mantle-rpc.publicnode.com, api.mainnet.abs.xyz, worldchain-mainnet.gateway.tenderly.co, mainnet.era.zksync.io, soneium-rpc.publicnode.com; fallbacks and request/error counts are in each window.json.
* Docs: `docs/` for all six chains, plus `docs/excerpts.jsonl`: verbatim excerpts with source URL, fetch time and character offsets into the stored text. They are written by `collect/make_doc_excerpts.py` from `collect/docs_excerpts_spec.json`.
* Manifests written by `collect/write_manifest_l2.py` (not by write_manifest.py), with the question-line mapping by line number and a verified inventory.

### Question lines served (mapping only)

`<l2>` = each of ink/, mantle/, abstract/, worldchain/, zksync/, soneium/. "census files" and "token/price files" as in the table above; the same mapping is in each `<l2>/MANIFEST.md`.

| Line | ink/ | mantle/ | abstract/ | worldchain/ | zksync/ | soneium/ |
|---|---|---|---|---|---|---|
| 1 | none | none | none | none | none | none |
| 2 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz | same | same | same | same | same |
| 3 | candidates-001.jsonl.gz, tokens-onchain-meta.csv.gz | same | same | same | same | same |
| 4 | census files, token/price files, defillama-dexs.json (+ .fetch.json) | same | same | same | same | same |
| 5 | candidates-001.jsonl.gz, blocks.csv.gz, txs-001.csv.gz, docs/ (incl. excerpts.jsonl) | same | same | same | same | same |
| 6 | docs/ (incl. excerpts.jsonl) | same | same | same | same | same |
| 7 | census files, token/price files | same | same | same | same | same |
| 8 | census files | same | same | same | same | same |

Top-level files added with these chains (`selection.csv`, `defillama-overview-dexs-all-chains.json.gz` + `.fetch.json`, `defillama-overview-dexs-candidates.jsonl.gz`, `rpc-receipts-probe-candidates.jsonl.gz`) serve line 4. `collect/` holds scripts and logs and is not mapped.
