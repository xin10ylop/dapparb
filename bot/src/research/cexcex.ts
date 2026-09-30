/**
 * CEX-to-CEX executable spread study across OKX, Gate.io and Kraken spot (all reachable without accounts).
 * Every ~2 s: pull all tickers from each venue, and for every pair listed on at least two of them compute the best
 * executable cross-venue spread = bid(sell venue) / ask(buy venue) - 1, in bps, gross and net of taker fees.
 *   npx tsx src/research/cexcex.ts --minutes 15 --out data/cexcex.jsonl
 */
import "dotenv/config";
import fs from "node:fs";
const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const minutes = Number(arg("minutes", "15"));
const out = fs.createWriteStream(arg("out", "data/cexcex.jsonl")!, { flags: "a" });
const FEES_BPS = { okx: 10, gate: 20, kraken: 40 }; // base-tier taker fees per leg, bps (list prices; VIP tiers are lower)
type Book = Record<string, { bid: number; ask: number; vol: number }>; // key = BASE-QUOTE (USDT or USD)
const get = async (u: string) => (await fetch(u, { signal: AbortSignal.timeout(6000) })).json() as Promise<any>;

async function okx(): Promise<Book> {
  const j = await get("https://www.okx.com/api/v5/market/tickers?instType=SPOT"); const b: Book = {};
  for (const t of j.data ?? []) if (String(t.instId).endsWith("-USDT") && Number(t.bidPx) > 0) b[t.instId] = { bid: Number(t.bidPx), ask: Number(t.askPx), vol: Number(t.volCcy24h) * Number(t.last) };
  return b;
}
async function gate(): Promise<Book> {
  const j = await get("https://api.gateio.ws/api/v4/spot/tickers"); const b: Book = {};
  for (const t of j ?? []) if (String(t.currency_pair).endsWith("_USDT") && Number(t.highest_bid) > 0) b[String(t.currency_pair).replace("_", "-")] = { bid: Number(t.highest_bid), ask: Number(t.lowest_ask), vol: Number(t.quote_volume) };
  return b;
}
async function kraken(): Promise<Book> {
  const j = await get("https://api.kraken.com/0/public/Ticker"); const b: Book = {};
  for (const [k, t] of Object.entries<any>(j.result ?? {})) {
    const m = /^([A-Z0-9]+?)(USDT|USD)$/.exec(k.replace(/^X(?=[A-Z]{3}Z)/, "").replace(/ZUSD$/, "USD")); if (!m) continue;
    const base = m[1]!.replace(/^X/, "").replace(/^XBT$/, "BTC");
    b[`${base}-${m[2]}`] = { bid: Number(t.b[0]), ask: Number(t.a[0]), vol: Number(t.v[1]) * Number(t.c[0]) };
  }
  return b;
}
const venues = { okx, gate, kraken } as const;

async function main() {
  const end = Date.now() + minutes * 60_000; let n = 0;
  const stats = new Map<string, { hits: number; maxNet: number; sumNet: number; venues: string; vol: number }>();
  while (Date.now() < end) {
    const t0 = Date.now();
    const books = await Promise.all(Object.entries(venues).map(async ([name, fn]) => [name, await fn().catch(() => ({} as Book))] as const));
    const byPair = new Map<string, Array<[string, { bid: number; ask: number; vol: number }]>>();
    for (const [name, b] of books) for (const [pair, q] of Object.entries(b)) { const key = pair.replace(/-USD$/, "-USDT"); byPair.set(key, [...(byPair.get(key) ?? []), [name, q]]); }
    let opportunities = 0;
    for (const [pair, qs] of byPair) {
      if (qs.length < 2) continue;
      let best = { net: -Infinity, gross: 0, buy: "", sell: "", vol: 0 };
      for (const [bn, bq] of qs) for (const [sn, sq] of qs) {
        if (bn === sn || !(bq.ask > 0) || !(sq.bid > 0)) continue;
        const gross = (sq.bid / bq.ask - 1) * 1e4;
        const net = gross - FEES_BPS[bn as keyof typeof FEES_BPS] - FEES_BPS[sn as keyof typeof FEES_BPS];
        if (net > best.net) best = { net, gross, buy: bn, sell: sn, vol: Math.min(bq.vol, sq.vol) };
      }
      if (best.net > 0 && best.vol > 50_000) {
        opportunities++;
        const s = stats.get(pair) ?? { hits: 0, maxNet: -Infinity, sumNet: 0, venues: "", vol: best.vol };
        s.hits++; s.maxNet = Math.max(s.maxNet, best.net); s.sumNet += best.net; s.venues = `${best.buy}→${best.sell}`; stats.set(pair, s);
        out.write(JSON.stringify({ t: t0, pair, ...best }) + "\n");
      }
    }
    n++;
    if (n % 30 === 0) console.log(`${new Date().toISOString()} samples=${n} pairs=${byPair.size} net-positive now=${opportunities} (min 24h vol $50k on both venues)`);
    await new Promise((r) => setTimeout(r, Math.max(200, 2000 - (Date.now() - t0))));
  }
  console.log(`\n=== CEX-CEX summary: ${n} samples over ${minutes} min ===`);
  const rows = [...stats.entries()].map(([pair, s]) => ({ pair, route: s.venues, samplesPositive: s.hits, pctOfTime: +(100 * s.hits / n).toFixed(1), maxNetBps: +s.maxNet.toFixed(1), avgNetBps: +(s.sumNet / s.hits).toFixed(1), minVol24hUsd: Math.round(s.vol / 1e3) + "k" })).sort((a, b) => b.maxNetBps - a.maxNetBps);
  console.table(rows.slice(0, 25));
  console.log(`pairs ever net-positive after base-tier taker fees: ${rows.length}; persistent (>50% of samples): ${rows.filter((r) => r.pctOfTime > 50).length}`);
  out.end(); process.exit(0);
}
main().catch((e) => { console.error(e); process.exit(1); });
