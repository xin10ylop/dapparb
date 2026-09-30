"""Shared JSON-RPC helper for the BSC collectors.

- per-endpoint in-flight cap (semaphore), default 3 (<= 4 required by task rules)
- retries on HTTP 429/5xx, timeouts, connection errors, JSON-RPC errors with exponential backoff
- rotates endpoints on failure; an endpoint that answers 'archive' / 'pruned' / 'missing trie' style
  errors for a request is skipped for that request.
"""
import itertools
import json
import os
import random
import threading
import time

import requests

os.environ.setdefault("REQUESTS_CA_BUNDLE", "/root/.ccr/ca-bundle.crt")

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

# endpoint -> max in-flight
DEFAULT_ENDPOINTS = {
    "https://bsc-dataseed.bnbchain.org": 3,
    "https://bsc-dataseed1.bnbchain.org": 2,
    "https://bsc-dataseed2.bnbchain.org": 2,
    "https://bsc-dataseed3.bnbchain.org": 2,
    "https://bsc-dataseed4.bnbchain.org": 2,
    "https://bsc-dataseed1.defibit.io": 3,
    "https://bsc-dataseed1.ninicoin.io": 3,
}
# publicnode refuses receipts older than ~9k blocks ("Archive requests require a personal token");
# it is only used as a fallback by the collectors.
FALLBACK_ENDPOINTS = {
    "https://bsc-rpc.publicnode.com": 3,
}

_tls = threading.local()


def _session():
    s = getattr(_tls, "s", None)
    if s is None:
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Content-Type": "application/json"})
        _tls.s = s
    return s


class RpcError(Exception):
    pass


class Pool:
    def __init__(self, endpoints=None, fallback=None, timeout=45, log=None):
        self.endpoints = dict(endpoints or DEFAULT_ENDPOINTS)
        self.fallback = dict(fallback if fallback is not None else FALLBACK_ENDPOINTS)
        allep = {**self.endpoints, **self.fallback}
        self.sem = {u: threading.BoundedSemaphore(n) for u, n in allep.items()}
        self.cool = {u: 0.0 for u in allep}  # endpoint cooldown-until timestamps
        self.stats = {u: {"ok": 0, "err": 0} for u in allep}
        self.lock = threading.Lock()
        self.rr = itertools.cycle(list(self.endpoints))
        self.timeout = timeout
        self.log = log or (lambda *a: None)

    def _pick(self, exclude):
        now = time.time()
        cands = [u for u in self.endpoints if u not in exclude and self.cool[u] <= now]
        if not cands:
            cands = [u for u in self.fallback if u not in exclude and self.cool[u] <= now]
        if not cands:
            return None
        with self.lock:
            for _ in range(len(self.endpoints)):
                u = next(self.rr)
                if u in cands:
                    return u
        return random.choice(cands)

    def call(self, method, params, max_attempts=40, validate=None):
        """Returns (result, endpoint). Raises RpcError after max_attempts."""
        exclude = set()
        last = None
        for attempt in range(max_attempts):
            u = self._pick(exclude)
            if u is None:
                exclude.clear()
                time.sleep(min(30, 0.5 * (2 ** min(attempt, 6))) + random.random())
                continue
            with self.sem[u]:
                try:
                    r = _session().post(u, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                                                            "params": params}), timeout=self.timeout)
                    code = r.status_code
                    body = r.text
                except Exception as e:  # timeouts, connection resets
                    code, body = None, repr(e)[:300]
            if code == 200:
                try:
                    j = json.loads(body)
                except Exception:
                    j = None
                if isinstance(j, dict) and "result" in j and j["result"] is not None:
                    res = j["result"]
                    if validate is not None:
                        ok, why = validate(res)
                        if not ok:
                            last = f"{u} validation: {why}"
                            self.stats[u]["err"] += 1
                            exclude.add(u)
                            time.sleep(0.3 * (attempt + 1))
                            continue
                    self.stats[u]["ok"] += 1
                    return res, u
                last = f"{u} 200 body={body[:300]}"
                low = body.lower()
                if any(k in low for k in ("archive", "pruned", "missing trie", "header not found",
                                          "not found", "unknown block")):
                    exclude.add(u)
                    continue
                if "result" in (j or {}) and j["result"] is None:
                    # null result: node does not have it (yet); try another endpoint
                    exclude.add(u)
                    time.sleep(0.5)
                    continue
            else:
                last = f"{u} http={code} body={str(body)[:300]}"
                low = str(body).lower()
                if code == 403 and "archive" in low:
                    exclude.add(u)
                    continue
            self.stats[u]["err"] += 1
            # backoff on 429 / 5xx / network errors
            backoff = min(60, 0.5 * (2 ** min(attempt, 7))) + random.random()
            if code == 429 or code is None or (code and code >= 500):
                self.cool[u] = time.time() + backoff
            exclude.add(u)
            if len(exclude) >= len(self.endpoints) + len(self.fallback):
                exclude.clear()
                time.sleep(backoff)
        raise RpcError(f"{method} {params} failed after {max_attempts} attempts; last={last}")
