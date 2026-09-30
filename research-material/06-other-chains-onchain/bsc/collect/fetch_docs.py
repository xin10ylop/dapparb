#!/usr/bin/env python3
"""Fetch BSC ordering / MEV / builder / hard-fork / DEX documentation verbatim.

For every entry in DOCS:
  - raw response body saved under ../docs/raw/<id>.<ext> (html bodies gzip-compressed: .html.gz)
  - plain-text rendering saved as ../docs/<id>.txt (html -> text via html2text, no summarising; markdown / toml /
    json kept verbatim) with a header block: URL, fetched_at (UTC), HTTP status, final URL, sha256 of raw body
  - one row in ../docs/index.csv
Pages are fetched sequentially (1 in-flight request) with retries on 429/5xx/network errors.
Local git checkouts listed in LOCAL (shallow clones of public GitHub repos) are copied verbatim with commit hash.
Re-run: python3 fetch_docs.py   (overwrites; fetched_at changes)
"""
import csv
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import time

import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))
RAWD = os.path.join(DOCS, "raw")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

# question-line codes (see MANIFEST.md):
# Q1 V4 on Base | Q4 other chains live (BSC) | Q5 V4 launches / contested gaps / priority fee |
# Q6 BSC ordering via private builders | Q7 chain-wide studies | Q8 closing paragraph
BEP = "https://raw.githubusercontent.com/bnb-chain/BEPs/master/BEPs/"
BNBD = "https://docs.bnbchain.org/bnb-smart-chain/"
BLOG = "https://www.bnbchain.org/en/blog/"
DOCS_LIST = [
    # --- BNB Chain official: MEV / PBS docs (rendered site) ---
    ("bnbdocs-mev-overview", BNBD + "validator/mev/overview/", "BSC MEV Overview", "BNB Chain docs", "Q6"),
    ("bnbdocs-mev-user-guide", BNBD + "validator/mev/user-guide/", "User Guide - BSC MEV", "BNB Chain docs", "Q6"),
    ("bnbdocs-mev-validator-integration", BNBD + "validator/mev/validator-integration/",
     "Integration Guide for Validator - BSC MEV", "BNB Chain docs", "Q6"),
    ("bnbdocs-mev-builder-integration", BNBD + "validator/mev/builder-integration/",
     "Integration Guide for Builder - BSC MEV", "BNB Chain docs", "Q6"),
    ("bnbdocs-mev-faqs", BNBD + "validator/mev/faqs/", "FAQs - BSC MEV", "BNB Chain docs", "Q6"),
    ("bnbdocs-evn-overview", BNBD + "validator/evn/overview/", "Enhanced Validator Network overview", "BNB Chain docs", "Q6"),
    ("bnbdocs-evn-faqs", BNBD + "validator/evn/faqs/", "EVN FAQs", "BNB Chain docs", "Q6"),
    ("bnbdocs-faq-lorentz", BNBD + "faq/lorentz-hard-fork-upgrade/", "Lorentz hard fork upgrade FAQ", "BNB Chain docs", "Q4;Q6"),
    ("bnbdocs-bsc-overview", BNBD + "overview/", "BNB Smart Chain overview", "BNB Chain docs", "Q4"),
    ("bnbdocs-bsc-introduction", BNBD + "introduction/", "BNB Smart Chain introduction", "BNB Chain docs", "Q4"),
    # --- BEPs ---
    ("bep-067", BEP + "BEP67.md", "BEP-67: Price-based Order", "bnb-chain/BEPs", "Q5;Q6"),
    ("bep-126", BEP + "BEP126.md", "BEP-126: Introduce Fast Finality Mechanism", "bnb-chain/BEPs", "Q6"),
    ("bep-322", BEP + "BEP322.md", "BEP-322: Builder API Specification for BNB Smart Chain", "bnb-chain/BEPs", "Q6"),
    ("bep-341", BEP + "BEP-341.md", "BEP-341: Validators can produce consecutive blocks", "bnb-chain/BEPs", "Q6"),
    ("bep-520", BEP + "BEP-520.md", "BEP-520: Short Block Interval Phase One: 1.5 seconds", "bnb-chain/BEPs", "Q4;Q6"),
    ("bep-524", BEP + "BEP-524.md", "BEP-524: Short Block Interval Phase Two: 0.75 seconds", "bnb-chain/BEPs", "Q4;Q6"),
    ("bep-563", BEP + "BEP-563.md", "BEP-563: Enhanced Validator Network", "bnb-chain/BEPs", "Q6"),
    ("bep-564", BEP + "BEP-564.md", "BEP-564: bsc/2 - New Block Fetching Messages", "bnb-chain/BEPs", "Q6"),
    ("bep-590", BEP + "BEP-590.md", "BEP-590: Extended Voting Rules for Fast Finality Stability", "bnb-chain/BEPs", "Q6"),
    ("bep-619", BEP + "BEP-619.md", "BEP-619: Short Block Interval Phase Three: 0.45 Seconds", "bnb-chain/BEPs", "Q4;Q6"),
    ("bep-648", BEP + "BEP-648.md", "BEP-648: Enhanced Fast Finality via In-Memory Voting Pool", "bnb-chain/BEPs", "Q6"),
    ("bep-658", BEP + "BEP-658.md", "BEP-658: Hardfork Meta-Osaka/Mendel", "bnb-chain/BEPs", "Q4;Q6"),
    ("bep-673", BEP + "BEP-673.md", "BEP-673: Hardfork Meta-Pasteur", "bnb-chain/BEPs", "Q4;Q6"),
    ("bep-675", BEP + "BEP-675.md", "BEP-675: Builder-Proposed Block with Validator Blind Signing (Draft)", "bnb-chain/BEPs", "Q6"),
    ("bep-718", BEP + "BEP-718.md", "BEP-718: Hardfork Meta-Jenner (Draft)", "bnb-chain/BEPs", "Q4;Q6"),
    ("beps-readme", "https://raw.githubusercontent.com/bnb-chain/BEPs/master/README.md", "BEPs index (README)",
     "bnb-chain/BEPs", "Q6"),
    # --- BSC client: hard-fork schedule ---
    ("bsc-changelog", "https://raw.githubusercontent.com/bnb-chain/bsc/master/CHANGELOG.md", "bsc CHANGELOG.md",
     "bnb-chain/bsc", "Q4;Q6"),
    ("bsc-params-config-go", "https://raw.githubusercontent.com/bnb-chain/bsc/master/params/config.go",
     "bsc params/config.go (hard-fork activation times)", "bnb-chain/bsc", "Q4;Q6"),
    ("bsc-builder-readme", "https://raw.githubusercontent.com/bnb-chain/bsc-builder/master/README.md",
     "bsc-builder README", "bnb-chain/bsc-builder", "Q6"),
    # --- BNB Chain blog ---
    ("blog-key-changes-mev-strategy", BLOG + "key-changes-in-bnb-smart-chains-mev-strategy",
     "Key Changes In BNB Smart Chain's MEV Strategy", "BNB Chain Blog", "Q6"),
    ("blog-mev-faqs", BLOG + "bnb-chain-mev-faqs", "BNB Chain MEV FAQs", "BNB Chain Blog", "Q6"),
    ("blog-exploring-mev-landscape", BLOG + "exploring-bnb-chains-maximal-extractable-value-mev-landscape-solutions",
     "Exploring BNB Chain's MEV Landscape & Solutions", "BNB Chain Blog", "Q6"),
    ("blog-unlocking-mev-guide", BLOG + "unlocking-the-potential-of-mev-on-bnb-chain-a-guide-for-builders-and-validators",
     "Unlocking the Potential of MEV on BNB Chain", "BNB Chain Blog", "Q6"),
    ("blog-good-will-alliance", BLOG + "bnb-good-will-alliance", "BNB Good Will Alliance", "BNB Chain Blog", "Q6"),
    ("blog-infrastructure-levelled-up", BLOG + "bnb-chains-infrastructure-just-levelled-up-heres-what-changed",
     "BNB Chain's Infrastructure Just Levelled Up, Here's What Changed", "BNB Chain Blog", "Q6"),
    ("blog-maxwell", BLOG + "bnb-chain-announces-maxwell-hardfork-bsc-moves-to-0-75-second-block-times",
     "BNB Chain Announces Maxwell Hardfork: BSC Moves to 0.75-Second Block Times", "BNB Chain Blog", "Q4;Q6"),
    ("blog-fermi", BLOG + "fermi-hard-fork-accelerates-bsc-to-0-45-second-block-times",
     "Fermi Hard Fork Accelerates BSC to 0.45-Second Block Times", "BNB Chain Blog", "Q4;Q6"),
    ("blog-osaka-mendel", BLOG + "osaka-mendel-hard-fork-strengthening-bnb-chain-after-sub-second-speed-gains",
     "Osaka/Mendel Hard Fork", "BNB Chain Blog", "Q4;Q6"),
    # --- builders' own docs ---
    ("48club-docs-faq", "https://docs.48.club/", "48 Club docs F.A.Q.", "48 Club", "Q6"),
    ("48club-puissant-builder", "https://docs.48.club/puissant-builder", "Puissant Builder", "48 Club", "Q6"),
    ("48club-puissant-send-bundle", "https://docs.48.club/puissant-builder/send-bundle", "Puissant Builder: Send Bundle",
     "48 Club", "Q5;Q6"),
    ("48club-puissant-auction-feed", "https://docs.48.club/puissant-builder/auction-transaction-feed",
     "Puissant Builder: Auction Transaction Feed", "48 Club", "Q6"),
    ("blockrazor-bsc-block-builder", "https://blockrazor.gitbook.io/blockrazor/bsc/block-builder",
     "BlockRazor: BSC Block Builder", "BlockRazor", "Q6"),
    ("blockrazor-send-bundle", "https://blockrazor.gitbook.io/blockrazor/block-builder/block-builder/send-bundle",
     "BlockRazor: Send Bundle", "BlockRazor", "Q5;Q6"),
    ("blockrazor-call-bundle", "https://blockrazor.gitbook.io/blockrazor/builder/bsc/call-bundle",
     "BlockRazor: Call Bundle", "BlockRazor", "Q6"),
    ("bloxroute-bsc-overview", "https://docs.bloxroute.com/bsc/overview", "bloXroute BSC Overview", "bloXroute", "Q6"),
    ("bloxroute-bsc-bundle-submission", "https://docs.bloxroute.com/bsc/submit-bundles/bsc-bundle-submission",
     "bloXroute BSC Bundle Submission", "bloXroute", "Q5;Q6"),
    ("blocksmith-docs", "https://docs.blocksmith.org/", "Blocksmith docs (General)", "Blocksmith", "Q6"),
    ("blocksmith-send-bundle", "https://docs.blocksmith.org/bsc-builder/api/eth_sendbundle", "Blocksmith eth_sendBundle",
     "Blocksmith", "Q6"),
    ("nodereal-builder", "https://docs.nodereal.io/docs/nodereal-builder", "NodeReal Builder", "NodeReal", "Q6"),
    ("nodereal-bundle-api-marketplace", "https://nodereal.io/api-marketplace/bsc-bundle-service-api",
     "NodeReal BSC MEV (Bundle Service) API", "NodeReal", "Q6"),
    ("jetbldr-home", "https://jetbldr.xyz/", "Jetbldr website", "Jetbldr", "Q6"),
    ("flashblock-home", "https://www.flashblock.trade", "Flashblock website", "Flashblock", "Q6"),
    # --- DEX landscape ---
    ("defillama-overview-dexs-bsc", "https://api.llama.fi/overview/dexs/bsc", "DefiLlama DEX overview, chain=bsc (raw JSON)",
     "DefiLlama", "Q4"),
    ("pancakeswap-v2-addresses", "https://developer.pancakeswap.finance/contracts/v2/addresses",
     "PancakeSwap v2 addresses", "PancakeSwap developer docs", "Q4"),
    ("pancakeswap-v3-addresses", "https://developer.pancakeswap.finance/contracts/v3/addresses",
     "PancakeSwap v3 addresses", "PancakeSwap developer docs", "Q4"),
    ("pancakeswap-infinity-addresses", "https://developer.pancakeswap.finance/contracts/infinity/resources/addresses",
     "PancakeSwap Infinity addresses", "PancakeSwap developer docs", "Q4;Q1"),
    ("pancakeswap-infinity-overview", "https://developer.pancakeswap.finance/contracts/infinity/overview",
     "PancakeSwap Infinity overview", "PancakeSwap developer docs", "Q4;Q1"),
    ("uniswap-v4-deployments", "https://docs.uniswap.org/contracts/v4/deployments", "Uniswap v4 deployments",
     "Uniswap docs", "Q1;Q4"),
    ("uniswap-v3-bnb-deployments", "https://docs.uniswap.org/contracts/v3/reference/deployments/bnb-deployments",
     "Uniswap v3 BNB deployments", "Uniswap docs", "Q4"),
    # --- BSC token launchpads (launch flow) ---
    ("fourmeme-protocol-integration", "https://four-meme.gitbook.io/four.meme/protocol-integration",
     "Four.meme Protocol Integration", "Four.meme", "Q5;Q4"),
    ("flap-docs-home", "https://docs.flap.sh/", "Flap docs", "Flap", "Q5;Q4"),
]

# (id, local path, repo url, path in repo, title, publisher, question lines)
LOCAL = [
    ("gwa-builder-list-toml", "/home/user/bnb-chain/good-will-alliance/mev-info/bsc-mainnet/builder-list.toml",
     "https://github.com/bnb-chain/good-will-alliance", "mev-info/bsc-mainnet/builder-list.toml",
     "Good Will Alliance BSC mainnet builder list", "bnb-chain/good-will-alliance", "Q6"),
    ("gwa-readme", "/home/user/bnb-chain/good-will-alliance/README.md", "https://github.com/bnb-chain/good-will-alliance",
     "README.md", "Good Will Alliance README", "bnb-chain/good-will-alliance", "Q6"),
    ("bsc-mev-info-builder-list-toml", "/home/user/bnb-chain/bsc-mev-info/mainnet/builder-list.toml",
     "https://github.com/bnb-chain/bsc-mev-info", "mainnet/builder-list.toml",
     "bsc-mev-info BSC mainnet builder list (header says deprecated)", "bnb-chain/bsc-mev-info", "Q6"),
    ("bsc-mev-info-validator-list-toml", "/home/user/bnb-chain/bsc-mev-info/mainnet/validator-list.toml",
     "https://github.com/bnb-chain/bsc-mev-info", "mainnet/validator-list.toml",
     "bsc-mev-info BSC mainnet validator list", "bnb-chain/bsc-mev-info", "Q6"),
    ("bsc-mev-info-readme", "/home/user/bnb-chain/bsc-mev-info/README.md", "https://github.com/bnb-chain/bsc-mev-info",
     "README.md", "bsc-mev-info README", "bnb-chain/bsc-mev-info", "Q6"),
] + [
    (f"bnbdocs-src-{p.replace('/', '-')[:-3]}", f"/home/user/bnb-chain/bnb-chain.github.io/docs/bnb-smart-chain/{p}",
     "https://github.com/bnb-chain/bnb-chain.github.io", f"docs/bnb-smart-chain/{p}",
     f"BNB Chain docs markdown source: {p}", "bnb-chain/bnb-chain.github.io", "Q6")
    for p in ["validator/mev/overview.md", "validator/mev/user-guide.md", "validator/mev/validator-integration.md",
              "validator/mev/builder-integration.md", "validator/mev/faqs.md", "validator/evn/overview.md",
              "validator/evn/faqs.md", "validator/evn/best-practice.md", "faq/lorentz-hard-fork-upgrade.md",
              "overview.md", "introduction.md"]
]


def html_to_text(html):
    import html2text
    h = html2text.HTML2Text()
    h.body_width = 0
    h.ignore_images = True
    h.ignore_emphasis = False
    h.protect_links = True
    return h.handle(html)


def stated_date(body, url):
    for pat in (r'"datePublished"\s*:\s*"([^"]+)"', r'property="article:published_time"\s+content="([^"]+)"',
                r'content="([^"]+)"\s+property="article:published_time"', r'(?im)^\s*[-*|]?\s*created:?\s*\|?\s*([0-9]{4}-[0-9]{2}-[0-9]{2})',
                r'"dateModified"\s*:\s*"([^"]+)"'):
        m = re.search(pat, body)
        if m:
            return m.group(1)
    return ""


def fetch(url):
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"})
    last = None
    for attempt in range(6):
        try:
            r = s.get(url, timeout=60, allow_redirects=True)
            if r.status_code in (429,) or r.status_code >= 500:
                last = (r.status_code, r.url, r.content, r.headers.get("content-type", ""))
                time.sleep(min(60, 3 * 2 ** attempt))
                continue
            return r.status_code, r.url, r.content, r.headers.get("content-type", "")
        except Exception as e:
            last = (None, url, repr(e).encode(), "")
            time.sleep(min(60, 3 * 2 ** attempt))
    return last


def main():
    os.makedirs(RAWD, exist_ok=True)
    rows = []
    for did, url, title, pub, ql in DOCS_LIST:
        code, final, body, ctype = fetch(url)
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        sha = hashlib.sha256(body).hexdigest()
        text_body = body.decode("utf-8", "replace")
        is_html = "html" in ctype or text_body.lstrip()[:15].lower().startswith(("<!doctype html", "<html"))
        if is_html:
            rawf = os.path.join(RAWD, did + ".html.gz")
            with gzip.open(rawf, "wb") as f:
                f.write(body)
            try:
                txt = html_to_text(text_body)
            except Exception as e:
                txt = f"[html2text failed: {e!r}]"
        else:
            ext = ".json" if "json" in ctype else (".md" if url.endswith(".md") else (".go" if url.endswith(".go") else ".txt"))
            rawf = os.path.join(RAWD, did + ext + (".gz" if len(body) > 1_000_000 else ""))
            if rawf.endswith(".gz"):
                with gzip.open(rawf, "wb") as f:
                    f.write(body)
            else:
                with open(rawf, "wb") as f:
                    f.write(body)
            txt = text_body if not ("json" in ctype and len(body) > 1_000_000) else \
                "[large JSON body: see raw file; not duplicated as text]"
        header = (f"URL: {url}\nFINAL_URL: {final}\nTITLE: {title}\nPUBLISHER: {pub}\nFETCHED_AT_UTC: {now}\n"
                  f"HTTP_STATUS: {code}\nCONTENT_TYPE: {ctype}\nRAW_SHA256: {sha}\nRAW_FILE: raw/{os.path.basename(rawf)}\n"
                  f"CONVERSION: {'html2text (verbatim text of the page, markup removed)' if is_html else 'verbatim'}\n"
                  + "=" * 78 + "\n")
        txtf = os.path.join(DOCS, did + ".txt")
        with open(txtf, "w") as f:
            f.write(header + txt)
        note = "" if code == 200 else f"HTTP {code}: page not retrieved (see raw file for error body)"
        rows.append({"id": did, "url": url, "title": title, "publisher": pub,
                     "date_stated": stated_date(text_body, url) if code == 200 else "", "fetched_at": now,
                     "http_status": code, "question_lines": ql, "text_file": os.path.basename(txtf),
                     "raw_file": "raw/" + os.path.basename(rawf), "raw_bytes": len(body), "raw_sha256": sha,
                     "note": note})
        print(did, code, len(body), flush=True)
        time.sleep(1.0)
    for did, path, repo, rpath, title, pub, ql in LOCAL:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        repo_dir = subprocess.check_output(["git", "-C", os.path.dirname(path), "rev-parse", "--show-toplevel"], text=True).strip()
        commit = subprocess.check_output(["git", "-C", repo_dir, "log", "-1", "--format=%H"], text=True).strip()
        cdate = subprocess.check_output(["git", "-C", repo_dir, "log", "-1", "--format=%cI"], text=True).strip()
        body = open(path, "rb").read()
        ext = os.path.splitext(path)[1]
        rawf = os.path.join(RAWD, did + ext)
        shutil.copyfile(path, rawf)
        url = f"{repo}/blob/{commit}/{rpath}"
        header = (f"URL: {url}\nTITLE: {title}\nPUBLISHER: {pub}\nFETCHED_AT_UTC: {now} (git clone --depth 1 of {repo})\n"
                  f"GIT_COMMIT: {commit} (commit date {cdate})\nRAW_SHA256: {hashlib.sha256(body).hexdigest()}\n"
                  f"RAW_FILE: raw/{os.path.basename(rawf)}\nCONVERSION: verbatim\n" + "=" * 78 + "\n")
        with open(os.path.join(DOCS, did + ".txt"), "w") as f:
            f.write(header + body.decode("utf-8", "replace"))
        rows.append({"id": did, "url": url, "title": title, "publisher": pub,
                     "date_stated": f"repo HEAD commit date {cdate}", "fetched_at": now, "http_status": "git",
                     "question_lines": ql, "text_file": did + ".txt", "raw_file": "raw/" + os.path.basename(rawf),
                     "raw_bytes": len(body), "raw_sha256": hashlib.sha256(body).hexdigest(), "note": ""})
    with open(os.path.join(DOCS, "index.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("index rows", len(rows))


if __name__ == "__main__":
    main()
