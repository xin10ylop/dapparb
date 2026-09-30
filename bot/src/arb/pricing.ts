import type { Address } from "viem";
import type { ChainConfig } from "../config/chains.js";
import { isV2, type Pool } from "../pools/types.js";
import { spotPrice } from "./quote.js";
import { Q96 } from "../math/v3.js";

/**
 * Minimum (virtual) reserve of the anchor token, in ETH, for a pool to be allowed to price the other token.
 * Without this a dust pool (e.g. 0.002 USDC against 1e6 units of a dead token) prices that token, the dead
 * token's side of every pool it sits in then "values" at whatever the dust pool implies, and the depth filter
 * lets pools with no real liquidity through (observed: a 4e9 bps "gap" worth $28 on a pool holding $0.0001).
 */
export const MIN_ANCHOR_ETH = 0.05;

/** Reserves in human units: real reserves for V2 pools, virtual reserves at the current price for CL pools. */
export function sideAmounts(pool: Pool): { amt0: number; amt1: number } {
  if (isV2(pool)) return { amt0: Number(pool.reserve0) / 10 ** pool.dec0, amt1: Number(pool.reserve1) / 10 ** pool.dec1 };
  const L = Number(pool.state.liquidity);
  if (L === 0) return { amt0: 0, amt1: 0 };
  const sqrtP = Number(pool.state.sqrtPriceX96) / Number(Q96);
  return { amt0: L / sqrtP / 10 ** pool.dec0, amt1: (L * sqrtP) / 10 ** pool.dec1 };
}

/**
 * Token → ETH price map derived from the pool set itself. A token is priced only through pools against an
 * anchor (WETH first, then USDC for tokens with no WETH pool) whose anchor side holds at least
 * MIN_ANCHOR_ETH; among those the depth-weighted median is used. Tokens with no such pool get no price.
 */
export function buildEthPrices(cfg: ChainConfig, pools: Pool[]): Map<string, number> {
  const weth = cfg.weth.toLowerCase();
  const usdc = cfg.usdc.toLowerCase();
  const prices = new Map<string, number>();
  prices.set(weth, 1);

  const priceVia = (anchor: string, anchorEth: number, skipPriced: boolean) => {
    const samples = new Map<string, Array<{ px: number; depth: number }>>();
    for (const p of pools) {
      const t0 = p.token0.toLowerCase();
      const t1 = p.token1.toLowerCase();
      if ((t0 !== anchor && t1 !== anchor) || t0 === t1) continue;
      const other = t0 === anchor ? t1 : t0;
      if (skipPriced && prices.has(other)) continue;
      const { amt0, amt1 } = sideAmounts(p);
      const depth = (t0 === anchor ? amt0 : amt1) * anchorEth; // anchor side, in ETH
      if (!(depth >= MIN_ANCHOR_ETH)) continue;
      const px = spotPrice(p); // token1 per token0, human units
      const otherInAnchor = t0 === anchor ? 1 / px : px;
      if (!Number.isFinite(otherInAnchor) || otherInAnchor <= 0) continue;
      const arr = samples.get(other) ?? [];
      arr.push({ px: otherInAnchor * anchorEth, depth });
      samples.set(other, arr);
    }
    for (const [token, arr] of samples) {
      const sorted = [...arr].sort((a, b) => a.px - b.px);
      const total = sorted.reduce((s, x) => s + x.depth, 0);
      let acc = 0;
      let px = sorted[Math.floor(sorted.length / 2)]!.px;
      for (const x of sorted) {
        acc += x.depth;
        if (acc >= total / 2) {
          px = x.px;
          break;
        }
      }
      prices.set(token, px);
    }
  };
  priceVia(weth, 1, false);
  const usdcEth = prices.get(usdc);
  if (usdcEth) priceVia(usdc, usdcEth, true);
  return prices;
}

export function toEth(prices: Map<string, number>, token: Address, amount: bigint, decimals: number): number {
  const px = prices.get(token.toLowerCase());
  if (px === undefined) return NaN;
  return (Number(amount) / 10 ** decimals) * px;
}
