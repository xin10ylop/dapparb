#!/usr/bin/env python3
"""Build ../builders.csv: every BSC builder entry with its on-chain address from
  (a) bnb-chain/good-will-alliance mev-info/bsc-mainnet/builder-list.toml   (current registry)
  (b) bnb-chain/bsc-mev-info mainnet/builder-list.toml                      (header states it is deprecated)
  (c) builders' own documentation pages fetched by fetch_docs.py (address stated in the page text)
Columns: builder_name, builder_org_derived (prefix of the TOML section name before the first '-', or the doc's builder), address, address_lower, rpc, website, source, source_url, git_commit,
         evidence_verbatim
evidence_verbatim is the exact TOML section text (a/b) or the exact sentence/lines from the doc text file (c).
Requires the shallow clones under /home/user/bnb-chain/ (see MANIFEST) and ../docs/*.txt.
"""
import csv
import os
import re
import subprocess
import tomllib

HERE = os.path.dirname(os.path.abspath(__file__))
OUTD = os.path.abspath(os.path.join(HERE, ".."))
DOCS = os.path.join(OUTD, "docs")

REG = [
    ("good-will-alliance builder-list.toml (current)", "/home/user/bnb-chain/good-will-alliance",
     "https://github.com/bnb-chain/good-will-alliance", "mev-info/bsc-mainnet/builder-list.toml"),
    ("bsc-mev-info builder-list.toml (file header: deprecated)", "/home/user/bnb-chain/bsc-mev-info",
     "https://github.com/bnb-chain/bsc-mev-info", "mainnet/builder-list.toml"),
]


def sections(text):
    """yield (name, verbatim_section_text, org_comment)"""
    lines = text.splitlines()
    cur, buf, org = None, [], ""
    last_org = ""
    for ln in lines:
        m = re.match(r"^\s*#\s*builder:\s*(.+)$", ln)
        if m:
            last_org = m.group(1).strip()
        m = re.match(r"^\[([^\]]+)\]\s*$", ln)
        if m:
            if cur:
                yield cur, "\n".join(buf).strip(), org
            cur, buf, org = m.group(1), [ln], last_org
            continue
        if cur is not None:
            if ln.strip().startswith("#"):
                continue
            buf.append(ln)
    if cur:
        yield cur, "\n".join(buf).strip(), org


def main():
    rows = []
    for label, repo_dir, repo_url, rpath in REG:
        commit = subprocess.check_output(["git", "-C", repo_dir, "log", "-1", "--format=%H"], text=True).strip()
        text = open(os.path.join(repo_dir, rpath)).read()
        data = tomllib.loads(text)
        for name, sect, org in sections(text):
            if name == "example":
                continue
            d = data.get(name, {})
            addr = d.get("Address", "")
            rows.append({"builder_name": name, "builder_org_derived": name.split("-")[0], "address": addr,
                         "address_lower": addr.lower(), "rpc": d.get("RPC", ""), "website": d.get("Website", ""),
                         "source": label, "source_url": f"{repo_url}/blob/{commit}/{rpath}", "git_commit": commit,
                         "evidence_verbatim": sect})
    # (c) builder docs: exact lines containing an address that the page describes as the builder's EOA
    doc_ev = [
        ("48club-puissant-send-bundle.txt", "48club Puissant Builder Control EOA", "48club",
         r"Builder Control EOA", 6),
        ("blockrazor-send-bundle.txt", "BlockRazor Builder EOA", "blockrazor", r"BlockRazor Builder EOA of which address", 1),
    ]
    for fn, name, org, anchor, span in doc_ev:
        p = os.path.join(DOCS, fn)
        if not os.path.exists(p):
            continue
        txt = open(p).read()
        url = re.search(r"^URL: (.+)$", txt, re.M).group(1)
        fetched = re.search(r"^FETCHED_AT_UTC: (.+)$", txt, re.M).group(1)
        body = txt.split("=" * 78 + "\n", 1)[1]
        blines = body.splitlines()
        for i, ln in enumerate(blines):
            if re.search(anchor, ln):
                ev = "\n".join(blines[i:i + span]).strip()
                m = re.search(r"0x[0-9a-fA-F]{40}", ev)
                if m:
                    rows.append({"builder_name": name, "builder_org_derived": org, "address": m.group(0),
                                 "address_lower": m.group(0).lower(), "rpc": "", "website": "",
                                 "source": f"builder documentation (fetched {fetched})", "source_url": url,
                                 "git_commit": "", "evidence_verbatim": ev})
                    break
    out = os.path.join(OUTD, "builders.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print("rows", len(rows))


if __name__ == "__main__":
    main()
