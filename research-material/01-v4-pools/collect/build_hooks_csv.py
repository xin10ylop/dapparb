#!/usr/bin/env python3
"""Build ../hooks.csv (one row per hook address) and ../hook-labels-long.csv (one row per (hook, label source)).

Hook set: every hook with >= 20 pools in the Initialize data counted here, plus every other hook in that data or in the 7-day data
that has at least one label source (Blockscout metadata fetched, Uniswap hooklist entry, Zora on-chain registry event, or a
launchpad/third-party document line containing the address). address(0) (no hook) is included as a count row with no label.
Counts: pool_count_so_far = Initialize events per hook in the Initialize data available when this script ran
(V4INIT final parts if initialize-parts.json exists, else the V4INIT work chunks, i.e. partial); count_block_range lists the
contiguous block ranges covered. pool_count_7d = same count over the V4RECENT 7-day Initialize window (complete for that window).
Label precedence for the single 'label' column (deterministic, no judgement): (1) the launchpad's own docs/repositories
(Zora, Clanker, Flaunch, Doppler, Bunni), (2) Zora on-chain ZoraHookRegistry event, (3) Uniswap hooklist entry, (4) third-party
code lists (Uniswap routing-api allowlist, KyberSwap dex-lib), (5) Blockscout verified contract name. All sources are kept in
hook-labels-long.csv with verbatim evidence."""
import csv, gzip, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import HOOK_FLAG_COLUMNS, hook_flags

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE); D = os.path.join(OUT, "hook-docs")
ZERO = "0x0000000000000000000000000000000000000000"

hc = json.loads(subprocess.check_output([sys.executable, os.path.join(HERE, "hook_counts.py")]))
counts = {h: (c, f, l) for h, c, f, l in hc["hooks"]}
cov = ";".join("%d-%d" % (a, b) for a, b in hc["coverage_block_ranges"])
count_src = "v4init_final" if os.path.exists(os.path.join(OUT, "initialize-parts.json")) else "v4init_work_chunks_partial"

c7 = {}
rp = json.load(open(os.path.join(OUT, "recent-parts.json")))
w7 = rp["pin"]["initialize_window"]
for p in rp["parts"]["initialize_7d"]:
    with gzip.open(os.path.join(OUT, p["file"]), "rt", newline="") as f:
        rd = csv.reader(f); next(rd)
        for r in rd:
            c7[r[9]] = c7.get(r[9], 0) + 1

bs = {}
bp = os.path.join(D, "blockscout", "index.jsonl.gz")
if os.path.exists(bp):
    for l in gzip.open(bp, "rt"):
        j = json.loads(l); bs[j["address"]] = j

hl = {}
hp = os.path.join(D, "uniswap-hooklist-base.jsonl.gz")
if os.path.exists(hp):
    for l in gzip.open(hp, "rt"):
        j = json.loads(l); hl[j["content"]["hook"]["address"].lower()] = j

zr = {}
zp = os.path.join(D, "zora-hook-registry-events.csv")
if os.path.exists(zp):
    for r in csv.DictReader(open(zp)):
        zr.setdefault(r["hook"], []).append(r)

PROJECT = [
    (r"docs\.zora\.co|/ourzora/", "Zora", 1), (r"clanker\.gitbook\.io|/clanker-devco/", "Clanker", 1),
    (r"flaunch|/flayerlabs/", "Flaunch", 1), (r"docs\.doppler\.lol", "Doppler", 1), (r"/Bunniapp/", "Bunni", 1),
    (r"/Uniswap/routing-api/", "Uniswap routing-api allowlist", 4), (r"/KyberNetwork/", "KyberSwap dex-lib", 4),
    (r"/Uniswap/docs/|docs\.uniswap\.org|/Uniswap/v4-core/", "Uniswap docs", 4),
]
docs = {}
with gzip.open(os.path.join(D, "doc-address-excerpts.csv.gz"), "rt", newline="") as f:
    for r in csv.DictReader(f):
        docs.setdefault(r["address"], []).append(r)


def proj(url):
    for pat, name, prio in PROJECT:
        if re.search(pat, url):
            return name, prio
    return "other document", 4


hooks = set(h for h, (c, _, _) in counts.items() if c >= 20)
labelled = set(bs) | set(hl) | set(zr) | set(docs)
hooks |= (set(counts) | set(c7)) & labelled
hooks.add(ZERO)

long_rows, out_rows = [], []
for h in sorted(hooks, key=lambda x: (-counts.get(x, (0,))[0], -c7.get(x, 0), x)):
    labels = []  # (prio, label, url, evidence, source_kind)
    b = bs.get(h, {})
    for r in docs.get(h, []):
        name, prio = proj(r["url"])
        labels.append((prio, name + ((" (" + b["name"] + ")") if b.get("name") else ""), r["url"], r["line_verbatim"], "document"))
    for r in zr.get(h, []):
        labels.append((2, "Zora (ZoraHookRegistry tag=%s version=%s)" % (r["tag"], r["version"]),
                       "https://base.blockscout.com/tx/%s" % r["tx_hash"],
                       "%s(hook=%s, tag=%s, version=%s) block %s log %s" % (r["event"], r["hook"], r["tag"], r["version"], r["block_number"], r["log_index"]),
                       "zora_onchain_registry"))
    if h in hl:
        e = hl[h]["content"]["hook"]
        labels.append((3, e.get("name", ""), hl[h]["raw_url"], json.dumps({"name": e.get("name"), "description": e.get("description"), "deployer": e.get("deployer")}),
                       "uniswap_hooklist"))
    if b.get("name"):
        labels.append((5, b["name"], b["url"].replace("/api/v2/addresses/", "/address/"), '"name": "%s", "is_verified": %s' % (b["name"], json.dumps(b.get("is_verified"))),
                       "blockscout"))
    labels.sort(key=lambda x: x[0])
    for pr, lab, url, ev, kind in labels:
        long_rows.append([h, kind, str(pr), lab, url, ev])
    top = labels[0] if labels else (None, "", "", "", "")
    cnt = counts.get(h)
    out_rows.append([h, str(cnt[0]) if cnt else "0", cov, count_src, str(cnt[1]) if cnt else "", str(cnt[2]) if cnt else "",
                     str(c7.get(h, 0)), "%d-%d" % tuple(w7), top[1], top[2], top[3], str(len(labels)),
                     b.get("name") or "", "" if not b else json.dumps(b.get("is_verified")), (b.get("creator_address_hash") or "").lower(),
                     (b.get("creation_transaction_hash") or "").lower(), (b.get("creation_tx_from") or "").lower(), (b.get("creation_tx_to") or "").lower(),
                     hl[h]["content"]["hook"].get("name", "") if h in hl else "",
                     ";".join("%s:%s" % (r["tag"], r["version"]) for r in zr.get(h, []))] + hook_flags(h))

with open(os.path.join(OUT, "hooks.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook_address", "pool_count_so_far", "count_block_range", "count_source", "first_init_block_in_counted_data", "last_init_block_in_counted_data",
                "pool_count_7d", "count_7d_block_range", "label", "label_source_url", "label_evidence", "n_label_sources",
                "blockscout_name", "blockscout_is_verified", "blockscout_creator_address", "blockscout_creation_tx", "creation_tx_from", "creation_tx_to",
                "uniswap_hooklist_name", "zora_registry_tag_version"] + HOOK_FLAG_COLUMNS)
    w.writerows(out_rows)
with open(os.path.join(OUT, "hook-labels-long.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["hook_address", "source_kind", "precedence", "label", "source_url", "evidence_verbatim"])
    w.writerows(long_rows)
print("hooks.csv rows", len(out_rows), "label rows", len(long_rows), "count_source", count_src, "coverage", cov)
