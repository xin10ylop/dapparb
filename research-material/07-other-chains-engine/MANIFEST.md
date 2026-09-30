# 07-other-chains-engine: repository scanner and engine on Arbitrum and Ethereum, with a same-method Base scan

Status: IN PROGRESS (counts last refreshed 2026-09-30T22:18:32Z; waiting for sentinels: SCANS, ENGINE_DETECT_ARBITRUM, ENGINE_DETECT_MAINNET).

Run notes: collectors were launched 2026-09-30T22:14:28Z (master PID in `collect/state/run_all.pid`, log `collect/run_all.log`,
step log `collect/pipeline.log`). The Status line above and the "Counts" section are rewritten by `collect/fill_manifest.py`
(descriptive metadata only). A detached waiter (`collect/manifest_waiter.sh`, log `collect/manifest_waiter.log`) runs it every
5 min and one last time after the sentinels SCANS, ENGINE_DETECT_ARBITRUM and ENGINE_DETECT_MAINNET exist. It can also be run by
hand. Everything else in this file is static.

This directory holds data only. Nothing here states a finding.

## Question lines served (mapping only)

| Files | Question line(s) |
|---|---|
| `scans/arbitrum/*`, `scans/mainnet/*` | "Other chains, live. The live search ran only on Base. Block-level scans covered Arbitrum and Ethereum." These are fresh raw block-level scans, replacing the earlier ones whose raw output was not kept; "BSC has the same ordering problem" is context only, and no BSC data is here (see gaps) |
| `scans/base/*` | Same-method Base baseline for the Arbitrum and Ethereum scans ("The live search ran only on Base"); "Pools under 0.1 ETH of liquidity" only through the depth-filter counts in the logs (`live pools` line; the scanner's default `--min-depth-eth 0.2`) |
| `scans/*/*.log.gz` (`uniswap v4 candidates` / `uniswap v4 pools discovered` log lines) | "Uniswap V4 ... I only had 20 V4 pools. The engine ... doesn't list every V4 pool yet": how many V4 pools the GeckoTerminal-based discovery lists, resolves, drops as hooked, or drops as out of universe on each chain and universe |
| `engine-detect/arbitrum/*`, `engine-detect/mainnet/*` | "Other chains, live": the unmodified live engine (`bot/src/main.ts`) run for 20 min on Arbitrum and Ethereum in detection-only mode. It does NOT simulate; see "Engine dry run on other chains" |
| `engine-detect/*/*.log.gz` (`factory enumerated` lines) | "Older V2 pairs. I took the newest 6,000 of about 3 million Uniswap V2 pairs": `total` vs `enumerated` per V2-style factory on Arbitrum (SushiV2) and Ethereum (UniswapV2, SushiV2, PancakeV2) under `--max-per-factory 6000` |
| `collect/engine-blocker-check-*.log`, sentinels `ENGINE_LIVE_ARBITRUM.FAILED` / `ENGINE_LIVE_MAINNET.FAILED` | "The live search ran only on Base": why the simulation-based dry run cannot run on other chains without a code change (evidence of the blocker, no interpretation) |
| `prior-summaries.md` | Verbatim copies of docs/ANALYSIS.md §2.1 and the other-chain row of §5, plus §1 "Chains scanned" and the §6 commands, for reference |

## Directory layout

```
MANIFEST.md
prior-summaries.md                        verbatim excerpts of docs/ANALYSIS.md (no commentary)
scans/<chain>/scan-<chain>-<universe>.jsonl.gz          raw rows written by scan.ts --out (or -part-NNNN.jsonl.gz if split)
scans/<chain>/scan-<chain>-<universe>.log.gz            raw stdout/stderr of scan.ts (pino JSON lines + plain-text SCAN SUMMARY if it finished)
scans/<chain>/scan-<chain>-<universe>.blocks.csv.gz     DERIVED: one row per "block scanned" log line
scans/<chain>/scan-<chain>-<universe>.meta.json         descriptive metadata (row counts, first/last block and time, exit, signal)
scans/<chain>/scan-<chain>-<universe>.code-provenance.txt   git HEAD, uncommitted bot/src changes, sha256 of every bot/src/*.ts at launch
engine-detect/<chain>/engine-detect-<chain>.{jsonl.gz,log.gz,heartbeats.csv.gz,meta.json,code-provenance.txt}
collect/                                  collector scripts, logs, gaps.jsonl (created only if a step fails)
collect/smoke/                            smoke-test logs (scans: 4-45 blocks per config at 21:42-22:08Z; engine: 2 min per chain), failure-path self-test log
collect/state/, collect/work/             transient working state (git-ignored); work/ holds the uncompressed JSONL while a run is live
```
`<chain>` is arbitrum, mainnet or base; `<universe>` is config or top.

## Sources and endpoints

| Use | Endpoint |
|---|---|
| Arbitrum scans and engine (HTTP) | `https://arbitrum-one-rpc.publicnode.com` (chains.ts `rpcUrls[0]`), viem fallback `https://arb1.arbitrum.io/rpc` |
| Arbitrum engine newHeads | `wss://arbitrum-one-rpc.publicnode.com` |
| Ethereum scans and engine (HTTP) | `https://ethereum-rpc.publicnode.com`, viem fallback `https://cloudflare-eth.com` |
| Ethereum engine newHeads | `wss://ethereum-rpc.publicnode.com` |
| Base scans (HTTP) | `https://base.meowrpc.com` via env `BASE_RPC_URL`. Fallbacks come from chains.ts: `base.drpc.org`, `base-mainnet.public.blastapi.io`, `mainnet.base.org`. `base-rpc.publicnode.com`, which the §2.1 Base scans used, was not used because it is reserved for the Base census collectors |
| Token universe (`--universe top`) and V4 pool candidates | GeckoTerminal public API `https://api.geckoterminal.com/api/v2/networks/{arbitrum,eth,base}/pools?sort=h24_volume_usd_desc` and `/dexes/<id>/pools` (bot/src/research/tokens.ts). The code sleeps 2.1 s between requests and retries a 429 once after 15 s |
| V4 pool keys | Uniswap V4 PositionManager `poolKeys(bytes25)` and StateView on each chain (addresses in bot/src/pools/v4.ts) |

Code: repository at git HEAD `1c1a93feee5cd05b5efc32ce39c35c39ba7ddd04`, run unmodified. Node v22.22.2, viem 2.57.1, tsx 4.23.15.
Another agent edited `bot/src` in the working tree while this collection ran: an opt-in `--v4-pools` flag in `main.ts`, a `makeV4Pool`
refactor in `pools/v4.ts`, and a new `pools/v4file.ts`, all modified 22:06–22:10Z. None of the runs here pass `--v4-pools`. Each run's exact
code state is in its `*.code-provenance.txt`.

## Method: block-level scans (`bot/src/research/scan.ts`, unmodified)

What the scanner does, from reading the code:
- **Discovery (once):** token list = `cfg.tokens` (`--universe config`) or `buildTokenUniverse(pages=5, maxTokens=200)` (`--universe top`: the
  configured tokens plus up to 200 tokens from GeckoTerminal's top pools by 24 h volume). For `top`, pairs = `longTailPairs` (all pairs among
  the configured tokens, plus each extra token against WETH and USDC). For `config`, pairs = all pairs of configured tokens. Every
  configured DEX factory and fee tier is looked up for each pair. Uniswap V4: `discoverV4Pools` takes the GeckoTerminal-listed V4 pools
  (pages 2 for config, 3 for top), resolves keys through the PositionManager, and keeps pools that are hookless or whose hook has no
  swap-related permission bits, that do not use a dynamic fee, and whose tokens are in the universe. Then `pruneEmpty`, then
  `filterByDepth(--min-depth-eth, default 0.2 ETH)`.
- **Sampling:** the loop polls `eth_blockNumber`. Whenever the head differs from the last scanned head, it syncs every pool pinned at that
  head (multicall; every 15th iteration re-fetches tick data for all pools, which takes much longer), runs `findOpportunities` (2-pool
  cycles) and `findTriangles` (3-pool cycles starting in WETH or USDC), prices gas (`eth_gasPrice`, plus the OP-stack L1 fee on Base for
  700 bytes of dummy calldata), writes one JSONL row per gross-positive cycle, and logs one `block scanned` line. Heads produced while an
  iteration is running are not scanned. The loop stops after `--blocks` distinct heads.
- **`--blocks` and time cap used here:** `--blocks` = 30 min / block time + 1, which is the fewest distinct heads that can span 30 minutes of chain time:
  Arbitrum 7201 (0.25 s), Ethereum 151 (12 s), Base 901 (2 s). The collector sends SIGTERM 31 min after the first `block scanned`
  line if the tool has not finished by itself. Smoke-test iteration times were: Arbitrum about 0.6 s, with forced resyncs of 15–176 s;
  Ethereum one iteration per 12 s block; Base on meowrpc about 4–5 s, with forced resyncs of 70–80 s. So the Arbitrum and Base runs are
  expected to end on the time cap, and the Ethereum runs by themselves or on the time cap. `meta.json` fields `window.time_capped`
  and `summary_present` record which happened. Only a run that finishes by itself prints the plain-text `SCAN SUMMARY` in its log.
- **Preload `collect/exit-flush.mjs`** is loaded with `node --import tsx --import exit-flush.mjs`. In the first smoke test (collect/smoke/smoke-scan-arb-config.log.gz),
  `scan.ts` called `process.exit(0)` right after `out.end()`, which dropped rows still buffered in the write stream: the last block
  logged 87 rows and the file got 1. The preload delays `process.exit` by 5 s, and on SIGTERM or SIGINT lets the process run 5 s before
  exiting with code 143 or 130, so queued rows are written. It changes nothing else. `meta.json` compares
  `jsonl_rows` with `log_rows_announced_by_block_scanned_lines`.
- **Sequencing:** per chain: config scan, then top scan, then (Arbitrum and Ethereum only) the engine run. The three chains run in parallel. Each
  endpoint serves one of these processes at a time; each process keeps at most 4 multicall chunks in flight.
- Other scan.ts defaults kept: `--triangles 1`, `--v4 1`, `--pages 5`, `--max-tokens 200`, `--min-depth-eth 0.2`.

## Method: engine on Arbitrum and Ethereum (`bot/src/main.ts`)

**Can the simulation-based dry run (`--mode dry`) run on arbitrum/mainnet without code changes? No.** Line numbers are for
`bot/src/main.ts` at git HEAD 1c1a93f. In the working tree at 22:15Z, the other agent's uncommitted `--v4-pools` edit moved the same
statements to lines 59, 61–64, 138, 158 and 274.
- `main.ts:57-60`: `codeOverride` (the executor runtime injected with an `eth_call` state override) is set only when
  `mode === "dry" && !process.env.ARB_CONTRACT && cfg.id === 8453`, and it reads the fixed path
  `./exec/artifacts/ArbExecutor.base.runtime.hex`. On chain ids 42161 and 1 it is `undefined`. A chain-specific runtime artifact
  from `contracts/script/ExportRuntime.s.sol` would therefore never be read. That script does select Arbitrum or mainnet immutables by
  `block.chainid`, and foundry.toml `fs_permissions` allows writing only to `contracts/` and `bot/src/exec/artifacts`. For that reason no
  artifact was generated.
- `main.ts:55`: in dry mode without `ARB_CONTRACT` or `--contract`, the executor address is the placeholder
  `0x00000000000000000000000000000000000a4bb0`, which has no code on these chains.
- `main.ts:122` creates the `Executor` and `main.ts:142` calls `executor.selfCheck`. Then `bot/src/exec/executor.ts:172-176`
  `fromAddress()` runs with no `codeOverride` and no signer, reads `owner()` from the placeholder, gets `0x`, and viem throws
  `ContractFunctionZeroDataError`. `main()` exits 1 right after `searcher ready`.
- Evidence: `collect/engine-blocker-check-arbitrum.log` and `collect/engine-blocker-check-mainnet.log`, from the unmodified command
  `LOG_JSON=1 node --import tsx src/main.ts --chain <chain> --mode dry`, run 22:04:50–22:05:30Z, `exit=1`. This was before the other agent's main.ts edit at 22:06:53Z, so it ran the HEAD version of main.ts.
- Sentinels `ENGINE_LIVE_ARBITRUM.FAILED` and `ENGINE_LIVE_MAINNET.FAILED` contain this reason. No simulation data exists for these chains.

**Substitute that was collected, using parameters only: detection-only live run.** `--contract ""` makes `main.ts:55` resolve `contract` to `""`,
which is not nullish, so the placeholder default is not used. `main.ts:122` then creates no Executor, and each selected candidate is
logged and written at `main.ts:258-262` as `opportunity (no contract configured; not simulated)`. Search, state engine and candidate selection
are the same code as the Base runs. There is no `eth_call` simulation, no revert decoding and no `sim` or `simNetUsd` field.
- Flags are those of the docs/ANALYSIS.md §2.6 Base run, plus `--contract ""`: `--mode dry --source logs --universe all --max-per-factory 6000
  --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6`. `--source logs` means a trigger on every websocket newHead, state from the block's
  receipts (`eth_getBlockReceipts`) and a full resync every 300 ticks. `--universe all` enumerates the newest 6,000 pools of each V2-style
  factory in chains.ts (Arbitrum: SushiV2 only; Ethereum: UniswapV2, SushiV2, PancakeV2), resolves every configured V3/Pancake tier for each
  pair found, and adds GeckoTerminal-listed V4 pools.
- Window: 20 min, starting at the `searcher ready` log line and ending with SIGINT, which runs main.ts's own SIGINT handler (`shutting down`
  stats line). The exact times are in `meta.json` `window`.
- Sentinels: `ENGINE_DETECT_ARBITRUM.DONE|FAILED`, `ENGINE_DETECT_MAINNET.DONE|FAILED`.
- Up to 3 attempts. An attempt that exits before `searcher ready` or before the window ends is recorded in `collect/gaps.jsonl`, its log is
  kept as `collect/engine-detect-<chain>.attemptN.log`, and the run is redone from scratch.
- Smoke test of this mode, 2 min per chain at 22:08–22:14Z: `collect/smoke/smoke-engine-*.{log,jsonl}`, with finalize outputs checked in scratch space.

## Exact commands to reproduce

```bash
# full pipeline (re-runnable: finished steps are skipped via collect/state/<name>.done; an unfinished live step is redone)
cd /home/user/dapparb/research-material/07-other-chains-engine/collect
setsid nohup bash run_all.sh > run_all.log 2>&1 < /dev/null &

# what one scan step runs (from /home/user/dapparb/bot); SIGTERM 31 min after the first "block scanned" line
LOG_JSON=1 node --import tsx --import ../research-material/07-other-chains-engine/collect/exit-flush.mjs \
  src/research/scan.ts --chain arbitrum --universe config --blocks 7201 --out <work>/scan-arbitrum-config.jsonl
#   arbitrum: --blocks 7201; mainnet: --blocks 151; base: --blocks 901 with BASE_RPC_URL=https://base.meowrpc.com; each with --universe config and top

# engine detection-only step; SIGINT 20 min after "searcher ready"
LOG_JSON=1 node --import tsx --import ../research-material/07-other-chains-engine/collect/exit-flush.mjs \
  src/main.ts --chain arbitrum --mode dry --contract "" --out <work>/engine-detect-arbitrum.jsonl \
  --source logs --universe all --max-per-factory 6000 --min-depth-eth 0.1 --min-profit-usd 0.01 --top 6

# blocker evidence (unmodified default dry run; exits 1)
LOG_JSON=1 node --import tsx src/main.ts --chain arbitrum --mode dry

# packing (called by the run scripts): python3 collect/finalize.py --jsonl <work jsonl> --log <log> --out-dir <dir> --name <name>
# counts section of this manifest: python3 collect/fill_manifest.py
```

## Schemas

### `scans/*/scan-*.jsonl.gz` (raw, one JSON object per gross-positive cycle per scanned block; written by scan.ts)
| Field | Meaning / units |
|---|---|
| `block` | head block number at which all pool state was read |
| `key` | human-readable route: `SYM>SYM@<Dex>/<tier>` per hop. The tier is the fee in pips for V3/Pancake/V4, tickSpacing for Aerodrome CL, `(s)` for an Aerodrome stable pool. Symbols come from the token list, or the first 8 characters of the address when unknown |
| `token` | symbol of the start/end token (the token borrowed and returned) |
| `route` | `<Dex>/<tier>:<pool address>` per hop, joined by ` -> `. A V4 pool appears as the first 20 bytes of its pool id |
| `amountIn` | optimal input, decimal string in human units of `token` |
| `profitToken` | amountOut − amountIn, human units of `token` (before gas) |
| `profitEth` | `profitToken` converted to ETH with the engine's price map (tokens priced through WETH or USDC pools with ≥ 0.05 ETH anchor depth); NaN is serialized as `null` |
| `gasEth` | tool's gas cost for this route in ETH = (route gas estimate / 250,000) × (250,000 × eth_gasPrice + L1 fee for 700 bytes on Base) / 1e18 |
| `netEth` | `profitEth − gasEth` |
| `gapBps` | spot-price gap between the pools before fees, in bps (rounded to 0.1). For triangles, the tool's summed log-gap × 10,000 |
| `gas` | tool's gas estimate for the route (gas units) |

### `scans/*/scan-*.blocks.csv.gz` (DERIVED: lossless extraction of the `block scanned` log lines)
`time_ms` (local wall clock when the line was logged, Unix ms), `time_utc`, `block`, `gross` (rows written for this block), `net` (rows with
netEth > 0), `sumNetUsd` (sum of netEth > 0 rows × ETH/USD from the WETH/USDC price in the pool set, rounded to 0.001), `gasPriceGwei`
(`eth_gasPrice` at that iteration), `txCostUsd` (250,000 gas + L1 fee, USD), `syncMs` (state read time), `searchMs` (cycle search time).
The log's `  <route> in=… gap=… profit=$… net=$…` lines (top 5 per block) are in the raw log only.

### `engine-detect/*/engine-detect-*.jsonl.gz` (raw, written by main.ts; one object per selected candidate)
`t` (UTC ISO time written), `block` (trigger block), `fb` (0 in logs mode), `route` (as `key` above), `pools` (pool addresses in hop order; a V4
pool appears as the first 20 bytes of its id), `token`, `amountIn` (human units), `predictedProfitUsd` (local-math profit before gas, USD),
`gasUsd` (gas estimate × cached gas price, USD), `netUsd`, `gapBps`. Rows are written only for candidates with `netUsd > 0.01`
(`--min-profit-usd`), at most 6 per tick (`--top`), with no pool used twice in a tick. There are no `sim` fields, because this mode does not simulate.

### `engine-detect/*/engine-detect-*.heartbeats.csv.gz` (DERIVED: lossless extraction of `heartbeat` log lines, one every 10 ticks)
`time_utc`, `time` (Unix ms), `ticks`, `gross` (cumulative cycles found), `net` (cumulative cycles with netUsd > min), `simulated`, `simOk`,
`sent`, `landed`, `failed`, `profitEth`, `gasSpentEth` (all 0 in this mode), `staleTicks`, `logsApplied` (cumulative logs applied to pool state),
`touchedPools` (cumulative), `block`, `fb`, `syncMs`, `searchMs`, `totalMs` (last tick), `pools`.

### `*.log.gz`
The raw stdout/stderr of the tool with `LOG_JSON=1`: one pino JSON object per line (`level` 30 = info, 40 = warn, 50 = error; `time` in Unix ms;
`msg`), a `# … cmd:` header line written by the collector, the tool's plain-text output (SCAN SUMMARY), `[exit-flush]` lines, and
`exit=<code> capped=<0|1>`. Useful discovery lines: `geckoterminal request failed` (status, url), `geckoterminal pools fetched`,
`token universe built`, `pool discovery complete` (candidates, found), `uniswap v4 candidates`, `uniswap v4 pools discovered` (listed, kept,
keyFailed, unknownKey, hooked, outOfUniverse), `live pools` (count by DEX after the depth filter), `factory enumerated` (dex, total,
enumerated; engine `--universe all` only), `universe enumerated`, `searcher ready` (tokens, pools, cycles), `shutting down` (final engine stats).

### `*.meta.json`
Descriptive only: jsonl file names, row count, unparseable lines, distinct blocks, first and last block, count of `block scanned` or
`heartbeat` lines, sum of `gross` over `block scanned` lines (for comparison with the row count), first and last scanned time (UTC), the
`searcher ready` and `live pools` log objects, exit and signal lines, whether the SCAN SUMMARY is present, warn and error line counts, and
the run window (attempt, exit code, time_capped, cap_minutes, blocks_flag, SIGINT time for engine runs).

## Counts

<!-- COUNTS:BEGIN -->
Filled by `collect/fill_manifest.py` at 2026-09-30T22:18:32Z.

Sentinels: `SCANS` missing, `ENGINE_DETECT_ARBITRUM` missing, `ENGINE_DETECT_MAINNET` missing, `ENGINE_LIVE_ARBITRUM.FAILED`, `ENGINE_LIVE_MAINNET.FAILED`

| Dir / run | JSONL files | JSONL rows | rows announced in log (scan) | unparseable lines | block-scanned / heartbeat lines | first block | last block | window start (UTC) | window end (UTC) | pools after depth filter | exit | time-capped | SCAN SUMMARY present | warn / error log lines |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Scan windows: first/last `block scanned` log time. Engine windows: `searcher ready` to SIGINT. Engine block range: first/last block among written rows (empty if no row was written).

File sizes (bytes):

- `scans/arbitrum/scan-arbitrum-config.code-provenance.txt`: 4800
- `scans/base/scan-base-config.code-provenance.txt`: 4800
- `scans/mainnet/scan-mainnet-config.code-provenance.txt`: 4800

`collect/gaps.jsonl`: 0 line(s).
<!-- COUNTS:END -->

## Coverage limits and gaps

- **Simulation-based dry run on Arbitrum and Ethereum: not run.** It is blocked without a code change (see above). The substitute has no
  on-chain simulation, so it contains no revert data and no simulated profit.
- **No chain beyond Base, Arbitrum and Ethereum can be run with this code:** `bot/src/config/chains.ts` `CHAINS` defines only `base`,
  `arbitrum` and `mainnet`; `bot/src/util/client.ts` `VIEM_CHAINS` only 8453, 42161 and 1; `bot/src/research/tokens.ts` `GT_NETWORK` only those
  three; `bot/src/pools/v4.ts` `V4` only those three. Any other `--chain` value throws at `bot/src/config/chains.ts:330` (evidence:
  `collect/smoke/selftest-engine-unknown-chain.log`: `unknown chain 'selftestchain' (known: base, arbitrum, mainnet)`). No BSC, Solana,
  Optimism, Unichain, Polygon or other L2 data is produced here. The
  on-chain transaction censuses for those chains are in `../06-other-chains-onchain/`.
- **DEX coverage is the chains.ts configuration.** Arbitrum: UniswapV3, SushiV3, PancakeV3, SushiV2, plus GeckoTerminal-listed Uniswap V4
  pools. Camelot is excluded in chains.ts; no Balancer, Curve, Trader Joe, Ramses or other venues. Ethereum: UniswapV3, SushiV3,
  PancakeV3, UniswapV2, SushiV2, PancakeV2, plus GeckoTerminal-listed V4; no Curve, Balancer, Maverick, Fluid or Ekubo. Base: the 11
  venues in chains.ts plus GeckoTerminal-listed V4.
- **Uniswap V4 pools are only those GeckoTerminal lists** on the pages fetched. They must also be resolvable through the PositionManager,
  have no swap-affecting hook permission bits and no dynamic fee, and lie in the token universe. The per-run numbers are in the
  `uniswap v4 …` log lines. Full V4 enumeration from PoolManager `Initialize` events is not part of this directory; see `../01-v4-pools/`.
- **GeckoTerminal per-DEX listings that returned HTTP 404 in the smoke tests** are skipped by the tool (it logs `geckoterminal request failed`
  and continues): Arbitrum `uniswap-v3-arbitrum` and `sushiswap-arbitrum`; Ethereum `uniswap-v3` and `uniswap-v2`. HTTP 429 responses
  are retried once after 15 s. A listing that still fails is skipped, and the warn line stays in the log. The top-universe token lists
  are therefore built from the listings that succeeded.
- **Block sampling:** scans read state at the heads they reach, not at every block. Heads that arrive during an iteration, including
  the slow forced resync every 15 iterations, are skipped. `blocks.csv` lists exactly which blocks were scanned.
- **Time cap:** runs ended by the 31-min SIGTERM have no plain-text SCAN SUMMARY. All their rows and per-block lines are kept.
- **Base scans use a different RPC** (`base.meowrpc.com`) from the §2.1 Base scans (`base-rpc.publicnode.com`), so per-iteration sync time
  and the number of heads scanned differ from those scans. Each run's `syncMs` is recorded per block.
- **Depth filter:** scans use the default `--min-depth-eth 0.2`; the engine runs use 0.1. Pools below these thresholds are not searched
  here. Only their counts are visible, via `pool discovery complete` (found) vs `live pools` (kept).
- **`--universe all` on Arbitrum enumerates one factory** (SushiV2 newest 6,000 of its `allPairsLength`), because chains.ts has no other
  V2-style or Aerodrome-style factory for Arbitrum. On Ethereum it enumerates the newest 6,000 each of UniswapV2, SushiV2 and PancakeV2.
  Older pairs are not enumerated.
- **Concurrent code edits:** another agent modified `bot/src` (opt-in `--v4-pools`) while these runs were set up. See `*.code-provenance.txt`.
- **Stray files outside this directory:** `/scan-base-config.log` and `/scan-eth-config.log` (1 KB each, at the filesystem root) were
  created by a mis-scoped smoke-test command at 21:44Z. They contain only a Node "module not found" error, are not data, and could not be
  deleted by this agent because a safety check blocks removal at `/`.
- Failed attempts and unrecoverable steps are appended to `collect/gaps.jsonl`, one JSON object per line: `t`, `step`, `reason`. An empty
  or missing file means none occurred.
