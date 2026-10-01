# 07-other-chains-engine: repository scanner and engine on Arbitrum and Ethereum, with a same-method Base scan

**Status:** COMPLETE WITH GAPS (finalized 2026-10-01). Sentinels: `SCANS.DONE`, `ENGINE_DETECT_ARBITRUM.DONE`,
`ENGINE_DETECT_MAINNET.DONE`, `ENGINE_LIVE_ARBITRUM.FAILED`, `ENGINE_LIVE_MAINNET.FAILED`. All six scans and both detection-only
engine runs finished and are packed. Gaps:
1. Simulation-based engine dry run (`--mode dry` with executor simulation) on Arbitrum and Ethereum: not run. It is blocked without a
   code change (sentinels `ENGINE_LIVE_ARBITRUM.FAILED` and `ENGINE_LIVE_MAINNET.FAILED`; see "Method: engine on Arbitrum and
   Ethereum"). The detection-only substitute in `engine-detect/` has no simulation fields.
2. No data for chains other than Base, Arbitrum and Ethereum (BSC, Solana, Optimism, Unichain, Polygon and other L2s): the code accepts
   only these three chains (see "Coverage limits and gaps").

The other coverage limits (V4 pools limited to GeckoTerminal listings, newest 6,000 pairs per V2-style factory, depth filters, block
sampling, time caps) are listed under "Coverage limits and gaps".

Run notes: collectors were launched 2026-09-30T22:14:28Z (master PID in `collect/state/run_all.pid`, log `collect/run_all.log`,
step log `collect/pipeline.log`).

*Added 2026-10-01 (container restart):* all processes died in a container restart at about 2026-09-30T22:58Z, while the three
`--universe top` scans were running (started 22:45:10Z mainnet, 22:46:18Z arbitrum, 22:49:27Z base). The pipeline was relaunched at
2026-10-01T01:04:58Z (`collect/pipeline.log`, line "relaunch after container restart"). The three `config` scans had finished and were
skipped. The three `top` scans were redone from scratch: `run_scan.sh` deletes the work JSONL and overwrites the log at the start of each
attempt, so nothing from the interrupted attempts is kept, and the re-runs are labelled "attempt 1" again. The interrupted attempts are
not recorded in `collect/gaps.jsonl`. The two detection-only engine runs ran after the re-run scans (started 01:39:25Z mainnet,
01:41:52Z arbitrum), each on its first attempt. `collect/run_all.log` holds both launches; `collect/pipeline.log` also holds the smoke
tests and the failure-path self-test.

The "Counts" section (between the COUNTS markers) is rewritten by `collect/fill_manifest.py` (descriptive metadata only). A detached
waiter (`collect/manifest_waiter.sh`, log `collect/manifest_waiter.log`) runs it every 5 min. It can also be run by hand.
*Corrected 2026-10-01:* this paragraph originally said the waiter runs fill_manifest.py one last time and exits once the sentinels
SCANS, ENGINE_DETECT_ARBITRUM and ENGINE_DETECT_MAINNET exist. Its test `have()` runs `ls NAME.DONE NAME.FAILED`, which succeeds only
if both files exist, so it never detected completion. At finalization it was still running (started 2026-10-01T01:05:00Z) and it stops
at its 8-hour limit, about 2026-10-01T09:05Z. Until then it rewrites the Counts section every 5 min (same values, new timestamp) and
appends one line to its log. fill_manifest.py also rewrites the first line that begins with `Status: `; the status at the top of this
file was finalized by hand on 2026-10-01 and is not written in that form, so fill_manifest.py leaves it unchanged. Everything else in
this file is static.
*Corrected 2026-10-01 (fixup):* the waiter did not run until ~09:05Z. The main session stopped it; the last line of
`collect/manifest_waiter.log` is `2026-10-01T02:56:31Z stopped by the main session (manifest counts finalized by the 2026-10-01
verification pass)`. Its last refresh of the Counts section is the one stamped 2026-10-01T02:55:01Z. No waiter or fill_manifest.py
process was running at the time of this fixup (~04:50Z), and the Counts section is no longer rewritten. The whole file is now static.

This directory holds data only. Nothing here states a finding. The exception is `prior-summaries.md`, which quotes docs/ANALYSIS.md
verbatim, including that document's own evaluative statements. Those statements are quoted text; they were not produced from the data in
this folder.
**Label (added 2026-10-01): `prior-summaries.md` is prior session text, not data.** It quotes conclusions and evaluative statements
that an earlier session wrote in docs/ANALYSIS.md. Treat it as claims made by that session, not as measurements. Where it is listed
below (question-line table, layout, inventory) the same label applies.

## Question lines served (mapping only)

Line numbers refer to the eight QUESTION LINES of this research task.

| Question line | Files in this folder |
|---|---|
| 1 | `scans/base/scan-base-config.log.gz`, `scans/base/scan-base-top.log.gz` (log lines `uniswap v4 candidates`, `uniswap v4 pools discovered`, `live pools` field `byDex.UniswapV4`); `scans/base/scan-base-config.meta.json`, `scans/base/scan-base-top.meta.json` (`live_pools.byDex.UniswapV4`); `scans/base/scan-base-config.jsonl.gz`, `scans/base/scan-base-top.jsonl.gz` (rows whose `route` contains `UniswapV4/`); the same log lines for Arbitrum and Ethereum in `scans/arbitrum/*.log.gz`, `scans/mainnet/*.log.gz`, `engine-detect/*/*.log.gz` |
| 2 | `engine-detect/arbitrum/engine-detect-arbitrum.log.gz`, `engine-detect/mainnet/engine-detect-mainnet.log.gz` (log lines `factory enumerated`, `universe enumerated; resolving every venue per pair`); uncompressed copies `collect/engine-detect-arbitrum.log`, `collect/engine-detect-mainnet.log` |
| 3 | `scans/*/*.log.gz` (log lines `pool discovery complete`, `live pools`); `scans/*/*.meta.json` (`live_pools`); `engine-detect/*/*.log.gz` (log lines `pool discovery complete`, `searcher ready`); `engine-detect/*/*.meta.json` (`searcher_ready`) |
| 4 | `scans/arbitrum/*`, `scans/mainnet/*`, `scans/base/*`; `engine-detect/arbitrum/*`, `engine-detect/mainnet/*`; `collect/engine-blocker-check-arbitrum.log`, `collect/engine-blocker-check-mainnet.log`; `collect/smoke/selftest-engine-unknown-chain.log`; `prior-summaries.md` (Excerpts 1 and 3; prior session text, not data). The raw §2.1 scans themselves are in `../00-prior-runs/block-scans/` (mapped in that folder's manifest) |
| 5 | none |
| 6 | none |
| 7 | none |
| 8 | `scans/base/scan-base-config.log.gz`, `scans/base/scan-base-top.log.gz` (log lines `uniswap v4 candidates`, `uniswap v4 pools discovered`); `scans/base/scan-base-config.meta.json`, `scans/base/scan-base-top.meta.json` (`live_pools.byDex.UniswapV4`) |

*Corrected 2026-10-01:* the earlier version of this table quoted the question lines and added explanations. It now maps line numbers to
files only. The explanations that were provenance are kept in the method sections below.

## Directory layout

```
MANIFEST.md
prior-summaries.md                        verbatim excerpts of docs/ANALYSIS.md (no commentary added); prior session text, not data
scans/<chain>/scan-<chain>-<universe>.jsonl.gz          raw rows written by scan.ts --out (or -part-NNNN.jsonl.gz if split; no file was split)
scans/<chain>/scan-<chain>-<universe>.log.gz            raw stdout/stderr of scan.ts (pino JSON lines + plain-text SCAN SUMMARY if it finished)
scans/<chain>/scan-<chain>-<universe>.blocks.csv.gz     DERIVED: one row per "block scanned" log line
scans/<chain>/scan-<chain>-<universe>.meta.json         descriptive metadata (row counts, first/last block and time, exit, signal)
scans/<chain>/scan-<chain>-<universe>.code-provenance.txt   git HEAD, uncommitted bot/src changes, sha256 of every bot/src/*.ts at launch
engine-detect/<chain>/engine-detect-<chain>.{jsonl.gz,log.gz,heartbeats.csv.gz,meta.json,code-provenance.txt}
collect/                                  collector scripts, logs, gaps.jsonl (created only if a step fails; not present, see below)
collect/<name>.log                        uncompressed raw log of each run; byte-identical to the decompressed <name>.log.gz
collect/smoke/                            smoke-test logs (scans: 4-45 blocks per config at 21:42-22:08Z; engine: 2 min per chain), failure-path self-test log
collect/state/, collect/work/             transient working state (git-ignored, local-only); work/ holds the uncompressed JSONL while a run is live
```
`<chain>` is arbitrum, mainnet or base; `<universe>` is config or top.

*Added 2026-10-01:* `collect/manifest_waiter.sh` and `collect/manifest_waiter.log` (see Run notes) are also in `collect/`. The
sentinel files are in `research-material/.sentinels/`, outside this folder; that directory is git-ignored, so the sentinels are not in the
repository. Their texts: `SCANS.DONE` "all 6 scans finished 2026-10-01T01:48:37Z; outputs in …/07-other-chains-engine/scans";
`ENGINE_DETECT_ARBITRUM.DONE` "done 2026-10-01T02:02:49Z; outputs in …/engine-detect/arbitrum"; `ENGINE_DETECT_MAINNET.DONE`
"done 2026-10-01T02:01:27Z; outputs in …/engine-detect/mainnet". `ENGINE_LIVE_ARBITRUM.FAILED` and `ENGINE_LIVE_MAINNET.FAILED` give
the reason stated in "Method: engine on Arbitrum and Ethereum" (same main.ts and executor.ts line references, same evidence logs).

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

Code (original text): repository at git HEAD `1c1a93feee5cd05b5efc32ce39c35c39ba7ddd04`, run unmodified. Node v22.22.2, viem 2.57.1, tsx 4.23.15.
Another agent edited `bot/src` in the working tree while this collection ran: an opt-in `--v4-pools` flag in `main.ts`, a `makeV4Pool`
refactor in `pools/v4.ts`, and a new `pools/v4file.ts`, all modified 22:06–22:10Z. None of the runs here pass `--v4-pools`. Each run's exact
code state is in its `*.code-provenance.txt`.

*Corrected 2026-10-01:* the git HEAD above applies to the three `config` scans only. Per run, from the `*.code-provenance.txt` files:
- `config` scans (launched 2026-09-30T22:14:28Z): git HEAD `1c1a93feee5cd05b5efc32ce39c35c39ba7ddd04` plus the uncommitted `bot/src`
  edits named above (`main.ts`, `pools/v4.ts` modified, `pools/v4file.ts` new). `bot/src/research/scan.ts` was not modified.
- `top` scans (launched 2026-10-01T01:04:58Z): git HEAD `5c1baf2b6a5537163957e65967ab1c77929736c7` ("engine: opt-in --v4-pools flag to
  load every V4 pool from PoolManager Initialize data"), no uncommitted changes under `bot/src`. Compared with the `config` scans, the
  sha256 of every `bot/src/**/*.ts` file is the same except `main.ts` (now `04a6d5d3…`) and `pools/v4file.ts`.
- engine-detect runs (launched 2026-10-01T01:39:25Z mainnet, 01:41:52Z arbitrum): git HEAD `376519a1b4f1247370ec70777906b2d048194c26`,
  no uncommitted changes under `bot/src`; the sha256 of every `bot/src/**/*.ts` file is identical to the `top` scans'.
- Node v22.22.2, viem 2.57.1, tsx 4.23.15 for all runs. None of the runs pass `--v4-pools`.

## Method: block-level scans (`bot/src/research/scan.ts`, unmodified)

The block-level scans summarized in docs/ANALYSIS.md §2.1 (excerpt in `prior-summaries.md`) did not keep their raw output; the scans in
`scans/` are new runs with raw output kept.
*Corrected 2026-10-01 (fixup):* the raw output of the §2.1 scans was kept after all. It was found later in the git-ignored `bot/data/` and
copied (gzip, byte-identical after decompression) to `../00-prior-runs/block-scans/` on 2026-10-01 (commit 9c8a37c): `scan-arb.jsonl/.log`,
`scan-arb2.jsonl/.log`, `scan-mainnet.jsonl/.log`, `scan-base.jsonl`, `scan-base-run1..4` logs, `scan-base-run4.jsonl`,
`scan-base-longtail.jsonl/.log`, plus `prof.log` and `repro.log`. They were produced on 2026-09-30 between ~10:28Z and 12:15Z by
`bot/src/research/scan.ts` as it was at that time (per `../00-prior-runs/MANIFEST.md`; whether that version equals the one used here was not
checked). Inventory, checksums and per-file descriptions are in `../00-prior-runs/MANIFEST.md`. The scans in
`scans/` are still separate, new runs.

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
  *Added 2026-10-01 (recorded outcome, from `meta.json`):* the four Arbitrum and Base scans ended on the time cap (exit 143,
  `time_capped` 1, no SCAN SUMMARY); the two Ethereum scans finished by themselves after 151 heads (exit 0, `time_capped` 0, SCAN
  SUMMARY present).
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
statements to lines 59, 61–64, 138, 158 and 274. *Added 2026-10-01:* in `main.ts` as committed at 5c1baf2 (sha256 `04a6d5d3…`, the
version the engine-detect runs loaded) the same statements are at lines 59 (`contract`), 61–64 (`codeOverride`), 139–140 (`new
Executor`), 159 (`selfCheck`) and 275–279 (the `opportunity (no contract configured; not simulated)` branch).
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
- Sentinels: `ENGINE_DETECT_ARBITRUM.DONE|FAILED`, `ENGINE_DETECT_MAINNET.DONE|FAILED`. *Added 2026-10-01:* both are `.DONE`.
- Up to 3 attempts. An attempt that exits before `searcher ready` or before the window ends is recorded in `collect/gaps.jsonl`, its log is
  kept as `collect/engine-detect-<chain>.attemptN.log`, and the run is redone from scratch. *Added 2026-10-01:* both runs completed on
  attempt 1; no `collect/engine-detect-<chain>.attemptN.log` file exists.
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

*Added 2026-10-01:* `collect/state/` is not in the repository. In a fresh checkout, `run_all.sh` finds no `<name>.done` marker, treats
every step as unfinished and re-collects it live (new blocks), overwriting the committed outputs. The commands under [L3] below recreate
the markers without collecting. Live windows cannot be re-collected for the same blocks.

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
Filled by `collect/fill_manifest.py` at 2026-10-01T02:55:01Z.

Sentinels: `SCANS.DONE`, `ENGINE_DETECT_ARBITRUM.DONE`, `ENGINE_DETECT_MAINNET.DONE`, `ENGINE_LIVE_ARBITRUM.FAILED`, `ENGINE_LIVE_MAINNET.FAILED`

| Dir / run | JSONL files | JSONL rows | rows announced in log (scan) | unparseable lines | block-scanned / heartbeat lines | first block | last block | window start (UTC) | window end (UTC) | pools after depth filter | exit | time-capped | SCAN SUMMARY present | warn / error log lines |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| engine-detect/arbitrum/engine-detect-arbitrum | engine-detect-arbitrum.jsonl.gz | 0 | - | 0 | 401 | None | None | 2026-10-01T01:42:43Z | 2026-10-01T02:02:43Z | 83 | 130 | - | - | 2 / 0 |
| engine-detect/mainnet/engine-detect-mainnet | engine-detect-mainnet.jsonl.gz | 15 | - | 0 | 10 | 26094243 | 26094323 | 2026-10-01T01:41:20Z | 2026-10-01T02:01:21Z | 1740 | 130 | - | - | 2 / 0 |
| scans/arbitrum/scan-arbitrum-config | scan-arbitrum-config.jsonl.gz | 132443 | 132443 | 0 | 645 | 510475000 | 510481479 | 2026-09-30T22:15:07.557Z | 2026-09-30T22:46:00.364Z | 151 | 143 | 1 | False | 2 / 0 |
| scans/arbitrum/scan-arbitrum-top | scan-arbitrum-top.jsonl.gz | 109075 | 109075 | 0 | 495 | 510511390 | 510517978 | 2026-10-01T01:10:39.280Z | 2026-10-01T01:41:45.963Z | 230 | 143 | 1 | False | 11 / 0 |
| scans/base/scan-base-config | scan-base-config.jsonl.gz | 65207 | 65207 | 0 | 248 | 52008645 | 52009606 | 2026-09-30T22:18:17.563Z | 2026-09-30T22:49:22.659Z | 255 | 143 | 1 | False | 1 / 0 |
| scans/base/scan-base-top | scan-base-top.jsonl.gz | 56322 | 56322 | 0 | 209 | 52014010 | 52014982 | 2026-10-01T01:17:24.600Z | 2026-10-01T01:48:35.717Z | 558 | 143 | 1 | False | 5 / 0 |
| scans/mainnet/scan-mainnet-config | scan-mainnet-config.jsonl.gz | 13385 | 13385 | 0 | 151 | 26093214 | 26093364 | 2026-09-30T22:14:50.493Z | 2026-09-30T22:45:04.686Z | 112 | 0 | 0 | True | 2 / 0 |
| scans/mainnet/scan-mainnet-top | scan-mainnet-top.jsonl.gz | 18048 | 18048 | 0 | 151 | 26094082 | 26094232 | 2026-10-01T01:09:28.771Z | 2026-10-01T01:39:19.823Z | 367 | 0 | 0 | True | 12 / 0 |

Scan windows: first/last `block scanned` log time. Engine windows: `searcher ready` to SIGINT. Engine block range: first/last block among written rows (empty if no row was written).

File sizes (bytes):

- `engine-detect/arbitrum/engine-detect-arbitrum.code-provenance.txt`: 4427
- `engine-detect/arbitrum/engine-detect-arbitrum.heartbeats.csv.gz`: 7458
- `engine-detect/arbitrum/engine-detect-arbitrum.jsonl.gz`: 59
- `engine-detect/arbitrum/engine-detect-arbitrum.log.gz`: 7388
- `engine-detect/arbitrum/engine-detect-arbitrum.meta.json`: 1120
- `engine-detect/mainnet/engine-detect-mainnet.code-provenance.txt`: 4427
- `engine-detect/mainnet/engine-detect-mainnet.heartbeats.csv.gz`: 529
- `engine-detect/mainnet/engine-detect-mainnet.jsonl.gz`: 1664
- `engine-detect/mainnet/engine-detect-mainnet.log.gz`: 3237
- `engine-detect/mainnet/engine-detect-mainnet.meta.json`: 1131
- `scans/arbitrum/scan-arbitrum-config.blocks.csv.gz`: 11838
- `scans/arbitrum/scan-arbitrum-config.code-provenance.txt`: 4800
- `scans/arbitrum/scan-arbitrum-config.jsonl.gz`: 7627037
- `scans/arbitrum/scan-arbitrum-config.log.gz`: 28144
- `scans/arbitrum/scan-arbitrum-config.meta.json`: 1236
- `scans/arbitrum/scan-arbitrum-top.blocks.csv.gz`: 9219
- `scans/arbitrum/scan-arbitrum-top.code-provenance.txt`: 4427
- `scans/arbitrum/scan-arbitrum-top.jsonl.gz`: 6711231
- `scans/arbitrum/scan-arbitrum-top.log.gz`: 22416
- `scans/arbitrum/scan-arbitrum-top.meta.json`: 1233
- `scans/base/scan-base-config.blocks.csv.gz`: 5029
- `scans/base/scan-base-config.code-provenance.txt`: 4800
- `scans/base/scan-base-config.jsonl.gz`: 3960257
- `scans/base/scan-base-config.log.gz`: 15551
- `scans/base/scan-base-config.meta.json`: 1344
- `scans/base/scan-base-top.blocks.csv.gz`: 4775
- `scans/base/scan-base-top.code-provenance.txt`: 4427
- `scans/base/scan-base-top.jsonl.gz`: 3790930
- `scans/base/scan-base-top.log.gz`: 11551
- `scans/base/scan-base-top.meta.json`: 1361
- `scans/mainnet/scan-mainnet-config.blocks.csv.gz`: 4132
- `scans/mainnet/scan-mainnet-config.code-provenance.txt`: 4800
- `scans/mainnet/scan-mainnet-config.jsonl.gz`: 636074
- `scans/mainnet/scan-mainnet-config.log.gz`: 11422
- `scans/mainnet/scan-mainnet-config.meta.json`: 1170
- `scans/mainnet/scan-mainnet-top.blocks.csv.gz`: 4138
- `scans/mainnet/scan-mainnet-top.code-provenance.txt`: 4427
- `scans/mainnet/scan-mainnet-top.jsonl.gz`: 1132513
- `scans/mainnet/scan-mainnet-top.log.gz`: 10312
- `scans/mainnet/scan-mainnet-top.meta.json`: 1168

`collect/gaps.jsonl`: 0 line(s).
<!-- COUNTS:END -->

## Verified inventory (2026-10-01)

Verified 2026-10-01T02:50:30Z by streaming every file (no file loaded whole): `gzip -t` on every `.gz` file, line counts of the decompressed
stream, a JSON parse of every line of every `.jsonl`/`.jsonl.gz` file and of every `.json` file, sha256 of the file bytes. Every check
passed. The row counts match the "Counts" section and each `meta.json` (`jsonl_rows`, `log_block_scanned_lines`,
`log_heartbeat_lines`). The largest committed file is `scans/arbitrum/scan-arbitrum-config.jsonl.gz` (7,627,037 bytes); no committed file
exceeds 90 MB. Committed: 79 files, 26352688 bytes (MANIFEST.md not counted). Local-only (git-ignored): 37 files, 178229085 bytes.

| File | Bytes | Rows / lines | Checks | sha256 | Git |
|---|---|---|---|---|---|
| `MANIFEST.md` | (this file) | (this file) | - | not listed (this file) | committed |
| `collect/engine-blocker-check-arbitrum.log` | 8727 | 9 lines | - | `a4e688bae0f4e8b6f4ef2a78b1a3203cb2531cb87e0aef0935c517bc2b1c4b40` | committed |
| `collect/engine-blocker-check-mainnet.log` | 8700 | 9 lines | - | `eaa1b61a92f5b29c947a4d62e821b3ffdd7e83a5a490574ac47820e22686287b` | committed |
| `collect/engine-detect-arbitrum.log` | 131301 | 416 lines | - | `a36cb2815058ecfdfad8d662af8f25b0935d5c7b9dd1cedfa6d32fae979bc926` | committed |
| `collect/engine-detect-mainnet.log` | 12769 | 42 lines | - | `1d457b78ccb3a707568692fd19ddca2e83ab21a963c83fe75a41155449e21de3` | committed |
| `collect/exit-flush.mjs` | 1183 | 22 lines | - | `b43172aa7db1b1b676db489be830551db8695b25bd3c2108538b929e3175d6ca` | committed |
| `collect/fill_manifest.py` | 5074 | 83 lines | - | `64724c179aa8d5cc1d1eca618c3d085b33a4d5c14a2394150884e72f57504175` | committed |
| `collect/finalize.py` | 7108 | 153 lines | - | `7b60f5d67fa71f0a593db026a4a689a9491a76d9e47116fbb2f265acc04fd3a1` | committed |
| `collect/manifest_waiter.log` | 4833 | 32 lines | final (corrected 2026-10-01 fixup: the row previously read 4549 bytes, 30 lines, sha256 `df779a749210b3b62ba706ecfacbc768ab662d4668cee6d25ac0644f26544ea6`, "still growing ... until about 09:05Z", as of 02:50:30Z; the waiter was stopped at 02:56:31Z, see Run notes) | `889732ab52ac714b82aec2fe1b656f74a124542d6f5e69cbef879a0e1bac59a7` | committed (af9f68d) |
| `collect/manifest_waiter.sh` | 743 | 15 lines | - | `e020ab66682e0db5f38c71ab8ea8b2b8bb8ce16703d36c72ce4df1b152df4488` | committed |
| `collect/pipeline.log` | 7365 | 54 lines | - | `49230c361813281cd9627b6d83d777de182533e42053034683acf0d94cb4380f` | committed |
| `collect/provenance.sh` | 830 | 15 lines | - | `b543562218de3a1fc569bf34f23698fafd044ae80c1441811f1db375db153a32` | committed |
| `collect/run_all.log` | 6015 | 48 lines | - | `670c30b29f8c8d20265cde60c4b352cbfc4301ef8b93c952973bd510aaeca16c` | committed |
| `collect/run_all.sh` | 3168 | 63 lines | - | `8b488e71cb49da63939336cd30fc6b8f6e60d6d67cb2a855176e80f6391417c0` | committed |
| `collect/run_engine_detect.sh` | 4501 | 72 lines | - | `1c1b7a75cb6a5dd0fe68d9c37fcc4465121ea815fb492d4c14410b76a35ed158` | committed |
| `collect/run_scan.sh` | 4003 | 62 lines | - | `c1d4efb9cd4874f3f68e6b997858b24b3a6fb1b96a38d72f686c7af5a9873c3b` | committed |
| `collect/scan-arbitrum-config.log` | 680462 | 3882 lines | - | `0e6d8df78fb272ede087d197d472d0b75822226e4824624aea4c608a6708bdd0` | committed |
| `collect/scan-arbitrum-top.log` | 523515 | 2993 lines | - | `5dbc1c0771f6fdb0192aaef6951acaf68c0ff99a9e7c7d26def0457b1b2d8284` | committed |
| `collect/scan-base-config.log` | 272583 | 1499 lines | - | `6196fb51f52352ec13b75c87958b25223d779ca713c86850a6c4418a8c0b17bf` | committed |
| `collect/scan-base-top.log` | 233977 | 1271 lines | - | `9054d171e3fa35619d9c7eb84a0f993322ef1b06813735a7ac6af05ba5d07580` | committed |
| `collect/scan-mainnet-config.log` | 165692 | 943 lines | - | `e14325d5035c2346d3b67f1e6c01980a388b08e44ec49d588a5969dc56103e29` | committed |
| `collect/scan-mainnet-top.log` | 166001 | 955 lines | - | `105e1be1933bb3321ca76b978a39376b880b93e2371990849a95b21f2b622dff` | committed |
| `collect/smoke/selftest-engine-unknown-chain.log` | 998 | 14 lines | - | `2b223e9e09232bcf96dfdf9019657d70dc328ce7d68e4cb4dea4a5d0d2838e86` | committed |
| `collect/smoke/smoke-engine-arbitrum.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `collect/smoke/smoke-engine-arbitrum.jsonl` | 0 | 0 rows (empty) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `collect/smoke/smoke-engine-arbitrum.log` | 15824 | 56 lines | - | `5e934b825c5c7b4180c835daf728942c03521ca217e59b3c1c15074f2ae11b05` | committed |
| `collect/smoke/smoke-engine-arbitrum.pid` | 6 | 1 line | - | `a8b7dedea4d6d6b427c59c6a46787cd8ded8505be3759aff784f1a5472b288c8` | committed |
| `collect/smoke/smoke-engine-arbitrum.window.json` | 85 | 1 line | parses as JSON | `5fa7b6f691e9d265ba8f64550b0d965588331bd132f492526f1fb84b46610320` | committed |
| `collect/smoke/smoke-engine-mainnet.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | committed |
| `collect/smoke/smoke-engine-mainnet.jsonl` | 2026 | 6 rows | every line parses as JSON | `50a05be916592a703f7561b6f3bdf853183c2990053a389ffba9f230af75a2e4` | committed |
| `collect/smoke/smoke-engine-mainnet.log` | 5746 | 23 lines | - | `15d36e4c5ba1fde5991fd2941092dbe0f89a9049385b4085ea835b2851a4e127` | committed |
| `collect/smoke/smoke-engine-mainnet.pid` | 6 | 1 line | - | `fb433407e47b1a8687f686e4e44cba3237cdbe1b7353b9bfcfa971b18ed5cafb` | committed |
| `collect/smoke/smoke-engine-mainnet.window.json` | 85 | 1 line | parses as JSON | `2a59f03478ac023225b8fedad530b923a278002f2e826cb821434dcf1d434b94` | committed |
| `collect/smoke/smoke-scan-arb-config.log.gz` | 1488 | 68 lines | gzip -t OK | `19e91d01420f2a1f13d8caf3d68234593cea61366fa9d71b6769da8f398f631e` | committed |
| `collect/smoke/smoke-scan-arb-top.log.gz` | 3456 | 303 lines | gzip -t OK | `16320b3bdba2d97ae396fbf06f7b7e7fe440acae9c7ed2670a72a1b4ceae43c7` | committed |
| `collect/smoke/smoke-scan-base-config.log.gz` | 2144 | 139 lines | gzip -t OK | `66695bd40cea3ec5344f9f9e16a80afc2382a3a6a2cc647b7f6325a9439a0134` | committed |
| `collect/smoke/smoke-scan-base-top.log.gz` | 3141 | 165 lines | gzip -t OK | `bfef33a0913f127afc6ce9d7a068f001adc7e7e82774611301420b0fd43f62f9` | committed |
| `collect/smoke/smoke-scan-eth-config.log.gz` | 1380 | 46 lines | gzip -t OK | `408197cf1ec974e75f913e1f2c5eef32a1697de5c0a5af0cb73db3eca53d4fa6` | committed |
| `collect/smoke/smoke-scan-eth-top.log.gz` | 1568 | 59 lines | gzip -t OK | `56725ed398ebafc8dbdbfb553cc016a57d4649b77e7dddb172d632b612a49ded` | committed |
| `collect/state/engine-detect-arbitrum.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/engine-detect-arbitrum.pid` | 6 | 1 line | - | `50cf76268d0b73f58590b67b867f0b8bda7b603c0ef2996a1bcaf0edab2fb639` | local-only [L4] |
| `collect/state/engine-detect-arbitrum.window.json` | 109 | 1 line | parses as JSON | `adda22e0bdcc9ec900cca2fc65d43b4f99f62832bbf4015b4c67384286f59b28` | local-only [L2] |
| `collect/state/engine-detect-mainnet.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/engine-detect-mainnet.pid` | 6 | 1 line | - | `99ae73d3c9485e7be77ed1cdc8c6ceffd8a07ad133ef7575eb6bbc0cd8296e74` | local-only [L4] |
| `collect/state/engine-detect-mainnet.window.json` | 109 | 1 line | parses as JSON | `c1bce3808005628b9d4cce436fdedeb611e351b0133af98908a80672fcc5c22d` | local-only [L2] |
| `collect/state/run_all.pid` | 4 | 1 line | - | `4fc50863286fe7f295042379d99ff3f8747138035c8a9dd724bab03ffb58665e` | local-only [L4] |
| `collect/state/scan-arbitrum-config.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-arbitrum-config.pid` | 6 | 1 line | - | `01488bb90a9dfe478c42010afb609976921c3ff1e7ca5de0abd745e9d8a18c05` | local-only [L4] |
| `collect/state/scan-arbitrum-config.window.json` | 166 | 1 line | parses as JSON | `174310228748f8383d04613c116b5ceb5510794b2b865a46023b003b1d7704ef` | local-only [L2] |
| `collect/state/scan-arbitrum-top.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-arbitrum-top.pid` | 5 | 1 line | - | `81d4783a2b23a2cec65938e818a4236830b3fd84575bc0b90ae84433d15da2ca` | local-only [L4] |
| `collect/state/scan-arbitrum-top.window.json` | 166 | 1 line | parses as JSON | `e6d23382cfd5a7e1fea157b8b829dae3a94b0b6749961a2452eee5e8b26d5bf9` | local-only [L2] |
| `collect/state/scan-base-config.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-base-config.pid` | 6 | 1 line | - | `ee9b79e92ed6b38c694fc3257941a10a4031df433f21e8d3ebc9980e847adee9` | local-only [L4] |
| `collect/state/scan-base-config.window.json` | 165 | 1 line | parses as JSON | `3ae42af311d7fc7988b8a06c6edc13de47b2306f100288d8aa827cf4983029a7` | local-only [L2] |
| `collect/state/scan-base-top.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-base-top.pid` | 5 | 1 line | - | `a13fc47e3cc977685cfb5bc68829feeca6d609499dd611b13a8f0cc8d2211a46` | local-only [L4] |
| `collect/state/scan-base-top.window.json` | 165 | 1 line | parses as JSON | `1605df15fcc2c1962d7140f38e9b7706fc62264ae37a1e3b6493db3438db89ad` | local-only [L2] |
| `collect/state/scan-mainnet-config.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-mainnet-config.pid` | 6 | 1 line | - | `ac38e6011c417909d72938dd0068e7c0e0e5a8f10159d165491ca85afffd3a33` | local-only [L4] |
| `collect/state/scan-mainnet-config.window.json` | 163 | 1 line | parses as JSON | `98bf8a4f4969b753e7ca04002a1acaf65e8c2456851554697488629025f597cf` | local-only [L2] |
| `collect/state/scan-mainnet-top.done` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scan-mainnet-top.pid` | 5 | 1 line | - | `ab6557812843af78e1517a997d9fd98e61cd0d61f1dfd9059789cef3f2cd9eda` | local-only [L4] |
| `collect/state/scan-mainnet-top.window.json` | 163 | 1 line | parses as JSON | `4486ce8531c0a2e1aa7ea5229abee9473f9d44d9b384929cbbf7e47f2c494fa1` | local-only [L2] |
| `collect/state/scans-arbitrum.finished` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scans-base.finished` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scans-mainnet.finished` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/state/scans.lock` | 0 | 0 (empty file) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L3] |
| `collect/work/engine-detect-arbitrum.jsonl` | 0 | 0 rows (empty) | - | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | local-only [L1] |
| `collect/work/engine-detect-mainnet.jsonl` | 4975 | 15 rows | every line parses as JSON | `208f1e705f38d145ade325a8cc422270ded04688554a0a6b01c3b7f781310a48` | local-only [L1] |
| `collect/work/scan-arbitrum-config.jsonl` | 60163858 | 132443 rows | every line parses as JSON | `39cb28b5232c3c5ae870f2301d44dcaedce80d36728e79446297bd96ccca6c82` | local-only [L1] |
| `collect/work/scan-arbitrum-top.jsonl` | 49610125 | 109075 rows | every line parses as JSON | `ada58b08f33c54b6ad8ad0c87466dd88ce40764ece71f44571c898f9cf29fedb` | local-only [L1] |
| `collect/work/scan-base-config.jsonl` | 29036563 | 65207 rows | every line parses as JSON | `7c540b7de30ad8fd2bb372cc0a4a35c91cc2586286411df6bd543f5e46577009` | local-only [L1] |
| `collect/work/scan-base-top.jsonl` | 25512590 | 56322 rows | every line parses as JSON | `df41509ce9107d92b7731696f6ba4dfeffd5e3096036c38ece81a57cd6f1c296` | local-only [L1] |
| `collect/work/scan-mainnet-config.jsonl` | 5960616 | 13385 rows | every line parses as JSON | `548a66d8701177ccdb643acad58eff95400de7d2ff498b7421cbf60601d9d1a2` | local-only [L1] |
| `collect/work/scan-mainnet-top.jsonl` | 7939103 | 18048 rows | every line parses as JSON | `cd15b864be575b928eb50842eed44ac9c91433e455bafa71e1e80f2107f7fe9c` | local-only [L1] |
| `engine-detect/arbitrum/engine-detect-arbitrum.code-provenance.txt` | 4427 | 51 lines | - | `3a08c0365df3b2a1635d0baaecfe75f5527b074ff77586eaed52c1316f834de8` | committed |
| `engine-detect/arbitrum/engine-detect-arbitrum.heartbeats.csv.gz` | 7458 | 402 lines (header + 401 rows) | gzip -t OK | `0119778404a7d4760cc2ea5e4aacda0d024db7e65113bb283c1bc8675683921e` | committed |
| `engine-detect/arbitrum/engine-detect-arbitrum.jsonl.gz` | 59 | 0 rows (empty) | gzip -t OK | `695f0a8a181c4de0548a987f1af2ae3f948cd642aa5c2a4fd448a1033147c418` | committed |
| `engine-detect/arbitrum/engine-detect-arbitrum.log.gz` | 7388 | 416 lines | gzip -t OK | `e3470fbce7b930c5c59b13224bb7546483170338b3d8a7dff0b6d0fa87b6babc` | committed |
| `engine-detect/arbitrum/engine-detect-arbitrum.meta.json` | 1120 | 44 lines, no final newline | parses as JSON | `06344c4daaa8218f67b9c8d25d031e625a332b3a151f9b37282f027e01e874de` | committed |
| `engine-detect/mainnet/engine-detect-mainnet.code-provenance.txt` | 4427 | 51 lines | - | `2315d8b5e78bd401f8b8875caa884a86b1d4791171bf582622381741916caae8` | committed |
| `engine-detect/mainnet/engine-detect-mainnet.heartbeats.csv.gz` | 529 | 11 lines (header + 10 rows) | gzip -t OK | `0252b5ea3b0d81b4852986fa39db7cffce4a9d4e3f9df3b7755ddcfe17bb0c5b` | committed |
| `engine-detect/mainnet/engine-detect-mainnet.jsonl.gz` | 1664 | 15 rows | gzip -t OK; every line parses as JSON | `3b4c12a8b5822e31027b39487966527b577077c7f87337b7bade6e2c15bb9aeb` | committed |
| `engine-detect/mainnet/engine-detect-mainnet.log.gz` | 3237 | 42 lines | gzip -t OK | `2e5b0be20ab416c98de0580d9b16853437f7ccea740646720d315c3a19d5ef0d` | committed |
| `engine-detect/mainnet/engine-detect-mainnet.meta.json` | 1131 | 44 lines, no final newline | parses as JSON | `2d7a3ff416272b9a2dd34c185e5a1194f35653765b802f812fc0a1be539cd594` | committed |
| `prior-summaries.md` | 3267 | 63 lines | prior session text, not data (label added 2026-10-01) | `660c372b956f3afbf08fe4a313580bd2d62e5f70a81b1cc33757c8a69376e233` | committed |
| `scans/arbitrum/scan-arbitrum-config.blocks.csv.gz` | 11838 | 646 lines (header + 645 rows) | gzip -t OK | `85528cae30a6d09318c0ecdfada7ad1f2f97727aa92d57055ca99df067e15e4e` | committed |
| `scans/arbitrum/scan-arbitrum-config.code-provenance.txt` | 4800 | 57 lines | - | `7f8bf54b871eabc7ff41553bd6391f8783e75c08fe706ff6f764d5ed44706074` | committed |
| `scans/arbitrum/scan-arbitrum-config.jsonl.gz` | 7627037 | 132443 rows | gzip -t OK; every line parses as JSON | `f4d7dbaa895c0eb3f414b6b81c43296ec05301342356e28236f4bc4d8dd4c4dd` | committed |
| `scans/arbitrum/scan-arbitrum-config.log.gz` | 28144 | 3882 lines | gzip -t OK | `5198d347af94aa7fb719b49bf8be5b7da25d8d608765d96ccdb800c9a5808d7b` | committed |
| `scans/arbitrum/scan-arbitrum-config.meta.json` | 1236 | 46 lines, no final newline | parses as JSON | `d642fe2e67f86792db73774b675b2294d46c726a457dfa2b910891f2363b4c13` | committed |
| `scans/arbitrum/scan-arbitrum-top.blocks.csv.gz` | 9219 | 496 lines (header + 495 rows) | gzip -t OK | `78ce65c61daf0855f87e4a7897afae463f19817d6b4aa15244d54722bfd47ed5` | committed |
| `scans/arbitrum/scan-arbitrum-top.code-provenance.txt` | 4427 | 51 lines | - | `9c513716b61e5bb19d697ed7264cceab1ca5e1b30ac05fcdb1754fbdfdc2132e` | committed |
| `scans/arbitrum/scan-arbitrum-top.jsonl.gz` | 6711231 | 109075 rows | gzip -t OK; every line parses as JSON | `06214f11f528130687d01600a2ffc14dbb4096604e2118ff1899095ced59064e` | committed |
| `scans/arbitrum/scan-arbitrum-top.log.gz` | 22416 | 2993 lines | gzip -t OK | `d6acfe1f4b5ac51fc1a3e12b038af608c65e51f0b8f553f01576eabf51bc9dad` | committed |
| `scans/arbitrum/scan-arbitrum-top.meta.json` | 1233 | 46 lines, no final newline | parses as JSON | `4117c088cb738d9c9f82116edf86c69efe3e430d18dd8e4b5e8b0b00e90b5d80` | committed |
| `scans/base/scan-base-config.blocks.csv.gz` | 5029 | 249 lines (header + 248 rows) | gzip -t OK | `42181761e07b93704cd74992f1133c414ee7d5fe4d1649971e8d8101f276db26` | committed |
| `scans/base/scan-base-config.code-provenance.txt` | 4800 | 57 lines | - | `13bcd09447f39399b3e18fc389ab13c40077b1ddefbe263ed313d47198a5960e` | committed |
| `scans/base/scan-base-config.jsonl.gz` | 3960257 | 65207 rows | gzip -t OK; every line parses as JSON | `ef157df7f716112f0045748a41fc3d9a5d7c31138f32767c1b39a042a702ea9e` | committed |
| `scans/base/scan-base-config.log.gz` | 15551 | 1499 lines | gzip -t OK | `f3ee625e10227c33c3bf4c7d311cba3377225603366870819b64b3253ce11391` | committed |
| `scans/base/scan-base-config.meta.json` | 1344 | 52 lines, no final newline | parses as JSON | `4951f484c0e4ba20ec3211580ccf51e9b18eedbbb13f6467c9e15d64cba77f1f` | committed |
| `scans/base/scan-base-top.blocks.csv.gz` | 4775 | 210 lines (header + 209 rows) | gzip -t OK | `c6c02e5bef295db11d29106fd0f42cbaa8d1d91e57137b269a3a79e8111b5c25` | committed |
| `scans/base/scan-base-top.code-provenance.txt` | 4427 | 51 lines | - | `9c513716b61e5bb19d697ed7264cceab1ca5e1b30ac05fcdb1754fbdfdc2132e` | committed |
| `scans/base/scan-base-top.jsonl.gz` | 3790930 | 56322 rows | gzip -t OK; every line parses as JSON | `f369b63ed9a83d93f84e059149cc0f2e1c4effbb835aaf5e6eb37495aff6d204` | committed |
| `scans/base/scan-base-top.log.gz` | 11551 | 1271 lines | gzip -t OK | `af40083f60a5579510281b6f7984671abc52a2addbedc99f71eb65c36598a57b` | committed |
| `scans/base/scan-base-top.meta.json` | 1361 | 53 lines, no final newline | parses as JSON | `faa95683c80f0bfce7aaf4b95518e03cba3621c0d47d116a775ff866a0d56f42` | committed |
| `scans/mainnet/scan-mainnet-config.blocks.csv.gz` | 4132 | 152 lines (header + 151 rows) | gzip -t OK | `07566f377dd1d97a6422e03b55f947e49c578ecd4c2423ea3c49b7274af5b92d` | committed |
| `scans/mainnet/scan-mainnet-config.code-provenance.txt` | 4800 | 57 lines | - | `13bcd09447f39399b3e18fc389ab13c40077b1ddefbe263ed313d47198a5960e` | committed |
| `scans/mainnet/scan-mainnet-config.jsonl.gz` | 636074 | 13385 rows | gzip -t OK; every line parses as JSON | `5d8c95a4e31c3a65cafc448d91608716628f88c4cb3781ecbb5562b8d4de3b53` | committed |
| `scans/mainnet/scan-mainnet-config.log.gz` | 11422 | 943 lines | gzip -t OK | `9baf7ef805ec5e2d9a7364f44758c8912402bfd54cc3cc2c797fdd4585cc72a9` | committed |
| `scans/mainnet/scan-mainnet-config.meta.json` | 1170 | 48 lines, no final newline | parses as JSON | `c1449c66918755c0823b98afeed72117300ad8319e658ae33b39c7e4739920e0` | committed |
| `scans/mainnet/scan-mainnet-top.blocks.csv.gz` | 4138 | 152 lines (header + 151 rows) | gzip -t OK | `ea62a7e7b818f56ad89246c34a57c1cc6c4f46e7b842e2754df3ddab732ebbcc` | committed |
| `scans/mainnet/scan-mainnet-top.code-provenance.txt` | 4427 | 51 lines | - | `9c513716b61e5bb19d697ed7264cceab1ca5e1b30ac05fcdb1754fbdfdc2132e` | committed |
| `scans/mainnet/scan-mainnet-top.jsonl.gz` | 1132513 | 18048 rows | gzip -t OK; every line parses as JSON | `a94788b8fd5a68aa031f4f13bf4b275868c9aa156f05d6344a82e5a8599ebe2f` | committed |
| `scans/mainnet/scan-mainnet-top.log.gz` | 10312 | 955 lines | gzip -t OK | `8d92bb6f52287c891546bb2c853a03dffac6dad4a9845833291bfc9b8dbc82e6` | committed |
| `scans/mainnet/scan-mainnet-top.meta.json` | 1168 | 48 lines, no final newline | parses as JSON | `c8f56d98f696e25929ba8c1319a4792fc845f70c6a461c72ab2c087ab199d0a1` | committed |

Byte-identity checks (sha256 of the decompressed stream): each `collect/work/<name>.jsonl` equals the decompressed committed
`<name>.jsonl.gz`, and each `collect/<name>.log` equals the decompressed committed `<name>.log.gz` (all 8 runs). Each
`collect/state/<name>.window.json` equals the `window` object of the committed `<name>.meta.json` written as compact JSON.

How to regenerate the local-only files (run from this folder):
- **[L1]** `collect/work/<name>.jsonl`: `mkdir -p collect/work && gunzip -c scans/<chain>/<name>.jsonl.gz > collect/work/<name>.jsonl`
  for the six scans, and `gunzip -c engine-detect/<chain>/<name>.jsonl.gz > collect/work/<name>.jsonl` for the two engine runs
  (produces byte-identical files). They were written by `collect/run_scan.sh` / `collect/run_engine_detect.sh` during the live runs.
- **[L2]** `collect/state/<name>.window.json`: `python3 -c "import json,sys;print(json.dumps(json.load(open(sys.argv[1]))['window'],separators=(',',':')))" scans/<chain>/<name>.meta.json > collect/state/<name>.window.json`
  (for engine runs use `engine-detect/<chain>/<name>.meta.json`; produces byte-identical files). Originally written by `collect/run_scan.sh` /
  `collect/run_engine_detect.sh`.
- **[L3]** empty marker files written by `collect/run_all.sh`, `collect/run_scan.sh` and `collect/run_engine_detect.sh`:
  `mkdir -p collect/state && touch collect/state/{scan-arbitrum-config,scan-arbitrum-top,scan-base-config,scan-base-top,scan-mainnet-config,scan-mainnet-top,engine-detect-arbitrum,engine-detect-mainnet}.done collect/state/scans-{arbitrum,base,mainnet}.finished collect/state/scans.lock`.
- **[L4]** `collect/state/*.pid`: process ids written at launch by `collect/run_all.sh`, `collect/run_scan.sh` and
  `collect/run_engine_detect.sh`. They identify processes of this collection only; no script reads them after a run, and they cannot be
  regenerated.

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
- **Base scans use a different RPC** (`base.meowrpc.com`) from the §2.1 Base scans (`base-rpc.publicnode.com`). Each run's `syncMs` is
  recorded per block in `blocks.csv`. *Corrected 2026-10-01:* removed a comparative statement about sync time and heads scanned
  relative to the §2.1 scans, which this folder does not contain. (Fixup 2026-10-01: the raw §2.1 scans are in
  `../00-prior-runs/block-scans/`.)
- **Depth filter:** scans use the default `--min-depth-eth 0.2`; the engine runs use 0.1. Pools below these thresholds are not searched
  here. Only their counts are visible, via `pool discovery complete` (found) vs `live pools` (kept).
- **`--universe all` on Arbitrum enumerates one factory** (SushiV2 newest 6,000 of its `allPairsLength`), because chains.ts has no other
  V2-style or Aerodrome-style factory for Arbitrum. On Ethereum it enumerates the newest 6,000 each of UniswapV2, SushiV2 and PancakeV2.
  Older pairs are not enumerated.
- **Concurrent code edits:** another agent modified `bot/src` (opt-in `--v4-pools`) while these runs were set up. See `*.code-provenance.txt`
  and the per-run code list under "Sources and endpoints".
- **Container restart:** the first attempts of the three `top` scans were killed at about 2026-09-30T22:58Z and re-run from scratch
  starting 2026-10-01T01:04:58Z (see Run notes). The `top` scans therefore cover different hours (01:09–01:48Z on 2026-10-01) from the
  `config` scans (22:14–22:49Z on 2026-09-30); exact windows are in the Counts table and each `meta.json`.
- **Stray files outside this directory:** `/scan-base-config.log` and `/scan-eth-config.log` (1 KB each, at the filesystem root) were
  created by a mis-scoped smoke-test command at 21:44Z. They contain only a Node "module not found" error, are not data, and could not be
  deleted by this agent because a safety check blocks removal at `/`. (Still present on 2026-10-01.)
- Failed attempts and unrecoverable steps are appended to `collect/gaps.jsonl`, one JSON object per line: `t`, `step`, `reason`. An empty
  or missing file means none occurred. *Corrected 2026-10-01:* `collect/gaps.jsonl` does not exist. No scan or engine-detect step has a
  `GAP` line in `collect/pipeline.log`. The only `GAP` lines there (22:19:48–22:21:58Z on 2026-09-30) belong to the deliberate
  failure-path self-test `selftest-engine` (`--chain selftestchain`, 3 attempts, each exit 1 before `searcher ready`); the
  `gaps.jsonl` entries and `collect/selftest-engine.attemptN.log` files that test wrote are not present; the attempt-1 log is kept as
  `collect/smoke/selftest-engine-unknown-chain.log`. The killed pre-restart `top` scan attempts were not recorded as gaps (see Run notes).

## Fixup (2026-10-01): manifest corrections only

Made by a fixup agent at ~04:50Z on 2026-10-01. No data file in this folder was changed; nothing was fetched.
- "Method: block-level scans": the statement that the §2.1 scans did not keep their raw output is corrected. The raw §2.1 scans are in
  `../00-prior-runs/block-scans/` (16 files, commit 9c8a37c). A pointer was also added to the "Base scans use a different RPC" item.
- Run notes: the statement that `collect/manifest_waiter.sh` was still running until about 09:05Z is corrected. It was stopped at
  2026-10-01T02:56:31Z (last line of `collect/manifest_waiter.log`). `ps` at ~04:50Z showed no `manifest_waiter` or `fill_manifest`
  process.
- Verified inventory: the `collect/manifest_waiter.log` row now gives the final file (4,833 bytes, 32 lines, sha256
  `889732ab52ac714b82aec2fe1b656f74a124542d6f5e69cbef879a0e1bac59a7`, equal to the committed version; `git status` clean). The old
  values are kept in the row.
- `prior-summaries.md` is labelled "prior session text, not data" in the intro, the question-line table, the layout and the
  inventory. Its sha256 is unchanged (`660c372b…`).
