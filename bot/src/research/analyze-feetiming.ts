/** Summarise data/feetiming.jsonl: fee transitions on Slipstream pools and the arb value in the blocks after a drop. */
import fs from "node:fs";
const rows = fs.readFileSync(process.argv[2] ?? "data/feetiming.jsonl", "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const byPool = new Map<string, any[]>();
for (const r of rows) byPool.set(r.pool, [...(byPool.get(r.pool) ?? []), r]);
const changes = rows.filter((r) => r.feeChanged !== null);
const drops = changes.filter((r) => r.fee < r.feeChanged);
const rises = changes.filter((r) => r.fee > r.feeChanged);
console.log(`pools=${byPool.size} records=${rows.length} blocks≈${new Set(rows.map((r) => r.block)).size}`);
console.log(`fee transitions: ${changes.length} (drops ${drops.length}, rises ${rises.length}); pools with any change: ${new Set(changes.map((r) => r.pool)).size}`);
const fmt = (r: any) => `${r.pair} ${r.dex}/${r.ts} ${r.feeChanged}→${r.fee} pips @${r.block} gap=${r.bestGapBps}bps bestCycle=$${r.bestCycleUsd}`;
console.log("largest fee drops:"); for (const r of [...drops].sort((a, b) => (b.feeChanged - b.fee) - (a.feeChanged - a.fee)).slice(0, 8)) console.log("  " + fmt(r));
console.log("largest fee rises:"); for (const r of [...rises].sort((a, b) => (b.fee - b.feeChanged) - (a.fee - a.feeChanged)).slice(0, 8)) console.log("  " + fmt(r));
// value of the best cycle through a pool in the 5 blocks after a drop vs a random block
const after = drops.map((d) => rows.filter((r) => r.pool === d.pool && r.block > d.block && r.block <= d.block + 5).map((r) => r.bestCycleUsd)).flat();
const base = rows.filter((r) => r.feeChanged === null).map((r) => r.bestCycleUsd);
const mean = (a: number[]) => (a.length ? a.reduce((s, x) => s + x, 0) / a.length : NaN);
const cnt = (a: number[], t: number) => a.filter((x) => x >= t).length;
console.log(`best cycle USD through the pool: after a fee drop mean=$${mean(after).toFixed(4)} (n=${after.length}, ≥$0.01: ${cnt(after, 0.01)}) | baseline mean=$${mean(base).toFixed(4)} (n=${base.length}, ≥$0.01: ${cnt(base, 0.01)})`);
console.log("pools with ≥$0.01 best cycle at any sample:", [...byPool.entries()].map(([p, rs]) => [rs[0].pair + " " + rs[0].dex + "/" + rs[0].ts, Math.max(...rs.map((r) => r.bestCycleUsd)), rs.filter((r) => r.bestCycleUsd >= 0.01).length] as const).filter((x) => x[1] >= 0.01).sort((a, b) => b[1] - a[1]).slice(0, 10).map((x) => `${x[0]} max=$${x[1].toFixed(3)} samples=${x[2]}`).join(" | "));
