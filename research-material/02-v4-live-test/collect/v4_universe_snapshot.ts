/**
 * V4UNIVERSE collector: per-pool reconstruction of the engine universe of the valid V4LIVE run (run-times.json).
 *
 * Reproduces the engine's universe-building sequence from bot/src/main.ts for the flags of that run
 * (--universe all --max-per-factory 6000 --v4-pools <spec> --min-depth-eth 0.1):
 *   enumerateUniverse(maxPerFactory) -> tokens = cfg.tokens + enumerated -> loadV4PoolsFromFile(spec, tokens)
 *   -> tokens += tokensAdded -> loadStaticMetadata -> syncPools(force) -> pruneEmpty -> buildEthPrices -> filterByDepth
 * with every on-chain read pinned to ONE block (PIN, default 52015721 = `liquidityHeadAfter` of the run's
 * `v4 pools loaded from file` record, i.e. inside the run window), and dumps every pool after pruneEmpty (same columns as
 * ../04-shallow-pools/pools-prefilter.csv.gz), the pools removed by pruneEmpty, the engine price map and the loader counts.
 *
 * Engine modules are imported unchanged by relative path (bot/src is not modified). Interpositions:
 *   - the engine's own viem client (makeHttpClient) is built with rpcUrls = [--rpc] (default blastapi, which serves archive
 *     eth_call) instead of the four-endpoint fallback, because the reads are at a historical block;
 *   - a Proxy around that client adds blockNumber=PIN to every multicall/readContract that names no block (the engine's
 *     enumerate / v4-file liquidity+metadata / static-metadata reads default to `latest`), returns PIN from getBlockNumber
 *     (so the loader's liquidityHeadBefore/After are PIN), retries transient RPC failures with exponential backoff before the
 *     engine's own chunk bisection sees the error, and records per-call successes/failures;
 *   - syncPools(force, blockNumber=PIN) is called on consecutive batches of --sync-batch pools instead of once on all pools
 *     (per-pool reads are independent and all at PIN; bounds memory and makes the stage resumable). syncStats are summed.
 * globalThis.fetch is wrapped only to add a browser-like User-Agent.
 *
 * Resumable: checkpoints in collect/work/v4universe/ (enumeration, v4 load + static metadata, each sync batch); a re-run with
 * the same pin/spec/flags continues from the last checkpoint.
 *
 * Run (from /home/user/dapparb/bot):
 *   LOG_JSON=1 npx tsx ../research-material/02-v4-live-test/collect/v4_universe_snapshot.ts [--pin <block>] [--out <dir>]
 *   smoke: ... --max-per-factory 25 --spec ../research-material/02-v4-live-test/initialize-topup.csv.gz --out <scratch> \
 *          --work <scratch>/work --sentinel none
 */
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import crypto from "node:crypto";
import { execSync } from "node:child_process";
import { createRequire } from "node:module";
import { parseAbi, type Address } from "../../../bot/node_modules/viem/_esm/index.js";
import { getChain } from "../../../bot/src/config/chains.js";
import { makeHttpClient } from "../../../bot/src/util/client.js";
import { enumerateUniverse } from "../../../bot/src/pools/enumerate.js";
import { isV4 } from "../../../bot/src/pools/v4.js";
import { loadV4PoolsFromFile, expandV4PoolFiles } from "../../../bot/src/pools/v4file.js";
import { loadStaticMetadata, pruneEmpty, syncPools, syncStats } from "../../../bot/src/pools/state.js";
import { buildEthPrices, sideAmounts, MIN_ANCHOR_ETH } from "../../../bot/src/arb/pricing.js";
import { filterByDepth, poolDepthEth } from "../../../bot/src/arb/depth.js";
import { CycleIndex } from "../../../bot/src/arb/incremental.js";
import { multicallChunked } from "../../../bot/src/util/multicall.js";
import { isV2, isV3, type Pool } from "../../../bot/src/pools/types.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

const RM = "/home/user/dapparb/research-material";
const RUN_TIMES = path.join(RM, "02-v4-live-test/run-times.json");
const runTimes = JSON.parse(fs.readFileSync(RUN_TIMES, "utf8"));
const OUT = arg("out", path.join(RM, "02-v4-live-test"))!;
const WORK = arg("work", path.join(RM, "02-v4-live-test/collect/work/v4universe"))!;
const PREFIX = arg("prefix", "v4universe-")!;
const SENT = path.join(RM, ".sentinels");
const NAME = arg("sentinel", "V4UNIVERSE")!;
const SPEC = arg("spec", runTimes.v4_pools_spec as string)!;
const MAX_PER_FACTORY = Number(arg("max-per-factory", "6000"));
const MIN_DEPTH_ETH = Number(arg("min-depth-eth", "0.1"));
const PIN_ARG = BigInt(arg("pin", "52015721")!);
const RPC = arg("rpc", "https://base-mainnet.public.blastapi.io")!;
const SYNC_BATCH = Number(arg("sync-batch", "8000"));
const UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";
const MAXB = 85 * 1024 * 1024;
const MAX_FAILED_KEPT = 200_000;
const nowIso = () => new Date().toISOString();
let peakRssMb = 0;
const rssMb = () => {
  const r = Math.round(process.memoryUsage().rss / 1048576);
  if (r > peakRssMb) peakRssMb = r;
  return r;
};
const say = (msg: string, o: object = {}) => console.log(JSON.stringify({ t: nowIso(), msg, rssMb: rssMb(), ...o }));

const cfg0 = getChain("base");
const cfg = { ...cfg0, rpcUrls: [RPC] };
const base = makeHttpClient(cfg as any);

// ---------------------------------------------------------------- viem isAddress cache: store flat keys
// viem's isAddress memoises results in an LruMap(8192) keyed by `${address}.${strict}`. The loader passes address strings that
// are slices of 1 MB decompressed CSV chunks (poolIdOf(key) on the raw row fields), so each cached key keeps its whole chunk alive:
// up to 8192 chunks (collect/v4_universe_memtest.log: ~800 MB heap retained after 4 of the 23 files, 13 MB with flat keys). A flat copy of
// each key bounds this without changing any result (pure memo cache). Under tsx the engine modules load viem's CJS build; both
// builds are patched.
const flatKey = (k: unknown) => (typeof k === "string" ? Buffer.from(k, "latin1").toString("latin1") : k);
const patchedCaches: string[] = [];
for (const f of ["/home/user/dapparb/bot/node_modules/viem/_cjs/utils/address/isAddress.js", "/home/user/dapparb/bot/node_modules/viem/_esm/utils/address/isAddress.js"]) {
  try {
    const cache = createRequire("/home/user/dapparb/bot/package.json")(f).isAddressCache;
    const proto = Object.getPrototypeOf(cache);
    cache.get = function (k: unknown) { return proto.get.call(this, flatKey(k)); };
    cache.set = function (k: unknown, v: unknown) { return proto.set.call(this, flatKey(k), v); };
    patchedCaches.push(f);
  } catch (e) {
    console.log(JSON.stringify({ t: new Date().toISOString(), msg: "isAddressCache patch failed", file: f, err: String(e).slice(0, 200) }));
  }
}

// ---------------------------------------------------------------- fetch: browser-like User-Agent
const origFetch = globalThis.fetch;
globalThis.fetch = (async (input: any, init?: any) => {
  const h = new Headers(init?.headers ?? {});
  if (!h.has("user-agent")) h.set("user-agent", UA);
  return origFetch(input, { ...(init ?? {}), headers: h });
}) as any;

// ---------------------------------------------------------------- recording proxy
interface Rec {
  fnStats: Record<string, Record<string, { calls: number; ok: number; fail: number }>>; // stage -> fn -> counts
  failedCalls: any[];
  failedCallsDropped: number;
  rpcErrors: any[];
  chunkThrows: number;
  stageChunkThrows: Record<string, number>;
}
let rec: Rec = { fnStats: {}, failedCalls: [], failedCallsDropped: 0, rpcErrors: [], chunkThrows: 0, stageChunkThrows: {} };
let PIN: bigint = PIN_ARG;
let stage = "init";

const TRANSIENT = /429|rate limit|timeout|timed out|fetch failed|ECONNRESET|ETIMEDOUT|EAI_AGAIN|socket|502|503|504|500|Bad Gateway|Service Unavailable|Gateway|network|HTTP request failed|upgrade to paid|too many|capacity|temporarily|ENOTFOUND|UND_ERR|missing trie node|header not found|unknown block/i;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function withRetry<T>(what: string, fn: () => Promise<T>): Promise<T> {
  let delay = 2000;
  for (let attempt = 1; ; attempt++) {
    try {
      return await fn();
    } catch (e) {
      const msg = String((e as any)?.shortMessage ?? e).slice(0, 300);
      if (rec.rpcErrors.length < 50_000) rec.rpcErrors.push({ t: nowIso(), stage, what, attempt, err: msg });
      if (attempt >= 7 || !TRANSIENT.test(String(e))) throw e;
      await sleep(delay);
      delay = Math.min(delay * 2, 60_000);
    }
  }
}

function record(contracts: any[], res: any[]) {
  const st = (rec.fnStats[stage] ??= {});
  for (let i = 0; i < contracts.length; i++) {
    const c = contracts[i];
    const r = res[i];
    const fn = c.functionName as string;
    const s = (st[fn] ??= { calls: 0, ok: 0, fail: 0 });
    s.calls++;
    if (r?.status === "success") s.ok++;
    else {
      s.fail++;
      if (rec.failedCalls.length < MAX_FAILED_KEPT)
        rec.failedCalls.push({ stage, fn, address: String(c.address).toLowerCase(), args: (c.args ?? []).map((a: any) => String(a)), err: String(r?.error?.shortMessage ?? r?.error ?? "").slice(0, 200) });
      else rec.failedCallsDropped++;
    }
  }
}

const client: any = new Proxy(base as any, {
  get(target, prop, recv) {
    if (prop === "multicall") {
      return async (args: any) => {
        const a = { ...args };
        if (a.blockNumber === undefined && a.blockTag === undefined) a.blockNumber = PIN;
        try {
          const res = await withRetry(`multicall(${a.contracts?.[0]?.functionName}x${a.contracts?.length})`, () => target.multicall(a));
          record(a.contracts, res as any[]);
          return res;
        } catch (e) {
          rec.chunkThrows++;
          rec.stageChunkThrows[stage] = (rec.stageChunkThrows[stage] ?? 0) + 1;
          throw e;
        }
      };
    }
    if (prop === "readContract") {
      return async (args: any) => {
        const a = { ...args };
        if (a.blockNumber === undefined && a.blockTag === undefined) a.blockNumber = PIN;
        return withRetry(`readContract(${a.functionName})`, () => target.readContract(a));
      };
    }
    if (prop === "getBlockNumber") return async () => PIN;
    return Reflect.get(target, prop, recv);
  },
});

// ---------------------------------------------------------------- checkpoint (de)serialization: bigint + Map
const ser = (o: unknown) =>
  JSON.stringify(o, (_k, v) => (typeof v === "bigint" ? { $b: v.toString() } : v instanceof Map ? { $m: [...v.entries()] } : v));
const de = (s: string) =>
  JSON.parse(s, (_k, v) => (v && typeof v === "object" && !Array.isArray(v) ? ("$b" in v ? BigInt(v.$b) : "$m" in v ? new Map(v.$m) : v) : v));
function saveCkpt(name: string, o: unknown) {
  const p = path.join(WORK, name);
  fs.writeFileSync(p + ".tmp", zlib.gzipSync(Buffer.from(ser(o)), { level: 3 }));
  fs.renameSync(p + ".tmp", p);
}
function loadCkpt(name: string, key: string): any | null {
  const p = path.join(WORK, name);
  if (!fs.existsSync(p)) return null;
  const o = de(zlib.gunzipSync(fs.readFileSync(p)).toString());
  if (o.key !== key) {
    say("checkpoint key mismatch; ignoring", { name });
    return null;
  }
  return o;
}

// ---------------------------------------------------------------- output helpers
function csvCell(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = typeof v === "bigint" ? v.toString() : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
const files: any[] = [];
function writeCsvGz(name: string, header: string[], rows: unknown[][]) {
  const toBuf = (rs: unknown[][]) => zlib.gzipSync(Buffer.from([header.join(","), ...rs.map((r) => r.map(csvCell).join(","))].join("\n") + "\n"), { level: 9 });
  let buf = toBuf(rows);
  if (buf.length <= MAXB) {
    const p = path.join(OUT, `${PREFIX}${name}.csv.gz`);
    fs.writeFileSync(p, buf);
    files.push({ file: path.basename(p), rows: rows.length, bytes: buf.length });
    return;
  }
  const parts = Math.ceil(buf.length / (MAXB * 0.9));
  const per = Math.ceil(rows.length / parts);
  for (let k = 0; k < parts; k++) {
    const rs = rows.slice(k * per, (k + 1) * per);
    buf = toBuf(rs);
    const p = path.join(OUT, `${PREFIX}${name}-part-${String(k + 1).padStart(4, "0")}.csv.gz`);
    fs.writeFileSync(p, buf);
    files.push({ file: path.basename(p), rows: rs.length, bytes: buf.length });
  }
}
function writeJsonlGz(name: string, rows: unknown[]) {
  const buf = zlib.gzipSync(Buffer.from(rows.map((r) => JSON.stringify(r, (_k, v) => (typeof v === "bigint" ? v.toString() : v))).join("\n") + (rows.length ? "\n" : "")), { level: 9 });
  const p = path.join(OUT, `${PREFIX}${name}.jsonl.gz`);
  fs.writeFileSync(p, buf);
  files.push({ file: path.basename(p), rows: rows.length, bytes: buf.length });
}
const num = (x: number | undefined) => (x === undefined || !Number.isFinite(x) ? "" : String(x));
const lc = (a: string) => a.toLowerCase();

function sentinel(ok: boolean, reason = "") {
  if (NAME === "none") return;
  fs.mkdirSync(SENT, { recursive: true });
  for (const s of ["DONE", "FAILED"]) try { fs.unlinkSync(path.join(SENT, `${NAME}.${s}`)); } catch {}
  fs.writeFileSync(path.join(SENT, `${NAME}.${ok ? "DONE" : "FAILED"}`), `${reason || "ok"}\n${nowIso()}\n`);
}

// ---------------------------------------------------------------- main
async function main() {
  fs.mkdirSync(OUT, { recursive: true });
  fs.mkdirSync(WORK, { recursive: true });
  const specFiles = expandV4PoolFiles(SPEC);
  const specFileInfo = specFiles.map((f) => ({ file: f, bytes: fs.statSync(f).size, mtime_utc: fs.statSync(f).mtime.toISOString() }));
  const key = crypto.createHash("sha256").update(JSON.stringify({ pin: PIN_ARG.toString(), SPEC, specFileInfo, MAX_PER_FACTORY, RPC, SYNC_BATCH })).digest("hex").slice(0, 16);
  let gitHead = "", gitDirty = "", gitSrc = "";
  try {
    gitHead = execSync("git -C /home/user/dapparb rev-parse HEAD").toString().trim();
    gitSrc = execSync("git -C /home/user/dapparb log -1 --format=%H -- bot/src").toString().trim();
    gitDirty = execSync("git -C /home/user/dapparb status --porcelain -- bot/src").toString().trim();
  } catch {}
  const meta: any = {
    name: NAME, started_utc: nowIso(), checkpoint_key: key,
    engine_sequence: "bot/src/main.ts (universe=all, --v4-pools): enumerateUniverse -> loadV4PoolsFromFile -> loadStaticMetadata -> syncPools(force) -> pruneEmpty -> buildEthPrices -> filterByDepth",
    repo_git_head: gitHead, engine_bot_src_last_commit: gitSrc, engine_bot_src_uncommitted_changes: gitDirty,
    flags: { universe: "all", max_per_factory: MAX_PER_FACTORY, min_depth_eth: MIN_DEPTH_ETH, v4_pools_spec: SPEC },
    v4_pool_files: specFileInfo.map((x) => ({ file: path.basename(x.file), dir: path.dirname(x.file), bytes: x.bytes, mtime_utc: x.mtime_utc })),
    rpc_url: RPC, sync_batch_pools: SYNC_BATCH, viem_isAddressCache_flat_key_patch: patchedCaches, min_anchor_eth: MIN_ANCHOR_ETH, stages: {},
    live_run_reference: {
      file: "run-times.json", launch_utc: runTimes.launch_utc, head_at_launch: runTimes.head_at_launch?.block, ready_log_utc: runTimes.ready_log_utc,
      head_at_ready: runTimes.head_at_ready?.block, head_at_stop: runTimes.head_at_stop?.block,
    },
  };
  const head = await withRetry("head", () => base.getBlockNumber());
  PIN = PIN_ARG;
  const blk = await withRetry("pinBlock", () => base.getBlock({ blockNumber: PIN }));
  meta.head_at_start = Number(head);
  meta.pinned_block = Number(PIN);
  meta.pinned_block_timestamp = Number(blk.timestamp);
  meta.pinned_block_time_utc = new Date(Number(blk.timestamp) * 1000).toISOString();
  meta.pinned_block_hash = blk.hash;
  say("pinned", { pin: Number(PIN), head: Number(head), key, spec_files: specFiles.length });
  const memTimer = setInterval(() => say("rss", { stage }), 60_000);
  memTimer.unref();
  const t = () => Date.now();
  let t0 = t();

  // 1. enumerate (checkpoint A)
  let tokens: any[];
  let pools: Pool[];
  let ck = loadCkpt("A-enumerate.json.gz", key);
  if (ck) {
    tokens = ck.tokens; pools = ck.pools; rec = ck.rec; meta.stages.enumerate = { ...ck.stageMeta, resumed_from_checkpoint: true };
    say("enumerate: resumed from checkpoint", meta.stages.enumerate);
  } else {
    stage = "enumerate";
    const u = await enumerateUniverse(client, cfg as any, { maxPerFactory: MAX_PER_FACTORY });
    tokens = [...cfg.tokens, ...u.tokens.filter((x) => !cfg.tokens.some((c) => lc(c.address) === lc(x.address)))];
    pools = u.pools;
    meta.stages.enumerate = { ms: t() - t0, tokens_total: tokens.length, cfg_tokens: cfg.tokens.length, enumerated_tokens: u.tokens.length, discovered_pools: u.pools.length };
    saveCkpt("A-enumerate.json.gz", { key, tokens, pools, rec, stageMeta: meta.stages.enumerate });
    say("enumerated", meta.stages.enumerate);
  }
  const nonV4Discovered = pools.length;

  // 2. V4 pools from the Initialize files + 3. static metadata (checkpoint B)
  let v4Stats: any;
  ck = loadCkpt("B-v4load-static.json.gz", key);
  if (ck) {
    tokens = ck.tokens; pools = ck.pools; rec = ck.rec; v4Stats = ck.v4Stats; meta.stages.v4load = ck.stageMeta.v4load; meta.stages.static = ck.stageMeta.static;
    meta.stages.v4load.resumed_from_checkpoint = true;
    say("v4load/static: resumed from checkpoint", { pools: pools.length, tokens: tokens.length });
  } else {
    ck = null;
    t0 = t();
    stage = "v4load";
    const r = await loadV4PoolsFromFile(client, cfg as any, SPEC, tokens);
    tokens = [...tokens, ...r.tokensAdded];
    pools.push(...r.pools);
    v4Stats = r.stats;
    meta.stages.v4load = { ms: t() - t0, v4_pools_built: r.pools.length, tokens_added: r.tokensAdded.length, tokens_total: tokens.length };
    say("v4 loaded", meta.stages.v4load);
    t0 = t();
    stage = "static";
    await loadStaticMetadata(client, cfg as any, pools);
    meta.stages.static = { ms: t() - t0 };
    saveCkpt("B-v4load-static.json.gz", { key, tokens, pools, rec, v4Stats, stageMeta: { v4load: meta.stages.v4load, static: meta.stages.static } });
    say("static done", meta.stages.static);
  }
  ck = null;

  // 4. sync (pinned), in batches (checkpoint per batch)
  t0 = t();
  stage = "sync";
  const agg = { stale: 0, total: 0, chunkFailures: 0 };
  const nBatches = Math.ceil(pools.length / SYNC_BATCH);
  let resumedBatches = 0;
  for (let b = 0; b < nBatches; b++) {
    const lo = b * SYNC_BATCH;
    const hi = Math.min(lo + SYNC_BATCH, pools.length);
    const name = `C-sync-${String(b).padStart(4, "0")}.json.gz`;
    const c = loadCkpt(name, key);
    if (c && c.lo === lo && c.hi === hi && c.addresses.length === hi - lo && c.addresses.every((a: string, i: number) => a === pools[lo + i]!.address)) {
      for (let i = lo; i < hi; i++) pools[i] = c.pools[i - lo];
      rec = c.rec;
      agg.stale += c.syncStats.stale; agg.total += c.syncStats.total; agg.chunkFailures += c.syncStats.chunkFailures;
      resumedBatches++;
      continue;
    }
    const tb = t();
    const batch = pools.slice(lo, hi);
    const synced = await syncPools(client, cfg as any, batch, { force: true, blockNumber: PIN });
    if (synced !== PIN) throw new Error(`syncPools returned block ${synced}, expected ${PIN}`);
    const s = { ...syncStats };
    agg.stale += s.stale; agg.total += s.total; agg.chunkFailures += s.chunkFailures;
    saveCkpt(name, { key, lo, hi, addresses: batch.map((p) => p.address), pools: batch, syncStats: s, rec });
    say("sync batch", { batch: b + 1, of: nBatches, lo, hi, ms: t() - tb, syncStats: s });
  }
  meta.stages.sync = { ms: t() - t0, block: Number(PIN), batches: nBatches, batches_resumed_from_checkpoint: resumedBatches, syncStats_summed: agg };
  say("synced", meta.stages.sync);

  // 5. prune, 6. prices, depth (engine order)
  const kept = pruneEmpty(pools);
  const keptSet = new Set(kept);
  const pruned = pools.filter((p) => !keptSet.has(p));
  const prices = buildEthPrices(cfg as any, kept);
  const afterDepth = filterByDepth(kept, prices, MIN_DEPTH_ETH);
  const pass = new Set(afterDepth);
  const cycles = new CycleIndex(afterDepth).candidates.length;
  meta.stages.prune_price = {
    pools_before_prune: pools.length, pools_after_prune: kept.length, pools_pruned: pruned.length,
    v4_before_prune: pools.filter(isV4).length, v4_after_prune_empty: kept.filter(isV4).length,
    priced_tokens: prices.size, min_depth_eth: MIN_DEPTH_ETH, pools_after_depth_filter: afterDepth.length, v4_after_depth_filter: afterDepth.filter(isV4).length,
    tokens_total: tokens.length, cycle_candidates_CycleIndex: cycles,
  };
  say("pruned/priced", meta.stages.prune_price);

  // loader counts in the engine's `v4 pools loaded from file` record layout (startupSync* and v4After* as main.ts computes them)
  meta.v4_loader_counts = {
    spec: SPEC, ...v4Stats,
    startupSyncPools: agg.total, startupSyncStalePools: agg.stale, startupSyncChunkFailures: agg.chunkFailures,
    v4AfterPruneEmpty: kept.filter(isV4).length, v4AfterDepthFilter: afterDepth.filter(isV4).length, minDepthEth: MIN_DEPTH_ETH,
  };
  meta.searcher_ready_equivalent = { tokens: tokens.length, pools: afterDepth.length, cycles, minDepthEth: MIN_DEPTH_ETH };
  meta.non_v4_discovered_pools = nonV4Discovered;

  const tokByAddr = new Map(tokens.map((x: any) => [lc(x.address), x] as const));

  // ---------------- extra reads (NOT part of the engine sequence), pinned at PIN: balanceOf(pool) for non-V4 pools
  stage = "extra_balances";
  t0 = t();
  const ERC20X = parseAbi(["function balanceOf(address) view returns (uint256)"]);
  const balKeys: Array<{ holder: string; token: string }> = [];
  const seenBal = new Set<string>();
  for (const p of pools) {
    if (isV4(p)) continue;
    for (const tk of [lc(p.token0), lc(p.token1)]) {
      const k = `${lc(p.address)}|${tk}`;
      if (seenBal.has(k)) continue;
      seenBal.add(k);
      balKeys.push({ holder: lc(p.address), token: tk });
    }
  }
  const balRes = await multicallChunked(client, cfg.multicall3, balKeys.map((b) => ({ address: b.token as Address, abi: ERC20X, functionName: "balanceOf", args: [b.holder as Address] })), { blockNumber: PIN });
  const bal = new Map<string, { ok: boolean; v: string }>();
  balKeys.forEach((b, i) => bal.set(`${b.holder}|${b.token}`, { ok: balRes[i]?.status === "success", v: balRes[i]?.status === "success" ? String(balRes[i]!.result) : "" }));
  meta.stages.extra_balances = { ms: t() - t0, balance_calls: balKeys.length, failed: balRes.filter((r) => r.status !== "success").length };
  stage = "write";

  // ---------------- write pools (same columns as ../04-shallow-pools/pools-prefilter.csv.gz)
  const poolHeader = [
    "pool_address", "v4_pool_id", "dex", "kind", "is_v4", "token0", "token1", "sym0", "sym1", "dec0", "dec1",
    "v4_currency0", "v4_currency1", "v4_fee_raw", "v4_tick_spacing", "v4_hooks",
    "v2_fee_bps", "aero_stable", "reserve0", "reserve1",
    "cl_tier", "sqrt_price_x96", "tick", "liquidity", "fee_pips", "tick_spacing", "fee_by_dir_zero_for_one", "fee_by_dir_one_for_zero",
    "cl_word_range_min", "cl_word_range_max", "cl_bitmap_words_fetched", "cl_initialized_ticks_fetched",
    "state_block", "token0_balance_of_pool", "token1_balance_of_pool", "token0_balance_ok", "token1_balance_ok",
    "engine_price_eth_token0_derived", "engine_price_eth_token1_derived", "side_amt0_derived", "side_amt1_derived", "engine_depth_eth_derived", "passes_min_depth_0_1_derived",
  ];
  const poolRow = (p: Pool) => {
    const v4p = isV4(p) ? p : null;
    const cl = isV3(p) ? p : null;
    const v2 = isV2(p) ? p : null;
    const { amt0, amt1 } = sideAmounts(p);
    const pr0 = prices.get(lc(p.token0));
    const pr1 = prices.get(lc(p.token1));
    const b0 = v4p ? undefined : bal.get(`${lc(p.address)}|${lc(p.token0)}`);
    const b1 = v4p ? undefined : bal.get(`${lc(p.address)}|${lc(p.token1)}`);
    return [
      lc(p.address), v4p ? lc(v4p.v4.poolId) : "", p.dex, p.kind, v4p ? "true" : "false", lc(p.token0), lc(p.token1),
      tokByAddr.get(lc(p.token0))?.symbol ?? "", tokByAddr.get(lc(p.token1))?.symbol ?? "", p.dec0, p.dec1,
      v4p ? lc(v4p.v4.key.currency0) : "", v4p ? lc(v4p.v4.key.currency1) : "", v4p ? v4p.v4.key.fee : "", v4p ? v4p.v4.key.tickSpacing : "", v4p ? lc(v4p.v4.key.hooks) : "",
      v2 ? v2.feeBps : "", v2 ? String(v2.stable) : "", v2 ? v2.reserve0 : "", v2 ? v2.reserve1 : "",
      cl ? cl.tier : "", cl ? cl.state.sqrtPriceX96 : "", cl ? cl.state.tick : "", cl ? cl.state.liquidity : "", cl ? cl.state.fee : "", cl ? cl.state.tickSpacing : "",
      cl?.state.feeByDir ? cl.state.feeByDir.zeroForOne : "", cl?.state.feeByDir ? cl.state.feeByDir.oneForZero : "",
      cl ? cl.state.wordRange.min : "", cl ? cl.state.wordRange.max : "", cl ? cl.state.bitmap.size : "", cl ? cl.state.ticks.size : "",
      p.block, b0?.v ?? "", b1?.v ?? "", b0 ? String(b0.ok) : "", b1 ? String(b1.ok) : "",
      num(pr0), num(pr1), num(amt0), num(amt1), num(poolDepthEth(p, prices)), keptSet.has(p) ? String(pass.has(p)) : "",
    ];
  };
  writeCsvGz("pools-prefilter", poolHeader, kept.map(poolRow));
  writeCsvGz("pools-pruned-empty", poolHeader, pruned.map(poolRow));

  // prices (same columns as ../04-shallow-pools/prices.csv.gz)
  writeCsvGz("prices", ["token", "symbol", "decimals", "engine_price_eth_derived", "is_weth", "is_usdc"],
    [...prices.entries()].map(([tk, px]) => [tk, tokByAddr.get(tk)?.symbol ?? "", tokByAddr.get(tk)?.decimals ?? "", num(px), String(tk === lc(cfg.weth)), String(tk === lc(cfg.usdc))]));

  writeJsonlGz("failed-calls", rec.failedCalls);
  writeJsonlGz("rpc-errors", rec.rpcErrors);

  meta.fn_stats_by_stage = rec.fnStats;
  meta.failed_calls_kept = rec.failedCalls.length;
  meta.failed_calls_dropped_over_cap = rec.failedCallsDropped;
  meta.chunk_throws_after_retries = rec.chunkThrows;
  meta.chunk_throws_by_stage = rec.stageChunkThrows;
  meta.failed_calls_by_stage = rec.failedCalls.reduce((m: any, f: any) => ((m[`${f.stage}:${f.fn}`] = (m[`${f.stage}:${f.fn}`] ?? 0) + 1), m), {});
  meta.rpc_errors_logged = rec.rpcErrors.length;
  meta.head_at_end = Number(await withRetry("head", () => base.getBlockNumber()));
  meta.finished_utc = nowIso();
  meta.rss_mb_at_end = rssMb();
  meta.peak_rss_mb_sampled_this_process = peakRssMb; // sampled every 60 s and at each log line
  meta.files = files;
  fs.writeFileSync(path.join(OUT, `${PREFIX}meta.json`), JSON.stringify(meta, (_k, v) => (typeof v === "bigint" ? v.toString() : v), 1));
  say("done", { files: files.length });
  sentinel(true, `ok pinned_block=${PIN} pools_after_prune=${kept.length} v4_after_prune=${kept.filter(isV4).length} chunk_throws_after_retries=${rec.chunkThrows}`);
}

main().then(() => process.exit(0)).catch((e) => {
  console.error(e);
  try { sentinel(false, `v4 universe snapshot crashed in stage ${stage}: ${String(e).slice(0, 500)}`); } catch {}
  process.exit(1);
});
