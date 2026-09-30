/**
 * CEX vs DEX lead-lag and spread study (the "statistical / spatial arbitrage" angle).
 * Samples OKX ETH-USDT spot mid every 250 ms and the Base WETH/USDC prices (Uniswap V3 0.05%, Slipstream-3 ts50,
 * PancakeSwap V3 0.01%) at every block; records everything for offline analysis.
 *   npx tsx src/research/leadlag.ts --minutes 45 --out data/leadlag.jsonl
 */
import "dotenv/config";
import fs from "node:fs";
import { getChain } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { V3_POOL_ABI } from "../abi.js";
import { sqrtPriceToPrice } from "../math/v3.js";

const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "45"));
const out = fs.createWriteStream(arg("out", "data/leadlag.jsonl")!, { flags: "a" });
const cfg = getChain("base");
const client = makeHttpClient(cfg);
const POOLS = [
  { name: "UniV3/500", address: "0xd0b53D9277642d899DF5C87A3966A349A798F224" },
  { name: "AeroCL3/50", address: "0x3FE04A59Ebd38cF06080a6F60a98D124eb59392A" },
  { name: "PancakeV3/100", address: "0x72AB388E2E2F6FaceF59E3C3FA2C4E29011c2D38" },
] as const;

async function cex() {
  const r = await fetch("https://www.okx.com/api/v5/market/ticker?instId=ETH-USDT", { signal: AbortSignal.timeout(3000) });
  const j: any = await r.json();
  const d = j.data?.[0];
  return d ? { bid: Number(d.bidPx), ask: Number(d.askPx), ts: Number(d.ts) } : null;
}

async function main() {
  const end = Date.now() + minutes * 60_000;
  let lastBlock = 0n; let cexN = 0; let dexN = 0;
  const cexLoop = (async () => {
    while (Date.now() < end) {
      const t0 = Date.now();
      try { const c = await cex(); if (c) { out.write(JSON.stringify({ src: "okx", t: t0, tsExch: c.ts, mid: (c.bid + c.ask) / 2, bid: c.bid, ask: c.ask }) + "\n"); cexN++; } } catch {}
      await new Promise((r) => setTimeout(r, Math.max(50, 250 - (Date.now() - t0))));
    }
  })();
  const dexLoop = (async () => {
    while (Date.now() < end) {
      try {
        const bn = await client.getBlockNumber();
        if (bn !== lastBlock) {
          lastBlock = bn;
          const t0 = Date.now();
          const res = await client.multicall({ contracts: POOLS.map((p) => ({ address: p.address as `0x${string}`, abi: V3_POOL_ABI, functionName: "slot0" })), allowFailure: true, blockNumber: bn });
          const blk = await client.getBlock({ blockNumber: bn });
          const px: Record<string, number> = {};
          res.forEach((r, i) => { if (r.status === "success") px[POOLS[i]!.name] = sqrtPriceToPrice((r.result as any)[0], 18, 6); });
          out.write(JSON.stringify({ src: "base", t: t0, block: Number(bn), blockTs: Number(blk.timestamp) * 1000, ...px }) + "\n"); dexN++;
        }
      } catch {}
      await new Promise((r) => setTimeout(r, 300));
    }
  })();
  const prog = setInterval(() => console.log(`cex samples=${cexN} dex blocks=${dexN}`), 60_000);
  await Promise.all([cexLoop, dexLoop]); clearInterval(prog); out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
