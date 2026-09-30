/**
 * Summarise a live/dry-run JSONL: what was detected, what simulated, how long opportunities lived, and the
 * upper bound on capture. Usage: npx tsx src/research/analyze.ts data/live-base-long.jsonl
 */
import fs from "node:fs";

const file = process.argv[2] ?? "data/live-base-long.jsonl";
const rows = fs.readFileSync(file, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const dets = rows.filter((r) => r.route);
const t0 = new Date(dets[0]?.t ?? 0).getTime();
const t1 = new Date(dets[dets.length - 1]?.t ?? 0).getTime();
const hours = Math.max((t1 - t0) / 3.6e6, 1e-6);
const simOk = dets.filter((r) => r.sim && "profitUsd" in r.sim);
const simRev = dets.filter((r) => r.sim && "error" in r.sim);
const wouldSend = dets.filter((r) => typeof r.simNetUsd === "number" && r.simNetUsd >= 0.01);
const byRoute = new Map<string, any[]>();
for (const r of dets) byRoute.set(r.route, [...(byRoute.get(r.route) ?? []), r]);

// cluster consecutive detections of the same route into "episodes" (gap > 3 blocks starts a new one)
interface Episode { route: string; startBlock: number; endBlock: number; n: number; maxPredicted: number; maxSimNet: number; simOk: number; simRev: number; token: string; }
const episodes: Episode[] = [];
for (const [route, rs] of byRoute) {
  rs.sort((a, b) => a.block - b.block || a.fb - b.fb);
  let cur: Episode | null = null;
  for (const r of rs) {
    if (!cur || r.block - cur.endBlock > 3) {
      cur = { route, startBlock: r.block, endBlock: r.block, n: 0, maxPredicted: 0, maxSimNet: -Infinity, simOk: 0, simRev: 0, token: r.token };
      episodes.push(cur);
    }
    cur.endBlock = r.block;
    cur.n++;
    cur.maxPredicted = Math.max(cur.maxPredicted, r.netUsd ?? 0);
    if (r.sim && "profitUsd" in r.sim) {
      cur.simOk++;
      cur.maxSimNet = Math.max(cur.maxSimNet, r.simNetUsd ?? -Infinity);
    } else if (r.sim && "error" in r.sim) cur.simRev++;
  }
}
const real = episodes.filter((e) => e.simOk > 0 && e.maxSimNet >= 0.01);
const lifetimes = real.map((e) => e.endBlock - e.startBlock + 1);
const capture = real.reduce((s, e) => s + e.maxSimNet, 0);
const errs = new Map<string, number>();
for (const r of simRev) errs.set(String(r.sim.error).slice(0, 50), (errs.get(String(r.sim.error).slice(0, 50)) ?? 0) + 1);
const tokenCount = new Map<string, number>();
for (const e of real) tokenCount.set(e.route.split("@")[0]!.split(">").join("/"), (tokenCount.get(e.route.split("@")[0]!.split(">").join("/")) ?? 0) + 1);

console.log(`file=${file}`);
console.log(`window: ${new Date(t0).toISOString()} → ${new Date(t1).toISOString()} (${hours.toFixed(2)} h)`);
console.log(`detections (predicted net > threshold): ${dets.length} across ${byRoute.size} routes; episodes: ${episodes.length}`);
console.log(`simulated: ok=${simOk.length} reverted=${simRev.length}; would-send (sim net ≥ $0.01): ${wouldSend.length}`);
console.log(`REAL episodes (simulated net ≥ $0.01 at least once): ${real.length}  → ${(real.length / hours).toFixed(1)} per hour`);
console.log(`  lifetime in blocks: min=${Math.min(...lifetimes)} median=${[...lifetimes].sort((a, b) => a - b)[Math.floor(lifetimes.length / 2)]} max=${Math.max(...lifetimes)}  (block = 2 s)`);
console.log(`  best simulated net per episode: sum=$${capture.toFixed(3)} → $${(capture / hours).toFixed(2)}/hour upper bound if every race were won`);
console.log(`  by pair: ${[...tokenCount.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).map(([k, v]) => `${k}:${v}`).join("  ")}`);
console.log(`sim revert reasons: ${[...errs.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4).map(([k, v]) => `${v}× ${k}`).join(" | ")}`);
console.log(`\nreal episodes:`);
for (const e of real.sort((a, b) => b.maxSimNet - a.maxSimNet).slice(0, 20)) console.log(`  $${e.maxSimNet.toFixed(4)} net  blocks ${e.startBlock}-${e.endBlock} (${e.endBlock - e.startBlock + 1})  simOk=${e.simOk}/${e.simOk + e.simRev}  ${e.route}`);
