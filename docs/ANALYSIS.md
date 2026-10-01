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

### 2.5 Reference run with the event-driven engine (exact state, decoded reverts)

22 minutes, 657 pools, block-level receipts from a public node, every candidate simulated:

| Metric | Value |
|---|---|
| Executable episodes (simulated net ≥ $0.01) | 24 → 65 per hour |
| Sum of best simulated net | $1.75 → **$4.77/hour ceiling at 100 % capture** (≈ $115/day) |
| Largest single episode | $0.51 (WETH/USDC, Uniswap V3 0.01 % ↔ PancakeSwap V3 0.01 %); next $0.43 (WETH/VIRTUAL) |
| Median lifetime | 1 block (2 s): with correct state, opportunities close within the next block |
| Where | XDP/USDC (21 of 24), WETH/USDC, WETH/VIRTUAL, USDC/PROS |
| Simulated reverts | 69, now decoded: `TransferFailed` (token-side restrictions), `UniswapV2: K`, `CannotRepay` short by 0.03–0.5 % |

### 2.6 Full-factory universe: does the ceiling scale with pool count?

Same engine as §2.5, but the universe is every pool the factories know about instead of the configured token
list: `--universe all --max-per-factory 6000` enumerates the newest 6,000 pools of each V2-style factory and
every Slipstream pool (Aerodrome CL: 3,648 + 2,766 + 2,259; Aerodrome V2: 6,000 of 29,600; Uniswap V2:
6,000 of 3,063,599; Sushi, Pancake, BaseSwap: ~6,000 each), resolves every V3/Pancake fee tier for each pair,
adds the Uniswap V4 pools GeckoTerminal lists, and keeps pools with at least 0.1 ETH of depth.

**The first run of this universe reported fake profit.** Its largest "episode" was $28.88 on a WMTW/USDC
cycle with a 4,010,240,259 bps gap. On-chain both WMTW pools hold a combined $0.002 of USDC. The token had
been priced from its own dead pool; that price then valued the pool's WMTW side at 0.1 ETH and it passed the
depth filter. Fix (`pricing.ts`, `depth.ts`): a token is priced only through WETH or USDC pools whose anchor
side holds at least 0.05 ETH (depth-weighted median across such pools), and a pool's depth is the smaller of
its two priced sides, so the side that could never be bought out of a dead pool cannot carry it. The run was
restarted with the fix; the universe after the filter went from 3,282 pools to 3,189 (3,608 cycles), versus
657 pools in §2.5.

**One real episode from the first run, traced on-chain.** At block 51998756 the searcher found
WETH→RSR (Uniswap V3 1 %)→WETH (Aerodrome) for 0.139021 WETH in, simulated net $13.07, gap 854 bps; the gap
had been opened in that block by a 1.67 M-gas transaction that bought RSR on Aerodrome. In the next block
(51998757), at transaction index 1, address `0xF0523316…` (481,276 transactions sent, 20 ETH balance) closed
it through contract `0xA0578728…` with 0.139020 WETH in: the same optimum to five decimals. Its receipt:

| | |
|---|---|
| Gross (WETH received − WETH spent) | 0.004871 WETH = $13.12 |
| Gas: 208,864 × 22.575 gwei (priority fee 22.570 gwei; Base's normal tip is ~0.001–0.05 gwei) | 0.004715 ETH = $12.70 |
| Kept | 0.000156 ETH = **$0.42**, 3.2 % of the gap |

**That operator's economics, measured.** Its last 50 transactions (1.82 h, 44 landed, 6 reverted) were
valued exactly by the change in ETH + WETH + USDC across its wallet and three contracts at each transaction's
block (archive `eth_getBalance` / `balanceOf`, 1,128 calls, none missing), which captures Uniswap V4 native-ETH
payouts that emit no `Transfer`:

| | |
|---|---|
| Sum over 47 blocks, gas included | **−$0.09** |
| Blocks with net > $0.27 | 2 (+$5.97; largest single win $5.55) |
| Blocks with net < −$0.27 | 7 (−$6.69: reverted attempts and "empty" landings that still paid the tip) |
| Everything else | 38 blocks netting between −$0.27 and +$0.27: contested wins grossing $7–13, tipping $6–13, keeping $0.20–0.42 |
| Fees paid in the window | 0.03803 ETH = $102.40 (mean $2.05 per attempt) |
| Wallet-level 24 h change of the same four addresses | +0.1085 ETH = +$292 (includes whatever else those contracts receive; a 5.94 ETH internal top-up in the window nets out) |

The contracts are called by that one wallet only (49 of 50 external calls in the window). This is the
priority-gas-auction equilibrium on Base: the sequencer orders by priority fee, the bots bid the gap away, and
the operator with half a million transactions keeps cents per contested win.

**The XDP/USDC pair, which produced 21 of the 24 episodes in §2.5, is a bot farm.** In the 3,000 blocks
(100 min) before 17:10 UTC the Uniswap V3 0.01 % pool had 11,541 swaps and the Slipstream pool 35,758; 5,873
transactions touched both pools in the same transaction, one per block. Four senders account for most of them.
All four, valued the same way (ETH + WETH + USDC + XDP at the pool price, at each transaction's block, gas
included, last 60 transactions of each):

| Bot | Transactions | Landed | Net | Fees | Per win |
|---|---|---|---|---|---|
| `0x7789515e…` → contract `0x952f339d…` | 809 in 100 min; sample 60 in 12 min (median tip 0.0043 gwei) | 60 / 60 | **+$0.13 → $0.66/hour** | $0.46 ($0.008 per tx) | median $0.0018, max $0.023 |
| `0x0190f008…` → contract `0xcd447b60…` | 411; sample 60 in 14 min (median tip 0.059 gwei) | 60 / 60 | **+$0.49 → $1.99/hour** | $3.85 ($0.064 per tx) | median $0.0069, max $0.046 |
| `0x000000c5…` → contract `0x0ce14aee…` | 163; sample 60 in 36 min (tip 0) | 60 / 60 | **+$0.89 → $1.49/hour** | $5.32 ($0.089 per tx) | median $0.0132, max $0.077 |
| `0x3be22b31…` → contract `0x08c61873…` | 146; sample 60 in 12 min (median tip 0.012 gwei) | 60 / 60 | **+$0.17 → $0.83/hour** | $0.80 ($0.013 per tx) | median $0.0038, max $0.015 |

These are the operators who capture the pair this repository's baseline kept detecting: 100–800 transactions
an hour each, every one landed, for $16–48 a day each and **about $5/hour for the whole pair**, which is the
§2.5 ceiling ($4.77/hour) measured from the other side. The pair's arbitrage income is real, it is fully
captured, and it is split four ways.

**Result of the anchored run (21 minutes, 3,189 pools, 3,608 cycles, block receipts from a public node):**

| Metric | §2.5 (657 pools, 22 min) | §2.6 (3,189 pools, 21 min) |
|---|---|---|
| Executable episodes (simulated net ≥ $0.01) | 24 → 65 per hour | 28 → 80 per hour |
| Sum of best simulated net | $1.75 → **$4.77/hour ceiling** | $0.69 → **$1.97/hour ceiling** ($0.73/hour in WETH/stables) |
| Largest single episode | $0.51 | $0.077 (XDP/USDC); best new pair PLAY/USDC $0.056, GITLAWB/USDC $0.034 |
| Median lifetime | 1 block | 1 block |
| Where | XDP/USDC 21 of 24 | XDP/USDC 26 of 28 |
| Simulated reverts | 69 | 57: 7× `TransferFailed` (taxed or restricted tokens), 4× `UniswapV2: K`, 4× `CannotRepay` short by 0.08–0.5 % |

Five times the pools did not raise the ceiling; the long tail added two cent-sized pairs and a great deal of
tokens that revert on transfer. Everything of value in a 3,189-pool universe still sits in the one pair the
four bots above already farm at one transaction per block. The ceiling is bounded by the market, not by the
breadth of the searcher.

## 3. Conclusions

1. **The architecture in the videos (listen for `Swap` events, then send a transaction) produces nothing.**
   At block boundaries, on every chain measured, the cross-DEX price gaps for liquid tokens are already inside
   the fee band.
2. **With exact block-level state on Base, small opportunities exist and are executable.** The best run:
   65 episodes per hour, $4.77/hour ceiling if every race were won, largest $0.51, median lifetime one block.
   Trade sizes were between $140 and $2,700; capital was never the constraint. What 200 ms state on a local
   node adds is unmeasured here. Breadth does not scale the value: every factory pool with anchored depth
   (3,189 pools, §2.6) gave 80 episodes per hour and a $1.97/hour ceiling, still 26 of 28 on the same pair.
3. **Flash loans are not the constraint.** Capital was never the binding factor in any measured episode; the
   largest optimal trade size was well under $1,000. Flash swaps (zero fee) cover every case; Morpho Blue is the
   only Base flash-loan pool with meaningful zero-fee depth (Balancer V2 on Base holds ~29 WETH after the
   November 2025 exploit).
4. **The leverage strategy (videos 1 and 2) is not income.** `LeverageManager` reproduces the example exactly
   (2,000 USDC own + 2,000 USDC borrowed → 1.483 WETH collateral, 2,000 USDC debt, health factor 1.66). The
   round trip costs about $5 in swap fees and the position is liquidated on roughly a 40 % drawdown of ETH.
   It is a way to take amplified directional risk in one transaction, nothing more.
5. **The "$4 million in seven days" figure** is the aggregate of the whole ecosystem's atomic arbitrage. Where
   it goes is now measured rather than assumed (§2.6): the bot that closed a real $13 gap one block after this
   searcher saw it kept $0.42 of it and paid $12.70 to the sequencer as priority fee; over its last 50
   transactions it netted −$0.09. The four bots that share the most active pair in this universe net $0.66,
   $1.99, $1.49 and $0.83 an hour, about $5/hour for the pair, which is the §2.5 ceiling seen from the other
   side. The income is real, fully captured, split among incumbents, and worth tens of dollars a day each.
6. **Every pool, every chain (§7).** On-chain censuses of every landed arbitrage settle the gaps this section left
   open.
   * Base atomic arbitrage grosses about $650/hour across all pools. 56 % of it is in Uniswap V4 pools.
   * 87 % is same-block backrunning, which no block-boundary searcher sees.
   * The block-boundary part is about $42/hour after fees for all bots combined.
   * All 234 operators together net about $250/hour, the top 10 take 87 % of that, and 26 make over $1/hour.
   * V4 launch pools, older V2 pairs and shallow pools are each small. The other L2s are near zero, and BSC is
     ordered by builders with exclusive searchers.

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
| DEX↔DEX atomic, 2-hop (videos 1-3) | Base, 12 venues incl. Uniswap V4, block and flashblock state, flash-swap funded, on-chain simulation; then every factory pool (46k found, 3,189 kept) | Verified episodes are worth cents; the incumbents that capture them net $0.7–2/hour each, measured from their own balances (§2.6) |
| DEX triangular (3 pools) | Included in every scan/dry run (`findTriangles`) | No 3-hop cycle cleared $0.01 net in any run; the two candidates that did were simulated and reverted |
| Slipstream dynamic-fee timing (own angle) | 209 pools, 1,041 blocks, 4,527 fee transitions | Best cycle through a pool after a fee drop averages $0.0001 vs $0.0005 baseline: nothing to time |
| CEX→DEX lead-lag, ETH (statistical) | OKX ETH-USDT every 250 ms vs 3 Base pools every block, 45 min | Base follows OKX with ~1 s lag (sign agreement 80-90 % at 1 s vs 60-70 % at 4 s); deviation of the pool price from its median ±5 bps at p5/p95, never >20 bps. Backtest of "trade the lag" on the pool with the 4-5 bps fee: 7 signals, 0-14 % win rate, mean −4 to −9 bps per trade; on the 1 bp pool 4 signals, +2 to +4 bps mean (n=4, noise) |
| CEX→DEX lead-lag, long tail | OKX vs deepest Base pool for VIRTUAL, DEGEN, ZORA, LINK, MORPHO, 30 min every block | Deviation from the median >30 bps in 0-4 % of blocks, never >60 bps |
| CEX↔CEX spatial (videos 4-5) | OKX, Gate, Kraken; 2,350 cross-listed pairs; executable bid/ask spread net of base-tier taker fees every 2 s for 15 min | Genuine pairs net-positive in <2 % of samples at 1-11 bps. Every persistent "spread" was a ticker collision (LIT, EDGE = different tokens), a withdrawal-disabled asset (CT) or a slow-transfer asset (STX on Stacks, DOG on Runes) |
| CEX triangular (video 4) | OKX and Gate, every A/USDT-B/USDT-A/B triangle with ≥$20k volume on all legs, net of 3 taker fees, 445 samples over 15 min | **0** triangles ever net-positive |
| Cross-chain DEX↔DEX | WETH/USDC Uniswap V3 0.05 % on Base, Arbitrum, Ethereum every 2 s, 450 samples | Spreads p5/p95 within ±5 bps, never >10 bps, before the 5 bps fee per leg and bridging |
| Spot-perp funding carry (video 5) | OKX and Hyperliquid, top-20 perps | 10.95 %/yr baseline (0.01 % per 8 h) on the majors; cross-venue differentials 5-24 %/yr on volatile alts; 0.30 % fees to open and close |
| Spot-futures basis (video 5) | OKX dated futures vs spot | 3.2-5.2 %/yr BTC, 3.2-4.5 %/yr ETH across all expiries, locked in at entry |
| Flash-loan liquidations (not in the videos; the other common flash-loan use) | Aave V3 and Morpho Blue on Base, all liquidation events in the last 43,200 blocks (~24 h) | Aave: 2 events, $4,850 of debt repaid, ≈ $242 gross at the 5 % bonus for the entire day, 2 liquidators. Morpho: 1 event. Bursty: large only on crash days, when documented incumbents take it |

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

## 7. The unmeasured gaps, measured (2026-10-01)

§2–§5 measured what a searcher sees at block boundaries in a chosen pool universe. This section measures the other
side: every atomic arbitrage that actually landed on chain, in every pool, using the raw material in
`research-material/` (index: `research-material/README.md`). Scripts and outputs are in `analysis/`.

### 7.1 Method

* **Classifier** (`analysis/arb_census.py`). A successful transaction with at least two swap logs is a cyclic arbitrage
  when the venues it touched, taken together, lose exactly one token and every other token nets to zero.
  * **Venue flows:**
    * ERC-20 `Transfer`s to and from the swap-log emitters.
    * WETH `Deposit`/`Withdrawal` on those pools.
    * Uniswap V4 `Swap` deltas. The pool side is the negated event amounts, and native ETH counts as WETH.
    * V4 hook fees minted as ERC-6909 claims to third parties.
    * PoolManager payouts to anyone other than the sender, its contract or a pool. These are hook and protocol fees,
      or a user's recipient.
  * **Exclusions:**
    * Transactions with liquidity events (V2/V3/Aerodrome mint, burn, collect, claim).
    * Rows where none of the profit token was paid into a venue. This means an invisible native-ETH leg, as in
      Curve stETH/ETH or a pool wrapping ETH itself.
  * **Valuation:** WETH, USDC, USDbC, DAI, USDT, cbBTC, cbETH, wstETH, weETH, EURC and ezETH are valued at anchored
    engine prices. Other tokens are valued only with a DefiLlama price at confidence ≥ 0.9, and only for the 12 other
    chains. A row is dropped when the venues gained another token worth more than 5 % of the profit, or a token with no
    reliable price. Such rows are user trades.
  * **Validation:** the largest rows were decoded by hand (`analysis/inspect_tx.py`). Every false positive found was
    traced to one of the cases above and fixed. The fixes were:
    * Aerodrome `Fees` transfers.
    * Liquidity removals.
    * Garbage long-tail prices.
    * User purchases.
    * A V4 hook fee.
    * A pool that wraps its own ETH.
    * A Kyber stETH swap.
* **Operator = beneficiary.** The operator is the address that received the profit, because bots rotate sender EOAs:
  one beneficiary took profit from 400+ one-shot senders. Each operator is charged every transaction its EOAs sent to
  its contracts in the window: wins, reverts and empty landings.
* **Backrun.** An arbitrage counts as a backrun when another sender's successful swap touched one of its pools earlier
  in the same block. A block-boundary searcher cannot see a backrun gap.
* **Base census:** blocks 51,995,609–52,017,160 (11.97 h, 30 Sep–1 Oct 2026), ETH $2,684.88.
* **Other chains:** one-hour censuses, and six hours for Ethereum.
* **Solana:** 600 consecutive slots (159 s) with the same venue-side test (`analysis/solana_report.py`). On Solana the
  signers' own balances must mirror the venue's loss, and the transaction must contain at least two real AMM legs.
* **Limits:**
  * 2,572 Base arbitrages whose profit is in a long-tail token have no reliable price and are not in the dollar
    figures.
  * On Ethereum, 4,226 transactions through 181 V4 pools whose keys could not be fetched without an API key were
    skipped. Ethereum builder payments are internal transfers, so Ethereum costs are understated. The same holds for
    BSC builder bribes.
  * On Solana, bots that keep profit in a program-owned account are not detected.

### 7.2 Base: where the arbitrage income is (11.97 h, 29,093 valued arbitrages, $647/hour gross)

| Pools touched | Arbs | Gross $/h | Priority fee / gross | Share of gross that is a same-block backrun |
|---|---|---|---|---|
| Engine universe, every pool ≥ 0.1 ETH | 17,563 | 204.45 | 39.5 % | 80.6 % |
| Uniswap V4 with hooks, pool ≥ 1 h old | 1,202 | 186.18 | 41.4 % | 91.8 % |
| Uniswap V4 without hooks | 3,861 | 160.63 | 13.7 % | 91.5 % |
| Pools the engine never enumerated (§7.3) | 5,737 | 78.49 | 21.0 % | 79.4 % |
| Uniswap V4 with hooks, pool < 1 h old (launches) | 314 | 16.42 | 47.4 % | 94.6 % |
| Engine universe, a pool < 0.1 ETH | 416 | 0.87 | 22.2 % | 69.7 % |
| **All** | **29,093** | **647.03** | **31.6 %** | **86.7 %** |

* **Backruns dominate.** 87 % of the income closes a gap opened earlier in the same block by someone else's swap.
  None of it is visible to a block-boundary engine like the one in §2.
* **The cross-block part is small.** The part that is visible at block boundaries totals $86/hour gross and
  $42/hour after the winners' own transaction fees (priority fee 47.5 % of gross), shared by 140 beneficiaries.
  * It swings between $18 and $234 an hour.
  * The engine's universe accounts for $12.35/hour of the net, within a factor of three of the §2.5/§2.6 ceiling
    ($1.97–4.77/hour).
* **The money is lumpy.** 12 arbitrages of ≥ $100 make 40 % of all gross.
* **Most dollars are not bid away.** 55 % of all gross was won while paying under 5 % of it as priority fee. The
  "winner keeps 3 %" outcome of §2.6 is real, but it is the contested regime:
  * The two contracts of the XDP-pair bot grossed $1,179 and $463 and spent $1,108 and $385, keeping 6 % and 17 %.
  * The large prizes are won by position, not by bid. The top 8 beneficiaries landed **the very next transaction after
    the swap that opened the gap** for 88 % of their gross, at 0.1–2.5 % priority. That requires seeing the triggering
    transaction before it is sequenced. Logs cannot show how they get it.

**Who earns it (234 beneficiaries, all their transactions charged):**
* All operators combined net **$251/hour**. A further $49/hour is spent by 2,592 zero-win senders calling shared
  contracts that could not be attributed.
* 150 operators (64 %) are net positive.
* The top 1, 3 and 10 take 28 %, 63 % and 87 % of the positive net.
* Only 26 net more than $1/hour, 11 more than $5/hour, and 7 more than $10/hour.
* The top two net about $100/hour each:
  * Their profit is mostly V4 backruns: 89 % of the first one's gross is hookless V4, and 63 % of the second's is
    hooked V4.
  * Each one's three largest trades make 47 % and 64 % of its gross.

### 7.3 The eight lines, one by one

**1. Uniswap V4 on Base ("the biggest gap").**
* **Measured: yes, the biggest pool category.**
  * V4 pools carry $363/hour gross, 56 % of all Base arbitrage income.
  * 92 % of it is same-block backruns of user swaps.
  * The non-backrun V4 part is $29.9/hour gross, $18.4/hour after fees.
* **Why the engine missed it.** The engine's all-V4 live test (`research-material/02-v4-live-test`, 20 min) had a
  $0.62/hour ceiling and no V4 episode, and it could not have found one. 98.4 % of V4 pools have hooks or dynamic fees
  that the engine cannot price locally, and the income is intra-block anyway.

**2. Older V2 pairs ("almost all abandoned").**
* **Mostly true.**
  * Of a random sample, 0.17 % hold ≥ 0.1 ETH and 0.065 % traded in 24 h.
  * On chain, older pairs of the V2 factories the engine supports carried $18.65/hour gross. One $169 trade is 76 %
    of that, and 98 % of it was backruns.
* **Not on the list, but larger:**
  * Uniswap V3 / Aerodrome CL / PancakeSwap V3 pools whose pair the engine never enumerated: $33.6/hour gross. V3
    pools cannot be listed through a V2 factory.
  * DEXes the engine does not support: $26.3/hour gross.

**3. Pools under 0.1 ETH.**
* **True.**
  * Arbitrage through engine-universe pools with a pool under 0.1 ETH: $0.87/hour gross.
  * The shallow live test had a $1.12/hour ceiling, $0.28/hour of it in tokens with a reliable price.
* **Blocking and taxing tokens.** 93 % of the tokens that block or tax transfers sit in pools under 0.1 ETH. The
  per-token rate is 20.2 % in the 0.001–0.1 ETH band, against 7.2 % in deep pools.

**4. Other chains, live.** Same classifier and costs, one census window per chain.

| Chain | Window | Valued arbs | Gross $/h | All operators' net $/h | Beneficiaries | Top-3 share of gross | Backrun share | V4 share |
|---|---|---|---|---|---|---|---|---|
| Ethereum | 6 h | 1,086 | 1,469 | 286 (builder payments not seen) | 164 | 58 % | 45 % | 61 % |
| Polygon | 1 h | 915 | 368 | −40 | 46 | 49 % | 61 % | 6 % |
| BSC | 1 h | 1,185 | 148 | 128 (bribes not seen) | 59 | 68 % | 70 % | 18 % |
| Mantle | 1 h | 10 | 5.34 | 2.63 | 3 | 100 % | 3 % | 0 |
| Arbitrum | 1 h | 79 | 3.90 | −2.51 | 10 | 91 % | 42 % | 53 % |
| Abstract | 1 h | 16 | 3.72 | 2.75 | 5 | 95 % | 4 % | 0 |
| Optimism | 1 h | 400 | 2.17 | −3.09 | 41 | 74 % | 41 % | 24 % |
| Ink | 1 h | 42 | 1.78 | 1.24 | 11 | 98 % | 17 % | 100 % |
| zkSync | 1 h | 10 | 0.79 | 0.09 | 2 | 100 % | 0 | 0 |
| World Chain | 1 h | 21 | 0.38 | 0.30 | 7 | 99 % | 51 % | 75 % |
| Soneium | 1 h | 92 | 0.38 | −0.22 | 11 | 97 % | 15 % | 0 |
| Unichain | 1 h | 100 | 0.23 | 0.11 | 9 | 64 % | 61 % | 82 % |

* **Solana** (159 s, 600 slots):
  * 1,768 valued arbitrages: $259 gross, i.e. $5,842/hour.
  * Fees and Jito tips take 31 % of gross, and 43 % of arbitrages under $0.10.
  * After fees, tips and the signers' failed transactions, all 197 signers net $3,053/hour; 164 are net positive.
  * The tips in the window, $889/hour, are about 10 % of Jito's 1,880 SOL/day total.
  * The window is 2.6 minutes, so the hourly figure is an order of magnitude, not an estimate.
* **Reading.** No L2 other than Base has an atomic-arbitrage market worth a dollar figure for a newcomer. Polygon is
  large but net negative across its operators (spam). Ethereum, BSC and Solana are large but ordered by builders or
  validators through bundles.

**5. V4 launches ("the one place a bigger number could appear").**
* **Not a bigger number.** Pools under one hour old carried $16.42/hour gross; two trades make 69 % of it.
* **The flow is contested.** 95 % is backruns, priority fees took 47 % of gross, and 106 of the 314 arbitrages paid
  more than half their gross as priority fee.
* **Where the large V4 money is.** It is in older hooked and hookless pools, won by being first behind a user's swap.

**6. BSC ordering through private builders.**
* **Confirmed** (`analysis/bsc_builders.py`, 8,000 blocks):
  * BlockRazor builds 43 % of blocks and the 48 Club builders 52 %.
  * 57 % of arbitrage gross is in zero-gas-price transactions, which only a builder can include.
  * 50 % of arbitrage gross is at block positions 0–2.
* **Exclusive flow.** Several searchers land only through one builder:
  * The #1 beneficiary holds 39 % of all arbitrage gross and lands 95 % of it in 48 Club blocks; 48 Club builds 52 %
    of blocks.
  * The #2 beneficiary lands 100 % of its gross in BlockRazor blocks.
  * The #3 lands 96 % in BlockRoute blocks, though BlockRoute builds 0.5 % of blocks.
  * Even the arbitrages at position ≥ 10 are 75 % zero-gas bundles, and the top three beneficiaries take 81 % of them.

**7. Chain-wide studies** (checked against the texts in `research-material/08-sources`).

| Claim | What the source says | Our census |
|---|---|---|
| Arbitrum ≈ $4,700/day | arXiv 2509.22143 Table 1: $433,121 regular + $69,806 Timeboosted profit, 17 Apr–31 Jul 2025 = **$4,790/day** | 30 Sep 2026, one hour: $3.90/hour gross ($94/day pace), 10 beneficiaries |
| Base: 4,365 bots, 21.4 M arbitrages, nine months | arXiv 2606.00720 §4.1, verbatim: 21,374,434 cyclic arbitrages by 4,365 bot addresses, 1 Jun 2025–28 Feb 2026 (≈ 3,250/hour) | 2,430 valued arbitrages/hour (+ 215/hour unvalued long-tail) |
| Only 28 % of those bots profitable after failed transactions | Not in 2606.00720. arXiv 2607.24172 Table 6 (Base, Sep 2023–Jul 2025): arbitrage bots profitable after state-invariant transaction costs: **23.4 %** speculative, **25.1 %** non-speculative; all MEV bots ≈ 26 % | 14.5 % of sending EOAs net positive (1,272 of 8,753, counting zero-win senders to arbitrage contracts); 64 % of beneficiaries that won at least once |

The line merges two papers. The 4,365 bots are not the population behind the 23–27 %.

**8. "Full V4 coverage is the one gap I wouldn't predict."**
* **Measured** via the census rather than a rerun, because the live test cannot see intra-block income (§7.2).
* **Answer.** V4 is where most of Base's arbitrage income is, but almost all of it is backrunning.

### 7.4 What this changes for the $/hour answer

The new evidence moves the totals, not the share a newcomer can take:

* **Block-boundary bot, any coverage** (the §2 engine; Alchemy + a VPS is enough). Cross-block income on Base for all
  bots together is about $42/hour after their fees: $86/hour gross, half of it bid away as priority fee. It is shared
  by 140 beneficiaries, and the top three take 45 %. Full V4, V3 and extra-DEX coverage would raise the engine's
  addressable ceiling from about $12/hour to that $42/hour. At the capture rates in §2.6, that is a few percent for a
  newcomer: roughly **$1–3/hour**, versus $0.50–1.50/hour before.
* **Same-block backrunning** is 87 % of the income: $561/hour gross. Its top earners make about $100/hour each by
  landing directly behind the swap that opened the gap, at near-zero priority fee. That needs pre-sequencing
  visibility of Base transactions and a submission path that lands in the next slot. Polling an RPC provider does not
  give either. Even inside this market, only 26 of 234 operators clear $1/hour.
* **Other chains** do not offer an easier version. The L2s other than Base are near zero. BSC, Ethereum and Solana
  route the income through builders, validators and bundles, where the incumbents have exclusive paths.

To reproduce, with the material in `research-material/` (the large originals are local-only; see its README):

```bash
cd analysis
python3 arb_census.py --census ../research-material/05-base-onchain --chain base --out base \
  --weth 0x4200000000000000000000000000000000000006 --pool-manager 0x498581ff718922c3f8e6a244956af099b2652b2b \
  --prices ../research-material/02-v4-live-test/v4universe-prices.csv.gz --prices ../research-material/04-shallow-pools/prices.csv.gz \
  --v4-init "../research-material/01-v4-pools/initialize-part-*.csv.gz" \
  --v4-init ../research-material/01-v4-pools/v4-window2-initialize-part-0001.csv.gz \
  --v4-init ../research-material/02-v4-live-test/initialize-topup.csv.gz --native-usd 2684.88
python3 base_report.py && python3 outside_breakdown.py
python3 v4keys_fetch.py && bash run_other_chains.sh && python3 chain_report.py && python3 bsc_builders.py
python3 solana_report.py
```

### 7.5 Step 1 done: pool coverage extended (2026-10-01)

**What changed in the engine** (`bot/`):

* **Pools are discovered from their own Swap logs** (`src/pools/activity.ts`, `--active-lookback`, `src/cli/registry.ts`),
  not only from factory enumeration.
  * The scan covers UniV2, Aerodrome V2, V3/Slipstream, PancakeSwap V3 and Uniswap V4 swaps.
  * Each emitter is classified by `factory()`. An unknown factory is accepted only for V3/PancakeSwap-style pools whose
    bytecode calls the callback the executor implements, and only after the factory passes an on-chain check: its
    busiest pools are quoted locally and executed on chain at the same block, and every quote must match to the wei.
    16 of 17 clone factories passed. One "UniswapV3Factory" clone charges 0.35 % where its pools report 0.30 %; it was
    excluded after its routes failed 73 dry-run simulations.
  * V4 pool ids are resolved through `PositionManager.poolKeys`, or from `Initialize` logs for pools the
    PositionManager never saw. They are kept when the key is locally priceable.
  * Everything goes into `data/pool-registry-<chain>.json`, so restarts only scan new blocks.
* **Scan cost on the public `mainnet.base.org` endpoint:**
  * 12 hours of Base: 1.08 M swap logs in 140 calls (40 s).
  * 3 days: 7.49 M swap logs in 992 calls (4 min), giving 20,560 accepted pools.
* **Live discovery.** Every `--registry-refresh-s` seconds (default 300) the engine scans the new blocks, and the new
  pools that pass the empty and depth filters join the running search. Observed: 4–6 pools per 2-minute refresh.
* **Startup.** The engine prices and depth-filters on slot0/liquidity/reserves first and fetches tick data only for
  the survivors. An activity-only universe starts in about 1 minute instead of about 9, and has 5.4 k pools after the
  0.1 ETH depth filter, against 3.2 k in §2.6.
* **Triangles in the event-driven search.** `CycleIndex` now also enumerates three-pool cycles through every touched
  pool, starting in WETH or USDC where possible, and accepts pools added at run time. Three-leg cycles are 58 % of the
  census's block-boundary income; before this change the `--source logs` path searched only two-pool cycles.

**Local math is exact on every pool type.** `src/research/quotecheck.ts` synced 15 pools of each type at one block and
compared `quote()` with on-chain execution at 0.01 %, 0.1 % and 1 % of in-range depth, both directions. The on-chain
side was `contracts/src/test-helpers/PoolQuoter.sol`, injected by state override, for V3-style pools, and the official
V4Quoter for V4. All 728 quotes matched to the wei:

| Pool type | Uniswap V3 | PancakeSwap V3 | Slipstream (3 factories) | Sushi V3 | V3 clones | PancakeSwap V3 clones | Uniswap V4 |
|---|---|---|---|---|---|---|---|
| Quotes / exact | 77 / 77 | 89 / 89 | 254 / 254 | 84 / 84 | 87 / 87 | 61 / 61 | 76 / 76 |

The sample above did not include the failing clone factory; the engine now runs the same check itself on every
clone factory before using its pools.

**Coverage of the census income** (`analysis/coverage.py`). An arbitrage counts as covered when every pool it used is in
the universe and it has at most three legs. All figures are out of sample: the registry was built from blocks that do
not include the arbitrage.

"Before" is factory enumeration plus every priceable V4 pool, at depth ≥ 0.1 ETH, scored on the same arbitrages.

| New universe (scored on) | All income: before → after | Block-boundary income: before → after |
|---|---|---|
| Registry of the 12 h after the census, depth ≥ 0.1 ETH (the 20,594 census arbitrages it did not scan) | 36.4 % → 41.3 % | 50.1 % → 59.2 % |
| Same, plus factory enumeration | 36.4 % → 41.3 % | 50.1 % → 59.3 % |
| Registry of the 3 days before the census (all 29,093 census arbitrages) | 36.6 % → **59.2 %** | 48.3 % → **61.7 %** |

* Factory enumeration on top of the registry adds nothing measurable (59.2 % with or without it), and the depth
  threshold between 0.01 and 0.1 ETH changes block-boundary coverage by under 0.5 points.
* **What is still not covered** of block-boundary income (3-day registry):

  | Gap | Share | Why |
  |---|---|---|
  | V4 pools | 18.9 % | 96 % of the uncovered V4 pools have swap hooks (launch platforms) and cannot be priced with local math. |
  | Other V2/V3 pools | 12.1 % | Algebra Integral, Balancer V3, WOOFi, Maverick, Solidly V3, V2 forks with unknown fees, and pools that did not trade in the scanned days. |
  | Routes with four or more legs | 7.3 % | |

**Dry runs with the extended universe** (`--universe config --active-lookback 21600 --min-depth-eth 0.1
--min-profit-usd 0.01`, event mode, public RPCs, nothing sent; summaries in `analysis/base/dryrun-*.json` by
`analysis/dryrun_summary.py`). Each candidate is now also simulated on exactly the block its state came from, which
separates a wrong state from a gap that closed. Four problems surfaced and were fixed between runs:

| Run | Simulations | OK at the state's block | Main failure | Fix |
|---|---|---|---|---|
| 1 (18 min) | 202 | 19 | `TransferFailed` (116): blocked or taxed tokens reached through ever-new triangles | Per-token strikes. Blame is split between a route's unproven tokens, and config tokens or tokens with a successful simulation are never blamed. Verdicts persist in `data/bad-tokens-<chain>.json`. |
| 2 (13 min) | 176 | 10 | `CannotRepay` (130), 73 of them through one clone factory | On-chain check of every clone factory (above). Also: with `--universe config` the token list aliased `cfg.tokens`, so every discovered token counted as a protected config token and was never parked. |
| 3 (10 min) | 66 | 17 | `CannotRepay` (43), 42 of them through a Slipstream pool (−0.64 %) | Slipstream fees come from a dynamic module and are not in the Swap event. Event mode now reads `fee()` at the exact block for every touched Slipstream pool, and re-prices candidates through any other Slipstream pool before simulating. |
| 4 (12 min) | 12 | **9** (+1 `CannotRepay`, 1 `TransferFailed`) | | |

In run 4, the simulated opportunities were worth $0.60 gross ($4.4/hour; $4.1/hour after gas) **if every one were won**.
Runs 3 and 4 together come to $4–6/hour gross. In run 3, 67 % of that value went through pools outside the old
universe and 44 % through three-leg routes; run 4 had 11 % and 21 %. These are 10–13-minute windows. They show that
the extended search finds real opportunities and wastes almost no simulations. They do not measure capture: §2.6 and
§7.2 show that contested block-boundary gaps are mostly bid away.
