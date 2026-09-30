#!/usr/bin/env python3
"""Raw Arbitrum One precompile reads relevant to the ordering policy during the census window.
eth_call at the census window's start block and end block (arbitrum-one.public.blastapi.io; end block also on
arb1.arbitrum.io) and at 'latest' (publicnode). Selectors computed with `cast sig`:
  ArbSys 0x64          arbOSVersion()          0x051038f2
  ArbOwnerPublic 0x6b  getCollectTips()        0x8e34a64d   (tip collection flag; PGA docs: tip collection activates PGA)
  ArbOwnerPublic 0x6b  getScheduledUpgrade()   0x81ef944c
  ArbOwnerPublic 0x6b  getNetworkFeeAccount()  0x2d9125e9
Writes ../arbitrum-chain-state.json (raw results / errors + derived decodings).
usage: python3 arbitrum_chain_state.py"""
import datetime, json, os, time, requests
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0 Safari/537.36", "content-type": "application/json"}
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
w = json.load(open(os.path.join(D, "window.json")))
CALLS = [("ArbSys.arbOSVersion()", "0x0000000000000000000000000000000000000064", "0x051038f2"),
         ("ArbOwnerPublic.getCollectTips()", "0x000000000000000000000000000000000000006b", "0x8e34a64d"),
         ("ArbOwnerPublic.getScheduledUpgrade()", "0x000000000000000000000000000000000000006b", "0x81ef944c"),
         ("ArbOwnerPublic.getNetworkFeeAccount()", "0x000000000000000000000000000000000000006b", "0x2d9125e9")]
# historical state: arbitrum.drpc.org answered "Unknown state" and publicnode refuses (archive); arb1.arbitrum.io
# served only the end block; arbitrum-one.public.blastapi.io served both window blocks.
TARGETS = [("window_start_block", hex(w["start_block"]), "https://arbitrum-one.public.blastapi.io"),
           ("window_end_block", hex(w["end_block"]), "https://arbitrum-one.public.blastapi.io"),
           ("window_end_block", hex(w["end_block"]), "https://arb1.arbitrum.io/rpc"),
           ("latest", "latest", "https://arbitrum-one-rpc.publicnode.com")]
out = {"fetched_at_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"), "window": [w["start_block"], w["end_block"]], "results": []}
for label, tag, url in TARGETS:
    for name, to, data in CALLS:
        res, err = None, None
        for i in range(6):
            try:
                r = requests.post(url, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": data}, tag]}), headers=UA, timeout=60)
                if r.status_code == 429 or r.status_code >= 500:
                    time.sleep(2 * (i + 1)); continue
                j = r.json()
                res, err = j.get("result"), j.get("error")
                break
            except Exception as ex:  # noqa
                err = str(ex)[:200]; time.sleep(2 * (i + 1))
        dec = None
        if res and len(res) >= 66:
            words = [res[2 + 64 * k: 2 + 64 * (k + 1)] for k in range((len(res) - 2) // 64)]
            dec = [str(int(x, 16)) for x in words] if "Account" not in name else ["0x" + words[0][24:]]
        rec = {"at": label, "block_tag": tag, "endpoint": url, "call": name, "to": to, "data": data,
               "result_raw": res, "error": err, "decoded_derived": dec}
        if name == "ArbSys.arbOSVersion()" and dec:
            # Nitro precompiles/ArbSys.go (v3.11.3 line 68): returns 55 + ArbOS version ("Nitro starts at version 56")
            rec["arbos_version_derived"] = str(int(dec[0]) - 55)
        out["results"].append(rec)
        time.sleep(0.3)
json.dump(out, open(os.path.join(D, "arbitrum-chain-state.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
