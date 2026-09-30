import { type Hex, keccak256, toHex } from "viem";
import { privateKeyToAccount, type PrivateKeyAccount } from "viem/accounts";

/**
 * Minimal Flashbots relay client (Ethereum mainnet). Bundles are simulated with eth_callBundle and submitted with
 * eth_sendBundle; a bundle that reverts is simply not included, so a lost race costs nothing — which is the only
 * sane way to run atomic arbitrage on mainnet, where public-mempool submissions get front-run or pay for reverts.
 * Requests are authenticated with the X-Flashbots-Signature header (a separate "searcher identity" key).
 */
export class FlashbotsClient {
  private readonly auth: PrivateKeyAccount;

  constructor(readonly relayUrl: string, authPrivateKey: Hex) {
    this.auth = privateKeyToAccount(authPrivateKey);
  }

  private async rpc(method: string, params: unknown[]): Promise<any> {
    const body = JSON.stringify({ jsonrpc: "2.0", id: 1, method, params });
    const sig = await this.auth.signMessage({ message: keccak256(toHex(body)) });
    const res = await fetch(this.relayUrl, {
      method: "POST",
      headers: { "content-type": "application/json", "X-Flashbots-Signature": `${this.auth.address}:${sig}` },
      body,
    });
    const j = (await res.json()) as { result?: any; error?: { message: string; code: number } };
    if (j.error) throw new Error(`${method}: ${j.error.message}`);
    return j.result;
  }

  /** Simulate a bundle on top of `stateBlock` as if included in `targetBlock`. */
  callBundle(signedTxs: Hex[], targetBlock: bigint, stateBlock: bigint | "latest" = "latest") {
    return this.rpc("eth_callBundle", [
      { txs: signedTxs, blockNumber: toHex(targetBlock), stateBlockNumber: stateBlock === "latest" ? "latest" : toHex(stateBlock) },
    ]);
  }

  /** Submit for inclusion in exactly `targetBlock`. Returns the bundle hash. */
  async sendBundle(signedTxs: Hex[], targetBlock: bigint, opts: { minTimestamp?: number; maxTimestamp?: number } = {}): Promise<Hex> {
    const r = await this.rpc("eth_sendBundle", [{ txs: signedTxs, blockNumber: toHex(targetBlock), ...opts }]);
    return r.bundleHash;
  }

  /** Inclusion stats for a submitted bundle. */
  getBundleStats(bundleHash: Hex, blockNumber: bigint) {
    return this.rpc("flashbots_getBundleStatsV2", [{ bundleHash, blockNumber: toHex(blockNumber) }]);
  }
}
