import type { Address } from "viem";
import { aeroStableGetAmountOut, aeroVolatileGetAmountOut, univ2GetAmountOut } from "../math/v2.js";
import { simulateExactInput, sqrtPriceToPrice } from "../math/v3.js";
import { isV2, type Pool } from "../pools/types.js";

export interface Quote {
  amountOut: bigint;
  ticksCrossed: number;
  /** Simulation could not fill the full input with the data we hold; the quote is unreliable. */
  truncated: boolean;
}

const ZERO: Quote = { amountOut: 0n, ticksCrossed: 0, truncated: true };

/** Exact-input quote on any pool kind. tokenIn must be one of the pool's tokens. */
export function quote(pool: Pool, tokenIn: Address, amountIn: bigint): Quote {
  if (amountIn <= 0n) return ZERO;
  const zeroForOne = tokenIn.toLowerCase() === pool.token0.toLowerCase();
  if (isV2(pool)) {
    const [rIn, rOut] = zeroForOne ? [pool.reserve0, pool.reserve1] : [pool.reserve1, pool.reserve0];
    if (rIn === 0n || rOut === 0n) return ZERO;
    let out: bigint;
    if (pool.kind === "univ2") out = univ2GetAmountOut(amountIn, rIn, rOut, pool.feeBps);
    else if (pool.stable) {
      const [dIn, dOut] = zeroForOne ? [10n ** BigInt(pool.dec0), 10n ** BigInt(pool.dec1)] : [10n ** BigInt(pool.dec1), 10n ** BigInt(pool.dec0)];
      try {
        out = aeroStableGetAmountOut(amountIn, rIn, rOut, dIn, dOut, pool.feeBps);
      } catch {
        return ZERO;
      }
    } else out = aeroVolatileGetAmountOut(amountIn, rIn, rOut, pool.feeBps);
    if (out >= rOut) return ZERO;
    return { amountOut: out, ticksCrossed: 0, truncated: false };
  }
  try {
    const r = simulateExactInput(pool.state, zeroForOne, amountIn);
    return { amountOut: r.amountOut, ticksCrossed: r.ticksCrossed, truncated: r.truncated };
  } catch {
    return ZERO;
  }
}

/** Mid price of token1 per token0 (float, human units). */
export function spotPrice(pool: Pool): number {
  if (isV2(pool)) {
    if (pool.reserve0 === 0n || pool.reserve1 === 0n) return 0;
    const x = Number(pool.reserve0) / 10 ** pool.dec0;
    const y = Number(pool.reserve1) / 10 ** pool.dec1;
    if (pool.kind === "aero-v2" && pool.stable) {
      // x^3*y + x*y^3 = k  →  marginal price -dy/dx = (3x^2*y + y^3) / (x^3 + 3x*y^2)
      return (3 * x * x * y + y * y * y) / (x * x * x + 3 * x * y * y);
    }
    return y / x;
  }
  return sqrtPriceToPrice(pool.state.sqrtPriceX96, pool.dec0, pool.dec1);
}

/** Round-trip fee of a pool as a fraction (0.003 = 0.3%). */
export function poolFee(pool: Pool): number {
  if (isV2(pool)) return pool.feeBps / 10_000;
  const d = pool.state.feeByDir;
  return (d ? Math.min(d.zeroForOne, d.oneForZero) : pool.state.fee) / 1_000_000;
}
