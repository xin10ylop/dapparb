/**
 * Uniswap V4 support (Base). V4 pools live inside the PoolManager singleton and are identified by a PoolKey hash.
 * State is read through the canonical StateView lens. Only hookless pools (or hooks without swap permissions) are
 * priced: a hook with beforeSwap/afterSwap/returns-delta flags can change the outcome arbitrarily.
 */
import { type Address, type Hex, type PublicClient, encodeAbiParameters, keccak256, parseAbi, zeroAddress } from "viem";
import type { ChainConfig, TokenConfig } from "../config/chains.js";
import type { V3Pool } from "./types.js";
import { multicallChunked } from "../util/multicall.js";
import { fetchTopPools } from "../research/tokens.js";
import { log } from "../util/log.js";

export interface V4Addresses {
  poolManager: Address;
  stateView: Address;
  positionManager: Address;
}

export const V4: Record<number, V4Addresses> = {
  8453: {
    poolManager: "0x498581fF718922c3f8e6A244956aF099B2652b2b",
    stateView: "0xA3c0c9b65baD0b08107Aa264b0f3dB444b867A71",
    positionManager: "0x7C5f5A4bBd8fD63184577525326123B519429bDc",
  },
  1: {
    poolManager: "0x000000000004444c5dc75cB358380D2e3dE08A90",
    stateView: "0x7fFE42C4a5DEeA5b0feC41C94C136Cf115597227",
    positionManager: "0xbD216513d74C8cf14cf4747E6AaA6420FF64ee9e",
  },
  42161: {
    poolManager: "0x360E68faCcca8cA495c1B759Fd9EEe466db9FB32",
    stateView: "0x76Fd297e2D437cd7f76d50F01AfE6160f86e9990",
    positionManager: "0xd88F38F930b7952f2DB2432Cb002E7abbF3dD869",
  },
};

export interface PoolKey {
  currency0: Address;
  currency1: Address;
  fee: number;
  tickSpacing: number;
  hooks: Address;
}

export interface V4Pool extends V3Pool {
  kind: "univ3"; // priced with the V3 engine
  v4: { poolId: Hex; key: PoolKey; manager: Address; stateView: Address };
}

export const STATE_VIEW_ABI = parseAbi([
  "function getSlot0(bytes32 poolId) view returns (uint160 sqrtPriceX96, int24 tick, uint24 protocolFee, uint24 lpFee)",
  "function getLiquidity(bytes32 poolId) view returns (uint128)",
  "function getTickBitmap(bytes32 poolId, int16 tick) view returns (uint256)",
  "function getTickInfo(bytes32 poolId, int24 tick) view returns (uint128 liquidityGross, int128 liquidityNet, uint256 feeGrowthOutside0X128, uint256 feeGrowthOutside1X128)",
]);
const POSM_ABI = parseAbi(["function poolKeys(bytes25 poolId) view returns (address currency0, address currency1, uint24 fee, int24 tickSpacing, address hooks)"]);

const DYNAMIC_FEE_FLAG = 0x800000;
// Hooks.sol permission bits encoded in the hook address
const BEFORE_SWAP_FLAG = 1n << 7n;
const AFTER_SWAP_FLAG = 1n << 6n;
const BEFORE_SWAP_RETURNS_DELTA_FLAG = 1n << 3n;
const AFTER_SWAP_RETURNS_DELTA_FLAG = 1n << 2n;

export function poolIdOf(k: PoolKey): Hex {
  return keccak256(
    encodeAbiParameters(
      [{ type: "address" }, { type: "address" }, { type: "uint24" }, { type: "int24" }, { type: "address" }],
      [k.currency0, k.currency1, k.fee, k.tickSpacing, k.hooks],
    ),
  );
}

/** A pool is locally priceable when nothing can alter the swap outcome besides the core math. */
export function isPriceable(k: PoolKey): boolean {
  if (k.fee === DYNAMIC_FEE_FLAG) return false;
  if (k.hooks === zeroAddress) return true;
  const bits = BigInt(k.hooks);
  return (bits & (BEFORE_SWAP_FLAG | AFTER_SWAP_FLAG | BEFORE_SWAP_RETURNS_DELTA_FLAG | AFTER_SWAP_RETURNS_DELTA_FLAG)) === 0n;
}

/**
 * Discover V4 pools among the top-volume pools listed by GeckoTerminal, resolving each PoolKey from the
 * PositionManager (pools that ever had a position minted through it). Restricted to the token universe.
 */
export async function discoverV4Pools(client: PublicClient, cfg: ChainConfig, tokens: TokenConfig[], pages = 3): Promise<V4Pool[]> {
  const a = V4[cfg.id];
  if (!a) return [];
  const universe = new Map(tokens.map((t) => [t.address.toLowerCase(), t] as const));
  const weth = tokens.find((t) => t.address.toLowerCase() === cfg.weth.toLowerCase());
  const gt = (await fetchTopPools(cfg, pages)).filter((p) => p.dex.startsWith("uniswap-v4") && /^0x[0-9a-f]{64}$/i.test(p.address));
  if (gt.length === 0) return [];
  const keys = await multicallChunked(
    client,
    cfg.multicall3,
    gt.map((p) => ({ address: a.positionManager, abi: POSM_ABI, functionName: "poolKeys", args: [p.address.slice(0, 52) as Hex] })),
  );
  const pools: V4Pool[] = [];
  const stats = { keyFailed: 0, unknownKey: 0, hooked: 0, outOfUniverse: 0 };
  keys.forEach((r, i) => {
    if (r.status !== "success") return void stats.keyFailed++;
    const [c0, c1, fee, tickSpacing, hooks] = r.result as [Address, Address, number, number, Address];
    if (tickSpacing === 0) return void stats.unknownKey++; // never touched by the PositionManager
    const key: PoolKey = { currency0: c0, currency1: c1, fee, tickSpacing, hooks };
    if (!isPriceable(key)) return void stats.hooked++;
    const t0 = c0 === zeroAddress ? weth : universe.get(c0.toLowerCase());
    const t1 = c1 === zeroAddress ? weth : universe.get(c1.toLowerCase());
    if (!t0 || !t1) return void stats.outOfUniverse++;
    const poolId = gt[i]!.address as Hex;
    pools.push({
      address: poolId.slice(0, 42) as Address, // synthetic unique address (first 20 bytes of the id) for graph keys
      dex: "UniswapV4",
      kind: "univ3",
      token0: t0.address,
      token1: t1.address,
      dec0: t0.decimals,
      dec1: t1.decimals,
      block: 0n,
      tier: fee,
      state: { sqrtPriceX96: 0n, tick: 0, liquidity: 0n, fee, tickSpacing, bitmap: new Map(), ticks: new Map(), wordRange: { min: 0, max: -1 } },
      v4: { poolId, key, manager: a.poolManager, stateView: a.stateView },
    });
  });
  log.info({ listed: gt.length, kept: pools.length, ...stats }, "uniswap v4 pools discovered");
  return pools;
}

export const isV4 = (p: unknown): p is V4Pool => typeof p === "object" && p !== null && (p as { v4?: unknown }).v4 !== undefined;
