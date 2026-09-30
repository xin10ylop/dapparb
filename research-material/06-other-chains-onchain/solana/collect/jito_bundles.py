#!/usr/bin/env python3
"""Jito bundles that landed in every slot of the pinned window (state/pin.json).
GET https://bundles.jito.wtf/api/v1/bundles/slot/<slot>  (public endpoint used by explorer.jito.wtf; the
endpoint ignores limit/offset query parameters - one response per slot).
Output ../data/jito-bundles-by-slot.jsonl.gz: one line per slot
  {"slot", "url", "fetched_at_utc", "http_status", "body": <verbatim parsed JSON: list of bundles
   {bundleId, slot, validator, tippers[], landedTipLamports, landedCu, blockIndex, timestamp, txSignatures[]}> }
Checkpoint: ../data/jito-bundles-by-slot.parts/<slot>.json (one per slot); the .jsonl.gz is (re)assembled from them.
Failures after retries -> ../data/jito-bundles-gaps.csv. <= 2 requests in flight, >= 0.25 s between request starts.
usage: python3 jito_bundles.py
"""
import datetime, gzip, json, os, random, threading, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); DATA = os.path.join(BASE, "data")
PARTS = os.path.join(DATA, "jito-bundles-by-slot.parts"); OUT = os.path.join(DATA, "jito-bundles-by-slot.jsonl.gz")
GAPS = os.path.join(DATA, "jito-bundles-gaps.csv")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
lock = threading.Lock(); last = [0.0]
def get(url):
    delay = 2.0
    for i in range(10):
        with lock:
            w = last[0] + 0.25 - time.time()
            if w > 0: time.sleep(w)
            last[0] = time.time()
        try:
            r = requests.get(url, headers=UA, timeout=60)
        except requests.RequestException as ex:
            print(now(), "net", url, str(ex)[:150], flush=True); time.sleep(delay + random.random()); delay = min(delay * 2, 120); continue
        if r.status_code == 429 or r.status_code >= 500:
            print(now(), "http", r.status_code, url, flush=True); time.sleep(delay + random.random()); delay = min(delay * 2, 120); continue
        return r
    return None
def main():
    os.makedirs(PARTS, exist_ok=True)
    pin = json.load(open(os.path.join(HERE, "state", "pin.json")))
    slots = list(range(pin["start_slot"], pin["end_slot"] + 1))
    todo = [s for s in slots if not os.path.exists(os.path.join(PARTS, "%d.json" % s))]
    print(now(), "todo", len(todo), flush=True)
    q = list(todo); ql = threading.Lock(); cnt = [0]
    def worker():
        while True:
            with ql:
                if not q: return
                s = q.pop(0)
            url = "https://bundles.jito.wtf/api/v1/bundles/slot/%d" % s
            t = now(); r = get(url)
            if r is None:
                with open(GAPS, "a") as f: f.write("%d,retries exhausted,%s\n" % (s, now()))
                continue
            try: body = r.json()
            except ValueError: body = None
            rec = {"slot": s, "url": url, "fetched_at_utc": t, "http_status": r.status_code, "body": body}
            if body is None: rec["body_text"] = r.text[:2000]
            p = os.path.join(PARTS, "%d.json" % s)
            json.dump(rec, open(p + ".tmp", "w"), separators=(",", ":")); os.replace(p + ".tmp", p)
            with ql:
                cnt[0] += 1
                if cnt[0] % 50 == 0: print(now(), "done", cnt[0], flush=True)
    th = [threading.Thread(target=worker) for _ in range(2)]; [t.start() for t in th]; [t.join() for t in th]
    missing = [s for s in slots if not os.path.exists(os.path.join(PARTS, "%d.json" % s))]
    with gzip.open(OUT + ".tmp", "wt") as f:
        for s in slots:
            p = os.path.join(PARTS, "%d.json" % s)
            if os.path.exists(p): f.write(open(p).read().strip() + "\n")
    os.replace(OUT + ".tmp", OUT)
    print(now(), "assembled", len(slots) - len(missing), "missing", len(missing), flush=True)
    if missing: raise SystemExit(3)
if __name__ == "__main__":
    main()
