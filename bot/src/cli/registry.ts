/**
 * Build or refresh the activity pool registry without starting the searcher.
 *
 *   npx tsx src/cli/registry.ts --chain base --lookback 7200 [--logs-rpc https://mainnet.base.org] [--registry file]
 *   npx tsx src/cli/registry.ts --from 51866009 --to 51995608 --registry /tmp/reg-before.json   # a fixed window
 *
 * Scans the Swap logs of the window the registry does not cover yet (newer blocks, and older ones when the lookback
 * reaches further back), classifies new emitters and prints the registry summary (accepted pools per DEX, rejections
 * by reason with their swap counts).
 */
import "dotenv/config";
import { getChain } from "../config/chains.js";
import { makeHttpClient } from "../util/client.js";
import { refreshRegistry, registryPath } from "../pools/activity.js";

function arg(name: string, def?: string): string | undefined {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

const cfg = getChain(arg("chain", "base")!);
const client = makeHttpClient(cfg);
const lookback = Number(arg("lookback", "7200"));
const file = arg("registry", registryPath(cfg))!;
const logsUrl = arg("logs-rpc", process.env.LOGS_RPC_URL ?? cfg.rpcUrls[0])!;

const from = arg("from"), to = arg("to");
refreshRegistry(client, cfg, file, lookback, logsUrl, from && to ? { from: Number(from), to: Number(to) } : undefined)
  .then(() => process.exit(0))
  .catch((e) => {
    console.error(e);
    process.exit(1);
  });
