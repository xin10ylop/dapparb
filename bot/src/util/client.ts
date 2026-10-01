import { createPublicClient, fallback, http, webSocket, type PublicClient, type Transport, type Chain } from "viem";
import { base, arbitrum, mainnet } from "viem/chains";
import type { ChainConfig } from "../config/chains.js";

const VIEM_CHAINS: Record<number, Chain> = { 8453: base, 42161: arbitrum, 1: mainnet };

export function viemChain(cfg: ChainConfig): Chain {
  const c = VIEM_CHAINS[cfg.id];
  if (!c) throw new Error(`no viem chain for id ${cfg.id}`);
  return c;
}

/** HTTP client with fallback across configured RPCs. Batches JSON-RPC requests issued within 10ms. */
export function makeHttpClient(cfg: ChainConfig): PublicClient<Transport, Chain> {
  const transports = cfg.rpcUrls.map((u) => http(u, { batch: { batchSize: 100, wait: 10 }, timeout: 20_000, retryCount: 2 }));
  return createPublicClient({ chain: viemChain(cfg), transport: fallback(transports, { rank: false }) });
}

export function makeWsClient(cfg: ChainConfig): PublicClient<Transport, Chain> | null {
  // NO_WS=1: no websocket; callers fall back to polling eth_blockNumber over HTTP (for networks that cannot upgrade to ws).
  if (process.env.NO_WS === "1") return null;
  const url = cfg.wsUrls?.[0];
  if (!url) return null;
  return createPublicClient({ chain: viemChain(cfg), transport: webSocket(url, { reconnect: true, timeout: 20_000 }) });
}
