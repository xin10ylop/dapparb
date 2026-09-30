import type { Pool } from "../pools/types.js";
import { sideAmounts } from "./pricing.js";

/**
 * Pool depth in ETH: the smaller of the two sides' values (real reserves for V2, virtual reserves at the
 * current price for CL pools). Taking the minimum means a pool whose own price is far from the market
 * (a dead pool holding lots of a priced token against dust of the other) is valued by its dust side and
 * discarded, instead of by the side that could never actually be bought out of it. A side whose token has
 * no anchored price counts as zero, so a pool between two unpriced tokens is discarded too.
 */
export function poolDepthEth(pool: Pool, prices: Map<string, number>): number {
  const p0 = prices.get(pool.token0.toLowerCase());
  const p1 = prices.get(pool.token1.toLowerCase());
  const { amt0, amt1 } = sideAmounts(pool);
  const v0 = p0 !== undefined ? amt0 * p0 : NaN;
  const v1 = p1 !== undefined ? amt1 * p1 : NaN;
  if (Number.isFinite(v0) && Number.isFinite(v1)) return Math.min(v0, v1);
  return Number.isFinite(v0) ? v0 : Number.isFinite(v1) ? v1 : 0;
}

export function filterByDepth(pools: Pool[], prices: Map<string, number>, minDepthEth: number): Pool[] {
  return pools.filter((p) => poolDepthEth(p, prices) >= minDepthEth);
}
