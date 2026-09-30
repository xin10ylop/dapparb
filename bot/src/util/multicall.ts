import type { Address, PublicClient } from "viem";

export interface McCall {
  address: Address;
  abi: any;
  functionName: string;
  args?: readonly unknown[];
}
export type McResult = { status: "success"; result: unknown } | { status: "failure"; error: unknown };

/** Number of chunk-level RPC failures (whole batches rejected, e.g. HTTP 429) in the last multicallChunked call. */
export const mcStats = { lastChunkFailures: 0, lastChunks: 0 };

/**
 * Multicall3 wrapper that splits large call sets into fixed-size chunks and runs them with bounded
 * concurrency. Public RPCs reject oversized JSON-RPC batches wholesale; viem's byte-based batching alone
 * does not protect against that. A failed chunk is retried once at half size before its calls are marked failed.
 */
export async function multicallChunked(
  client: PublicClient,
  multicallAddress: Address,
  calls: McCall[],
  opts: { chunk?: number; concurrency?: number; blockNumber?: bigint; blockTag?: "pending" | "latest" } = {},
): Promise<McResult[]> {
  const chunk = opts.chunk ?? 300;
  const concurrency = opts.concurrency ?? 4;
  const out: McResult[] = new Array(calls.length);
  const ranges: Array<[number, number]> = [];
  for (let i = 0; i < calls.length; i += chunk) ranges.push([i, Math.min(i + chunk, calls.length)]);

  async function run(lo: number, hi: number, depth: number): Promise<void> {
    try {
      const res = await client.multicall({
        contracts: calls.slice(lo, hi) as any,
        allowFailure: true,
        multicallAddress,
        batchSize: 0, // one eth_call per chunk; we control chunking here
        ...(opts.blockNumber !== undefined ? { blockNumber: opts.blockNumber } : opts.blockTag ? { blockTag: opts.blockTag } : {}),
      } as any);
      for (let i = 0; i < res.length; i++) out[lo + i] = res[i] as McResult;
    } catch (e) {
      if (depth < 2 && hi - lo > 25) {
        const mid = (lo + hi) >> 1;
        await run(lo, mid, depth + 1);
        await run(mid, hi, depth + 1);
      } else {
        mcStats.lastChunkFailures++;
        for (let i = lo; i < hi; i++) out[i] = { status: "failure", error: e };
      }
    }
  }

  mcStats.lastChunkFailures = 0;
  mcStats.lastChunks = ranges.length;
  let next = 0;
  const workers = Array.from({ length: Math.min(concurrency, ranges.length) }, async () => {
    while (next < ranges.length) {
      const [lo, hi] = ranges[next++]!;
      await run(lo, hi, 0);
    }
  });
  await Promise.all(workers);
  return out;
}
