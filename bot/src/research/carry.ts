/**
 * Delta-neutral carry snapshot (spot-perp funding, cross-venue funding differential, dated-futures basis) from public
 * endpoints reachable here: OKX (spot, perps, dated futures) and Hyperliquid (perps). Prints annualised figures.
 *   npx tsx src/research/carry.ts [--top 25]
 */
const arg = (n: string, d?: string) => { const i = process.argv.indexOf(`--${n}`); return i >= 0 ? process.argv[i + 1]! : d; };
const top = Number(arg("top", "25"));
const get = async (u: string) => (await fetch(u, { signal: AbortSignal.timeout(8000) })).json() as Promise<any>;

async function main() {
  // Hyperliquid: funding is hourly
  const hl: any = await (await fetch("https://api.hyperliquid.xyz/info", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ type: "metaAndAssetCtxs" }) })).json();
  const hlMap = new Map<string, { funding: number; mark: number; oracle: number; oi: number; vol: number }>();
  hl[0].universe.forEach((u: any, i: number) => { const c = hl[1][i]; hlMap.set(u.name, { funding: Number(c.funding), mark: Number(c.markPx), oracle: Number(c.oraclePx), oi: Number(c.openInterest) * Number(c.markPx), vol: Number(c.dayNtlVlm) }); });
  // OKX perps: funding every 8h (fundingRate), tickers for volume
  const swaps: any = await get("https://www.okx.com/api/v5/market/tickers?instType=SWAP");
  const usdt = swaps.data.filter((t: any) => t.instId.endsWith("-USDT-SWAP")).sort((a: any, b: any) => Number(b.volCcy24h) * Number(b.last) - Number(a.volCcy24h) * Number(a.last)).slice(0, top);
  const rows: any[] = [];
  for (const t of usdt) {
    const coin = t.instId.split("-")[0];
    const fr: any = await get(`https://www.okx.com/api/v5/public/funding-rate?instId=${t.instId}`).catch(() => null);
    const f = fr?.data?.[0];
    const okxFunding = f ? Number(f.fundingRate) : NaN;
    const perDay = 24 / (f ? Math.round((Number(f.nextFundingTime) - Number(f.fundingTime)) / 3.6e6) || 8 : 8);
    const okxApr = okxFunding * perDay * 365 * 100;
    const h = hlMap.get(coin);
    const hlApr = h ? h.funding * 24 * 365 * 100 : NaN;
    rows.push({ coin, okxFundingApr: +okxApr.toFixed(2), hlFundingApr: +hlApr.toFixed(2), crossVenueApr: Number.isFinite(hlApr) ? +Math.abs(okxApr - hlApr).toFixed(2) : NaN, okxVol24hUsd: Math.round(Number(t.volCcy24h) * Number(t.last) / 1e6) + "M", hlOiUsd: h ? Math.round(h.oi / 1e6) + "M" : "-" });
    await new Promise((r) => setTimeout(r, 120));
  }
  // OKX dated futures basis for BTC/ETH
  const fut: any = await get("https://www.okx.com/api/v5/market/tickers?instType=FUTURES");
  const spot: any = await get("https://www.okx.com/api/v5/market/tickers?instType=SPOT");
  const spotPx = (c: string) => Number(spot.data.find((s: any) => s.instId === `${c}-USDT`)?.last);
  const basis: any[] = [];
  for (const f of fut.data.filter((x: any) => /^(BTC|ETH)-(USDT|USD|USDC)-\d{6}$/.test(x.instId))) {
    const c = f.instId.split("-")[0]; const exp = f.instId.split("-")[2];
    const expDate = new Date(2000 + Number(exp.slice(0, 2)), Number(exp.slice(2, 4)) - 1, Number(exp.slice(4, 6)));
    const days = (expDate.getTime() - Date.now()) / 8.64e7;
    if (days <= 3) continue;
    const b = Number(f.last) / spotPx(c) - 1;
    if (!Number.isFinite(b)) continue;
    basis.push({ inst: f.instId, daysToExpiry: Math.round(days), basisPct: +(b * 100).toFixed(3), annualisedPct: +((b * 365) / days * 100).toFixed(2) });
  }
  console.log("=== perp funding, annualised % (positive = longs pay shorts) ===");
  console.table(rows.sort((a, b) => (b.crossVenueApr || 0) - (a.crossVenueApr || 0)));
  console.log("=== OKX dated futures basis vs spot ===");
  console.table(basis.sort((a, b) => a.daysToExpiry - b.daysToExpiry));
  const fees = { okxTakerSpotPct: 0.1, okxTakerPerpPct: 0.05, hlTakerPct: 0.045 };
  console.log("round-trip taker fees (%, per leg, list prices):", fees, "→ a spot+perp basis trade costs ≈", (2 * (fees.okxTakerSpotPct + fees.okxTakerPerpPct)).toFixed(2), "% to open+close");
}
main().then(() => process.exit(0)).catch((e) => { console.error(e); process.exit(1); });
