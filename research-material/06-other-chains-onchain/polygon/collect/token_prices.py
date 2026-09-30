#!/usr/bin/env python3
"""Token metadata and USD reference prices for the ERC-20 tokens that appear in a chain's census candidates.

Reads <chain_dir>/window.json and <chain_dir>/candidates-*.jsonl.gz (produced by census.py) and writes:
  tokens-onchain-meta.csv.gz          one row per ERC-20 contract that emitted a Transfer log (topic0 0xddf252ad..,
                                      3 topics) inside a candidate tx: raw eth_call results of decimals()/symbol()/name()
                                      at block tag 'latest' (time in token_prices.fetch.json) + derived decodings
  prices-defillama-historical.jsonl.gz one line per DefiLlama coins API request (URL, UTC fetch time, HTTP status,
                                      requested timestamp, raw JSON body) for the window start / middle / end timestamps
  native-price-chart-defillama.json   raw DefiLlama 5-minute chart of the native gas token(s) across the window
  token_prices.fetch.json             run metadata (counts, endpoints, times, errors)
Sentinel: .sentinels/EVM_TOKENPRICES_<CHAIN>.DONE / .FAILED

usage: python3 token_prices.py --chain <chain> --out <chain_dir>
"""
import argparse, csv, datetime, glob, gzip, json, os, sys, time, traceback
import requests

SENTINEL_DIR = "/home/user/dapparb/research-material/.sentinels"
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "content-type": "application/json"}
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
CFG = {
    "arbitrum": dict(rpc=["https://arbitrum-one-rpc.publicnode.com", "https://arbitrum.drpc.org"], llama="arbitrum",
                     native=["coingecko:ethereum"]),
    "optimism": dict(rpc=["https://optimism-rpc.publicnode.com", "https://optimism.drpc.org"], llama="optimism",
                     native=["coingecko:ethereum"]),
    "unichain": dict(rpc=["https://unichain-rpc.publicnode.com", "https://unichain.drpc.org"], llama="unichain",
                     native=["coingecko:ethereum"]),
    "ethereum": dict(rpc=["https://ethereum-rpc.publicnode.com", "https://eth.drpc.org"], llama="ethereum",
                     native=["coingecko:ethereum"]),
    "polygon": dict(rpc=["https://polygon-bor-rpc.publicnode.com", "https://polygon.drpc.org"], llama="polygon",
                    native=["coingecko:polygon-ecosystem-token", "coingecko:matic-network", "coingecko:ethereum"]),
}
SEL = {"decimals": "0x313ce567", "symbol": "0x95d89b41", "name": "0x06fdde03"}


def now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def post(url, payload):
    for i in range(8):
        try:
            r = requests.post(url, data=json.dumps(payload), headers=UA, timeout=90)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 * (i + 1)); continue
            j = r.json()
            if isinstance(payload, list) and isinstance(j, dict):
                time.sleep(2 * (i + 1)); continue
            return j
        except (requests.RequestException, ValueError):
            time.sleep(2 * (i + 1))
    raise RuntimeError("rpc failed %s" % url)


def get(url):
    last = None
    for i in range(8):
        try:
            r = requests.get(url, headers=UA, timeout=90)
            last = r
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(5 * (i + 1)); continue
            return r
        except requests.RequestException:
            time.sleep(5 * (i + 1))
    return last


def dec_uint(h):
    if not h or h == "0x" or len(h) < 66:
        return ""
    return str(int(h[2:66], 16))


def dec_str(h):
    """ABI string, or bytes32 (e.g. MKR) -> text with backslash escapes for undecodable bytes"""
    if not h or h == "0x":
        return ""
    b = bytes.fromhex(h[2:])
    try:
        if len(b) >= 64:
            off = int.from_bytes(b[0:32], "big")
            if off + 32 <= len(b):
                n = int.from_bytes(b[off:off + 32], "big")
                if off + 32 + n <= len(b) and n < 10000:
                    return b[off + 32:off + 32 + n].decode("utf-8", errors="backslashreplace")
        if len(b) == 32:
            return b.rstrip(b"\x00").decode("utf-8", errors="backslashreplace")
    except Exception:  # noqa
        pass
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", required=True, choices=sorted(CFG))
    ap.add_argument("--out", required=True)
    ap.add_argument("--smoke", action="store_true", help="test run: write sentinel under the out dir instead")
    a = ap.parse_args()
    cfg = CFG[a.chain]
    d = os.path.abspath(a.out)
    sentinel = os.path.join(SENTINEL_DIR if not a.smoke else os.path.abspath(a.out), "EVM_TOKENPRICES_%s" % a.chain.upper())
    meta = {"chain": a.chain, "started_at_utc": now(), "rpc": cfg["rpc"], "errors": []}
    try:
        win = json.load(open(os.path.join(d, "window.json")))
        assert win.get("status") == "complete", "census not complete"
        counts = {}
        for p in sorted(glob.glob(os.path.join(d, "candidates-*.jsonl.gz"))):
            with gzip.open(p, "rt") as f:
                for line in f:
                    rec = json.loads(line)
                    for lg in rec["logs"]:
                        t = lg.get("topics") or []
                        if len(t) == 3 and t[0].lower() == TRANSFER:
                            ad = lg["address"].lower()
                            counts[ad] = counts.get(ad, 0) + 1
        tokens = sorted(counts)
        meta["n_tokens"] = len(tokens)
        print(now(), "tokens", len(tokens), flush=True)
        res = {}
        B = 20
        # eth_call at "latest" (publicnode treats calls at an explicit recent block number as archive requests);
        # decimals/symbol/name are read-only metadata. Items that error on the first endpoint are retried on the next.
        todo = [(t, fn) for t in tokens for fn in SEL]
        for url in cfg["rpc"]:
            if not todo:
                break
            failed = []
            for i in range(0, len(todo), 3 * B):
                chunk = todo[i:i + 3 * B]
                payload = [{"jsonrpc": "2.0", "id": j, "method": "eth_call", "params": [{"to": t, "data": SEL[fn]}, "latest"]}
                           for j, (t, fn) in enumerate(chunk)]
                try:
                    got = post(url, payload)
                except RuntimeError as ex:
                    meta["errors"].append(str(ex))
                    for t, fn in chunk:
                        res.setdefault(t, {})[fn] = ("", "batch failed at %s" % url, url)
                    failed.extend(chunk)
                    continue
                byid = {x.get("id"): x for x in got}
                for j, (t, fn) in enumerate(chunk):
                    x = byid.get(j)
                    if x is None:
                        res.setdefault(t, {})[fn] = ("", "missing in batch response", url); failed.append((t, fn))
                    elif "error" in x:
                        e = ("%s" % x["error"])[:200]
                        res.setdefault(t, {})[fn] = ("", e, url)
                        if "revert" not in e.lower():
                            failed.append((t, fn))
                    else:
                        res.setdefault(t, {})[fn] = (x.get("result") or "", "", url)
                time.sleep(0.1)
            todo = failed
        meta["eth_call_block"] = "latest"
        meta["eth_call_time_utc"] = now()
        with gzip.open(os.path.join(d, "tokens-onchain-meta.csv.gz"), "wt", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["token_address", "n_transfer_logs_in_candidates", "decimals_raw", "symbol_raw", "name_raw",
                        "decimals_error", "symbol_error", "name_error", "call_block_tag", "call_endpoint",
                        "decimals_derived", "symbol_derived", "name_derived"])
            for t in tokens:
                r = res.get(t, {})
                dr, de, du = r.get("decimals", ("", "not requested", ""))
                sr, se, su = r.get("symbol", ("", "not requested", ""))
                nr, ne, nu = r.get("name", ("", "not requested", ""))
                eps = ";".join(sorted(set(x for x in (du, su, nu) if x)))
                w.writerow([t, counts[t], dr, sr, nr, de, se, ne, "latest", eps, dec_uint(dr), dec_str(sr), dec_str(nr)])
        print(now(), "onchain meta written", flush=True)
        # DefiLlama historical prices at window start / mid / end
        ts_list = [win["start_timestamp"], (win["start_timestamp"] + win["end_timestamp"]) // 2, win["end_timestamp"]]
        coins = ["%s:%s" % (cfg["llama"], t) for t in tokens] + cfg["native"]
        n_req = 0
        with gzip.open(os.path.join(d, "prices-defillama-historical.jsonl.gz"), "wt") as f:
            for ts in ts_list:
                for i in range(0, len(coins), 40):
                    url = "https://coins.llama.fi/prices/historical/%d/%s" % (ts, ",".join(coins[i:i + 40]))
                    t0 = now()
                    r = get(url)
                    n_req += 1
                    body = None
                    try:
                        body = r.json() if r is not None else None
                    except ValueError:
                        body = {"_non_json_body": r.text[:2000]}
                    f.write(json.dumps({"url": url, "fetched_at_utc": t0, "http_status": r.status_code if r is not None else None,
                                        "timestamp_requested": ts, "response": body}, separators=(",", ":")) + "\n")
                    time.sleep(0.4)
        meta["defillama_requests"] = n_req
        meta["price_timestamps_requested"] = ts_list
        span = int((win["end_timestamp"] - win["start_timestamp"]) / 300) + 2
        url = "https://coins.llama.fi/chart/%s?start=%d&span=%d&period=5m" % (",".join(cfg["native"]), win["start_timestamp"], span)
        r = get(url)
        open(os.path.join(d, "native-price-chart-defillama.json"), "wb").write(r.content if r is not None else b"")
        meta["native_chart_url"] = url
        meta["native_chart_http_status"] = r.status_code if r is not None else None
        meta["finished_at_utc"] = now()
        json.dump(meta, open(os.path.join(d, "token_prices.fetch.json"), "w"), indent=1)
        if os.path.exists(sentinel + ".FAILED"):
            os.remove(sentinel + ".FAILED")
        open(sentinel + ".DONE", "w").write("%s token meta + prices done %s tokens=%d\n" % (a.chain, meta["finished_at_utc"], len(tokens)))
        print(now(), "done", json.dumps({k: v for k, v in meta.items() if k != "errors"}), flush=True)
    except Exception as ex:
        traceback.print_exc()
        open(sentinel + ".FAILED", "w").write("%s token prices failed %s: %r\n" % (a.chain, now(), ex))
        sys.exit(1)


if __name__ == "__main__":
    main()
