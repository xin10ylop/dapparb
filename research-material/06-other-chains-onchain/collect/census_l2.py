#!/usr/bin/env python3
"""Runs the unmodified shared census.py for the additional L2 chains (added 2026-10-01).

Adds l2_config.CENSUS_CHAINS to census.CHAINS, then calls census.main() with the same command-line arguments
(--chain, --out, --workers, --smoke, --seg-blocks, --part-limit-mb). census.py must be in the same directory
(identical copy of ../_shared_collect/census.py).
usage: python3 -B census_l2.py --chain ink --out ..
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402
import l2_config  # noqa: E402

for k, v in l2_config.CENSUS_CHAINS.items():
    if k in census.CHAINS:
        raise SystemExit("chain %s already defined in census.py" % k)
    census.CHAINS[k] = dict(v)

if __name__ == "__main__":
    census.main()
