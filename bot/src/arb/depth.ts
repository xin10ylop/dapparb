import { isV2, type Pool } from "../pools/types.js";
import { Q96 } from "../math/v3.js";

/**
 * Approximate pool depth in ETH: for V2 the WETH-equivalent value of one side of the reserves; for V3 the
 * virtual reserves implied by current liquidity at the current price (amount0 = L / sqrtP, amount1 = L * sqrtP).
 * Used to discard dust pools before the (expensive) cycle optimizer runs.
 */
export function poolDepthEth(pool: Pool, prices: Map<string, number>): number {
  const p0 = prices.get(pool.token0.toLowerCase());
  const p1 = prices.get(pool.token1.toLowerCase());
  if (isV2(pool)) {
    const v0 = p0 !== undefined ? (Number(pool.reserve0) / 10 ** pool.dec0) * p0 : NaN;
    const v1 = p1 !== undefined ? (Number(pool.reserve1) / 10 ** pool.dec1) * p1 : NaN;
    return Number.isFinite(v0) ? v0 : Number.isFinite(v1) ? v1 : 0;
  }
  const L = Number(pool.state.liquidity);
  if (L === 0) return 0;
  const sqrtP = Number(pool.state.sqrtPriceX96) / Number(Q96);
  const amount0 = L / sqrtP / 10 ** pool.dec0;
  const amount1 = (L * sqrtP) / 10 ** pool.dec1;
  const v0 = p0 !== undefined ? amount0 * p0 : NaN;
  const v1 = p1 !== undefined ? amount1 * p1 : NaN;
  return Number.isFinite(v0) ? v0 : Number.isFinite(v1) ? v1 : 0;
}

export function filterByDepth(pools: Pool[], prices: Map<string, number>, minDepthEth: number): Pool[] {
  return pools.filter((p) => poolDepthEth(p, prices) >= minDepthEth);
}
