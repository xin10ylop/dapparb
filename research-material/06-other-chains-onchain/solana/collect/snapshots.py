#!/usr/bin/env python3
"""One-time raw JSON snapshots (verbatim bodies, gzip) into ../snapshots/ with an index.csv (url, method, fetch time, status, file).
Groups:
  defillama: api.llama.fi overview/summary endpoints for Solana DEX volume, aggregators, fees, Jito tips
  jito:      kobe.mainnet.jito.network public stats (validators incl. running_jito / running_bam, MEV rewards) and
             bundles.jito.wtf recent bundles (sort by time and by tip)
  rpc:       Solana JSON-RPC state at fetch time (getVoteAccounts, getClusterNodes, getEpochInfo, getRecentPerformanceSamples,
             getRecentPrioritizationFees, getLeaderSchedule for the current epoch is NOT fetched - getSlotLeaders covers the window)
usage: python3 snapshots.py
"""
import csv, datetime, gzip, json, os, re, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); OUT = os.path.join(BASE, "snapshots")
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
RPC = "https://api.mainnet-beta.solana.com"
def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
GETS = [
 ("defillama", "https://api.llama.fi/overview/dexs/solana"),
 ("defillama", "https://api.llama.fi/overview/dexs/solana?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=false&dataType=dailyVolume"),
 ("defillama", "https://api.llama.fi/overview/aggregators/solana"),
 ("defillama", "https://api.llama.fi/overview/fees/solana?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true"),
 ("defillama", "https://api.llama.fi/summary/fees/jito-mev-tips?dataType=dailyFees"),
 ("defillama", "https://api.llama.fi/summary/fees/jito?dataType=dailyFees"),
 ("defillama", "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"),
 ("jito", "https://kobe.mainnet.jito.network/api/v1/mev_rewards"),
 ("jito", "https://kobe.mainnet.jito.network/api/v1/daily_mev_rewards"),
 ("jito", "https://kobe.mainnet.jito.network/api/v1/validators"),
 ("jito", "https://kobe.mainnet.jito.network/api/v1/jitosol_validators"),
 ("jito", "https://kobe.mainnet.jito.network/api/v1/stake_pool_stats"),
 ("jito", "https://bundles.jito.wtf/api/v1/bundles/tip_floor"),
 ("jito", "https://bundles.jito.wtf/api/v1/bundles/recent?limit=1000&sort=Time&asc=false"),
 ("jito", "https://bundles.jito.wtf/api/v1/bundles/recent?limit=1000&sort=Tip&asc=false&timeframe=Day"),
 ("jito", "https://bundles.jito.wtf/api/v1/bundles/recent?limit=1000&sort=Tip&asc=false&timeframe=Week"),
]
RPCS = [
 ("getEpochInfo", [{"commitment": "finalized"}]),
 ("getVoteAccounts", [{"commitment": "finalized"}]),
 ("getClusterNodes", []),
 ("getRecentPerformanceSamples", [60]),
 ("getRecentPrioritizationFees", []),
 ("getVersion", []),
]
def slug(u):
    s = re.sub(r"^https?://", "", u).strip("/"); return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:150]
rows = []
idx = os.path.join(OUT, "index.csv")
if os.path.exists(idx): rows = list(csv.DictReader(open(idx)))
done = {r["url"] + "|" + r["method"] for r in rows if r["http_status"] == "200"}
for grp, u in GETS:
    if u + "|GET" in done: continue
    t = now(); st, fn, note = None, "", ""
    for i in range(4):
        try:
            r = requests.get(u, headers=UA, timeout=120); st = r.status_code
            if st == 429 or st >= 500: time.sleep(5 * (i + 1)); continue
            if st == 200:
                fn = "%s__%s.json.gz" % (grp, slug(u)); open(os.path.join(OUT, fn), "wb").write(gzip.compress(r.content))
            else: note = r.text[:200]
            break
        except requests.RequestException as ex:
            note = str(ex)[:200]; time.sleep(5 * (i + 1))
    rows.append({"group": grp, "url": u, "method": "GET", "params": "", "fetched_at_utc": t, "http_status": st, "file": fn, "note": note})
    print(t, st, u, flush=True); time.sleep(1)
for m, p in RPCS:
    if RPC + "|" + m in done: continue
    t = now(); st, fn, note = None, "", ""
    for i in range(4):
        try:
            r = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": m, "params": p}, headers=UA, timeout=120); st = r.status_code
            if st == 429 or st >= 500: time.sleep(5 * (i + 1)); continue
            if st == 200:
                fn = "rpc__%s.json.gz" % m; open(os.path.join(OUT, fn), "wb").write(gzip.compress(r.content))
            break
        except requests.RequestException as ex:
            note = str(ex)[:200]; time.sleep(5 * (i + 1))
    rows.append({"group": "rpc", "url": RPC, "method": m, "params": json.dumps(p), "fetched_at_utc": t, "http_status": st, "file": fn, "note": note})
    print(t, st, m, flush=True); time.sleep(2)
# keep only the latest row per (url, method)
last = {}
for r in rows: last[r["url"] + "|" + r["method"]] = r
with open(idx, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["group", "url", "method", "params", "fetched_at_utc", "http_status", "file", "note"]); w.writeheader()
    w.writerows(last.values())
