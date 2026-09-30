import type { Address } from "viem";

export type DexKind =
  | "univ2" // Uniswap V2 & exact forks (Sushi V2). Fee applied as amountIn*(10000-fee)/10000 inside the formula.
  | "aero-v2" // Aerodrome / Velodrome V2-style pools (volatile + stable), fee read from factory, `hook` callback.
  | "univ3" // Uniswap V3 & exact forks (Sushi V3), uniswapV3SwapCallback.
  | "aero-cl" // Aerodrome Slipstream (V3 fork keyed by tickSpacing, dynamic fee, uniswapV3SwapCallback).
  | "pancake-v3"; // PancakeSwap V3 (pancakeV3SwapCallback).

export interface DexConfig {
  name: string;
  kind: DexKind;
  factory: Address;
  /** V3-style: fee tiers (univ3/pancake) or tick spacings (aero-cl). V2-style: unused. */
  tiers?: number[];
  /** univ2 kind: fee in basis points (30 = 0.30%). */
  feeBps?: number;
  /** Callback selector name the contract must implement for flash swaps on this DEX. */
  callback: "uniswapV2Call" | "hook" | "pancakeCall" | "uniswapV3SwapCallback" | "pancakeV3SwapCallback";
  /** On-chain quoter (V3-style) used for verification of local math. */
  quoter?: Address;
}

export interface TokenConfig {
  symbol: string;
  address: Address;
  decimals: number;
}

export interface FlashLoanProviders {
  morphoBlue?: Address;
  aaveV3Pool?: Address;
  balancerV2Vault?: Address;
}

export interface ChainConfig {
  id: number;
  name: string;
  rpcUrls: string[];
  wsUrls?: string[];
  blockTimeMs: number;
  /** OP-stack chains charge an L1 data fee on top of L2 gas. */
  opStack: boolean;
  multicall3: Address;
  weth: Address;
  usdc: Address;
  tokens: TokenConfig[];
  dexes: DexConfig[];
  flash: FlashLoanProviders;
  /** Chain supports Flashbots-style private bundles (reverts cost nothing). */
  flashbotsRelay?: string;
}

const MULTICALL3: Address = "0xcA11bde05977b3631167028862bE2a173976CA11";

export const BASE: ChainConfig = {
  id: 8453,
  name: "base",
  rpcUrls: [
    process.env.BASE_RPC_URL ?? "https://base-rpc.publicnode.com",
    "https://base.drpc.org",
    "https://base-mainnet.public.blastapi.io",
    "https://mainnet.base.org",
  ],
  wsUrls: process.env.BASE_WS_URL ? [process.env.BASE_WS_URL] : ["wss://base-rpc.publicnode.com"],
  blockTimeMs: 2000,
  opStack: true,
  multicall3: MULTICALL3,
  weth: "0x4200000000000000000000000000000000000006",
  usdc: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  tokens: [
    { symbol: "WETH", address: "0x4200000000000000000000000000000000000006", decimals: 18 },
    { symbol: "USDC", address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", decimals: 6 },
    { symbol: "USDbC", address: "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA", decimals: 6 },
    { symbol: "DAI", address: "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb", decimals: 18 },
    { symbol: "USDT", address: "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2", decimals: 6 },
    { symbol: "cbETH", address: "0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22", decimals: 18 },
    { symbol: "wstETH", address: "0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452", decimals: 18 },
    { symbol: "weETH", address: "0x04C0599Ae5A44757c0af6F9eC3b93da8976c150A", decimals: 18 },
    { symbol: "cbBTC", address: "0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf", decimals: 8 },
    { symbol: "AERO", address: "0x940181a94A35A4569E4529A3CDfB74e38FD98631", decimals: 18 },
    { symbol: "VIRTUAL", address: "0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b", decimals: 18 },
    { symbol: "BRETT", address: "0x532f27101965dd16442E59d40670FaF5eBB142E4", decimals: 18 },
    { symbol: "DEGEN", address: "0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed", decimals: 18 },
    { symbol: "TOSHI", address: "0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4", decimals: 18 },
    { symbol: "ZORA", address: "0x1111111111166b7FE7bd91427724B487980aFc69", decimals: 18 },
    { symbol: "WELL", address: "0xA88594D404727625A9437C3f886C7643872296AE", decimals: 18 },
    { symbol: "EURC", address: "0x60a3E35Cc302bFA44Cb288Bc5a4F316Fdb1adb42", decimals: 6 },
    { symbol: "LINK", address: "0x88Fb150BDc53A65fe94Dea0c9BA0a6dAf8C6e196", decimals: 18 },
    { symbol: "MORPHO", address: "0xBAa5CC21fd487B8Fcc2F632f3F4E8D37262a0842", decimals: 18 },
  ],
  dexes: [
    {
      name: "UniswapV3",
      kind: "univ3",
      factory: "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",
    },
    {
      name: "AerodromeCL",
      kind: "aero-cl",
      factory: "0x5e7BB104d84c7CB9B682AaC2F3d509f5F406809A",
      tiers: [1, 10, 50, 100, 200, 2000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x254cF9E1E6e233aa1AC962CB9B05b2cfeAaE15b0",
    },
    {
      name: "AerodromeCL3",
      kind: "aero-cl",
      factory: "0xf8f2eB4940CFE7d13603DDDD87f123820Fc061Ef",
      tiers: [1, 10, 50, 100, 200, 2000],
      callback: "uniswapV3SwapCallback",
    },
    {
      name: "AerodromeCL2",
      kind: "aero-cl",
      factory: "0xaDe65c38CD4849aDBA595a4323a8C7DdfE89716a",
      tiers: [1, 10, 50, 100, 200, 2000],
      callback: "uniswapV3SwapCallback",
    },
    {
      name: "PancakeV3",
      kind: "pancake-v3",
      factory: "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
      tiers: [100, 500, 2500, 10000],
      callback: "pancakeV3SwapCallback",
      quoter: "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
    },
    {
      name: "SushiV3",
      kind: "univ3",
      factory: "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0xb1E835Dc2785b52265711e17fCCb0fd018226a6e",
    },
    {
      name: "Aerodrome",
      kind: "aero-v2",
      factory: "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
      callback: "hook",
    },
    {
      name: "UniswapV2",
      kind: "univ2",
      factory: "0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6",
      feeBps: 30,
      callback: "uniswapV2Call",
    },
    {
      name: "SushiV2",
      kind: "univ2",
      factory: "0x71524B4f93c58fcbF659783284E38825f0622859",
      feeBps: 30,
      callback: "uniswapV2Call",
    },
    {
      name: "PancakeV2",
      kind: "univ2",
      factory: "0x02a84c1b3BBD7401a5f7fa98a384EBC70bB5749E",
      feeBps: 25,
      callback: "pancakeCall",
    },
    {
      name: "BaseSwap",
      kind: "univ2",
      factory: "0xFDa619b6d20975be80A10332cD39b9a4b0FAa8BB",
      feeBps: 25,
      callback: "pancakeCall",
    },
  ],
  flash: {
    morphoBlue: "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb",
    aaveV3Pool: "0xA238Dd80C259a72e81d7e4664a9801593F98d1c5",
    balancerV2Vault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
  },
};

export const ARBITRUM: ChainConfig = {
  id: 42161,
  name: "arbitrum",
  rpcUrls: [process.env.ARBITRUM_RPC_URL ?? "https://arbitrum-one-rpc.publicnode.com", "https://arb1.arbitrum.io/rpc"],
  wsUrls: process.env.ARBITRUM_WS_URL ? [process.env.ARBITRUM_WS_URL] : ["wss://arbitrum-one-rpc.publicnode.com"],
  blockTimeMs: 250,
  opStack: false,
  multicall3: MULTICALL3,
  weth: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
  usdc: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
  tokens: [
    { symbol: "WETH", address: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1", decimals: 18 },
    { symbol: "USDC", address: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831", decimals: 6 },
    { symbol: "USDC.e", address: "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", decimals: 6 },
    { symbol: "USDT", address: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", decimals: 6 },
    { symbol: "DAI", address: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1", decimals: 18 },
    { symbol: "WBTC", address: "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f", decimals: 8 },
    { symbol: "ARB", address: "0x912CE59144191C1204E64559FE8253a0e49E6548", decimals: 18 },
    { symbol: "GMX", address: "0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a", decimals: 18 },
    { symbol: "LINK", address: "0xf97f4df75117a78c1A5a0DBb814Af92458539FB4", decimals: 18 },
    { symbol: "wstETH", address: "0x5979D7b546E38E414F7E9822514be443A4800529", decimals: 18 },
    { symbol: "PENDLE", address: "0x0c880f6761F1af8d9Aa9C466984b80DAb9a8c9e8", decimals: 18 },
    { symbol: "MAGIC", address: "0x539bdE0d7Dbd336b79148AA742883198BBF60342", decimals: 18 },
  ],
  dexes: [
    {
      name: "UniswapV3",
      kind: "univ3",
      factory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
    },
    {
      name: "SushiV3",
      kind: "univ3",
      factory: "0x1af415a1EbA07a4986a52B6f2e7dE7003D82231e",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x0524E833cCD057e4d7A296e3aaAb9f7675964Ce1",
    },
    {
      name: "PancakeV3",
      kind: "pancake-v3",
      factory: "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
      tiers: [100, 500, 2500, 10000],
      callback: "pancakeV3SwapCallback",
      quoter: "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
    },
    {
      name: "SushiV2",
      kind: "univ2",
      factory: "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
      feeBps: 30,
      callback: "uniswapV2Call",
    },
    // Camelot V2 is intentionally excluded: its pairs use per-direction fees (token0FeePercent/token1FeePercent)
    // and an optional stable-swap curve, so the standard x*y=k quote is wrong for them.
  ],
  flash: {
    morphoBlue: "0x6c247b1F6182318877311737BaC0844bAa518F5e",
    aaveV3Pool: "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
    balancerV2Vault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
  },
};

export const MAINNET: ChainConfig = {
  id: 1,
  name: "mainnet",
  rpcUrls: [process.env.MAINNET_RPC_URL ?? "https://ethereum-rpc.publicnode.com", "https://cloudflare-eth.com"],
  wsUrls: process.env.MAINNET_WS_URL ? [process.env.MAINNET_WS_URL] : ["wss://ethereum-rpc.publicnode.com"],
  blockTimeMs: 12000,
  opStack: false,
  multicall3: MULTICALL3,
  weth: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
  usdc: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  tokens: [
    { symbol: "WETH", address: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", decimals: 18 },
    { symbol: "USDC", address: "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", decimals: 6 },
    { symbol: "USDT", address: "0xdAC17F958D2ee523a2206206994597C13D831ec7", decimals: 6 },
    { symbol: "DAI", address: "0x6B175474E89094C44Da98b954EedeAC495271d0F", decimals: 18 },
    { symbol: "WBTC", address: "0x2260FAc5e5542A773aa44fBCfF9F0f0d38f0c4C9", decimals: 8 },
    { symbol: "wstETH", address: "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0", decimals: 18 },
    { symbol: "LINK", address: "0x514910771AF9Ca656af840dff83E8264EcF986CA", decimals: 18 },
    { symbol: "UNI", address: "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", decimals: 18 },
    { symbol: "PEPE", address: "0x6982508145454Ce325dDbE47a25d4ec3d2311933", decimals: 18 },
    { symbol: "SHIB", address: "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE", decimals: 18 },
    { symbol: "AAVE", address: "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9", decimals: 18 },
    { symbol: "MKR", address: "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2", decimals: 18 },
  ],
  dexes: [
    {
      name: "UniswapV3",
      kind: "univ3",
      factory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
    },
    {
      name: "SushiV3",
      kind: "univ3",
      factory: "0xbACEB8eC6b9355Dfc0269C18bac9d6E2Bdc29C4F",
      tiers: [100, 500, 3000, 10000],
      callback: "uniswapV3SwapCallback",
      quoter: "0x64e8802FE490fa7cc61d3463958199161Bb608A7",
    },
    {
      name: "PancakeV3",
      kind: "pancake-v3",
      factory: "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
      tiers: [100, 500, 2500, 10000],
      callback: "pancakeV3SwapCallback",
      quoter: "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
    },
    {
      name: "UniswapV2",
      kind: "univ2",
      factory: "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
      feeBps: 30,
      callback: "uniswapV2Call",
    },
    {
      name: "SushiV2",
      kind: "univ2",
      factory: "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
      feeBps: 30,
      callback: "uniswapV2Call",
    },
    {
      name: "PancakeV2",
      kind: "univ2",
      factory: "0x1097053Fd2ea711dad45caCcc45EfF7548fCB362",
      feeBps: 25,
      callback: "pancakeCall",
    },
  ],
  flash: {
    morphoBlue: "0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb",
    aaveV3Pool: "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
    balancerV2Vault: "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
  },
  flashbotsRelay: "https://relay.flashbots.net",
};

export const CHAINS: Record<string, ChainConfig> = { base: BASE, arbitrum: ARBITRUM, mainnet: MAINNET };

export function getChain(name: string): ChainConfig {
  const c = CHAINS[name];
  if (!c) throw new Error(`unknown chain '${name}' (known: ${Object.keys(CHAINS).join(", ")})`);
  return c;
}
