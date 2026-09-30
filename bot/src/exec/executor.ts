import {
  type Address,
  type Hex,
  type PublicClient,
  type Chain,
  type Transport,
  createWalletClient,
  http,
  encodeFunctionData,
  decodeErrorResult,
  BaseError,
  ContractFunctionRevertedError,
  formatEther,
} from "viem";
import { privateKeyToAccount, type PrivateKeyAccount } from "viem/accounts";
import type { ChainConfig } from "../config/chains.js";
import { ARB_EXECUTOR_ABI } from "../abi.js";
import type { Opportunity } from "../arb/search.js";
import { isV2, type Pool } from "../pools/types.js";
import { viemChain } from "../util/client.js";
import { log } from "../util/log.js";

export const KIND_UNIV2 = 0;
export const KIND_AERO_V2 = 1;
export const KIND_V3 = 2;
export const KIND_PANCAKE_V3 = 3;

export interface ContractHop {
  pool: Address;
  kind: number;
  zeroForOne: boolean;
  tokenIn: Address;
  tokenOut: Address;
  amountOut: bigint;
  feeBps: number;
}

export function contractKind(pool: Pool): number {
  switch (pool.kind) {
    case "univ2":
      return KIND_UNIV2;
    case "aero-v2":
      return KIND_AERO_V2;
    case "univ3":
    case "aero-cl":
      return KIND_V3;
    case "pancake-v3":
      return KIND_PANCAKE_V3;
  }
}

export function toContractHops(opp: Opportunity): ContractHop[] {
  return opp.hops.map((h, i) => ({
    pool: h.pool.address,
    kind: contractKind(h.pool),
    zeroForOne: h.tokenIn.toLowerCase() === h.pool.token0.toLowerCase(),
    tokenIn: h.tokenIn,
    tokenOut: h.tokenOut,
    // Hop 0 on a V2-style pool: pass the exact output we computed so the pair sends it before the callback.
    amountOut: i === 0 && isV2(h.pool) ? h.amountOut : 0n,
    feeBps: isV2(h.pool) ? h.pool.feeBps : 0,
  }));
}

export interface SimResult {
  ok: boolean;
  profit?: bigint;
  gasUsed?: bigint;
  error?: string;
  latencyMs: number;
}

export interface ExecutorOptions {
  cfg: ChainConfig;
  client: PublicClient<Transport, Chain>;
  contract: Address;
  privateKey?: Hex;
  /** Extra RPC URLs to broadcast the raw transaction to in parallel (e.g. the sequencer). */
  submitRpcUrls?: string[];
  /** Fraction (0..1) of the simulated net profit to bid as priority fee. */
  bidFraction: number;
  maxPriorityGwei: number;
  maxFeeGwei: number;
  /** Transaction is valid for this many blocks after the current one. */
  blocksValid: number;
  /** Require the simulated profit to be at least this fraction of the locally predicted profit. */
  minSimToPredictRatio: number;
  /**
   * Dry-run without a deployment: runtime bytecode injected at `contract` via eth_call state override.
   * With an empty storage the contract's owner is address(0), which is also eth_call's default sender,
   * so `onlyExecutor` passes. Immutables (flash-loan providers) are baked into the runtime code.
   */
  codeOverride?: Hex;
}

export interface SendResult {
  hash: Hex;
  nonce: number;
  priorityFeeGwei: number;
  maxBlock: bigint;
}

/**
 * Builds, simulates and submits ArbExecutor transactions. Simulation is an eth_call from the executor
 * address at the latest (or pending) state; the contract's own revert reasons are decoded so that an
 * unprofitable route is distinguishable from an RPC or nonce problem.
 */
export class Executor {
  readonly account: PrivateKeyAccount | null;
  private readonly wallet;
  private nonce: number | null = null;
  private owner: Address | null = null;

  constructor(readonly opts: ExecutorOptions) {
    this.account = opts.privateKey ? privateKeyToAccount(opts.privateKey) : null;
    this.wallet = this.account
      ? createWalletClient({ account: this.account, chain: viemChain(opts.cfg), transport: http(opts.cfg.rpcUrls[0]) })
      : null;
  }

  /** Address used as `from` for simulation: the hot wallet, or the contract owner in dry-run mode. */
  async fromAddress(): Promise<Address> {
    if (this.opts.codeOverride) return "0x0000000000000000000000000000000000000000";
    if (this.account) return this.account.address;
    if (!this.owner) this.owner = await this.opts.client.readContract({ address: this.opts.contract, abi: ARB_EXECUTOR_ABI, functionName: "owner" });
    return this.owner;
  }

  calldata(opp: Opportunity, minProfit: bigint, maxBlock: bigint): Hex {
    return encodeFunctionData({
      abi: ARB_EXECUTOR_ABI,
      functionName: "execute",
      args: [toContractHops(opp), opp.amountIn, minProfit, maxBlock],
    });
  }

  async simulate(opp: Opportunity, minProfit: bigint, blockTag: "latest" | "pending" = "latest"): Promise<SimResult> {
    const t0 = Date.now();
    const from = await this.fromAddress();
    const data = this.calldata(opp, minProfit, 0n);
    const stateOverride = this.opts.codeOverride ? [{ address: this.opts.contract, code: this.opts.codeOverride }] : undefined;
    try {
      const call = await this.opts.client.call({ account: from, to: this.opts.contract, data, blockTag, stateOverride });
      const profit = call.data ? BigInt(call.data) : 0n;
      // Gas estimate is best-effort (some RPCs reject estimateGas with overrides); fall back to the local estimate.
      const gas = await this.opts.client.estimateGas({ account: from, to: this.opts.contract, data, blockTag, stateOverride }).catch(() => 0n);
      return { ok: true, profit, gasUsed: gas, latencyMs: Date.now() - t0 };
    } catch (e) {
      const msg = decodeRevert(e);
      if (process.env.LOG_LEVEL === "debug") log.debug({ err: e instanceof Error ? e.message.slice(0, 600) : String(e).slice(0, 600) }, "simulate raw error");
      return { ok: false, error: msg, latencyMs: Date.now() - t0 };
    }
  }

  async refreshNonce(): Promise<number> {
    if (!this.account) throw new Error("no signer");
    this.nonce = await this.opts.client.getTransactionCount({ address: this.account.address, blockTag: "pending" });
    return this.nonce;
  }

  /**
   * Sign and broadcast. Priority fee = min(cap, bidFraction * netProfit / gas). On OP-stack chains the
   * base fee is negligible and the priority fee is the entire ordering auction.
   */
  async send(opp: Opportunity, minProfit: bigint, sim: SimResult, netProfitWei: bigint, currentBlock: bigint): Promise<SendResult> {
    if (!this.account || !this.wallet) throw new Error("executor has no signer (dry-run mode)");
    if (this.nonce === null) await this.refreshNonce();
    const gasUsed = sim.gasUsed && sim.gasUsed > 0n ? sim.gasUsed : opp.gasEstimate;
    const gasLimit = (gasUsed * 125n) / 100n;
    const block = await this.opts.client.getBlock({ blockTag: "latest" });
    const baseFee = block.baseFeePerGas ?? 0n;
    const bidWei = (netProfitWei * BigInt(Math.round(this.opts.bidFraction * 1000))) / 1000n;
    let priority = bidWei / gasUsed;
    const maxPriority = BigInt(Math.round(this.opts.maxPriorityGwei * 1e9));
    if (priority > maxPriority) priority = maxPriority;
    if (priority < 1n) priority = 1n;
    let maxFee = baseFee * 2n + priority;
    const maxFeeCap = BigInt(Math.round(this.opts.maxFeeGwei * 1e9));
    if (maxFee > maxFeeCap) maxFee = maxFeeCap;
    const maxBlock = currentBlock + BigInt(this.opts.blocksValid);
    const nonce = this.nonce!;
    const signed = await this.wallet.signTransaction({
      account: this.account,
      chain: viemChain(this.opts.cfg),
      to: this.opts.contract,
      data: this.calldata(opp, minProfit, maxBlock),
      gas: gasLimit,
      maxFeePerGas: maxFee,
      maxPriorityFeePerGas: priority,
      nonce,
      value: 0n,
      type: "eip1559",
    });
    this.nonce = nonce + 1;
    const urls = [this.opts.cfg.rpcUrls[0]!, ...(this.opts.submitRpcUrls ?? [])];
    const results = await Promise.allSettled(urls.map((u) => rawSend(u, signed)));
    const hash = results.find((r): r is PromiseFulfilledResult<Hex> => r.status === "fulfilled")?.value;
    if (!hash) {
      this.nonce = null; // resync on next send
      throw new Error(`broadcast failed on all endpoints: ${results.map((r) => (r.status === "rejected" ? String(r.reason).slice(0, 120) : "ok")).join(" | ")}`);
    }
    log.info({ hash, nonce, priorityGwei: Number(priority) / 1e9, gasLimit: Number(gasLimit), maxBlock: Number(maxBlock), profitEth: formatEther(netProfitWei) }, "tx broadcast");
    return { hash, nonce, priorityFeeGwei: Number(priority) / 1e9, maxBlock };
  }
}

async function rawSend(url: string, signed: Hex): Promise<Hex> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "eth_sendRawTransaction", params: [signed] }),
  });
  const j = (await res.json()) as { result?: Hex; error?: { message: string } };
  if (j.error) throw new Error(j.error.message);
  return j.result!;
}

export function decodeRevert(e: unknown): string {
  if (e instanceof BaseError) {
    const revert = e.walk((err) => err instanceof ContractFunctionRevertedError) as ContractFunctionRevertedError | null;
    if (revert?.data) return `${revert.data.errorName}(${(revert.data.args ?? []).map(String).join(",")})`;
    const raw = (e as any).cause?.data ?? (e as any).data;
    if (typeof raw === "string" && raw.startsWith("0x") && raw.length >= 10) {
      try {
        const d = decodeErrorResult({ abi: ARB_EXECUTOR_ABI, data: raw as Hex });
        return `${d.errorName}(${(d.args ?? []).map(String).join(",")})`;
      } catch {
        /* fallthrough */
      }
    }
    return e.shortMessage.slice(0, 200);
  }
  return String(e).slice(0, 200);
}
