#!/usr/bin/env python3
"""Selection step for the additional L2 censuses (added 2026-10-01).

1. Fetches the DefiLlama DEX overview for all chains
   (https://api.llama.fi/overview/dexs?excludeTotalDataChart=true) and stores the raw body gzip-compressed as
   ../defillama-overview-dexs-all-chains.json.gz (+ ../defillama-overview-dexs-all-chains.fetch.json).
2. Fetches the per-chain DefiLlama DEX overview of each candidate chain
   (https://api.llama.fi/overview/dexs/<slug>?excludeTotalDataChart=true), one JSON line per request with the raw
   body, into ../defillama-overview-dexs-candidates.jsonl.gz.
3. Probes each candidate's public HTTP JSON-RPC endpoints: eth_chainId, eth_blockNumber and
   eth_getBlockReceipts(head - 5); one JSON line per endpoint into ../rpc-receipts-probe-candidates.jsonl.gz.
4. Writes ../selection.csv: one row per candidate chain with the volume numbers, the probe outcome and whether the
   chain was selected. Rule: candidates ordered by breakdown24h_sum_derived (descending); the first MAX_SELECT
   chains with at least one endpoint that served eth_getBlockReceipts are selected.

The candidate list is fixed (given by the task); no other chain of the overview is considered.
usage: python3 select_l2_chains.py   (run from this directory)
"""
import csv, datetime, gzip, hashlib, json, os, sys, time
from decimal import Decimal
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)  # 06-other-chains-onchain/
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "content-type": "application/json"}
MAX_SELECT = 6
OVERVIEW_URL = "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true"
# (DefiLlama chain name as in allChains, breakdown24h key, per-chain slug, census dir, chain id, public RPC endpoints)
CANDIDATES = [
    ("Linea", "linea", "linea", "linea", 59144,
     ["https://rpc.linea.build", "https://linea-rpc.publicnode.com", "https://linea.drpc.org"]),
    ("Scroll", "scroll", "scroll", "scroll", 534352,
     ["https://rpc.scroll.io", "https://scroll-rpc.publicnode.com", "https://scroll.drpc.org"]),
    ("ZKsync Era", "era", "zksync-era", "zksync", 324,
     ["https://mainnet.era.zksync.io", "https://zksync.drpc.org"]),
    ("Blast", "blast", "blast", "blast", 81457,
     ["https://rpc.blast.io", "https://blast-rpc.publicnode.com", "https://blast.drpc.org"]),
    ("Mantle", "mantle", "mantle", "mantle", 5000,
     ["https://rpc.mantle.xyz", "https://mantle-rpc.publicnode.com", "https://mantle.drpc.org"]),
    ("Ink", "ink", "ink", "ink", 57073,
     ["https://rpc-gel.inkonchain.com", "https://rpc-qnd.inkonchain.com", "https://ink-rpc.publicnode.com",
      "https://ink.drpc.org"]),
    ("Soneium", "soneium", "soneium", "soneium", 1868,
     ["https://rpc.soneium.org", "https://soneium-rpc.publicnode.com", "https://soneium.drpc.org"]),
    ("World Chain", "wc", "world-chain", "worldchain", 480,
     ["https://worldchain-mainnet.g.alchemy.com/public", "https://480.rpc.thirdweb.com",
      "https://worldchain-mainnet.gateway.tenderly.co", "https://worldchain.drpc.org",
      "https://sparkling-autumn-dinghy.worldchain-mainnet.quiknode.pro"]),
    ("Abstract", "abstract", "abstract", "abstract", 2741,
     ["https://api.mainnet.abs.xyz", "https://abstract.drpc.org"]),
    ("Taiko", "taiko", "taiko", "taiko", 167000,
     ["https://rpc.mainnet.taiko.xyz", "https://taiko-rpc.publicnode.com", "https://taiko.drpc.org"]),
    ("Mode", "mode", "mode", "mode", 34443,
     ["https://mainnet.mode.network", "https://mode.drpc.org"]),
]


def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url):
    last = None
    for i in range(6):
        t = now()
        try:
            r = requests.get(url, headers=UA, timeout=180)
        except requests.RequestException as ex:
            last = (t, None, str(ex)[:300]); time.sleep(5 * (i + 1)); continue
        if r.status_code == 429 or r.status_code >= 500:
            last = (t, r, None); time.sleep(5 * (i + 1)); continue
        return t, r, None
    return last


def rpc(url, method, params):
    t = now()
    try:
        r = requests.post(url, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}),
                          headers=UA, timeout=60)
    except requests.RequestException as ex:
        return {"at_utc": t, "http_status": None, "exception": str(ex)[:300]}
    out = {"at_utc": t, "http_status": r.status_code}
    try:
        j = r.json()
    except ValueError:
        out["non_json_body"] = r.text[:500]
        return out
    if isinstance(j, dict) and "error" in j:
        out["error"] = j["error"]
    if isinstance(j, dict) and "result" in j:
        out["result"] = j["result"]
    return out


def main():
    # 1. all-chains overview
    t, r, ex = get(OVERVIEW_URL)
    if r is None or r.status_code != 200:
        raise SystemExit("overview fetch failed: %s %s" % (t, ex or (r.status_code if r is not None else None)))
    body = r.content
    with open(os.path.join(OUT, "defillama-overview-dexs-all-chains.json.gz"), "wb") as f:
        f.write(gzip.compress(body, 9))
    meta = {"url": OVERVIEW_URL, "fetched_at_utc": t, "http_status": r.status_code, "bytes_uncompressed": len(body),
            "sha256_uncompressed": hashlib.sha256(body).hexdigest(),
            "stored_as": "defillama-overview-dexs-all-chains.json.gz (gzip of the unmodified response body)"}
    json.dump(meta, open(os.path.join(OUT, "defillama-overview-dexs-all-chains.fetch.json"), "w"), indent=1)
    print(now(), "overview", json.dumps(meta), flush=True)
    ov = json.loads(body, parse_float=Decimal, parse_int=Decimal)
    sums = {}
    for p in ov["protocols"]:
        for ck, v in (p.get("breakdown24h") or {}).items():
            for _, val in (v or {}).items():
                s = sums.setdefault(ck, [Decimal(0), 0])
                s[0] += Decimal(val) if val is not None else Decimal(0)
                s[1] += 1
    # 2. per-chain overviews
    per = {}
    with gzip.open(os.path.join(OUT, "defillama-overview-dexs-candidates.jsonl.gz"), "wt") as f:
        for name, key, slug, d, cid, eps in CANDIDATES:
            url = "https://api.llama.fi/overview/dexs/%s?excludeTotalDataChart=true" % slug
            t, r, ex = get(url)
            resp = None
            if r is not None:
                try:
                    resp = json.loads(r.content, parse_float=Decimal, parse_int=Decimal)
                except ValueError:
                    resp = None
            per[name] = (url, t, r.status_code if r is not None else None, resp)
            line = {"chain": name, "url": url, "fetched_at_utc": t, "http_status": r.status_code if r is not None else None,
                    "exception": ex, "response": json.loads(r.content) if resp is not None else (r.text[:2000] if r is not None else None)}
            f.write(json.dumps(line, separators=(",", ":")) + "\n")
            print(now(), "per-chain", name, line["http_status"], resp.get("total24h") if isinstance(resp, dict) else None, flush=True)
            time.sleep(0.5)
    # 3. RPC probe
    probe = {}
    with gzip.open(os.path.join(OUT, "rpc-receipts-probe-candidates.jsonl.gz"), "wt") as f:
        for name, key, slug, d, cid, eps in CANDIDATES:
            for u in eps:
                rec = {"chain": name, "expected_chain_id": cid, "endpoint": u}
                rec["eth_chainId"] = rpc(u, "eth_chainId", [])
                rec["eth_blockNumber"] = rpc(u, "eth_blockNumber", [])
                bn = rec["eth_blockNumber"].get("result")
                ok = False
                if isinstance(bn, str) and bn.startswith("0x"):
                    b = int(bn, 16) - 5
                    rec["probe_block"] = b
                    x = rpc(u, "eth_getBlockReceipts", [hex(b)])
                    res = x.pop("result", None)
                    if isinstance(res, list):
                        x["result_derived"] = {"n_receipts": len(res),
                                               "receipt_block_numbers": sorted(set(int(y["blockNumber"], 16) for y in res if y.get("blockNumber"))),
                                               "receipt_fields_of_first": sorted(res[0].keys()) if res else []}
                        ok = x.get("http_status") == 200 and all(int(y["blockNumber"], 16) == b for y in res if y.get("blockNumber"))
                    elif res is not None:
                        x["result_unexpected_type"] = str(res)[:500]
                    rec["eth_getBlockReceipts"] = x
                cidr = rec["eth_chainId"].get("result")
                rec["chain_id_matches_derived"] = isinstance(cidr, str) and cidr.startswith("0x") and int(cidr, 16) == cid
                rec["receipts_served_derived"] = bool(ok and rec["chain_id_matches_derived"])
                probe.setdefault(name, []).append(rec)
                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
                print(now(), "probe", name, u, rec["receipts_served_derived"], flush=True)
    # 4. selection.csv
    rows = []
    for name, key, slug, d, cid, eps in CANDIDATES:
        s = sums.get(key, [Decimal(0), 0])
        url, t, st, resp = per[name]
        okeps = [x["endpoint"] for x in probe[name] if x["receipts_served_derived"]]
        bad = [x["endpoint"] for x in probe[name] if not x["receipts_served_derived"]]
        rows.append({"defillama_chain": name, "defillama_breakdown24h_key": key, "in_overview_allChains": str(name in ov["allChains"]).lower(),
                     "breakdown24h_sum_derived": str(s[0]), "breakdown24h_entries_derived": s[1],
                     "per_chain_total24h": str(resp.get("total24h")) if isinstance(resp, dict) else "",
                     "per_chain_url": url, "per_chain_fetched_at_utc": t, "chain_id": cid,
                     "receipts_endpoints_ok": ";".join(okeps), "receipts_endpoints_not_ok": ";".join(bad),
                     "census_dir": d})
    rows.sort(key=lambda x: -Decimal(x["breakdown24h_sum_derived"]))
    nsel = 0
    for i, x in enumerate(rows):
        x["volume_rank_derived"] = i + 1
        sel = bool(x["receipts_endpoints_ok"]) and nsel < MAX_SELECT
        if sel:
            nsel += 1
        x["selected"] = str(sel).lower()
        if not sel:
            x["census_dir"] = ""
    cols = ["volume_rank_derived", "defillama_chain", "defillama_breakdown24h_key", "in_overview_allChains",
            "breakdown24h_sum_derived", "breakdown24h_entries_derived", "per_chain_total24h", "per_chain_url",
            "per_chain_fetched_at_utc", "chain_id", "receipts_endpoints_ok", "receipts_endpoints_not_ok", "selected",
            "census_dir"]
    with open(os.path.join(OUT, "selection.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(now(), "selection.csv written; selected:", [x["defillama_chain"] for x in rows if x["selected"] == "true"], flush=True)


if __name__ == "__main__":
    main()
