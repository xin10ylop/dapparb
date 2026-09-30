/** Summarise data/leadlag.jsonl: CEX (OKX) vs Base pool price spreads and lead-lag. */
import fs from "node:fs";
const rows = fs.readFileSync(process.argv[2] ?? "data/leadlag.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const cex = rows.filter((r) => r.src === "okx").sort((a, b) => a.t - b.t);
const dex = rows.filter((r) => r.src === "base").sort((a, b) => a.t - b.t);
const cexAt = (t: number) => { let lo = 0, hi = cex.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (cex[m]!.t <= t) lo = m; else hi = m - 1; } return cex[lo]; };
console.log(`cex samples=${cex.length} dex blocks=${dex.length} window=${((dex[dex.length - 1]?.t - dex[0]?.t) / 60000).toFixed(1)} min`);
for (const name of ["UniV3/500", "AeroCL3/50", "PancakeV3/100"]) {
  const spreads: number[] = []; const lagRet: Record<number, number[]> = {};
  for (let i = 1; i < dex.length; i++) {
    const d = dex[i]!; if (!(d as any)[name]) continue;
    const c = cexAt(d.t); if (!c) continue;
    spreads.push(((d as any)[name] / c.mid - 1) * 1e4);
    // does the CEX move in the previous k*250ms predict the DEX return over this block? (sign agreement)
    const dPrev = dex[i - 1]!; if (!(dPrev as any)[name]) continue;
    const dexRet = (d as any)[name] / (dPrev as any)[name] - 1;
    for (const lagMs of [0, 500, 1000, 2000, 4000]) {
      const c0 = cexAt(dPrev.t - lagMs); const c1 = cexAt(d.t - lagMs); if (!c0 || !c1) continue;
      const cexRet = c1.mid / c0.mid - 1;
      if (Math.abs(cexRet) > 1e-5 && Math.abs(dexRet) > 1e-5) (lagRet[lagMs] ??= []).push(Math.sign(cexRet) === Math.sign(dexRet) ? 1 : 0);
    }
  }
  const s = [...spreads].sort((a, b) => a - b); const q = (p: number) => s[Math.floor(p * (s.length - 1))]!;
  console.log(`${name}: spread vs OKX mid (bps): p5=${q(0.05).toFixed(1)} p50=${q(0.5).toFixed(1)} p95=${q(0.95).toFixed(1)} |>10bps: ${(100 * spreads.filter((x) => Math.abs(x) > 10).length / spreads.length).toFixed(1)}% |>20bps: ${(100 * spreads.filter((x) => Math.abs(x) > 20).length / spreads.length).toFixed(1)}%`);
  console.log(`   sign agreement of DEX block return with CEX return shifted by lag: ${Object.entries(lagRet).map(([k, v]) => `${k}ms:${(100 * v.reduce((a, b) => a + b, 0) / v.length).toFixed(0)}% (n=${v.length})`).join("  ")}`);
}
