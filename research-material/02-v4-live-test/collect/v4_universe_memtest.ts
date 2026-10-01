/**
 * Diagnostic for V4UNIVERSE (not a data collector): heap retained by the engine's V4 file parser (loadV4PoolsFromFile step 1)
 * with and without the viem isAddressCache flat-key patch used in v4_universe_snapshot.ts. No RPC call is made: the stub
 * client throws at the first getBlockNumber (right after parsing). Prints heap/RSS after a forced GC and the size of viem's
 * isAddressCache in the CJS build (the one the engine modules use under tsx here) and in the ESM build.
 *
 * Run (from /home/user/dapparb/bot), output kept in collect/v4_universe_memtest.log:
 *   NODE_OPTIONS="--max-old-space-size=4000 --expose-gc" npx tsx ../research-material/02-v4-live-test/collect/v4_universe_memtest.ts <spec>
 *   PATCH=1 NODE_OPTIONS=... (same)          # with the flat-key patch
 */
import { createRequire } from "node:module";
import { getChain } from "../../../bot/src/config/chains.js";
import { loadV4PoolsFromFile } from "../../../bot/src/pools/v4file.js";
import { isAddressCache as esmCache } from "../../../bot/node_modules/viem/_esm/utils/address/isAddress.js";

const isAddressCache = createRequire("/home/user/dapparb/bot/package.json")("/home/user/dapparb/bot/node_modules/viem/_cjs/utils/address/isAddress.js").isAddressCache;
if (process.env.PATCH) {
  const flat = (k: any) => (typeof k === "string" ? Buffer.from(k, "latin1").toString("latin1") : k);
  for (const cache of [isAddressCache, esmCache] as any[]) {
    const proto: any = Object.getPrototypeOf(cache);
    cache.get = function (k: any) { return proto.get.call(this, flat(k)); };
    cache.set = function (k: any, v: any) { return proto.set.call(this, flat(k), v); };
  }
}
const cfg = getChain("base");
const spec = process.argv[2]!;
const client: any = { getBlockNumber: async () => { throw new Error("STOP_AFTER_PARSE"); } };
(async () => {
  try {
    await loadV4PoolsFromFile(client, cfg, spec, cfg.tokens);
  } catch (e) {
    if (!String(e).includes("STOP_AFTER_PARSE")) throw e;
  }
  (globalThis as any).gc?.();
  const m = process.memoryUsage();
  console.log(JSON.stringify({ t: new Date().toISOString(), patch: !!process.env.PATCH, spec, rssMb: m.rss >> 20, heapUsedMbAfterGc: m.heapUsed >> 20, isAddressCacheSizeCjs: isAddressCache.size, isAddressCacheSizeEsm: esmCache.size }));
})();
