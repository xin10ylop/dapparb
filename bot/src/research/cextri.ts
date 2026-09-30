/**
 * Single-exchange triangular arbitrage study (OKX and Gate spot). For every triangle A/USDT, B/USDT, A/B: cycle
 * return of USDT → A → B → USDT (and the reverse) using best bid/ask, net of three taker fees. Sampled every ~2 s.
 *   npx tsx src/research/cextri.ts --minutes 15 --out data/cextri.jsonl
 */
import "dotenv/config";
import fs from "node:fs";
const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "15"));
const out = fs.createWriteStream(arg("out", "data/cextri.jsonl")!, { flags: "a" });
const get = async (u: string) => (await fetch(u, { signal: AbortSignal.timeout(6000) })).json() as Promise<any>;
type Q = { bid: number; ask: number; vol: number };
async function okx(): Promise<Map<string, Q>> { const j = await get("https://www.okx.com/api/v5/market/tickers?instType=SPOT"); const m = new Map<string, Q>(); for (const t of j.data ?? []) if (Number(t.bidPx) > 0 && Number(t.askPx) > 0) m.set(t.instId, { bid: +t.bidPx, ask: +t.askPx, vol: +t.volCcy24h * +t.last }); return m; }
async function gate(): Promise<Map<string, Q>> { const j = await get("https://api.gateio.ws/api/v4/spot/tickers"); const m = new Map<string, Q>(); for (const t of j ?? []) if (+t.highest_bid > 0 && +t.lowest_ask > 0) m.set(String(t.currency_pair).replace("_", "-"), { bid: +t.highest_bid, ask: +t.lowest_ask, vol: +t.quote_volume }); return m; }
const VENUES = { okx: { fn: okx, feeBps: 10 }, gate: { fn: gate, feeBps: 20 } } as const;
async function main() {
  const end = Date.now() + minutes * 60_000; let n = 0;
  const stats = new Map<string, { hits: number; maxNet: number; sumNet: number }>();
  while (Date.now() < end) {
    const t0 = Date.now(); let posNow = 0;
    for (const [venue, v] of Object.entries(VENUES)) {
      const book = await v.fn().catch(() => new Map<string, Q>());
      const bases = new Set<string>(); for (const k of book.keys()) if (k.endsWith("-USDT")) bases.add(k.slice(0, -5));
      const f = 1 - v.feeBps / 1e4;
      for (const [pair, q] of book) {
        const [a, b] = pair.split("-"); if (!a || !b || b === "USDT" || !bases.has(a) || !bases.has(b)) continue; // pair A-B with both A/USDT and B/USDT listed
        const aU = book.get(`${a}-USDT`)!, bU = book.get(`${b}-USDT`)!;
        if (Math.min(q.vol, aU.vol, bU.vol) < 20_000) continue;
        // path 1: USDT -> B (buy at bU.ask) -> A (buy A with B at q.ask, price of A in B) -> USDT (sell A at aU.bid)
        const r1 = (1 / bU.ask) * f * (1 / q.ask) * f * aU.bid * f;
        // path 2: USDT -> A (buy at aU.ask) -> B (sell A for B at q.bid) -> USDT (sell B at bU.bid)
        const r2 = (1 / aU.ask) * f * q.bid * f * bU.bid * f;
        const best = Math.max(r1, r2); const net = (best - 1) * 1e4;
        if (net > 0) {
          posNow++;
          const key = `${venue}:${pair}`; const s = stats.get(key) ?? { hits: 0, maxNet: -Infinity, sumNet: 0 };
          s.hits++; s.maxNet = Math.max(s.maxNet, net); s.sumNet += net; stats.set(key, s);
          out.write(JSON.stringify({ t: t0, venue, pair, netBps: +net.toFixed(2), path: r1 >= r2 ? "USDT>B>A>USDT" : "USDT>A>B>USDT", minVol: Math.round(Math.min(q.vol, aU.vol, bU.vol)) }) + "\n");
        }
      }
    }
    n++;
    if (n % 30 === 0) console.log(`${new Date().toISOString()} samples=${n} net-positive triangles now=${posNow}`);
    await new Promise((r) => setTimeout(r, Math.max(200, 2000 - (Date.now() - t0))));
  }
  console.log(`\n=== CEX triangular summary: ${n} samples over ${minutes} min ===`);
  const rows = [...stats.entries()].map(([k, s]) => ({ triangle: k, samplesPositive: s.hits, pctOfTime: +(100 * s.hits / n).toFixed(1), maxNetBps: +s.maxNet.toFixed(1), avgNetBps: +(s.sumNet / s.hits).toFixed(1) })).sort((a, b) => b.maxNetBps - a.maxNetBps);
  console.table(rows.slice(0, 20));
  console.log(`triangles ever net-positive after 3 taker fees: ${rows.length}; persistent (>50% of samples): ${rows.filter((r) => r.pctOfTime > 50).length}`);
  out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
