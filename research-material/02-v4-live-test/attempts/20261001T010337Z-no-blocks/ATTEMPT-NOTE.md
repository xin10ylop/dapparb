# Attempt 2026-10-01T01:03:37Z: invalid (no blocks processed)

Recorded facts:
- The engine reached `searcher ready` at 2026-10-01T01:37:18Z (75,009 tokens, 11,779 pools, 9,494 cycles) and logged
  `subscribed to newHeads via websocket`.
- During the following 1,200 s it logged no heartbeat. The shutdown record shows `ticks: 0`, `logsApplied: 0`,
  `touchedPools: 0`. `live-v4.jsonl` is empty.
- The container had restarted at about 2026-09-30T23:00Z. At about 02:00Z a direct test of
  `wss://base-rpc.publicnode.com` (eth_subscribe newHeads) did not complete the websocket handshake within 20 s.
  The agent proxy's notes (/root/.ccr/README.md) list "WebSocket upgrades" as not supported through the proxy.
  In the same period (01:42Z-02:02Z) the detection-only engine runs in 07-other-chains-engine did receive newHeads over
  `wss://arbitrum-one-rpc.publicnode.com` and `wss://ethereum-rpc.publicnode.com` (4,000 and 100 ticks). The cause
  of the Base websocket failure was not determined.
- The engine's block trigger in `--source logs` mode is the websocket newHeads subscription when a websocket URL is
  configured (bot/src/main.ts), so no block reached the searcher.

The run was repeated with `NO_WS=1`, which makes the engine use its existing HTTP `eth_blockNumber` polling trigger
(see the main manifest section for the repeated run). The V4LIVE.DONE sentinel this attempt wrote is kept here as
`V4LIVE.DONE.invalidated`.
