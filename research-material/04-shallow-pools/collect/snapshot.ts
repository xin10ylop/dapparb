/**
 * SHALLOW_SNAPSHOT collector.
 *
 * Reproduces the engine's universe-building sequence from bot/src/main.ts (universe=all, max-per-factory 6000):
 *   enumerateUniverse -> discoverV4Pools(pages=2) -> loadStaticMetadata -> syncPools(force) -> pruneEmpty
 *   -> buildEthPrices -> (poolDepthEth / filterByDepth 0.1)
 * with every on-chain read pinned to ONE block (PIN), and dumps every pool BEFORE the depth filter (after pruneEmpty),
 * the pools removed by pruneEmpty, the engine price map, token metadata, CL tick data and pool token balances.
 *
 * Engine modules are imported unchanged by relative path. The only interposition is a Proxy around the engine's own
 * viem client (makeHttpClient) that
 *   - adds blockNumber=PIN to every multicall/readContract that does not specify a block (engine calls default to latest),
 *   - retries transient RPC failures (HTTP 429/5xx, timeouts, fetch errors) with exponential backoff before letting the
 *     engine's own chunk bisection see the error,
 *   - records per-call successes/failures and the raw factory enumeration results (allPools/allPairs/token0/token1).
 * globalThis.fetch is wrapped to keep the raw GeckoTerminal responses used by discoverV4Pools.
 *
 * Run (from /home/user/dapparb/bot):
 *   LOG_JSON=1 npx tsx ../research-material/04-shallow-pools/collect/snapshot.ts [--pin <block>] [--out <dir>]
 */
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { parseAbi, zeroAddress, type Address } from "../../../bot/node_modules/viem/_esm/index.js";
import { getChain } from "../../../bot/src/config/chains.js";
import { makeHttpClient } from "../../../bot/src/util/client.js";
import { enumerateUniverse } from "../../../bot/src/pools/enumerate.js";
import { discoverV4Pools, isV4, V4 } from "../../../bot/src/pools/v4.js";
import { loadStaticMetadata, pruneEmpty, syncPools, syncStats } from "../../../bot/src/pools/state.js";
import { buildEthPrices, sideAmounts, MIN_ANCHOR_ETH } from "../../../bot/src/arb/pricing.js";
import { filterByDepth, poolDepthEth } from "../../../bot/src/arb/depth.js";
import { multicallChunked } from "../../../bot/src/util/multicall.js";
import { isV2, isV3, type Pool } from "../../../bot/src/pools/types.js";
import { AERO_POOL_ABI, V2_PAIR_ABI, V3_POOL_ABI } from "../../../bot/src/abi.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

const OUT = arg("out", "/home/user/dapparb/research-material/04-shallow-pools")!;
const SENT = "/home/user/dapparb/research-material/.sentinels";
const NAME = arg("sentinel", "SHALLOW_SNAPSHOT")!;
const MAX_PER_FACTORY = Number(arg("max-per-factory", "6000"));
const V4_PAGES = 2; // main.ts: universe === "top" ? 3 : 2
const LIMIT_TOKENS = arg("limit-tokens"); // smoke tests only
const MAXB = 85 * 1024 * 1024;
const nowIso = () => new Date().toISOString();
const say = (msg: string, o: object = {}) => console.log(JSON.stringify({ t: nowIso(), msg, ...o }));

const cfg = getChain("base");
const base = makeHttpClient(cfg);

// ---------------------------------------------------------------- recording proxy
const fnStats = new Map<string, { calls: number; ok: number; fail: number }>();
const failedCalls: any[] = [];
const rpcErrors: any[] = [];
const enumRows: Array<{ factory: string; index: string; result: string; ok: boolean }> = [];
const t01Rows = new Map<string, { t0?: string; t1?: string; t0ok?: boolean; t1ok?: boolean }>();
const tokenMetaCalls = new Map<string, { decimals?: string; decOk?: boolean; symbol?: string; symOk?: boolean }>();
let chunkThrows = 0;
let PIN: bigint = 0n;
let stage = "init";
const stageChunkThrows: Record<string, number> = {};

const TRANSIENT = /429|rate limit|timeout|timed out|fetch failed|ECONNRESET|ETIMEDOUT|EAI_AGAIN|socket|502|503|504|500|Bad Gateway|Service Unavailable|Gateway|network|HTTP request failed|upgrade to paid|too many|capacity|temporarily|ENOTFOUND|UND_ERR/i;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function withRetry<T>(what: string, fn: () => Promise<T>): Promise<T> {
  let delay = 2000;
  for (let attempt = 1; ; attempt++) {
    try {
      return await fn();
    } catch (e) {
      const msg = String((e as any)?.shortMessage ?? e).slice(0, 300);
      rpcErrors.push({ t: nowIso(), stage, what, attempt, err: msg });
      if (attempt >= 7 || !TRANSIENT.test(String(e))) throw e;
      await sleep(delay);
      delay = Math.min(delay * 2, 60_000);
    }
  }
}

function record(contracts: any[], res: any[]) {
  for (let i = 0; i < contracts.length; i++) {
    const c = contracts[i];
    const r = res[i];
    const fn = c.functionName as string;
    const s = fnStats.get(fn) ?? { calls: 0, ok: 0, fail: 0 };
    s.calls++;
    if (r?.status === "success") s.ok++;
    else {
      s.fail++;
      failedCalls.push({ stage, fn, address: String(c.address).toLowerCase(), args: (c.args ?? []).map((a: any) => String(a)), err: String(r?.error?.shortMessage ?? r?.error ?? "").slice(0, 200) });
    }
    fnStats.set(fn, s);
    const addr = String(c.address).toLowerCase();
    if (fn === "allPools" || fn === "allPairs") enumRows.push({ factory: addr, index: String(c.args[0]), result: r?.status === "success" ? String(r.result).toLowerCase() : "", ok: r?.status === "success" });
    else if (fn === "token0" || fn === "token1") {
      if (stage !== "enumerate") continue;
      const row = t01Rows.get(addr) ?? {};
      if (fn === "token0") { row.t0 = r?.status === "success" ? String(r.result).toLowerCase() : ""; row.t0ok = r?.status === "success"; }
      else { row.t1 = r?.status === "success" ? String(r.result).toLowerCase() : ""; row.t1ok = r?.status === "success"; }
      t01Rows.set(addr, row);
    } else if ((fn === "decimals" || fn === "symbol") && stage === "enumerate") {
      const row = tokenMetaCalls.get(addr) ?? {};
      if (fn === "decimals") { row.decOk = r?.status === "success"; row.decimals = r?.status === "success" ? String(r.result) : ""; }
      else { row.symOk = r?.status === "success"; row.symbol = r?.status === "success" ? String(r.result) : ""; }
      tokenMetaCalls.set(addr, row);
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
          chunkThrows++;
          stageChunkThrows[stage] = (stageChunkThrows[stage] ?? 0) + 1;
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

// ---------------------------------------------------------------- GeckoTerminal capture
const gtLog: any[] = [];
const origFetch = globalThis.fetch;
globalThis.fetch = (async (input: any, init?: any) => {
  const url = typeof input === "string" ? input : input?.url ?? String(input);
  if (!url.includes("geckoterminal.com")) return origFetch(input, init);
  const t = nowIso();
  try {
    const r = await origFetch(input, init);
    let body = "";
    try { body = await r.clone().text(); } catch {}
    gtLog.push({ t, url, status: r.status, body });
    return r;
  } catch (e) {
    gtLog.push({ t, url, status: null, error: String(e).slice(0, 200) });
    throw e;
  }
}) as any;

// ---------------------------------------------------------------- output helpers
function csvCell(v: unknown): string {
  if (v === null || v === undefined) return "";
  const s = typeof v === "bigint" ? v.toString() : String(v);
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
const files: any[] = [];
function writeCsvGz(base: string, header: string[], rows: unknown[][]) {
  const toBuf = (rs: unknown[][]) => zlib.gzipSync(Buffer.from([header.join(","), ...rs.map((r) => r.map(csvCell).join(","))].join("\n") + "\n"), { level: 9 });
  let buf = toBuf(rows);
  if (buf.length <= MAXB) {
    const p = path.join(OUT, `${base}.csv.gz`);
    fs.writeFileSync(p, buf);
    files.push({ file: path.basename(p), rows: rows.length, bytes: buf.length });
    return;
  }
  const parts = Math.ceil(buf.length / (MAXB * 0.9));
  const per = Math.ceil(rows.length / parts);
  for (let k = 0; k < parts; k++) {
    const rs = rows.slice(k * per, (k + 1) * per);
    buf = toBuf(rs);
    const p = path.join(OUT, `${base}-part-${String(k + 1).padStart(4, "0")}.csv.gz`);
    fs.writeFileSync(p, buf);
    files.push({ file: path.basename(p), rows: rs.length, bytes: buf.length });
  }
}
function writeJsonlGz(base: string, rows: unknown[]) {
  const buf = zlib.gzipSync(Buffer.from(rows.map((r) => JSON.stringify(r, (_k, v) => (typeof v === "bigint" ? v.toString() : v))).join("\n") + (rows.length ? "\n" : "")), { level: 9 });
  const p = path.join(OUT, `${base}.jsonl.gz`);
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
  const meta: any = { name: NAME, started_utc: nowIso(), engine_sequence: "bot/src/main.ts lines ~95-120 (universe=all)", max_per_factory: MAX_PER_FACTORY, v4_gt_pages: V4_PAGES, rpc_urls: cfg.rpcUrls, min_anchor_eth: MIN_ANCHOR_ETH, stages: {} };
  const head = await withRetry("head", () => base.getBlockNumber());
  PIN = arg("pin") ? BigInt(arg("pin")!) : head - 3n;
  const blk = await withRetry("pinBlock", () => base.getBlock({ blockNumber: PIN }));
  meta.head_at_start = Number(head);
  meta.pinned_block = Number(PIN);
  meta.pinned_block_timestamp = Number(blk.timestamp);
  meta.pinned_block_time_utc = new Date(Number(blk.timestamp) * 1000).toISOString();
  meta.pinned_block_hash = blk.hash;
  say("pinned", { pin: Number(PIN), head: Number(head) });

  const t = () => Date.now();
  let t0 = t();
  // 1. enumerate
  stage = "enumerate";
  const u = await enumerateUniverse(client, cfg, { maxPerFactory: MAX_PER_FACTORY });
  let tokens = [...cfg.tokens, ...u.tokens.filter((x) => !cfg.tokens.some((c) => lc(c.address) === lc(x.address)))];
  let pools: Pool[] = u.pools;
  if (LIMIT_TOKENS) {
    // smoke test only: keep pools whose both tokens are within the first N tokens of the list (plus cfg tokens)
    const keep = new Set(tokens.slice(0, Number(LIMIT_TOKENS)).map((x) => lc(x.address)));
    for (const c of cfg.tokens) keep.add(lc(c.address));
    pools = pools.filter((p) => keep.has(lc(p.token0)) && keep.has(lc(p.token1)));
    meta.smoke_limit_tokens = Number(LIMIT_TOKENS);
  }
  meta.stages.enumerate = { ms: t() - t0, tokens_total: tokens.length, cfg_tokens: cfg.tokens.length, enumerated_tokens: u.tokens.length, discovered_pools: u.pools.length, pools_after_smoke_limit: pools.length };
  say("enumerated", meta.stages.enumerate);

  // 2. V4 (GeckoTerminal-listed)
  t0 = t();
  stage = "v4";
  const v4 = await discoverV4Pools(client, cfg, tokens, V4_PAGES);
  pools.push(...v4);
  meta.stages.v4 = { ms: t() - t0, v4_pools: v4.length, gt_requests: gtLog.length, gt_non200: gtLog.filter((g) => g.status !== 200).length };
  say("v4", meta.stages.v4);

  // 3. static metadata
  t0 = t();
  stage = "static";
  await loadStaticMetadata(client, cfg, pools);
  meta.stages.static = { ms: t() - t0 };

  // 4. sync (pinned)
  t0 = t();
  stage = "sync";
  const synced = await syncPools(client, cfg, pools, { force: true, blockNumber: PIN });
  meta.stages.sync = { ms: t() - t0, block: Number(synced), syncStats: { ...syncStats } };
  say("synced", meta.stages.sync);

  // 5. prune
  const kept = pruneEmpty(pools);
  const keptSet = new Set(kept);
  const pruned = pools.filter((p) => !keptSet.has(p));
  // 6. prices, depth
  const prices = buildEthPrices(cfg, kept);
  const pass01 = new Set(filterByDepth(kept, prices, 0.1));
  meta.stages.prune_price = { pools_before_prune: pools.length, pools_after_prune: kept.length, pools_pruned: pruned.length, priced_tokens: prices.size, pools_passing_filterByDepth_0_1: pass01.size };
  say("pruned/priced", meta.stages.prune_price);

  const tokByAddr = new Map(tokens.map((x) => [lc(x.address), x] as const));

  // ---------------- extra reads (NOT part of the engine sequence), pinned at PIN
  stage = "extra_balances";
  t0 = t();
  const ERC20X = parseAbi([
    "function balanceOf(address) view returns (uint256)",
    "function name() view returns (string)",
    "function totalSupply() view returns (uint256)",
  ]);
  const pm = lc(V4[cfg.id]!.poolManager);
  // balances of each non-V4 pool's two tokens held by the pool; V4 tokens held by the PoolManager
  const balKeys: Array<{ holder: string; token: string }> = [];
  const seenBal = new Set<string>();
  for (const p of pools) {
    const holders = isV4(p) ? [pm] : [lc(p.address)];
    const toks = isV4(p) ? [p.v4.key.currency0, p.v4.key.currency1].map(lc).filter((x) => x !== zeroAddress) : [lc(p.token0), lc(p.token1)];
    for (const h of holders) for (const tk of toks) {
      const k = `${h}|${tk}`;
      if (seenBal.has(k)) continue;
      seenBal.add(k);
      balKeys.push({ holder: h, token: tk });
    }
  }
  const balRes = await multicallChunked(client, cfg.multicall3, balKeys.map((b) => ({ address: b.token as Address, abi: ERC20X, functionName: "balanceOf", args: [b.holder as Address] })), { blockNumber: PIN });
  const bal = new Map<string, { ok: boolean; v: string }>();
  balKeys.forEach((b, i) => bal.set(`${b.holder}|${b.token}`, { ok: balRes[i]?.status === "success", v: balRes[i]?.status === "success" ? String(balRes[i]!.result) : "" }));
  // native ETH held by the PoolManager (for V4 pools keyed on currency0 = 0x0)
  let pmEth = "";
  try { pmEth = String(await withRetry("pmEth", () => base.getBalance({ address: pm as Address, blockNumber: PIN }))); } catch (e) { rpcErrors.push({ stage, what: "pmEth", err: String(e).slice(0, 200) }); }
  meta.stages.extra_balances = { ms: t() - t0, balance_calls: balKeys.length, failed: balRes.filter((r) => r.status !== "success").length };

  stage = "extra_token_meta";
  t0 = t();
  const allTok = [...new Set([...tokens.map((x) => lc(x.address)), ...pools.flatMap((p) => [lc(p.token0), lc(p.token1)])])];
  const tmRes = await multicallChunked(client, cfg.multicall3, allTok.flatMap((a) => [{ address: a as Address, abi: ERC20X, functionName: "name" }, { address: a as Address, abi: ERC20X, functionName: "totalSupply" }]), { blockNumber: PIN });
  meta.stages.extra_token_meta = { ms: t() - t0, tokens: allTok.length };

  // recheck raw state of the pruned pools at PIN (separates "empty" from "read failed")
  stage = "extra_pruned_recheck";
  t0 = t();
  const rcCalls: any[] = [];
  const rcMap: Array<{ p: Pool; what: string }> = [];
  const SV = parseAbi(["function getSlot0(bytes32 poolId) view returns (uint160 sqrtPriceX96, int24 tick, uint24 protocolFee, uint24 lpFee)", "function getLiquidity(bytes32 poolId) view returns (uint128)"]);
  for (const p of pruned) {
    if (isV2(p)) { rcCalls.push({ address: p.address, abi: p.kind === "aero-v2" ? AERO_POOL_ABI : V2_PAIR_ABI, functionName: "getReserves" }); rcMap.push({ p, what: "reserves" }); }
    else if (isV4(p)) {
      rcCalls.push({ address: p.v4.stateView, abi: SV, functionName: "getSlot0", args: [p.v4.poolId] }); rcMap.push({ p, what: "slot0" });
      rcCalls.push({ address: p.v4.stateView, abi: SV, functionName: "getLiquidity", args: [p.v4.poolId] }); rcMap.push({ p, what: "liquidity" });
    } else {
      rcCalls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "slot0" }); rcMap.push({ p, what: "slot0" });
      rcCalls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "liquidity" }); rcMap.push({ p, what: "liquidity" });
    }
  }
  const rcRes = await multicallChunked(client, cfg.multicall3, rcCalls, { blockNumber: PIN });
  const recheck = new Map<Pool, Record<string, string>>();
  rcRes.forEach((r, i) => {
    const { p, what } = rcMap[i]!;
    const o = recheck.get(p) ?? {};
    o[`${what}_ok`] = String(r.status === "success");
    if (r.status === "success") {
      const v = r.result as any;
      if (what === "reserves") { o.r0 = String(v[0]); o.r1 = String(v[1]); }
      else if (what === "slot0") { o.sqrtP = String(v[0]); o.tick = String(v[1]); }
      else o.liq = String(v);
    }
    recheck.set(p, o);
  });
  meta.stages.extra_pruned_recheck = { ms: t() - t0, calls: rcCalls.length, failed: rcRes.filter((r) => r.status !== "success").length };
  stage = "write";

  // ---------------- write pools
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
      num(pr0), num(pr1), num(amt0), num(amt1), num(poolDepthEth(p, prices)), keptSet.has(p) ? String(pass01.has(p)) : "",
    ];
  };
  writeCsvGz("pools-prefilter", poolHeader, kept.map(poolRow));
  const prunedHeader = [...poolHeader, "recheck_reserves_ok", "recheck_reserve0", "recheck_reserve1", "recheck_slot0_ok", "recheck_sqrt_price_x96", "recheck_tick", "recheck_liquidity_ok", "recheck_liquidity"];
  writeCsvGz("pools-pruned-empty", prunedHeader, pruned.map((p) => {
    const o = recheck.get(p) ?? {};
    return [...poolRow(p), o.reserves_ok ?? "", o.r0 ?? "", o.r1 ?? "", o.slot0_ok ?? "", o.sqrtP ?? "", o.tick ?? "", o.liquidity_ok ?? "", o.liq ?? ""];
  }));

  // CL tick data as fetched by syncPools(force) for the kept pools
  const tickRows: unknown[][] = [];
  for (const p of kept) {
    if (!isV3(p)) continue;
    const id = isV4(p) ? lc(p.v4.poolId) : "";
    for (const [tk, net] of [...p.state.ticks.entries()].sort((a, b) => a[0] - b[0])) tickRows.push([lc(p.address), id, tk, net, p.state.ticksGross?.get(tk) ?? ""]);
  }
  writeCsvGz("cl-ticks-prefilter", ["pool_address", "v4_pool_id", "tick", "liquidity_net", "liquidity_gross"], tickRows);

  // prices
  writeCsvGz("prices", ["token", "symbol", "decimals", "engine_price_eth_derived", "is_weth", "is_usdc"],
    [...prices.entries()].map(([tk, px]) => [tk, tokByAddr.get(tk)?.symbol ?? "", tokByAddr.get(tk)?.decimals ?? "", num(px), String(tk === lc(cfg.weth)), String(tk === lc(cfg.usdc))]));

  // tokens
  const inPre = new Map<string, number>();
  const inPru = new Map<string, number>();
  for (const p of kept) for (const x of [lc(p.token0), lc(p.token1)]) inPre.set(x, (inPre.get(x) ?? 0) + 1);
  for (const p of pruned) for (const x of [lc(p.token0), lc(p.token1)]) inPru.set(x, (inPru.get(x) ?? 0) + 1);
  const cfgSet = new Set(cfg.tokens.map((x) => lc(x.address)));
  const enumSet = new Set(u.tokens.map((x) => lc(x.address)));
  const allTokRows = allTok.map((a, i) => {
    const tk = tokByAddr.get(a);
    const n = tmRes[2 * i];
    const s = tmRes[2 * i + 1];
    return [a, tk?.symbol ?? "", tk?.decimals ?? "", String(cfgSet.has(a)), String(enumSet.has(a)),
      n?.status === "success" ? String(n.result) : "", String(n?.status === "success"), s?.status === "success" ? String(s.result) : "", String(s?.status === "success"),
      String(inPre.get(a) ?? 0), String(inPru.get(a) ?? 0), num(prices.get(a))];
  });
  writeCsvGz("tokens", ["token", "symbol_engine", "decimals_engine", "in_cfg_tokens", "in_enumerated_tokens", "name", "name_ok", "total_supply", "total_supply_ok",
    "n_prefilter_pools_derived", "n_pruned_pools_derived", "engine_price_eth_derived"], allTokRows);

  // tokens seen during enumeration whose decimals() failed (dropped by enumerateUniverse)
  writeCsvGz("enumerated-token-meta-calls", ["token", "decimals_ok", "decimals", "symbol_ok", "symbol"],
    [...tokenMetaCalls.entries()].map(([a, r]) => [a, String(!!r.decOk), r.decimals ?? "", String(!!r.symOk), r.symbol ?? ""]));

  // V4 PoolManager balances
  const pmRows = [...bal.entries()].filter(([k]) => k.startsWith(pm + "|")).map(([k, v]) => [pm, k.split("|")[1], v.v, String(v.ok)]);
  pmRows.push([pm, zeroAddress, pmEth, String(pmEth !== "")]);
  writeCsvGz("v4-poolmanager-balances", ["holder", "token", "balance", "balance_ok"], pmRows);

  // factory enumeration (raw allPools/allPairs + token0/token1 of each enumerated pool)
  const dexByFactory = new Map(cfg.dexes.map((d) => [lc(d.factory), d.name] as const));
  const discovered = new Set(u.pools.map((p) => lc(p.address)));
  writeCsvGz("factory-enumeration", ["factory", "dex", "index", "pool_address", "call_ok", "token0", "token1", "token0_ok", "token1_ok", "in_discovered_pools_derived"],
    enumRows.map((r) => { const tt = t01Rows.get(r.result) ?? {}; return [r.factory, dexByFactory.get(r.factory) ?? "", r.index, r.result, String(r.ok), tt.t0 ?? "", tt.t1 ?? "", tt.t0ok === undefined ? "" : String(tt.t0ok), tt.t1ok === undefined ? "" : String(tt.t1ok), String(discovered.has(r.result))]; }));

  writeJsonlGz("geckoterminal-responses", gtLog);
  writeJsonlGz("snapshot-failed-calls", failedCalls);
  writeJsonlGz("snapshot-rpc-errors", rpcErrors);

  meta.fn_stats = Object.fromEntries(fnStats);
  meta.chunk_throws_after_retries = chunkThrows;
  meta.chunk_throws_by_stage = stageChunkThrows;
  meta.failed_calls_by_stage = failedCalls.reduce((m: any, f: any) => ((m[`${f.stage}:${f.fn}`] = (m[`${f.stage}:${f.fn}`] ?? 0) + 1), m), {});
  meta.head_at_end = Number(await withRetry("head", () => base.getBlockNumber()));
  meta.finished_utc = nowIso();
  meta.files = files;
  fs.writeFileSync(path.join(OUT, "snapshot-meta.json"), JSON.stringify(meta, null, 1));
  say("done", { files: files.length });
  sentinel(true, `ok pinned_block=${PIN} chunk_throws_after_retries=${chunkThrows}`);
}

main().then(() => process.exit(0)).catch((e) => {
  console.error(e);
  try { sentinel(false, `snapshot crashed in stage ${stage}: ${String(e).slice(0, 500)}`); } catch {}
  process.exit(1);
});
