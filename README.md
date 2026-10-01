# dapparb — atomic DEX arbitrage searcher + flash-loan leverage, built and measured honestly

This repository is a from-scratch, production-grade implementation of the two "flash loan passive income"
strategies pitched in the DApp University videos, **plus the empirical measurement the videos leave out**:
how much of that profit actually exists for an independent operator in 2026.

Read [`docs/ANALYSIS.md`](docs/ANALYSIS.md) first if you only care about the answer.

## What is here

| Component | Path | Status |
|---|---|---|
| `ArbExecutor` — flash-swap arbitrage executor (Uniswap V2/V3/V4 & forks, Aerodrome V2/Slipstream, PancakeSwap V2/V3; Morpho/Aave/Balancer flash-loan fallback) | `contracts/src/ArbExecutor.sol` | 25 fork tests passing on Base |
| `LeverageManager` — one-transaction leveraged long/short on Aave V3 (the "trade crypto you don't have" strategy) | `contracts/src/LeverageManager.sol` | 6 fork tests passing on Base |
| Searcher bot — pool discovery, bit-exact local AMM math, event-driven state from logs (exact), pool→cycle index with closed-form sizing (2 ms/block), 2-hop + triangular search, Flashblocks / logs / block state sources, eth_call simulation with ABI self-check, EIP-1559 / Flashbots submission | `bot/src` | validated end-to-end on an Anvil fork; log-state exactness verified live |
| Research campaigns — block/flashblock scans, Slipstream fee timing, OKX↔Base lead-lag (ETH and long tail), funding/basis carry | `bot/src/research` | results in `docs/ANALYSIS.md` |
| Infrastructure as code — co-located Base node (Flashblocks) + bot, Terraform + compose, latency probe | `infra/` | written from official docs, not executed here |
| Empirical scanner — records every gross- and net-profitable cycle per block, with persistence analysis | `bot/src/research/scan.ts` | results in `docs/ANALYSIS.md` |
| Leverage CLI — builds/sends `LeverageManager` calls with a Uniswap V3 route | `bot/src/cli/leverage.ts` | |

Supported chains out of the box: **Base** (primary; Flashblocks + preconf RPC), Arbitrum, Ethereum mainnet (Flashbots).
Uniswap V4 pools (hookless, static fee, incl. native-ETH pairs) are priced with the same engine via `StateView` and executed through the PoolManager's flash accounting.

## Design decisions that differ from the videos (and why)

1. **Flash swaps, not flash loans, for arbitrage.** Hop 0 of every cycle is a V2/V3 flash swap: the pool pays out
   first and is repaid inside its callback. Zero fee, one fewer external call, ~120k gas for a V3→V2 cycle.
   Flash loans (Morpho 0 %, Aave 0.05 %, Balancer) remain as a fallback path (`executeFlashLoan`).
2. **Balancer V2 is no longer a usable flash-loan source on Base.** After the November 2025 exploit the Base vault
   holds ~29 WETH. Morpho Blue holds ~82k WETH / $230M USDC at 0 % and is the default fallback.
3. **Local, bit-exact pricing instead of on-chain quoters.** The bot ports Uniswap V3's `TickMath`/`SqrtPriceMath`/
   `SwapMath` to BigInt and walks the tick bitmap itself; `bot/src/math/v3.live.test.ts` checks it against every
   V3-style quoter on Base with zero mismatches. One RPC round-trip per tick, not one per quote.
4. **Polling state is too slow; events are exact.** Every supported AMM emits enough in its own events (V3 `Swap`
   carries sqrtPrice, liquidity and tick; V2 `Sync` carries reserves; Mint/Burn carry the range and amount) to
   reconstruct pricing state with no state reads at all. The engine applies a block's (or flashblock's) receipts and
   re-evaluates only the cycles through the pools that changed: ~2 ms per block, verified identical to a full search.
   Public endpoints only serve this at 2 s granularity; a local Flashblocks-aware node serves pending receipts at 200 ms.
5. **Priority fee is the auction.** On OP-stack chains the base fee is ~0.006 gwei; ordering is decided by the
   priority fee, so the executor bids a configurable fraction of the *simulated* net profit.
6. **Simulate before you send, and decode why it failed.** Every candidate is `eth_call`-simulated (with a bytecode
   state override in dry-run mode, so no deployment is needed) and the contract's custom errors
   (`InsufficientProfit`, `CannotRepay`, …) are decoded so a lost race is distinguishable from a bug.

## Quick start

```bash
# toolchain: Node >= 20, Foundry
cd contracts && forge build && forge test          # fork tests hit Base public RPCs (BASE_RPC_URL to override)
cd ../bot && npm install && npm run typecheck

# 1) measure before you spend anything: 60 blocks on Base, hand-picked token universe
npx tsx src/research/scan.ts --chain base --blocks 60
#    …or the long-tail universe from GeckoTerminal's top-volume pools
npx tsx src/research/scan.ts --chain base --blocks 60 --universe top --pages 10 --max-tokens 250

# 2) dry-run the live loop (event-driven state from block receipts, simulation via bytecode override, nothing sent)
npx tsx src/main.ts --chain base --mode dry --source logs --universe top --min-profit-usd 0.05
#    on a flashblocks-aware node: --receipts-tag pending (200 ms state); public endpoints cannot sustain that rate
#    …or every pool the factories know about (46k found on Base, ~3.2k with ≥ 0.1 ETH of anchored depth; see docs/ANALYSIS.md §2.6)
npx tsx src/main.ts --chain base --mode dry --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01
#    …or (recommended) every pool that actually trades, discovered from Swap logs (docs/ANALYSIS.md §7.5): build the
#    registry once (~4 min for 3 days on mainnet.base.org), then start in ~1 min; it keeps discovering new pools live
npx tsx src/cli/registry.ts --chain base --lookback 129600 --logs-rpc https://mainnet.base.org
npx tsx src/main.ts --chain base --mode dry --source logs --universe config --active-lookback 21600 --min-depth-eth 0.1 --min-profit-usd 0.01

# 3) deploy + go live (only after the dry run shows simulated net profit that you believe)
cd ../contracts && forge script script/Deploy.s.sol --rpc-url base --broadcast --private-key $PRIVATE_KEY
cd ../bot && ARB_CONTRACT=0x... PRIVATE_KEY=0x... npx tsx src/main.ts --chain base --mode live --source flashblocks
```

`bot/.env.example` documents every knob (bid fraction, fee caps, submission endpoints, RPCs).

## Leverage (videos 1 & 2)

`LeverageManager.open` uses Aave V3's `flashLoan` with `interestRateMode = 2`: the borrowed amount is not repaid
in the transaction, it becomes the user's variable-rate debt (no flash premium). The user grants two approvals
(`ERC20.approve` for their own contribution and `VariableDebtToken.approveDelegation` for the borrowed amount);
the contract never custodies anything between transactions and enforces a minimum health factor.

```bash
npx tsx src/cli/leverage.ts open-long  --manager 0x... --user-usdc 2000 --flash-usdc 2000 --min-hf 1.3
npx tsx src/cli/leverage.ts open-short --manager 0x... --user-weth 1 --flash-weth 1
npx tsx src/cli/leverage.ts status     --manager 0x... --user 0x...
npx tsx src/cli/leverage.ts close-long --manager 0x... --collateral-to-swap-weth 0.8
```

Fork-test result for the video's exact example (2000 USDC own + 2000 USDC borrowed): 1.483 WETH collateral,
2000 USDC debt, health factor 1.66, round-trip cost ≈ $5 in swap fees. This is **leverage, not income**: a 2x long
is liquidated at roughly a 40 % drawdown; see the risk notes in `docs/ANALYSIS.md`.

## Tests

```bash
cd contracts && forge test -vv                               # 31 fork tests (Base)
cd bot && npx tsx --test src/math/v2.test.ts                 # integer math
cd bot && npx tsx --test src/math/v3.live.test.ts            # local V3 sim vs on-chain quoters (live)
cd bot && npx tsx --test src/arb/pipeline.fork.test.ts       # push a pool on Anvil → search → simulate → send
cd bot && npx tsx --test src/arb/incremental.test.ts         # event-mode two-pool cycles and triangles, incremental add
cd bot && npx tsx src/research/quotecheck.ts --per-dex 15    # local quote vs on-chain swap for every pool type (live)
```

## Safety notes

* The hot wallet only needs gas; profits accrue to the contract and are withdrawn by the owner.
* `execute` reverts unless the cycle returns `amountIn + minProfit`; callbacks are authenticated with transient
  storage so no third party can trigger a payout.
* Reverted transactions still cost gas on L2s. The bot only sends what simulated profitably in the same
  200 ms window, and tracks landed/reverted outcomes so you can see your win rate.
* Never point `--mode live` at a contract you have not deployed yourself from this source.
