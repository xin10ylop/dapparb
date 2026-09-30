/**
 * Live verification: local V3 simulation must match the on-chain QuoterV2 exactly for a range of sizes
 * across Uniswap V3, PancakeSwap V3, Sushi V3 and Aerodrome Slipstream pools on Base.
 * Run: npx tsx --test src/math/v3.live.test.ts
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { BASE } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools } from "../pools/discovery.js";
import { loadStaticMetadata, syncPools } from "../pools/state.js";
import { isV3, type V3Pool } from "../pools/types.js";
import { AERO_CL_QUOTER_ABI, QUOTER_V2_ABI } from "../abi.js";
import { simulateExactInput } from "./v3.js";

test("local V3 simulation matches on-chain quoter", async () => {
  const client = makeHttpClient(BASE);
  const weth = BASE.tokens.find((t) => t.symbol === "WETH")!;
  const usdc = BASE.tokens.find((t) => t.symbol === "USDC")!;
  const aero = BASE.tokens.find((t) => t.symbol === "AERO")!;
  const cbbtc = BASE.tokens.find((t) => t.symbol === "cbBTC")!;
  const pools = await discoverPools(client, BASE, [weth, usdc, aero, cbbtc]);
  await loadStaticMetadata(client, BASE, pools);
  const block = await syncPools(client, BASE, pools, { force: true });
  const v3 = pools.filter(isV3).filter((p) => p.state.liquidity > 0n) as V3Pool[];
  assert.ok(v3.length >= 8, `expected many V3 pools, got ${v3.length}`);

  const sizes = [1n, 100n, 10_000n, 1_000_000n]; // multiples of 1e-4 units of tokenIn
  let checked = 0;
  let mismatches: string[] = [];
  for (const p of v3) {
    const dex = BASE.dexes.find((d) => d.name === p.dex)!;
    for (const zeroForOne of [true, false]) {
      const tokenIn = zeroForOne ? p.token0 : p.token1;
      const tokenOut = zeroForOne ? p.token1 : p.token0;
      const decIn = zeroForOne ? p.dec0 : p.dec1;
      for (const s of sizes) {
        const amountIn = (s * 10n ** BigInt(decIn)) / 10_000n;
        if (amountIn === 0n) continue;
        const local = simulateExactInput(p.state, zeroForOne, amountIn);
        let onchain: bigint | null = null;
        try {
          if (p.kind === "aero-cl") {
            const r = await client.simulateContract({
              address: dex.quoter!,
              abi: AERO_CL_QUOTER_ABI,
              functionName: "quoteExactInputSingle",
              args: [{ tokenIn, tokenOut, amountIn, tickSpacing: p.tier, sqrtPriceLimitX96: 0n }],
              blockNumber: block,
            });
            onchain = r.result[0];
          } else {
            const r = await client.simulateContract({
              address: dex.quoter!,
              abi: QUOTER_V2_ABI,
              functionName: "quoteExactInputSingle",
              args: [{ tokenIn, tokenOut, amountIn, fee: p.tier, sqrtPriceLimitX96: 0n }],
              blockNumber: block,
            });
            onchain = r.result[0];
          }
        } catch (e) {
          onchain = null; // quoter reverted (e.g. insufficient liquidity) — local must be truncated
        }
        checked++;
        if (onchain === null) {
          if (!local.truncated && local.amountOut > 0n) mismatches.push(`${p.dex} ${p.address} z4o=${zeroForOne} in=${amountIn}: quoter reverted but local=${local.amountOut}`);
          continue;
        }
        if (local.truncated) continue; // we ran out of tick window; acceptable, bot treats as unquotable
        if (local.amountOut !== onchain) mismatches.push(`${p.dex} ${p.address} z4o=${zeroForOne} in=${amountIn}: local=${local.amountOut} quoter=${onchain} crossed=${local.ticksCrossed}`);
      }
    }
  }
  console.log(`checked ${checked} quotes across ${v3.length} pools at block ${block}; mismatches=${mismatches.length}`);
  for (const m of mismatches.slice(0, 20)) console.log("  MISMATCH", m);
  assert.equal(mismatches.length, 0);
});
