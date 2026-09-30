#!/usr/bin/env python3
"""DEX landscape raw material for BSC.
1. DefiLlama https://api.llama.fi/overview/dexs/bsc  -> ../dex/defillama-overview-dexs-bsc.json.gz (raw body, verbatim)
   + ../dex/defillama-overview-dexs-bsc.meta.json (url, fetched_at, http status, sha256)
2. Verbatim excerpts (exact line ranges) of the address tables in the doc pages fetched by fetch_docs.py
   -> ../dex/dex-address-excerpts.txt  (each block: source text file, URL, fetched_at, line range, verbatim lines)
Run fetch_docs.py first.
"""
import gzip
import hashlib
import json
import os
import re
import time

import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, "..", "dex"))
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
LLAMA = "https://api.llama.fi/overview/dexs/bsc"

# (label, doc text file, start regex, number of lines to copy from the match)
EXCERPTS = [
    ("PancakeSwap v2 factory (PancakeFactory) per chain", "pancakeswap-v2-addresses.txt", r"^Core\[\]", 20),
    ("PancakeSwap v2 router (PancakeRouter)", "pancakeswap-v2-addresses.txt", r"View PancakeRouter.sol", 18),
    ("PancakeSwap v3 core (factory, pool deployer)", "pancakeswap-v3-addresses.txt", r"^Core\[\]", 8),
    ("PancakeSwap v3 periphery", "pancakeswap-v3-addresses.txt", r"^Periphery\[\]", 16),
    ("PancakeSwap v3 smart router", "pancakeswap-v3-addresses.txt", r"^Smart Router\[\]", 10),
    ("PancakeSwap Infinity core (Vault, CLPoolManager, BinPoolManager)", "pancakeswap-infinity-addresses.txt",
     r"^PCS Infinity have been deployed", 12),
    ("PancakeSwap Infinity periphery + universal router", "pancakeswap-infinity-addresses.txt",
     r"^From <https://github.com/pancakeswap/infinity-periphery>", 22),
    ("Uniswap sdk-core BNB addresses (v2/v3/v4 incl. v4PoolManagerAddress)", "uniswap-sdk-core-addresses-ts.txt",
     r"^// BNB v3 addresses", 16),
    ("Uniswap sdk-core V2 factory per chain (BNB line)", "uniswap-sdk-core-addresses-ts.txt",
     r"\[ChainId\.BNB\]: '0x8909", 1),
    ("Uniswap sdk-core V2 router per chain (BNB line)", "uniswap-sdk-core-addresses-ts.txt",
     r"\[ChainId\.BNB\]: '0x4752", 1),
    ("Four.meme contract addresses", "fourmeme-docs-integration-guide.txt", r"TokenManager2 \(V2\) \| `0x", 1),
    ("Four.meme contract table", "fourmeme-docs-integration-guide.txt", r"(?i)^\|\s*Contract", 12),
    ("Flap BNB Chain deployed contracts", "flap-deployed-addresses-main-md.txt", r"^### BNB Chain", 14),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    s = requests.Session()
    s.headers["User-Agent"] = UA
    code, body = None, b""
    for attempt in range(6):
        try:
            r = s.get(LLAMA, timeout=120)
            code, body = r.status_code, r.content
            if code == 200:
                break
        except Exception as e:
            code, body = None, repr(e).encode()
        time.sleep(5 * 2 ** attempt)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with gzip.open(os.path.join(OUT, "defillama-overview-dexs-bsc.json.gz"), "wb") as f:
        f.write(body)
    meta = {"url": LLAMA, "fetched_at_utc": now, "http_status": code, "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(), "note": "raw response body, gzip-compressed, not modified"}
    json.dump(meta, open(os.path.join(OUT, "defillama-overview-dexs-bsc.meta.json"), "w"), indent=1)
    print("defillama", code, len(body))
    out = []
    for label, fn, rx, n in EXCERPTS:
        p = os.path.join(DOCS, fn)
        if not os.path.exists(p):
            out.append(f"### {label}\nSOURCE_FILE: docs/{fn}\nNOT FOUND (doc not fetched)\n")
            continue
        txt = open(p).read()
        url = re.search(r"^URL: (.+)$", txt, re.M).group(1)
        fetched = re.search(r"^FETCHED_AT_UTC: (.+)$", txt, re.M).group(1)
        lines = txt.splitlines()
        hdr_end = next(i for i, l in enumerate(lines) if l.startswith("=" * 78))
        hit = None
        for i in range(hdr_end + 1, len(lines)):
            if re.search(rx, lines[i]):
                hit = i
                break
        if hit is None:
            out.append(f"### {label}\nSOURCE_FILE: docs/{fn}\nURL: {url}\nANCHOR NOT FOUND: {rx}\n")
            continue
        seg = lines[hit:hit + n]
        out.append(f"### {label}\nSOURCE_FILE: docs/{fn} (lines {hit + 1}-{hit + len(seg)})\nURL: {url}\n"
                   f"FETCHED_AT_UTC: {fetched}\n---8<--- verbatim\n" + "\n".join(seg) + "\n---8<---\n")
    with open(os.path.join(OUT, "dex-address-excerpts.txt"), "w") as f:
        f.write("Verbatim excerpts of DEX / launchpad contract address tables relevant to BSC.\n"
                "Each block copies exact consecutive lines of the saved doc text file named in SOURCE_FILE.\n\n")
        f.write("\n".join(out))
    print("excerpts", len(out))


if __name__ == "__main__":
    main()
