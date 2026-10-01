# 04-shallow-pools — MANIFEST

**Status: COMPLETE** (finalized 2026-10-01). All three collectors of this directory have `.DONE` sentinels
(SHALLOW_LIVE, SHALLOW_SNAPSHOT, TRANSFER_PROBE), and every file listed in "Verified inventory (2026-10-01)" passed the checks
described there. The design limits of each collection are listed under "Coverage limits and gaps" and at the end of the
transfer-probe section.

*Provenance of this file:* first written 2026-09-30 ~22:06 UTC with status IN PROGRESS while the live run and the snapshot were
still running (counts marked `TBD`). The transfer-behaviour probe was then recorded as not collected (attempts 1 and 2), and was
collected in attempt 3 on 2026-10-01 02:12-02:19 UTC (section at the end of this file). *Corrections 2026-10-01 (documentation
pass):* status line, the `TBD` counts and times (filled in from the files, `run-times.json` and `snapshot-meta.json`), and the
statements that said the transfer probe was not collected or that `.sentinels/TRANSFER_PROBE.FAILED` exists; each correction is
marked "[corrected 2026-10-01]" in place.

This directory has raw material only. It contains no analysis, rankings or conclusions.

| Collector | Sentinel | Status at writing (2026-09-30 ~22:06Z) | Final status (2026-10-01) |
|---|---|---|---|
| Live engine run, shallow pools (step 3) | `.sentinels/SHALLOW_LIVE.DONE` / `.FAILED` | running (ready 22:03:50Z, scheduled stop ~22:23:51Z) | DONE |
| Pinned-block universe snapshot (step 1) | `.sentinels/SHALLOW_SNAPSHOT.DONE` / `.FAILED` | running (pinned block 52008246) | DONE |
| Transfer-behaviour probe (step 2) | `.sentinels/TRANSFER_PROBE.DONE` [corrected 2026-10-01; was `TRANSFER_PROBE.FAILED` after attempts 1-2] | not collected (attempts 1 and 2) | DONE (attempt 3, directory `transfer-probe/`) |

`.sentinels/` is git-ignored, so the sentinel contents are quoted here verbatim (as of 2026-10-01):

| Sentinel file | Content |
|---|---|
| `SHALLOW_LIVE.DONE` | `ok` / `2026-09-30T22:23:51.826Z` |
| `SHALLOW_SNAPSHOT.DONE` | `ok pinned_block=52008246 chunk_throws_after_retries=0` / `2026-09-30T22:49:30.464Z` |
| `TRANSFER_PROBE.DONE` | `done 2026-10-01T02:19:45Z: transfer-probe.csv.gz 67,194 rows (ok 59,406, no_holder 7,788), block 52008246, 3,714 eth_calls, 0 rpc errors` |

## Question lines served (mapping only)

Question line numbers refer to the numbered QUESTION LINES given to the collectors (1 = "Uniswap V4 on Base…", 2 = "Older V2
pairs…", 3 = "Pools under 0.1 ETH of liquidity…", 8 = "So the search went far beyond selected pairs…").

| Question line | File(s) in this directory |
|---|---|
| 1 | `geckoterminal-responses.jsonl.gz`; rows with `is_v4=true` in `pools-prefilter.csv.gz` and `pools-pruned-empty.csv.gz`; rows with non-empty `v4_pool_id` in `cl-ticks-prefilter.csv.gz`; `v4-poolmanager-balances.csv.gz`; `uniswap v4 candidates` / `uniswap v4 pools discovered` lines in `live-shallow.log` and `collect/snapshot.log`; `snapshot-meta.json` (`stages.v4`) |
| 2 | `factory-enumeration.csv.gz`; `factory enumerated` lines in `collect/snapshot.log` (and in `live-shallow.log`); `snapshot-meta.json` (`fn_stats.allPairs`, `stages.enumerate`); UniswapV2 rows in `pools-prefilter.csv.gz` and `pools-pruned-empty.csv.gz` |
| 3 | `live-shallow.jsonl`, `live-shallow.log`, `run-times.json`; `pools-prefilter.csv.gz`, `pools-pruned-empty.csv.gz`, `cl-ticks-prefilter.csv.gz`, `prices.csv.gz`, `tokens.csv.gz`, `snapshot-meta.json`; `transfer-probe/transfer-probe.csv.gz`, `transfer-probe/holders.csv.gz`, `transfer-probe/probe-batches-raw.jsonl.gz`, `transfer-probe/probe-meta.json` |
| 8 | `live-shallow.jsonl`, `live-shallow.log`, `run-times.json`; `pools-prefilter.csv.gz`, `pools-pruned-empty.csv.gz`, `factory-enumeration.csv.gz`, `tokens.csv.gz`, `snapshot-meta.json` |

## Verified inventory (2026-10-01)

Checks run 2026-10-01 by streaming every file (no file loaded fully into memory): `gzip -t` on every `.gz` file (all 17 OK);
CSV files parsed with a CSV reader (rows = data records excluding the header; every record has the header's column count);
every line of every `.jsonl` / `.jsonl.gz` file parsed as JSON (0 failures); every `.json` file parsed (OK); every line of
`live-shallow.log` and `collect/snapshot.log` parsed as JSON (OK). Largest committed file: 5,086,835 bytes; no committed file
exceeds 90 MB. Row counts agree with `snapshot-meta.json` `files`, `run-times.json` `blocks.jsonl_candidate_rows` (42) and
`probe-meta.json` (`batches` 3,714, `rows` 67,194); the sha256 values of `transfer-probe/transfer-probe.csv.gz` and
`transfer-probe/holders.csv.gz` equal `probe-meta.json` `output_sha256` and `holders_file_sha256`; `sha256` of the bytes encoded
by `transfer-probe/collect/probe-runtime.hex` equals `probe-meta.json` `probe_runtime_sha256`, and the hex string equals
`deployedBytecode.object` in `transfer-probe/collect/out/TransferProbe.sol/TransferProbe.json`.

Paths are relative to this directory. "Rows" = CSV data records (header excluded); "lines" = text lines (for JSONL, one record
per line). "local-only" = git-ignored, not in the repository.

| File | Bytes | Rows / lines | sha256 | Repository |
|---|---:|---|---|---|
| `MANIFEST.md` | (this file) | – | – | committed |
| `cl-ticks-prefilter.csv.gz` | 1,353,843 | 96,659 rows | `d03ae996644ea62b2db14696049a91534b28ba65b3d9b2258f2dbe011dc200a1` | committed |
| `enumerated-token-meta-calls.csv.gz` | 943,008 | 33,621 rows | `8220343c355714dee7dc979a880675aa9e455a041dc3c59b6e393993cdb38d53` | committed |
| `factory-enumeration.csv.gz` | 1,951,362 | 38,737 rows | `d36cf527165de2ca01ae0cce90d5189818bad612c427a6b3f7c5e6876ed2b85e` | committed |
| `geckoterminal-responses.jsonl.gz` | 76,626 | 16 lines | `68e2fd6418c77747cb83c2bde8c342b2fe587d072699d7f29104c78300e3a3ca` | committed |
| `live-shallow.jsonl` | 16,865 | 42 lines | `8226317546e2238046970b6d07d401cdcff722ca544dc7f8a1892421ce53862f` | committed |
| `live-shallow.log` | 41,363 | 114 lines | `5243c104a678a644ade05e9579b3b037e4c9d5f0150aeac8f3cefd721abb4a7e` | committed |
| `pools-prefilter.csv.gz` | 3,159,400 | 35,734 rows | `0633b190bfc9b2379d9e987140e59d35bd79663dff64a5972dddbeff2238c9c9` | committed |
| `pools-pruned-empty.csv.gz` | 758,897 | 10,409 rows | `21ee8ebeff1730edfe0008e2664dc16c62bac0123d6d1c90c645ad88de58cf91` | committed |
| `prices.csv.gz` | 67,745 | 1,732 rows | `dd4c3f6b6adb591d31e00165894f9372df546ba6b81cfdc7f6187a6ebe9f8515` | committed |
| `run-times.json` | 3,329 | 90 lines | `e6f49e5c9b830a6ad4c9c367f2dd0b60d50238da8cdd6814c7d0323914859138` | committed |
| `snapshot-failed-calls.jsonl.gz` | 1,071 | 54 lines | `a58a2e193484c1e96ab6411d798b62ae51e774f4c3dc8d0f46dd81c20ff35c83` | committed |
| `snapshot-meta.json` | 4,372 | 257 lines | `467723852ec0d49cfd34945e6e2eeebee338005f32c02f07f52441f762939e22` | committed |
| `snapshot-rpc-errors.jsonl.gz` | 20 | 0 lines (empty gzip stream) | `f61f27bd17de546264aa58f40f3aafaac7021e0ef69c17f6b1b4cd7664a037ec` | committed |
| `tokens.csv.gz` | 1,212,031 | 33,597 rows (33,619 physical lines incl. header: 3 quoted `name` values contain line breaks) | `9118d43215ad4a08790c39d00d1fa5ece5355dfb230d3fc731b7ede0b5c304fc` | committed |
| `v4-poolmanager-balances.csv.gz` | 338 | 8 rows | `f2f8545b5169b325c2173bb9ccd4f2e99ae5914130cdfa70322ae18f8e17a3d7` | committed |
| `collect/run_live_shallow.log` | 402 | 3 lines | `1446ab7c5be054a05f098c91d326186fd1f555f3441b84eb0c7b7042e7708344` | committed |
| `collect/run_live_shallow.py` | 11,994 | 286 lines | `ee87c0ebfb2aa61de0bac68783db3b5e6b448806af62a5a3727aae8f8cbcfe18` | committed |
| `collect/run_live_shallow.state.json` | 3,329 | 90 lines (byte-identical to `run-times.json`) | `e6f49e5c9b830a6ad4c9c367f2dd0b60d50238da8cdd6814c7d0323914859138` | committed |
| `collect/run_snapshot.log` | 42 | 1 line | `f08b83cfa328638f320aeec459a0df932b801863e7dbc81fd2562af50093843c` | committed |
| `collect/run_snapshot.sh` | 917 | 12 lines | `94cbc4c6c8eefda94afa6a51795bacf1e7fa009d68842e99d5c70871f5faab14` | committed |
| `collect/snapshot.log` | 2,602 | 19 lines | `1c3c0dcfc6f5e5611f3accf39b95da5a69f5af4d30c56ae1f7a99b341cd99b5b` | committed |
| `collect/snapshot.ts` | 24,972 | 441 lines | `bc721d79382721c91e7da99d0a344386aab71ae998c82edd1396448b8114aa78` | committed |
| `transfer-probe/transfer-probe.csv.gz` | 3,430,493 | 67,194 rows | `da46ce84a09b7bdf4bf7c6b79b22284aea6de9b9c505251d4ce8d5618068b4c2` | committed |
| `transfer-probe/holders.csv.gz` | 2,035,343 | 33,597 rows | `bba284fe6b20d724fcc07d3bfd131036cd25700246b9bdacaf32a42fff890505` | committed |
| `transfer-probe/probe-batches-raw.jsonl.gz` | 5,086,835 | 3,714 lines | `a8fe5c033b4e0c0686a30e2b5936fc9959e11f44d395e9e54c0f7ab36d624741` | committed |
| `transfer-probe/probe-meta.json` | 1,231 | 29 lines | `34ecbfc30838033725c414a7e35d8f24369c36597190f67089df6efec4d49fec` | committed |
| `transfer-probe/collect/build_table.py` | 4,768 | 65 lines | `5f5659a1c3e877c51735436d3aefa2de8784d9edb0183130068ab16d56f21380` | committed |
| `transfer-probe/collect/foundry.toml` | 127 | 7 lines | `846def216e7b459a997e01ee3b87f71b7d75d7ebc1e8db7152018e6959abe573` | committed |
| `transfer-probe/collect/probe-batches-smoke.jsonl.gz` | 5,494 | 4 lines | `4e7e9f403abf3508f36e292b2262b193e9f8dbcd8af79dd7825e629999cacd81` | committed |
| `transfer-probe/collect/probe-runtime.hex` | 3,998 | 1 line (no trailing newline) | `30d3a8e5a78f810aede65abb2ea11ef48e78f3f28d2873966f01670d1e3de905` | committed |
| `transfer-probe/collect/run_probe.log` | 3,859 | 76 lines | `b9a8b5d013c4e8ede6bcb47d9391b5e95a4a8128df6c4266f08ed7f2d1faffbb` | committed |
| `transfer-probe/collect/run_probe.py` | 5,616 | 112 lines | `c685323510f4c667530e9bb665fb2ca81716928a7e267eec40a5a2c412ed8f59` | committed |
| `transfer-probe/collect/select_holders.py` | 3,949 | 80 lines | `d121b51314d3dc0917d309ba43995866262d76f8f82d7511b5d7e233395186bc` | committed |
| `transfer-probe/collect/src/TransferProbe.sol` | 2,535 | 61 lines | `d96749b179e39184b666ef9af79389921b6c16759a8d123fc18a07f793b9c40c` | committed |
| `transfer-probe/collect/cache/solidity-files-cache.json` | 1,176 | 1 line | `063c762cd338c7c5264083ecaf3437fb59a8174973d9a10ef039cd0d4ea8d5cc` | committed (forge build cache) |
| `transfer-probe/collect/out/build-info/032bef9159f93409.json` | 97 | 1 line | `994be102549611ba4c84f4c1b5d9ec6ec68695234a38490e9734102c1999c2ab` | committed (forge build output) |
| `transfer-probe/collect/out/TransferProbe.sol/TransferProbe.json` | 21,201 | 1 line | `a48864d2ad2776957b4d1b20f59568c174bb006ddbe23f760bdaa5f44b893691` | committed (forge build output) |
| `transfer-probe/collect/work/holders.csv.gz` | 2,035,343 | 33,597 rows | `bba284fe6b20d724fcc07d3bfd131036cd25700246b9bdacaf32a42fff890505` | local-only (`collect/work/`) |
| `transfer-probe/collect/work/probe-batches.jsonl` | 60,373,414 | 3,714 lines | `40914c7d44c81190b2071823d85ba9ddc27a3c8f571233b531d865b61ca43a6f` | local-only (`collect/work/`) |
| `transfer-probe/collect/work/probe-batches.jsonl.gz` | 5,086,835 | 3,714 lines | `a8fe5c033b4e0c0686a30e2b5936fc9959e11f44d395e9e54c0f7ab36d624741` | local-only (`collect/work/`) |
| `transfer-probe/collect/work/probe-batches-smoke.jsonl` | 64,772 | 4 lines | `2e4a492c1cdd6a46eef02c62efe413f1660a889a7309b3ead8ff30d015ddd460` | local-only (`collect/work/`) |
| `transfer-probe/collect/__pycache__/run_probe.cpython-311.pyc` | 14,396 | – (Python bytecode) | `9c6828a14e4e2f24ade8531aaa750d81b99bc50117e7e9894c3d7d65e1ff6fff` | local-only (`__pycache__/` rule in `.gitignore`) |

### Local-only files: how to regenerate

All local-only files are working copies of committed files or by-products of the committed scripts. Commands run from
`research-material/04-shallow-pools/transfer-probe/collect/`:

| Local-only file | Committed equivalent (verified 2026-10-01) | Regenerate |
|---|---|---|
| `work/holders.csv.gz` | byte-identical to `../holders.csv.gz` | `mkdir -p work && cp ../holders.csv.gz work/holders.csv.gz`; or rebuild from the committed snapshot files with `python3 select_holders.py` (offline, no RPC; gzip bytes can differ because the gzip header stores a timestamp) |
| `work/probe-batches.jsonl` | decompressed content of `../probe-batches-raw.jsonl.gz` has the same sha256 | `gunzip -c ../probe-batches-raw.jsonl.gz > work/probe-batches.jsonl`; or re-query with `python3 run_probe.py --batch 16 --workers 3` (eth_call at block 52008246 on an endpoint serving historical state) |
| `work/probe-batches.jsonl.gz` | byte-identical to `../probe-batches-raw.jsonl.gz` | `cp ../probe-batches-raw.jsonl.gz work/probe-batches.jsonl.gz` |
| `work/probe-batches-smoke.jsonl` | decompressed content of `probe-batches-smoke.jsonl.gz` has the same sha256 | `gunzip -c probe-batches-smoke.jsonl.gz > work/probe-batches-smoke.jsonl`; or `python3 run_probe.py --smoke` |
| `__pycache__/run_probe.cpython-311.pyc` | none (bytecode cache) | created automatically by Python 3.11 when `build_table.py` imports `run_probe`; not needed to use the data |

`run_probe.py` reads `work/holders.csv.gz` and appends to `work/probe-batches*.jsonl`; `build_table.py` reads
`work/holders.csv.gz` and `work/probe-batches.jsonl`. Restore those two `work/` files (commands above) before running either
script from a fresh checkout.

## Sources and endpoints

- Base mainnet (chain id 8453) JSON-RPC via the engine's own client (`bot/src/util/client.ts` `makeHttpClient`):
  viem `fallback([base-rpc.publicnode.com, base.drpc.org, base-mainnet.public.blastapi.io, mainnet.base.org], rank=false)`.
  The live engine also uses `wss://base-rpc.publicnode.com` for newHeads.
- GeckoTerminal API v2 (`api.geckoterminal.com/api/v2/networks/base/...`) via `bot/src/research/tokens.ts` `fetchTopPools(cfg, 2)`
  (network top pages 1-2 plus page 1 of each DEX listing in `GT_DEXES`), which `discoverV4Pools` uses for the V4 candidates.
- Contracts: DEX factories/tiers from `bot/src/config/chains.ts` (BASE), V4 PoolManager `0x498581ff718922c3f8e6a244956af099b2652b2b`,
  StateView `0xa3c0c9b65bad0b08107aa264b0f3db444b867a71`, PositionManager `0x7c5f5a4bbd8fd63184577525326123b519429bdc`,
  Multicall3 `0xca11bde05977b3631167028862be2a173976ca11`.
- Transfer probe (step 2): `https://base-mainnet.public.blastapi.io` only (see the transfer-probe section).

## Reproduce

No foundry tools are needed for steps 1 and 3 [corrected 2026-10-01: the transfer probe (step 2, `transfer-probe/`) compiles its
probe contract with forge; see its section]. Engine code under bot/src is unmodified.

```bash
# Step 3: live run (detached; waits for 'searcher ready', runs 1200 s more, stops by process group SIGINT->SIGTERM->SIGKILL)
cd /home/user/dapparb/research-material/04-shallow-pools/collect && setsid nohup python3 -u run_live_shallow.py > run_live_shallow.log 2>&1 < /dev/null &
#   the engine command it runs:
#   cd /home/user/dapparb/bot && LOG_JSON=1 npx tsx src/main.ts --chain base --mode dry --source logs --universe all \
#     --max-per-factory 6000 --min-depth-eth 0.001 --min-profit-usd 0.01 --top 6 \
#     --out /home/user/dapparb/research-material/04-shallow-pools/live-shallow.jsonl  > live-shallow.log 2>&1
#   (LOG_JSON=1 only switches pino output from pino-pretty to one JSON object per line; engine behaviour is unchanged.)
#   Not resumable: a live window cannot be replayed. The launcher exits immediately if run-times.json has status DONE.

# Step 1: snapshot (detached)
cd /home/user/dapparb/research-material/04-shallow-pools/collect && setsid nohup ./run_snapshot.sh > run_snapshot.log 2>&1 < /dev/null &
#   which runs: cd /home/user/dapparb/bot && LOG_JSON=1 npx tsx ../research-material/04-shallow-pools/collect/snapshot.ts > collect/snapshot.log
#   Re-run at the same block: ./run_snapshot.sh --pin 52008246   (needs an endpoint that serves eth_call at that block;
#   publicnode only serves recent blocks, drpc/blastapi serve archive eth_call)
#   Smoke test used before the full run: --max-per-factory 25 --sentinel none --out <scratch dir>

# Step 2: transfer probe -- commands in the section "Transfer-behaviour probe (attempt 3 ...)" at the end of this file.
```

## Time window, blocks, pinned snapshot

| Item | Value |
|---|---|
| Live run launch | 2026-09-30T21:53:55.034Z (engine pid 4747, launcher pid 4722) [corrected 2026-10-01: 21:53:55.034Z is the `launched` line of `collect/run_live_shallow.log`; `run-times.json` `launch_utc` = 21:53:54.620Z (taken just before the process was started); `run-times.json` `engine_pid` = 4723 is the process started by the launcher, 4747 is the pid written in the engine's log lines] |
| Live run 'searcher ready' | 2026-09-30T22:03:50.413Z (log `time` 1790805830413); detected by launcher 22:03:51.69Z |
| Live run stop | SIGINT sent 2026-09-30T22:23:51.758Z (`run-times.json` `stop_utc`, 1200.5 s after detection); engine exit 22:23:51.823Z [filled in 2026-10-01] |
| Live run heads read by the launcher | launch 52007943, ready 52008242, stop 52008842 (`eth_blockNumber` on publicnode) [filled in 2026-10-01] |
| Live run first/last processed block | `run-times.json` → `blocks` [filled in 2026-10-01]: block field of log records 52008242-52008835; heartbeat blocks 52008269-52008835 (54 heartbeats); `live-shallow.jsonl` rows 52008242-52008815 |
| Snapshot pinned block | **52008246** (head 52008249 at 22:04:05Z minus 3); block timestamp 1790805839 = 2026-09-30T22:03:59Z, hash `0x0876ef696f85aa9adc5dbd4766aec2da9b5b695e4115471c79e0666b14934afd` (`snapshot-meta.json`) |
| Snapshot wall-clock | started 2026-09-30T22:04:05Z; finished 2026-09-30T22:49:30.463Z (`snapshot-meta.json` `finished_utc`; head at end 52009611) [filled in 2026-10-01] |
| Transfer probe | eth_calls at block 52008246, sent 2026-10-01 02:12-02:19 UTC (see its section) |

The live run's universe was built from its own reads at `latest` during 21:53:55–22:03:50Z (roughly blocks 52007950–52008240;
first ready-time block visible in the log is 52008242). The snapshot is a separate, later pass at one pinned block,
so the two pool sets are not identical.

### `searcher ready` line (live run, verbatim)

```
{"level":30,"time":1790805830413,"pid":4747,"hostname":"vm","tokens":33595,"pools":5234,"cycles":6422,"minDepthEth":0.001,"source":"logs","mode":"dry","contract":"0x00000000000000000000000000000000000a4BB0","codeOverride":true,"msg":"searcher ready"}
```

## Files and schemas

Hex is lowercase `0x…` in snapshot files. The engine's own outputs (`live-shallow.*`) keep the engine's checksummed
addresses. Big integers are base-10 strings. "derived" = computed deterministically from raw columns or by engine functions.

### Live run (step 3)

Engine and flags: as the `docs/ANALYSIS.md` §2.6 Base run (raw files of that run are in `../02-v4-live-test/prior/`), except
`--min-depth-eth 0.001` (the §2.6 run used 0.1). Full command under Reproduce.

**`live-shallow.jsonl`** — as written by the engine (`bot/src/main.ts`), one JSON object per candidate the engine acted on
(top 6 per tick after the `--min-profit-usd 0.01` predicted-net filter, one per pool per tick). Plain JSONL (not gzipped) so that
`bot/src/research/analyze.ts` can read it directly. Rows: 42 [filled in 2026-10-01].

| Field | Meaning |
|---|---|
| `t` | ISO UTC wall-clock time of the record |
| `block` | block number that triggered the tick |
| `fb` | flashblock index (always 0 with `--source logs`) |
| `route` | engine's route label `TOKENIN>TOKENOUT@DEX[/tier] ...` |
| `pools` | pool addresses per hop (V4: first 20 bytes of the poolId) |
| `token` | symbol of the start/profit token |
| `amountIn` | input amount, token units (decimal string) |
| `predictedProfitUsd`, `gasUsd`, `netUsd` | engine's off-chain prediction (USD via engine price map; gas = estimate × gas price + L1 fee) |
| `gapBps` | engine's price-gap measure for the route |
| `sim` | `eth_call` simulation of the executor with code override: `{profitUsd, gas, ms}` on success or `{error, ms}` on revert |
| `simNetUsd` | simulated profit minus gas at simulated gasUsed (present when `sim` succeeded) |
| `blacklisted` | true when the route/token was parked after 3 reverts (key present only on such rows) |

**`live-shallow.log`** — engine stdout/stderr, pino JSON lines (`time` = epoch ms, `msg` = message). Messages include
`factory enumerated`, `pool discovery complete`, `geckoterminal request failed`, `uniswap v4 pools discovered`, `searcher ready`,
`heartbeat` (every 10 ticks: `ticks, gross, net, simulated, simOk, …, block, syncMs, searchMs, totalMs, pools`), the per-candidate
records (same fields as the JSONL), `shutting down` (final stats on SIGINT). Lines: 114 [filled in 2026-10-01].

**`run-times.json`** — written by `collect/run_live_shallow.py` at the end: `status` (DONE/FAILED), `reason`, `launch_utc`, `ready_utc`
(from the log line's `time`), `stop_utc` (time the SIGINT was sent), `attempts[]` (per attempt: `min_depth_eth`, `cmd`, `engine_pid`,
`head_at_launch`/`head_at_ready`/`head_at_stop` = eth_blockNumber read by the launcher, `ready_detected_utc`, `searcher_ready_line_verbatim`,
`searcher_ready_counts`, `stop_signals`, `exit_code`, `seconds_ready_to_stop`, `log_tail` on failure), `retry_reason` if the 0.01 retry
was used, `blocks` (`first/last_heartbeat_block`, `first/last_block_in_log_records`, `first/last_block_in_jsonl`, `jsonl_candidate_rows`,
`heartbeat_count`), `shutdown_stats_line` (the engine's final `shutting down` object). [2026-10-01: the file has `status` DONE and one
attempt (`min_depth_eth` 0.001); no `reason` or `retry_reason` key is present.]

`collect/run_live_shallow.state.json` is the launcher's checkpoint (same structure, updated during the run; its final content is
byte-identical to `run-times.json`).

### Snapshot (step 1)

Sequence reproduced with the engine modules imported unchanged (`collect/snapshot.ts`), in main.ts order:
`enumerateUniverse(maxPerFactory 6000)` → tokens = cfg.tokens ∪ enumerated tokens → `discoverV4Pools(tokens, pages=2)` →
`loadStaticMetadata` → `syncPools(force, blockNumber=PIN)` → `pruneEmpty` → `buildEthPrices(kept)` → `poolDepthEth` /
`filterByDepth(kept, prices, 0.1)`.
**Pinning:** the script wraps the engine's own viem client in a Proxy that adds `blockNumber = PIN` to every `multicall` and
`readContract` that does not name a block (the engine's enumerate/discover/static-metadata reads default to `latest`), and returns PIN from
`getBlockNumber`. All on-chain reads of the sequence are therefore at block 52008246. The same Proxy retries transient RPC errors
(HTTP 429/5xx, timeouts, rate-limit messages) up to 7 attempts with exponential backoff (2 s → 60 s) before the engine's own
chunk bisection sees the error, and records every per-call failure. `globalThis.fetch` is wrapped only to keep the raw GeckoTerminal
responses. GeckoTerminal data is live at request time (not pinnable).

Extra reads not in the engine sequence (all at PIN): `balanceOf(pool)` for each non-V4 pool's two tokens; `balanceOf(PoolManager)` for
each V4 currency and `eth_getBalance(PoolManager)`; `name()` and `totalSupply()` for every token; a re-read of `getReserves` /
`slot0`+`liquidity` (V4: StateView `getSlot0`+`getLiquidity`) for every pruned pool.

**`pools-prefilter.csv.gz`** — every pool after `pruneEmpty` (the set the depth filter sees). One row per pool. Rows: 35,734 [filled in 2026-10-01].
**`pools-pruned-empty.csv.gz`** — every pool removed by `pruneEmpty`; same columns plus `recheck_*`. Rows: 10,409 [filled in 2026-10-01].

| Column | Meaning |
|---|---|
| `pool_address` | pool address; for V4 the engine's synthetic address = first 20 bytes of the poolId |
| `v4_pool_id` | V4 poolId (bytes32), empty otherwise |
| `dex` | engine DEX name (UniswapV3, AerodromeCL, AerodromeCL2, AerodromeCL3, PancakeV3, SushiV3, Aerodrome, UniswapV2, SushiV2, PancakeV2, BaseSwap, UniswapV4) |
| `kind` | engine kind: univ2, aero-v2, univ3, aero-cl, pancake-v3 (V4 pools are `univ3` in the engine) |
| `is_v4` | true/false |
| `token0`, `token1` | engine token addresses (V4 native ETH is mapped by the engine to WETH) |
| `sym0`, `sym1`, `dec0`, `dec1` | engine symbol (sliced to 12 chars by enumerate.ts) and decimals |
| `v4_currency0`, `v4_currency1`, `v4_fee_raw`, `v4_tick_spacing`, `v4_hooks` | raw V4 PoolKey from PositionManager.poolKeys (currency 0x000…0 = native ETH; fee 8388608 = dynamic-fee flag) |
| `v2_fee_bps` | V2-style fee: univ2 from chains.ts `feeBps`; aero-v2 from factory `getFee(pool, stable)` (Aerodrome units as the engine stores them) |
| `aero_stable` | aero-v2 stable flag (false for univ2) |
| `reserve0`, `reserve1` | V2 `getReserves` at PIN, raw token units |
| `cl_tier` | CL factory key: fee (univ3/pancake/V4) or tickSpacing (aero-cl) |
| `sqrt_price_x96`, `tick`, `liquidity` | CL slot0 / in-range liquidity at PIN (V4 via StateView) |
| `fee_pips` | CL fee in 1e-6 units as the engine holds it (aero-cl: `fee()` at PIN; V4: lpFee from getSlot0) |
| `tick_spacing` | CL tick spacing |
| `fee_by_dir_zero_for_one`, `fee_by_dir_one_for_zero` | V4 only: engine's effective fee per direction including protocol fee (pips) |
| `cl_word_range_min/max`, `cl_bitmap_words_fetched`, `cl_initialized_ticks_fetched` | tick-bitmap word window fetched by `syncPools(force)` (±3000 ticks + 1 word) and number of initialized ticks found in it |
| `state_block` | engine `pool.block` after sync (PIN when any state call succeeded, 0 otherwise) |
| `token0_balance_of_pool`, `token1_balance_of_pool`, `token*_balance_ok` | extra read: ERC-20 `balanceOf(pool)` at PIN (empty for V4) |
| `engine_price_eth_token0_derived`, `engine_price_eth_token1_derived` | derived: `buildEthPrices` value (ETH per whole token); empty = unpriced |
| `side_amt0_derived`, `side_amt1_derived` | derived: engine `sideAmounts` (human units; V2 real reserves, CL virtual reserves L/√P and L·√P) |
| `engine_depth_eth_derived` | derived: engine `poolDepthEth` |
| `passes_min_depth_0_1_derived` | derived: membership in engine `filterByDepth(kept, prices, 0.1)` (empty in the pruned file) |
| `recheck_reserves_ok`, `recheck_reserve0/1`, `recheck_slot0_ok`, `recheck_sqrt_price_x96`, `recheck_tick`, `recheck_liquidity_ok`, `recheck_liquidity` | pruned file only: independent re-read at PIN |

**`cl-ticks-prefilter.csv.gz`** — tick data exactly as fetched by `syncPools(force)` for CL pools in the prefilter set.
Columns: `pool_address`, `v4_pool_id`, `tick`, `liquidity_net` (signed, raw), `liquidity_gross` (raw). Rows: 96,659 [filled in 2026-10-01].

**`prices.csv.gz`** — full engine price map. Columns: `token`, `symbol`, `decimals`, `engine_price_eth_derived` (ETH per whole token,
from `buildEthPrices` over the prefilter pools; anchor rule `MIN_ANCHOR_ETH` = 0.05), `is_weth`, `is_usdc`. Rows: 1,732 [filled in 2026-10-01].

**`tokens.csv.gz`** — every token in the engine token list or in any snapshot pool. Columns: `token`, `symbol_engine`,
`decimals_engine`, `in_cfg_tokens`, `in_enumerated_tokens`, `name`, `name_ok`, `total_supply` (raw), `total_supply_ok`,
`n_prefilter_pools_derived`, `n_pruned_pools_derived`, `engine_price_eth_derived`. Rows: 33,597 [filled in 2026-10-01; 3 `name`
values contain line breaks inside quoted fields, so read it with a CSV parser, not line by line].

**`enumerated-token-meta-calls.csv.gz`** — raw `decimals()`/`symbol()` results that `enumerateUniverse` requested for tokens of
factory-enumerated pools (tokens with `decimals_ok=false` are dropped by the engine). Columns: `token`, `decimals_ok`, `decimals`,
`symbol_ok`, `symbol`. Rows: 33,621 [filled in 2026-10-01].

**`factory-enumeration.csv.gz`** — raw factory enumeration (`allPools(i)` / `allPairs(i)` for the newest `min(length, 6000)` indices of
each enumerable factory) with the `token0()`/`token1()` results. Columns: `factory`, `dex`, `index`, `pool_address`, `call_ok`, `token0`,
`token1`, `token0_ok`, `token1_ok`, `in_discovered_pools_derived` (the address is among the pools `discoverPools` found by resolving every
venue per pair). Factory lengths at PIN are in `collect/snapshot.log` (`factory enumerated` lines: `total`, `enumerated`). Rows: 38,737 [filled in 2026-10-01].

**`v4-poolmanager-balances.csv.gz`** — extra read: `balanceOf(PoolManager)` at PIN for each V4 currency in the snapshot, plus a row for
token `0x000…0` = PoolManager native ETH balance (`eth_getBalance`). Columns: `holder`, `token`, `balance`, `balance_ok`. Rows: 8.

**`geckoterminal-responses.jsonl.gz`** — every GeckoTerminal request made during the snapshot: `{t, url, status, body}` (body = raw JSON text;
`status` null + `error` on network failure). The engine retries a 429 once after 15 s and then skips that page. Lines: 16
(`snapshot-meta.json` `stages.v4`: `gt_requests` 16, `gt_non200` 2).

**`snapshot-failed-calls.jsonl.gz`** — every individual multicall sub-call with status failure: `{stage, fn, address, args, err}`. Lines: 54.
**`snapshot-rpc-errors.jsonl.gz`** — every RPC-level error seen by the retry wrapper: `{t, stage, what, attempt, err}`. Lines: 0 (valid empty gzip).

**`snapshot-meta.json`** — pinned block (number, timestamp, hash), head at start/end, per-stage timings and counts, `syncStats`,
`fn_stats` (calls/ok/fail per function name), `chunk_throws_after_retries`, `chunk_throws_by_stage`, `failed_calls_by_stage`, file list
with row counts and byte sizes.

### Collector code and logs (`collect/`)

`run_live_shallow.py` (launcher), `run_live_shallow.log`, `run_live_shallow.state.json`; `snapshot.ts`, `run_snapshot.sh`,
`run_snapshot.log`, `snapshot.log` (script progress lines + engine pino JSON lines).

## Coverage limits and gaps

1. **Transfer-behaviour probe (step 2)** [corrected 2026-10-01]: originally recorded here as "not collected. No per-token transfer
   simulation data exists here; `.sentinels/TRANSFER_PROBE.FAILED` records this." That was the state after attempts 1 and 2
   (section "Transfer-behaviour probe (attempt 2, 2026-10-01)"). Attempt 3 collected it (section "Transfer-behaviour probe
   (attempt 3, …)" at the end of this file; sentinel `TRANSFER_PROBE.DONE`; data in `transfer-probe/`); its own coverage limits are
   listed at the end of that section. Separately, the engine's own simulation outcome per candidate (`sim.error` in
   `live-shallow.jsonl`, e.g. decoded `TransferFailed` reverts) is recorded only for routes the engine selected.
2. **V4 coverage is the engine's GeckoTerminal-listed set only** (network top pages 1-2 + page 1 per DEX listing; hooked pools with
   swap-permission bits or dynamic fee and pools outside the token universe are dropped by `discoverV4Pools`). The live run's log shows
   `listed 20, kept 10, hooked 2, outOfUniverse 8`; the snapshot's counts are in `collect/snapshot.log` (`listed 20, kept 9, hooked 2,
   outOfUniverse 9` [filled in 2026-10-01]). The full V4 pool list is in `../01-v4-pools`.
3. **Newest 6,000 per V2-style factory** (`--max-per-factory 6000`): e.g. UniswapV2 `allPairsLength` 3,063,708 at the snapshot's block, of
   which indices 3,057,708-3,063,707 were enumerated; Aerodrome V2 6,000 of 29,601; PancakeV2 6,000 of 15,243; BaseSwap 6,000 of 8,258;
   SushiV2 6,000 of 6,095. Slipstream factories were enumerated in full. V3-style pools (UniswapV3, PancakeV3, SushiV3) are only found by
   resolving every configured tier for token pairs revealed by the enumerated pools, not by factory enumeration.
4. **GeckoTerminal rate limiting.** The live run's startup logged `geckoterminal request failed` (HTTP 429) for the `aerodrome-base` listing
   page; per the engine's code that page was skipped. The snapshot's GT statuses are in `geckoterminal-responses.jsonl.gz`
   (14 with status 200, 2 with status 429 [filled in 2026-10-01]).
5. **Live run vs snapshot are different pool sets and times** (see Time window). The live run's depth filter was 0.001 ETH; pools with engine
   depth < 0.001 ETH and unpriced-both-sides pools (depth 0) were not in its search set.
6. **Tick data window**: CL tick data covers only the engine's fetched window (±3000 ticks around the current tick plus one bitmap word on
   each side); ticks outside it are not in `cl-ticks-prefilter.csv.gz`.
7. **Pruned-pool recheck** is a separate read at the same block, not the engine's own sync result.
8. **Engine RPC failures during the live run** (if any) appear only as `tick failed` / `gas refresh failed` lines in `live-shallow.log`;
   the engine does not record skipped blocks explicitly. Blocks with no heartbeat/candidate line are not listed individually.
   [2026-10-01: `live-shallow.log` contains 0 `tick failed` and 0 `gas refresh failed` lines.]
9. **Concurrency**: another agent's engine run (V4 live test) and several collectors shared the same public endpoints during both runs.
10. Only Base was collected here; no other chains.


## Transfer-behaviour probe (attempt 2, 2026-10-01)

**Status: NOT COMPLETED.** `.sentinels/TRANSFER_PROBE.FAILED` was rewritten with this attempt's reason. No `transfer-probe.csv.gz`
or `probe-meta.json` exists. No RPC calls were made in this attempt.
[corrected 2026-10-01: this paragraph describes the state after attempt 2 only. Attempt 3 (next section) completed the probe:
`.sentinels/TRANSFER_PROBE.FAILED` no longer exists, `.sentinels/TRANSFER_PROBE.DONE` does, and `transfer-probe/transfer-probe.csv.gz`
and `transfer-probe/probe-meta.json` exist.]

What exists (directory `transfer-probe/`):

| File | Content |
|---|---|
| `transfer-probe/collect/select_holders.py` | holder selection script (offline, reads only the snapshot files in this directory) |
| `transfer-probe/collect/work/holders.csv.gz` | holder selection output, one row per token in `tokens.csv.gz` (33,597 rows + header) [2026-10-01: local-only (git-ignored `collect/work/`); the committed byte-identical copy is `transfer-probe/holders.csv.gz`] |

Holder selection method (deterministic, no RPC): for each token, among non-V4 rows of `pools-prefilter.csv.gz` and
`pools-pruned-empty.csv.gz` with `token*_balance_ok == true`, the pool with the largest `token*_balance_of_pool` (block 52008246);
tie-break lowest pool address. `kind` univ2/aero-v2 -> `v2`; univ3/aero-cl/pancake-v3 -> `cl`. Fallback to the V4 PoolManager
`0x498581ff718922c3f8e6a244956af099b2652b2b` from `v4-poolmanager-balances.csv.gz` only when no pool had a positive balance.
Command: `cd transfer-probe/collect && python3 select_holders.py`.

`holders.csv.gz` columns: `token`, `symbol` (tokens.csv `symbol_engine`), `decimals` (`decimals_engine`), `holder`, `holder_kind`
(v2|cl|v4_poolmanager, empty = none), `holder_dex`, `holder_balance_snapshot` (raw, base-10), `holder_source_file`,
`n_pools_with_balance_ok`, `n_pools_positive_balance` (counts of snapshot pool rows for that token).

Row counts by `holder_kind`: v2 24,700; cl 5,003; v4_poolmanager 0; none (no positive balance in any snapshot pool or the
PoolManager file) 3,894. Unique holder addresses: 29,478. [re-counted 2026-10-01 on `transfer-probe/holders.csv.gz`: same values]

Not collected: the per-token eth_call transfer probe (step 2 of the task: probe contract, batcher, state-override calls at
block 52008246) and its outputs. The attempt stopped before the probe contract was written. [2026-10-01: collected in attempt 3, next section.]

## Transfer-behaviour probe (attempt 3, 2026-10-01, collected by the main session)

Status: DONE (sentinel TRANSFER_PROBE.DONE). Attempts 1 and 2 (see above) did not produce probe data; attempt 2 produced
the holder selection `transfer-probe/holders.csv.gz`, which this attempt uses unchanged.

Serves: question line 3 (see "Question lines served").

Method:
- Holder per token (from `holders.csv.gz`): the non-V4 pool with the largest snapshot balance of the token among
  `pools-prefilter.csv.gz` and `pools-pruned-empty.csv.gz` (rows with `token*_balance_ok=true`; tie-break lowest pool
  address). 29,703 tokens have a holder, 3,894 have none (`no_holder`).
- One `eth_call` per batch of 16 tokens at Base block **52008246** (the snapshot block) on
  `https://base-mainnet.public.blastapi.io`, with state overrides: the runtime of `collect/src/TransferProbe.sol`
  (solc 0.8.28, optimizer 200, evm cancun) is placed at the batcher `0x000000000000000000000000000000000070b3e1` and at
  every holder in the batch. `run` calls `probeOne` on each holder; `probeOne` executes at the holder address, so the
  token sees `msg.sender == holder pool` (the token movement of a buy out of that pool). It reads
  `balanceOf(holder)`, sets `amount = balance * bps / 10000`, reads the recipient balance, calls
  `transfer(recipient, amount)` with a 1,500,000 gas cap (low-level call, never reverts the batch), then reads both
  balances again.
- Two passes in separate `eth_call`s: bps 100 (1 %) and bps 1 (0.01 %). Recipient
  `0xa875ba6c6102637ce162c2fb6c20ebaa6e411629` (= last 20 bytes of keccak256("dapparb transfer probe recipient");
  no code at the block).
- Within one batch, state changes of earlier items are visible to later items (same `eth_call`). Holders' own pool code
  is replaced by the probe for the whole call, so a token whose transfer logic calls into one of those pools sees the
  probe code there.

Commands:
```
cd research-material/04-shallow-pools/transfer-probe/collect
forge build                                   # compiles src/TransferProbe.sol -> probe-runtime.hex
python3 run_probe.py --smoke                  # 32 tokens (results: collect/probe-batches-smoke.jsonl.gz)
python3 run_probe.py --batch 16 --workers 3   # full run, 3,714 eth_calls, 2026-10-01 02:12-02:19 UTC
python3 build_table.py                        # -> transfer-probe.csv.gz, probe-meta.json
```
[2026-10-01 notes on these commands: `forge build` writes `out/TransferProbe.sol/TransferProbe.json` (and `cache/`); the committed
`probe-runtime.hex` equals that file's `deployedBytecode.object` string (verified). `run_probe.py` and `build_table.py` read and
write `collect/work/` (local-only): restore `work/holders.csv.gz` and `work/probe-batches.jsonl` from the committed copies first
(see "Local-only files: how to regenerate"). The smoke run wrote `work/probe-batches-smoke.jsonl` (4 eth_calls = 2 batches x 2 bps);
`collect/probe-batches-smoke.jsonl.gz` is its gzip copy. `build_table.py` writes `holders_file` = `collect/work/holders.csv.gz` and
`raw_batches_file` = `collect/work/probe-batches.jsonl.gz` into `probe-meta.json`; the committed `probe-meta.json` names the
committed copies (`transfer-probe/holders.csv.gz`, `transfer-probe/probe-batches-raw.jsonl.gz`) instead, so a rerun of
`build_table.py` produces a `probe-meta.json` that differs in those two strings and in `built_utc`. `build_table.py` also calls
`/root/.foundry/bin/forge --version` for the `compiler` string.]

Files (in `transfer-probe/`):

| File | Rows | Content |
|---|---|---|
| transfer-probe.csv.gz | 67,194 (33,597 tokens x 2 bps) | one row per (token, bps); status `ok` 59,406, `no_holder` 7,788 |
| holders.csv.gz | 33,597 | token, symbol, decimals, holder, holder_kind (v2/cl), holder_dex, holder_balance_snapshot, source file, pool counts |
| probe-batches-raw.jsonl.gz | 3,714 | raw `eth_call` result hex per batch, with the items probed. Keys per line: `batch_id` (`bps<bps>-<batch index>`), `bps`, `items` (list of `[holder, token]`), `utc` (time the result was written), `result` (raw return hex; an `error` key replaces it on RPC failure — none present) |
| probe-meta.json | - | block, endpoint, recipient, batcher, gas settings, compiler, runtime sha256, row counts by status |
| collect/probe-batches-smoke.jsonl.gz | 4 | smoke-run raw results (same keys as probe-batches-raw), 32 tokens |

`transfer-probe.csv.gz` columns (all raw; integers in token base units):
token, symbol, holder, holder_kind, holder_dex, holder_balance_snapshot (from the snapshot files), bps, status
(`ok` = the probe returned; `no_holder`; `probe_call_failed` = the call into the holder reverted, data in
outer_revert_hex; `rpc_error`), balance_of_ok (balanceOf(holder) returned >= 32 bytes), holder_balance_at_call,
amount (transfer argument), call_success (the token's `transfer` call did not revert), returned_bool (`true`/`false` when
the return data is exactly 32 bytes with value 1/0, else `none`), return_or_revert_data_hex (return data on success, revert
data on failure), gas_used (gas consumed by the transfer call), recipient_before, recipient_after, received
(= recipient_after - recipient_before, signed), holder_before, holder_after, holder_debited (= holder_before -
holder_after, signed), outer_revert_hex, rpc_error, pinned_block, endpoint, batch_id.

Coverage limits: one block (52008246); one holder per token; the 3,894 tokens without a positive pool balance in the
snapshot were not probed; only `transfer` from a pool to a fresh EOA-like address was simulated (no transferFrom, no
sell direction into a pool, no router path); per-transfer gas cap 1.5 M.
