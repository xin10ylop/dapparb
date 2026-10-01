#!/usr/bin/env python3
"""Runs the unmodified shared token_prices.py for the additional L2 chains (added 2026-10-01).

Adds l2_config.TOKEN_CFG to token_prices.CFG, then calls token_prices.main() with the same command-line arguments
(--chain, --out, --smoke). token_prices.py must be in the same directory (identical copy of
../_shared_collect/token_prices.py).
usage: python3 -B token_prices_l2.py --chain ink --out ..
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_prices  # noqa: E402
import l2_config  # noqa: E402

for k, v in l2_config.TOKEN_CFG.items():
    if k in token_prices.CFG:
        raise SystemExit("chain %s already defined in token_prices.py" % k)
    token_prices.CFG[k] = dict(v)

if __name__ == "__main__":
    token_prices.main()
