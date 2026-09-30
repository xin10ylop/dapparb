import { parseAbi } from "viem";

export const ERC20_ABI = parseAbi([
  "function balanceOf(address) view returns (uint256)",
  "function decimals() view returns (uint8)",
  "function symbol() view returns (string)",
  "function allowance(address,address) view returns (uint256)",
  "function approve(address,uint256) returns (bool)",
  "function transfer(address,uint256) returns (bool)",
]);

export const UNIV3_FACTORY_ABI = parseAbi(["function getPool(address,address,uint24) view returns (address)"]);
export const AERO_CL_FACTORY_ABI = parseAbi(["function getPool(address,address,int24) view returns (address)"]);
export const UNIV2_FACTORY_ABI = parseAbi(["function getPair(address,address) view returns (address)"]);
export const AERO_FACTORY_ABI = parseAbi([
  "function getPool(address,address,bool) view returns (address)",
  "function getFee(address,bool) view returns (uint256)",
]);

/** Works for Uniswap V3, Sushi V3, Pancake V3 and Slipstream: we only decode the first two slot0 words. */
export const V3_POOL_ABI = parseAbi([
  "function slot0() view returns (uint160 sqrtPriceX96, int24 tick)",
  "function liquidity() view returns (uint128)",
  "function fee() view returns (uint24)",
  "function tickSpacing() view returns (int24)",
  "function token0() view returns (address)",
  "function token1() view returns (address)",
  "function tickBitmap(int16) view returns (uint256)",
  "function ticks(int24) view returns (uint128 liquidityGross, int128 liquidityNet)",
]);

export const V2_PAIR_ABI = parseAbi([
  "function getReserves() view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)",
  "function token0() view returns (address)",
  "function token1() view returns (address)",
]);

export const AERO_POOL_ABI = parseAbi([
  "function getReserves() view returns (uint256 reserve0, uint256 reserve1, uint256 blockTimestampLast)",
  "function token0() view returns (address)",
  "function token1() view returns (address)",
  "function stable() view returns (bool)",
  "function getAmountOut(uint256 amountIn, address tokenIn) view returns (uint256)",
]);

export const QUOTER_V2_ABI = parseAbi([
  "struct QuoteExactInputSingleParams { address tokenIn; address tokenOut; uint256 amountIn; uint24 fee; uint160 sqrtPriceLimitX96; }",
  "function quoteExactInputSingle(QuoteExactInputSingleParams params) returns (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedTicksCrossed, uint256 gasEstimate)",
]);

/** Slipstream quoter keys by tickSpacing instead of fee. */
export const AERO_CL_QUOTER_ABI = parseAbi([
  "struct QuoteExactInputSingleParams { address tokenIn; address tokenOut; uint256 amountIn; int24 tickSpacing; uint160 sqrtPriceLimitX96; }",
  "function quoteExactInputSingle(QuoteExactInputSingleParams params) returns (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedTicksCrossed, uint256 gasEstimate)",
]);

export const MULTICALL3_ABI = parseAbi([
  "struct Call3 { address target; bool allowFailure; bytes callData; }",
  "struct Result { bool success; bytes returnData; }",
  "function aggregate3(Call3[] calls) payable returns (Result[] returnData)",
  "function getCurrentBlockTimestamp() view returns (uint256)",
]);

export const OP_GAS_ORACLE_ABI = parseAbi([
  "function getL1Fee(bytes) view returns (uint256)",
  "function l1BaseFee() view returns (uint256)",
]);

export const ARB_EXECUTOR_ABI = parseAbi([
  "struct Hop { address pool; uint8 kind; bool zeroForOne; address tokenIn; address tokenOut; uint256 amountOut; uint16 feeBps; uint24 fee; int24 tickSpacing; address hooks; }",
  "function execute(Hop[] hops, uint256 amountIn, uint256 minProfit, uint256 maxBlock) returns (uint256 profit)",
  "function executeFlashLoan(uint8 provider, Hop[] hops, uint256 amountIn, uint256 minProfit, uint256 maxBlock) returns (uint256 profit)",
  "function withdraw(address token, uint256 amount, address to)",
  "function owner() view returns (address)",
  "function executors(address) view returns (bool)",
  "function setExecutor(address,bool)",
  "event Executed(address indexed token, uint256 amountIn, uint256 profit, uint8 hops)",
  "error NotOwner()",
  "error NotExecutor()",
  "error BadCaller()",
  "error BadRoute()",
  "error Expired(uint256 blockNumber, uint256 maxBlock)",
  "error InsufficientProfit(int256 got, uint256 want)",
  "error CannotRepay(uint256 have, uint256 owed)",
  "error TransferFailed()",
  "error BadProvider()",
]);
