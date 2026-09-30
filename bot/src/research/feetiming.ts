/**
 * Slipstream dynamic-fee timing study. Per block: every Aerodrome CL pool's current fee, the best cycle through it,
 * and the spot gap to the best other venue on the same pair. Fees on these pools move with volatility; the question
 * is whether the moment a fee drops back leaves a stale price that is cheaply arbitrageable.
 *   npx tsx src/research/feetiming.ts --minutes 45 --out data/feetiming.jsonl
 */
import "dotenv/config";
import fs from "node:fs";
import { getChain } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools, longTailPairs } from "../pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools, syncStats } from "../pools/state.js";
import { buildTokenUniverse } from "./tokens.js";
import { filterByDepth } from "../arb/depth.js";
import { buildEthPrices, toEth } from "../arb/pricing.js";
import { findOpportunities } from "../arb/search.js";
import { spotPrice, poolFee } from "../arb/quote.js";
import { isV3, pairKey, type Pool } from "../pools/types.js";

const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "45"));
const out = fs.createWriteStream(arg("out", "data/feetiming.jsonl")!, { flags: "a" });
const cfg = getChain("base");
const client = makeHttpClient(cfg);

async function main() {
  const tokens = await buildTokenUniverse(client, cfg, 6, 250);
  const dec = new Map(tokens.map((t) => [t.address.toLowerCase(), t.decimals] as const));
  const sym = new Map(tokens.map((t) => [t.address.toLowerCase(), t.symbol] as const));
  let pools = await discoverPools(client, cfg, tokens, longTailPairs(cfg, tokens));
  await loadStaticMetadata(client, cfg, pools);
  await syncPools(client, cfg, pools, { force: true });
  pools = pruneEmpty(pools);
  pools = filterByDepth(pools, buildEthPrices(cfg, pools), 0.2);
  const cl = pools.filter((p) => p.kind === "aero-cl");
  const byPair = new Map<string, Pool[]>();
  for (const p of pools) byPair.set(pairKey(p.token0, p.token1), [...(byPair.get(pairKey(p.token0, p.token1)) ?? []), p]);
  console.log(`pools=${pools.length} slipstream=${cl.length}; sampling for ${minutes} min`);
  const lastFee = new Map<string, number>();
  const end = Date.now() + minutes * 60_000;
  let last = 0n; let n = 0;
  while (Date.now() < end) {
    const bn = await client.getBlockNumber();
    if (bn === last) { await new Promise((r) => setTimeout(r, 400)); continue; }
    last = bn; n++;
    await syncPools(client, cfg, pools, { blockNumber: bn, force: n % 30 === 1 });
    if (syncStats.chunkFailures > 0) continue;
    const prices = buildEthPrices(cfg, pools);
    const ethUsd = 1 / (prices.get(cfg.usdc.toLowerCase()) ?? NaN);
    const opps = findOpportunities(pools, { budgetMs: 1500 });
    const bestByPool = new Map<string, number>();
    for (const o of opps) {
      const usd = toEth(prices, o.token, o.profit, dec.get(o.token.toLowerCase()) ?? 18) * ethUsd;
      for (const h of o.hops) bestByPool.set(h.pool.address, Math.max(bestByPool.get(h.pool.address) ?? 0, usd));
    }
    for (const p of cl) {
      if (!isV3(p)) continue;
      const instant = p.state.feeHistory?.[p.state.feeHistory.length - 1] ?? p.state.fee;
      const prev = lastFee.get(p.address);
      lastFee.set(p.address, instant);
      const peers = (byPair.get(pairKey(p.token0, p.token1)) ?? []).filter((q) => q !== p);
      const px = spotPrice(p);
      let bestGap = 0; let bestPeer = "";
      for (const q of peers) { const g = Math.abs(spotPrice(q) / px - 1) * 1e4; if (g > bestGap) { bestGap = g; bestPeer = `${q.dex}${isV3(q) ? "/" + q.tier : ""}`; } }
      const rec = { block: Number(bn), t: Date.now(), pool: p.address, pair: `${sym.get(p.token0.toLowerCase())}/${sym.get(p.token1.toLowerCase())}`, dex: p.dex, ts: p.state.tickSpacing, fee: instant, feeMax: p.state.fee, feeChanged: prev !== undefined && prev !== instant ? prev : null, peers: peers.length, bestGapBps: +bestGap.toFixed(1), bestPeer, bestCycleUsd: +(bestByPool.get(p.address) ?? 0).toFixed(4), roundTripFeeBps: +((poolFee(p) * 1e4) + 5).toFixed(1) };
      if (rec.feeChanged !== null || rec.bestCycleUsd >= 0.005 || n % 15 === 0) out.write(JSON.stringify(rec) + "\n");
    }
    if (n % 30 === 0) console.log(`block ${bn} sampled ${n} blocks, fee changes so far: ${fs.readFileSync(arg("out", "data/feetiming.jsonl")!, "utf8").split("\n").filter((l) => l.includes('"feeChanged":') && !l.includes('"feeChanged":null')).length}`);
  }
  out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
