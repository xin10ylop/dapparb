/**
 * End-to-end pipeline test on an Anvil fork of Base:
 *   1. push a V3 pool with a large swap to manufacture a discrepancy,
 *   2. sync pool state from the fork and run the searcher,
 *   3. confirm the searcher finds the cycle through the pushed pool,
 *   4. deploy ArbExecutor on the fork, simulate the searcher's calldata and compare profit to the prediction.
 * Run: npx tsx --test src/arb/pipeline.fork.test.ts   (needs anvil on PATH)
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import { createPublicClient, createTestClient, createWalletClient, http, parseAbi, parseEther, encodeAbiParameters, type Address, type Hex } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";
import { BASE } from "../config/chains.js";
import { discoverPools } from "../pools/discovery.js";
import { loadStaticMetadata, pruneEmpty, syncPools } from "../pools/state.js";
import { findOpportunities } from "./search.js";
import { Executor } from "../exec/executor.js";

const RPC = "http://127.0.0.1:8552";
const PK = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80" as Hex;
const WETH = "0x4200000000000000000000000000000000000006" as Address;
const UNIV3_500 = "0xd0b53D9277642d899DF5C87A3966A349A798F224" as Address;

test("searcher finds a manufactured opportunity and the contract simulation matches", async (t) => {
  const anvil = spawn("anvil", ["--fork-url", process.env.FORK_RPC_URL ?? "https://base-mainnet.public.blastapi.io", "--port", "8552", "--silent"], { stdio: "ignore" });
  t.after(() => anvil.kill());
  const client = createPublicClient({ chain: base, transport: http(RPC) });
  for (let i = 0; i < 60; i++) {
    try {
      await client.getBlockNumber();
      break;
    } catch {
      await new Promise((r) => setTimeout(r, 1000));
    }
  }
  const testClient = createTestClient({ chain: base, mode: "anvil", transport: http(RPC) });
  const account = privateKeyToAccount(PK);
  const wallet = createWalletClient({ account, chain: base, transport: http(RPC) });

  // Deploy a tiny pusher contract that sells WETH into a V3 pool (pays in the callback).
  const pusherAbi = parseAbi(["function push(address pool, uint256 amount)", "function uniswapV3SwapCallback(int256,int256,bytes)"]);
  const pusherBytecode = fs.readFileSync(new URL("../../../contracts/out/Pusher.sol/Pusher.json", import.meta.url), "utf8");
  const pusherCode = JSON.parse(pusherBytecode).bytecode.object as Hex;
  const dh = await wallet.deployContract({ abi: pusherAbi, bytecode: pusherCode });
  const pusher = (await client.waitForTransactionReceipt({ hash: dh })).contractAddress!;
  // give the pusher 300 WETH by writing WETH.balanceOf storage (slot 3 for WETH9)
  const slot = (await import("viem")).keccak256(encodeAbiParameters([{ type: "address" }, { type: "uint256" }], [pusher, 3n]));
  await testClient.setStorageAt({ address: WETH, index: slot, value: ("0x" + parseEther("300").toString(16).padStart(64, "0")) as Hex });
  const ph = await wallet.writeContract({ address: pusher, abi: pusherAbi, functionName: "push", args: [UNIV3_500, parseEther("300")] });
  const pr = await client.waitForTransactionReceipt({ hash: ph });
  assert.equal(pr.status, "success", "push swap must succeed");

  // Deploy ArbExecutor on the fork.
  const execJson = JSON.parse(fs.readFileSync(new URL("../../../contracts/out/ArbExecutor.sol/ArbExecutor.json", import.meta.url), "utf8"));
  const eh = await wallet.deployContract({
    abi: execJson.abi,
    bytecode: execJson.bytecode.object as Hex,
    args: [BASE.flash.morphoBlue!, BASE.flash.aaveV3Pool!, BASE.flash.balancerV2Vault!],
  });
  const execAddr = (await client.waitForTransactionReceipt({ hash: eh })).contractAddress!;

  // Search on the fork state (WETH/USDC universe only for speed).
  // archive-capable upstream + a small DEX subset keep Anvil's slot fetching (and the test) fast
  const cfg = {
    ...BASE,
    rpcUrls: [RPC],
    dexes: BASE.dexes
      .filter((d) => ["UniswapV3", "AerodromeCL", "Aerodrome", "UniswapV2"].includes(d.name))
      .map((d) => (d.name === "UniswapV3" ? { ...d, tiers: [500] } : d.name === "AerodromeCL" ? { ...d, tiers: [100] } : d)),
  };
  const weth = BASE.tokens.find((x) => x.symbol === "WETH")!;
  const usdc = BASE.tokens.find((x) => x.symbol === "USDC")!;
  let pools = await discoverPools(client as any, cfg, [weth, usdc]);
  await loadStaticMetadata(client as any, cfg, pools);
  await syncPools(client as any, cfg, pools, { force: true });
  pools = pruneEmpty(pools);
  const opps = findOpportunities(pools);
  assert.ok(opps.length > 0, "must find opportunities after the push");
  const viaPushed = opps.filter((o) => o.hops.some((h) => h.pool.address.toLowerCase() === UNIV3_500.toLowerCase()));
  assert.ok(viaPushed.length > 0, "best opportunities must route through the pushed pool");
  const best = viaPushed[0]!;
  console.log(`best: ${best.hops.map((h) => h.pool.dex).join("->")} amountIn=${best.amountIn} predictedProfit=${best.profit} wei WETH gasEst=${best.gasEstimate}`);
  const USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
  assert.ok([WETH.toLowerCase(), USDC.toLowerCase()].includes(best.token.toLowerCase()), "profit token must be WETH or USDC");
  const wethStart = viaPushed.find((o) => o.token.toLowerCase() === WETH.toLowerCase());
  assert.ok(wethStart, "a WETH-denominated orientation must also be emitted");

  // Simulate the contract call with the searcher's calldata, from the owner (deployer).
  const ex = new Executor({ cfg, client: client as any, contract: execAddr, privateKey: PK, bidFraction: 0.5, maxPriorityGwei: 1, maxFeeGwei: 1, blocksValid: 2, minSimToPredictRatio: 0.8 });
  const sim = await ex.simulate(best, 1n);
  console.log("sim:", sim);
  if (!sim.ok) {
    try {
      await client.call({ account, to: execAddr, data: ex.calldata(best, 1n, 0n) });
    } catch (e: any) {
      console.log("RAW ERROR:", e?.message?.slice(0, 1500));
      console.log("CAUSE:", JSON.stringify(e?.cause ?? null, (_k, v) => (typeof v === "bigint" ? v.toString() : v)).slice(0, 1500));
    }
  }
  assert.ok(sim.ok, `simulation must succeed: ${sim.error}`);
  const ratio = Number(sim.profit!) / Number(best.profit);
  console.log(`simulated/predicted profit ratio = ${ratio.toFixed(6)}, gasUsed=${sim.gasUsed}`);
  assert.ok(ratio > 0.999 && ratio < 1.001, "on-chain profit must match local prediction to within 0.1%");

  // Actually send it on the fork and verify the profit lands in the contract.
  const erc20 = parseAbi(["function balanceOf(address) view returns (uint256)"]);
  const profitToken = best.token;
  const before = await client.readContract({ address: profitToken, abi: erc20, functionName: "balanceOf", args: [execAddr] });
  const sent = await ex.send(best, sim.profit! / 2n, sim, sim.profit!, await client.getBlockNumber());
  const rcpt = await client.waitForTransactionReceipt({ hash: sent.hash });
  assert.equal(rcpt.status, "success");
  const after = await client.readContract({ address: profitToken, abi: erc20, functionName: "balanceOf", args: [execAddr] });
  console.log(`landed: gasUsed=${rcpt.gasUsed} profit=${after - before} (wei of profit token)`);
  assert.equal(after - before, sim.profit);
});
