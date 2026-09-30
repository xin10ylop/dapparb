# Infrastructure: co-located Base node + searcher

Everything the searcher needs to see state ~200 ms after it exists and to submit within the same window is a
Base node that consumes the Flashblocks stream. Public endpoints cannot do this: the preconfirmation RPC
allows ~5 requests per 10 s (measured 2026-09-30) and Base publishes no WebSocket RPC. Facts from Base's own
docs and the 2026 measurement papers (sources in `docs/ANALYSIS.md`):

* Ordering: arrival time decides which 200 ms flashblock a transaction lands in; priority fee only orders
  within that flashblock. Only the first slot of a flashblock is fee-sensitive.
* Base's sequencer location is not published (all endpoints are Cloudflare-fronted). Arbitrum's public sequencer
  gateway resolves to AWS us-east-2. Pick the region empirically: run the latency probe from candidate regions
  and keep the one with the lowest sequencer round-trip.
* Node requirements (docs.base.org): 8+ cores, 64 GB RAM recommended, locally attached NVMe, ≥2 TB for a
  full node (archive ≈4.5 TB). Base runs its own archive nodes on `i7i.12xlarge` (~$3.3k/month list price).
  A full node fits an `i7ie.3xlarge`-class instance (12 vCPU, 96 GiB, 7.5 TB NVMe); check current pricing.

## Layout

```
infra/
  docker-compose.yml   op-node + op-reth (Base image) with the Flashblocks websocket enabled, plus the bot
  terraform/main.tf    one instance, NVMe RAID-0, security group (no inbound RPC exposure)
  probe-latency.sh     RTT to sequencer / preconf endpoints from the current machine
```

The bot connects to the local node only:

```
BASE_RPC_URL=http://127.0.0.1:8545
BASE_WS_URL=ws://127.0.0.1:8546
SUBMIT_RPC_URLS=https://mainnet-sequencer.base.org      # direct submission endpoint (docs.base.org)
npx tsx src/main.ts --chain base --mode live --source logs --receipts-tag pending --universe top
```

`--source logs --receipts-tag pending` reads pending receipts from the local flashblocks-aware node every
200 ms, derives exact pool state from the logs (verified: 0 mismatches vs. multicall), and re-evaluates only
the cycles through pools that changed (~10–20 per block, sub-millisecond). Fall back to
`--receipts-tag latest` on a node without Flashblocks support (2 s granularity).

## Not verified here

This container cannot provision cloud resources or run a 2 TB node, so the compose file and Terraform were
written from the official base/node documentation and have not been executed. Treat them as a starting point
to be validated on the target instance; every other component in this repository was executed and tested.
