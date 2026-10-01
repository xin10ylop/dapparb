/**
 * Pool → cycle index for event-driven search. A block that touches k pools only re-evaluates the cycles those k
 * pools participate in, instead of every pair on every token: two-pool cycles on the same pair, and three-pool
 * triangles (A→B→C→A) that use a touched pool as one leg. Pools can be added while running (live discovery).
 */
import type { Address } from "viem";
import { isV2, pairKey, type Pool } from "../pools/types.js";
import { evalCycle, estimateGas, optimizeAmount, sizeBounds, type Opportunity } from "./search.js";
import { poolFee, spotPrice } from "./quote.js";
import { optimalV2Cycle } from "../math/v2.js";
import { evalRoute, optimizeRoute } from "./triangles.js";

interface Candidate { a: Pool; b: Pool } // sell into a, then b (ordered)

/** ln(out per in after fee) at infinitesimal size, human units; NaN when the pool has no price. */
function logRate(p: Pool, from: string): number {
  const px = spotPrice(p);
  if (!Number.isFinite(px) || px <= 0) return NaN;
  const fee = poolFee(p);
  return from === p.token0.toLowerCase() ? Math.log(px * (1 - fee)) : Math.log((1 / px) * (1 - fee));
}

export class CycleIndex {
  private readonly byPool = new Map<string, Candidate[]>();
  readonly candidates: Candidate[] = [];
  private readonly byPair = new Map<string, Pool[]>();
  private readonly byAddr = new Map<string, Pool>();
  private readonly nbr = new Map<string, Set<string>>();
  /** Start tokens preferred for triangle profit (lowercase), e.g. WETH and USDC; otherwise the cycle starts at the touched pool. */
  private readonly startPref: string[];

  constructor(pools: Pool[], startPref: string[] = []) {
    this.startPref = startPref.map((t) => t.toLowerCase());
    for (const p of pools) this.add(p);
  }

  get pools(): number {
    return this.byAddr.size;
  }

  /** Index a pool: two-pool candidates against every pool on the same pair, and the token-neighbour graph for triangles. */
  add(p: Pool): void {
    const addr = p.address.toLowerCase();
    if (this.byAddr.has(addr)) return;
    this.byAddr.set(addr, p);
    const k = pairKey(p.token0, p.token1);
    const g = this.byPair.get(k) ?? [];
    for (const q of g) {
      for (const c of [{ a: p, b: q }, { a: q, b: p }]) {
        this.candidates.push(c);
        for (const x of [c.a, c.b]) {
          const xk = x.address.toLowerCase();
          const arr = this.byPool.get(xk);
          if (arr) arr.push(c);
          else this.byPool.set(xk, [c]);
        }
      }
    }
    g.push(p);
    this.byPair.set(k, g);
    const t0 = p.token0.toLowerCase(), t1 = p.token1.toLowerCase();
    if (!this.nbr.has(t0)) this.nbr.set(t0, new Set());
    if (!this.nbr.has(t1)) this.nbr.set(t1, new Set());
    this.nbr.get(t0)!.add(t1);
    this.nbr.get(t1)!.add(t0);
  }

  /** Best `n` pools for the directed edge from → to, by log-rate. */
  private bestEdge(from: string, to: string, n: number): Array<{ pool: Pool; rate: number }> {
    const g = this.byPair.get(pairKey(from as Address, to as Address)) ?? [];
    const out: Array<{ pool: Pool; rate: number }> = [];
    for (const pool of g) {
      const rate = logRate(pool, from);
      if (Number.isFinite(rate)) out.push({ pool, rate });
    }
    return out.sort((a, b) => b.rate - a.rate).slice(0, n);
  }

  /**
   * Triangles A→B→C→A that use a touched pool as one leg, both directions. Pre-filter: the sum of log-rates of the
   * legs (best two pools per other edge) must exceed `minEdge`; survivors are sized exactly with optimizeRoute.
   */
  searchTriangles(touched: Iterable<string>, budgetMs = 100, opts: { minEdge?: number; poolsPerEdge?: number } = {}): Opportunity[] {
    const minEdge = opts.minEdge ?? 0.0002;
    const perEdge = opts.poolsPerEdge ?? 2;
    const deadline = Date.now() + budgetMs;
    const out: Opportunity[] = [];
    const seen = new Set<string>();
    for (const t of touched) {
      const P = this.byAddr.get(t.toLowerCase());
      if (!P) continue;
      const A = P.token0.toLowerCase(), B = P.token1.toLowerCase();
      const nA = this.nbr.get(A), nB = this.nbr.get(B);
      if (!nA || !nB) continue;
      const [small, big] = nA.size < nB.size ? [nA, nB] : [nB, nA];
      for (const C of small) {
        if (C === A || C === B || !big.has(C)) continue;
        if (Date.now() > deadline) return out;
        // direction 1: A -P-> B -> C -> A ; direction 2: B -P-> A -> C -> B
        for (const [X, Y] of [[A, B], [B, A]] as const) {
          const rP = logRate(P, X);
          if (!Number.isFinite(rP)) continue;
          const e2 = this.bestEdge(Y, C, perEdge);
          const e3 = this.bestEdge(C, X, perEdge);
          if (e2.length === 0 || e3.length === 0 || rP + e2[0]!.rate + e3[0]!.rate <= minEdge) continue;
          for (const q of e2) for (const r of e3) {
            const edge = rP + q.rate + r.rate;
            if (edge <= minEdge) continue;
            // legs in cycle order; rotate so the cycle starts at a preferred (priced) token when one is present
            let legs: Array<{ pool: Pool; from: string; to: string }> = [
              { pool: P, from: X, to: Y },
              { pool: q.pool, from: Y, to: C },
              { pool: r.pool, from: C, to: X },
            ];
            for (const pref of this.startPref) {
              const startAt = legs.findIndex((l) => l.from === pref);
              if (startAt < 0) continue;
              if (startAt > 0) legs = [...legs.slice(startAt), ...legs.slice(0, startAt)];
              break;
            }
            const key = legs.map((l) => l.pool.address.toLowerCase() + ">" + l.to).join("|");
            if (seen.has(key)) continue;
            seen.add(key);
            const tok = (pool: Pool, a: string) => (pool.token0.toLowerCase() === a ? pool.token0 : pool.token1) as Address;
            const route = legs.map((l) => ({ pool: l.pool, tokenIn: tok(l.pool, l.from), tokenOut: tok(l.pool, l.to) }));
            const start = route[0]!.tokenIn;
            const b = sizeBounds(route[0]!.pool, start, Math.expm1(edge));
            const best = optimizeRoute(route, b.lo, b.hi);
            if (best.profit <= 0n) continue;
            const ev = evalRoute(route, best.amountIn);
            if (!ev.valid) continue;
            out.push({ token: start, hops: ev.hops, amountIn: best.amountIn, amountOut: ev.amountOut, profit: ev.amountOut - best.amountIn, gasEstimate: estimateGas(ev.hops), gapBps: edge * 1e4 });
          }
        }
      }
    }
    return out.sort((x, y) => (y.profit > x.profit ? 1 : y.profit < x.profit ? -1 : 0));
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
