#!/usr/bin/env python3
"""DefiLlama USD reference prices for every mint in ../token-mints-seen.csv.gz plus coingecko:solana.
GET https://coins.llama.fi/prices/historical/<ts>/<coin,coin,...>?searchWidth=6h with ts = blockTime of the middle
slot of the window (from ../slots.csv.gz), 40 coins per request, <= 1 request in flight, 1.5 s spacing.
Output ../prices-defillama-historical.jsonl.gz: one line per request {"batch", "url", "timestamp_requested",
"fetched_at_utc", "http_status", "coins_requested": [...], "body": <verbatim JSON>}.
Checkpoint: ../data/prices.parts/<batch>.json. Coins absent from a body = DefiLlama returned no price for them (not an error).
usage: python3 prices.py
"""
import csv, datetime, gzip, json, os, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); DATA = os.path.join(BASE, "data")
PARTS = os.path.join(DATA, "prices.parts"); OUT = os.path.join(BASE, "prices-defillama-historical.jsonl.gz")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
def main():
    os.makedirs(PARTS, exist_ok=True)
    rows = [r for r in csv.DictReader(gzip.open(os.path.join(BASE, "slots.csv.gz"), "rt")) if r["status"] == "ok"]
    ts = int(rows[len(rows) // 2]["block_time"])
    mints = [r["mint"] for r in csv.DictReader(gzip.open(os.path.join(BASE, "token-mints-seen.csv.gz"), "rt"))]
    coins = ["coingecko:solana"] + ["solana:" + m for m in mints]
    batches = [coins[i:i + 40] for i in range(0, len(coins), 40)]
    failed = []
    for b, cs in enumerate(batches):
        p = os.path.join(PARTS, "%05d.json" % b)
        if os.path.exists(p): continue
        url = "https://coins.llama.fi/prices/historical/%d/%s?searchWidth=6h" % (ts, ",".join(cs))
        rec = None; delay = 3
        for i in range(8):
            t = now()
            try:
                r = requests.get(url, headers=UA, timeout=60)
                if r.status_code == 429 or r.status_code >= 500:
                    print(t, "http", r.status_code, "batch", b, flush=True); time.sleep(delay); delay = min(delay * 2, 120); continue
                rec = {"batch": b, "url": url, "timestamp_requested": ts, "fetched_at_utc": t, "http_status": r.status_code,
                       "coins_requested": cs, "body": r.json() if r.status_code == 200 else None}
                if r.status_code != 200: rec["body_text"] = r.text[:500]
                break
            except (requests.RequestException, ValueError) as ex:
                print(t, "err", ex, flush=True); time.sleep(delay); delay = min(delay * 2, 120)
        if rec is None or rec["http_status"] != 200:
            failed.append(b); print(now(), "FAILED batch", b, flush=True); continue
        json.dump(rec, open(p + ".tmp", "w"), separators=(",", ":")); os.replace(p + ".tmp", p)
        print(now(), "batch", b, "/", len(batches), "prices", len(rec["body"].get("coins", {})), flush=True)
        time.sleep(1.5)
    with gzip.open(OUT + ".tmp", "wt") as f:
        for b in range(len(batches)):
            p = os.path.join(PARTS, "%05d.json" % b)
            if os.path.exists(p): f.write(open(p).read().strip() + "\n")
    os.replace(OUT + ".tmp", OUT)
    if failed:
        open(os.path.join(DATA, "prices-gaps.csv"), "w").write("batch\n" + "\n".join(map(str, failed)) + "\n"); raise SystemExit(3)
if __name__ == "__main__":
    main()
