#!/usr/bin/env python3
"""Writes ../MANIFEST-evm.md (index of the five EVM census directories) from their window.json files.
usage: python3 write_manifest_evm.py <parent_dir>"""
import datetime, json, os, sys

P = os.path.abspath(sys.argv[1])
CH = [("arbitrum", "Arbitrum One", "EVM_CENSUS_ARBITRUM", "60 min"), ("optimism", "OP Mainnet", "EVM_CENSUS_OPTIMISM", "60 min"),
      ("unichain", "Unichain", "EVM_CENSUS_UNICHAIN", "60 min"), ("ethereum", "Ethereum mainnet", "EVM_CENSUS_ETHEREUM", "6 h"),
      ("polygon", "Polygon PoS", "EVM_CENSUS_POLYGON", "60 min")]
S = "/home/user/dapparb/research-material/.sentinels"


def utc(ts):
    return datetime.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ")


L = []
A = L.append
A("# 06-other-chains-onchain: EVM on-chain arbitrage census index (Arbitrum, Optimism, Unichain, Ethereum, Polygon)\n")
A("Collected 2026-09-30 (UTC). Raw material only: no analysis, estimates or conclusions anywhere in these directories. Each chain directory has its own MANIFEST.md with schemas, row counts, endpoints, reproduction commands and a 'Coverage limits and gaps' section.\n")
A("`bsc/` in this parent directory is produced by a separate collector with its own manifest and is not indexed here.\n")
A("## Question-line IDs (verbatim user text)\n")
Q = [
    ("Q-V4BASE", "Uniswap V4 on Base. This is the biggest gap. Clanker and Zora launch new tokens as V4 pools with hooks, and I only had 20 V4 pools. The engine supports V4. It just doesn't list every V4 pool yet."),
    ("Q-OLDV2", "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs. Almost all the older ones are abandoned tokens."),
    ("Q-SMALLPOOLS", "Pools under 0.1 ETH of liquidity. Profit is capped at a slice of a pool's liquidity, so these pay a few dollars at most. They are also where most tokens that block or tax transfers sit."),
    ("Q-OTHERCHAINS", "Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum. BSC, where PancakeSwap is biggest, Solana and the other L2s were not measured."),
    ("Q-GAPS", "Would the gaps change the answer?"),
    ("Q-V4LAUNCH", "V4 launches are the one place a bigger number could appear. New launches open large, short-lived price gaps. It is also the most fought-over flow on Base. The RSR trade shows how contested gaps end: the winner kept 3% and paid the rest as priority fee."),
    ("Q-BSCORDER", "BSC has the same ordering problem. Its transaction ordering goes through private block builders, so a public bot still lands behind the incumbents."),
    ("Q-STUDIES", "Chain-wide studies already count every pool. On Arbitrum, atomic arbitrage totals about $4,700 a day for all bots combined. On Base, 4,365 bots made 21.4 million arbitrages over nine months, and only 28% of those bots were profitable after paying for failed transactions."),
    ("Q-COVERAGE", "So the search went far beyond selected pairs, but it did not cover everything. The one gap where I wouldn't predict the result is full Uniswap V4 coverage on Base. Measuring it means listing every V4 pool from the pool manager's creation events and rerunning the same 20-minute live test."),
]
A("| ID | Question line |\n|---|---|")
for k, v in Q:
    A("| %s | %s |" % (k, v))
A("\n## Mapping (which directory serves which line)\n")
A("| Directory | Question lines |\n|---|---|")
A("| arbitrum/ | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-STUDIES (Arbitrum $4,700/day line), Q-V4LAUNCH (V4 swaps + priority fees on Arbitrum), Q-OLDV2, Q-SMALLPOOLS (as observed on Arbitrum), Q-BSCORDER (comparison: Timeboost / PGA ordering docs) |")
A("| optimism/ | Q-OTHERCHAINS (other L2s), Q-GAPS, Q-COVERAGE, Q-STUDIES (failed-transaction cost line), Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: OP-stack sequencer / Flashblocks ordering docs) |")
A("| unichain/ | Q-OTHERCHAINS (other L2s), Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: Unichain TEE priority ordering / Flashblocks / revert-protection docs) |")
A("| ethereum/ | Q-OTHERCHAINS, Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS, Q-BSCORDER (comparison: builder tags miner/extraData per block) |")
A("| polygon/ | Q-OTHERCHAINS (other chains), Q-GAPS, Q-COVERAGE, Q-V4LAUNCH, Q-OLDV2, Q-SMALLPOOLS |")
A("\nQ-V4BASE is not served by these directories (Base only).\n")
A("## Index\n")
A("| Chain | Dir | Window (chain time, UTC) | Blocks | Measured block interval | Sentinel | Status |\n|---|---|---|---|---|---|---|")
for c, name, sen, span in CH:
    wp = os.path.join(P, c, "window.json")
    if not os.path.exists(wp):
        A("| %s | %s/ | (not pinned) | | | %s | MISSING |" % (name, c, sen)); continue
    w = json.load(open(wp))
    st = "DONE" if os.path.exists(os.path.join(S, sen + ".DONE")) else ("FAILED" if os.path.exists(os.path.join(S, sen + ".FAILED")) else "IN PROGRESS")
    tps = "EVM_TOKENPRICES_%s" % c.upper()
    tpst = "DONE" if os.path.exists(os.path.join(S, tps + ".DONE")) else ("FAILED" if os.path.exists(os.path.join(S, tps + ".FAILED")) else "IN PROGRESS")
    A("| %s | %s/ | %s: %s to %s | %d to %d (%d) | %.4f s | %s (%s); %s (%s) | census %s |" % (
        name, c, span, utc(w["start_timestamp"]), utc(w["end_timestamp"]), w["start_block"], w["end_block"],
        w.get("n_blocks_in_window", w["end_block"] - w["start_block"] + 1), w.get("measured_block_interval_s", 0.0), sen, st, tps, tpst, w.get("status")))
A("\n## Per-chain contents (same layout in every chain directory)\n")
A("* `blocks.csv.gz`, `txs-NNN.csv.gz`, `reverted-NNN.csv.gz`, `candidates-NNN.jsonl.gz`: the on-chain arbitrage census per the shared definition (eth_getBlockReceipts + eth_getBlockByNumber(block,false) for every block of the window).")
A("* `topic0-counts.csv.gz`: per-topic0 log/tx counts over all transactions of the window (lets the reader see event signatures that are not in the known swap-topic list).")
A("* `swap-topics.csv`: KNOWN SWAP TOPICS (topic0 via `cast keccak`, source URL, first example log in the window = on-chain verification; empty = not observed/verified).")
A("* `window.json`: pinned window, endpoints, request/error counts, integrity checks, measured block interval.")
A("* `tokens-onchain-meta.csv.gz`, `prices-defillama-historical.jsonl.gz`, `native-price-chart-defillama.json`: token decimals/symbols and DefiLlama USD reference prices for tokens seen in candidates.")
A("* `defillama-dexs.json`: raw https://api.llama.fi/overview/dexs/<chain>.")
A("* `docs/` (arbitrum, optimism, unichain only): official transaction-ordering documentation, verbatim text + raw bodies + index.csv with URL and fetch time.")
A("* `collect/`: the collector scripts and their logs. `_shared_collect/` in this parent holds the master copies of the same scripts (identical md5) plus write_manifest_evm.py, which generated this file.\n")
A("## Shared method notes\n")
A("* Endpoints: publicnode (primary) for every chain; drpc public endpoints (and mainnet.unichain.org for Unichain) as fallbacks; <= 4 HTTP requests in flight per endpoint; JSON-RPC batching of several blocks per HTTP request on the L2s.")
A("* Window end: head minus a small margin at pin time (Polygon: 'finalized' tag); window start: first block with timestamp > end_timestamp - window length. All five windows were pinned at 2026-09-30T21:07:32Z and end within 2026-09-30T21:06:47Z-21:07:30Z chain time.")
A("* Candidate criteria and all schemas: see each chain's MANIFEST.md.")
A("\n## Coverage limits and gaps (set level)\n")
A("* One window per chain, same evening (UTC); no repetition across days/times.")
A("* No calldata, no traces (internal transfers, coinbase payments, revert reasons), no mempool/private-orderflow/bundle data, no flashblock-level ordering data for any chain.")
A("* Swap detection is signature-based (see each swap-topics.csv and the list of unmatched venue types in each chain's MANIFEST.md).")
A("* Chains not in this set: Base (other directories), BSC (bsc/, separate collector), Solana, and all other L2s/L1s (Blast, Linea, zkSync, Scroll, Mantle, Avalanche, Sonic, ...).")
A("* Literature (arXiv papers quoted in docs/ANALYSIS.md 4.1) is not collected in this directory.")
open(os.path.join(P, "MANIFEST-evm.md"), "w").write("\n".join(L) + "\n")
print("wrote", os.path.join(P, "MANIFEST-evm.md"))
