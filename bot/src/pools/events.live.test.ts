/**
 * Exactness of the event-driven state engine: state after applying block N's logs to the multicall state of block N-1
 * must equal the multicall state at block N for every pool the logs touched (V2 reserves, V3/V4 sqrtPrice, liquidity,
 * tick). Run: npx tsx --test src/pools/events.live.test.ts
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { BASE } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { discoverPools } from "./discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools } from "./state.js";
import { discoverV4Pools } from "./v4.js";
import { isV2, isV3, type Pool } from "./types.js";
import { applyLogs, fetchBlockLogs, fetchBlockLogsViaReceipts, PoolIndex } from "./events.js";

const snapshot = (p: Pool) => (isV2(p) ? `${p.reserve0}/${p.reserve1}` : `${p.state.sqrtPriceX96}/${p.state.liquidity}/${p.state.tick}${isV3(p) && (p as any).v4 ? "/" + p.state.feeByDir?.zeroForOne + "/" + p.state.feeByDir?.oneForZero : ""}`);

test("logs reproduce multicall state exactly", async () => {
  const client = makeHttpClient(BASE);
  let pools = await discoverPools(client, BASE);
  pools.push(...(await discoverV4Pools(client, BASE, BASE.tokens, 2)));
  await loadStaticMetadata(client, BASE, pools);
  const start = (await client.getBlockNumber()) - 3n;
  await syncPools(client, BASE, pools, { force: true, blockNumber: start });
  pools = pruneEmpty(pools);
  const index = new PoolIndex(pools);
  let checked = 0, touchedTotal = 0, mismatches: string[] = [];
  for (let b = start + 1n; b <= start + 3n; b++) {
    const t0 = Date.now();
    const logs = await fetchBlockLogsViaReceipts(client, index, b);
    const tLogs = Date.now() - t0;
    if (b === start + 1n) {
      const t1 = Date.now();
      const viaFilter = await fetchBlockLogs(client, index, b);
      console.log(`fetch benchmark: getBlockReceipts ${tLogs}ms (${logs.length} tracked logs) vs getLogs(address filter) ${Date.now() - t1}ms (${viaFilter.length})`);
    }
    const res = applyLogs(index, logs, b);
    touchedTotal += res.touched.size;
    const derived = new Map([...res.touched].map((k) => [k, snapshot(pools.find((p) => p.address.toLowerCase() === k)!)]));
    // ground truth
    const truth = pools.map((p) => ({ ...p, state: isV3(p) ? { ...p.state, bitmap: new Map(p.state.bitmap), ticks: new Map(p.state.ticks) } : undefined })) as Pool[];
    await syncPools(client, BASE, truth, { blockNumber: b });
    for (const [k, snap] of derived) {
      const t = truth.find((p) => p.address.toLowerCase() === k)!;
      checked++;
      if (snapshot(t) !== snap) mismatches.push(`block ${b} ${t.dex} ${t.address}: derived=${snap} truth=${snapshot(t)}`);
    }
    console.log(`block ${b}: ${logs.length} logs in ${tLogs}ms, applied=${res.applied} ignored=${res.ignored} touched=${res.touched.size} dirtyTicks=${res.dirtyTicks.size}`);
  }
  console.log(`checked ${checked} touched-pool states over 3 blocks (${touchedTotal} touches); mismatches=${mismatches.length}`);
  for (const m of mismatches.slice(0, 10)) console.log("  MISMATCH", m);
  assert.ok(checked > 0, "at least one tracked pool must have traded");
  assert.equal(mismatches.length, 0);
});
