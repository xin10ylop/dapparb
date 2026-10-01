/**
 * Event-driven state engine. Every AMM this bot prices emits enough in its own events to reconstruct the state the
 * pricing math needs, so a block's logs (or a flashblock's pending logs on a node that serves them) replace the
 * multicall entirely:
 *   Uniswap V2 & forks   Sync(uint112,uint112)                       → reserves
 *   Aerodrome V2         Sync(uint256,uint256)                       → reserves
 *   Uniswap V3 / Slipstream / Sushi V3  Swap(...,uint160 sqrtP,uint128 L,int24 tick) → slot0 + liquidity
 *   PancakeSwap V3       Swap(... + protocol fees)                   → slot0 + liquidity
 *   Uniswap V4           Swap(bytes32 id, ..., uint24 fee)           → slot0 + liquidity + lp fee
 *   Mint/Burn/ModifyLiquidity                                        → mark tick data dirty (refetched lazily)
 */
import { type Address, type Hex, type PublicClient, decodeAbiParameters, keccak256, toHex } from "viem";
import { isV2, isV3, type Pool, type V3Pool } from "./types.js";
import { isV4 } from "./v4.js";
import { compressTick, tickPosition, type V3PoolState } from "../math/v3.js";

const int24FromTopic = (t: Hex): number => Number(decodeAbiParameters([{ type: "int24" }], t)[0]);

/**
 * Apply a liquidity change on [tickLower, tickUpper) exactly as Tick.update/Pool.modifyLiquidity do:
 * liquidityNet(lower) += Δ, liquidityNet(upper) -= Δ, liquidityGross(both) += |Δ| (flipping the bitmap bit when a
 * tick becomes initialised or cleared) and the active liquidity when the current tick is inside the range.
 * Returns false when the range lies outside the fetched tick window (caller must refetch tick data).
 */
function applyLiquidityDelta(st: V3PoolState, tickLower: number, tickUpper: number, delta: bigint): boolean {
  const gross = (st.ticksGross ??= new Map());
  const inWindow = (t: number) => {
    const w = tickPosition(compressTick(t, st.tickSpacing)).wordPos;
    return w >= st.wordRange.min && w <= st.wordRange.max;
  };
  const upd = (tick: number, netDelta: bigint) => {
    const g0 = gross.get(tick) ?? 0n;
    const g1 = g0 + (delta < 0n ? -delta : delta) * (delta < 0n ? -1n : 1n); // gross += Δ (Δ<0 on burn)
    const n1 = (st.ticks.get(tick) ?? 0n) + netDelta;
    if (g1 <= 0n) {
      gross.delete(tick);
      st.ticks.delete(tick);
    } else {
      gross.set(tick, g1);
      st.ticks.set(tick, n1);
    }
    const c = compressTick(tick, st.tickSpacing);
    const { wordPos, bitPos } = tickPosition(c);
    const word = st.bitmap.get(wordPos) ?? 0n;
    const mask = 1n << BigInt(bitPos);
    st.bitmap.set(wordPos, g1 > 0n ? word | mask : word & ~mask);
  };
  if (!inWindow(tickLower) || !inWindow(tickUpper)) return false;
  upd(tickLower, delta);
  upd(tickUpper, -delta);
  if (st.tick >= tickLower && st.tick < tickUpper) st.liquidity += delta;
  return true;
}

const sig = (s: string) => keccak256(toHex(s));
export const TOPICS = {
  v2Sync: sig("Sync(uint112,uint112)"),
  aeroSync: sig("Sync(uint256,uint256)"),
  v3Swap: sig("Swap(address,address,int256,int256,uint160,uint128,int24)"),
  pancakeV3Swap: sig("Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)"),
  v4Swap: sig("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)"),
  v3Mint: sig("Mint(address,address,int24,int24,uint128,uint256,uint256)"),
  v3Burn: sig("Burn(address,int24,int24,uint128,uint256,uint256)"),
  v4ModifyLiquidity: sig("ModifyLiquidity(bytes32,address,int24,int24,int256,bytes32)"),
} as const;

export interface RawLog {
  address: Address;
  topics: Hex[];
  data: Hex;
  blockNumber?: bigint | Hex;
  logIndex?: number | Hex;
}

export interface ApplyResult {
  touched: Set<string>; // lowercase pool addresses whose pricing state changed
  dirtyTicks: Set<string>; // pools whose tick data must be refetched before their next V3 quote
  applied: number;
  ignored: number;
}

/** Index pools by the address (V2/V3) or PoolManager address + poolId (V4) that emits their events. */
export class PoolIndex {
  readonly byAddress = new Map<string, Pool>();
  readonly v4ByManagerAndId = new Map<string, Pool>();
  constructor(pools: Pool[]) {
    for (const p of pools) {
      if (isV4(p)) this.v4ByManagerAndId.set(`${p.v4.manager.toLowerCase()}:${p.v4.poolId.toLowerCase()}`, p);
      else this.byAddress.set(p.address.toLowerCase(), p);
    }
  }
  /** Track a pool added while running (live discovery). */
  add(p: Pool): void {
    if (isV4(p)) this.v4ByManagerAndId.set(`${p.v4.manager.toLowerCase()}:${p.v4.poolId.toLowerCase()}`, p);
    else this.byAddress.set(p.address.toLowerCase(), p);
  }
  /** Addresses to pass as an eth_getLogs filter (V4 pools share the PoolManager). */
  addresses(): Address[] {
    const set = new Set<string>(this.byAddress.keys());
    for (const k of this.v4ByManagerAndId.keys()) set.add(k.split(":")[0]!);
    return [...set] as Address[];
  }
}

export function applyLogs(index: PoolIndex, logs: RawLog[], blockNumber?: bigint): ApplyResult {
  const res: ApplyResult = { touched: new Set(), dirtyTicks: new Set(), applied: 0, ignored: 0 };
  for (const log of logs) {
    const topic = log.topics[0];
    if (!topic) continue;
    const addr = log.address.toLowerCase();
    let pool: Pool | undefined = index.byAddress.get(addr);
    if (!pool && (topic === TOPICS.v4Swap || topic === TOPICS.v4ModifyLiquidity)) {
      const id = log.topics[1]?.toLowerCase();
      if (id) pool = index.v4ByManagerAndId.get(`${addr}:${id}`);
    }
    if (!pool) {
      res.ignored++;
      continue;
    }
    const key = pool.address.toLowerCase();
    try {
      if (topic === TOPICS.v2Sync && isV2(pool)) {
        const [r0, r1] = decodeAbiParameters([{ type: "uint112" }, { type: "uint112" }], log.data);
        pool.reserve0 = r0;
        pool.reserve1 = r1;
      } else if (topic === TOPICS.aeroSync && isV2(pool)) {
        const [r0, r1] = decodeAbiParameters([{ type: "uint256" }, { type: "uint256" }], log.data);
        pool.reserve0 = r0;
        pool.reserve1 = r1;
      } else if ((topic === TOPICS.v3Swap || topic === TOPICS.pancakeV3Swap) && isV3(pool)) {
        const [, , sqrtP, L, tick] = decodeAbiParameters(
          topic === TOPICS.v3Swap
            ? [{ type: "int256" }, { type: "int256" }, { type: "uint160" }, { type: "uint128" }, { type: "int24" }]
            : [{ type: "int256" }, { type: "int256" }, { type: "uint160" }, { type: "uint128" }, { type: "int24" }, { type: "uint128" }, { type: "uint128" }],
          log.data,
        );
        const st = (pool as V3Pool).state;
        st.sqrtPriceX96 = sqrtP as bigint;
        st.liquidity = L as bigint;
        st.tick = Number(tick);
      } else if (topic === TOPICS.v4Swap && isV3(pool)) {
        const [a0, , sqrtP, L, tick, fee] = decodeAbiParameters(
          [{ type: "int128" }, { type: "int128" }, { type: "uint160" }, { type: "uint128" }, { type: "int24" }, { type: "uint24" }],
          log.data,
        );
        const st = (pool as V3Pool).state;
        // the event's fee is the effective swap fee (lp + protocol) for this swap's direction
        const zeroForOne = (sqrtP as bigint) < st.sqrtPriceX96 || ((sqrtP as bigint) === st.sqrtPriceX96 && (a0 as bigint) < 0n);
        st.feeByDir ??= { zeroForOne: st.fee, oneForZero: st.fee };
        if (zeroForOne) st.feeByDir.zeroForOne = Number(fee);
        else st.feeByDir.oneForZero = Number(fee);
        st.sqrtPriceX96 = sqrtP as bigint;
        st.liquidity = L as bigint;
        st.tick = Number(tick);
      } else if ((topic === TOPICS.v3Mint || topic === TOPICS.v3Burn) && isV3(pool)) {
        const tickLower = int24FromTopic(log.topics[2]!);
        const tickUpper = int24FromTopic(log.topics[3]!);
        const amount = topic === TOPICS.v3Mint
          ? (decodeAbiParameters([{ type: "address" }, { type: "uint128" }, { type: "uint256" }, { type: "uint256" }], log.data)[1] as bigint)
          : (decodeAbiParameters([{ type: "uint128" }, { type: "uint256" }, { type: "uint256" }], log.data)[0] as bigint);
        if (amount === 0n) continue;
        const delta = topic === TOPICS.v3Mint ? amount : -amount;
        if (!applyLiquidityDelta((pool as V3Pool).state, tickLower, tickUpper, delta)) res.dirtyTicks.add(key);
      } else if (topic === TOPICS.v4ModifyLiquidity && isV3(pool)) {
        const [tickLower, tickUpper, delta] = decodeAbiParameters([{ type: "int24" }, { type: "int24" }, { type: "int256" }, { type: "bytes32" }], log.data);
        if ((delta as bigint) === 0n) continue;
        if (!applyLiquidityDelta((pool as V3Pool).state, Number(tickLower), Number(tickUpper), delta as bigint)) res.dirtyTicks.add(key);
      } else {
        res.ignored++;
        continue;
      }
      if (blockNumber !== undefined) pool.block = blockNumber;
      res.touched.add(key);
      res.applied++;
    } catch {
      res.ignored++;
    }
  }
  return res;
}

/** Logs of one block for the tracked pools, via eth_getLogs with an address filter. */
export async function fetchBlockLogs(client: PublicClient, index: PoolIndex, blockNumber: bigint): Promise<RawLog[]> {
  const addresses = index.addresses();
  const logs = await client.getLogs({ address: addresses, fromBlock: blockNumber, toBlock: blockNumber });
  return logs as unknown as RawLog[];
}

/** All logs of one block via eth_getBlockReceipts (one call, no filter), filtered locally to tracked emitters. */
export async function fetchBlockLogsViaReceipts(client: PublicClient, index: PoolIndex, blockTag: bigint | "pending" | "latest"): Promise<RawLog[]> {
  const receipts: any[] = await client.request({ method: "eth_getBlockReceipts" as any, params: [typeof blockTag === "bigint" ? ("0x" + blockTag.toString(16)) : blockTag] as any });
  const tracked = new Set(index.addresses().map((a) => a.toLowerCase()));
  const out: RawLog[] = [];
  for (const r of receipts ?? []) {
    if (r.status !== "0x1") continue;
    for (const l of r.logs ?? []) if (tracked.has(String(l.address).toLowerCase())) out.push({ address: l.address, topics: l.topics, data: l.data, blockNumber: l.blockNumber, logIndex: l.logIndex });
  }
  return out;
}
