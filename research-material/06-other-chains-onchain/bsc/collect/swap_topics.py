#!/usr/bin/env python3
"""Build ../census/swap-topics.csv for BSC.

topic0 of every signature below is computed with `cast keccak` (foundry). Each topic0 is then looked up in the
raw census window (../census/raw/chunk-*.jsonl.gz); the first log found (lowest block, then tx index, then log
index) is recorded as the verification example (tx hash, emitter address, block). A topic0 with no log in the
window is kept in the list with an empty verified_example_tx and a note.

Columns: topic0, signature, protocol, source_url, verified_example_tx, example_emitter, example_block,
         verification_note
"""
import csv
import gzip
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "..", "census")
RAW = os.path.join(CENSUS, "raw")
CAST = "/root/.foundry/bin/cast"

GH = "https://github.com/"
SIGS = [
    # --- baseline (task definition) ---
    ("Swap(address,uint256,uint256,uint256,uint256,address)",
     "Uniswap V2 pair / PancakeSwap V2 pair / V2 forks (Biswap, BabySwap, ApeSwap, MDEX, Thena V1 pairs etc.)",
     GH + "Uniswap/v2-core/blob/master/contracts/interfaces/IUniswapV2Pair.sol ; " + GH +
     "pancakeswap/pancake-swap-core/blob/master/contracts/interfaces/IPancakePair.sol ; " + GH +
     "ThenafiBNB/THENA-Contracts/blob/main/contracts/Pair.sol"),
    ("Swap(address,address,int256,int256,uint160,uint128,int24)",
     "Uniswap V3 pool / Algebra V1 (e.g. THENA Fusion) / KyberSwap Elastic (same type list)",
     GH + "Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol ; " + GH +
     "cryptoalgebra/AlgebraV1/blob/master/src/core/contracts/interfaces/pool/IAlgebraPoolEvents.sol ; " + GH +
     "KyberNetwork/ks-elastic-sc/blob/main/contracts/interfaces/pool/IPoolEvents.sol"),
    ("Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)", "PancakeSwap V3 pool",
     GH + "pancakeswap/pancake-v3-contracts/blob/main/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolEvents.sol"),
    ("Swap(address,address,uint256,uint256,uint256,uint256)", "Velodrome/Aerodrome/Solidly V2-style pool",
     GH + "velodrome-finance/contracts/blob/main/contracts/interfaces/IPool.sol"),
    ("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)",
     "Uniswap V4 PoolManager (BSC PoolManager per Uniswap docs: 0x28e2ea090877bf75740558f6bfb36a5ffee9e9df)",
     GH + "Uniswap/v4-core/blob/main/src/interfaces/IPoolManager.sol ; https://docs.uniswap.org/contracts/v4/deployments"),
    ("Swap(bytes32,address,address,uint256,uint256)", "Balancer V2 Vault (and forks emitting the identical event; BSC emitter is not the canonical 0xba12222222228d8ba445958a75a0704d566bf2c8 Vault address)",
     GH + "balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IVault.sol"),
    ("Swap(address,address,address,uint256,uint256,uint256,uint256)", "Balancer V3 Vault",
     GH + "balancer/balancer-v3-monorepo/blob/main/pkg/interfaces/contracts/vault/IVaultEvents.sol"),
    ("TokenExchange(address,int128,uint256,int128,uint256)", "Curve StableSwap (int128 index) / Ellipsis (Curve fork on BSC)",
     GH + "curvefi/curve-contract/blob/master/contracts/pools/3pool/StableSwap3Pool.vy"),
    ("TokenExchange(address,uint256,uint256,uint256,uint256)",
     "Curve CryptoSwap / StableSwap-NG (uint256 index) / PancakeSwap StableSwap (same type list)",
     GH + "curvefi/curve-crypto-contract/blob/master/contracts/tricrypto/CurveCryptoSwap.vy"),
    ("TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)", "Curve tricrypto-ng / twocrypto-ng",
     GH + "curvefi/tricrypto-ng/blob/main/contracts/main/CurveTricryptoOptimizedWETH.vy"),
    ("TokenExchangeUnderlying(address,int128,uint256,int128,uint256)", "Curve metapool / Ellipsis metapool",
     GH + "curvefi/curve-contract/blob/master/contracts/pool-templates/meta/SwapTemplateMeta.vy"),
    # --- BSC local DEXes ---
    ("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24,uint16)",
     "PancakeSwap Infinity CLPoolManager (concentrated liquidity)",
     GH + "pancakeswap/infinity-core/blob/main/src/pool-cl/interfaces/ICLPoolManager.sol"),
    ("Swap(bytes32,address,int128,int128,uint24,uint24,uint16)", "PancakeSwap Infinity BinPoolManager (liquidity book)",
     GH + "pancakeswap/infinity-core/blob/main/src/pool-bin/interfaces/IBinPoolManager.sol"),
    ("Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)",
     "Algebra Integral pool (e.g. THENA V3.3 / other Algebra Integral deployments)",
     GH + "cryptoalgebra/Algebra/blob/master/src/core/contracts/interfaces/pool/IAlgebraPoolEvents.sol"),
    ("DODOSwap(address,address,uint256,uint256,address,address)", "DODO V2 (DVM/DPP/DSP pools)",
     GH + "DODOEX/contractV2/blob/main/contracts/DODOVendingMachine/impl/DVMTrader.sol"),
    ("SellBaseToken(address,uint256,uint256)", "DODO V1 pool",
     GH + "DODOEX/dodo-smart-contract/blob/master/contracts/impl/Trader.sol"),
    ("BuyBaseToken(address,uint256,uint256)", "DODO V1 pool",
     GH + "DODOEX/dodo-smart-contract/blob/master/contracts/impl/Trader.sol"),
    ("Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)", "Trader Joe Liquidity Book v2.1/v2.2 pair",
     GH + "traderjoe-xyz/joe-v2/blob/main/src/interfaces/ILBPair.sol"),
    ("Swap(address,address,address,uint256,uint256,address)", "Wombat Exchange pool",
     GH + "wombat-exchange/v1-core/blob/master/contracts/wombat-core/pool/Pool.sol"),
    ("WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)", "WOOFi WooPPV2",
     GH + "woonetwork/WooPoolV2/blob/main/contracts/interfaces/IWooPPV2.sol"),
    ("Swap(address,address,bool,bool,uint256,uint256,int32)", "Maverick V1 pool",
     "https://api.openchain.xyz/signature-database/v1/lookup?event=0x3b841dc9ab51e3104bda4f61b41e4271192d22cd19da5ee6e292dc8e2744f713 (Maverick V1 IPool source repo not reachable at fetch time)"),
    ("PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)", "Maverick V2 pool",
     GH + "maverickprotocol/v2-common/blob/main/contracts/interfaces/IMaverickV2Pool.sol"),
    ("Swap(address,address,uint24,bool,uint256,uint256,int24)", "iZiSwap (iZUMi) pool",
     GH + "izumiFinance/iZiSwap-core/blob/main/contracts/interfaces/IiZiSwapPool.sol"),
    ("Swap(bool,uint256,uint256,address)", "Fluid DEX T1 pool",
     GH + "Instadapp/fluid-contracts-public/blob/main/contracts/protocols/dex/poolT1/coreModule/events.sol"),
    # --- BSC launchpad bonding curves (token launches) ---
    ("TokenPurchase(address,address,uint256,uint256,uint256,uint256,uint256,uint256)",
     "Four.meme TokenManager2 bonding-curve buy (TokenManager2 0x5c952063c7fc8610ffdb798152d69f0b9550762b)",
     "https://four-meme.gitbook.io/four.meme/protocol-integration ; " + GH +
     "four-meme-community/four-meme-ai/blob/main/skills/four-meme-integration/SKILL.md"),
    ("TokenSale(address,address,uint256,uint256,uint256,uint256,uint256,uint256)",
     "Four.meme TokenManager2 bonding-curve sell",
     "https://four-meme.gitbook.io/four.meme/protocol-integration"),
    ("TokenBought(uint256,address,address,uint256,uint256,uint256,uint256)",
     "Flap Portal bonding-curve buy (Portal 0xe2ce6ab80874fa9fa2aae65d277dd6b8e65c9de0)",
     "https://docs.flap.sh/flap/developers/trade-tokens"),
    ("TokenSold(uint256,address,address,uint256,uint256,uint256,uint256)", "Flap Portal bonding-curve sell",
     "https://docs.flap.sh/flap/developers/trade-tokens"),
]


def keccak(sig):
    return subprocess.check_output([CAST, "keccak", sig], text=True).strip().lower()


def main():
    rows = []
    for sig, proto, src in SIGS:
        rows.append({"topic0": keccak(sig), "signature": sig, "protocol": proto, "source_url": src})
    want = {r["topic0"] for r in rows}
    found = {}
    fns = sorted((fn for fn in os.listdir(RAW) if fn.startswith("chunk-") and fn.endswith(".jsonl.gz")),
                 key=lambda fn: (fn.startswith("chunk-gapfill"), fn))
    for fn in fns:
        if len(found) == len(want):
            break
        with gzip.open(os.path.join(RAW, fn), "rt") as g:
            for line in g:
                d = json.loads(line)
                for rc in d["receipts"]:
                    for lg in rc["logs"]:
                        t = lg["topics"][0].lower() if lg["topics"] else None
                        if t in want and t not in found:
                            found[t] = (rc["transactionHash"], lg["address"].lower(), int(rc["blockNumber"], 16))
    w = json.load(open(os.path.join(CENSUS, "window.json")))
    for r in rows:
        ex = found.get(r["topic0"])
        if ex:
            r["verified_example_tx"], r["example_emitter"], r["example_block"] = ex
            r["verification_note"] = "first log with this topic0 in census window (raw chunks)"
        else:
            r["verified_example_tx"] = r["example_emitter"] = r["example_block"] = ""
            r["verification_note"] = (f"no log with this topic0 in census window blocks {w['start_block']}-"
                                      f"{w['end_block']}; topic0 computed with cast keccak only (unverified on BSC)")
    out = os.path.join(CENSUS, "swap-topics.csv")
    with open(out + ".tmp", "w", newline="") as f:
        cw = csv.DictWriter(f, fieldnames=["topic0", "signature", "protocol", "source_url", "verified_example_tx",
                                           "example_emitter", "example_block", "verification_note"],
                            lineterminator="\n")
        cw.writeheader()
        cw.writerows(rows)
    os.replace(out + ".tmp", out)
    for r in rows:
        print(r["topic0"][:12], bool(r["verified_example_tx"]), r["example_emitter"], r["signature"][:60])


if __name__ == "__main__":
    main()
