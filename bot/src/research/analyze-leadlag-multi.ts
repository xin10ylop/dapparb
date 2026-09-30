import fs from "node:fs";
const rows = fs.readFileSync(process.argv[2] ?? "data/leadlag-multi.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const cex = rows.filter((r) => r.src === "okx").sort((a, b) => a.t - b.t);
const dex = rows.filter((r) => r.src === "base").sort((a, b) => a.t - b.t);
const cexAt = (t: number) => { let lo = 0, hi = cex.length - 1; while (lo < hi) { const m = (lo + hi + 1) >> 1; if (cex[m]!.t <= t) lo = m; else hi = m - 1; } return cex[lo]; };
console.log(`cex=${cex.length} dex=${dex.length} window=${((dex[dex.length - 1]?.t - dex[0]?.t) / 60000).toFixed(1)} min`);
const syms = new Set<string>(); for (const d of dex) Object.keys(d.px).forEach((s) => syms.add(s));
for (const s of syms) {
  const spreads: number[] = []; let persist = 0, persistN = 0, prevOut = false;
  for (const d of dex) {
    const p = d.px[s]; const c = cexAt(d.t); if (!p || !c) continue;
    const cexUsd = c.mids[s]; const ethUsd = c.mids["ETH"]; if (!cexUsd) continue;
    const dexUsd = p.quote === "WETH" ? p.price * ethUsd : p.price;
    const bps = (dexUsd / cexUsd - 1) * 1e4; spreads.push(bps);
    const outside = Math.abs(bps - 0) > 30; if (outside) { persistN++; if (prevOut) persist++; } prevOut = outside;
  }
  if (!spreads.length) continue;
  const so = [...spreads].sort((a, b) => a - b); const q = (x: number) => so[Math.floor(x * (so.length - 1))]!;
  const med = q(0.5); const dev = spreads.map((x) => Math.abs(x - med));
  console.log(`${s.padEnd(8)} n=${spreads.length} DEX-OKX bps: p5=${q(0.05).toFixed(0)} p50=${med.toFixed(0)} p95=${q(0.95).toFixed(0)} | |dev from median|>30bps: ${(100 * dev.filter((x) => x > 30).length / dev.length).toFixed(1)}%  >60bps: ${(100 * dev.filter((x) => x > 60).length / dev.length).toFixed(1)}%  >100bps: ${(100 * dev.filter((x) => x > 100).length / dev.length).toFixed(1)}%`);
}
