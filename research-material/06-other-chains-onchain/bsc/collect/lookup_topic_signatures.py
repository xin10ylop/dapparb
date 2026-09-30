#!/usr/bin/env python3
"""Look up text signatures for every topic0 in census/topic0-inventory.csv.gz (or --topics-file, one topic0
per line / first TSV column) in the public signature database api.openchain.xyz (mirror of the Sourcify/Samczsun
4byte database). Output: ../census/topic0-signatures.csv.gz with columns
  topic0, signatures (all names returned, '|'-joined, verbatim), has_verified_contract ('|'-joined per name),
  lookup_source, looked_up_at_utc
A topic0 with no match gets an empty signatures field. This is a lookup only (a hash -> text mapping from a
third-party database); a match is a keccak preimage and does not by itself say which contract emitted it.
"""
import argparse
import csv
import gzip
import json
import os
import time

import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "census")
API = "https://api.openchain.xyz/signature-database/v1/lookup"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics-file")
    ap.add_argument("--out", default=os.path.join(CENSUS, "topic0-signatures.csv.gz"))
    a = ap.parse_args()
    topics = []
    if a.topics_file:
        for line in open(a.topics_file):
            t = line.split("\t")[0].strip()
            if t.startswith("0x") and len(t) == 66:
                topics.append(t.lower())
    else:
        with gzip.open(os.path.join(CENSUS, "topic0-inventory.csv.gz"), "rt") as f:
            for r in csv.DictReader(f):
                if r["topic0"].startswith("0x") and len(r["topic0"]) == 66:
                    topics.append(r["topic0"].lower())
    res = {}
    s = requests.Session()
    s.headers["User-Agent"] = UA
    B = 60
    for i in range(0, len(topics), B):
        batch = topics[i:i + B]
        for attempt in range(8):
            try:
                r = s.get(API, params={"event": ",".join(batch), "filter": "false"}, timeout=60)
                if r.status_code == 200 and r.json().get("ok"):
                    ev = r.json()["result"]["event"]
                    for t in batch:
                        res[t] = ev.get(t) or []
                    break
                print("http", r.status_code, r.text[:200], flush=True)
            except Exception as e:
                print("err", repr(e)[:200], flush=True)
            time.sleep(2 ** attempt)
        else:
            for t in batch:
                res[t] = None  # lookup failed
        time.sleep(0.3)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with gzip.open(a.out + ".tmp", "wt", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["topic0", "signatures", "has_verified_contract", "lookup_source", "looked_up_at_utc"])
        for t in topics:
            v = res.get(t)
            if v is None:
                w.writerow([t, "", "", "LOOKUP_FAILED " + API, now])
            else:
                w.writerow([t, "|".join(x["name"] for x in v), "|".join(str(x.get("hasVerifiedContract")) for x in v),
                            API, now])
    os.replace(a.out + ".tmp", a.out)
    print("topics", len(topics), "with_match", sum(1 for v in res.values() if v), "failed",
          sum(1 for v in res.values() if v is None))


if __name__ == "__main__":
    main()
