#!/usr/bin/env python3
"""Compute topic0 for candidate swap event signatures (cast keccak) and look for one real Base log per topic.
Writes swap-topics.csv (topic0, signature, protocol, source_url, verified_example_tx, verified_example_block, verified_example_emitter, search_note).
Search: eth_getLogs on base.drpc.org, first the newest 100 blocks, then windows of 9,000 blocks walking back from a pinned head, up to MAX_WINDOWS windows.
"""
import csv, json, os, subprocess, sys, time, requests
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'swap-topics.csv')
RPC = 'https://base.drpc.org'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'
S = requests.Session(); S.headers.update({'User-Agent': UA, 'Content-Type': 'application/json'})
MAX_WINDOWS = int(os.environ.get('MAX_WINDOWS', '6'))
WIN = 9000  # superseded: drpc free plan now rejects address-less getLogs over ~100 blocks (see MANIFEST)
CANDS = [
 ('Swap(address,uint256,uint256,uint256,uint256,address)', 'Uniswap V2 and forks (SushiSwap V2, BaseSwap, SwapBased, Solidly V1-style)', 'https://github.com/Uniswap/v2-core/blob/master/contracts/interfaces/IUniswapV2Pair.sol'),
 ('Swap(address,address,int256,int256,uint160,uint128,int24)', 'Uniswap V3 / Aerodrome Slipstream / Sushi V3 / Algebra (v1, Integral 1.0) / Kyber Elastic', 'https://github.com/Uniswap/v3-core/blob/main/contracts/interfaces/pool/IUniswapV3PoolEvents.sol'),
 ('Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)', 'PancakeSwap V3', 'https://github.com/pancakeswap/pancake-v3-contracts/blob/main/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolEvents.sol'),
 ('Swap(address,address,uint256,uint256,uint256,uint256)', 'Aerodrome / Velodrome V2 (Solidly V2-style)', 'https://github.com/aerodrome-finance/contracts/blob/main/contracts/interfaces/IPool.sol'),
 ('Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)', 'Uniswap V4 PoolManager', 'https://github.com/Uniswap/v4-core/blob/main/src/interfaces/IPoolManager.sol'),
 ('Swap(bytes32,address,address,uint256,uint256)', 'Balancer V2 Vault', 'https://github.com/balancer/balancer-v2-monorepo/blob/master/pkg/interfaces/contracts/vault/IVault.sol'),
 ('Swap(address,address,address,uint256,uint256,uint256,uint256)', 'Balancer V3 Vault', 'https://github.com/balancer/balancer-v3-monorepo/blob/main/pkg/interfaces/contracts/vault/IVaultEvents.sol'),
 ('TokenExchange(address,int128,uint256,int128,uint256)', 'Curve StableSwap / StableSwap-NG (int128 indices)', 'https://github.com/curvefi/stableswap-ng/blob/main/contracts/main/CurveStableSwapNG.vy'),
 ('TokenExchange(address,uint256,uint256,uint256,uint256)', 'Curve CryptoSwap v2 (uint256 indices)', 'https://github.com/curvefi/curve-crypto-contract/blob/master/contracts/two/CurveCryptoSwap2ETH.vy'),
 ('TokenExchange(address,uint256,uint256,uint256,uint256,uint256,uint256)', 'Curve Tricrypto-NG / Twocrypto-NG (uint256 indices, fee, packed_price_scale)', 'https://github.com/curvefi/twocrypto-ng/blob/main/contracts/main/CurveTwocryptoOptimized.vy'),
 ('TokenExchangeUnderlying(address,int128,uint256,int128,uint256)', 'Curve metapool / lending pool TokenExchangeUnderlying', 'https://github.com/curvefi/stableswap-ng/blob/main/contracts/main/CurveStableSwapMetaNG.vy'),
 ('PoolSwap(address,address,(uint256,bool,bool,int32),uint256,uint256)', 'Maverick V2 pool', 'https://github.com/maverickprotocol/v2-common (IMaverickV2Pool.PoolSwap)'),
 ('Swap(address,address,bool,bool,uint256,uint256,int32)', 'Maverick V1 pool', 'https://docs.mav.xyz (Maverick V1 IPool.Swap)'),
 ('Swap(address,address,uint24,bytes32,bytes32,uint24,bytes32,bytes32)', 'Trader Joe Liquidity Book v2.1/v2.2 pair', 'https://github.com/traderjoe-xyz/joe-v2/blob/main/src/interfaces/ILBPair.sol'),
 ('DODOSwap(address,address,uint256,uint256,address,address)', 'DODO V2 (DVM/DPP/DSP)', 'https://github.com/DODOEX/contractV2/blob/main/contracts/DODOVendingMachine/impl/DVMTrader.sol'),
 ('WooSwap(address,address,uint256,uint256,address,address,address,uint256,uint256)', 'WOOFi WooPPV2', 'https://github.com/woonetwork/WooPoolV2/blob/main/contracts/interfaces/IWooPPV2.sol'),
 ('Swap(bool,uint256,uint256,address)', 'Fluid DEX (T1 pool)', 'https://github.com/Instadapp/fluid-contracts-public/blob/main/contracts/protocols/dex/poolT1/coreModule/core/main.sol'),
 ('Swap(address,address,int256,int256,uint160,uint128,int24,uint24,uint24)', 'Algebra Integral v1.2+ (overrideFee, pluginFee) forks', 'https://github.com/cryptoalgebra/Algebra/blob/master/src/core/contracts/interfaces/pool/IAlgebraPoolEvents.sol'),
 ('Swap(address,address,uint24,bool,uint256,uint256,int24)', 'iZiSwap pool', 'https://github.com/izumiFinance/iZiSwap-core/blob/main/contracts/iZiSwapPool.sol'),
 ('TokensTraded(address,address,address,uint256,uint256,uint128,bool)', 'Carbon DeFi (Bancor) CarbonController', 'https://github.com/bancorprotocol/carbon-contracts/blob/main/contracts/carbon/CarbonController.sol'),
 ('HookSwap(bytes32,address,int128,int128,uint128,uint128)', 'Uniswap V4 custom-accounting hooks (OpenZeppelin uniswap-hooks standard HookSwap event)', 'https://github.com/OpenZeppelin/uniswap-hooks/blob/master/src/base/BaseCustomAccounting.sol'),
 ('Swap(address,uint256,uint256,uint256,uint256,address,address)', 'UniV2-fork variant with extra address field', '(candidate; searched on Base only)'),
]
def keccak(sig):
    env = dict(os.environ); env['PATH'] = '/root/.foundry/bin:' + env.get('PATH', '')
    return subprocess.check_output(['cast', 'keccak', sig], env=env, text=True).strip().lower()
def rpc(method, params, tries=8):
    back = 1.0
    for i in range(tries):
        try:
            r = S.post(RPC, data=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}), timeout=60)
            if r.status_code in (429, 500, 502, 503, 504):
                raise RuntimeError('http %d' % r.status_code)
            j = r.json()
            if 'error' in j:
                raise RuntimeError(json.dumps(j['error'])[:300])
            return j['result']
        except Exception as e:
            print('retry', method, e, file=sys.stderr); time.sleep(back); back = min(back * 2, 30)
    raise RuntimeError('failed ' + method)
head = int(rpc('eth_blockNumber', []), 16) - 20
print('pinned head', head, file=sys.stderr)
rows = []
for sig, proto, src in CANDS:
    t = keccak(sig)
    ex = ('', '', ''); note = ''
    wins = [(head - 99, head)] + [(head - (w + 1) * WIN + 1, head - w * WIN) for w in range(MAX_WINDOWS)]
    for lo, hi in wins:
        logs = rpc('eth_getLogs', [{'fromBlock': hex(lo), 'toBlock': hex(hi), 'topics': [t]}])
        if logs:
            L = logs[0]; ex = (L['transactionHash'].lower(), str(int(L['blockNumber'], 16)), L['address'].lower())
            note = 'found in blocks %d-%d (%d logs in that window)' % (lo, hi, len(logs)); break
        time.sleep(0.2)
    if not ex[0]:
        note = 'no log found in blocks %d-%d' % (head - MAX_WINDOWS * WIN + 1, head)
    print(t, sig, ex, note, file=sys.stderr)
    rows.append([t, sig, proto, src, ex[0], ex[1], ex[2], note])
with open(OUT, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['topic0', 'signature', 'protocol', 'source_url', 'verified_example_tx', 'verified_example_block', 'verified_example_emitter', 'search_note'])
    w.writerows(rows)
print('wrote', OUT, file=sys.stderr)
