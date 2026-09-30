/**
 * Cross-chain DEX-to-DEX spread study: the same pair's deepest Uniswap V3 pool on Base, Arbitrum and Ethereum,
 * sampled every ~2 s. Non-atomic by construction (inventory on each chain, rebalanced by bridging).
 *   npx tsx src/research/crosschain.ts --minutes 15 --out data/crosschain.jsonl
 */
import "dotenv/config";
import fs from "node:fs";
import { createPublicClient, http } from "viem";
import { base, arbitrum, mainnet } from "viem/chains";
import { V3_POOL_ABI } from "../abi.js";
import { sqrtPriceToPrice } from "../math/v3.js";
const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "15"));
const out = fs.createWriteStream(arg("out", "data/crosschain.jsonl")!, { flags: "a" });
// WETH/USDC 0.05% Uniswap V3 on each chain (token order differs per chain; price normalised to USDC per WETH)
const POOLS = [
  { chain: "base", client: createPublicClient({ chain: base, transport: http("https://base-rpc.publicnode.com") }), address: "0xd0b53D9277642d899DF5C87A3966A349A798F224", wethIs0: true, fee: 5 },
  { chain: "arbitrum", client: createPublicClient({ chain: arbitrum, transport: http("https://arbitrum-one-rpc.publicnode.com") }), address: "0xC6962004f452bE9203591991D15f6b388e09E8D0", wethIs0: true, fee: 5 },
  { chain: "mainnet", client: createPublicClient({ chain: mainnet, transport: http("https://ethereum-rpc.publicnode.com") }), address: "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640", wethIs0: false, fee: 5 },
] as const;
async function main() {
  const end = Date.now() + minutes * 60_000; let n = 0; const spreads: Record<string, number[]> = {};
  while (Date.now() < end) {
    const t0 = Date.now();
    const px: Record<string, number> = {};
    await Promise.all(POOLS.map(async (p) => {
      try {
        const [sqrtP] = await p.client.readContract({ address: p.address as `0x${string}`, abi: V3_POOL_ABI, functionName: "slot0" });
        const raw = sqrtPriceToPrice(sqrtP, p.wethIs0 ? 18 : 6, p.wethIs0 ? 6 : 18); // token1 per token0
        px[p.chain] = p.wethIs0 ? raw : 1 / raw;
      } catch {}
    }));
    const rec: any = { t: t0, ...px };
    for (const a of Object.keys(px)) for (const b of Object.keys(px)) if (a < b) { const bps = (px[a]! / px[b]! - 1) * 1e4; rec[`${a}-${b}`] = +bps.toFixed(2); (spreads[`${a}-${b}`] ??= []).push(bps); }
    out.write(JSON.stringify(rec) + "\n"); n++;
    if (n % 60 === 0) console.log(`${new Date().toISOString()} samples=${n}`, Object.fromEntries(Object.entries(spreads).map(([k, v]) => { const s = [...v].sort((x, y) => x - y); const q = (p: number) => s[Math.floor(p * (s.length - 1))]!.toFixed(1); return [k, `p5=${q(0.05)} p50=${q(0.5)} p95=${q(0.95)} |>10bps ${(100 * v.filter((x) => Math.abs(x) > 10).length / v.length).toFixed(0)}%`]; })));
    await new Promise((r) => setTimeout(r, Math.max(200, 2000 - (Date.now() - t0))));
  }
  console.log("=== cross-chain WETH/USDC spread summary (bps, positive = first chain pricier) ===");
  for (const [k, v] of Object.entries(spreads)) { const s = [...v].sort((x, y) => x - y); const q = (p: number) => s[Math.floor(p * (s.length - 1))]!.toFixed(1); console.log(`${k}: n=${v.length} p5=${q(0.05)} p50=${q(0.5)} p95=${q(0.95)} |abs>10bps: ${(100 * v.filter((x) => Math.abs(x) > 10).length / v.length).toFixed(1)}%  |abs>20bps: ${(100 * v.filter((x) => Math.abs(x) > 20).length / v.length).toFixed(1)}%  (fees: 5 bps per leg + bridge/rebalance cost)`); }
  out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
