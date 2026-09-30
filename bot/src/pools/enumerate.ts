/**
 * Full-universe pool discovery for Base: enumerate every pool from the factories that expose enumeration
 * (Aerodrome V2 `allPools`, the three Slipstream factories `allPools`, Uniswap V2 / Sushi V2 / Pancake V2 /
 * BaseSwap `allPairs`), then look up every V3/Pancake tier for each token pair those pools reveal. This reaches the
 * long tail that GeckoTerminal's top-volume listings never show.
 */
import { type Address, type PublicClient, parseAbi, zeroAddress } from "viem";
import type { ChainConfig, TokenConfig } from "../config/chains.js";
import { multicallChunked } from "../util/multicall.js";
import { discoverPools } from "./discovery.js";
import { ERC20_ABI } from "../abi.js";
import type { Pool } from "./types.js";
import { log } from "../util/log.js";

const ENUM_ABI = parseAbi([
  "function allPoolsLength() view returns (uint256)",
  "function allPools(uint256) view returns (address)",
  "function allPairsLength() view returns (uint256)",
  "function allPairs(uint256) view returns (address)",
]);
const T01 = parseAbi(["function token0() view returns (address)", "function token1() view returns (address)"]);

export async function enumerateUniverse(client: PublicClient, cfg: ChainConfig, opts: { maxPerFactory?: number } = {}): Promise<{ tokens: TokenConfig[]; pools: Pool[] }> {
  const maxPer = opts.maxPerFactory ?? 20_000;
  const addrs: Address[] = [];
  for (const d of cfg.dexes) {
    const isAero = d.kind === "aero-v2" || d.kind === "aero-cl";
    const isV2 = d.kind === "univ2";
    if (!isAero && !isV2) continue;
    try {
      const len = Number(await client.readContract({ address: d.factory, abi: ENUM_ABI, functionName: isAero ? "allPoolsLength" : "allPairsLength" }));
      const n = Math.min(len, maxPer);
      const start = len - n; // newest first
      const res = await multicallChunked(client, cfg.multicall3, Array.from({ length: n }, (_, i) => ({ address: d.factory, abi: ENUM_ABI, functionName: isAero ? "allPools" : "allPairs", args: [BigInt(start + i)] })));
      let got = 0;
      for (const r of res) if (r.status === "success" && r.result !== zeroAddress) { addrs.push(r.result as Address); got++; }
      log.info({ dex: d.name, total: len, enumerated: got }, "factory enumerated");
    } catch (e) {
      log.warn({ dex: d.name, err: String(e).slice(0, 80) }, "factory enumeration failed");
    }
  }
  // tokens of every enumerated pool
  const t01 = await multicallChunked(client, cfg.multicall3, addrs.flatMap((a) => [{ address: a, abi: T01, functionName: "token0" }, { address: a, abi: T01, functionName: "token1" }]));
  const tokenSet = new Set<string>();
  const pairs: Array<[Address, Address]> = [];
  for (let i = 0; i < addrs.length; i++) {
    const a = t01[2 * i], b = t01[2 * i + 1];
    if (a?.status !== "success" || b?.status !== "success") continue;
    const t0 = a.result as Address, t1 = b.result as Address;
    tokenSet.add(t0.toLowerCase()); tokenSet.add(t1.toLowerCase()); pairs.push([t0, t1]);
  }
  const tokenAddrs = [...tokenSet] as Address[];
  const meta = await multicallChunked(client, cfg.multicall3, tokenAddrs.flatMap((a) => [{ address: a, abi: ERC20_ABI, functionName: "decimals" }, { address: a, abi: ERC20_ABI, functionName: "symbol" }]));
  const tokens: TokenConfig[] = [];
  const byAddr = new Map<string, TokenConfig>();
  tokenAddrs.forEach((a, i) => {
    const d = meta[2 * i], s = meta[2 * i + 1];
    if (d?.status !== "success") return;
    const t = { address: a, decimals: Number(d.result), symbol: s?.status === "success" ? String(s.result).slice(0, 12) : a.slice(0, 8) };
    tokens.push(t); byAddr.set(a.toLowerCase(), t);
  });
  const pairCfgs = pairs.map(([a, b]) => [byAddr.get(a.toLowerCase()), byAddr.get(b.toLowerCase())]).filter((p): p is [TokenConfig, TokenConfig] => !!p[0] && !!p[1]);
  const seen = new Set<string>();
  const uniq = pairCfgs.filter(([a, b]) => { const k = [a.address, b.address].map((x) => x.toLowerCase()).sort().join("-"); if (seen.has(k)) return false; seen.add(k); return true; });
  log.info({ enumeratedPools: addrs.length, tokens: tokens.length, pairs: uniq.length }, "universe enumerated; resolving every venue per pair");
  const pools = await discoverPools(client, cfg, tokens, uniq);
  return { tokens, pools };
}
