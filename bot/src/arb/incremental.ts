/**
 * Pool → cycle index for event-driven search. A block that touches k pools only re-evaluates the cycles those k
 * pools participate in, instead of every pair on every token.
 */
import type { Address } from "viem";
import { isV2, pairKey, type Pool } from "../pools/types.js";
import { evalCycle, estimateGas, optimizeAmount, sizeBounds, type Opportunity } from "./search.js";
import { poolFee, spotPrice } from "./quote.js";
import { optimalV2Cycle } from "../math/v2.js";

interface Candidate { a: Pool; b: Pool } // sell into a, then b (ordered)

export class CycleIndex {
  private readonly byPool = new Map<string, Candidate[]>();
  readonly candidates: Candidate[] = [];

  constructor(pools: Pool[]) {
    const groups = new Map<string, Pool[]>();
    for (const p of pools) groups.set(pairKey(p.token0, p.token1), [...(groups.get(pairKey(p.token0, p.token1)) ?? []), p]);
    for (const g of groups.values()) {
      if (g.length < 2) continue;
      for (const a of g) for (const b of g) {
        if (a === b) continue;
        const c = { a, b };
        this.candidates.push(c);
        for (const p of [a, b]) {
          const k = p.address.toLowerCase();
          this.byPool.set(k, [...(this.byPool.get(k) ?? []), c]);
        }
      }
    }
  }

  cyclesTouching(touched: Iterable<string>): Candidate[] {
    const seen = new Set<Candidate>();
    for (const t of touched) for (const c of this.byPool.get(t.toLowerCase()) ?? []) seen.add(c);
    return [...seen];
  }

  /** Evaluate only the candidates touching the given pools. Same math and same pre-filter as findOpportunities. */
  search(touched: Iterable<string>, budgetMs = 100): Opportunity[] {
    const out: Opportunity[] = [];
    const deadline = Date.now() + budgetMs;
    for (const { a, b } of this.cyclesTouching(touched)) {
      if (Date.now() > deadline) break;
      const pa = spotPrice(a), pb = spotPrice(b);
      if (!(pa > 0 && pb > 0)) continue;
      const gap = pb / pa - 1;
      if (gap * 1e4 <= (poolFee(a) + poolFee(b)) * 1e4) continue;
      // token0 cheaper on a: start in token1 (sell token1 on a, sell token0 on b) and the mirror in token0
      const orient: Array<[Address, Address, Pool, Pool]> = [
        [a.token1, a.token0, a, b],
        [a.token0, a.token1, b, a],
      ];
      for (const [token, other, X, Y] of orient) {
        const bnd = sizeBounds(X, token, gap);
        let seed: bigint | undefined;
        if (isV2(X) && isV2(Y) && !(X.kind === "aero-v2" && X.stable) && !(Y.kind === "aero-v2" && Y.stable)) {
          const xIn = token.toLowerCase() === X.token0.toLowerCase();
          seed = optimalV2Cycle(xIn ? X.reserve0 : X.reserve1, xIn ? X.reserve1 : X.reserve0, X.feeBps, xIn ? Y.reserve1 : Y.reserve0, xIn ? Y.reserve0 : Y.reserve1, Y.feeBps);
        }
        const best = optimizeAmount(token, other, X, Y, bnd.lo, bnd.hi, seed);
        if (best.profit <= 0n) continue;
        const cyc = evalCycle(token, other, X, Y, best.amountIn);
        if (!cyc.valid) continue;
        out.push({ token, hops: cyc.hops, amountIn: best.amountIn, amountOut: cyc.amountOut, profit: cyc.amountOut - best.amountIn, gasEstimate: estimateGas(cyc.hops), gapBps: gap * 1e4 });
      }
    }
    return out.sort((x, y) => (y.profit > x.profit ? 1 : y.profit < x.profit ? -1 : 0));
  }
}
