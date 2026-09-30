/**
 * Long-tail token universe discovery via GeckoTerminal's public API: pulls the top pools by 24h volume
 * for a network and returns the distinct ERC-20 tokens involved (with decimals fetched on-chain).
 */
import type { Address, PublicClient } from "viem";
import { getAddress, isAddress } from "viem";
import type { ChainConfig, TokenConfig } from "../config/chains.js";
import { ERC20_ABI } from "../abi.js";
import { multicallChunked } from "../util/multicall.js";
import { log } from "../util/log.js";

const GT_NETWORK: Record<number, string> = { 8453: "base", 42161: "arbitrum", 1: "eth" };

export interface GtPool {
  address: Address;
  name: string;
  dex: string;
  volume24h: number;
  reserveUsd: number;
  baseToken: Address;
  quoteToken: Address;
}

/** GeckoTerminal DEX ids whose pools we can price locally (per chain). */
const GT_DEXES: Record<number, string[]> = {
  8453: ["uniswap-v4-base", "aerodrome-slipstream-3", "aerodrome-slipstream", "aerodrome-slipstream-2", "uniswap-v3-base", "pancakeswap-v3-base", "sushiswap-v3-base", "aerodrome-base", "uniswap-v2-base", "sushiswap-v2-base", "pancakeswap-v2-base", "baseswap"],
  42161: ["uniswap-v3-arbitrum", "sushiswap-v3-arbitrum", "pancakeswap-v3-arbitrum", "sushiswap-arbitrum"],
  1: ["uniswap-v3", "sushiswap-v3-ethereum", "pancakeswap-v3-ethereum", "uniswap-v2", "sushiswap"],
};

const gtCache = new Map<string, { at: number; pools: GtPool[] }>();

export async function fetchTopPools(cfg: ChainConfig, pages = 5): Promise<GtPool[]> {
  const cacheKey = `${cfg.id}:${pages}`;
  const cached = gtCache.get(cacheKey);
  if (cached && Date.now() - cached.at < 10 * 60_000) return cached.pools;
  const pools = await fetchTopPoolsUncached(cfg, pages);
  gtCache.set(cacheKey, { at: Date.now(), pools });
  return pools;
}

async function fetchTopPoolsUncached(cfg: ChainConfig, pages: number): Promise<GtPool[]> {
  const net = GT_NETWORK[cfg.id];
  if (!net) throw new Error(`no GeckoTerminal network for chain ${cfg.id}`);
  const out: GtPool[] = [];
  const urls: string[] = [];
  for (let page = 1; page <= pages; page++) urls.push(`https://api.geckoterminal.com/api/v2/networks/${net}/pools?page=${page}&sort=h24_volume_usd_desc`);
  // per-DEX listings reach much deeper into the long tail than the network-wide top list
  const perDexPages = Math.max(1, Math.ceil(pages / 2));
  for (const dex of GT_DEXES[cfg.id] ?? []) for (let page = 1; page <= perDexPages; page++) urls.push(`https://api.geckoterminal.com/api/v2/networks/${net}/dexes/${dex}/pools?page=${page}&sort=h24_volume_usd_desc`);
  for (const url of urls) {
    let res = await fetch(url, { headers: { accept: "application/json" } });
    if (res.status === 429) {
      await new Promise((r) => setTimeout(r, 15_000));
      res = await fetch(url, { headers: { accept: "application/json" } });
    }
    if (!res.ok) {
      log.warn({ status: res.status, url }, "geckoterminal request failed");
      continue;
    }
    const j = (await res.json()) as any;
    for (const p of j.data ?? []) {
      const a = p.attributes;
      const base = String(p.relationships?.base_token?.data?.id ?? "").split("_")[1];
      const quote = String(p.relationships?.quote_token?.data?.id ?? "").split("_")[1];
      const isV4Id = /^0x[0-9a-f]{64}$/i.test(String(a.address));
      if (!base || !quote || !isAddress(base) || !isAddress(quote) || (!isAddress(a.address) && !isV4Id)) continue;
      out.push({
        address: (isV4Id ? String(a.address).toLowerCase() : getAddress(a.address)) as Address,
        name: a.name,
        dex: p.relationships?.dex?.data?.id ?? "?",
        volume24h: Number(a.volume_usd?.h24 ?? 0),
        reserveUsd: Number(a.reserve_in_usd ?? 0),
        baseToken: getAddress(base),
        quoteToken: getAddress(quote),
      });
    }
    await new Promise((r) => setTimeout(r, 2100)); // free-tier rate limit (30 req/min)
  }
  const seen = new Set<string>();
  const dedup = out.filter((p) => (seen.has(p.address.toLowerCase()) ? false : (seen.add(p.address.toLowerCase()), true)));
  log.info({ requests: urls.length, pools: dedup.length }, "geckoterminal pools fetched");
  return dedup;
}

/** Distinct tokens from the top pools, with decimals/symbol read on-chain. Keeps the configured tokens first. */
export async function buildTokenUniverse(client: PublicClient, cfg: ChainConfig, pages = 5, maxTokens = 250): Promise<TokenConfig[]> {
  const pools = await fetchTopPools(cfg, pages);
  const known = new Map(cfg.tokens.map((t) => [t.address.toLowerCase(), t] as const));
  const volByToken = new Map<string, number>();
  for (const p of pools) {
    for (const t of [p.baseToken, p.quoteToken]) volByToken.set(t.toLowerCase(), (volByToken.get(t.toLowerCase()) ?? 0) + p.volume24h);
  }
  const candidates = [...volByToken.entries()]
    .filter(([a]) => !known.has(a))
    .sort((x, y) => y[1] - x[1])
    .slice(0, maxTokens)
    .map(([a]) => getAddress(a));
  const calls = candidates.flatMap((a) => [
    { address: a, abi: ERC20_ABI, functionName: "decimals" },
    { address: a, abi: ERC20_ABI, functionName: "symbol" },
  ]);
  const res = await multicallChunked(client, cfg.multicall3, calls);
  const extra: TokenConfig[] = [];
  candidates.forEach((a, i) => {
    const d = res[2 * i];
    const s = res[2 * i + 1];
    if (d?.status !== "success") return;
    extra.push({ address: a, decimals: Number(d.result), symbol: s?.status === "success" ? String(s.result) : a.slice(0, 8) });
  });
  log.info({ topPools: pools.length, newTokens: extra.length }, "token universe built");
  return [...cfg.tokens, ...extra];
}
