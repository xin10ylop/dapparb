#!/usr/bin/env python3
"""Build ../dex-programs.csv and ../jito-tip-accounts.csv from official sources, with evidence.

1. Fetches every source URL below verbatim into ../docs/program-id-sources/<slug>.(body.gz) and checks that the
   program id string occurs in the fetched body (column id_found_in_source).
2. Fetches Jupiter's program-id-to-label maps (lite-api.jup.ag and api.jup.ag, swap/v1) verbatim; every entry is
   added as a row (source_kind=jupiter_program_id_to_label_api). The map is Jupiter's list of venues its router
   quotes/routes through.
3. Jito tip accounts: getTipAccounts on the mainnet block engine (verbatim response saved) + docs page check.
4. On-chain check: getMultipleAccounts(encoding base64, dataSlice 0/0) on api.mainnet-beta.solana.com for every
   program id -> executable flag and owner (loader).
usage: python3 programs.py
"""
import csv, datetime, gzip, hashlib, json, os, re, time, requests
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE)
SRC = os.path.join(BASE, "docs", "program-id-sources"); os.makedirs(SRC, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}
RPC = "https://api.mainnet-beta.solana.com"
def now(): return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

RAY = "https://docs.raydium.io/reference/program-addresses"
NAMED = [  # (program_id, name, [official source urls])
 ("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8", "Raydium AMM v4", [RAY, "https://docs.raydium.io/products/amm-v4"]),
 ("CPMMoo8L3F4NbTegBCKVNunggL7H1ZpdTHKxQB5qKP1C", "Raydium CPMM", [RAY, "https://docs.raydium.io/products/cpmm"]),
 ("CAMMCzo5YL8w4VFF8KVHrK22GGUsp5VTaW7grrKgrWqK", "Raydium CLMM", [RAY, "https://docs.raydium.io/products/clmm"]),
 ("LanMV9sAd7wArD4vJFi2qDdfnVhFxYSUg6eADduJ3uj", "Raydium LaunchLab", [RAY, "https://docs.raydium.io/products/launchlab"]),
 ("routeUGWgWzqBWFcrCfv8tritsqukccJPu3q5GPP3xS", "Raydium AMM Routing", [RAY]),
 ("5quBtoiQqxF9Jv6KYKctB59NT3gtJD2Y65kdnB1Uev3h", "Raydium Stable Swap AMM", [RAY]),
 ("whirLbMiicVdio4qvUfM5KAg6Ct8VwpYzGff3uctyCc", "Orca Whirlpool", [
     "https://raw.githubusercontent.com/orca-so/whirlpools/main/programs/whirlpool/src/lib.rs",
     "https://raw.githubusercontent.com/orca-so/whirlpools/main/README.md"]),
 ("LBUZKhRxPF3XUpBCjp4YzTKgLccjZhTSDM9YuVaPwxo", "Meteora DLMM", [
     "https://raw.githubusercontent.com/MeteoraAg/dlmm-sdk/main/programs/lb_clmm/src/lib.rs",
     "https://raw.githubusercontent.com/MeteoraAg/dlmm-sdk/main/README.md"]),
 ("Eo7WjKq67rjJQSZxS6z3YkapzY3eMj6Xy8X5EQVn5UaB", "Meteora DAMM v1 (Dynamic AMM)", [
     "https://raw.githubusercontent.com/MeteoraAg/damm-v1-sdk/main/README.md",
     "https://raw.githubusercontent.com/MeteoraAg/damm-v1-sdk/main/programs/dynamic-amm/src/lib.rs",
     "https://raw.githubusercontent.com/MeteoraAg/dynamic-amm-sdk/main/README.md",
     "https://raw.githubusercontent.com/MeteoraAg/dynamic-amm-sdk/main/programs/dynamic-amm/src/lib.rs"]),
 ("cpamdpZCGKUy5JxQXB4dcpGPiikHawvSWAd6mEn1sGG", "Meteora DAMM v2 (CP-AMM)", [
     "https://raw.githubusercontent.com/MeteoraAg/damm-v2/main/programs/cp-amm/src/lib.rs",
     "https://raw.githubusercontent.com/MeteoraAg/damm-v2/main/README.md"]),
 ("dbcij3LWUppWqq96dh6gJWwBifmcGfLSB5D4DuSMaqN", "Meteora Dynamic Bonding Curve", [
     "https://docs.meteora.ag/developer-guides/dbc",
     "https://raw.githubusercontent.com/MeteoraAg/dynamic-bonding-curve/main/programs/dynamic-bonding-curve/src/lib.rs"]),
 ("PhoeNiXZ8ByJGLkxNfZRnkUfjvmuYqLR89jjFHGqdXY", "Phoenix v1", [
     "https://raw.githubusercontent.com/Ellipsis-Labs/phoenix-v1/master/README.md",
     "https://raw.githubusercontent.com/Ellipsis-Labs/phoenix-v1/master/src/lib.rs"]),
 ("opnb2LAfJYbRMAHHvqjCwQxanZn7ReEHp1k81EohpZb", "OpenBook v2", [
     "https://raw.githubusercontent.com/openbook-dex/openbook-v2/master/README.md",
     "https://raw.githubusercontent.com/openbook-dex/openbook-v2/master/programs/openbook-v2/src/lib.rs"]),
 ("srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX", "OpenBook v1 (Serum fork)", [
     "https://raw.githubusercontent.com/openbook-dex/program/master/README.md"]),
 ("2wT8Yq49kHgDzXuPxZSaeLaH1qbmGXtEyPy64bL7aD3c", "Lifinity Swap v2", [
     "https://unpkg.com/@lifinity/sdk-v2@2.0.3/lib/network.js"]),
 ("EewxydAPCCVuNEyrVN68PuSYdQ7wKn27V9Gjeoi8dy3S", "Lifinity Swap v1", ["https://unpkg.com/@lifinity/sdk@0.2.25/lib/network.js"]),
 ("pAMMBay6oceH9fJKBRHGP5D4bD4sWpmSwMn52FMfXEA", "PumpSwap (pump.fun AMM)", [
     "https://raw.githubusercontent.com/pump-fun/pump-public-docs/main/idl/pump_amm.json",
     "https://raw.githubusercontent.com/pump-fun/pump-public-docs/main/README.md"]),
 ("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P", "pump.fun bonding curve", [
     "https://raw.githubusercontent.com/pump-fun/pump-public-docs/main/idl/pump.json",
     "https://raw.githubusercontent.com/pump-fun/pump-public-docs/main/README.md"]),
 ("JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4", "Jupiter Aggregator v6", [
     "https://raw.githubusercontent.com/jup-ag/instruction-parser/main/README.md",
     "https://raw.githubusercontent.com/jup-ag/jupiter-cpi/main/src/lib.rs",
     "https://raw.githubusercontent.com/jup-ag/jupiter-cpi/main/README.md"]),
 ("JUP4Fb2cqiRUcaTHdrPC8h2gNsA2ETXiPDD33WcGuJB", "Jupiter Aggregator v4", [
     "https://raw.githubusercontent.com/jup-ag/instruction-parser/main/README.md"]),
 ("j1o2qRpjcyUwEvwtcfhEQefh773ZgjxcVRry7LDqg5X", "Jupiter Limit Order v2", [
     "https://dev.jup.ag/docs/"]),
 ("jupoNjAxXgZ4rjzxzPMP4oxduvQsQtZzyknqvzYNrNu", "Jupiter Limit Order (v1)", [
     "https://unpkg.com/@jup-ag/limit-order-sdk@0.1.10/dist/index.js"]),
 ("DCA265Vj8a9CEuX1eb1LWRnDT7uK6q1xMipnNyatn23M", "Jupiter DCA", [
     "https://unpkg.com/@jup-ag/dca-sdk@3.0.1/dist/index.js"]),
 ("6m2CDdhRgxpH4WjvdzxAYbGxwdGUz5MziiL5jek2kBma", "OKX DEX Aggregation Router v2", [
     "https://raw.githubusercontent.com/okxlabs/Web3-DEX-Router-Solana-V1/main/README.md",
     "https://github.com/okxlabs/Web3-DEX-Router-Solana-V1"]),
 ("DF1ow4tspfHX9JwWJsAb9epbkA8hmpSEAtxXy1V27QBH", "DFlow Aggregator v4", [
     "https://docs.dflow.net/docs/introduction", "https://pond.dflow.net/introduction"]),
 ("SSwpkEEcbUqx4vtoEByFjSkhKdCT862DNVb52nZg1UZ", "Saber Stable Swap", [
     "https://raw.githubusercontent.com/saber-hq/stable-swap/master/README.md"]),
 ("MNFSTqtC93rEfYHB6hF82sKdZpUDFWkViLByLd1k1Ms", "Manifest", [
     "https://raw.githubusercontent.com/CKS-Systems/manifest/main/README.md"]),
 ("5ocnV1qiCgaQR8Jb8xWnVbApfaygJ8tNoZfgPwsgx9kx", "Sanctum Infinity", [
     "https://raw.githubusercontent.com/igneous-labs/S/master/README.md"]),
]
JUP_MAPS = ["https://lite-api.jup.ag/swap/v1/program-id-to-label", "https://api.jup.ag/swap/v1/program-id-to-label"]
JITO_DOCS = ["https://docs.jito.wtf/lowlatencytxnsend/",
             "https://raw.githubusercontent.com/jito-labs/jito-docs/main/docs/source/lowlatencytxnsend.md"]
JITO_BE = "https://mainnet.block-engine.jito.wtf/api/v1/getTipAccounts"

def slug(u):
    s = re.sub(r"^https?://", "", u).strip("/"); return re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:150]
fetched = {}
index_rows = []
def fetch(u):
    if u in fetched: return fetched[u]
    t = now(); body, st, note = None, None, ""
    for i in range(3):
        try:
            r = requests.get(u, headers=UA, timeout=45); st = r.status_code
            if r.status_code == 429 or r.status_code >= 500: time.sleep(3 * (i + 1)); continue
            body = r.content if r.status_code == 200 else None; break
        except requests.RequestException as ex:
            note = str(ex)[:200]; time.sleep(3 * (i + 1))
    if body is not None:
        open(os.path.join(SRC, slug(u) + ".body.gz"), "wb").write(gzip.compress(body))
    index_rows.append({"url": u, "http_status": st, "fetched_at_utc": t, "file": (slug(u) + ".body.gz") if body is not None else "",
                       "sha256": hashlib.sha256(body).hexdigest() if body is not None else "", "note": note})
    fetched[u] = (body.decode("utf-8", "replace") if body is not None else None, st, t)
    return fetched[u]

def main():
    rows = {}
    for pid, name, urls in NAMED:
        found = []
        tried = []
        for u in urls:
            body, st, t = fetch(u); tried.append("%s(%s)" % (u, st))
            if body is not None and pid in body: found.append(u)
        rows[pid] = {"program_id": pid, "name": name, "source_url": " ".join(found) if found else "",
                     "source_kind": "official_docs_or_repo" if found else "",
                     "id_found_in_source": "1" if found else "0", "sources_tried": " ".join(tried),
                     "jupiter_label": ""}
    # Jupiter maps
    labels = {}
    for u in JUP_MAPS:
        body, st, t = fetch(u)
        if body:
            for k, v in json.loads(body).items():
                labels.setdefault(k, {})[u] = v
    for pid, d in labels.items():
        lab = " / ".join(sorted(set(d.values())))
        if pid in rows:
            rows[pid]["jupiter_label"] = lab
            if rows[pid]["id_found_in_source"] == "0":
                rows[pid]["source_url"] = " ".join(sorted(d.keys())); rows[pid]["source_kind"] = "jupiter_program_id_to_label_api"
                rows[pid]["id_found_in_source"] = "1"
        else:
            rows[pid] = {"program_id": pid, "name": lab, "source_url": " ".join(sorted(d.keys())),
                         "source_kind": "jupiter_program_id_to_label_api", "id_found_in_source": "1",
                         "sources_tried": "", "jupiter_label": lab}
    # Jito tip accounts
    for u in JITO_DOCS: fetch(u)
    be = requests.post(JITO_BE, json={"jsonrpc": "2.0", "id": 1, "method": "getTipAccounts", "params": []}, headers=UA, timeout=30)
    be_t = now()
    json.dump({"url": JITO_BE, "method": "getTipAccounts", "fetched_at_utc": be_t, "http_status": be.status_code, "body": be.json()},
              open(os.path.join(SRC, "jito-block-engine-getTipAccounts.json"), "w"), indent=1)
    tips = be.json()["result"]
    # on-chain check
    ids = list(rows.keys()) + tips
    chain = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        r = requests.post(RPC, json={"jsonrpc": "2.0", "id": 1, "method": "getMultipleAccounts",
                                     "params": [chunk, {"encoding": "base64", "dataSlice": {"offset": 0, "length": 0}, "commitment": "finalized"}]},
                          headers=UA, timeout=60).json()
        ctx_slot = r["result"]["context"]["slot"]
        for pid, acc in zip(chunk, r["result"]["value"]):
            chain[pid] = {"exists": acc is not None, "executable": (acc or {}).get("executable"), "owner": (acc or {}).get("owner"),
                          "lamports": (acc or {}).get("lamports"), "slot": ctx_slot}
        time.sleep(1)
    chk_t = now()
    with open(os.path.join(BASE, "dex-programs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["program_id", "name", "source_url", "source_kind", "id_found_in_source", "jupiter_label",
                    "onchain_exists", "onchain_executable", "onchain_owner", "onchain_checked_slot", "onchain_checked_at_utc", "sources_tried"])
        for pid in sorted(rows, key=lambda k: (rows[k]["source_kind"] != "official_docs_or_repo", rows[k]["name"].lower())):
            r = rows[pid]; c = chain.get(pid, {})
            w.writerow([pid, r["name"], r["source_url"], r["source_kind"], r["id_found_in_source"], r["jupiter_label"],
                        c.get("exists"), c.get("executable"), c.get("owner"), c.get("slot"), chk_t, r["sources_tried"]])
    docs_found = {}
    for u in JITO_DOCS:
        body = fetched[u][0] or ""
        docs_found[u] = body
    with open(os.path.join(BASE, "jito-tip-accounts.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tip_account", "source_url", "found_in_getTipAccounts", "found_in_docs_urls", "onchain_exists", "onchain_owner", "onchain_lamports", "onchain_checked_slot", "fetched_at_utc"])
        for t in tips:
            fd = " ".join(u for u, b in docs_found.items() if t in b); c = chain.get(t, {})
            w.writerow([t, JITO_BE + " (POST getTipAccounts); " + JITO_DOCS[0], "1", fd, c.get("exists"), c.get("owner"), c.get("lamports"), c.get("slot"), be_t])
    with open(os.path.join(SRC, "index.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["url", "http_status", "fetched_at_utc", "file", "sha256", "note"]); w.writeheader(); w.writerows(index_rows)
    print("programs", len(rows), "not found in source:", [r["name"] for r in rows.values() if r["id_found_in_source"] == "0"])
    print("tips", tips)

if __name__ == "__main__":
    main()
