#!/usr/bin/env python3
"""V4INIT top-up: Uniswap V4 PoolManager Initialize events on Base from the block after the V4INIT pin up to the
current head (minus 10 blocks), so that the --v4-pools list used by the live test also contains the pools
created between the V4INIT pin (block 52,006,302) and the engine launch.

Collect-only. Same decoder, checks and 27 columns as the V4INIT collector (imports
/home/user/dapparb/research-material/01-v4-pools/collect/common.py: decode_initialize, pool_id_of, get_logs_range).

Output (in ../ = /home/user/dapparb/research-material/02-v4-live-test):
  initialize-topup.csv.gz   header + rows sorted by (block_number, log_index); same columns as initialize-part-NNNN.csv.gz
  initialize-topup.json     pin, block range, rows, endpoints used per chunk, sha256 of the output and of common.py
State (resumable): collect/state/topup-pin.json (pinned range; reused on rerun), collect/work/topup/c_<from>_<to>.csv.gz
  (one checkpoint per completed chunk, no header), collect/state/topup-gaps.json (chunks no endpoint could serve).
Exit code 0 only if every chunk of the pinned range was fetched and the output was written and re-read.

Usage: python3 -u topup_initialize.py [--to BLOCK] [--from BLOCK] [--out FILE] [--repin]
  --from/--to/--out are for smoke tests (default from = V4INIT block_to + 1, to = head - 10).
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.dirname(HERE)
V4DIR = "/home/user/dapparb/research-material/01-v4-pools"
sys.path.insert(0, os.path.join(V4DIR, "collect"))
import common as C  # noqa: E402

CHUNK = 1000
HEAD_MARGIN = 10


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def endpoints():
    return [
        C.Endpoint("publicnode", "https://base-rpc.publicnode.com", max_range=CHUNK, inflight=1),
        C.Endpoint("mainnet.base.org", "https://mainnet.base.org", max_range=CHUNK, inflight=1),
        C.Endpoint("developer-access-mainnet.base.org", "https://developer-access-mainnet.base.org", max_range=CHUNK, inflight=1),
        C.Endpoint("tenderly", "https://gateway.tenderly.co/public/base", max_range=CHUNK, inflight=1),
    ]


def head_block(eps):
    last = None
    for ep in eps:
        try:
            return int(ep.call_retry("eth_blockNumber", [], tries=3, timeout=20), 16), ep.name
        except Exception as e:  # noqa
            last = e
            C.log("eth_blockNumber failed on", ep.name, str(e)[:150])
    raise RuntimeError("no endpoint answered eth_blockNumber: %s" % last)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="frm", type=int)
    ap.add_argument("--to", type=int)
    ap.add_argument("--out")
    ap.add_argument("--repin", action="store_true", help="discard the stored pin and pin to the current head")
    a = ap.parse_args()
    smoke = a.out is not None
    eps = endpoints()
    state_dir = os.path.join(HERE, "state")
    work = os.path.join(HERE, "work", "topup" if not smoke else "topup-smoke")
    os.makedirs(state_dir, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    pin_path = os.path.join(state_dir, "topup-pin.json" if not smoke else "topup-smoke-pin.json")
    if a.repin:
        if os.path.exists(pin_path):
            os.remove(pin_path)
        for f in os.listdir(work):
            os.remove(os.path.join(work, f))

    if os.path.exists(pin_path) and a.frm is None and a.to is None:
        pin = json.load(open(pin_path))
        C.log("reusing pin", pin)
    else:
        idx = json.load(open(os.path.join(V4DIR, "initialize-parts.json")))
        frm = a.frm if a.frm is not None else int(idx["block_to"]) + 1
        if a.to is not None:
            to, src = a.to, "--to argument"
            head = None
        else:
            head, name = head_block(eps)
            to, src = head - HEAD_MARGIN, "eth_blockNumber(%s) - %d" % (name, HEAD_MARGIN)
        pin = {"from_block": frm, "to_block": to, "to_block_source": src, "head_at_pin": head, "pinned_at_utc": C.now_utc(),
               "v4init_block_to": int(idx["block_to"]), "chunk_size": CHUNK, "topic0": C.T_INITIALIZE, "address": C.POOL_MANAGER}
        with open(pin_path + ".tmp", "w") as f:
            json.dump(pin, f, indent=1)
        os.replace(pin_path + ".tmp", pin_path)
        C.log("pinned", pin)

    frm, to = pin["from_block"], pin["to_block"]
    if to < frm:
        C.log("empty range", frm, to)
    chunks = [(b, min(b + CHUNK - 1, to)) for b in range(frm, to + 1, CHUNK)]
    served = {}
    gaps = []
    for (cf, ct) in chunks:
        path = os.path.join(work, "c_%d_%d.csv.gz" % (cf, ct))
        if os.path.exists(path):
            continue
        rows, err, used = None, [], None
        for rnd in range(3):
            for ep in eps:
                try:
                    logs = C.get_logs_range(ep, cf, ct, [C.T_INITIALIZE])
                    rows = []
                    for lg in logs:
                        r = C.decode_initialize(lg)
                        # r: block, tx, txi, logi, pool_id, c0, c1, fee, ts, hooks, ...
                        if C.pool_id_of(r[5], r[6], r[7], r[8], r[9]) != r[4]:
                            raise C.RpcError("pool_id != keccak(abi.encode(key)) at %s" % r[1], kind="other")
                        rows.append(r)
                    used = ep.name
                    break
                except Exception as e:  # noqa
                    err.append("%s: %s" % (ep.name, str(e)[:200]))
                    C.log("chunk", cf, ct, "failed on", ep.name, str(e)[:150])
            if rows is not None:
                break
            time.sleep(10 * (rnd + 1))
        if rows is None:
            gaps.append({"from": cf, "to": ct, "errors": err[-8:]})
            continue
        rows.sort(key=lambda r: (int(r[0]), int(r[3])))
        C.atomic_write_rows_gz(path, rows)
        served["%d_%d" % (cf, ct)] = used
        C.log("chunk", cf, ct, "rows", len(rows), "via", used)

    gaps_path = os.path.join(state_dir, "topup-gaps.json" if not smoke else "topup-smoke-gaps.json")
    with open(gaps_path, "w") as f:
        json.dump({"pin": pin, "gaps": gaps, "written_utc": C.now_utc()}, f, indent=1)
    if gaps:
        C.log("GAPS", len(gaps), "chunk(s) could not be fetched; see", gaps_path)
        sys.exit(2)

    # assemble
    out = a.out or os.path.join(OUTDIR, "initialize-topup.csv.gz")
    allrows = []
    for (cf, ct) in chunks:
        allrows.extend(C.read_rows_gz(os.path.join(work, "c_%d_%d.csv.gz" % (cf, ct))))
    allrows.sort(key=lambda r: (int(r[0]), int(r[3])))
    tmp = out + ".tmp"
    with gzip.open(tmp, "wt", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(C.INIT_COLUMNS)
        w.writerows(allrows)
    os.replace(tmp, out)
    with gzip.open(out, "rt", newline="") as f:
        reread = sum(1 for _ in csv.reader(f)) - 1
    if reread != len(allrows):
        C.log("re-read mismatch", reread, len(allrows))
        sys.exit(3)
    served_all = {}
    try:
        served_all = json.load(open(os.path.join(state_dir, "topup-served.json" if not smoke else "topup-smoke-served.json")))
    except Exception:  # noqa
        pass
    served_all.update(served)
    with open(os.path.join(state_dir, "topup-served.json" if not smoke else "topup-smoke-served.json"), "w") as f:
        json.dump(served_all, f, indent=1)
    idx = {"dataset": "Uniswap V4 PoolManager Initialize events, Base (chain 8453), top-up after the V4INIT pin",
           "file": os.path.basename(out), "rows": len(allrows), "block_from": frm, "block_to": to, "pin": pin,
           "columns": C.INIT_COLUMNS, "chunks": len(chunks), "gaps": 0, "endpoint_per_chunk": served_all,
           "sha256": sha256_file(out), "bytes": os.path.getsize(out),
           "decoder": os.path.join(V4DIR, "collect", "common.py"), "decoder_sha256": sha256_file(os.path.join(V4DIR, "collect", "common.py")),
           "written_utc": C.now_utc()}
    jpath = out[:-len(".csv.gz")] + ".json" if out.endswith(".csv.gz") else out + ".json"
    with open(jpath, "w") as f:
        json.dump(idx, f, indent=1)
    C.log("done", len(allrows), "rows", frm, "-", to, "->", out)


if __name__ == "__main__":
    main()
