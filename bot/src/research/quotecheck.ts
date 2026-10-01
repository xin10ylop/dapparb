/**
 * Local swap math vs on-chain execution, per pool type, at one pinned block.
 *
 *   npx tsx src/research/quotecheck.ts [--per-dex 20] [--registry data/pool-registry-base.json] [--universe data/universe-activeonly.jsonl]
 *   npx tsx src/research/quotecheck.ts --pools 0xabc...,0xdef...     # specific registry pools
 *
 * Samples registry pools of every DEX label (Uniswap V3, PancakeSwap V3, Slipstream, Sushi V3, V3/Pancake clones,
 * Uniswap V4), syncs them with the engine's own code at block B, and compares quote() with:
 *   - V3-style pools: contracts/src/test-helpers/PoolQuoter.sol injected by state override (calls pool.swap and
 *     reverts in the callback with the deltas, so it works for clones that have no quoter);
 *   - V4 pools: the official V4Quoter.
 * Sizes are 0.01 %, 0.1 % and 1 % of the pool's in-range virtual reserve of the input token, both directions.
 */
import "dotenv/config";
import fs from "node:fs";
import { type Address, type Hex, decodeFunctionResult, encodeFunctionData, parseAbi } from "viem";
import { BASE } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { loadRegistry, poolsFromRegistry, registryPath } from "../pools/activity.js";
import { loadStaticMetadata, syncPools } from "../pools/state.js";
import { isV3, type V3Pool } from "../pools/types.js";
import { isV4 } from "../pools/v4.js";
import { quote } from "../arb/quote.js";
import { sideAmounts } from "../arb/pricing.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}
const cfg = BASE;
const client = makeHttpClient(cfg);
const perDex = Number(arg("per-dex", "20"));
const reg = loadRegistry(arg("registry", registryPath(cfg))!, cfg);
const universeFile = arg("universe", "data/universe-activeonly.jsonl")!;
const QUOTER_AT = "0x00000000000000000000000000000000000ab0b0" as Address;
const QUOTER_CODE = ("0x" + fs.readFileSync(new URL("../exec/artifacts/PoolQuoter.runtime.hex", import.meta.url), "utf8").trim().replace(/^0x/, "")) as Hex;
const QUOTER_ABI = parseAbi(["function quote(address pool, bool zeroForOne, uint256 amountIn) returns (uint256 amountOut, uint256 amountInUsed)"]);
const V4_QUOTER = "0x0d5e0f971ed27fbff6c2837bf31316121532048d" as Address;
const V4_QUOTER_ABI = parseAbi([
  "struct PoolKey { address currency0; address currency1; uint24 fee; int24 tickSpacing; address hooks; }",
  "struct QuoteExactSingleParams { PoolKey poolKey; bool zeroForOne; uint128 exactAmount; bytes hookData; }",
  "function quoteExactInputSingle(QuoteExactSingleParams params) returns (uint256 amountOut, uint256 gasEstimate)",
]);

async function main() {
  // pools that passed the engine's depth filter, grouped by DEX label
  const deep = new Set<string>();
  for (const l of fs.readFileSync(universeFile, "utf8").split("\n")) {
    if (!l.trim()) continue;
    const d = JSON.parse(l);
    if ((d.depthEth ?? 1) >= 0.1) deep.add(String(d.poolId ?? d.address).toLowerCase());
  }
  const groups = new Map<string, string[]>();
  for (const [k, e] of Object.entries(reg.pools)) {
    if (e.kind === "univ2" || e.kind === "aero-v2" || !deep.has(k)) continue;
    const g = e.dex.split(":")[0]!;
    const arr = groups.get(g) ?? [];
    if (arr.length < perDex) arr.push(k);
    groups.set(g, arr);
  }
  const only = arg("pools");
  const keys = only ? only.split(",").map((k) => k.trim().toLowerCase()) : [...groups.values()].flat();
  const { pools } = poolsFromRegistry(reg, cfg, keys);
  await loadStaticMetadata(client, cfg, pools);
  const block = await syncPools(client, cfg, pools, { force: true });
  const res = new Map<string, { quotes: number; exact: number; within1bp: number; worst: number; truncated: number; failed: number; examples: string[] }>();
  for (const p of pools as V3Pool[]) {
    if (!isV3(p)) continue;
    const label = p.dex.split(":")[0]!;
    const r = res.get(label) ?? { quotes: 0, exact: 0, within1bp: 0, worst: 0, truncated: 0, failed: 0, examples: [] };
    res.set(label, r);
    const { amt0, amt1 } = sideAmounts(p);
    for (const zeroForOne of [true, false]) {
      const virt = zeroForOne ? amt0 : amt1;
      const dec = zeroForOne ? p.dec0 : p.dec1;
      for (const frac of [1e-4, 1e-3, 1e-2]) {
        const amountIn = BigInt(Math.floor(virt * frac * 10 ** Math.min(dec, 15))) * 10n ** BigInt(Math.max(0, dec - 15));
        if (amountIn <= 0n) continue;
        const local = quote(p, zeroForOne ? p.token0 : p.token1, amountIn);
        let onchain: bigint | null = null;
        try {
          if (isV4(p)) {
            const data = encodeFunctionData({ abi: V4_QUOTER_ABI, functionName: "quoteExactInputSingle", args: [{ poolKey: p.v4.key, zeroForOne, exactAmount: amountIn, hookData: "0x" }] });
            const out = await client.call({ to: V4_QUOTER, data, blockNumber: block });
            onchain = (decodeFunctionResult({ abi: V4_QUOTER_ABI, functionName: "quoteExactInputSingle", data: out.data! }) as readonly [bigint, bigint])[0];
          } else {
            const data = encodeFunctionData({ abi: QUOTER_ABI, functionName: "quote", args: [p.address, zeroForOne, amountIn] });
            const out = await client.call({ to: QUOTER_AT, data, blockNumber: block, stateOverride: [{ address: QUOTER_AT, code: QUOTER_CODE }] });
            const [amountOut, used] = decodeFunctionResult({ abi: QUOTER_ABI, functionName: "quote", data: out.data! }) as readonly [bigint, bigint];
            onchain = used === amountIn ? amountOut : null; // partial fill: pool ran out of range
          }
        } catch {
          r.failed++;
          continue;
        }
        if (local.truncated || onchain === null) {
          r.truncated++;
          continue;
        }
        r.quotes++;
        const rel = onchain === 0n ? (local.amountOut === 0n ? 0 : 1) : Math.abs(Number(local.amountOut - onchain)) / Number(onchain);
        if (local.amountOut === onchain) r.exact++;
        if (rel <= 1e-4) r.within1bp++;
        if (rel > r.worst) r.worst = rel;
        if (rel > 1e-4 && r.examples.length < 3) r.examples.push(`${p.address} ${zeroForOne ? "0>1" : "1>0"} in=${amountIn} local=${local.amountOut} chain=${onchain} fee=${p.state.fee} feeByDir=${JSON.stringify(p.state.feeByDir ?? null)} ts=${p.state.tickSpacing}`);
      }
    }
  }
  console.log(`block ${block}`);
  for (const [label, r] of res) {
    console.log(`${label.padEnd(16)} quotes ${String(r.quotes).padStart(4)}  exact ${String(r.exact).padStart(4)}  within 1bp ${String(r.within1bp).padStart(4)}  worst ${(r.worst * 1e4).toFixed(2)} bp  truncated ${r.truncated}  call-failed ${r.failed}`);
    for (const e of r.examples) console.log("    ", e);
  }
}
main().then(() => process.exit(0)).catch((e) => {
  console.error(e);
  process.exit(1);
});
