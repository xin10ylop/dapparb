/**
 * Empirical arbitrage scanner. Discovers every pool for the configured token universe, then for N blocks
 * re-syncs state, runs the cycle optimizer, prices gas, and records every gross- and net-profitable
 * opportunity. Ends with a distribution summary and a persistence analysis (an "opportunity" that survives
 * many blocks is almost always a broken/taxed token or a stale pool, not free money).
 *
 * Usage: npx tsx src/research/scan.ts --chain base --blocks 60 [--out data/scan-base.jsonl]
 */
import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import { formatUnits, type Address } from "viem";
import { getChain } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools } from "../pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools } from "../pools/state.js";
import { findOpportunities, type Opportunity } from "../arb/search.js";
import { findTriangles } from "../arb/triangles.js";
import { buildEthPrices, toEth } from "../arb/pricing.js";
import { isV2, type Pool } from "../pools/types.js";
import { log } from "../util/log.js";
import { OP_GAS_ORACLE_ABI } from "../abi.js";
import { buildTokenUniverse } from "./tokens.js";
import { filterByDepth } from "../arb/depth.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

const chainName = arg("chain", "base")!;
const blocks = Number(arg("blocks", "30"));
const outFile = arg("out", `data/scan-${chainName}.jsonl`)!;
const triangles = arg("triangles", "1") !== "0";
const universe = arg("universe", "config") as "config" | "top";
const minDepthEth = Number(arg("min-depth-eth", "0.2"));
const cfg = getChain(chainName);
const client = makeHttpClient(cfg);

const decimalsOf = new Map(cfg.tokens.map((t) => [t.address.toLowerCase(), t.decimals] as const));
const symbolOf = new Map(cfg.tokens.map((t) => [t.address.toLowerCase(), t.symbol] as const));
const sym = (a: Address) => symbolOf.get(a.toLowerCase()) ?? a.slice(0, 8);
const poolLabel = (p: Pool) => `${p.dex}${isV2(p) ? (p.kind === "aero-v2" && p.stable ? "(s)" : "") : `/${p.tier}`}`;

interface Row {
  block: number;
  key: string; // pair + buy pool + sell pool
  token: string;
  route: string;
  amountIn: string;
  profitToken: string;
  profitEth: number;
  gasEth: number;
  netEth: number;
  gapBps: number;
  gas: number;
}

async function gasCostEth(gasUnits: bigint): Promise<{ gasEth: number; gasPriceGwei: number }> {
  const gasPrice = await client.getGasPrice();
  let l1 = 0n;
  if (cfg.opStack) {
    try {
      // ~700 bytes of calldata for a 2-hop route
      const dummy = ("0x" + "ab".repeat(700)) as `0x${string}`;
      l1 = await client.readContract({ address: "0x420000000000000000000000000000000000000F", abi: OP_GAS_ORACLE_ABI, functionName: "getL1Fee", args: [dummy] });
    } catch {
      l1 = 0n;
    }
  }
  const wei = gasUnits * gasPrice + l1;
  return { gasEth: Number(wei) / 1e18, gasPriceGwei: Number(gasPrice) / 1e9 };
}

async function main() {
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  const out = fs.createWriteStream(outFile, { flags: "a" });
  log.info({ chain: cfg.name, tokens: cfg.tokens.length, dexes: cfg.dexes.length }, "discovering pools");
  const tokens = universe === "top" ? await buildTokenUniverse(client, cfg, Number(arg("pages", "5")), Number(arg("max-tokens", "200"))) : cfg.tokens;
  for (const t of tokens) {
    decimalsOf.set(t.address.toLowerCase(), t.decimals);
    symbolOf.set(t.address.toLowerCase(), t.symbol);
  }
  let pools = await discoverPools(client, cfg, tokens);
  await loadStaticMetadata(client, cfg, pools);
  await syncPools(client, cfg, pools, { force: true });
  pools = pruneEmpty(pools);
  pools = filterByDepth(pools, buildEthPrices(cfg, pools), minDepthEth);
  const byKind: Record<string, number> = {};
  for (const p of pools) byKind[p.dex] = (byKind[p.dex] ?? 0) + 1;
  log.info({ live: pools.length, byDex: byKind }, "live pools");

  const rows: Row[] = [];
  const seenBlocks = new Set<number>();
  let lastBlock = 0n;
  let iter = 0;
  const t0 = Date.now();
  while (seenBlocks.size < blocks) {
    const bn = await client.getBlockNumber();
    if (bn === lastBlock) {
      await new Promise((r) => setTimeout(r, Math.max(100, cfg.blockTimeMs / 4)));
      continue;
    }
    lastBlock = bn;
    iter++;
    const tSync = Date.now();
    await syncPools(client, cfg, pools, { blockNumber: bn, force: iter % 15 === 1 });
    const tSearch = Date.now();
    const prices = buildEthPrices(cfg, pools);
    const ethUsd = 1 / (prices.get(cfg.usdc.toLowerCase()) ?? NaN);
    const opps = [...findOpportunities(pools), ...(triangles ? findTriangles(pools, { startTokens: new Set([cfg.weth.toLowerCase(), cfg.usdc.toLowerCase()]) }) : [])].sort((a, b) => (b.profit > a.profit ? 1 : b.profit < a.profit ? -1 : 0));
    const tDone = Date.now();
    const { gasEth, gasPriceGwei } = await gasCostEth(250_000n);
    seenBlocks.add(Number(bn));

    const blockRows: Row[] = [];
    for (const o of opps) {
      const dec = decimalsOf.get(o.token.toLowerCase()) ?? 18;
      const profitEth = toEth(prices, o.token, o.profit, dec);
      const g = (Number(o.gasEstimate) / 250_000) * gasEth;
      blockRows.push({
        block: Number(bn),
        key: o.hops.map((h) => `${sym(h.tokenIn)}>${sym(h.tokenOut)}@${poolLabel(h.pool)}`).join(" "),
        token: sym(o.token),
        route: o.hops.map((h) => `${poolLabel(h.pool)}:${h.pool.address}`).join(" -> "),
        amountIn: formatUnits(o.amountIn, dec),
        profitToken: formatUnits(o.profit, dec),
        profitEth,
        gasEth: g,
        netEth: profitEth - g,
        gapBps: Math.round(o.gapBps * 10) / 10,
        gas: Number(o.gasEstimate),
      });
    }
    rows.push(...blockRows);
    for (const r of blockRows) out.write(JSON.stringify(r) + "\n");
    const net = blockRows.filter((r) => r.netEth > 0);
    const top = blockRows.slice(0, 5).map((r) => `${r.key} in=${Number(r.amountIn).toPrecision(4)} ${r.token} gap=${r.gapBps}bps profit=$${(r.profitEth * ethUsd).toFixed(3)} net=$${(r.netEth * ethUsd).toFixed(3)}`);
    log.info(
      { block: Number(bn), gross: blockRows.length, net: net.length, sumNetUsd: +(net.reduce((s, r) => s + r.netEth, 0) * ethUsd).toFixed(3), gasPriceGwei, txCostUsd: +(gasEth * ethUsd).toFixed(4), syncMs: tSearch - tSync, searchMs: tDone - tSearch },
      "block scanned",
    );
    for (const t of top) log.info("  " + t);
  }
  out.end();

  // ---- Summary ----
  const prices = buildEthPrices(cfg, pools);
  const ethUsd = 1 / (prices.get(cfg.usdc.toLowerCase()) ?? NaN);
  const nBlocks = seenBlocks.size;
  const net = rows.filter((r) => r.netEth > 0);
  const byKey = new Map<string, Row[]>();
  for (const r of net) byKey.set(r.key, [...(byKey.get(r.key) ?? []), r]);
  const persistent = [...byKey.entries()].filter(([, rs]) => rs.length >= Math.max(3, nBlocks * 0.5));
  const transient = [...byKey.entries()].filter(([, rs]) => rs.length < Math.max(3, nBlocks * 0.5));
  const sumUsd = (rs: Row[]) => rs.reduce((s, r) => s + r.netEth, 0) * ethUsd;
  console.log("\n================ SCAN SUMMARY ================");
  console.log(`chain=${cfg.name} blocks=${nBlocks} elapsed=${((Date.now() - t0) / 1000).toFixed(0)}s pools=${pools.length} ethUsd=${ethUsd.toFixed(0)}`);
  console.log(`gross-positive cycles: ${rows.length}  net-positive (after gas): ${net.length}`);
  console.log(`distinct net-positive routes: ${byKey.size}  of which PERSISTENT (>=50% of blocks; suspect): ${persistent.length}`);
  console.log(`upper-bound net USD if ALL transient opps were captured: $${sumUsd(transient.flatMap(([, rs]) => rs)).toFixed(2)} over ${nBlocks} blocks`);
  console.log(`upper-bound net USD from persistent (suspect) routes:      $${sumUsd(persistent.flatMap(([, rs]) => rs)).toFixed(2)}`);
  const buckets = [0.001, 0.01, 0.1, 1, 10, 100];
  const dist = buckets.map((b, i) => {
    const lo = i === 0 ? 0 : buckets[i - 1]!;
    return `$${lo}-${b}: ${net.filter((r) => r.netEth * ethUsd > lo && r.netEth * ethUsd <= b).length}`;
  });
  console.log(`net profit distribution (USD): ${dist.join(" | ")} | >$100: ${net.filter((r) => r.netEth * ethUsd > 100).length}`);
  console.log("\nTop transient routes by total net USD:");
  for (const [k, rs] of transient.sort((a, b) => sumUsd(b[1]) - sumUsd(a[1])).slice(0, 15)) console.log(`  ${k}: blocks=${rs.length} total=$${sumUsd(rs).toFixed(3)} max=$${(Math.max(...rs.map((r) => r.netEth)) * ethUsd).toFixed(3)}`);
  console.log("\nPersistent routes (verify manually; usually fee-on-transfer tokens, paused pools or stale data):");
  for (const [k, rs] of persistent.sort((a, b) => sumUsd(b[1]) - sumUsd(a[1])).slice(0, 15)) console.log(`  ${k}: blocks=${rs.length}/${nBlocks} avg=$${(sumUsd(rs) / rs.length).toFixed(3)} route=${rs[0]!.route}`);
  process.exit(0);
}

main().catch((e) => {
  log.error(e);
  process.exit(1);
});
