### 2.6 Full-factory universe: does the ceiling scale with pool count?

Same engine as §2.5, but the universe is every pool the factories know about instead of the configured token
list: `--universe all --max-per-factory 6000` enumerates the newest 6,000 pools of each V2-style factory and
every Slipstream pool (Aerodrome CL: 3,648 + 2,766 + 2,259; Aerodrome V2: 6,000 of 29,600; Uniswap V2:
6,000 of 3,063,599; Sushi, Pancake, BaseSwap: ~6,000 each), resolves every V3/Pancake fee tier for each pair,
adds the Uniswap V4 pools GeckoTerminal lists, and keeps pools with at least 0.1 ETH of depth.

**The first run of this universe reported fake profit.** Its largest "episode" was $28.88 on a WMTW/USDC
cycle with a 4,010,240,259 bps gap. On-chain both WMTW pools hold a combined $0.002 of USDC. The token had
been priced from its own dead pool; that price then valued the pool's WMTW side at 0.1 ETH and it passed the
depth filter. Fix (`pricing.ts`, `depth.ts`): a token is priced only through WETH or USDC pools whose anchor
side holds at least 0.05 ETH (depth-weighted median across such pools), and a pool's depth is the smaller of
its two priced sides, so the side that could never be bought out of a dead pool cannot carry it. The run was
restarted with the fix; the universe after the filter went from 3,282 pools to 3,189 (3,608 cycles), versus
657 pools in §2.5.

**One real episode from the first run, traced on-chain.** At block 51998756 the searcher found
WETH→RSR (Uniswap V3 1 %)→WETH (Aerodrome) for 0.139021 WETH in, simulated net $13.07, gap 854 bps; the gap
had been opened in that block by a 1.67 M-gas transaction that bought RSR on Aerodrome. In the next block
(51998757), at transaction index 1, address `0xF0523316…` (481,276 transactions sent, 20 ETH balance) closed
it through contract `0xA0578728…` with 0.139020 WETH in: the same optimum to five decimals. Its receipt:

| | |
|---|---|
| Gross (WETH received − WETH spent) | 0.004871 WETH = $13.12 |
| Gas: 208,864 × 22.575 gwei (priority fee 22.570 gwei; Base's normal tip is ~0.001–0.05 gwei) | 0.004715 ETH = $12.70 |
| Kept | 0.000156 ETH = **$0.42**, 3.2 % of the gap |

**That operator's economics, measured.** Its last 50 transactions (1.82 h, 44 landed, 6 reverted) were
valued exactly by the change in ETH + WETH + USDC across its wallet and three contracts at each transaction's
block (archive `eth_getBalance` / `balanceOf`, 1,128 calls, none missing), which captures Uniswap V4 native-ETH
payouts that emit no `Transfer`:

| | |
|---|---|
| Sum over 47 blocks, gas included | **−$0.09** |
| Blocks with net > $0.27 | 2 (+$5.97; largest single win $5.55) |
| Blocks with net < −$0.27 | 7 (−$6.69: reverted attempts and "empty" landings that still paid the tip) |
| Everything else | 38 blocks netting between −$0.27 and +$0.27: contested wins grossing $7–13, tipping $6–13, keeping $0.20–0.42 |
| Fees paid in the window | 0.03803 ETH = $102.40 (mean $2.05 per attempt) |
| Wallet-level 24 h change of the same four addresses | +0.1085 ETH = +$292 (includes whatever else those contracts receive; a 5.94 ETH internal top-up in the window nets out) |

The contracts are called by that one wallet only (49 of 50 external calls in the window). This is the
priority-gas-auction equilibrium on Base: the sequencer orders by priority fee, the bots bid the gap away, and
the operator with half a million transactions keeps cents per contested win.

**The XDP/USDC pair, which produced 21 of the 24 episodes in §2.5, is a bot farm.** In the 3,000 blocks
(100 min) before 17:10 UTC the Uniswap V3 0.01 % pool had 11,541 swaps and the Slipstream pool 35,758; 5,873
transactions touched both pools in the same transaction, one per block. Four senders account for most of them.
All four, valued the same way (ETH + WETH + USDC + XDP at the pool price, at each transaction's block, gas
included, last 60 transactions of each):

| Bot | Transactions | Landed | Net | Fees | Per win |
|---|---|---|---|---|---|
| `0x7789515e…` → contract `0x952f339d…` | 809 in 100 min; sample 60 in 12 min (median tip 0.0043 gwei) | 60 / 60 | **+$0.13 → $0.66/hour** | $0.46 ($0.008 per tx) | median $0.0018, max $0.023 |
| `0x0190f008…` → contract `0xcd447b60…` | 411; sample 60 in 14 min (median tip 0.059 gwei) | 60 / 60 | **+$0.49 → $1.99/hour** | $3.85 ($0.064 per tx) | median $0.0069, max $0.046 |
| `0x000000c5…` → contract `0x0ce14aee…` | 163; sample 60 in 36 min (tip 0) | 60 / 60 | **+$0.89 → $1.49/hour** | $5.32 ($0.089 per tx) | median $0.0132, max $0.077 |
| `0x3be22b31…` → contract `0x08c61873…` | 146; sample 60 in 12 min (median tip 0.012 gwei) | 60 / 60 | **+$0.17 → $0.83/hour** | $0.80 ($0.013 per tx) | median $0.0038, max $0.015 |

These are the operators who capture the pair this repository's baseline kept detecting: 100–800 transactions
an hour each, every one landed, for $16–48 a day each and **about $5/hour for the whole pair**, which is the
§2.5 ceiling ($4.77/hour) measured from the other side. The pair's arbitrage income is real, it is fully
captured, and it is split four ways.
