import type { Address, PublicClient } from "viem";
import type { ChainConfig } from "../config/chains.js";
import { AERO_FACTORY_ABI, AERO_POOL_ABI, V2_PAIR_ABI, V3_POOL_ABI } from "../abi.js";
import { isV2, isV3, type Pool, type V2Pool, type V3Pool } from "./types.js";
import { compressTick, tickPosition } from "../math/v3.js";
import { log } from "../util/log.js";
import { multicallChunked } from "../util/multicall.js";

/** How far (in price terms) we want fetched tick data to cover on each side of the current price. */
const TICK_COVERAGE = 3000; // ~±35% price range at 1.0001^3000

function wordsNeeded(tickSpacing: number): number {
  return Math.max(1, Math.ceil(TICK_COVERAGE / (256 * tickSpacing)));
}

/**
 * One-time static metadata: V3 tickSpacing/fee (Slipstream fee is dynamic and refreshed each sync),
 * Aerodrome V2 fee from the factory.
 */
export async function loadStaticMetadata(client: PublicClient, cfg: ChainConfig, pools: Pool[]): Promise<void> {
  const calls: any[] = [];
  const map: Array<{ pool: Pool; what: string }> = [];
  const aeroFactory = cfg.dexes.find((d) => d.kind === "aero-v2")?.factory;
  for (const p of pools) {
    if (isV3(p)) {
      calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "tickSpacing" });
      map.push({ pool: p, what: "tickSpacing" });
      calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "fee" });
      map.push({ pool: p, what: "fee" });
    } else if (p.kind === "aero-v2" && aeroFactory) {
      calls.push({ address: aeroFactory, abi: AERO_FACTORY_ABI, functionName: "getFee", args: [p.address, p.stable] });
      map.push({ pool: p, what: "aeroFee" });
    }
  }
  const res = await multicallChunked(client, cfg.multicall3, calls);
  res.forEach((r, i) => {
    const { pool, what } = map[i]!;
    if (r.status !== "success") return;
    if (what === "tickSpacing") (pool as V3Pool).state.tickSpacing = Number(r.result);
    else if (what === "fee") (pool as V3Pool).state.fee = Number(r.result);
    else if (what === "aeroFee") (pool as V2Pool).feeBps = Number(r.result);
  });
}

/**
 * Refresh mutable state for all pools at a single block: V2 reserves, V3 slot0/liquidity (+ dynamic fee
 * for Slipstream). Tick bitmaps and tick liquidityNet are refreshed for pools whose current word range
 * is missing or whose tick moved (`force` refreshes all).
 */
export async function syncPools(client: PublicClient, cfg: ChainConfig, pools: Pool[], opts: { force?: boolean; blockNumber?: bigint; pending?: boolean } = {}): Promise<bigint> {
  // pending=true reads the node's pending state (flashblocks on Base preconf RPC) and is not pinned to a block.
  const blockNumber = opts.pending ? 0n : (opts.blockNumber ?? (await client.getBlockNumber()));
  const tag = opts.pending ? { blockTag: "pending" as const } : { blockNumber };
  const calls: any[] = [];
  const map: Array<{ pool: Pool; what: string }> = [];
  for (const p of pools) {
    if (isV2(p)) {
      calls.push({ address: p.address, abi: p.kind === "aero-v2" ? AERO_POOL_ABI : V2_PAIR_ABI, functionName: "getReserves" });
      map.push({ pool: p, what: "reserves" });
    } else {
      calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "slot0" });
      map.push({ pool: p, what: "slot0" });
      calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "liquidity" });
      map.push({ pool: p, what: "liquidity" });
      if (p.kind === "aero-cl") {
        calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "fee" });
        map.push({ pool: p, what: "fee" });
      }
    }
  }
  const res = await multicallChunked(client, cfg.multicall3, calls, tag);
  const dead = new Set<Address>();
  res.forEach((r, i) => {
    const { pool, what } = map[i]!;
    if (r.status !== "success") {
      dead.add(pool.address);
      return;
    }
    if (!opts.pending) pool.block = blockNumber;
    if (what === "reserves") {
      const [r0, r1] = r.result as [bigint, bigint, bigint];
      (pool as V2Pool).reserve0 = r0;
      (pool as V2Pool).reserve1 = r1;
    } else if (what === "slot0") {
      const [sqrtP, tick] = r.result as [bigint, number];
      (pool as V3Pool).state.sqrtPriceX96 = sqrtP;
      (pool as V3Pool).state.tick = Number(tick);
    } else if (what === "liquidity") (pool as V3Pool).state.liquidity = r.result as bigint;
    else if (what === "fee") (pool as V3Pool).state.fee = Number(r.result);
  });

  // Tick data for V3 pools whose word window no longer covers the current tick (or on force).
  const needTicks = pools.filter((p): p is V3Pool => {
    if (!isV3(p) || dead.has(p.address) || p.state.sqrtPriceX96 === 0n) return false;
    if (opts.force) return true;
    const w = tickPosition(compressTick(p.state.tick, p.state.tickSpacing)).wordPos;
    const n = wordsNeeded(p.state.tickSpacing);
    return w - n < p.state.wordRange.min || w + n > p.state.wordRange.max;
  });
  if (needTicks.length > 0) await fetchTickData(client, cfg, needTicks, opts.pending ? undefined : blockNumber);
  return blockNumber;
}

export async function fetchTickData(client: PublicClient, cfg: ChainConfig, pools: V3Pool[], blockNumber?: bigint): Promise<void> {
  const tag = blockNumber === undefined ? { blockTag: "pending" as const } : { blockNumber };
  // 1) bitmap words
  const calls: any[] = [];
  const map: Array<{ pool: V3Pool; wordPos: number }> = [];
  for (const p of pools) {
    const center = tickPosition(compressTick(p.state.tick, p.state.tickSpacing)).wordPos;
    const n = wordsNeeded(p.state.tickSpacing) + 1; // one extra word each side as a buffer
    p.state.bitmap = new Map();
    p.state.ticks = new Map();
    p.state.wordRange = { min: center - n, max: center + n };
    for (let w = center - n; w <= center + n; w++) {
      calls.push({ address: p.address, abi: V3_POOL_ABI, functionName: "tickBitmap", args: [w] });
      map.push({ pool: p, wordPos: w });
    }
  }
  const words = await multicallChunked(client, cfg.multicall3, calls, tag);
  const tickCalls: any[] = [];
  const tickMap: Array<{ pool: V3Pool; tick: number }> = [];
  words.forEach((r, i) => {
    const { pool, wordPos } = map[i]!;
    if (r.status !== "success") return;
    const word = r.result as bigint;
    pool.state.bitmap.set(wordPos, word);
    if (word === 0n) return;
    for (let bit = 0; bit < 256; bit++) {
      if ((word >> BigInt(bit)) & 1n) {
        const tick = (wordPos * 256 + bit) * pool.state.tickSpacing;
        tickCalls.push({ address: pool.address, abi: V3_POOL_ABI, functionName: "ticks", args: [tick] });
        tickMap.push({ pool, tick });
      }
    }
  });
  // 2) liquidityNet for every initialized tick
  if (tickCalls.length > 0) {
    const res = await multicallChunked(client, cfg.multicall3, tickCalls, tag);
    res.forEach((r, i) => {
      const { pool, tick } = tickMap[i]!;
      if (r.status !== "success") return;
      const [, liquidityNet] = r.result as [bigint, bigint];
      pool.state.ticks.set(tick, liquidityNet);
    });
  }
  log.debug({ pools: pools.length, words: calls.length, ticks: tickCalls.length }, "tick data refreshed");
}

/** Drop pools with no liquidity/reserves so we don't waste cycles on them. */
export function pruneEmpty(pools: Pool[], minReserveWei = 1n): Pool[] {
  return pools.filter((p) => {
    if (isV2(p)) return p.reserve0 > minReserveWei && p.reserve1 > minReserveWei;
    return p.state.sqrtPriceX96 > 0n && (p.state.liquidity > 0n || p.state.ticks.size > 0);
  });
}
