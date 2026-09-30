import type { Address } from "viem";
import type { Pool } from "../pools/types.js";
import { poolFee, quote, spotPrice } from "./quote.js";
import { estimateGas, sizeBounds, type CycleHop, type Opportunity } from "./search.js";

/**
 * Three-hop cycle search (A -> B -> C -> A across three different pools / token pairs).
 *
 * Pre-filter: for every directed token pair keep the best log-rate ln(price * (1 - fee)) among its pools;
 * a triangle can only be profitable if the three best log-rates sum to > 0 (Bellman-Ford style negative-cycle
 * condition). Exact sizing then runs only on the surviving triangles, over the top pools per edge.
 */

interface DirectedEdge {
  pool: Pool;
  logRate: number; // ln(out per in after fee) at infinitesimal size, in human units
}

function directedEdges(pools: Pool[]): Map<string, DirectedEdge[]> {
  const m = new Map<string, DirectedEdge[]>();
  const push = (from: string, to: string, e: DirectedEdge) => {
    const k = `${from}>${to}`;
    const arr = m.get(k);
    if (arr) arr.push(e);
    else m.set(k, [e]);
  };
  for (const p of pools) {
    const px = spotPrice(p); // token1 per token0
    if (!Number.isFinite(px) || px <= 0) continue;
    const fee = poolFee(p);
    const t0 = p.token0.toLowerCase();
    const t1 = p.token1.toLowerCase();
    push(t0, t1, { pool: p, logRate: Math.log(px * (1 - fee)) });
    push(t1, t0, { pool: p, logRate: Math.log((1 / px) * (1 - fee)) });
  }
  for (const arr of m.values()) arr.sort((a, b) => b.logRate - a.logRate);
  return m;
}

export interface TriangleOptions {
  /** Minimum sum of log-rates (≈ fractional edge) before exact sizing. 0.0002 = 2 bps. */
  minEdge?: number;
  /** Max pools considered per directed edge. */
  poolsPerEdge?: number;
  /** Start tokens (lowercase) for cycles; defaults to all tokens. */
  startTokens?: Set<string>;
  /** Size bounds for the start token, in wei. */
  bounds?: (token: Address) => { lo: bigint; hi: bigint };
  /** Wall-clock budget in ms. */
  budgetMs?: number;
}

export function evalRoute(hops: Array<{ pool: Pool; tokenIn: Address; tokenOut: Address }>, amountIn: bigint): { hops: CycleHop[]; amountOut: bigint; valid: boolean } {
  const out: CycleHop[] = [];
  let amt = amountIn;
  for (const h of hops) {
    const q = quote(h.pool, h.tokenIn, amt);
    if (q.truncated || q.amountOut === 0n) return { hops: [], amountOut: 0n, valid: false };
    out.push({ pool: h.pool, tokenIn: h.tokenIn, tokenOut: h.tokenOut, amountIn: amt, amountOut: q.amountOut, ticksCrossed: q.ticksCrossed });
    amt = q.amountOut;
  }
  return { hops: out, amountOut: amt, valid: true };
}

export function optimizeRoute(hops: Array<{ pool: Pool; tokenIn: Address; tokenOut: Address }>, lo: bigint, hi: bigint): { amountIn: bigint; profit: bigint } {
  const profitAt = (x: bigint): bigint => {
    if (x <= 0n) return -1n;
    const r = evalRoute(hops, x);
    return r.valid ? r.amountOut - x : -x;
  };
  let best = { amountIn: 0n, profit: 0n };
  const grid: bigint[] = [];
  for (let x = lo; x <= hi; x *= 2n) grid.push(x);
  let bestIdx = -1;
  let bestP = 0n;
  let lastP = -1n;
  let declines = 0;
  for (let i = 0; i < grid.length; i++) {
    const x = grid[i]!;
    const p = profitAt(x);
    if (p > bestP) {
      bestP = p;
      bestIdx = i;
    }
    if (p <= lastP && bestIdx >= 0) declines++;
    else declines = 0;
    if (declines >= 2 || p === -x) break;
    lastP = p;
  }
  if (bestIdx < 0) return best;
  best = { amountIn: grid[bestIdx]!, profit: bestP };
  let a = bestIdx > 0 ? grid[bestIdx - 1]! : grid[bestIdx]! / 2n;
  let b = bestIdx < grid.length - 1 ? grid[bestIdx + 1]! : grid[bestIdx]! * 2n;
  let c = b - ((b - a) * 618n) / 1000n;
  let d = a + ((b - a) * 618n) / 1000n;
  let fc = profitAt(c);
  let fd = profitAt(d);
  for (let i = 0; i < 24 && b - a > (b + a) / 2000n; i++) {
    if (fc > fd) {
      b = d;
      d = c;
      fd = fc;
      c = b - ((b - a) * 618n) / 1000n;
      fc = profitAt(c);
    } else {
      a = c;
      c = d;
      fc = fd;
      d = a + ((b - a) * 618n) / 1000n;
      fd = profitAt(d);
    }
  }
  for (const x of [c, d, (a + b) / 2n]) {
    const p = profitAt(x);
    if (p > best.profit) best = { amountIn: x, profit: p };
  }
  return best;
}



export function findTriangles(pools: Pool[], opts: TriangleOptions = {}): Opportunity[] {
  const minEdge = opts.minEdge ?? 0.0002;
  const perEdge = opts.poolsPerEdge ?? 2;
  const edges = directedEdges(pools);
  // adjacency: from -> set(to)
  const adj = new Map<string, Set<string>>();
  for (const k of edges.keys()) {
    const [from, to] = k.split(">") as [string, string];
    if (!adj.has(from)) adj.set(from, new Set());
    adj.get(from)!.add(to);
  }
  const results: Opportunity[] = [];
  const seen = new Set<string>();
  const deadline = Date.now() + (opts.budgetMs ?? 5_000);
  let enumerated = 0;
  outer: for (const [A, bs] of adj) {
    if (opts.startTokens && !opts.startTokens.has(A)) continue;
    for (const B of bs) {
      if (Date.now() > deadline) break outer;
      const cs = adj.get(B);
      if (!cs) continue;
      for (const C of cs) {
        if (C === A || C === B) continue;
        if (!adj.get(C)?.has(A)) continue;
        const e1 = edges.get(`${A}>${B}`)!;
        const e2 = edges.get(`${B}>${C}`)!;
        const e3 = edges.get(`${C}>${A}`)!;
        const bestSum = e1[0]!.logRate + e2[0]!.logRate + e3[0]!.logRate;
        if (bestSum <= minEdge) continue;
        // exact sizing over top pools per edge
        for (const p1 of e1.slice(0, perEdge))
          for (const p2 of e2.slice(0, perEdge))
            for (const p3 of e3.slice(0, perEdge)) {
              if (p1.logRate + p2.logRate + p3.logRate <= minEdge) continue;
              const key = [p1.pool.address, p2.pool.address, p3.pool.address].join("|");
              if (seen.has(key)) continue;
              seen.add(key);
              enumerated++;
              const tokenA = (p1.pool.token0.toLowerCase() === A ? p1.pool.token0 : p1.pool.token1) as Address;
              const tokenB = (p1.pool.token0.toLowerCase() === B ? p1.pool.token0 : p1.pool.token1) as Address;
              const tokenC = (p2.pool.token0.toLowerCase() === C ? p2.pool.token0 : p2.pool.token1) as Address;
              const route = [
                { pool: p1.pool, tokenIn: tokenA, tokenOut: tokenB },
                { pool: p2.pool, tokenIn: tokenB, tokenOut: tokenC },
                { pool: p3.pool, tokenIn: tokenC, tokenOut: tokenA },
              ];
              const edge = p1.logRate + p2.logRate + p3.logRate; // ≈ fractional mispricing of the cycle
              const b = opts.bounds ? opts.bounds(tokenA) : sizeBounds(p1.pool, tokenA, Math.expm1(edge));
              const best = optimizeRoute(route, b.lo, b.hi);
              if (best.profit <= 0n) continue;
              const ev = evalRoute(route, best.amountIn);
              if (!ev.valid) continue;
              results.push({
                token: tokenA,
                hops: ev.hops,
                amountIn: best.amountIn,
                amountOut: ev.amountOut,
                profit: ev.amountOut - best.amountIn,
                gasEstimate: estimateGas(ev.hops),
                gapBps: bestSum * 10_000,
              });
            }
      }
    }
  }
  if (process.env.LOG_LEVEL === "debug") console.log(`triangles: enumerated=${enumerated} found=${results.length}`);
  return results.sort((a, b) => (b.profit > a.profit ? 1 : b.profit < a.profit ? -1 : 0));
}
