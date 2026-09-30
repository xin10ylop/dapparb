# Findings: what the flash-loan strategies from the videos actually yield in 2026

All numbers below were measured live on 30 Sep 2026 with the code in this repository, from a cloud container
using public RPC endpoints. Nothing was deployed on a mainnet; every figure comes from simulation against live
chain state (`eth_call` with the executor bytecode injected via state override) or from fork tests.

## 1. Setup

| Item | Value |
|---|---|
| Chains scanned | Base (primary), Arbitrum One, Ethereum mainnet |
| Base venues covered | Uniswap V2/V3, Aerodrome V2 (volatile + stable), Aerodrome Slipstream (3 factories), PancakeSwap V2/V3, SushiSwap V2/V3, BaseSwap; Uniswap V4 hookless pools |
| Token universes | hand-picked top 19 tokens; "long tail" = distinct tokens in GeckoTerminal's top-volume pools |
| Live pools after depth filter (≥ 0.2 ETH depth) | 253 (top-19 universe), 342 (long-tail universe) |
| State freshness | block boundary (2 s) and Base Flashblocks (~200 ms, via the preconfirmation RPC's `pending` tag) |
| Cycle types | 2-pool cycles (both orientations) and 3-pool triangles starting in WETH or USDC |
| Gas cost per attempt on Base | ≈ $0.004–0.006 (L2 gas 0.006 gwei + L1 data fee) |
| Verification | local V3 math vs. on-chain quoters: 0 mismatches; fork pipeline test: simulated profit = predicted profit (ratio 1.000000) and the transaction landed with that profit |

## 2. Results

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

### 2.2 Flashblock-granularity dry run (long-tail universe, simulation on every candidate)

Window 12:04–12:25 UTC (0.34 h), 4,455 flashblock ticks, sync + search ≈ 170 ms per tick.

| Metric | Value |
|---|---|
| Candidates with predicted net > $0.01 | 374 across 12 routes (23 episodes) |
| Simulated OK / reverted | 46 / 328 |
| Episodes with simulated net ≥ $0.01 at least once | **12** (≈ 35 per hour) |
| Lifetime of those episodes | median 6 blocks (≈ 12 s), min 1 |
| Sum of best simulated net per episode | **$0.57** → ≈ $1.65 per hour, ≈ $40 per day, as an upper bound that assumes every one is captured |
| Largest single episode | $0.17 net (USDC/WETH between Slipstream-3 and PancakeSwap V3 0.01 %), executable for 6 consecutive blocks |
| Simulated / predicted profit on stable state | 0.96–1.00 |

### 2.3 Why most candidates reverted

The trace of a representative failure (USDC → XDP → USDC across Uniswap V3 and Slipstream-3) shows the
Slipstream pool's fee module returning 100,000 pips (10 %) at swap time while the same pool reported 0.01 %
minutes later. Slipstream fees are set per pool by a dynamic module and move with volatility, i.e. precisely when
price gaps open. The bot now quotes such pools with the maximum fee observed over a recent window and parks a
route after three consecutive reverts.

## 3. Conclusions

1. **The architecture in the videos (listen for `Swap` events, then send a transaction) produces nothing.**
   At block boundaries, on every chain measured, the cross-DEX price gaps for liquid tokens are already inside
   the fee band.
2. **With 200 ms state on Base, small opportunities do exist and persist for seconds.** They are worth cents, not
   dollars: about $1.65 per hour of simulated upper bound over 342 pools, before any lost races or reverted
   transactions. Breadth (more pools, Uniswap V4, more tokens) scales this roughly linearly; it does not change
   the order of magnitude.
3. **Flash loans are not the constraint.** Capital was never the binding factor in any measured episode; the
   largest optimal trade size was well under $1,000. Flash swaps (zero fee) cover every case; Morpho Blue is the
   only Base flash-loan pool with meaningful zero-fee depth (Balancer V2 on Base holds ~29 WETH after the
   November 2025 exploit).
4. **The leverage strategy (videos 1 and 2) is not income.** `LeverageManager` reproduces the example exactly
   (2,000 USDC own + 2,000 USDC borrowed → 1.483 WETH collateral, 2,000 USDC debt, health factor 1.66). The
   round trip costs about $5 in swap fees and the position is liquidated on roughly a 40 % drawdown of ETH.
   It is a way to take amplified directional risk in one transaction, nothing more.
5. **The "$4 million in seven days" figure** is the aggregate of the whole ecosystem's atomic arbitrage, most of
   which is paid to block builders and captured by a small number of operators with private infrastructure. None
   of it is visible to a public-RPC bot at block or flashblock granularity in these measurements.

## 4. What is reproducible here

```bash
cd bot
npx tsx src/research/scan.ts --chain base --blocks 60 --universe top --pages 10 --max-tokens 250
npx tsx src/main.ts --chain base --mode dry --source flashblocks --universe top --min-profit-usd 0.01
npx tsx src/research/analyze.ts data/live-base.jsonl
```

Raw records from the runs referenced above are not committed (they are in `bot/data/`, git-ignored) but the
scripts regenerate them in minutes.
