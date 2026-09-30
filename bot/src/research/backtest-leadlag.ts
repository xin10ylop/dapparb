/**
 * Statistical (lead-lag) strategy backtest on recorded OKX/Base data: when OKX's mid moved by more than `trigger`
 * bps over the last `window` ms and the Base pool has not yet moved as much, buy (or sell) at the pool's price plus
 * fee, and close `hold` blocks later at the pool's price minus fee. Reports the net P&L distribution in bps.
 *   npx tsx src/research/backtest-leadlag.ts data/leadlag.jsonl --pool AeroCL3/50 --fee-bps 4 --trigger 8 --hold 2
 */
import fs from "node:fs";
const file = process.argv[2] ?? "data/leadlag.jsonl";
const arg = (n: string, d: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const pool = arg("pool", "AeroCL3/50"); const feeBps = Number(arg("fee-bps", "4")); const trigger = Number(arg("trigger", "8")); const hold = Number(arg("hold", "2")); const window = Number(arg("window", "1500"));
const rows = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const cex = rows.filter((r) => r.src === "okx").sort((a, b) => a.t - b.t);
const dex = rows.filter((r) => r.src === "base" && r[pool]).sort((a, b) => a.t - b.t);
const cexAt = (t: number) => { let lo = 0, hi = cex.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (cex[m]!.t <= t) lo = m; else hi = m - 1; } return cex[lo]; };
const pnl: number[] = []; let signals = 0;
for (let i = 1; i + hold < dex.length; i++) {
  const d = dex[i]!; const c1 = cexAt(d.t); const c0 = cexAt(d.t - window); if (!c0 || !c1) continue;
  const cexMove = (c1.mid / c0.mid - 1) * 1e4;
  const dexMove = (d[pool] / dex[i - 1]![pool] - 1) * 1e4;
  if (Math.abs(cexMove) < trigger || Math.sign(dexMove) === Math.sign(cexMove) && Math.abs(dexMove) >= Math.abs(cexMove) * 0.5) continue;
  signals++;
  const dir = Math.sign(cexMove); // +1: expect DEX up → buy now, sell in `hold` blocks
  const entry = d[pool] * (1 + dir * feeBps / 1e4); // pay the fee/impact on entry
  const exit = dex[i + hold]![pool] * (1 - dir * feeBps / 1e4);
  pnl.push(dir * (exit / entry - 1) * 1e4);
}
const s = [...pnl].sort((a, b) => a - b); const q = (p: number) => (s.length ? s[Math.floor(p * (s.length - 1))]!.toFixed(1) : "-");
const mean = pnl.length ? pnl.reduce((a, b) => a + b, 0) / pnl.length : NaN;
console.log(`${file} pool=${pool} fee=${feeBps}bps trigger=${trigger}bps window=${window}ms hold=${hold} blocks: signals=${signals} trades=${pnl.length} win-rate=${(100 * pnl.filter((x) => x > 0).length / Math.max(1, pnl.length)).toFixed(0)}% mean=${mean.toFixed(2)}bps p10=${q(0.1)} p50=${q(0.5)} p90=${q(0.9)} sum=${pnl.reduce((a, b) => a + b, 0).toFixed(0)}bps`);
