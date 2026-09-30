# 00-prior-runs: raw data from the earlier sessions of 2026-09-30

Status: COMPLETE (static copies). Collected by the main session; files are gzip copies of what the earlier runs wrote.
Descriptions state how each file was produced. They contain no findings.

## Question lines served

| Files | Question line(s) |
|---|---|
| engine-runs/live-base-all.jsonl.gz, dry-all.log.gz | "I only had 20 V4 pools" (log lines `uniswap v4 candidates` / `uniswap v4 pools discovered`); "Older V2 pairs" (log lines `factory enumerated`); "Pools under 0.1 ETH" (`searcher ready` counts at --min-depth-eth 0.1); "So the search went far beyond selected pairs" |
| engine-runs/live-base-blocks-long5.jsonl.gz, dry-blocks-long5.log.gz | Reference run with 657 configured pools (docs/ANALYSIS.md §2.5), the "selected pairs" baseline |
| engine-runs/live-base-all-v0.jsonl.gz, dry-all-v0.log.gz | First full-universe attempt, contains the RSR/WETH detection at block 51998756 ("The RSR trade ...") |
| competitor-ledgers/* | "The RSR trade shows how contested gaps end"; "It is also the most fought-over flow on Base" |
| papers-fetched-earlier/* | "Chain-wide studies already count every pool" and the Base figures (21.4 M, 4,365 bots) |
| research-runs/* | "Other chains, live" (cross-chain WETH/USDC samples on Base, Arbitrum, Ethereum) and the other angles in docs/ANALYSIS.md §5 |

## engine-runs/

Produced by `bot/src/main.ts` in `--mode dry` on Base (nothing was ever sent on-chain). One JSON object per line.

Detection record fields: `t` (UTC ISO time written), `block`, `fb` (flashblock index, 0 in block/logs modes), `route`
(human-readable hops), `pools` (pool addresses in hop order; V4 pools as the first 20 bytes of the pool id), `token`
(start/profit token symbol), `amountIn` (human units of `token`), `predictedProfitUsd`, `gasUsd`, `netUsd` (searcher's
local-math prediction), `gapBps`, `sim` (on-chain `eth_call` simulation of the executor with a bytecode override:
`{profitUsd, gas, ms}` on success or `{error, ms}` on revert), optional `simLatest` (re-simulation at `latest`), `simNetUsd`
(simulated profit minus gas, present only when simulation succeeded). USD values use the engine's token→ETH price map
and the WETH/USDC price at the time.

Provenance notes (facts about the code version that produced each file):
- Every file except `live-base-all.jsonl` was produced BEFORE commit fd8d236 (anchored pricing). Their USD values for
  long-tail tokens come from the earlier unanchored price map (a token could be priced from its own illiquid pool).
- Files produced before the revert-decoding rewrite show `unknown reason` in `sim.error`; later files show decoded errors
  (`CannotRepay(have,owed)`, `TransferFailed()`, `Error(UniswapV2: K)`, `revert 0xa932492f` = Aerodrome `K()`).

| File | What run | Universe / flags (from its log) |
|---|---|---|
| live-base.jsonl, live-base-validate.jsonl, live-base-long.jsonl (+ dry-validate.log, dry-long.log, dry-flashblocks-run1.log) | Flashblock-source dry runs, ~12:00–12:27 UTC | Long-tail universe; state refreshed through the preconf RPC, which rate-limits at ~5 req/10 s (docs/ANALYSIS.md §2.2–2.3) |
| live-base-logs.jsonl, dry-logs.log | First logs-source attempt, ~15:45 UTC | Short; process stopped |
| live-base-blocks-long.jsonl, dry-blocks-long*.log | Logs/blocks-source attempts, 15:43–16:10 UTC | Runs 2–4 stopped early (self-check failures, see logs) |
| live-base-blocks-long5.jsonl, dry-blocks-long5.log | §2.5 reference run, ~16:15–16:38 UTC, 22 min | 657 pools, event-driven state from block receipts |
| live-base-all-v0.jsonl, dry-all-v0.log | First `--universe all` run, 16:46–16:55 UTC | `--universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6`; 3,282 pools / 3,652 cycles after the depth filter; unanchored pricing |
| live-base-all.jsonl, dry-all.log | §2.6 run, 17:04–17:25 UTC, 21 min | Same flags, anchored pricing; 3,189 pools / 3,608 cycles |
| pipeline.log, arbtest.log, lev.log | Test logs (fork pipeline test, executor tests, leverage test) | — |

The two `--universe all` logs contain per-factory enumeration counts (`factory enumerated`: dex, total, enumerated),
`universe enumerated` (38,673 pools, 33,528 tokens, 37,262 pairs), `pool discovery complete` (1,341,432 candidates,
46,134 found), the GeckoTerminal V4 lines (`listed: 242`, `v4: 20`, `kept: 10`, `hooked: 4`, `outOfUniverse: 6`), and
per-tick heartbeats.

## competitor-ledgers/

Collected 16:58–17:12 UTC from Base RPCs (publicnode for recent logs, blastapi for archive `eth_getBalance`/`eth_call`)
and the Blockscout v2 API. ETH/USD used where a USD figure was needed: 2,692.47 (Aerodrome Slipstream WETH/USDC pool
0xb2cc224c1c9fee385f8ad6a55b4d94e92359dc59 at ~16:58 UTC).

| File | Content |
|---|---|
| competitor_txs.json | Blockscout `/api/v2/addresses/0xF0523316Cf23EF167d874Fa030b2214280E38Ee6/transactions?filter=from` response: its last 50 transactions (blocks 51995475–51998757). This is the sender of the RSR-closing tx 0x2310e683…2b4. |
| competitor_pnl.json | `{rows, hours}`; row = [tx_hash, landed, fee_eth (L2 + L1), weth_flow, usdc_flow, gross_eth, other_token_count] from ERC-20 Transfer logs into/out of its three contracts. This method does not see native-ETH payouts. |
| competitor_perblock.json | Row = [block, tx_count, all_landed, delta_eth, fee_eth, tx_hashes]; delta_eth = change of ETH + WETH + USDC (USDC converted at the ETH/USD above) summed over the EOA and its contracts 0x627E9E10…, 0xA0578728…, 0xfA256106… between block-1 and block. 1,128 archive calls, none missing. |
| arbers_XDP.json | `{sender: [[block, tx_hash, max_priority_fee_gwei, to], …]}` for every tx that emitted a swap on BOTH XDP/USDC pools 0x1ef035205f94c7734827961c438474d089a334a0 (Uniswap V3 0.01 %) and 0x2df380544b88adb3ad0a94100dcc45fd705aae2d (Slipstream) in the 3,000 blocks before ~17:08 UTC. |
| arbers_WETHUSDC.json | Same for WETH/USDC pools 0x72ab388e2e2f6facef59e3c3fa2c4e29011c2d38 (Uniswap V3 0.01 %) and 0xb4cb800910b228ed3d0834cf79d697127bbb00e5 (PancakeSwap V3 0.01 %). |
| ledger_0x778951.json, ledger_0x0190f0.json | Row = [block, delta_eth, fee_eth, xdp_units_delta] for the last 60 txs of senders 0x7789515e58bf00c99f11337bc267db8c30872351 (contract 0x952f339d…) and 0x0190f008a0118f41b43b3ee13b7162590fd925cc (contract 0xcd447b60…); delta_eth = change of ETH + WETH + USDC + XDP (XDP valued at 0.021453 USDC) over EOA + contract between block-1 and block. |
| mine.json | Off-chain vs on-chain `getAmountOut` comparison for one Aerodrome V2 pool at 4 sizes. |

Gap: the ledgers of the other two XDP senders (0x000000c557fa9a96d66cd6371abde62d879d0e61, 0x3be22b314654c396a12c5e8d79abdd65aac3caaf)
were computed but not saved; only their summary rows exist, in docs/ANALYSIS.md §2.6.

## papers-fetched-earlier/

Plain text extracted from the papers fetched earlier in the session (PDF text, not re-checked for extraction errors).
`08-sources/` holds a fresh, provenance-tracked collection; these are kept because they were the texts actually read.
arXiv 2606.00720 (Wu & Öz, "To Wait or To Probe"), arXiv 2501.17335 (Öz et al., cross-chain arbitrage), "Optimistic MEV in
Ethereum Layer 2s" (Solmaz et al.), "Cross-Rollup MEV: Non-Atomic Arbitrage on Layer-2 Blockchains" (Gogol et al.),
"Blockspace Under Pressure" (Wang et al.), "Quantifying the Value of Revert Protection" (Zhu et al.), ESMA TRV risk
analysis on MEV (1 July 2025), "How to Serve Your Sandwich? MEV Attacks in Private L2 Mempools" (Gogol et al.).

## research-runs/

Raw outputs of the non-Base-DEX measurements summarized in docs/ANALYSIS.md §5 (producing scripts in bot/src/research/):
feetiming (Slipstream fee transitions, 209 pools, 1,041 blocks), leadlag (OKX ETH-USDT vs 3 Base pools, 45 min),
leadlag-multi (OKX vs Base long-tail pools, 30 min), cexcex (OKX/Gate/Kraken spreads, 15 min), cextri (log only; the
.jsonl output was empty), crosschain (WETH/USDC Uniswap V3 0.05 % on Base, Arbitrum, Ethereum every 2 s, 450 samples).

## misc/

geckoterminal-top-pools-base.json (GeckoTerminal top-pools page for Base, fetched ~10:41 UTC); defillama-arbitrum-timeboost.json
(DefiLlama protocol record); v4-poolmanager-logs-sample.jsonl (raw `eth_getLogs` responses for the Base PoolManager,
~12:09 UTC); section-2.6-draft.md (draft text later inserted into docs/ANALYSIS.md).
