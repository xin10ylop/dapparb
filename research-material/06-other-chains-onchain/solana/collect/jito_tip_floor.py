#!/usr/bin/env python3
"""Poll https://bundles.jito.wtf/api/v1/bundles/tip_floor every 60 s.
Appends one JSON line per poll to ../tip-floor.jsonl:
  {"poll_no", "fetched_at_utc", "http_status", "body": <verbatim parsed JSON or null>, "body_text": <raw text if not JSON>, "error"}
Resumable: counts existing lines and continues until --snapshots successful polls exist.
On completion writes /home/user/dapparb/research-material/.sentinels/SOL_JITO_TIPFLOOR.DONE (or .FAILED).
usage: python3 jito_tip_floor.py --snapshots 60 --interval 60
"""
import argparse, datetime, json, os, time, requests
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "tip-floor.jsonl")
SENT = "/home/user/dapparb/research-material/.sentinels/SOL_JITO_TIPFLOOR"
URL = "https://bundles.jito.wtf/api/v1/bundles/tip_floor"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--snapshots", type=int, default=60); ap.add_argument("--interval", type=float, default=60)
    a = ap.parse_args()
    ok, n = 0, 0
    if os.path.exists(OUT):
        for l in open(OUT):
            n += 1
            if json.loads(l).get("http_status") == 200: ok += 1
    fails_in_row = 0
    while ok < a.snapshots:
        t0 = time.time(); rec = {"poll_no": n + 1, "fetched_at_utc": now(), "url": URL}
        try:
            r = requests.get(URL, headers=UA, timeout=30)
            rec["http_status"] = r.status_code
            try: rec["body"] = r.json()
            except ValueError: rec["body"] = None; rec["body_text"] = r.text[:2000]
        except requests.RequestException as ex:
            rec["http_status"] = None; rec["error"] = str(ex)[:300]
        with open(OUT, "a") as f: f.write(json.dumps(rec, separators=(",", ":")) + "\n")
        n += 1
        if rec.get("http_status") == 200: ok += 1; fails_in_row = 0
        else: fails_in_row += 1
        print(rec["fetched_at_utc"], "poll", n, "status", rec.get("http_status"), "ok", ok, flush=True)
        if fails_in_row >= 30:
            open(SENT + ".FAILED", "w").write("30 consecutive failed polls; last: %s\n" % json.dumps(rec)); return
        time.sleep(max(0, a.interval - (time.time() - t0)))
    open(SENT + ".DONE", "w").write("%s %d successful polls (%d total) in %s\n" % (now(), ok, n, OUT))
if __name__ == "__main__":
    main()
