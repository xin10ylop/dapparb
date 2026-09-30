# Verbatim excerpts from docs/ANALYSIS.md (reference only)

Copied 2026-09-30T22:06Z from `docs/ANALYSIS.md` in the working tree (HEAD fd66f90; file sha256 37fe782b446bf7bb…). Text between the markers is unchanged; line numbers refer to that file. No commentary added.

## Excerpt 1: section 2.1 (lines 22-34)

<!-- BEGIN VERBATIM docs/ANALYSIS.md:22-34 -->
### 2.1 Block-boundary scans (every DEX pair for the token universe, every block)

| Run | Chain | Blocks | Pools | Gross-positive cycles | Net-positive after gas |
|---|---|---|---|---|---|
| top-19 tokens | Base | 120 | 565 | 2,544 | **0** |
| top-19 tokens, corrected direction + depth filter | Base | 25 | 253 | — | 2 per block, all ≈ $0.001 (one TOSHI route) |
| long-tail tokens | Base | 30 | 342 | — | 2–4 per block, all < $0.005 |
| config tokens | Ethereum mainnet | 20 | 106 | 98 per block | 0 (best gross $0.026 vs ≈ $0.10 gas) |
| config tokens | Arbitrum | 200 | 111 | — | 0 after removing Camelot (custom fee model) |

Every "gross-positive" hit at block boundaries was worth a fraction of a cent. The one persistent route
(TOSHI between SushiSwap V2 and Slipstream) was simulated on-chain and returned exactly the predicted $0.004,
so the model is right: the opportunity is real and worthless.
<!-- END VERBATIM -->

## Excerpt 2: section 5 heading, table header, and the table row that covers chains other than Base (lines 234-237, 245)

<!-- BEGIN VERBATIM docs/ANALYSIS.md:234-237 -->
## 5. Every arbitrage angle in the videos, measured (2026-09-30, public data, no accounts)

| Angle | What was measured | Result |
|---|---|---|
<!-- END VERBATIM -->
<!-- BEGIN VERBATIM docs/ANALYSIS.md:245 -->
| Cross-chain DEX↔DEX | WETH/USDC Uniswap V3 0.05 % on Base, Arbitrum, Ethereum every 2 s, 450 samples | Spreads p5/p95 within ±5 bps, never >10 bps, before the 5 bps fee per leg and bridging |
<!-- END VERBATIM -->

## Excerpt 3: section 1 table header and the 'Chains scanned' row (lines 9-11)

<!-- BEGIN VERBATIM docs/ANALYSIS.md:9-11 -->
| Item | Value |
|---|---|
| Chains scanned | Base (primary), Arbitrum One, Ethereum mainnet |
<!-- END VERBATIM -->

## Excerpt 4: section 6 reproduction commands (lines 250-266)

<!-- BEGIN VERBATIM docs/ANALYSIS.md:250-266 -->
## 6. What is reproducible here

```bash
cd bot
npx tsx src/research/scan.ts --chain base --blocks 60 --universe top --pages 10 --max-tokens 250
npx tsx src/main.ts --chain base --mode dry --source logs --universe top --min-profit-usd 0.01   # event-driven
npx tsx src/research/analyze.ts data/live-base.jsonl
npx tsx --test src/pools/events.live.test.ts          # log-derived state == multicall state
npx tsx src/arb/incremental.bench.ts                  # incremental vs full search on live blocks
npx tsx src/research/feetiming.ts --minutes 45        # Slipstream dynamic-fee study
npx tsx src/research/leadlag.ts --minutes 45          # OKX vs Base ETH lead-lag
npx tsx src/research/leadlag-multi.ts --minutes 30    # OKX vs Base long-tail tokens
npx tsx src/research/carry.ts                         # funding / basis snapshot
```

Raw records from the runs referenced above are not committed (they are in `bot/data/`, git-ignored) but the
scripts regenerate them in minutes.
<!-- END VERBATIM -->
