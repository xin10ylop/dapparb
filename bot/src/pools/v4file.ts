/**
 * Opt-in V4 pool source (`--v4-pools <file|glob>[,<file|glob>...]`): every Uniswap V4 pool listed in PoolManager
 * `Initialize` data (CSV with a header row, optionally gzip-compressed, e.g. the V4INIT collector's
 * research-material/01-v4-pools/initialize-part-NNNN.csv.gz) instead of the GeckoTerminal top listings.
 *
 * Required columns: pool_id, currency0, currency1, fee_raw, tick_spacing, hooks (block_number is used when present).
 * Steps: parse every row; keep the keys `isPriceable` accepts (no dynamic fee, no swap-affecting hook flags) and count
 * the rest by reason; check pool_id == keccak256(abi.encode(key)); map currency address(0) to WETH as discoverV4Pools
 * does; drop pools whose StateView.getLiquidity is 0 at startup (chunked Multicall3); fetch ERC-20 decimals/symbol for
 * currencies not yet in the token universe (chunked Multicall3); build the pools with makeV4Pool.
 */
import fs from "node:fs";
import path from "node:path";
import zlib from "node:zlib";
import { type Address, type Hex, type PublicClient, getAddress, zeroAddress } from "viem";
import type { ChainConfig, TokenConfig } from "../config/chains.js";
import { ERC20_ABI } from "../abi.js";
import { multicallChunked, type McCall, type McResult } from "../util/multicall.js";
import { log } from "../util/log.js";
import { isPriceable, makeV4Pool, poolIdOf, STATE_VIEW_ABI, V4, type PoolKey, type V4Pool } from "./v4.js";

const DYNAMIC_FEE_FLAG = 0x800000;
const REQUIRED = ["pool_id", "currency0", "currency1", "fee_raw", "tick_spacing", "hooks"] as const;
const HEX32 = /^0x[0-9a-f]{64}$/;
const HEX20 = /^0x[0-9a-f]{40}$/;
/** Copy into a flat string: substrings of a line would otherwise keep the whole decompressed chunk alive. */
const own = <T extends string>(x: T): T => Buffer.from(x, "latin1").toString("latin1") as T;

export interface V4FileStats {
  files: number;
  rowsRead: number;
  rowsPerFile: Array<{ file: string; rows: number; indexRows?: number }>;
  indexRowMismatches: number;
  blockMin: number | null;
  blockMax: number | null;
  priceable: number;
  priceableHookless: number;
  priceableWithHook: number;
  droppedDynamicFee: number;
  droppedHookSwapFlags: number;
  droppedMalformed: number;
  droppedDuplicatePoolId: number;
  droppedPoolIdMismatch: number;
  droppedSameTokenAfterNativeMapping: number;
  liquidityChecked: number;
  liquidityHeadBefore: string;
  liquidityHeadAfter: string;
  liquidityPositive: number;
  droppedLiquidityZero: number;
  droppedLiquidityCallFailed: number;
  tokensNotInUniverse: number;
  tokensAdded: number;
  tokenMetadataFailed: number;
  droppedTokenMetadataFailed: number;
  v4PoolsBuilt: number;
  parseMs: number;
  liquidityMs: number;
  metadataMs: number;
}

/** Comma-separated list of files or globs (`*` / `?` in the file name only), expanded and sorted per entry. */
export function expandV4PoolFiles(spec: string): string[] {
  const out: string[] = [];
  for (const part of spec.split(",").map((s) => s.trim()).filter(Boolean)) {
    const dir = path.dirname(part);
    const base = path.basename(part);
    if (!/[*?]/.test(base)) {
      if (!fs.existsSync(part)) throw new Error(`--v4-pools: ${part} not found`);
      out.push(part);
      continue;
    }
    if (/[*?]/.test(dir)) throw new Error(`--v4-pools: wildcards are supported in the file name only (${part})`);
    const re = new RegExp("^" + base.replace(/[.+^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*").replace(/\?/g, ".") + "$");
    const matches = fs.readdirSync(dir).filter((f) => re.test(f)).sort().map((f) => path.join(dir, f));
    if (matches.length === 0) throw new Error(`--v4-pools: no file matches ${part}`);
    out.push(...matches);
  }
  return [...new Set(out)];
}

/** Stream a (gzip) CSV: header callback, then one callback per non-empty data line. Returns the data line count. */
async function readCsv(file: string, onHeader: (cols: string[]) => void, onLine: (line: string) => void): Promise<number> {
  const raw = fs.createReadStream(file, { highWaterMark: 4 << 20 });
  let src: NodeJS.ReadableStream = raw;
  if (file.endsWith(".gz")) {
    const gunzip = zlib.createGunzip({ chunkSize: 1 << 20 });
    raw.on("error", (e) => gunzip.destroy(e));
    src = raw.pipe(gunzip);
  }
  let rest = "";
  let header = true;
  let n = 0;
  const emit = (line: string) => {
    if (header) {
      onHeader(line.split(","));
      header = false;
    } else if (line.length > 0) {
      onLine(line);
      n++;
    }
  };
  for await (const chunk of src as AsyncIterable<Buffer>) {
    const s = rest + chunk.toString("utf8");
    let start = 0;
    for (let nl = s.indexOf("\n"); nl >= 0; nl = s.indexOf("\n", start)) {
      emit(s.charCodeAt(nl - 1) === 13 ? s.slice(start, nl - 1) : s.slice(start, nl));
      start = nl + 1;
    }
    rest = s.slice(start);
  }
  if (rest.length > 0) emit(rest);
  return n;
}

/** Row count of a part as listed in a sibling initialize-parts.json (the V4INIT index), when there is one. */
function indexRowsFor(file: string, cache: Map<string, Map<string, number> | null>): number | undefined {
  const dir = path.dirname(file);
  if (!cache.has(dir)) {
    let m: Map<string, number> | null = null;
    try {
      const j = JSON.parse(fs.readFileSync(path.join(dir, "initialize-parts.json"), "utf8")) as { parts?: Array<{ file: string; rows: number }> };
      m = new Map((j.parts ?? []).map((p) => [p.file, Number(p.rows)] as const));
    } catch {
      m = null;
    }
    cache.set(dir, m);
  }
  return cache.get(dir)?.get(path.basename(file));
}

/** multicallChunked, then one more pass over the calls that failed (whole-chunk RPC rejections). */
async function multicallWithRetry(client: PublicClient, cfg: ChainConfig, calls: McCall[], opts: { blockNumber?: bigint } = {}): Promise<McResult[]> {
  const res = await multicallChunked(client, cfg.multicall3, calls, opts);
  const failed = res.map((r, i) => (r.status === "success" ? -1 : i)).filter((i) => i >= 0);
  if (failed.length > 0) {
    const again = await multicallChunked(client, cfg.multicall3, failed.map((i) => calls[i]!), { ...opts, chunk: 100, concurrency: 2 });
    again.forEach((r, j) => (res[failed[j]!] = r));
  }
  return res;
}

interface Candidate {
  poolId: Hex;
  key: PoolKey;
  a0: string; // lowercase token address after mapping native ETH to WETH
  a1: string;
}

export async function loadV4PoolsFromFile(
  client: PublicClient,
  cfg: ChainConfig,
  spec: string,
  tokens: TokenConfig[],
): Promise<{ pools: V4Pool[]; tokensAdded: TokenConfig[]; stats: V4FileStats }> {
  const a = V4[cfg.id];
  if (!a) throw new Error(`--v4-pools: no Uniswap V4 addresses configured for chain ${cfg.id}`);
  const files = expandV4PoolFiles(spec);
  const weth = cfg.weth.toLowerCase();
  const stats: V4FileStats = {
    files: files.length, rowsRead: 0, rowsPerFile: [], indexRowMismatches: 0, blockMin: null, blockMax: null,
    priceable: 0, priceableHookless: 0, priceableWithHook: 0,
    droppedDynamicFee: 0, droppedHookSwapFlags: 0, droppedMalformed: 0, droppedDuplicatePoolId: 0, droppedPoolIdMismatch: 0, droppedSameTokenAfterNativeMapping: 0,
    liquidityChecked: 0, liquidityHeadBefore: "", liquidityHeadAfter: "", liquidityPositive: 0, droppedLiquidityZero: 0, droppedLiquidityCallFailed: 0,
    tokensNotInUniverse: 0, tokensAdded: 0, tokenMetadataFailed: 0, droppedTokenMetadataFailed: 0, v4PoolsBuilt: 0,
    parseMs: 0, liquidityMs: 0, metadataMs: 0,
  };

  // 1) parse every row; keep the locally priceable keys
  const t0 = Date.now();
  const seen = new Set<string>();
  const cands: Candidate[] = [];
  const indexCache = new Map<string, Map<string, number> | null>();
  for (const file of files) {
    let col: Record<string, number> = {};
    let width = 0;
    const rows = await readCsv(
      file,
      (h) => {
        col = Object.fromEntries(h.map((c, i) => [c.trim(), i]));
        width = h.length;
        const missing = REQUIRED.filter((c) => col[c] === undefined);
        if (missing.length > 0) throw new Error(`--v4-pools: ${file} lacks column(s) ${missing.join(", ")}`);
      },
      (line) => {
        const f = line.split(",");
        if (f.length !== width) return void stats.droppedMalformed++;
        if (col.block_number !== undefined) {
          const b = Number(f[col.block_number]);
          if (Number.isInteger(b)) {
            if (stats.blockMin === null || b < stats.blockMin) stats.blockMin = b;
            if (stats.blockMax === null || b > stats.blockMax) stats.blockMax = b;
          }
        }
        const fee = Number(f[col.fee_raw!]);
        const tickSpacing = Number(f[col.tick_spacing!]);
        const hooks = f[col.hooks!]!.toLowerCase() as Address;
        const currency0 = f[col.currency0!]!.toLowerCase() as Address;
        const currency1 = f[col.currency1!]!.toLowerCase() as Address;
        if (!Number.isInteger(fee) || !Number.isInteger(tickSpacing) || !HEX20.test(hooks)) return void stats.droppedMalformed++;
        const key: PoolKey = { currency0, currency1, fee, tickSpacing, hooks };
        if (!isPriceable(key)) {
          if (fee === DYNAMIC_FEE_FLAG) stats.droppedDynamicFee++;
          else stats.droppedHookSwapFlags++;
          return;
        }
        const poolId = own(f[col.pool_id!]!.toLowerCase() as Hex);
        if (!HEX32.test(poolId) || !HEX20.test(currency0) || !HEX20.test(currency1)) return void stats.droppedMalformed++;
        if (seen.has(poolId)) return void stats.droppedDuplicatePoolId++;
        seen.add(poolId);
        if (poolIdOf(key) !== poolId) return void stats.droppedPoolIdMismatch++;
        stats.priceable++;
        if (hooks === zeroAddress) stats.priceableHookless++;
        else stats.priceableWithHook++;
        const a0 = currency0 === zeroAddress ? weth : currency0;
        const a1 = currency1 === zeroAddress ? weth : currency1;
        if (a0 === a1) return void stats.droppedSameTokenAfterNativeMapping++;
        cands.push({ poolId, key: { currency0: own(currency0), currency1: own(currency1), fee, tickSpacing, hooks: own(hooks) }, a0: own(a0), a1: own(a1) });
      },
    );
    const indexRows = indexRowsFor(file, indexCache);
    if (indexRows !== undefined && indexRows !== rows) {
      stats.indexRowMismatches++;
      log.warn({ file, rows, indexRows }, "v4 pool file row count differs from initialize-parts.json");
    }
    stats.rowsRead += rows;
    stats.rowsPerFile.push({ file: path.basename(file), rows, ...(indexRows !== undefined ? { indexRows } : {}) });
    log.debug({ file, rows, rowsSoFar: stats.rowsRead, candidates: cands.length }, "v4 pool file read");
  }
  stats.parseMs = Date.now() - t0;
  log.info({ files: files.length, rowsRead: stats.rowsRead, priceable: stats.priceable, candidates: cands.length, parseMs: stats.parseMs }, "v4 pool files parsed; checking liquidity");

  // 2) drop pools with zero in-range liquidity now (StateView.getLiquidity at `latest`), before the heavy sync.
  // Not pinned to one block: public nodes refuse eth_call ~128 blocks behind head, and this pass can take minutes.
  const t1 = Date.now();
  stats.liquidityHeadBefore = (await client.getBlockNumber()).toString();
  const liq = await multicallWithRetry(
    client,
    cfg,
    cands.map((c) => ({ address: a.stateView, abi: STATE_VIEW_ABI, functionName: "getLiquidity", args: [c.poolId] })),
  );
  stats.liquidityChecked = cands.length;
  const live: Candidate[] = [];
  liq.forEach((r, i) => {
    if (r.status !== "success") return void stats.droppedLiquidityCallFailed++;
    if ((r.result as bigint) === 0n) return void stats.droppedLiquidityZero++;
    live.push(cands[i]!);
  });
  stats.liquidityPositive = live.length;
  stats.liquidityHeadAfter = (await client.getBlockNumber()).toString();
  stats.liquidityMs = Date.now() - t1;
  log.info({ liquidityHeadBefore: stats.liquidityHeadBefore, liquidityHeadAfter: stats.liquidityHeadAfter, liquidityChecked: stats.liquidityChecked, liquidityPositive: stats.liquidityPositive, droppedLiquidityZero: stats.droppedLiquidityZero, droppedLiquidityCallFailed: stats.droppedLiquidityCallFailed, liquidityMs: stats.liquidityMs }, "v4 pool liquidity checked; fetching token metadata");

  // 3) ERC-20 metadata for currencies not yet in the universe (same calls as the factory enumeration)
  const t2 = Date.now();
  const universe = new Map(tokens.map((t) => [t.address.toLowerCase(), t] as const));
  if (!universe.has(weth)) universe.set(weth, { symbol: "WETH", address: cfg.weth, decimals: 18 });
  const missing = [...new Set(live.flatMap((c) => [c.a0, c.a1]))].filter((x) => !universe.has(x));
  stats.tokensNotInUniverse = missing.length;
  const meta = await multicallWithRetry(
    client,
    cfg,
    missing.flatMap((x) => [
      { address: x as Address, abi: ERC20_ABI, functionName: "decimals" },
      { address: x as Address, abi: ERC20_ABI, functionName: "symbol" },
    ]),
  );
  const tokensAdded: TokenConfig[] = [];
  missing.forEach((x, i) => {
    const d = meta[2 * i];
    const s = meta[2 * i + 1];
    if (d?.status !== "success") return void stats.tokenMetadataFailed++;
    const address = getAddress(x);
    const t: TokenConfig = { address, decimals: Number(d.result), symbol: s?.status === "success" ? String(s.result).slice(0, 12) : address.slice(0, 8) };
    tokensAdded.push(t);
    universe.set(x, t);
  });
  stats.tokensAdded = tokensAdded.length;
  stats.metadataMs = Date.now() - t2;

  // 4) engine pool objects, built exactly as discoverV4Pools builds them
  const pools: V4Pool[] = [];
  for (const c of live) {
    const tok0 = universe.get(c.a0);
    const tok1 = universe.get(c.a1);
    if (!tok0 || !tok1) {
      stats.droppedTokenMetadataFailed++;
      continue;
    }
    const key: PoolKey = {
      currency0: getAddress(c.key.currency0),
      currency1: getAddress(c.key.currency1),
      fee: c.key.fee,
      tickSpacing: c.key.tickSpacing,
      hooks: getAddress(c.key.hooks),
    };
    pools.push(makeV4Pool(a, c.poolId, key, tok0, tok1));
  }
  stats.v4PoolsBuilt = pools.length;
  log.info({ tokensNotInUniverse: stats.tokensNotInUniverse, tokensAdded: stats.tokensAdded, tokenMetadataFailed: stats.tokenMetadataFailed, v4PoolsBuilt: stats.v4PoolsBuilt, metadataMs: stats.metadataMs }, "v4 pools built; starting the engine's startup sync");
  return { pools, tokensAdded, stats };
}
