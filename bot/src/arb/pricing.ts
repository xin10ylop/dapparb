import type { Address } from "viem";
import type { ChainConfig } from "../config/chains.js";
import { isV2, type Pool } from "../pools/types.js";
import { spotPrice } from "./quote.js";

/**
 * Robust token → ETH price map derived from the pool set itself (median across WETH-paired pools,
 * weighted toward deep pools), with a USDC fallback for tokens that only trade against stables.
 */
export function buildEthPrices(cfg: ChainConfig, pools: Pool[]): Map<string, number> {
  const weth = cfg.weth.toLowerCase();
  const usdc = cfg.usdc.toLowerCase();
  const prices = new Map<string, number>();
  prices.set(weth, 1);

  const samples = new Map<string, Array<{ px: number; depth: number }>>();
  const add = (token: string, px: number, depth: number) => {
    if (!Number.isFinite(px) || px <= 0) return;
    const arr = samples.get(token) ?? [];
    arr.push({ px, depth });
    samples.set(token, arr);
  };
  for (const p of pools) {
    const t0 = p.token0.toLowerCase();
    const t1 = p.token1.toLowerCase();
    if (t0 !== weth && t1 !== weth) continue;
    const px = spotPrice(p); // token1 per token0
    const depth = isV2(p) ? Number(t0 === weth ? p.reserve0 : p.reserve1) / 1e18 : Number(p.state.liquidity) / 1e18;
    if (t0 === weth) add(t1, 1 / px, depth); // token1 in ETH = 1/(token1 per ETH)
    else add(t0, px, depth); // token0 in ETH = token1(=WETH) per token0
  }
  const pick = (arr: Array<{ px: number; depth: number }>): number => {
    // depth-weighted median
    const sorted = [...arr].sort((a, b) => a.px - b.px);
    const total = sorted.reduce((s, x) => s + x.depth, 0);
    let acc = 0;
    for (const x of sorted) {
      acc += x.depth;
      if (acc >= total / 2) return x.px;
    }
    return sorted[Math.floor(sorted.length / 2)]!.px;
  };
  for (const [token, arr] of samples) prices.set(token, pick(arr));

  // Fallback via USDC for tokens without a WETH pool.
  const usdcEth = prices.get(usdc);
  if (usdcEth) {
    for (const p of pools) {
      const t0 = p.token0.toLowerCase();
      const t1 = p.token1.toLowerCase();
      if (t0 !== usdc && t1 !== usdc) continue;
      const other = t0 === usdc ? t1 : t0;
      if (prices.has(other)) continue;
      const px = spotPrice(p);
      const otherInUsdc = t0 === usdc ? 1 / px : px;
      prices.set(other, otherInUsdc * usdcEth);
    }
  }
  return prices;
}

export function toEth(prices: Map<string, number>, token: Address, amount: bigint, decimals: number): number {
  const px = prices.get(token.toLowerCase());
  if (px === undefined) return NaN;
  return (Number(amount) / 10 ** decimals) * px;
}
