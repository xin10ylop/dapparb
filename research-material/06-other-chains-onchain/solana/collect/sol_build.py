#!/usr/bin/env python3
"""Build the tabular outputs of the Solana slot sample from ../data/raw-slots/slot-*.json.gz (deterministic, re-runnable).
Inputs: state/pin.json, ../data/slot-leaders.json, ../data/get-blocks.json, ../dex-programs.csv, ../jito-tip-accounts.csv
Outputs (in ..):
  slots.csv.gz                     one row per slot of the window
  txs-nonvote-NNN.csv.gz           one minimal row per non-vote tx
  dex-txs-NNN.jsonl.gz             one JSON line per non-vote tx invoking (top-level or inner) any program in dex-programs.csv
  jito-tip-transfers.csv.gz        one row per System Program transfer instruction (top-level or inner) into a Jito tip account
  program-invocations.csv.gz       per program id: number of non-vote txs / instructions invoking it in the window
  token-mints-seen.csv.gz          mints appearing in pre/postTokenBalances of dex txs (+ decimals, token program)
Parts rotate before 85 MB compressed.
"""
import csv, gzip, io, json, os, glob, struct, collections
HERE = os.path.dirname(os.path.abspath(__file__)); BASE = os.path.dirname(HERE); DATA = os.path.join(BASE, "data")
RAW = os.path.join(DATA, "raw-slots")
SYSTEM = "11111111111111111111111111111111"
CBUDGET = "ComputeBudget111111111111111111111111111111"
VOTE = "Vote111111111111111111111111111111111111111"
MAXB = 80 * 1024 * 1024
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"; B58I = {c: i for i, c in enumerate(B58)}

def b58dec(s):
    n = 0
    for c in s: n = n * 58 + B58I[c]
    full = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    pad = len(s) - len(s.lstrip("1"))
    return b"\x00" * pad + full

class Rot:
    """rotating gzip writer (csv or jsonl) keeping every part < MAXB compressed"""
    def __init__(self, stem, ext, header=None):
        self.stem, self.ext, self.header, self.n, self.f, self.raw, self.rows, self.files = stem, ext, header, 0, None, None, 0, []
    def _open(self):
        self.n += 1; p = os.path.join(BASE, "%s-%03d.%s.gz" % (self.stem, self.n, self.ext)); self.files.append(p)
        self.raw = open(p, "wb"); self.f = io.TextIOWrapper(gzip.GzipFile(fileobj=self.raw, mode="wb", compresslevel=6), newline="")
        if self.header: csv.writer(self.f).writerow(self.header)
    def write(self, line_or_row):
        if self.f is None or self.raw.tell() > MAXB:
            if self.f: self.f.close()
            self._open()
        if self.ext == "csv": csv.writer(self.f).writerow(line_or_row)
        else: self.f.write(line_or_row + "\n")
        self.rows += 1
    def close(self):
        if self.f: self.f.close()

def decode_cb(data_b58):
    try: d = b58dec(data_b58)
    except Exception: return None
    if not d: return None
    t = d[0]
    try:
        if t == 2 and len(d) >= 5: return ("cu_limit", struct.unpack_from("<I", d, 1)[0])
        if t == 3 and len(d) >= 9: return ("cu_price_micro_lamports", struct.unpack_from("<Q", d, 1)[0])
        if t == 1 and len(d) >= 5: return ("heap_frame_bytes", struct.unpack_from("<I", d, 1)[0])
        if t == 4 and len(d) >= 5: return ("loaded_accounts_data_size_limit", struct.unpack_from("<I", d, 1)[0])
    except struct.error: return None
    return None

def main():
    pin = json.load(open(os.path.join(HERE, "state", "pin.json")))
    start, end = pin["start_slot"], pin["end_slot"]
    leaders = json.load(open(os.path.join(DATA, "slot-leaders.json")))["result"]
    produced = set(json.load(open(os.path.join(DATA, "get-blocks.json")))["result"] or [])
    dex = {}
    for r in csv.DictReader(open(os.path.join(BASE, "dex-programs.csv"))): dex[r["program_id"]] = r["name"]
    tips = set(r["tip_account"] for r in csv.DictReader(open(os.path.join(BASE, "jito-tip-accounts.csv"))))
    for stale in glob.glob(os.path.join(BASE, "txs-nonvote-[0-9][0-9][0-9].csv.gz")) + glob.glob(os.path.join(BASE, "dex-txs-[0-9][0-9][0-9].jsonl.gz")):
        os.remove(stale)   # previous build's parts (part count can change)
    slots_out = gzip.open(os.path.join(BASE, "slots.csv.gz"), "wt", newline=""); sw = csv.writer(slots_out)
    sw.writerow(["slot", "status", "block_time", "blockhash", "previous_blockhash", "parent_slot", "block_height", "tx_count",
                 "vote_tx_count", "vote_tx_mixed_count", "nonvote_tx_count", "leader", "in_getBlocks_result", "endpoint", "fetched_at_utc", "rpc_error"])
    txw = Rot("txs-nonvote", "csv", ["slot", "block_time", "index", "signature", "version", "err_flag", "err_json", "fee",
                                    "compute_units_consumed", "cost_units", "num_required_signatures", "first_signer",
                                    "jito_tip_lamports", "jito_tip_account_balance_delta_lamports", "invokes_known_dex",
                                    "known_dex_programs", "program_ids", "n_top_level_ix", "n_inner_ix",
                                    "cb_cu_limit", "cb_cu_price_micro_lamports", "tx_config_json", "log_truncated"])
    dxw = Rot("dex-txs", "jsonl")
    tipw = gzip.open(os.path.join(BASE, "jito-tip-transfers.csv.gz"), "wt", newline=""); tw = csv.writer(tipw)
    tw.writerow(["slot", "index", "signature", "top_ix_index", "depth", "instruction", "from", "to", "lamports", "tx_err_flag"])
    prog = collections.defaultdict(lambda: [0, 0, 0, 0])  # txs, top-level ix, inner ix, txs with err
    mints = {}
    for s in range(start, end + 1):
        p = os.path.join(RAW, "slot-%d.json.gz" % s)
        leader = leaders[s - start] if leaders and s - start < len(leaders) else ""
        if not os.path.exists(p):
            sw.writerow([s, "missing", "", "", "", "", "", "", "", "", "", leader, int(s in produced), "", "", ""]); continue
        o = json.load(gzip.open(p, "rt"))
        if o["status"] != "ok":
            sw.writerow([s, o["status"], "", "", "", "", "", "", "", "", "", leader, int(s in produced), o.get("endpoint"), o.get("fetched_at_utc"), json.dumps(o.get("rpc_error"))]); continue
        h = o["header"]; bt = h.get("blockTime")
        sw.writerow([s, "ok", bt, h.get("blockhash"), h.get("previousBlockhash"), h.get("parentSlot"), h.get("blockHeight"), o["tx_count"],
                     o["vote_tx_count"], o["vote_tx_mixed_count"], len(o["nonvote"]), leader, int(s in produced), o["endpoint"], o["fetched_at_utc"], ""])
        for item in o["nonvote"]:
            i, t = item["index"], item["tx"]
            msg, meta = t["transaction"]["message"], t["meta"]
            la = meta.get("loadedAddresses") or {}
            keys = list(msg["accountKeys"]) + list(la.get("writable") or []) + list(la.get("readonly") or [])
            nsig = msg["header"]["numRequiredSignatures"]
            signers = keys[:nsig]
            sig = t["transaction"]["signatures"][0]
            err = meta.get("err"); errf = 0 if err is None else 1
            inner_by = {ii["index"]: ii["instructions"] for ii in (meta.get("innerInstructions") or [])}
            invoked = []; n_inner = 0; cb = {}; tip_ix = []
            for ti, ix in enumerate(msg["instructions"]):
                seq = [(ix, 1)] + [(jx, jx.get("stackHeight")) for jx in inner_by.get(ti, [])]
                for k, (jx, depth) in enumerate(seq):
                    pid = keys[jx["programIdIndex"]] if jx["programIdIndex"] < len(keys) else None
                    invoked.append([ti, depth, pid])
                    if k > 0: n_inner += 1
                    if pid == CBUDGET and k == 0:
                        d = decode_cb(jx.get("data", ""))
                        if d: cb[d[0]] = d[1]
                    if pid == SYSTEM:
                        try: d = b58dec(jx.get("data", ""))
                        except Exception: d = b""
                        acc = jx.get("accounts") or []
                        if len(d) >= 12:
                            typ = struct.unpack_from("<I", d, 0)[0]
                            to = frm = None; kind = None
                            if typ == 2 and len(acc) >= 2: frm, to, kind = keys[acc[0]], keys[acc[1]], "transfer"
                            elif typ == 11 and len(acc) >= 3: frm, to, kind = keys[acc[0]], keys[acc[2]], "transfer_with_seed"
                            if to in tips:
                                lam = struct.unpack_from("<Q", d, 4)[0]
                                tip_ix.append({"top_ix_index": ti, "depth": depth, "instruction": kind, "from": frm, "to": to, "lamports": lam})
            pids_ordered = list(dict.fromkeys(x[2] for x in invoked))
            for pid in pids_ordered: prog[pid][0] += 1; prog[pid][3] += errf
            for ti_, depth, pid in invoked:
                if depth == 1: prog[pid][1] += 1
                else: prog[pid][2] += 1
            dex_hit = [dex[pid] for pid in pids_ordered if pid in dex]
            tip_lam = sum(x["lamports"] for x in tip_ix)
            pre, post = meta.get("preBalances") or [], meta.get("postBalances") or []
            tip_delta = sum(post[k] - pre[k] for k, a in enumerate(keys) if a in tips and k < len(pre) and k < len(post))
            logs = meta.get("logMessages") or []
            trunc = int(any(l == "Log truncated" for l in logs))
            for x in tip_ix:
                tw.writerow([s, i, sig, x["top_ix_index"], x["depth"], x["instruction"], x["from"], x["to"], x["lamports"], errf])
            cfg = msg.get("transactionConfig")
            txw.write([s, bt, i, sig, t.get("version"), errf, json.dumps(err, separators=(",", ":")) if err is not None else "", meta.get("fee"),
                       meta.get("computeUnitsConsumed"), meta.get("costUnits"), nsig, signers[0] if signers else "",
                       tip_lam, tip_delta, int(bool(dex_hit)), ";".join(dex_hit), ";".join(p_ or "" for p_ in pids_ordered),
                       len(msg["instructions"]), n_inner, cb.get("cu_limit", ""), cb.get("cu_price_micro_lamports", ""),
                       json.dumps(cfg, separators=(",", ":")) if cfg is not None else "", trunc])
            if dex_hit:
                rec = {"slot": s, "block_time": bt, "index": i, "signature": sig, "version": t.get("version"), "err": err,
                       "fee": meta.get("fee"), "computeUnitsConsumed": meta.get("computeUnitsConsumed"), "costUnits": meta.get("costUnits"),
                       "signers": signers, "num_required_signatures": nsig,
                       "invoked_programs": invoked,
                       "known_dex_programs_invoked": [[pid, dex[pid]] for pid in pids_ordered if pid in dex],
                       "preTokenBalances": meta.get("preTokenBalances"), "postTokenBalances": meta.get("postTokenBalances"),
                       "signer_balances": [{"account": signers[k], "pre": pre[k] if k < len(pre) else None, "post": post[k] if k < len(post) else None} for k in range(len(signers))],
                       "jito_tip_transfers": tip_ix, "jito_tip_lamports": tip_lam, "jito_tip_account_balance_delta_lamports": tip_delta,
                       "compute_budget_ix_decoded": cb, "transactionConfig": cfg,
                       "account_keys_resolved": keys, "log_truncated": trunc}
                dxw.write(json.dumps(rec, separators=(",", ":")))
                for tb in (meta.get("preTokenBalances") or []) + (meta.get("postTokenBalances") or []):
                    m = tb.get("mint")
                    if m and m not in mints:
                        mints[m] = [tb.get("uiTokenAmount", {}).get("decimals"), tb.get("programId"), 0]
                for m in set(tb.get("mint") for tb in (meta.get("preTokenBalances") or []) + (meta.get("postTokenBalances") or [])):
                    if m in mints: mints[m][2] += 1
    slots_out.close(); txw.close(); dxw.close(); tipw.close()
    with gzip.open(os.path.join(BASE, "program-invocations.csv.gz"), "wt", newline="") as f:
        w = csv.writer(f); w.writerow(["program_id", "known_dex_name", "nonvote_txs_invoking", "top_level_invocations", "inner_invocations", "nonvote_txs_invoking_with_err"])
        for pid, v in sorted(prog.items(), key=lambda kv: -kv[1][0]): w.writerow([pid, dex.get(pid, ""), v[0], v[1], v[2], v[3]])
    with gzip.open(os.path.join(BASE, "token-mints-seen.csv.gz"), "wt", newline="") as f:
        w = csv.writer(f); w.writerow(["mint", "decimals", "token_program", "dex_txs_with_balance_entry"])
        for m, v in sorted(mints.items(), key=lambda kv: -kv[1][2]): w.writerow([m] + v)
    json.dump({"txs_nonvote_parts": [os.path.basename(x) for x in txw.files], "txs_nonvote_rows": txw.rows,
               "dex_txs_parts": [os.path.basename(x) for x in dxw.files], "dex_txs_rows": dxw.rows,
               "programs": len(prog), "mints": len(mints)}, open(os.path.join(DATA, "build-summary.json"), "w"), indent=1)
    print("built", txw.rows, dxw.rows, len(prog), len(mints))

if __name__ == "__main__":
    main()
