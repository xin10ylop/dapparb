/**
 * Reproduce / debug a route offline: rebuild it from pool addresses, re-price it from live state, and simulate the
 * executor calldata at `latest` (main RPC) and `pending` (preconf RPC), printing decoded revert reasons.
 *
 *   npx tsx src/cli/simroute.ts --chain base --pools 0xA,0xB --token 0xTOKEN [--amount 168.03] [--contract 0x..]
 */
import "dotenv/config";
import fs from "node:fs";
import { createPublicClient, formatUnits, getAddress, http, parseUnits, type Address, type Hex } from "viem";
import { getChain } from "../config/chains.js";
import { makeHttpClient, viemChain } from "../util/client.js";
import { discoverPools } from "../pools/discovery.js";
import { loadStaticMetadata, syncPools } from "../pools/state.js";
import { evalCycle, estimateGas, optimizeAmount, sizeBounds } from "../arb/search.js";
import { spotPrice } from "../arb/quote.js";
import { Executor } from "../exec/executor.js";
import { ERC20_ABI } from "../abi.js";

const arg = (n: string, d?: string) => {
  const i = process.argv.indexOf(`--${n}`);
  return i >= 0 ? process.argv[i + 1]! : d;
};
const cfg = getChain(arg("chain", "base")!);
const client = makeHttpClient(cfg);
const preconf = createPublicClient({ chain: viemChain(cfg), transport: http(process.env.BASE_PRECONF_RPC_URL ?? "https://mainnet-preconf.base.org") });
const poolAddrs = arg("pools")!.split(",").map((a) => getAddress(a.trim()));
const token = getAddress(arg("token")!);

async function main() {
  // discover the two pools' tokens, then rebuild the pool objects through the normal path
  const ERC = ERC20_ABI;
  const meta = await Promise.all(poolAddrs.map(async (p) => {
    const [t0, t1] = await Promise.all([
      client.readContract({ address: p, abi: [{ type: "function", name: "token0", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" }], functionName: "token0" }),
      client.readContract({ address: p, abi: [{ type: "function", name: "token1", inputs: [], outputs: [{ type: "address" }], stateMutability: "view" }], functionName: "token1" }),
    ]);
    return { p, t0: t0 as Address, t1: t1 as Address };
  }));
  const tokenAddrs = [...new Set(meta.flatMap((m) => [m.t0, m.t1]))];
  const tokens = await Promise.all(tokenAddrs.map(async (a) => ({ address: a, decimals: Number(await client.readContract({ address: a, abi: ERC, functionName: "decimals" })), symbol: String(await client.readContract({ address: a, abi: ERC, functionName: "symbol" }).catch(() => a.slice(0, 8))) })));
  const pools = await discoverPools(client, cfg, tokens);
  await loadStaticMetadata(client, cfg, pools);
  await syncPools(client, cfg, pools, { force: true });
  const A = pools.find((p) => p.address.toLowerCase() === poolAddrs[0]!.toLowerCase());
  const B = pools.find((p) => p.address.toLowerCase() === poolAddrs[1]!.toLowerCase());
  if (!A || !B) throw new Error(`pools not found via discovery: A=${!!A} B=${!!B} (unsupported DEX?)`);
  const other = (A.token0.toLowerCase() === token.toLowerCase() ? A.token1 : A.token0) as Address;
  const dec = tokens.find((t) => t.address.toLowerCase() === token.toLowerCase())!.decimals;
  console.log(`A=${A.dex} ${A.address} spot=${spotPrice(A)}  B=${B.dex} ${B.address} spot=${spotPrice(B)}  token=${token} other=${other}`);
  const gap = Math.abs(spotPrice(B) / spotPrice(A) - 1);
  const b = sizeBounds(A, token, gap);
  const best = arg("amount") ? { amountIn: parseUnits(arg("amount")!, dec), profit: 0n } : optimizeAmount(token, other, A, B, b.lo, b.hi);
  const cyc = evalCycle(token, other, A, B, best.amountIn);
  console.log(`amountIn=${formatUnits(best.amountIn, dec)} valid=${cyc.valid} amountOut=${cyc.valid ? formatUnits(cyc.amountOut, dec) : "-"} predictedProfit=${cyc.valid ? formatUnits(cyc.amountOut - best.amountIn, dec) : "-"}`);
  if (!cyc.valid) return;
  const opp = { token, hops: cyc.hops, amountIn: best.amountIn, amountOut: cyc.amountOut, profit: cyc.amountOut - best.amountIn, gasEstimate: estimateGas(cyc.hops), gapBps: gap * 1e4 };
  const contract = (arg("contract") ?? getAddress("0x00000000000000000000000000000000000a4bb0")) as Address;
  const codeOverride = arg("contract") ? undefined : (fs.readFileSync(new URL("../exec/artifacts/ArbExecutor.base.runtime.hex", import.meta.url), "utf8").trim() as Hex);
  const ex = new Executor({ cfg, client, contract, bidFraction: 0.5, maxPriorityGwei: 0.05, maxFeeGwei: 0.5, blocksValid: 2, minSimToPredictRatio: 0.8, codeOverride });
  for (const [label, c, tag] of [["latest@main", client, "latest"], ["pending@preconf", preconf, "pending"], ["latest@preconf", preconf, "latest"]] as const) {
    const r = await ex.simulateWith(c as any, opp, 1n, tag);
    console.log(`${label}: ok=${r.ok} profit=${r.ok ? formatUnits(r.profit!, dec) : "-"} gas=${r.gasUsed ?? "-"} err=${r.error ?? "-"} (${r.latencyMs}ms)`);
  }
  // hop-by-hop: simulate just hop 0 as a flash swap returning to token... not possible atomically; instead quote each hop at current state
  for (const h of cyc.hops) console.log(`  hop ${h.pool.dex} ${h.pool.address}: ${formatUnits(h.amountIn, h.tokenIn.toLowerCase() === token.toLowerCase() ? dec : tokens.find((t) => t.address.toLowerCase() === h.tokenIn.toLowerCase())!.decimals)} -> ${h.amountOut} ticksCrossed=${h.ticksCrossed}`);
}
main().then(() => process.exit(0)).catch((e) => {
  console.error(e);
  process.exit(1);
});
