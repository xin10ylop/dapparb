/** Benchmark: full search vs incremental search on real blocks. npx tsx src/arb/incremental.bench.ts */
import { BASE } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools, longTailPairs } from "../pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools } from "../pools/state.js";
import { discoverV4Pools } from "../pools/v4.js";
import { buildTokenUniverse } from "../research/tokens.js";
import { filterByDepth } from "./depth.js";
import { buildEthPrices } from "./pricing.js";
import { findOpportunities } from "./search.js";
import { CycleIndex } from "./incremental.js";
import { applyLogs, fetchBlockLogsViaReceipts, PoolIndex } from "../pools/events.js";

const client = makeHttpClient(BASE);
const tokens = await buildTokenUniverse(client, BASE, 4, 250);
let pools = await discoverPools(client, BASE, tokens, longTailPairs(BASE, tokens));
pools.push(...(await discoverV4Pools(client, BASE, tokens, 2)));
await loadStaticMetadata(client, BASE, pools);
const start = (await client.getBlockNumber()) - 6n;
await syncPools(client, BASE, pools, { force: true, blockNumber: start });
pools = pruneEmpty(pools);
pools = filterByDepth(pools, buildEthPrices(BASE, pools), 0.2);
const pi = new PoolIndex(pools);
const ci = new CycleIndex(pools);
console.log(`pools=${pools.length} cycle candidates=${ci.candidates.length}`);
let fullMs = 0, incMs = 0, fetchMs = 0, touchedSum = 0, n = 0, agree = 0, disagree = 0;
for (let b = start + 1n; b <= start + 6n; b++) {
  const t0 = process.hrtime.bigint();
  const logs = await fetchBlockLogsViaReceipts(client, pi, b);
  const t1 = process.hrtime.bigint();
  const res = applyLogs(pi, logs, b);
  const t2 = process.hrtime.bigint();
  const inc = ci.search(res.touched, 5000);
  const t3 = process.hrtime.bigint();
  const full = findOpportunities(pools, { budgetMs: 20000 });
  const t4 = process.hrtime.bigint();
  fetchMs += Number(t1 - t0) / 1e6; incMs += Number(t3 - t2) / 1e6; fullMs += Number(t4 - t3) / 1e6; touchedSum += res.touched.size; n++;
  // every incremental result must also be in the full result (same pools, same profit)
  const key = (o: any) => o.hops.map((h: any) => h.pool.address).join(">") + ":" + o.token;
  const fullKeys = new Map(full.map((o) => [key(o), o.profit]));
  for (const o of inc) { if (fullKeys.get(key(o)) === o.profit) agree++; else disagree++; }
  console.log(`block ${b}: logs=${logs.length} touched=${res.touched.size} | fetch ${(Number(t1 - t0) / 1e6).toFixed(0)}ms apply ${(Number(t2 - t1) / 1e6).toFixed(2)}ms incremental ${(Number(t3 - t2) / 1e6).toFixed(2)}ms (${inc.length} opps) vs full ${(Number(t4 - t3) / 1e6).toFixed(1)}ms (${full.length} opps)`);
}
console.log(`avg per block: fetch ${(fetchMs / n).toFixed(0)}ms, incremental search ${(incMs / n).toFixed(2)}ms over ${(touchedSum / n).toFixed(1)} touched pools, full search ${(fullMs / n).toFixed(1)}ms → speedup ${(fullMs / incMs).toFixed(0)}x; incremental results consistent with full: ${agree}/${agree + disagree}`);
process.exit(0);
