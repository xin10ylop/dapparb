import { type Address, type PublicClient, zeroAddress } from "viem";
import type { ChainConfig, DexConfig, TokenConfig } from "../config/chains.js";
import { AERO_CL_FACTORY_ABI, AERO_FACTORY_ABI, UNIV2_FACTORY_ABI, UNIV3_FACTORY_ABI } from "../abi.js";
import { sortTokens, type Pool } from "./types.js";
import { log } from "../util/log.js";
import { multicallChunked } from "../util/multicall.js";

interface Candidate {
  dex: DexConfig;
  tokenA: TokenConfig;
  tokenB: TokenConfig;
  tier: number; // fee / tickSpacing / (0=volatile,1=stable for aero-v2) / 0 for univ2
}

/**
 * Long-tail universes: pairing every token with every other is quadratic, but long-tail tokens trade almost
 * exclusively against WETH/USDC. Pair each extra token with the base tokens, and keep the full pairing among
 * the hand-picked config tokens.
 */
export function longTailPairs(cfg: ChainConfig, tokens: TokenConfig[]): Array<[TokenConfig, TokenConfig]> {
  const core = cfg.tokens;
  const coreSet = new Set(core.map((t) => t.address.toLowerCase()));
  const bases = core.filter((t) => t.address.toLowerCase() === cfg.weth.toLowerCase() || t.address.toLowerCase() === cfg.usdc.toLowerCase());
  const pairs: Array<[TokenConfig, TokenConfig]> = [];
  for (let i = 0; i < core.length; i++) for (let j = i + 1; j < core.length; j++) pairs.push([core[i]!, core[j]!]);
  for (const t of tokens) {
    if (coreSet.has(t.address.toLowerCase())) continue;
    for (const b of bases) pairs.push([t, b]);
  }
  return pairs;
}

/**
 * Enumerate every pool that exists for each token pair across all configured DEXes.
 * Uses multicall so a full sweep of ~20 tokens x 9 DEXes is a handful of RPC round trips.
 */
export async function discoverPools(client: PublicClient, cfg: ChainConfig, tokens: TokenConfig[] = cfg.tokens, pairs?: Array<[TokenConfig, TokenConfig]>): Promise<Pool[]> {
  const candidates: Candidate[] = [];
  const pairList: Array<[TokenConfig, TokenConfig]> = pairs ?? [];
  if (!pairs) {
    for (let i = 0; i < tokens.length; i++) for (let j = i + 1; j < tokens.length; j++) pairList.push([tokens[i]!, tokens[j]!]);
  }
  {
    for (const [tokenA, tokenB] of pairList) {
      for (const dex of cfg.dexes) {
        if (dex.kind === "univ2") candidates.push({ dex, tokenA, tokenB, tier: 0 });
        else if (dex.kind === "aero-v2") {
          candidates.push({ dex, tokenA, tokenB, tier: 0 });
          candidates.push({ dex, tokenA, tokenB, tier: 1 });
        } else for (const t of dex.tiers ?? []) candidates.push({ dex, tokenA, tokenB, tier: t });
      }
    }
  }

  const contracts = candidates.map((c) => {
    const [t0, t1] = sortTokens(c.tokenA.address, c.tokenB.address);
    switch (c.dex.kind) {
      case "univ3":
      case "pancake-v3":
        return { address: c.dex.factory, abi: UNIV3_FACTORY_ABI, functionName: "getPool", args: [t0, t1, c.tier] } as const;
      case "aero-cl":
        return { address: c.dex.factory, abi: AERO_CL_FACTORY_ABI, functionName: "getPool", args: [t0, t1, c.tier] } as const;
      case "aero-v2":
        return { address: c.dex.factory, abi: AERO_FACTORY_ABI, functionName: "getPool", args: [t0, t1, c.tier === 1] } as const;
      case "univ2":
        return { address: c.dex.factory, abi: UNIV2_FACTORY_ABI, functionName: "getPair", args: [t0, t1] } as const;
    }
  });

  const results = await multicallChunked(client, cfg.multicall3, contracts as any);

  const pools: Pool[] = [];
  const seen = new Set<string>();
  results.forEach((r, idx) => {
    if (r.status !== "success") return;
    const addr = r.result as Address;
    if (!addr || addr === zeroAddress) return;
    const key = addr.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    const c = candidates[idx]!;
    const [t0, t1] = sortTokens(c.tokenA.address, c.tokenB.address);
    const dec0 = t0 === c.tokenA.address ? c.tokenA.decimals : c.tokenB.decimals;
    const dec1 = t1 === c.tokenB.address ? c.tokenB.decimals : c.tokenA.decimals;
    const base = { address: addr, dex: c.dex.name, token0: t0, token1: t1, dec0, dec1, block: 0n };
    if (c.dex.kind === "univ2") {
      pools.push({ ...base, kind: "univ2", feeBps: c.dex.feeBps ?? 30, stable: false, reserve0: 0n, reserve1: 0n });
    } else if (c.dex.kind === "aero-v2") {
      pools.push({ ...base, kind: "aero-v2", feeBps: 0, stable: c.tier === 1, reserve0: 0n, reserve1: 0n });
    } else {
      pools.push({
        ...base,
        kind: c.dex.kind,
        tier: c.tier,
        state: {
          sqrtPriceX96: 0n,
          tick: 0,
          liquidity: 0n,
          fee: c.dex.kind === "aero-cl" ? 0 : c.tier,
          tickSpacing: c.dex.kind === "aero-cl" ? c.tier : 0,
          bitmap: new Map(),
          ticks: new Map(),
          wordRange: { min: 0, max: -1 },
        },
      });
    }
  });
  log.info({ candidates: candidates.length, found: pools.length }, "pool discovery complete");
  return pools;
}
