import type { Address } from "viem";
import { isV2, pairKey, type Pool } from "../pools/types.js";
import { optimalV2Cycle } from "../math/v2.js";
import { poolFee, quote, spotPrice } from "./quote.js";
import { Q96 } from "../math/v3.js";

export interface CycleHop {
  pool: Pool;
  tokenIn: Address;
  tokenOut: Address;
  amountIn: bigint;
  amountOut: bigint;
  ticksCrossed: number;
}

export interface Opportunity {
  /** token we borrow/flash-swap and end up holding more of */
  token: Address;
  hops: CycleHop[];
  amountIn: bigint;
  amountOut: bigint;
  profit: bigint; // in `token` units
  /** Estimated execution gas (units) */
  gasEstimate: bigint;
  /** spot-price gap between the two pools, in bps, before fees */
  gapBps: number;
}

export interface SearchOptions {
  /** Minimum spot gap (in bps) over combined fees to bother optimizing. */
  minEdgeBps?: number;
  /** Amount bounds per token address (in wei). Defaults: derived from pool reserves. */
  minAmount?: (token: Address) => bigint;
  maxAmount?: (token: Address) => bigint;
  /** Only search cycles whose start token passes this predicate (e.g. WETH/USDC only). */
  startTokenFilter?: (token: Address) => boolean;
  /** Wall-clock budget in ms; the search returns what it has when exceeded. */
  budgetMs?: number;
}

/** Calibrated on Base fork tests: V3→V2 118k, V2→V3 121k, V3→V3 ~205k + ~15-20k per initialized tick crossed. */
export const GAS = {
  base: 30_000n, // tx intrinsic + contract entry + profit check
  v2Hop: 42_000n,
  v3Hop: 88_000n,
  tickCross: 16_000n,
  flashLoanOverhead: 60_000n, // Morpho path measured at +~60k vs. a flash swap
};

export function estimateGas(hops: CycleHop[]): bigint {
  let g = GAS.base;
  for (const h of hops) {
    g += isV2(h.pool) ? GAS.v2Hop : GAS.v3Hop + BigInt(h.ticksCrossed) * GAS.tickCross;
  }
  return g;
}

/** Full cycle evaluation: sell `amountIn` of token on `buyPool`, sell proceeds on `sellPool`. */
export function evalCycle(token: Address, other: Address, buyPool: Pool, sellPool: Pool, amountIn: bigint): { hops: CycleHop[]; amountOut: bigint; valid: boolean } {
  const q1 = quote(buyPool, token, amountIn);
  if (q1.truncated || q1.amountOut === 0n) return { hops: [], amountOut: 0n, valid: false };
  const q2 = quote(sellPool, other, q1.amountOut);
  if (q2.truncated || q2.amountOut === 0n) return { hops: [], amountOut: 0n, valid: false };
  return {
    valid: true,
    amountOut: q2.amountOut,
    hops: [
      { pool: buyPool, tokenIn: token, tokenOut: other, amountIn, amountOut: q1.amountOut, ticksCrossed: q1.ticksCrossed },
      { pool: sellPool, tokenIn: other, tokenOut: token, amountIn: q1.amountOut, amountOut: q2.amountOut, ticksCrossed: q2.ticksCrossed },
    ],
  };
}

/**
 * Maximize profit(x) = cycle(x) - x over x in [lo, hi]. Profit is unimodal for constant-product and
 * concentrated-liquidity AMMs, so a geometric grid scan followed by golden-section refinement converges
 * to the optimum within ~40 evaluations.
 */
export function optimizeAmount(token: Address, other: Address, buyPool: Pool, sellPool: Pool, lo: bigint, hi: bigint, seed?: bigint): { amountIn: bigint; profit: bigint } {
  const profitAt = (x: bigint): bigint => {
    if (x <= 0n) return -1n;
    const r = evalCycle(token, other, buyPool, sellPool, x);
    return r.valid ? r.amountOut - x : -x; // penalize infeasible sizes
  };
  let best = { amountIn: 0n, profit: 0n };
  const consider = (x: bigint) => {
    const p = profitAt(x);
    if (p > best.profit) best = { amountIn: x, profit: p };
  };
  // Geometric grid, ratio 2.
  const grid: bigint[] = [];
  for (let x = lo; x <= hi; x *= 2n) grid.push(x);
  if (grid.length === 0) grid.push(lo);
  if (seed && seed > lo && seed < hi) grid.push(seed);
  grid.sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  let bestIdx = -1;
  let bestGridProfit = 0n;
  let lastP = -1n;
  let declines = 0;
  for (let i = 0; i < grid.length; i++) {
    const x = grid[i]!;
    const p = profitAt(x);
    if (p > bestGridProfit) {
      bestGridProfit = p;
      bestIdx = i;
    }
    // profit(x) is unimodal: once it has peaked and fallen twice, or the size became infeasible, stop.
    if (p <= lastP && bestIdx >= 0) declines++;
    else declines = 0;
    if (declines >= 2 || p === -x) break;
    lastP = p;
  }
  if (bestIdx < 0) return best;
  best = { amountIn: grid[bestIdx]!, profit: bestGridProfit };
  // Golden-section refinement between neighbours.
  let a = bestIdx > 0 ? grid[bestIdx - 1]! : grid[bestIdx]! / 2n;
  let b = bestIdx < grid.length - 1 ? grid[bestIdx + 1]! : grid[bestIdx]! * 2n;
  const PHI_NUM = 618n;
  const PHI_DEN = 1000n;
  let c = b - ((b - a) * PHI_NUM) / PHI_DEN;
  let d = a + ((b - a) * PHI_NUM) / PHI_DEN;
  let fc = profitAt(c);
  let fd = profitAt(d);
  for (let i = 0; i < 24 && b - a > (b + a) / 2000n; i++) {
    if (fc > fd) {
      b = d;
      d = c;
      fd = fc;
      c = b - ((b - a) * PHI_NUM) / PHI_DEN;
      fc = profitAt(c);
    } else {
      a = c;
      c = d;
      fc = fd;
      d = a + ((b - a) * PHI_NUM) / PHI_DEN;
      fd = profitAt(d);
    }
  }
  consider(c);
  consider(d);
  consider((a + b) / 2n);
  return best;
}

function groupByPair(pools: Pool[]): Map<string, Pool[]> {
  const m = new Map<string, Pool[]>();
  for (const p of pools) {
    const k = pairKey(p.token0, p.token1);
    const arr = m.get(k);
    if (arr) arr.push(p);
    else m.set(k, [p]);
  }
  return m;
}

/**
 * Size bounds for selling `token` into `pool`. The optimal arb size can never exceed the amount that moves
 * this pool's price all the way to the other pool's price (`gap`, as a fraction), so we cap there (x4 for
 * liquidity that may appear across ticks). For V2 that follows from x*y=k; for V3 we use the current-range
 * liquidity: Δx = L·(1/√P' − 1/√P) for token0 in, Δy = L·(√P' − √P) for token1 in.
 */
export function sizeBounds(pool: Pool, token: Address, gap: number): { lo: bigint; hi: bigint } {
  const isT0 = token.toLowerCase() === pool.token0.toLowerCase();
  const dec = isT0 ? pool.dec0 : pool.dec1;
  const unit = 10n ** BigInt(dec);
  const lo = unit / 100_000n > 0n ? unit / 100_000n : 1n; // 1e-5 units
  const g = Math.min(Math.max(gap, 0.0001), 0.5);
  let hi: bigint;
  if (isV2(pool)) {
    const rIn = isT0 ? pool.reserve0 : pool.reserve1;
    // moving price by factor (1+g) needs Δx = rIn·(sqrt(1+g) − 1)
    hi = (rIn * BigInt(Math.floor((Math.sqrt(1 + g) - 1) * 4e6))) / 1_000_000n;
    if (hi > rIn / 2n) hi = rIn / 2n;
  } else {
    const L = pool.state.liquidity;
    const sqrtP = pool.state.sqrtPriceX96;
    if (L === 0n || sqrtP === 0n) return { lo, hi: lo * 2n };
    // price of token0 falls by (1+g) when selling token0: √P' = √P / sqrt(1+g); rises when selling token1.
    const f = BigInt(Math.floor(Math.sqrt(1 + g) * 1e9));
    if (isT0) {
      // Δx = L·(1/√P' − 1/√P) = L·(sqrt(1+g) − 1)/√P  (in Q96 terms: L·(f−1e9)·2^96 / (1e9·√P))
      hi = (L * (f - 1_000_000_000n) * Q96) / (1_000_000_000n * sqrtP);
    } else {
      // Δy = L·(√P' − √P) = L·√P·(sqrt(1+g) − 1)
      hi = (L * sqrtP * (f - 1_000_000_000n)) / (1_000_000_000n * Q96);
    }
    hi = hi * 4n;
  }
  return { lo, hi: hi > lo * 2n ? hi : lo * 2n };
}

/** @deprecated kept for callers that have no gap estimate */
function defaultBounds(pool: Pool, token: Address): { lo: bigint; hi: bigint } {
  return sizeBounds(pool, token, 0.05);
}

/**
 * Enumerate all 2-pool cycles for every token pair and return the profitable ones (before gas).
 * Pre-filter on spot-price gap vs. combined fees so the expensive optimizer only runs where a
 * profit is mathematically possible.
 */
export function findOpportunities(pools: Pool[], opts: SearchOptions = {}): Opportunity[] {
  const minEdgeBps = opts.minEdgeBps ?? 0;
  const out: Opportunity[] = [];
  const deadline = Date.now() + (opts.budgetMs ?? 5_000);
  const dbg = process.env.LOG_LEVEL === "debug";
  let groupIdx = 0;
  for (const [, group] of groupByPair(pools)) {
    if (group.length < 2) continue;
    if (Date.now() > deadline) break;
    if (dbg && ++groupIdx % 10 === 0) console.log(`search: group ${groupIdx} pools=${group.length} found=${out.length} t=${Date.now() - (deadline - (opts.budgetMs ?? 5_000))}ms`);
    const priced = group
      .map((p) => ({ p, px: spotPrice(p), fee: poolFee(p) }))
      .filter((x) => Number.isFinite(x.px) && x.px > 0);
    for (let i = 0; i < priced.length; i++) {
      for (let j = 0; j < priced.length; j++) {
        if (i === j) continue;
        const A = priced[i]!;
        const B = priced[j]!;
        // px = token1 per token0 (the price of token0 quoted in token1). px_A < px_B means token0 is cheaper
        // on A: buy token0 on A by selling token1, then sell token0 on B for token1. Cycle starts/ends in token1.
        const gap = B.px / A.px - 1; // >0 means token0 is more expensive on B
        const gapBps = gap * 10_000;
        const feeBps = (A.fee + B.fee) * 10_000;
        if (gapBps <= feeBps + minEdgeBps) continue;
        const token = A.p.token1;
        const other = A.p.token0;
        if (opts.startTokenFilter && !opts.startTokenFilter(token)) continue;
        const bA = sizeBounds(A.p, token, gap);
        const lo = opts.minAmount ? opts.minAmount(token) : bA.lo;
        const hi = opts.maxAmount ? opts.maxAmount(token) : bA.hi;
        let seed: bigint | undefined;
        if (isV2(A.p) && isV2(B.p) && !(A.p.kind === "aero-v2" && A.p.stable) && !(B.p.kind === "aero-v2" && B.p.stable)) {
          // selling token1 into A (reserves a1=reserve1 of token1, b1=reserve0 of token0), then token0 into B
          seed = optimalV2Cycle(A.p.reserve1, A.p.reserve0, A.p.feeBps, B.p.reserve0, B.p.reserve1, B.p.feeBps);
        }
        if (dbg) console.log(`  pair ${A.p.dex}:${A.p.address.slice(0, 8)} -> ${B.p.dex}:${B.p.address.slice(0, 8)} gap=${gapBps.toFixed(0)} lo=${lo} hi=${hi}`);
        const best = optimizeAmount(token, other, A.p, B.p, lo, hi, seed);
        if (best.profit > 0n) {
          const cyc = evalCycle(token, other, A.p, B.p, best.amountIn);
          if (cyc.valid) {
            out.push({ token, hops: cyc.hops, amountIn: best.amountIn, amountOut: cyc.amountOut, profit: cyc.amountOut - best.amountIn, gasEstimate: estimateGas(cyc.hops), gapBps });
          }
        }
        // Same discrepancy, opposite orientation: start in token0, sell it on B (expensive), buy it back on A (cheap).
        // Profit is then denominated in token0 (usually WETH), which is what gas is paid in.
        if (opts.startTokenFilter && !opts.startTokenFilter(other)) continue;
        const bB0 = sizeBounds(B.p, other, gap);
        const lo2 = opts.minAmount ? opts.minAmount(other) : bB0.lo;
        const hi2 = opts.maxAmount ? opts.maxAmount(other) : bB0.hi;
        let seed2: bigint | undefined;
        if (isV2(A.p) && isV2(B.p) && !(A.p.kind === "aero-v2" && A.p.stable) && !(B.p.kind === "aero-v2" && B.p.stable)) {
          seed2 = optimalV2Cycle(B.p.reserve0, B.p.reserve1, B.p.feeBps, A.p.reserve1, A.p.reserve0, A.p.feeBps);
        }
        const best2 = optimizeAmount(other, token, B.p, A.p, lo2, hi2, seed2);
        if (best2.profit > 0n) {
          const cyc2 = evalCycle(other, token, B.p, A.p, best2.amountIn);
          if (cyc2.valid) {
            out.push({ token: other, hops: cyc2.hops, amountIn: best2.amountIn, amountOut: cyc2.amountOut, profit: cyc2.amountOut - best2.amountIn, gasEstimate: estimateGas(cyc2.hops), gapBps });
          }
        }
      }
    }
  }
  return out.sort((a, b) => (b.profit > a.profit ? 1 : b.profit < a.profit ? -1 : 0));
}
