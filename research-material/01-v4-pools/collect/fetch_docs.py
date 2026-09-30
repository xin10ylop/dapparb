#!/usr/bin/env python3
"""Fetch launchpad / Uniswap documentation and source files that state hook, factory or deployer addresses on Base.
For every URL: raw body saved verbatim (gzip) under ../hook-docs/raw/, plain text (HTML tags stripped, entities unescaped, each link target appended after its anchor text as " <href>") under
../hook-docs/text/, and every text line containing a 20-byte hex address written verbatim to
../hook-docs/doc-address-excerpts.csv.gz (url, fetched_utc, http_status, line_no, address, line_verbatim).
Fetch log (appended per fetch): ../hook-docs/fetch-log.jsonl (url, fetched_utc, http_status, bytes, sha256, raw_file, text_file).
Usage: python3 fetch_docs.py            (fetches the URL list below; re-fetches everything)"""
import csv, gzip, hashlib, html, json, os, re, time
from html.parser import HTMLParser
import requests

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
D = os.path.join(OUT, "hook-docs"); RAW = os.path.join(D, "raw"); TXT = os.path.join(D, "text")
for p in (RAW, TXT):
    os.makedirs(p, exist_ok=True)
os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}

URLS = [
    # Uniswap v4-core: hook permission flags (bit order used for the hf_* columns)
    "https://raw.githubusercontent.com/Uniswap/v4-core/main/src/libraries/Hooks.sol",
    "https://raw.githubusercontent.com/Uniswap/v4-core/main/src/types/PoolId.sol",
    "https://raw.githubusercontent.com/Uniswap/v4-core/main/src/libraries/LPFeeLibrary.sol",
    "https://raw.githubusercontent.com/Uniswap/v4-core/main/src/interfaces/IPoolManager.sol",
    "https://docs.uniswap.org/contracts/v4/deployments",
    # Uniswap routing allowlist (names hook constants per launchpad)
    "https://raw.githubusercontent.com/Uniswap/routing-api/main/lib/util/hooksAddressesAllowlist.ts",
    "https://raw.githubusercontent.com/Uniswap/hooklist/main/README.md",
    # Zora
    "https://docs.zora.co/llms.txt",
    "https://docs.zora.co/coins/contracts/hook-registry",
    "https://docs.zora.co/coins/contracts/hook",
    "https://docs.zora.co/coins/contracts/factory",
    "https://docs.zora.co/coins/contracts/architecture",
    "https://docs.zora.co/coins/contracts/liquidity-migration",
    "https://docs.zora.co/coins/contracts/creating-a-coin",
    "https://docs.zora.co/changelogs/coins",
    "https://raw.githubusercontent.com/ourzora/zora-protocol/main/packages/coins/src/deployment/ForkedCoinsAddresses.sol",
    "https://raw.githubusercontent.com/ourzora/zora-protocol/main/packages/coins-deployments/.github/PR_TEMPLATE_UPGRADE_INSTRUCTIONS.md",
    "https://raw.githubusercontent.com/ourzora/zora-protocol/main/packages/coins/test/LiquidityMigration.t.sol",
    # Clanker
    "https://clanker.gitbook.io/documentation/references/deployed-contracts",
    "https://clanker.gitbook.io/documentation/references/core-contracts",
    "https://clanker.gitbook.io/documentation/general/token-deployments",
    "https://raw.githubusercontent.com/clanker-devco/DOCS/main/references/deployed-contracts.md",
    "https://raw.githubusercontent.com/clanker-devco/v4-contracts/main/README.md",
    "https://raw.githubusercontent.com/clanker-devco/clanker-sdk/main/src/utils/clankers.ts",
    # Flaunch
    "https://raw.githubusercontent.com/flayerlabs/flaunch-gitbook/main/readme/for-aggregators.md",
    "https://raw.githubusercontent.com/flayerlabs/flaunch-sdk/main/src/addresses.ts",
    "https://raw.githubusercontent.com/flayerlabs/flaunchgg-contracts/main/README.md",
    # Doppler
    "https://docs.doppler.lol/reference/contract-addresses",
    "https://docs.doppler.lol/advanced-features/doppler-hooks",
    # Bunni
    "https://raw.githubusercontent.com/Bunniapp/bunni-v2/main/README.md",
]


class _T(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag == "a":
            self.href = dict(attrs).get("href")
        if tag in ("p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "pre", "table", "section", "td", "th", "code"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1
        if tag == "a" and getattr(self, "href", None) and not self.skip:
            # keep link targets (addresses are often only in explorer links); rendered as " <href>"
            self.out.append(" <%s>" % self.href)
            self.href = None
        if tag in ("td", "th"):
            self.out.append(" | ")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def to_text(body, ctype):
    if "html" in ctype or body.lstrip().startswith(("<!DOCTYPE", "<!doctype", "<html")):
        t = _T()
        t.feed(body)
        txt = "".join(t.out)
        lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in txt.split("\n")]
        return "\n".join(l for l in lines if l)
    return body


def slug(u):
    s = re.sub(r"^https?://", "", u)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    return s[:180]


def fetch(u):
    last = None
    for i in range(6):
        try:
            r = requests.get(u, headers=UA, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                last = r
                time.sleep(min(60, 3 * 2 ** i))
                continue
            return r
        except requests.RequestException as e:
            last = e
            time.sleep(min(60, 3 * 2 ** i))
    return last


ADDR = re.compile(r"0x[0-9a-fA-F]{40}(?![0-9a-fA-F])")


def main(urls=URLS):
    ex_path = os.path.join(D, "doc-address-excerpts.csv.gz")
    rows = []
    if os.path.exists(ex_path):
        with gzip.open(ex_path, "rt", newline="") as f:
            rd = csv.reader(f)
            next(rd)
            rows = [r for r in rd if r[0] not in set(urls)]
    logf = open(os.path.join(D, "fetch-log.jsonl"), "a")
    for u in urls:
        r = fetch(u)
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if not isinstance(r, requests.Response):
            logf.write(json.dumps({"url": u, "fetched_utc": ts, "error": repr(r)}) + "\n")
            print(ts, "ERROR", u, repr(r))
            continue
        body = r.content
        s = slug(u)
        rawf = os.path.join(RAW, s + ".gz")
        with gzip.open(rawf, "wb") as f:
            f.write(body)
        txt = to_text(r.text, r.headers.get("content-type", ""))
        txtf = os.path.join(TXT, s + ".txt")
        with open(txtf, "w") as f:
            f.write("# url: %s\n# fetched_utc: %s\n# http_status: %d\n\n" % (u, ts, r.status_code))
            f.write(txt)
        n = 0
        if r.status_code == 200:
            for i, line in enumerate(txt.split("\n"), 1):
                for m in ADDR.finditer(line):
                    a = m.group(0).lower()
                    st = max(0, m.start() - 300)
                    rows.append([u, ts, str(r.status_code), str(i), a, line[st:m.end() + 300]])
                    n += 1
        logf.write(json.dumps({"url": u, "fetched_utc": ts, "http_status": r.status_code, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                               "raw_file": os.path.relpath(rawf, OUT), "text_file": os.path.relpath(txtf, OUT), "address_mentions": n}) + "\n")
        logf.flush()
        print(ts, r.status_code, len(body), n, u, flush=True)
        time.sleep(0.5)
    with gzip.open(ex_path, "wt", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["url", "fetched_utc", "http_status", "line_no", "address", "line_verbatim"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
