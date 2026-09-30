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

export async function fetchTopPools(cfg: ChainConfig, pages = 5): Promise<GtPool[]> {
  const net = GT_NETWORK[cfg.id];
  if (!net) throw new Error(`no GeckoTerminal network for chain ${cfg.id}`);
  const out: GtPool[] = [];
  for (let page = 1; page <= pages; page++) {
    const url = `https://api.geckoterminal.com/api/v2/networks/${net}/pools?page=${page}&sort=h24_volume_usd_desc`;
    const res = await fetch(url, { headers: { accept: "application/json" } });
    if (!res.ok) {
      log.warn({ status: res.status, page }, "geckoterminal request failed");
      break;
    }
    const j = (await res.json()) as any;
    for (const p of j.data ?? []) {
      const a = p.attributes;
      const base = String(p.relationships?.base_token?.data?.id ?? "").split("_")[1];
      const quote = String(p.relationships?.quote_token?.data?.id ?? "").split("_")[1];
      if (!base || !quote || !isAddress(base) || !isAddress(quote) || !isAddress(a.address)) continue;
      out.push({
        address: getAddress(a.address),
        name: a.name,
        dex: p.relationships?.dex?.data?.id ?? "?",
        volume24h: Number(a.volume_usd?.h24 ?? 0),
        reserveUsd: Number(a.reserve_in_usd ?? 0),
        baseToken: getAddress(base),
        quoteToken: getAddress(quote),
      });
    }
    await new Promise((r) => setTimeout(r, 700)); // free-tier rate limit (30 req/min)
  }
  return out;
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
