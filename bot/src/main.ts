/**
 * Live searcher loop.
 *
 *   npx tsx src/main.ts --chain base --mode dry            # observe + simulate only
 *   npx tsx src/main.ts --chain base --mode live           # sign & send (needs PRIVATE_KEY, ARB_CONTRACT)
 *   --source blocks|flashblocks|logs   state trigger. `logs` = event-driven: eth_getBlockReceipts per block (or pending
 *                                     on a node that serves it), exact state from Swap/Sync/Mint/Burn logs, and an
 *                                     incremental search over the pools that changed only.
 *   --universe config|top         token universe: hand-picked config list or GeckoTerminal top-volume tokens
 *   --min-profit-usd 0.05         minimum simulated net profit to act on
 *   --top 3                       max candidates simulated per tick
 *   --v4-pools <file|glob>[,...]  opt-in: Uniswap V4 pools from PoolManager Initialize CSV(.gz) data instead of
 *                                 GeckoTerminal listings (see src/pools/v4file.ts)
 *   --active-lookback <blocks>    add every pool that swapped in the last <blocks> blocks (Swap-log discovery, see
 *                                 src/pools/activity.ts); the registry persists, so restarts only scan new blocks
 *   --registry <file>             pool registry file (default data/pool-registry-<chain>.json)
 *   --logs-rpc <url>              endpoint for the Swap-log scan (default LOGS_RPC_URL, else the first RPC)
 *   --dump-pools <file>           write every non-empty candidate pool with its depth (JSON lines) before the depth filter
 */
import "dotenv/config";
import fs from "node:fs";
import path from "node:path";
import { formatUnits, getAddress, type Address, type Hex } from "viem";
import { getChain } from "./config/chains.js";
import { makeHttpClient, makeWsClient } from "./util/client.js";
import { discoverPools, longTailPairs } from "./pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools, syncStats } from "./pools/state.js";
import { findOpportunities, type Opportunity } from "./arb/search.js";
import { findTriangles } from "./arb/triangles.js";
import { buildEthPrices, toEth } from "./arb/pricing.js";
import { filterByDepth, poolDepthEth } from "./arb/depth.js";
import { Executor } from "./exec/executor.js";
import { FlashblocksClient } from "./exec/flashblocks.js";
import { buildTokenUniverse } from "./research/tokens.js";
import { isV2, type Pool } from "./pools/types.js";
import { OP_GAS_ORACLE_ABI } from "./abi.js";
import { discoverV4Pools, isV4 } from "./pools/v4.js";
import { loadV4PoolsFromFile, type V4FileStats } from "./pools/v4file.js";
import { enumerateUniverse } from "./pools/enumerate.js";
import { classifyActivity, poolsFromRegistry, refreshRegistry, registryPath, saveRegistry, scanSwapActivity, verifyCloneFactories, type Registry } from "./pools/activity.js";
import { applyLogs, fetchBlockLogsViaReceipts, PoolIndex } from "./pools/events.js";
import { fetchTickData, refreshAeroClFees } from "./pools/state.js";
import { evalRoute } from "./arb/triangles.js";
import { CycleIndex } from "./arb/incremental.js";
import { isV3 as isV3Pool, type V3Pool } from "./pools/types.js";
import { log } from "./util/log.js";
import { createPublicClient, http } from "viem";
import { viemChain } from "./util/client.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

const chainName = arg("chain", "base")!;
const mode = arg("mode", "dry") as "dry" | "live";
const cfg = getChain(chainName);
const source = (arg("source", cfg.id === 8453 ? "flashblocks" : "blocks") ?? "blocks") as "blocks" | "flashblocks" | "logs";
const receiptsTag = (arg("receipts-tag", "latest") ?? "latest") as "latest" | "pending"; // `pending` needs a flashblocks-aware node
const universe = arg("universe", "config") as "config" | "top" | "all";
const minProfitUsd = Number(arg("min-profit-usd", "0.05"));
const topK = Number(arg("top", "3"));
const minDepthEth = Number(arg("min-depth-eth", "0.2"));
const triangles = arg("triangles", "1") !== "0";
const v4PoolsSpec = arg("v4-pools");
const activeLookback = Number(arg("active-lookback", "0"));
const registryRefreshMs = Number(arg("registry-refresh-s", "300")) * 1000;
const dumpPools = arg("dump-pools");
const contract = (process.env.ARB_CONTRACT ?? arg("contract") ?? (mode === "dry" ? getAddress("0x00000000000000000000000000000000000a4bb0") : undefined)) as Address | undefined;
/** Dry-run with no deployment: inject the compiled runtime at a placeholder address via state override. */
const codeOverride: Hex | undefined =
  mode === "dry" && !process.env.ARB_CONTRACT && cfg.id === 8453
    ? (fs.readFileSync(new URL("./exec/artifacts/ArbExecutor.base.runtime.hex", import.meta.url), "utf8").trim() as Hex)
    : undefined;
const privateKey = process.env.PRIVATE_KEY as Hex | undefined;
const preconfUrl = process.env.BASE_PRECONF_RPC_URL ?? "https://mainnet-preconf.base.org";
const flashblocksUrl = process.env.BASE_FLASHBLOCKS_WS ?? "wss://mainnet.flashblocks.base.org/ws";
const outFile = arg("out", `data/live-${chainName}.jsonl`)!;

const client = makeHttpClient(cfg);
/** State reads at the `pending` tag against the preconf endpoint reflect flashblocks (~200ms freshness). */
const preconf = createPublicClient({ chain: viemChain(cfg), transport: http(preconfUrl, { batch: { batchSize: 100, wait: 5 }, timeout: 10_000 }) });

const symbolOf = new Map<string, string>();
const decimalsOf = new Map<string, number>();
const sym = (a: Address) => symbolOf.get(a.toLowerCase()) ?? a.slice(0, 8);
const poolLabel = (p: Pool) => `${p.dex}${isV2(p) ? (p.kind === "aero-v2" && p.stable ? "(s)" : "") : `/${p.tier}`}`;
const routeLabel = (o: Opportunity) => o.hops.map((h) => `${sym(h.tokenIn)}>${sym(h.tokenOut)}@${poolLabel(h.pool)}`).join(" ");

interface Stats {
  ticks: number;
  gross: number;
  net: number;
  simulated: number;
  simOk: number;
  sent: number;
  landed: number;
  failed: number;
  profitEth: number;
  gasSpentEth: number;
  staleTicks: number;
  simOkAtBlock: number;
  droppedByFeeRefresh: number;
  logsApplied: number;
  touchedPools: number;
}
const stats: Stats = { ticks: 0, gross: 0, net: 0, simulated: 0, simOk: 0, sent: 0, landed: 0, failed: 0, profitEth: 0, gasSpentEth: 0, staleTicks: 0, simOkAtBlock: 0, droppedByFeeRefresh: 0, logsApplied: 0, touchedPools: 0 };

async function main() {
  if (mode === "live" && (!contract || !privateKey)) throw new Error("live mode needs ARB_CONTRACT and PRIVATE_KEY");
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  const out = fs.createWriteStream(outFile, { flags: "a" });

  let tokens: typeof cfg.tokens;
  let pools: Pool[];
  if (universe === "all") {
    const u = await enumerateUniverse(client, cfg, { maxPerFactory: Number(arg("max-per-factory", "20000")) });
    tokens = [...cfg.tokens, ...u.tokens.filter((t) => !cfg.tokens.some((c) => c.address.toLowerCase() === t.address.toLowerCase()))];
    pools = u.pools;
  } else {
    // a copy: tokens found later (V4 files, the activity registry) are appended to it and must not leak into cfg.tokens
    tokens = universe === "top" ? await buildTokenUniverse(client, cfg, Number(arg("pages", "5")), Number(arg("max-tokens", "200"))) : [...cfg.tokens];
    pools = await discoverPools(client, cfg, tokens, universe === "top" ? longTailPairs(cfg, tokens) : undefined);
  }
  for (const t of tokens) {
    symbolOf.set(t.address.toLowerCase(), t.symbol);
    decimalsOf.set(t.address.toLowerCase(), t.decimals);
  }
  let v4File: V4FileStats | null = null;
  if (v4PoolsSpec) {
    const r = await loadV4PoolsFromFile(client, cfg, v4PoolsSpec, tokens);
    tokens = [...tokens, ...r.tokensAdded];
    for (const t of r.tokensAdded) {
      symbolOf.set(t.address.toLowerCase(), t.symbol);
      decimalsOf.set(t.address.toLowerCase(), t.decimals);
    }
    pools.push(...r.pools);
    v4File = r.stats;
  } else if (arg("v4", "1") !== "0") pools.push(...(await discoverV4Pools(client, cfg, tokens, universe === "top" ? 3 : 2)));
  const regFile = arg("registry", registryPath(cfg))!;
  const logsUrl = arg("logs-rpc", process.env.LOGS_RPC_URL ?? cfg.rpcUrls[0])!;
  let registry: Registry | null = null;
  if (activeLookback > 0) {
    const { reg } = await refreshRegistry(client, cfg, regFile, activeLookback, logsUrl);
    registry = reg;
    const fromReg = poolsFromRegistry(reg, cfg);
    const poolKey = (p: Pool) => (isV4(p) ? p.v4.poolId : p.address).toLowerCase();
    const have = new Set(pools.map(poolKey));
    let added = 0;
    for (const p of fromReg.pools) if (!have.has(poolKey(p))) { pools.push(p); have.add(poolKey(p)); added++; }
    const known = new Set(tokens.map((t) => t.address.toLowerCase()));
    for (const t of fromReg.tokens) if (!known.has(t.address.toLowerCase())) {
      tokens.push(t);
      known.add(t.address.toLowerCase());
      symbolOf.set(t.address.toLowerCase(), t.symbol);
      decimalsOf.set(t.address.toLowerCase(), t.decimals);
    }
    log.info({ registryPools: fromReg.pools.length, addedToUniverse: added, universeBeforeFilters: pools.length }, "active pools merged");
  }
  await loadStaticMetadata(client, cfg, pools);
  // Price and depth-filter on slot0/liquidity/reserves first; tick data only for the survivors.
  const syncedAt = await syncPools(client, cfg, pools, { force: true, skipTicks: true });
  const startupSync = { startupSyncPools: syncStats.total, startupSyncStalePools: syncStats.stale, startupSyncChunkFailures: syncStats.chunkFailures };
  pools = pruneEmpty(pools);
  const v4AfterPrune = pools.filter(isV4).length;
  let prices = buildEthPrices(cfg, pools);
  if (dumpPools) {
    // every non-empty candidate with its depth, so coverage can be evaluated offline for any --min-depth-eth
    fs.mkdirSync(path.dirname(dumpPools), { recursive: true });
    fs.writeFileSync(dumpPools, pools.map((p) => JSON.stringify({ address: p.address, poolId: isV4(p) ? p.v4.poolId : undefined, dex: p.dex, kind: p.kind, token0: p.token0, token1: p.token1, tier: isV2(p) ? undefined : p.tier, depthEth: +poolDepthEth(p, prices).toPrecision(6) })).join("\n") + "\n");
    log.info({ file: dumpPools, pools: pools.length, minDepthEth }, "pool candidates written (with depth; the universe is depthEth >= minDepthEth)");
  }
  pools = filterByDepth(pools, prices, minDepthEth);
  await fetchTickData(client, cfg, pools.filter((p): p is V3Pool => isV3Pool(p)), syncedAt);
  if (v4File) log.info({ spec: v4PoolsSpec, ...v4File, ...startupSync, v4AfterPruneEmpty: v4AfterPrune, v4AfterDepthFilter: pools.filter(isV4).length, minDepthEth }, "v4 pools loaded from file");
  const poolIndex = new PoolIndex(pools);
  const cycleIndex = new CycleIndex(pools, [cfg.weth, cfg.usdc]);
  log.info({ tokens: tokens.length, pools: pools.length, cycles: cycleIndex.candidates.length, minDepthEth, source, mode, contract: contract ?? "(none)", codeOverride: !!codeOverride }, "searcher ready");

  const executor = contract
    ? new Executor({
        cfg,
        client,
        contract,
        privateKey,
        submitRpcUrls: (process.env.SUBMIT_RPC_URLS ?? "").split(",").filter(Boolean),
        bidFraction: Number(process.env.BID_FRACTION ?? "0.5"),
        maxPriorityGwei: Number(process.env.MAX_PRIORITY_GWEI ?? "0.05"),
        maxFeeGwei: Number(process.env.MAX_FEE_GWEI ?? "0.5"),
        blocksValid: Number(process.env.BLOCKS_VALID ?? "2"),
        minSimToPredictRatio: 0.8,
        codeOverride,
      })
    : null;

  if (executor) {
    // any pool pair works as a sample route for the ABI/bytecode self-check
    const a = pools[0]!;
    const b = pools.find((p) => p !== a && p.token0 === a.token0 && p.token1 === a.token1) ?? pools[1]!;
    await executor.selfCheck({ token: a.token1, hops: [{ pool: a, tokenIn: a.token1, tokenOut: a.token0, amountIn: 1n, amountOut: 1n, ticksCrossed: 0 }, { pool: b, tokenIn: b.token0, tokenOut: b.token1, amountIn: 1n, amountOut: 1n, ticksCrossed: 0 }], amountIn: 1n, amountOut: 1n, profit: 0n, gasEstimate: 0n, gapBps: 0 });
  }

  // gas price cache (refreshed every ~10s)
  let gasPriceWei = await client.getGasPrice();
  let l1FeeWei = 0n;
  const refreshGas = async () => {
    try {
      gasPriceWei = await client.getGasPrice();
      if (cfg.opStack) {
        const dummy = ("0x" + "ab".repeat(700)) as Hex;
        l1FeeWei = await client.readContract({ address: "0x420000000000000000000000000000000000000F", abi: OP_GAS_ORACLE_ABI, functionName: "getL1Fee", args: [dummy] });
      }
    } catch (e) {
      log.warn({ err: String(e).slice(0, 100) }, "gas refresh failed");
    }
  };
  await refreshGas();
  setInterval(refreshGas, 10_000).unref();

  // Live discovery: every few minutes scan the Swap logs since the registry's last block, classify new emitters, and
  // stage the ones that pass the empty/depth filters; tick() merges them into the pool set, indexes and searches.
  const staged: Pool[] = [];
  const poolKeyOf = (p: Pool) => (isV4(p) ? p.v4.poolId : p.address).toLowerCase();
  const inUniverse = new Set(pools.map(poolKeyOf));
  let regBusy = false;
  const refreshLive = async () => {
    if (!registry || regBusy) return;
    regBusy = true;
    try {
      const head = Number(await client.getBlockNumber());
      if (head <= registry.scannedTo) return;
      const from = registry.scannedTo + 1;
      const scan = await scanSwapActivity(logsUrl, from, head);
      for (const [id, key] of scan.v4Init) (registry.v4Init ??= {})[id] = key;
      const cls = await classifyActivity(client, cfg, registry, scan.activity);
      await verifyCloneFactories(client, cfg, registry);
      registry.scannedTo = head;
      saveRegistry(regFile, registry);
      const keys = cls.added.filter((k) => !inUniverse.has(k));
      if (keys.length === 0) return;
      const fresh = poolsFromRegistry(registry, cfg, keys);
      for (const t of fresh.tokens) {
        symbolOf.set(t.address.toLowerCase(), t.symbol);
        decimalsOf.set(t.address.toLowerCase(), t.decimals);
      }
      await loadStaticMetadata(client, cfg, fresh.pools);
      const at = await syncPools(client, cfg, fresh.pools, { force: true, skipTicks: true });
      let ok = pruneEmpty(fresh.pools);
      ok = filterByDepth(ok, buildEthPrices(cfg, [...pools, ...ok]), minDepthEth);
      await fetchTickData(client, cfg, ok.filter((p): p is V3Pool => isV3Pool(p)), at);
      staged.push(...ok);
      log.info({ blocks: head - from + 1, emitters: scan.activity.size, classifiedNew: cls.added.length, passedFilters: ok.length }, "live discovery");
    } catch (e) {
      log.warn({ err: String(e).slice(0, 200) }, "live discovery failed");
    } finally {
      regBusy = false;
    }
  };
  if (registry) setInterval(() => void refreshLive(), registryRefreshMs).unref();

  /** Block at which each Slipstream pool's fee was last read exactly (event mode). */
  const feeFreshAt = new Map<string, bigint>();
  let busy = false;
  let pendingTrigger: { block: bigint; index: number } | null = null;
  let lastForce = 0;
  const inFlight = new Map<string, number>(); // route key -> tick index when sent (avoid double-sending)
  /** Routes whose simulation reverted repeatedly (transfer-restricted tokens, paused pools, mispriced pools). */
  const revertCount = new Map<string, number>();
  const blacklistUntil = new Map<string, number>(); // route key or token -> tick index
  // Tokens that make our transfers fail (blocked, taxed, paused). The broader universe and triangle search route
  // through many of them, each time via a different pool combination, so strikes are counted per token and the
  // verdict is kept across restarts.
  const badTokensFile = path.resolve(`data/bad-tokens-${cfg.name}.json`);
  const tokenStrikes = new Map<string, number>();
  const badTokens = new Set<string>(((): string[] => {
    try {
      return JSON.parse(fs.readFileSync(badTokensFile, "utf8")) as string[];
    } catch {
      return [];
    }
  })());
  for (const t of badTokens) blacklistUntil.set(t, Number.MAX_SAFE_INTEGER);
  const protectedTokens = new Set([cfg.weth, cfg.usdc, ...cfg.tokens.map((t) => t.address)].map((a) => a.toLowerCase()));
  const okTokens = new Set<string>();
  if (badTokens.size > 0) log.info({ file: badTokensFile, tokens: badTokens.size }, "transfer-failing tokens loaded");
  const isBlacklisted = (routeKey: string, tokens: string[]) => {
    const now = stats.ticks;
    if ((blacklistUntil.get(routeKey) ?? -1) > now) return true;
    return tokens.some((t) => (blacklistUntil.get(t) ?? -1) > now);
  };

  async function tick(trigger: { block: bigint; index: number }) {
    if (busy) {
      pendingTrigger = trigger;
      return;
    }
    busy = true;
    try {
      const t0 = Date.now();
      stats.ticks++;
      if (staged.length > 0) {
        const add = staged.splice(0).filter((p) => !inUniverse.has(poolKeyOf(p)));
        // they were synced when discovered; bring them to this tick's block (event mode only sees their logs from now on)
        if (add.length > 0) await syncPools(client, cfg, add, { blockNumber: trigger.block, force: true });
        for (const p of add) {
          inUniverse.add(poolKeyOf(p));
          pools.push(p);
          poolIndex.add(p);
          cycleIndex.add(p);
        }
        log.info({ added: add.length, pools: pools.length }, "live-discovered pools merged");
      }
      const usePending = source === "flashblocks";
      const stateClient = usePending ? preconf : client;
      let touched: Set<string> | null = null;
      if (source === "logs") {
        // Event-driven: exact state from the block's logs; periodic full resync as a safety net.
        if (stats.ticks - lastForce > 300 || stats.ticks === 1) {
          await syncPools(client, cfg, pools, { blockNumber: trigger.block, force: true });
          lastForce = stats.ticks;
        } else {
          const logs = await fetchBlockLogsViaReceipts(client, poolIndex, receiptsTag === "pending" ? "pending" : trigger.block);
          const res = applyLogs(poolIndex, logs, trigger.block);
          if (res.dirtyTicks.size > 0) await fetchTickData(client, cfg, pools.filter((p): p is V3Pool => isV3Pool(p) && res.dirtyTicks.has(p.address.toLowerCase())), trigger.block);
          // Slipstream fees move without an event: read them for the touched pools at this block
          const touchedCl = [...res.touched].map((k) => poolIndex.byAddress.get(k)).filter((p): p is V3Pool => !!p && p.kind === "aero-cl");
          if (touchedCl.length > 0) {
            await refreshAeroClFees(client, cfg, touchedCl, trigger.block);
            for (const p of touchedCl) feeFreshAt.set(p.address.toLowerCase(), trigger.block);
          }
          touched = res.touched;
          stats.logsApplied += res.applied;
        }
      } else {
        // In flashblocks mode we read `pending` state (no block pin); in block mode pin to the block.
        await syncPools(stateClient as any, cfg, pools, usePending ? { pending: true, force: stats.ticks - lastForce > 200 } : { blockNumber: trigger.block, force: stats.ticks - lastForce > 30 });
        if (stats.ticks - lastForce > (usePending ? 200 : 30)) lastForce = stats.ticks;
      }
      const tSync = Date.now();
      // Never search on frozen state: a rejected sync (public endpoints rate-limit at a few requests per 10 s)
      // would otherwise re-emit the same stale candidates until the next successful refresh.
      if (source !== "logs" && (syncStats.chunkFailures > 0 || syncStats.stale > pools.length / 10)) {
        stats.staleTicks++;
        if (stats.staleTicks % 25 === 1) log.warn({ chunkFailures: syncStats.chunkFailures, stalePools: syncStats.stale, staleTicks: stats.staleTicks }, "state refresh rejected by RPC; skipping tick (use a dedicated node for sustained 200 ms freshness)");
        return;
      }
      if (stats.ticks % 50 === 1) prices = buildEthPrices(cfg, pools);
      const ethUsd = 1 / (prices.get(cfg.usdc.toLowerCase()) ?? NaN);
      const opps = touched
        ? [...cycleIndex.search(touched, 150), ...(triangles ? cycleIndex.searchTriangles(touched, 150) : [])].sort((a, b) => (b.profit > a.profit ? 1 : b.profit < a.profit ? -1 : 0)) // only cycles through pools that changed in this block
        : [...findOpportunities(pools), ...(triangles ? findTriangles(pools, { startTokens: new Set([cfg.weth.toLowerCase(), cfg.usdc.toLowerCase()]) }) : [])].sort((a, b) => (b.profit > a.profit ? 1 : b.profit < a.profit ? -1 : 0));
      if (touched) stats.touchedPools += touched.size;
      const tSearch = Date.now();
      stats.gross += opps.length;

      // net profit in ETH
      const scored = opps
        .map((o) => {
          const dec = decimalsOf.get(o.token.toLowerCase()) ?? 18;
          const profitEth = toEth(prices, o.token, o.profit, dec);
          const gasEth = Number(o.gasEstimate * gasPriceWei + l1FeeWei) / 1e18;
          return { o, profitEth, gasEth, netEth: profitEth - gasEth, netUsd: (profitEth - gasEth) * ethUsd };
        })
        .filter((x) => Number.isFinite(x.netEth) && x.netUsd > minProfitUsd)
        .sort((a, b) => b.netEth - a.netEth);
      stats.net += scored.length;

      // one tx per pool per tick
      const usedPools = new Set<string>();
      const candidates: typeof scored = [];
      for (const s of scored) {
        const key = s.o.hops.map((h) => h.pool.address.toLowerCase());
        if (key.some((k) => usedPools.has(k))) continue;
        key.forEach((k) => usedPools.add(k));
        candidates.push(s);
        if (candidates.length >= topK) break;
      }

      // Event mode: a candidate through a Slipstream pool whose fee was not read at this block is re-priced with the
      // exact fee first; candidates that no longer clear the threshold are dropped before any simulation.
      if (touched && candidates.length > 0) {
        const stale = new Map<string, V3Pool>();
        for (const c of candidates) for (const h of c.o.hops) if (h.pool.kind === "aero-cl" && feeFreshAt.get(h.pool.address.toLowerCase()) !== trigger.block) stale.set(h.pool.address.toLowerCase(), h.pool as V3Pool);
        if (stale.size > 0) {
          await refreshAeroClFees(client, cfg, [...stale.values()], trigger.block);
          for (const k of stale.keys()) feeFreshAt.set(k, trigger.block);
          for (let i = candidates.length - 1; i >= 0; i--) {
            const c = candidates[i]!;
            if (!c.o.hops.some((h) => stale.has(h.pool.address.toLowerCase()))) continue;
            const ev = evalRoute(c.o.hops.map((h) => ({ pool: h.pool, tokenIn: h.tokenIn, tokenOut: h.tokenOut })), c.o.amountIn);
            const profit = ev.valid ? ev.amountOut - c.o.amountIn : -1n;
            const profitEth = profit > 0n ? toEth(prices, c.o.token, profit, decimalsOf.get(c.o.token.toLowerCase()) ?? 18) : NaN;
            const netUsd = (profitEth - c.gasEth) * ethUsd;
            if (!(netUsd > minProfitUsd)) {
              candidates.splice(i, 1);
              stats.droppedByFeeRefresh++;
              continue;
            }
            c.o = { ...c.o, hops: ev.hops, amountOut: ev.amountOut, profit };
            c.profitEth = profitEth;
            c.netEth = profitEth - c.gasEth;
            c.netUsd = netUsd;
          }
        }
      }

      for (const c of candidates) {
        const rec: any = {
          t: new Date().toISOString(),
          block: Number(trigger.block),
          fb: trigger.index,
          route: routeLabel(c.o),
          pools: c.o.hops.map((h) => h.pool.address),
          token: sym(c.o.token),
          amountIn: formatUnits(c.o.amountIn, decimalsOf.get(c.o.token.toLowerCase()) ?? 18),
          predictedProfitUsd: +(c.profitEth * ethUsd).toFixed(4),
          gasUsd: +(c.gasEth * ethUsd).toFixed(4),
          netUsd: +c.netUsd.toFixed(4),
          gapBps: +c.o.gapBps.toFixed(1),
        };
        if (!executor) {
          log.info(rec, "opportunity (no contract configured; not simulated)");
          out.write(JSON.stringify(rec) + "\n");
          continue;
        }
        const routeKey = rec.pools.join("|");
        const routeTokens = c.o.hops.map((h) => h.tokenIn.toLowerCase());
        if (isBlacklisted(routeKey, routeTokens)) continue;
        if ((inFlight.get(routeKey) ?? -10) > stats.ticks - 3) continue; // sent recently, wait for outcome
        stats.simulated++;
        const minProfit = 1n; // the contract enforces > 0; we decide on simulated numbers below
        if (source === "logs" && touched) {
          // Event mode: also simulate on exactly the block the state came from. This separates "the opportunity was real
          // in our state" from "it was still there when we looked again" (a load-balanced RPC can answer `latest` from
          // a node a block behind or ahead).
          const pinned = await executor.simulateWith(client, c.o, minProfit, trigger.block);
          rec.simAtBlock = pinned.ok ? { profitUsd: +(toEth(prices, c.o.token, pinned.profit!, decimalsOf.get(c.o.token.toLowerCase()) ?? 18) * ethUsd).toFixed(4), ms: pinned.latencyMs } : { error: pinned.error, ms: pinned.latencyMs };
          if (pinned.ok) {
            stats.simOkAtBlock++;
            for (const t of routeTokens) okTokens.add(t);
          }
        }
        let sim = await executor.simulate(c.o, minProfit, usePending ? "pending" : "latest");
        rec.sim = sim.ok ? { profitUsd: +(toEth(prices, c.o.token, sim.profit!, decimalsOf.get(c.o.token.toLowerCase()) ?? 18) * ethUsd).toFixed(4), gas: Number(sim.gasUsed), ms: sim.latencyMs } : { error: sim.error, ms: sim.latencyMs };
        if (!sim.ok && usePending && /unknown reason/.test(sim.error ?? "")) {
          // Dataless revert at `pending` on the preconf endpoint: cross-check at `latest` on the main RPC to separate
          // an endpoint artifact (pending block being rebuilt) from a real revert.
          const again = await executor.simulateWith(client, c.o, minProfit, "latest");
          rec.simLatest = again.ok ? { profitUsd: +(toEth(prices, c.o.token, again.profit!, decimalsOf.get(c.o.token.toLowerCase()) ?? 18) * ethUsd).toFixed(4), ms: again.latencyMs } : { error: again.error, ms: again.latencyMs };
          if (again.ok) sim = again;
        }
        if (sim.ok) for (const t of routeTokens) okTokens.add(t);
        if (!sim.ok && /TransferFailed/.test(sim.error ?? "")) {
          // Only a non-base token can be the culprit. Blame is split between the route's suspects (a triangle through a
          // good token and a blocked one must not condemn the good one), and a token that ever simulated fine, or is
          // one of the hand-picked config tokens, is never parked. Two full strikes park a token.
          const suspects = routeTokens.filter((t) => !protectedTokens.has(t) && !okTokens.has(t) && !badTokens.has(t));
          for (const t of suspects) {
            const k = (tokenStrikes.get(t) ?? 0) + 1 / suspects.length;
            tokenStrikes.set(t, k);
            if (k >= 2) {
              badTokens.add(t);
              blacklistUntil.set(t, Number.MAX_SAFE_INTEGER);
              try {
                fs.writeFileSync(badTokensFile, JSON.stringify([...badTokens]));
              } catch {}
              log.info({ token: t, symbol: sym(t as Address), strikes: +k.toFixed(2) }, "token parked: transfers fail");
            }
          }
        }
        if (!sim.ok) {
          const n = (revertCount.get(routeKey) ?? 0) + 1;
          revertCount.set(routeKey, n);
          // Three strikes: park the route for ~10 minutes of ticks. A dataless revert is almost always a token that
          // blocks contract transfers; park the non-base token too so its other routes stop wasting simulations.
          if (n >= 3) {
            blacklistUntil.set(routeKey, stats.ticks + 3000);
            if (/unknown reason|0x$/.test(sim.error ?? "")) {
              for (const t of routeTokens) if (t !== cfg.weth.toLowerCase() && t !== cfg.usdc.toLowerCase()) blacklistUntil.set(t, stats.ticks + 3000);
            }
            rec.blacklisted = true;
          }
          log.info(rec, "simulation reverted");
          out.write(JSON.stringify(rec) + "\n");
          continue;
        }
        revertCount.delete(routeKey);
        stats.simOk++;
        const simProfitEth = toEth(prices, c.o.token, sim.profit!, decimalsOf.get(c.o.token.toLowerCase()) ?? 18);
        const gasUsed = sim.gasUsed && sim.gasUsed > 0n ? sim.gasUsed : c.o.gasEstimate;
        const simGasEth = Number(gasUsed * gasPriceWei + l1FeeWei) / 1e18;
        const simNetEth = simProfitEth - simGasEth;
        rec.simNetUsd = +(simNetEth * ethUsd).toFixed(4);
        if (simNetEth * ethUsd < minProfitUsd) {
          log.info(rec, "simulated net below threshold");
          out.write(JSON.stringify(rec) + "\n");
          continue;
        }
        if (mode !== "live") {
          log.info(rec, "DRY-RUN: would send");
          out.write(JSON.stringify(rec) + "\n");
          continue;
        }
        try {
          const netWei = BigInt(Math.floor(simNetEth * 1e18));
          const sent = await executor.send(c.o, sim.profit! / 2n, sim, netWei, trigger.block);
          inFlight.set(routeKey, stats.ticks);
          stats.sent++;
          rec.tx = sent.hash;
          rec.priorityGwei = sent.priorityFeeGwei;
          log.info(rec, "SENT");
          out.write(JSON.stringify(rec) + "\n");
          // async receipt tracking
          client
            .waitForTransactionReceipt({ hash: sent.hash, timeout: 60_000 })
            .then((r) => {
              const gasEth = Number(r.gasUsed * r.effectiveGasPrice) / 1e18;
              stats.gasSpentEth += gasEth;
              if (r.status === "success") {
                stats.landed++;
                stats.profitEth += simProfitEth;
                log.info({ hash: sent.hash, block: Number(r.blockNumber), gasUsd: +(gasEth * ethUsd).toFixed(4) }, "LANDED");
              } else {
                stats.failed++;
                log.warn({ hash: sent.hash, block: Number(r.blockNumber), gasUsd: +(gasEth * ethUsd).toFixed(4) }, "REVERTED on-chain (someone was faster)");
              }
              out.write(JSON.stringify({ t: new Date().toISOString(), tx: sent.hash, status: r.status, block: Number(r.blockNumber), gasUsd: +(gasEth * ethUsd).toFixed(4) }) + "\n");
            })
            .catch((e) => log.warn({ hash: sent.hash, err: String(e).slice(0, 100) }, "receipt wait failed (dropped or expired)"));
        } catch (e) {
          log.error({ err: String(e).slice(0, 200) }, "send failed");
        }
      }
      const tEnd = Date.now();
      if (stats.ticks % (usePending ? 55 : 10) === 0) {
        log.info({ ...stats, block: Number(trigger.block), fb: trigger.index, syncMs: tSync - t0, searchMs: tSearch - tSync, totalMs: tEnd - t0, pools: pools.length }, "heartbeat");
      }
    } catch (e) {
      log.error({ err: String(e).slice(0, 300) }, "tick failed");
    } finally {
      busy = false;
      if (pendingTrigger) {
        const p = pendingTrigger;
        pendingTrigger = null;
        void tick(p);
      }
    }
  }

  if (source === "logs" && receiptsTag === "pending") {
    // A flashblocks-aware node serves pending receipts; poll it at the flashblock cadence.
    let lastSig = "";
    setInterval(async () => {
      try {
        const bn = await client.getBlockNumber();
        void tick({ block: bn + 1n, index: 0 });
      } catch {}
    }, 200).unref();
    void lastSig;
  } else if (source === "flashblocks") {
    const fb = new FlashblocksClient(flashblocksUrl);
    fb.on("flashblock", (f) => void tick({ block: f.blockNumber, index: f.index }));
    fb.start();
  } else {
    const ws = makeWsClient(cfg);
    if (ws) {
      ws.watchBlockNumber({ onBlockNumber: (bn) => void tick({ block: bn, index: 0 }), emitMissed: false });
      log.info("subscribed to newHeads via websocket");
    } else {
      let last = 0n;
      const everyMs = Math.max(150, cfg.blockTimeMs / 4);
      setInterval(async () => {
        try {
          const bn = await client.getBlockNumber();
          if (bn !== last) {
            last = bn;
            void tick({ block: bn, index: 0 });
          }
        } catch (e) {
          log.warn({ err: String(e).slice(0, 200) }, "block-number poll failed");
        }
      }, everyMs);
      log.info({ everyMs }, "polling eth_blockNumber over HTTP (no websocket)");
    }
  }

  process.on("SIGINT", () => {
    log.info(stats, "shutting down");
    out.end();
    process.exit(0);
  });
}

main().catch((e) => {
  log.error(e);
  process.exit(1);
});
