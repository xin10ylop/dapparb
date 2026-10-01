/**
 * Activity-based pool discovery. Factory enumeration (enumerate.ts) only reaches the newest pools of V2-style factories
 * and the V3 tiers of pairs those pools reveal; the on-chain census (docs/ANALYSIS.md §7) found Base arbitrage in
 * Uniswap V3 pools whose pair was never enumerated, in older V2 pairs, in Uniswap V4 pools and in V3 clones. Every pool
 * that matters trades, so this module discovers pools from their own Swap logs:
 *
 *   1. scan Swap logs (UniV2, Aerodrome V2, V3/Slipstream, PancakeSwap V3, Uniswap V4) over a block range with
 *      adaptive eth_getLogs chunking (public endpoints cap the range or the response size);
 *   2. classify each new emitter: factory() maps it to a configured DEX; an unknown factory is accepted only for
 *      V3/Pancake-style pools whose bytecode calls the callback our executor implements (exact clones); V4 pool ids
 *      are resolved through PositionManager.poolKeys and kept when the key is locally priceable;
 *   3. persist everything in a registry file (data/pool-registry-<chain>.json) so restarts only scan new blocks and
 *      rejected emitters are not re-queried;
 *   4. build engine Pool objects for the accepted entries.
 */
import fs from "node:fs";
import path from "node:path";
import { type Address, type Hex, type PublicClient, decodeFunctionResult, encodeFunctionData, getAddress, keccak256, parseAbi, toHex, zeroAddress } from "viem";
import type { ChainConfig, DexConfig, DexKind, TokenConfig } from "../config/chains.js";
import { ERC20_ABI } from "../abi.js";
import { multicallChunked } from "../util/multicall.js";
import { log } from "../util/log.js";
import { isPriceable, makeV4Pool, poolIdOf, V4, type PoolKey } from "./v4.js";
import { loadStaticMetadata, syncPools } from "./state.js";
import { isV3, type Pool, type V3Pool } from "./types.js";
import { quote } from "../arb/quote.js";
import { sideAmounts } from "../arb/pricing.js";

const sig = (s: string) => keccak256(toHex(s));
export const SWAP_TOPICS = {
  univ2: sig("Swap(address,uint256,uint256,uint256,uint256,address)"),
  aero: sig("Swap(address,address,uint256,uint256,uint256,uint256)"),
  v3: sig("Swap(address,address,int256,int256,uint160,uint128,int24)"),
  pancake: sig("Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)"),
  v4: sig("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)"),
} as const;
/** PoolManager Initialize(id, currency0, currency1, fee, tickSpacing, hooks, sqrtPriceX96, tick): keys of pools the
 * PositionManager never saw (created by launchers or custom routers). */
export const V4_INITIALIZE = sig("Initialize(bytes32,address,address,uint24,int24,address,uint160,int24)");
type Family = keyof typeof SWAP_TOPICS;
const FAMILY_OF = new Map<string, Family>(Object.entries(SWAP_TOPICS).map(([k, v]) => [v.toLowerCase(), k as Family]));
/** Which configured DEX kinds may emit each family's Swap event. */
const KINDS_OF: Record<Exclude<Family, "v4">, DexKind[]> = { univ2: ["univ2"], aero: ["aero-v2"], v3: ["univ3", "aero-cl"], pancake: ["pancake-v3"] };
/** Callback selectors an unknown-factory clone must call for our executor to settle it. */
const CLONE_CALLBACK: Partial<Record<Family, { selector: string; kind: DexKind; name: string }>> = {
  v3: { selector: "fa461e33", kind: "univ3", name: "V3clone" }, // uniswapV3SwapCallback(int256,int256,bytes)
  pancake: { selector: "23a69e75", kind: "pancake-v3", name: "PancakeV3clone" }, // pancakeV3SwapCallback(int256,int256,bytes)
};

const SOFT_REJECTIONS = new Set(["no-factory-or-tokens", "no-fee-or-tickspacing", "v4-key-call-failed", "token-metadata", "v4-key-unknown"]);
const POOL_META_ABI = parseAbi([
  "function factory() view returns (address)",
  "function token0() view returns (address)",
  "function token1() view returns (address)",
  "function fee() view returns (uint24)",
  "function tickSpacing() view returns (int24)",
  "function stable() view returns (bool)",
]);
const POSM_ABI = parseAbi(["function poolKeys(bytes25 poolId) view returns (address currency0, address currency1, uint24 fee, int24 tickSpacing, address hooks)"]);

export interface RegistryPool {
  kind: DexKind;
  dex: string;
  token0: Address;
  token1: Address;
  /** V3-style: fee (univ3/pancake) or tickSpacing (aero-cl), as the factory keys it. */
  tier?: number;
  stable?: boolean;
  feeBps?: number;
  factory?: Address;
  v4?: { poolId: Hex; key: PoolKey };
  firstSeen: number;
  lastSeen: number;
  swaps: number;
}
export interface RegistryReject {
  reason: string;
  family: Family;
  factory?: string;
  lastSeen: number;
  swaps: number;
}
export interface Registry {
  version: 1;
  chainId: number;
  scannedFrom: number;
  scannedTo: number;
  /** key: lowercase pool address, or V4 pool id */
  pools: Record<string, RegistryPool>;
  rejected: Record<string, RegistryReject>;
  tokens: Record<string, { symbol: string; decimals: number }>;
  /** Priceable V4 keys seen in Initialize logs, for pools the PositionManager does not know. */
  v4Init?: Record<string, PoolKey>;
  /** Clone factories checked against on-chain execution (local quote must equal the pool's own swap result). */
  factoryChecks?: Record<string, { ok: boolean; block: number; detail: string }>;
}

export function registryPath(cfg: ChainConfig): string {
  return path.resolve(`data/pool-registry-${cfg.name}.json`);
}

export function loadRegistry(file: string, cfg: ChainConfig): Registry {
  try {
    const r = JSON.parse(fs.readFileSync(file, "utf8")) as Registry;
    if (r.version === 1 && r.chainId === cfg.id) return r;
    log.warn({ file }, "registry belongs to another chain or version; starting a new one");
  } catch {}
  return { version: 1, chainId: cfg.id, scannedFrom: 0, scannedTo: 0, pools: {}, rejected: {}, tokens: {} };
}

export function saveRegistry(file: string, reg: Registry): void {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(reg));
  fs.renameSync(tmp, file);
}

/** Swap activity per emitter (or V4 pool id) seen in a block range. */
export interface Activity {
  family: Family;
  emitter: Address; // the pool, or the PoolManager for V4
  swaps: number;
  firstSeen: number;
  lastSeen: number;
}

export function activityKey(l: { address: string; topics: readonly string[] }): { key: string; family: Family } | null {
  const fam = FAMILY_OF.get(String(l.topics[0] ?? "").toLowerCase());
  if (!fam) return null;
  if (fam === "v4") return l.topics[1] ? { key: String(l.topics[1]).toLowerCase(), family: fam } : null;
  return { key: l.address.toLowerCase(), family: fam };
}

export function recordActivity(acc: Map<string, Activity>, l: { address: string; topics: readonly string[] }, block: number): void {
  const k = activityKey(l);
  if (!k) return;
  const a = acc.get(k.key);
  if (a) {
    a.swaps++;
    a.firstSeen = Math.min(a.firstSeen, block);
    a.lastSeen = Math.max(a.lastSeen, block);
  } else acc.set(k.key, { family: k.family, emitter: l.address.toLowerCase() as Address, swaps: 1, firstSeen: block, lastSeen: block });
}

async function rpc(url: string, method: string, params: unknown[]): Promise<any> {
  const res = await fetch(url, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }), signal: AbortSignal.timeout(60_000) });
  const text = await res.text();
  let body: any;
  try {
    body = JSON.parse(text);
  } catch {
    throw new Error(`HTTP ${res.status}: ${text.slice(0, 120)}`);
  }
  if (body.error) throw new Error(`${body.error.code}: ${body.error.message}`);
  return body.result;
}

/**
 * Swap logs over [from, to] with an adaptive range: a range or size rejection halves the chunk, a quiet success grows
 * it. Chunks run with bounded concurrency.
 */
export async function scanSwapActivity(logsUrl: string, from: number, to: number, opts: { initialSpan?: number; maxSpan?: number; concurrency?: number } = {}): Promise<{ activity: Map<string, Activity>; v4Init: Map<string, PoolKey>; logs: number; calls: number }> {
  const acc = new Map<string, Activity>();
  const v4Init = new Map<string, PoolKey>();
  const topics = [[...Object.values(SWAP_TOPICS), V4_INITIALIZE]];
  const initTopic = V4_INITIALIZE.toLowerCase();
  let span = opts.initialSpan ?? 100;
  const maxSpan = opts.maxSpan ?? 2000;
  const concurrency = opts.concurrency ?? 3;
  let next = from;
  let nLogs = 0;
  let calls = 0;
  let done = 0;
  const t0 = Date.now();
  async function chunk(lo: number, hi: number, depth = 0): Promise<void> {
    calls++;
    try {
      const logs: any[] = await rpc(logsUrl, "eth_getLogs", [{ fromBlock: toHex(lo), toBlock: toHex(hi), topics }]);
      for (const l of logs) {
        if (String(l.topics[0]).toLowerCase() === initTopic) {
          const w = String(l.data).slice(2);
          const ts = BigInt("0x" + w.slice(64, 128));
          const key: PoolKey = { currency0: getAddress("0x" + l.topics[2].slice(26)), currency1: getAddress("0x" + l.topics[3].slice(26)), fee: Number(BigInt("0x" + w.slice(0, 64))), tickSpacing: Number(ts >= 1n << 255n ? ts - (1n << 256n) : ts), hooks: getAddress("0x" + w.slice(128 + 24, 192)) };
          if (isPriceable(key)) v4Init.set(String(l.topics[1]).toLowerCase(), key);
        } else recordActivity(acc, l, Number(l.blockNumber));
      }
      nLogs += logs.length;
      done += hi - lo + 1;
      if (logs.length < 5000 && hi - lo + 1 >= span) span = Math.min(maxSpan, Math.ceil(span * 1.5));
    } catch (e) {
      const msg = String(e);
      if (hi > lo && /range|too large|limit|exceed|timeout|10000|more than|response size|-32005|429|rate/i.test(msg)) {
        span = Math.max(1, Math.floor((hi - lo + 1) / 2));
        if (/429|rate/i.test(msg)) await new Promise((r) => setTimeout(r, 1000 * (depth + 1)));
        const mid = lo + Math.floor((hi - lo) / 2);
        await chunk(lo, mid, depth + 1);
        await chunk(mid + 1, hi, depth + 1);
        return;
      }
      if (depth < 4) {
        await new Promise((r) => setTimeout(r, 1000 * (depth + 1)));
        return chunk(lo, hi, depth + 1);
      }
      throw new Error(`getLogs ${lo}-${hi} failed: ${msg.slice(0, 160)}`);
    }
  }
  const workers = Array.from({ length: concurrency }, async () => {
    while (next <= to) {
      const lo = next;
      const hi = Math.min(to, lo + span - 1);
      next = hi + 1;
      await chunk(lo, hi);
      if (calls % 25 === 0) log.info({ blocksDone: done, of: to - from + 1, logs: nLogs, emitters: acc.size, span, calls, s: Math.round((Date.now() - t0) / 1000) }, "swap-log scan progress");
    }
  });
  await Promise.all(workers);
  return { activity: acc, v4Init, logs: nLogs, calls };
}

const RPC_CODE_CHUNK = 50;
async function getCodes(client: PublicClient, addrs: Address[]): Promise<Map<string, string>> {
  const out = new Map<string, string>();
  for (let i = 0; i < addrs.length; i += RPC_CODE_CHUNK) {
    const part = addrs.slice(i, i + RPC_CODE_CHUNK);
    const codes = await Promise.all(part.map((a) => client.getCode({ address: a }).catch(() => undefined)));
    part.forEach((a, j) => out.set(a.toLowerCase(), (codes[j] ?? "0x").toLowerCase()));
  }
  return out;
}

/** Selector check: a PUSH4 of the callback selector in the pool's runtime code. */
const callsSelector = (code: string, selector: string) => code.includes("63" + selector);

/**
 * Classify emitters not yet in the registry and add them (accepted or rejected). Existing entries only get their
 * activity counters updated. Returns the keys of newly accepted pools.
 */
export async function classifyActivity(client: PublicClient, cfg: ChainConfig, reg: Registry, activity: Map<string, Activity>): Promise<{ added: string[]; rejected: number }> {
  const byFactory = new Map<string, DexConfig>(cfg.dexes.map((d) => [d.factory.toLowerCase(), d]));
  const v4a = V4[cfg.id];
  const fresh: Array<[string, Activity]> = [];
  for (const [k, a] of activity) {
    const r = reg.rejected[k];
    // a rejection caused by a failed call (rate limit, flaky node) is retried once the pool trades again an hour later
    if (r && SOFT_REJECTIONS.has(r.reason) && a.lastSeen > r.lastSeen + 1800) delete reg.rejected[k];
    const p = reg.pools[k] ?? reg.rejected[k];
    if (p) {
      p.swaps += a.swaps;
      p.lastSeen = Math.max(p.lastSeen, a.lastSeen);
      if ("firstSeen" in p) p.firstSeen = Math.min(p.firstSeen, a.firstSeen);
    } else fresh.push([k, a]);
  }
  const added: string[] = [];
  let rejected = 0;
  const reject = (k: string, a: Activity, reason: string, factory?: string) => {
    reg.rejected[k] = { reason, family: a.family, factory, lastSeen: a.lastSeen, swaps: a.swaps };
    rejected++;
  };

  // --- V2/V3-style emitters: factory, tokens, fee/tickSpacing/stable ---
  const plain = fresh.filter(([, a]) => a.family !== "v4");
  const calls = plain.flatMap(([k, a]) => {
    const address = k as Address;
    const c = [
      { address, abi: POOL_META_ABI, functionName: "factory" },
      { address, abi: POOL_META_ABI, functionName: "token0" },
      { address, abi: POOL_META_ABI, functionName: "token1" },
    ];
    if (a.family === "v3" || a.family === "pancake") c.push({ address, abi: POOL_META_ABI, functionName: "fee" }, { address, abi: POOL_META_ABI, functionName: "tickSpacing" });
    else if (a.family === "aero") c.push({ address, abi: POOL_META_ABI, functionName: "stable" }, { address, abi: POOL_META_ABI, functionName: "stable" });
    else c.push({ address, abi: POOL_META_ABI, functionName: "token0" }, { address, abi: POOL_META_ABI, functionName: "token0" }); // keep 5 per pool
    return c;
  });
  const res = await multicallChunked(client, cfg.multicall3, calls);
  const candidates: Array<{ k: string; a: Activity; dex: DexConfig | null; factory: string; t0: Address; t1: Address; fee: number; ts: number; stable: boolean }> = [];
  plain.forEach(([k, a], i) => {
    const r = res.slice(5 * i, 5 * i + 5) as Array<{ status: string; result?: unknown } | undefined>;
    if (r.slice(0, 3).some((x) => x?.status !== "success")) return reject(k, a, "no-factory-or-tokens");
    const factory = String(r[0]!.result).toLowerCase();
    const t0 = getAddress(String(r[1]!.result)), t1 = getAddress(String(r[2]!.result));
    const dex = byFactory.get(factory) ?? null;
    const fam = a.family as Exclude<Family, "v4">;
    if (dex && !KINDS_OF[fam].includes(dex.kind)) return reject(k, a, `event-kind-mismatch:${dex.kind}`, factory);
    const fee = a.family === "v3" || a.family === "pancake" ? (r[3]?.status === "success" ? Number(r[3].result) : NaN) : 0;
    const ts = a.family === "v3" || a.family === "pancake" ? (r[4]?.status === "success" ? Number(r[4].result) : NaN) : 0;
    const stable = a.family === "aero" && r[3]?.status === "success" ? Boolean(r[3].result) : false;
    if (!Number.isFinite(fee) || !Number.isFinite(ts)) return reject(k, a, "no-fee-or-tickspacing", factory);
    if (!dex && !CLONE_CALLBACK[a.family]) return reject(k, a, "unknown-factory", factory);
    candidates.push({ k, a, dex, factory, t0, t1, fee, ts, stable });
  });
  // unknown-factory V3/Pancake clones: accept only when the pool calls the callback our executor implements
  const clones = candidates.filter((c) => !c.dex);
  const codes = await getCodes(client, clones.map((c) => c.k as Address));
  const accepted = candidates.filter((c) => {
    if (c.dex) return true;
    const cb = CLONE_CALLBACK[c.a.family]!;
    if (callsSelector(codes.get(c.k) ?? "", cb.selector)) return true;
    reject(c.k, c.a, "unknown-factory-other-callback", c.factory);
    return false;
  });

  // --- V4 pool ids: keys from the PositionManager, verified against the id ---
  const v4fresh = fresh.filter(([, a]) => a.family === "v4");
  const v4ok: Array<{ k: string; a: Activity; key: PoolKey }> = [];
  if (v4fresh.length > 0) {
    if (!v4a) v4fresh.forEach(([k, a]) => reject(k, a, "v4-unsupported-chain"));
    else {
      const kr = await multicallChunked(client, cfg.multicall3, v4fresh.map(([k]) => ({ address: v4a.positionManager, abi: POSM_ABI, functionName: "poolKeys", args: [k.slice(0, 52) as Hex] })));
      v4fresh.forEach(([k, a], i) => {
        if (a.emitter !== v4a.poolManager.toLowerCase()) return reject(k, a, "v4-other-manager");
        const r = kr[i];
        if (r?.status !== "success") return reject(k, a, "v4-key-call-failed");
        const [currency0, currency1, fee, tickSpacing, hooks] = r.result as [Address, Address, number, number, Address];
        const fromInit = reg.v4Init?.[k];
        if (Number(tickSpacing) === 0 && !fromInit) return reject(k, a, "v4-key-unknown");
        const key: PoolKey = Number(tickSpacing) === 0 ? fromInit! : { currency0, currency1, fee: Number(fee), tickSpacing: Number(tickSpacing), hooks };
        if (poolIdOf(key).toLowerCase() !== k) return reject(k, a, "v4-key-mismatch");
        if (!isPriceable(key)) return reject(k, a, key.hooks === zeroAddress ? "v4-dynamic-fee" : "v4-swap-hook-or-dynamic-fee");
        v4ok.push({ k, a, key });
      });
    }
  }

  // --- token metadata for every token not yet known ---
  const need = new Set<string>();
  const known = (t: string) => reg.tokens[t.toLowerCase()] !== undefined;
  for (const c of accepted) for (const t of [c.t0, c.t1]) if (!known(t)) need.add(t.toLowerCase());
  for (const v of v4ok) for (const t of [v.key.currency0, v.key.currency1]) if (t !== zeroAddress && !known(t)) need.add(t.toLowerCase());
  const needList = [...need] as Address[];
  const meta = await multicallChunked(client, cfg.multicall3, needList.flatMap((a) => [{ address: a, abi: ERC20_ABI, functionName: "decimals" }, { address: a, abi: ERC20_ABI, functionName: "symbol" }]));
  needList.forEach((a, i) => {
    const d = meta[2 * i] as { status: string; result?: unknown } | undefined, s = meta[2 * i + 1] as { status: string; result?: unknown } | undefined;
    if (d?.status !== "success") return;
    reg.tokens[a.toLowerCase()] = { decimals: Number(d.result), symbol: s?.status === "success" ? String(s.result).replace(/[^\x20-\x7e]/g, "").slice(0, 12) : a.slice(0, 8) };
  });
  const weth = cfg.weth.toLowerCase();
  reg.tokens[weth] ??= { symbol: "WETH", decimals: 18 };

  for (const c of accepted) {
    if (!known(c.t0) || !known(c.t1)) {
      reject(c.k, c.a, "token-metadata", c.factory);
      continue;
    }
    const base = { token0: c.t0, token1: c.t1, factory: c.factory as Address, firstSeen: c.a.firstSeen, lastSeen: c.a.lastSeen, swaps: c.a.swaps };
    if (c.dex) {
      const kind = c.dex.kind;
      if (kind === "univ2") reg.pools[c.k] = { ...base, kind, dex: c.dex.name, feeBps: c.dex.feeBps ?? 30 };
      else if (kind === "aero-v2") reg.pools[c.k] = { ...base, kind, dex: c.dex.name, stable: c.stable };
      else reg.pools[c.k] = { ...base, kind, dex: c.dex.name, tier: kind === "aero-cl" ? c.ts : c.fee };
    } else {
      const cb = CLONE_CALLBACK[c.a.family]!;
      reg.pools[c.k] = { ...base, kind: cb.kind, dex: `${cb.name}:${c.factory.slice(0, 10)}`, tier: c.fee };
    }
    added.push(c.k);
  }
  for (const v of v4ok) {
    const c0 = v.key.currency0 === zeroAddress ? weth : v.key.currency0.toLowerCase();
    const c1 = v.key.currency1 === zeroAddress ? weth : v.key.currency1.toLowerCase();
    if (!known(c0) || !known(c1) || c0 === c1) {
      reject(v.k, v.a, c0 === c1 ? "v4-same-token-after-native-mapping" : "token-metadata");
      continue;
    }
    reg.pools[v.k] = { kind: "univ3", dex: "UniswapV4", token0: getAddress(c0), token1: getAddress(c1), tier: v.key.fee, v4: { poolId: v.k as Hex, key: v.key }, firstSeen: v.a.firstSeen, lastSeen: v.a.lastSeen, swaps: v.a.swaps };
    added.push(v.k);
  }
  return { added, rejected };
}

/** Engine pools (and their tokens) for registry entries, optionally only those seen since `sinceBlock`. */
export function poolsFromRegistry(reg: Registry, cfg: ChainConfig, keys?: Iterable<string>, sinceBlock = 0): { pools: Pool[]; tokens: TokenConfig[] } {
  const tok = (a: string): TokenConfig => {
    const m = reg.tokens[a.toLowerCase()]!;
    return { address: getAddress(a), decimals: m.decimals, symbol: m.symbol };
  };
  const pools: Pool[] = [];
  const tokens = new Map<string, TokenConfig>();
  const v4a = V4[cfg.id];
  for (const k of keys ?? Object.keys(reg.pools)) {
    const e = reg.pools[k];
    if (!e || e.lastSeen < sinceBlock) continue;
    if (isClone(e) && !reg.factoryChecks?.[String(e.factory).toLowerCase()]?.ok) continue; // clone factory not verified exact
    const t0 = tok(e.token0), t1 = tok(e.token1);
    tokens.set(t0.address.toLowerCase(), t0);
    tokens.set(t1.address.toLowerCase(), t1);
    const base = { address: getAddress(k.length === 42 ? k : k.slice(0, 42)), dex: e.dex, token0: t0.address, token1: t1.address, dec0: t0.decimals, dec1: t1.decimals, block: 0n };
    if (e.v4) {
      if (!v4a) continue;
      // makeV4Pool orders tokens as currency0/currency1 (native mapped to WETH), the same order as e.token0/e.token1
      pools.push(makeV4Pool(v4a, e.v4.poolId, e.v4.key, t0, t1));
    } else if (e.kind === "univ2") pools.push({ ...base, kind: "univ2", feeBps: e.feeBps ?? 30, stable: false, reserve0: 0n, reserve1: 0n });
    else if (e.kind === "aero-v2") pools.push({ ...base, kind: "aero-v2", feeBps: 0, stable: !!e.stable, reserve0: 0n, reserve1: 0n });
    else
      pools.push({
        ...base,
        kind: e.kind,
        tier: e.tier ?? 0,
        state: { sqrtPriceX96: 0n, tick: 0, liquidity: 0n, fee: e.kind === "aero-cl" ? 0 : (e.tier ?? 0), tickSpacing: e.kind === "aero-cl" ? (e.tier ?? 0) : 0, bitmap: new Map(), ticks: new Map(), wordRange: { min: 0, max: -1 } },
      });
  }
  return { pools, tokens: [...tokens.values()] };
}

const isClone = (e: RegistryPool) => /clone:/.test(e.dex);
const QUOTER_AT = "0x00000000000000000000000000000000000ab0b0" as Address;
const QUOTER_ABI = parseAbi(["function quote(address pool, bool zeroForOne, uint256 amountIn) returns (uint256 amountOut, uint256 amountInUsed)"]);
let quoterCode: Hex | null = null;

/**
 * A clone's bytecode can call the right callback and still charge a different fee (observed: a "0.3 %" UniswapV3Factory
 * clone that takes 0.35 %). Before a clone factory's pools are used, quote its busiest pools locally and on chain at
 * the same block (contracts/src/test-helpers/PoolQuoter.sol by state override: the pool's own swap, reverted in the
 * callback) and accept the factory only when every comparable quote matches to the wei. Factories with no pool that
 * has in-range liquidity stay unchecked and are retried on the next refresh.
 */
export async function verifyCloneFactories(client: PublicClient, cfg: ChainConfig, reg: Registry, maxPoolsPerFactory = 3): Promise<void> {
  quoterCode ??= ("0x" + fs.readFileSync(new URL("../exec/artifacts/PoolQuoter.runtime.hex", import.meta.url), "utf8").trim().replace(/^0x/, "")) as Hex;
  const byFactory = new Map<string, string[]>();
  for (const [k, e] of Object.entries(reg.pools)) {
    if (!isClone(e) || !e.factory) continue;
    const f = e.factory.toLowerCase();
    if (reg.factoryChecks?.[f]) continue;
    byFactory.set(f, [...(byFactory.get(f) ?? []), k]);
  }
  if (byFactory.size === 0) return;
  const pick = [...byFactory.values()].flatMap((ks) => ks.sort((a, b) => reg.pools[b]!.swaps - reg.pools[a]!.swaps).slice(0, maxPoolsPerFactory));
  const checks = { ...(reg.factoryChecks ?? {}) };
  for (const f of byFactory.keys()) checks[f] = { ok: true, block: 0, detail: "" }; // let poolsFromRegistry build them
  const { pools } = poolsFromRegistry({ ...reg, factoryChecks: checks }, cfg, pick);
  await loadStaticMetadata(client, cfg, pools);
  const block = await syncPools(client, cfg, pools, { force: true });
  const verdict = new Map<string, { compared: number; bad: string[] }>();
  for (const p of pools as V3Pool[]) {
    if (!isV3(p) || p.state.liquidity === 0n) continue;
    const f = String(reg.pools[p.address.toLowerCase()]?.factory ?? "").toLowerCase();
    const v = verdict.get(f) ?? { compared: 0, bad: [] };
    verdict.set(f, v);
    const { amt0, amt1 } = sideAmounts(p);
    for (const zeroForOne of [true, false]) {
      const virt = zeroForOne ? amt0 : amt1, dec = zeroForOne ? p.dec0 : p.dec1;
      const amountIn = BigInt(Math.floor(virt * 1e-3 * 10 ** Math.min(dec, 15))) * 10n ** BigInt(Math.max(0, dec - 15));
      if (amountIn <= 0n) continue;
      const local = quote(p, zeroForOne ? p.token0 : p.token1, amountIn);
      if (local.truncated) continue;
      try {
        const out = await client.call({ to: QUOTER_AT, data: encodeFunctionData({ abi: QUOTER_ABI, functionName: "quote", args: [p.address, zeroForOne, amountIn] }), blockNumber: block, stateOverride: [{ address: QUOTER_AT, code: quoterCode }] });
        const [amountOut, used] = decodeFunctionResult({ abi: QUOTER_ABI, functionName: "quote", data: out.data! }) as readonly [bigint, bigint];
        if (used !== amountIn) continue;
        v.compared++;
        if (amountOut !== local.amountOut) v.bad.push(`${p.address} ${zeroForOne ? "0>1" : "1>0"} local=${local.amountOut} chain=${amountOut}`);
      } catch (e) {
        v.bad.push(`${p.address} swap reverted: ${String(e).slice(0, 80)}`);
      }
    }
  }
  reg.factoryChecks ??= {};
  for (const [f, v] of verdict) {
    if (v.compared === 0 && v.bad.length === 0) continue;
    reg.factoryChecks[f] = { ok: v.bad.length === 0, block: Number(block), detail: v.bad.length ? v.bad.slice(0, 2).join("; ") : `${v.compared} quotes exact` };
    log.info({ factory: f, ...reg.factoryChecks[f] }, "clone factory checked");
  }
}

/** Rejection counts by reason (with swaps), for logging. */
export function registrySummary(reg: Registry): Record<string, unknown> {
  const byDex = new Map<string, number>();
  for (const e of Object.values(reg.pools)) byDex.set(e.dex.split(":")[0]!, (byDex.get(e.dex.split(":")[0]!) ?? 0) + 1);
  const rej = new Map<string, { n: number; swaps: number }>();
  for (const e of Object.values(reg.rejected)) {
    const r = rej.get(e.reason) ?? { n: 0, swaps: 0 };
    r.n++;
    r.swaps += e.swaps;
    rej.set(e.reason, r);
  }
  const fc = Object.values(reg.factoryChecks ?? {});
  return { scannedFrom: reg.scannedFrom, scannedTo: reg.scannedTo, accepted: Object.keys(reg.pools).length, byDex: Object.fromEntries(byDex), rejected: Object.fromEntries(rej), tokens: Object.keys(reg.tokens).length, cloneFactories: { exact: fc.filter((x) => x.ok).length, failed: fc.filter((x) => !x.ok).length } };
}

async function scanInto(client: PublicClient, cfg: ChainConfig, reg: Registry, logsUrl: string, from: number, to: number): Promise<void> {
  const t0 = Date.now();
  const scan = await scanSwapActivity(logsUrl, from, to);
  for (const [id, key] of scan.v4Init) (reg.v4Init ??= {})[id] = key;
  const cls = await classifyActivity(client, cfg, reg, scan.activity);
  log.info({ from, to, logs: scan.logs, calls: scan.calls, emitters: scan.activity.size, added: cls.added.length, rejected: cls.rejected, s: Math.round((Date.now() - t0) / 1000) }, "pool registry scanned");
}

/**
 * Bring the registry up to date over the window [head - lookback + 1, head] (or an explicit [from, to]): scan the part
 * after the registry's end, backfill the part before its start, classify new emitters, save. A registry that does not
 * touch the window is rebuilt from the window. Returns the registry and the last block scanned.
 */
export async function refreshRegistry(client: PublicClient, cfg: ChainConfig, file: string, lookback: number, logsUrl: string, window?: { from: number; to: number }): Promise<{ reg: Registry; head: number }> {
  let reg = loadRegistry(file, cfg);
  const head = window?.to ?? Number(await client.getBlockNumber());
  const start = window?.from ?? Math.max(1, head - lookback + 1);
  if (reg.scannedTo !== 0 && (reg.scannedTo < start - 1 || reg.scannedFrom > head + 1)) {
    log.warn({ registry: [reg.scannedFrom, reg.scannedTo], window: [start, head] }, "registry does not touch the requested window; rebuilding it");
    reg = loadRegistry("", cfg);
  }
  if (reg.scannedTo === 0) {
    await scanInto(client, cfg, reg, logsUrl, start, head);
    reg.scannedFrom = start;
    reg.scannedTo = head;
  } else {
    if (start < reg.scannedFrom) {
      await scanInto(client, cfg, reg, logsUrl, start, reg.scannedFrom - 1);
      reg.scannedFrom = start;
    }
    if (head > reg.scannedTo) {
      await scanInto(client, cfg, reg, logsUrl, reg.scannedTo + 1, head);
      reg.scannedTo = head;
    }
  }
  await verifyCloneFactories(client, cfg, reg);
  saveRegistry(file, reg);
  log.info(registrySummary(reg), "pool registry");
  return { reg, head };
}
