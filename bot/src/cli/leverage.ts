/**
 * Build & (optionally) send LeverageManager transactions with a Uniswap V3 SwapRouter02 route.
 *
 *   npx tsx src/cli/leverage.ts open-long  --manager 0x.. --user-usdc 2000 --flash-usdc 2000 [--fee 500] [--min-hf 1.3]
 *   npx tsx src/cli/leverage.ts open-short --manager 0x.. --user-weth 1    --flash-weth 1
 *   npx tsx src/cli/leverage.ts status     --manager 0x.. --user 0x..
 *   npx tsx src/cli/leverage.ts close-long --manager 0x.. --collateral-to-swap-weth 0.8
 * Without PRIVATE_KEY the CLI prints the calldata and the approvals the user must grant first.
 */
import "dotenv/config";
import { createPublicClient, createWalletClient, encodeFunctionData, formatEther, formatUnits, http, parseAbi, parseEther, parseUnits, type Address, type Hex } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

const WETH: Address = "0x4200000000000000000000000000000000000006";
const USDC: Address = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const AAVE_POOL: Address = "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5";
const ROUTER: Address = "0x2626664c2603336E57B271c5C0b26F421741e481";

const ROUTER_ABI = parseAbi([
  "struct ExactInputSingleParams { address tokenIn; address tokenOut; uint24 fee; address recipient; uint256 amountIn; uint256 amountOutMinimum; uint160 sqrtPriceLimitX96; }",
  "function exactInputSingle(ExactInputSingleParams params) payable returns (uint256 amountOut)",
]);
const LEV_ABI = parseAbi([
  "struct Swap { address target; address spender; bytes data; uint256 minOut; }",
  "struct OpenParams { address collateralAsset; address debtAsset; uint256 userAmount; uint256 flashAmount; uint256 minHealthFactor; Swap swap; }",
  "struct CloseParams { address collateralAsset; address debtAsset; uint256 debtToRepay; uint256 collateralToWithdraw; Swap swap; uint256 collateralToSwap; }",
  "function open(OpenParams p)",
  "function close(CloseParams p)",
]);
const AAVE_ABI = parseAbi([
  "function getUserAccountData(address) view returns (uint256 totalCollateralBase, uint256 totalDebtBase, uint256 availableBorrowsBase, uint256 currentLiquidationThreshold, uint256 ltv, uint256 healthFactor)",
  "function getReserveData(address) view returns ((uint256 configuration, uint128 liquidityIndex, uint128 currentLiquidityRate, uint128 variableBorrowIndex, uint128 currentVariableBorrowRate, uint128 currentStableBorrowRate, uint40 lastUpdateTimestamp, uint16 id, address aTokenAddress, address stableDebtTokenAddress, address variableDebtTokenAddress, address interestRateStrategyAddress, uint128 accruedToTreasury, uint128 unbacked, uint128 isolationModeTotalDebt))",
]);
const ERC20 = parseAbi(["function balanceOf(address) view returns (uint256)", "function approve(address,uint256) returns (bool)", "function approveDelegation(address,uint256)"]);

const arg = (n: string, d?: string) => {
  const i = process.argv.indexOf(`--${n}`);
  return i >= 0 ? process.argv[i + 1]! : d;
};
const cmd = process.argv[2];
const manager = arg("manager") as Address | undefined;
const client = createPublicClient({ chain: base, transport: http(process.env.BASE_RPC_URL ?? "https://base-rpc.publicnode.com") });
const pk = process.env.PRIVATE_KEY as Hex | undefined;
const account = pk ? privateKeyToAccount(pk) : null;
const wallet = account ? createWalletClient({ account, chain: base, transport: http(process.env.BASE_RPC_URL ?? "https://base-rpc.publicnode.com") }) : null;

function swapData(tokenIn: Address, tokenOut: Address, fee: number, amountIn: bigint, recipient: Address): Hex {
  return encodeFunctionData({ abi: ROUTER_ABI, functionName: "exactInputSingle", args: [{ tokenIn, tokenOut, fee, recipient, amountIn, amountOutMinimum: 0n, sqrtPriceLimitX96: 0n }] });
}

async function reserves() {
  const [w, u] = await Promise.all([
    client.readContract({ address: AAVE_POOL, abi: AAVE_ABI, functionName: "getReserveData", args: [WETH] }),
    client.readContract({ address: AAVE_POOL, abi: AAVE_ABI, functionName: "getReserveData", args: [USDC] }),
  ]);
  return { aWETH: w.aTokenAddress, vdWETH: w.variableDebtTokenAddress, aUSDC: u.aTokenAddress, vdUSDC: u.variableDebtTokenAddress };
}

async function main() {
  if (!manager && cmd !== "help") throw new Error("--manager required");
  const r = await reserves();
  if (cmd === "status") {
    const user = (arg("user") ?? account?.address) as Address;
    const d = await client.readContract({ address: AAVE_POOL, abi: AAVE_ABI, functionName: "getUserAccountData", args: [user] });
    const [aW, aU, vW, vU] = await Promise.all([r.aWETH, r.aUSDC, r.vdWETH, r.vdUSDC].map((t) => client.readContract({ address: t, abi: ERC20, functionName: "balanceOf", args: [user] })));
    console.log({ user, collateralUsd: Number(d[0]) / 1e8, debtUsd: Number(d[1]) / 1e8, healthFactor: Number(d[5]) / 1e18, aWETH: formatEther(aW!), aUSDC: formatUnits(aU!, 6), debtWETH: formatEther(vW!), debtUSDC: formatUnits(vU!, 6) });
    return;
  }
  const fee = Number(arg("fee", "500"));
  const minHf = parseEther(arg("min-hf", "1.3")!);
  let data: Hex;
  let approvals: string[] = [];
  if (cmd === "open-long") {
    const userUsdc = parseUnits(arg("user-usdc", "0")!, 6);
    const flashUsdc = parseUnits(arg("flash-usdc", "0")!, 6);
    data = encodeFunctionData({ abi: LEV_ABI, functionName: "open", args: [{ collateralAsset: WETH, debtAsset: USDC, userAmount: userUsdc, flashAmount: flashUsdc, minHealthFactor: minHf, swap: { target: ROUTER, spender: ROUTER, data: swapData(USDC, WETH, fee, userUsdc + flashUsdc, manager!), minOut: 0n } }] });
    approvals = [`USDC.approve(${manager}, ${userUsdc})`, `VariableDebtUSDC(${r.vdUSDC}).approveDelegation(${manager}, ${flashUsdc})`];
  } else if (cmd === "open-short") {
    const userWeth = parseEther(arg("user-weth", "0")!);
    const flashWeth = parseEther(arg("flash-weth", "0")!);
    data = encodeFunctionData({ abi: LEV_ABI, functionName: "open", args: [{ collateralAsset: USDC, debtAsset: WETH, userAmount: userWeth, flashAmount: flashWeth, minHealthFactor: minHf, swap: { target: ROUTER, spender: ROUTER, data: swapData(WETH, USDC, fee, userWeth + flashWeth, manager!), minOut: 0n } }] });
    approvals = [`WETH.approve(${manager}, ${userWeth})`, `VariableDebtWETH(${r.vdWETH}).approveDelegation(${manager}, ${flashWeth})`];
  } else if (cmd === "close-long") {
    const user = (arg("user") ?? account?.address) as Address;
    const debt = await client.readContract({ address: r.vdUSDC, abi: ERC20, functionName: "balanceOf", args: [user] });
    const coll = await client.readContract({ address: r.aWETH, abi: ERC20, functionName: "balanceOf", args: [user] });
    const toSwap = parseEther(arg("collateral-to-swap-weth")!);
    data = encodeFunctionData({ abi: LEV_ABI, functionName: "close", args: [{ collateralAsset: WETH, debtAsset: USDC, debtToRepay: (debt * 10001n) / 10000n, collateralToWithdraw: coll, swap: { target: ROUTER, spender: ROUTER, data: swapData(WETH, USDC, fee, toSwap, manager!), minOut: (debt * 10006n) / 10000n }, collateralToSwap: toSwap }] });
    approvals = [`aWETH(${r.aWETH}).approve(${manager}, ${coll})`];
    console.log({ debtUSDC: formatUnits(debt, 6), collateralWETH: formatEther(coll), sellingWETH: formatEther(toSwap) });
  } else {
    console.log("commands: open-long | open-short | close-long | status");
    return;
  }
  console.log("required approvals first:", approvals);
  console.log("calldata:", data);
  if (wallet && account && arg("send") === "1") {
    const hash = await wallet.sendTransaction({ to: manager!, data });
    console.log("sent", hash);
    const rc = await client.waitForTransactionReceipt({ hash });
    console.log("status", rc.status, "gasUsed", rc.gasUsed);
  }
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
