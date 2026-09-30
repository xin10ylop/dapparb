# 06-other-chains-onchain: EVM on-chain arbitrage census index (Arbitrum, Optimism, Unichain, Ethereum, Polygon)

Collected 2026-09-30 (UTC). Raw material only: no analysis, estimates or conclusions anywhere in these directories. Each chain directory has its own MANIFEST.md with schemas, row counts, endpoints, reproduction commands and a 'Coverage limits and gaps' section.

`bsc/` in this parent directory is produced by a separate collector with its own manifest and is not indexed here.

## Question-line IDs (verbatim user text)

| ID | Question line |
|---|---|
| Q-V4BASE | Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet. |
| Q-OLDV2 | Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens. |
| Q-SMALLPOOLS | Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit. |
| Q-OTHERCHAINS | Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured. |
| Q-GAPS | Would the gaps change the answer? |
| Q-V4LAUNCH | V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee. |
| Q-BSCORDER | BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents. |
| Q-STUDIES | Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions. |
| Q-COVERAGE | So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test. |

## Mapping (which directory serves which line)

| Directory | Question lines |
|---|---|
| arbitrum/ | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-STUDIES (Arbitrum $4,700/day line), Q-V4LAUNCH (V4 swaps + priority fees on Arbitrum), Q-OLDV2, Q-SMALLPOOLS (as observed on Arbitrum), Q-BSCORDER (comparison: Timeboost / PGA ordering docs) |
| optimism/ | Q-OTHERCHAINS (other L2s), Q-GAPS, Q-COVERAGE, Q-STUDIES (failed-transaction cost line), Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: OP-stack sequencer / Flashblocks ordering docs) |
| unichain/ | Q-OTHERCHAINS (other L2s), Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: Unichain TEE priority ordering / Flashblocks / revert-protection docs) |
| ethereum/ | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: builder tags miner/extraData per block) |
| polygon/ | Q-OTHERCHAINS (other chains), Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS |

Q-V4BASE is not served by these directories (Base only).

## Index

| Chain | Dir | Window (chain time, UTC) | Blocks | Measured block interval | Sentinel | Status |
|---|---|---|---|---|---|---|
| Arbitrum One | arbitrum/ | 60 min: 2026-09-30T20:07:21Z to 2026-09-30T21:07:20Z | 510447028 to 510460284 (13257) | 0.2715 s | EVM_CENSUS_ARBITRUM (DONE); EVM_TOKENPRICES_ARBITRUM (DONE) | census complete |
| OP Mainnet | optimism/ | 60 min: 2026-09-30T20:07:23Z to 2026-09-30T21:07:21Z | 157600033 to 157601832 (1800) | 2.0000 s | EVM_CENSUS_OPTIMISM (DONE); EVM_TOKENPRICES_OPTIMISM (DONE) | census complete |
| Unichain | unichain/ | 60 min: 2026-09-30T20:07:22Z to 2026-09-30T21:07:21Z | 60050483 to 60054082 (3600) | 1.0000 s | EVM_CENSUS_UNICHAIN (DONE); EVM_TOKENPRICES_UNICHAIN (DONE) | census complete |
| Ethereum mainnet | ethereum/ | 6 h: 2026-09-30T15:06:59Z to 2026-09-30T21:06:47Z | 26091086 to 26092877 (1792) | 12.0536 s | EVM_CENSUS_ETHEREUM (DONE); EVM_TOKENPRICES_ETHEREUM (DONE) | census complete |
| Polygon PoS | polygon/ | 60 min: 2026-09-30T20:07:32Z to 2026-09-30T21:07:30Z | 94729141 to 94731540 (2400) | 1.4998 s | EVM_CENSUS_POLYGON (DONE); EVM_TOKENPRICES_POLYGON (DONE) | census complete |

## Per-chain contents (same layout in every chain directory)

* `blocks.csv.gz`, `txs-NNN.csv.gz`, `reverted-NNN.csv.gz`, `candidates-NNN.jsonl.gz`: the on-chain arbitrage census per the shared definition (eth_getBlockReceipts + eth_getBlockByNumber(block,false) for every block of the window).
* `topic0-counts.csv.gz`: per-topic0 log/tx counts over all transactions of the window (lets the reader see event signatures that are not in the known swap-topic list).
* `swap-topics.csv`: KNOWN SWAP TOPICS (topic0 via `cast keccak`, source URL, first example log in the window = on-chain verification; empty = not observed/verified).
* `window.json`: pinned window, endpoints, request/error counts, integrity checks, measured block interval.
* `tokens-onchain-meta.csv.gz`, `prices-defillama-historical.jsonl.gz`, `native-price-chart-defillama.json`: token decimals/symbols and DefiLlama USD reference prices for tokens seen in candidates.
* `defillama-dexs.json`: raw https://api.llama.fi/overview/dexs/<chain>.
* `docs/` (arbitrum, optimism, unichain only): official transaction-ordering documentation, verbatim text + raw bodies + index.csv with URL and fetch time.
* `collect/`: the collector scripts and their logs. `_shared_collect/` in this parent holds the master copies of the same scripts (identical md5) plus write_manifest_evm.py, which generated this file.

## Shared method notes

* Endpoints: publicnode (primary) for every chain; drpc public endpoints (and mainnet.unichain.org for Unichain) as fallbacks; <= 4 HTTP requests in flight per endpoint; JSON-RPC batching of several blocks per HTTP request on the L2s.
* Window end: head minus a small margin at pin time (Polygon: 'finalized' tag); window start: first block with timestamp > end_timestamp - window length. All five windows were pinned at 2026-09-30T21:07:32Z and end within 2026-09-30T21:06:47Z-21:07:30Z chain time.
* Candidate criteria and all schemas: see each chain's MANIFEST.md.

## Coverage limits and gaps (set level)

* One window per chain, same evening (UTC); no repetition across days/times.
* No calldata, no traces (internal transfers, coinbase payments, revert reasons), no mempool/private-orderflow/bundle data, no flashblock-level ordering data for any chain.
* Swap detection is signature-based (see each swap-topics.csv and the list of unmatched venue types in each chain's MANIFEST.md).
* Chains not in this set: Base (other directories), BSC (bsc/, separate collector), Solana, and all other L2s/L1s (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, Sonic, ...).
* Literature (arXiv papers quoted in docs/ANALYSIS.md 4.1) is not collected in this directory.
