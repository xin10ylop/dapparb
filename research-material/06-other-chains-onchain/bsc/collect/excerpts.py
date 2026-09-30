#!/usr/bin/env python3
"""Write ../docs/excerpts.txt: exact consecutive-line excerpts from the saved doc text files (no editing), for the
passages most often needed: BSC hard-fork activation times, block-interval BEP abstracts, header time encoding,
builder-payment / bundle-auction rules. Each block names source file, URL, fetch time and line range.
Run after fetch_docs.py.
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))

EX = [
    ("BSC mainnet hard-fork activation blocks/times (params/config.go BSCChainConfig)", "bsc-params-config-go.txt",
     r"BSCChainConfig = &ChainConfig\{", 50),
    ("BEP-520 (Lorentz, 1.5 s) abstract", "bep-520.txt", r"(?i)^#+\s*1\.?\s*Summary", 12),
    ("BEP-520 millisecond timestamp in MixDigest", "bep-520.txt", r"Regarding the representation of block time", 16),
    ("BEP-524 (Maxwell, 0.75 s) summary", "bep-524.txt", r"(?i)^#+\s*1\.?\s*Summary", 12),
    ("BEP-619 (Fermi, 0.45 s) summary", "bep-619.txt", r"(?i)^#+\s*1\.?\s*Summary", 12),
    ("BEP-322 summary", "bep-322.txt", r"(?i)^#+\s*1\.?\s*Summary", 12),
    ("BEP-675 summary (draft)", "bep-675.txt", r"(?i)^#+\s*1\.?\s*Summary", 14),
    ("BEP-67 price-based order", "bep-067.txt", r"(?i)^#+\s*1\.?\s*Summary", 30),
    ("48 Club Puissant: auction price composition + Builder Control EOA", "48club-puissant-send-bundle.txt",
     r"Version 2 of puissant-builder offers", 8),
    ("BlockRazor: bundle ordering preference + builder EOA + min gas price", "blockrazor-send-bundle.txt",
     r"The block construction algorithm of BlockRazor Builder favors", 4),
    ("bloXroute BSC bundle submission: mev_builders parameter", "bloxroute-bsc-bundle-submission.txt",
     r"mev_builders", 6),
    ("bsc getchainstatus.js: how GetMevStatus attributes a block to a builder", "bsc-getchainstatus-js.txt",
     r"^async function getBlockMevInfo", 44),
    ("Fermi blog: activation", "blog-fermi.txt", r"(?i)fermi", 12),
    ("Good Will Alliance blog: first initiative", "blog-good-will-alliance.txt", r"The first initiative of the alliance", 10),
]


def main():
    out = ["Verbatim excerpts (exact consecutive lines of the saved doc text files; nothing edited).\n"]
    for label, fn, rx, n in EX:
        p = os.path.join(DOCS, fn)
        if not os.path.exists(p):
            out.append(f"### {label}\nSOURCE_FILE: docs/{fn}\nNOT FOUND\n")
            continue
        txt = open(p).read()
        url = re.search(r"^URL: (.+)$", txt, re.M).group(1)
        fetched = re.search(r"^FETCHED_AT_UTC: (.+)$", txt, re.M).group(1)
        lines = txt.splitlines()
        h = next(i for i, l in enumerate(lines) if l.startswith("=" * 78))
        hit = next((i for i in range(h + 1, len(lines)) if re.search(rx, lines[i])), None)
        if hit is None:
            out.append(f"### {label}\nSOURCE_FILE: docs/{fn}\nURL: {url}\nANCHOR NOT FOUND: {rx}\n")
            continue
        seg = lines[hit:hit + n]
        out.append(f"### {label}\nSOURCE_FILE: docs/{fn} (lines {hit + 1}-{hit + len(seg)})\nURL: {url}\n"
                   f"FETCHED_AT_UTC: {fetched}\n---8<--- verbatim\n" + "\n".join(seg) + "\n---8<---\n")
    open(os.path.join(DOCS, "excerpts.txt"), "w").write("\n".join(out))
    print("blocks", len(out) - 1)


if __name__ == "__main__":
    main()
