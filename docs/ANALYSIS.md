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

### 2.3 Correction: the flashblock run had ~10 s state freshness, not 200 ms

Re-analysis of the run records showed every episode starting on a :x0-second boundary with a byte-identical
prediction for ten seconds, and successful simulations clustered in the first three seconds after each boundary.
A direct test explains it: the public preconfirmation endpoint accepts about 5 requests per 10 s and answers
HTTP 429 for the rest of the window, and `syncPools` silently kept the old state when a batch was rejected.
Consequences for the numbers above:

* the 46 successful simulations and their dollar sizes are valid (each was checked against live state);
* the "median lifetime of 6 blocks" and the 87 % simulation revert rate are artifacts of frozen local state,
  not measurements of competition;
* the true opportunity flow at 200 ms freshness is **unmeasured**; it requires a dedicated node or paid endpoint
  that can serve pending state at 5 Hz. The bot now detects rejected refreshes and skips the tick instead of
  searching on stale data.

### 2.4 Why candidates through Slipstream pools reverted

The trace of a representative failure (USDC → XDP → USDC across Uniswap V3 and Slipstream-3) shows the
Slipstream pool's fee module returning 100,000 pips (10 %) at swap time while the same pool reported 0.01 %
minutes later. Slipstream fees are set per pool by a dynamic module and move with volatility, i.e. precisely when
price gaps open. The bot now quotes such pools with the maximum fee observed over a recent window and parks a
route after three consecutive reverts.

## 3. Conclusions

1. **The architecture in the videos (listen for `Swap` events, then send a transaction) produces nothing.**
   At block boundaries, on every chain measured, the cross-DEX price gaps for liquid tokens are already inside
   the fee band.
2. **With ~10 s state on Base (what public endpoints actually sustain), small opportunities exist.** They are
   worth cents, not dollars: 14 verified episodes in 23 minutes, median $0.026 and largest $0.17 of simulated net
   profit, $0.61 in total, with trade sizes between $140 and $2,700 (median $250). What 200 ms freshness would
   add is unmeasured here. Breadth (more pools, Uniswap V4, more tokens) scales the count roughly linearly; it
   does not change the per-episode size.
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

## 4. Engineering results (phase 2)

All measured live on Base on 2026-09-30 unless stated.

| Component | Result |
|---|---|
| Event-driven state engine (`bot/src/pools/events.ts`) | State derived from Swap/Sync/Mint/Burn/ModifyLiquidity logs matches multicall state exactly: 37/37 touched pools over 3 blocks, 0 mismatches, including same-block Mint/Burn and Uniswap V4 |
| Block log source | `eth_getBlockReceipts` ≈ 100 ms per block on a public node vs 11 s for a 600-address `eth_getLogs` filter; on a local node this is single-digit ms |
| Pool→cycle index + closed-form sizing (`bot/src/arb/incremental.ts`, `search.ts`) | 2.3 ms per block to re-evaluate every cycle through the ~22 pools that trade in a typical block, identical results to the full search (111/111); full search 40 ms; the closed form is exact when no tick is crossed and seeds the search otherwise |
| Uniswap V4 protocol fee | Base V4 pools charge lp + protocol fee (e.g. 625 pips effective vs 500 lp); the effective fee is direction-dependent and now taken from the packed `protocolFee` in `getSlot0` and from each Swap event |
| Slipstream dynamic fees | 2,486 fee transitions in 484 blocks across 36 pools (e.g. AERO/cbBTC oscillating 750↔2700 pips every few blocks). Quoting uses the max fee over a recent window |
| Public preconf RPC | ≈5 requests per 10 s before HTTP 429; unusable for sustained 200 ms state. Sync failures are now detected and the tick is skipped |
| Executor self-check | On start the bot proves the deployed/injected bytecode and its ABI agree (an invalid route must revert with `BadRoute()`); a stale runtime artifact previously made every simulation fail silently |

### 4.1 What the 2026 measurement literature says (sources in the agent reports, all publicly available)

* Base, Jun 2025–Feb 2026: 21.4 M successful cyclic arbitrages by 4,365 bot addresses; 986 M spam transactions.
  Success rate by architecture: off-chain discovery 42.5 %, on-chain evaluation 18.5 %, on-chain probing 4.6 %.
  Flashblocks (Jul 2025) cut active bots from 983 to 462 in four weeks. (Wu & Öz, arXiv 2606.00720)
* Base retains only 7.34 % of atomic-arbitrage revenue as priority fees (Ethereum: 28.8 %). Ordering is by arrival
  time at 200 ms flashblock granularity, then by priority fee within the flashblock. (Entropy Advisors; docs.base.org)
* Arbitrum atomic (DEX-DEX) arbitrage profit, Apr–Jul 2025: ≈ $503 K total across all searchers, ≈ $4.7 K/day, mean
  $0.78 per arbitrage. (Messias & Torres, arXiv 2509.22143)
* Once fees on failed transactions are counted, the share of profitable bots is 28 % on Base and 24 % on Optimism.
  (arXiv 2607.24172)
* Losses come from standing token approvals, unauthenticated callbacks and fake tokens/pools: 104 attacks, $2.76 M
  (arXiv 2504.13398); JaredFromSubway drained of $7.5–15 M on 2026-06-20 via fake WETH/USDC/USDT and standing
  approvals. `ArbExecutor` grants no standing approvals and authenticates every callback in transient storage.
* Leverage: ETH fell 66–68 % peak-to-trough twice (2025, 2025–26); an Aave 2x loop liquidates near −40 %, with a 5 %
  liquidation bonus on Base WETH. Aave liquidated $429 M in six days in Feb 2026.
* CEX-DEX (non-atomic) arbitrage: top-3 operators ≈ 90 % of $233.8 M extracted; 1 of 19 labeled searchers net-negative.

### 4.2 Capital-based strategies from the other videos (measured 2026-09-30)

* Perp funding on OKX/Hyperliquid for the top-20 pairs sits at the 10.95 %/yr baseline (0.01 % per 8 h); cross-venue
  differentials of 5–24 %/yr exist on volatile alts and flip sign. A spot+perp basis trade costs ≈ 0.30 % in taker
  fees to open and close. On $5 K of capital that is tens of dollars per month, before exchange and liquidation risk
  on the short leg.
* Base ETH pools follow OKX's mid with a ~1 s lag (sign agreement 83–93 % at 1 s vs 66–69 % at 4 s), but the
  ETH/USDC deviation around its median is ±5 bps at the 5th/95th percentiles and never exceeded 20 bps in 26 minutes:
  inside the fee band. See §5 for long-tail tokens.

## 5. Every arbitrage angle in the videos, measured (2026-09-30, public data, no accounts)

| Angle | What was measured | Result |
|---|---|---|
| DEX↔DEX atomic, 2-hop (videos 1-3) | Base, 12 venues incl. Uniswap V4, block and flashblock state, flash-swap funded, on-chain simulation | Verified episodes are worth cents; see §2 and §6 |
| DEX triangular (3 pools) | Included in every scan/dry run (`findTriangles`) | No 3-hop cycle cleared $0.01 net in any run; the two candidates that did were simulated and reverted |
| Slipstream dynamic-fee timing (own angle) | 209 pools, 1,041 blocks, 4,527 fee transitions | Best cycle through a pool after a fee drop averages $0.0001 vs $0.0005 baseline: nothing to time |
| CEX→DEX lead-lag, ETH (statistical) | OKX ETH-USDT every 250 ms vs 3 Base pools every block, 45 min | Base follows OKX with ~1 s lag (sign agreement 80-90 % at 1 s vs 60-70 % at 4 s); deviation of the pool price from its median ±5 bps at p5/p95, never >20 bps. Backtest of "trade the lag" on the pool with the 4-5 bps fee: 7 signals, 0-14 % win rate, mean −4 to −9 bps per trade; on the 1 bp pool 4 signals, +2 to +4 bps mean (n=4, noise) |
| CEX→DEX lead-lag, long tail | OKX vs deepest Base pool for VIRTUAL, DEGEN, ZORA, LINK, MORPHO, 30 min every block | Deviation from the median >30 bps in 0-4 % of blocks, never >60 bps |
| CEX↔CEX spatial (videos 4-5) | OKX, Gate, Kraken; 2,350 cross-listed pairs; executable bid/ask spread net of base-tier taker fees every 2 s for 15 min | Genuine pairs net-positive in <2 % of samples at 1-11 bps. Every persistent "spread" was a ticker collision (LIT, EDGE = different tokens), a withdrawal-disabled asset (CT) or a slow-transfer asset (STX on Stacks, DOG on Runes) |
| CEX triangular (video 4) | OKX and Gate, every A/USDT-B/USDT-A/B triangle with ≥$20k volume on all legs, net of 3 taker fees, 445 samples over 15 min | **0** triangles ever net-positive |
| Cross-chain DEX↔DEX | WETH/USDC Uniswap V3 0.05 % on Base, Arbitrum, Ethereum every 2 s, 450 samples | Spreads p5/p95 within ±5 bps, never >10 bps, before the 5 bps fee per leg and bridging |
| Spot-perp funding carry (video 5) | OKX and Hyperliquid, top-20 perps | 10.95 %/yr baseline (0.01 % per 8 h) on the majors; cross-venue differentials 5-24 %/yr on volatile alts; 0.30 % fees to open and close |
| Spot-futures basis (video 5) | OKX dated futures vs spot | 3.2-5.2 %/yr BTC, 3.2-4.5 %/yr ETH across all expiries, locked in at entry |

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
