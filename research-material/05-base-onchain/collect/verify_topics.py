#!/usr/bin/env python3
"""Swap-topic list for the census + one real Base log per topic (raw lookup, no analysis).

Input : collect/swap_topics_used.csv (topic0 computed with `cast keccak <signature>`; this exact list is what
        census.py loaded for criterion A; it is not changed by this script).
Output: ../swap-topics.csv with columns
        topic0, signature, protocol, source_url, verified_example_tx, verified_example_block, verified_example_emitter,
        verified_example_log_index, verification_method
Method: base.blockscout.com etherscan-compatible API module=logs&action=getLogs&topic0=<t> over block windows walking
        back from a pinned head (1k, 16k, 500k, 10M blocks; 6 tries per window, 120 s timeout,
        3 s pause before each request, backoff 5-90 s); the first returned log is then re-checked by fetching
        the tx receipt from gateway.tenderly.co/public/base (fallback base-rpc.publicnode.com / base.drpc.org) and
        confirming a log with that topic0 at that emitter exists in it. If nothing is found, the example columns stay
        empty and verification_method says which windows were searched.
Sequential, 1 in-flight per endpoint, backoff on 429/5xx/timeouts. Writes ../swap-topics.csv after every topic;
resumable (rows that already have verified_example_tx are kept and not re-queried; since 2026-10-01 also rows whose
"no log found" search covered all 4 windows of the same pinned head with no failed window).
Rate limit (added 2026-10-01): an HTTP 429 from Blockscout that carries x-ratelimit-reset (ms) is waited out
(reset + 5 s, at most 1800 s) up to 8 times per window before the normal 6 tries/backoff apply.
Optional: --head N pins head N instead of (live eth_blockNumber - 20). Added 2026-10-01 so the re-run after the
container restart searched the same windows as the first run (head 52007824):
    python3 -u verify_topics.py --head 52007824
"""
import argparse, csv, json, os, sys, time
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', 'swap-topics.csv'))
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
S = requests.Session(); S.headers.update({'User-Agent': UA})
BS = 'https://base.blockscout.com/api'
RPCS = ['https://gateway.tenderly.co/public/base', 'https://base-rpc.publicnode.com', 'https://base.drpc.org']
WINDOWS = [1000, 16000, 500000, 10000000]


def log(*a):
    print(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), *a, file=sys.stderr, flush=True)


def rpc(method, params):
    for url in RPCS:
        for i in range(4):
            try:
                r = S.post(url, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}, timeout=60)
                j = r.json()
                if j.get('error'):
                    raise RuntimeError(str(j['error'])[:200])
                return j['result']
            except Exception as e:
                log('rpc retry', url, method, e); time.sleep(2 ** i)
    return None


RL_WAITS = 8        # per window: HTTP 429 answers that carry x-ratelimit-reset are waited out this many times (not counted as tries)
RL_CAP_S = 1800     # longest single wait for x-ratelimit-reset (s)


def bs_logs(t, lo, hi):
    back = 5; rl = 0; i = 0
    while i < 6:
        time.sleep(3)
        try:
            r = S.get(BS, params={'module': 'logs', 'action': 'getLogs', 'fromBlock': lo, 'toBlock': hi, 'topic0': t}, timeout=120)
            reset = r.headers.get('x-ratelimit-reset', '')
            if r.status_code == 429 and reset.isdigit() and rl < RL_WAITS:
                # added 2026-10-01: Blockscout sends x-ratelimit-limit (10) and x-ratelimit-reset (ms until the quota resets)
                rl += 1; wait = min(int(reset) / 1000.0 + 5, RL_CAP_S)
                log('blockscout 429', t[:10], lo, hi, 'x-ratelimit-limit', r.headers.get('x-ratelimit-limit'),
                    'x-ratelimit-reset_ms', reset, 'waiting %.0f s (rate-limit wait %d/%d)' % (wait, rl, RL_WAITS))
                time.sleep(wait); continue
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError('http %d' % r.status_code)
            j = r.json()
            res = j.get('result')
            if isinstance(res, list):
                return res
            if j.get('message', '').lower().startswith('no logs'):
                return []
            raise RuntimeError(str(j)[:200])
        except Exception as e:
            log('blockscout retry', t[:10], lo, hi, e); time.sleep(back); back = min(back * 2, 90)
        i += 1
    return None


COLS = ['topic0', 'signature', 'protocol', 'source_url', 'verified_example_tx', 'verified_example_block', 'verified_example_emitter', 'verified_example_log_index', 'verification_method']


def write_out(rows_by_topic, order):
    """Rewrite ../swap-topics.csv; keeps census_* columns already added by finalize.py."""
    old = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            for r in csv.DictReader(f):
                old[r['topic0']] = r
    extra = []
    for r in old.values():
        extra = [c for c in r.keys() if c.startswith('census_')]; break
    with open(OUT + '.tmp', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS + extra); w.writeheader()
        for tr in order:
            r = dict(rows_by_topic.get(tr['topic0']) or old.get(tr['topic0']) or tr)
            for c in COLS:
                r.setdefault(c, '')
            if not r.get('verification_method'):
                r['verification_method'] = 'pending: collect/verify_topics.py running'
            for c in extra:
                r[c] = old.get(tr['topic0'], {}).get(c, '')
            w.writerow({k: r.get(k, '') for k in COLS + extra})
    os.replace(OUT + '.tmp', OUT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--head', type=int, default=None, help='pin this head block instead of live eth_blockNumber - 20')
    a = ap.parse_args()
    head = a.head if a.head is not None else int(rpc('eth_blockNumber', []), 16) - 20
    log('pinned head', head, '(--head)' if a.head is not None else '(live eth_blockNumber - 20)')
    with open(os.path.join(HERE, 'swap_topics_used.csv')) as f:
        topics = list(csv.DictReader(f))
    done = {}
    if os.path.exists(OUT):  # resume: keep rows already verified
        with open(OUT) as f:
            for r in csv.DictReader(f):
                vm = r.get('verification_method', '')
                # added 2026-10-01: also keep a finished "no log found" search of all windows for this same head
                searched_all = (vm.startswith('no log found') and 'failed:' not in vm
                                and vm.count('-%d' % head) == len(WINDOWS))
                if r.get('verified_example_tx') or searched_all:
                    done[r['topic0']] = {c: r.get(c, '') for c in COLS}
    rows = dict(done)
    for tr in topics:
        t = tr['topic0']
        if t in done:
            log(t, 'already done (verified, or all windows searched), kept'); continue
        ex = None; searched = []; errs = []
        for w in WINDOWS:
            lo = max(0, head - w + 1)
            res = bs_logs(t, lo, head)
            if res is None:
                errs.append('%d-%d failed' % (lo, head)); continue
            searched.append('%d-%d' % (lo, head))
            if res:
                L = sorted(res, key=lambda x: (int(x['blockNumber'], 16), int(x['logIndex'] or '0x0', 16)))[-1]
                ex = L; break
            time.sleep(1)
        out = dict(tr)
        out.update({'verified_example_tx': '', 'verified_example_block': '', 'verified_example_emitter': '', 'verified_example_log_index': '', 'verification_method': ''})
        if ex:
            txh = ex['transactionHash'].lower(); emitter = ex['address'].lower()
            rc = rpc('eth_getTransactionReceipt', [txh])
            match = None
            if rc:
                for L in rc['logs']:
                    if L['topics'] and L['topics'][0].lower() == t and L['address'].lower() == emitter:
                        match = L; break
            if match:
                out.update({'verified_example_tx': txh, 'verified_example_block': str(int(rc['blockNumber'], 16)), 'verified_example_emitter': emitter,
                            'verified_example_log_index': str(int(match['logIndex'], 16)),
                            'verification_method': 'blockscout getLogs topic0 window %s (head pinned %d); newest log re-checked in eth_getTransactionReceipt' % (searched[-1], head)})
            else:
                out['verification_method'] = 'blockscout returned tx %s but receipt re-check failed' % txh
        else:
            out['verification_method'] = 'no log found; blockscout windows searched: %s%s' % (', '.join(searched) or 'none', ('; failed: ' + ', '.join(errs)) if errs else '')
        log(t, tr['signature'], out['verified_example_tx'] or out['verification_method'])
        rows[t] = out
        write_out(rows, topics)
    write_out(rows, topics)
    log('wrote', OUT, 'pinned head', head)


if __name__ == '__main__':
    sys.exit(main())
