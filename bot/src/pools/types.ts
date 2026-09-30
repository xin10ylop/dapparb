import type { Address } from "viem";
import type { DexKind } from "../config/chains.js";
import type { V3PoolState } from "../math/v3.js";

export interface PoolBase {
  address: Address;
  dex: string;
  kind: DexKind;
  token0: Address;
  token1: Address;
  dec0: number;
  dec1: number;
  /** Block number at which `state` was last refreshed. */
  block: bigint;
}

export interface V2Pool extends PoolBase {
  kind: "univ2" | "aero-v2";
  feeBps: number;
  stable: boolean; // aero-v2 only
  reserve0: bigint;
  reserve1: bigint;
}

export interface V3Pool extends PoolBase {
  kind: "univ3" | "aero-cl" | "pancake-v3";
  tier: number; // fee (univ3/pancake) or tickSpacing (aero-cl) used as the factory key
  state: V3PoolState;
}

export type Pool = V2Pool | V3Pool;

export const isV3 = (p: Pool): p is V3Pool => p.kind === "univ3" || p.kind === "aero-cl" || p.kind === "pancake-v3";
export const isV2 = (p: Pool): p is V2Pool => p.kind === "univ2" || p.kind === "aero-v2";

export function pairKey(a: Address, b: Address): string {
  return a.toLowerCase() < b.toLowerCase() ? `${a.toLowerCase()}-${b.toLowerCase()}` : `${b.toLowerCase()}-${a.toLowerCase()}`;
}

export function sortTokens(a: Address, b: Address): [Address, Address] {
  return a.toLowerCase() < b.toLowerCase() ? [a, b] : [b, a];
}
