/**
 * CEX (OKX) vs Base DEX price study for long-tail tokens listed on both. One OKX tickers call every 500 ms covers
 * every spot pair; the deepest Base pool per token is read at every block. Records go to a JSONL for analysis.
 *   npx tsx src/research/leadlag-multi.ts --minutes 30 --tokens AERO,VIRTUAL,BRETT,DEGEN,ZORA,MORPHO,LINK,AAVE
 */
import "dotenv/config";
import fs from "node:fs";
import { getChain } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools } from "../pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools } from "../pools/state.js";
import { buildEthPrices } from "../arb/pricing.js";
import { poolDepthEth } from "../arb/depth.js";
import { spotPrice } from "../arb/quote.js";
import type { Pool } from "../pools/types.js";

const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "30"));
const wanted = (arg("tokens", "AERO,VIRTUAL,BRETT,DEGEN,ZORA,MORPHO,LINK,AAVE")!).split(",");
const out = fs.createWriteStream(arg("out", "data/leadlag-multi.jsonl")!, { flags: "a" });
const cfg = getChain("base");
const client = makeHttpClient(cfg);

async function main() {
  const tokens = cfg.tokens.filter((t) => wanted.includes(t.symbol) || ["WETH", "USDC"].includes(t.symbol));
  let pools = await discoverPools(client, cfg, tokens);
  await loadStaticMetadata(client, cfg, pools);
  await syncPools(client, cfg, pools, { force: true });
  pools = pruneEmpty(pools);
  const prices = buildEthPrices(cfg, pools);
  // deepest pool per token (against WETH or USDC)
  const chosen = new Map<string, Pool>();
  for (const t of tokens) {
    if (["WETH", "USDC"].includes(t.symbol)) continue;
    const cands = pools.filter((p) => [p.token0, p.token1].map((a) => a.toLowerCase()).includes(t.address.toLowerCase()) && [p.token0, p.token1].some((a) => [cfg.weth, cfg.usdc].map((x) => x.toLowerCase()).includes(a.toLowerCase())));
    cands.sort((a, b) => poolDepthEth(b, prices) - poolDepthEth(a, prices));
    if (cands[0]) chosen.set(t.symbol, cands[0]);
  }
  console.log("tracking:", [...chosen.entries()].map(([s, p]) => `${s}@${p.dex}${(p as any).tier ? "/" + (p as any).tier : ""} depth=${poolDepthEth(p, prices).toFixed(1)}ETH`).join("  "));
  const tracked = [...chosen.values()];
  const end = Date.now() + minutes * 60_000;
  let cexN = 0, dexN = 0, lastBlock = 0n;
  const cexLoop = (async () => {
    while (Date.now() < end) {
      const t0 = Date.now();
      try {
        const r: any = await (await fetch("https://www.okx.com/api/v5/market/tickers?instType=SPOT", { signal: AbortSignal.timeout(4000) })).json();
        const mids: Record<string, number> = {};
        for (const t of r.data ?? []) { const c = String(t.instId).split("-")[0]!; if ((wanted.includes(c) || c === "ETH") && String(t.instId).endsWith("-USDT")) mids[c] = (Number(t.bidPx) + Number(t.askPx)) / 2; }
        out.write(JSON.stringify({ src: "okx", t: t0, mids }) + "\n"); cexN++;
      } catch {}
      await new Promise((r) => setTimeout(r, Math.max(100, 500 - (Date.now() - t0))));
    }
  })();
  const dexLoop = (async () => {
    while (Date.now() < end) {
      try {
        const bn = await client.getBlockNumber();
        if (bn !== lastBlock) {
          lastBlock = bn;
          const t0 = Date.now();
          await syncPools(client, cfg, tracked, { blockNumber: bn });
          const px: Record<string, { price: number; quote: string }> = {};
          for (const [sym, p] of chosen) {
            const t = tokens.find((x) => x.symbol === sym)!;
            const isT0 = p.token0.toLowerCase() === t.address.toLowerCase();
            const sp = spotPrice(p); // token1 per token0
            const quoteAddr = (isT0 ? p.token1 : p.token0).toLowerCase();
            px[sym] = { price: isT0 ? sp : 1 / sp, quote: quoteAddr === cfg.weth.toLowerCase() ? "WETH" : "USDC" };
          }
          out.write(JSON.stringify({ src: "base", t: t0, block: Number(bn), px }) + "\n"); dexN++;
        }
      } catch {}
      await new Promise((r) => setTimeout(r, 300));
    }
  })();
  const prog = setInterval(() => console.log(`cex=${cexN} dex=${dexN}`), 60_000);
  await Promise.all([cexLoop, dexLoop]); clearInterval(prog); out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
