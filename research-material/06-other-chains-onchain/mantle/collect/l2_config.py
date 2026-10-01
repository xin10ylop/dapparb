"""Chain configurations for the additional L2 censuses (added 2026-10-01).

census.py and token_prices.py (identical copies of ../_shared_collect/) keep their chain settings in the dicts
census.CHAINS and token_prices.CFG. census_l2.py and token_prices_l2.py add the entries below to those dicts at run
time and then call the unmodified main() of each script, so the shared method is reused byte for byte.
Keys have the same meaning as in census.py / token_prices.py. Endpoints were checked with
select_l2_chains.py (../rpc-receipts-probe-candidates.jsonl.gz) and by hand (batch support) before launch.
"""

CENSUS_CHAINS = {
    "ink": dict(chain_id=57073, primary="https://ink-rpc.publicnode.com",
                fallbacks=["https://rpc-gel.inkonchain.com", "https://rpc-qnd.inkonchain.com", "https://ink.drpc.org"],
                window_s=3600, end_tag="latest", head_margin=10, batch=8, seg_blocks=600, nominal_interval=1.0,
                sentinel="EVM_CENSUS_INK", extra_logs={}, extra_data_text=False),
    "mantle": dict(chain_id=5000, primary="https://mantle-rpc.publicnode.com",
                   fallbacks=["https://rpc.mantle.xyz", "https://mantle.drpc.org"],
                   window_s=3600, end_tag="latest", head_margin=5, batch=10, seg_blocks=300, nominal_interval=2.0,
                   sentinel="EVM_CENSUS_MANTLE", extra_logs={}, extra_data_text=False),
    "abstract": dict(chain_id=2741, primary="https://api.mainnet.abs.xyz",
                     fallbacks=["https://abstract.drpc.org"],
                     window_s=3600, end_tag="latest", head_margin=10, batch=10, seg_blocks=600, nominal_interval=0.75,
                     sentinel="EVM_CENSUS_ABSTRACT", extra_logs={}, extra_data_text=False),
    "worldchain": dict(chain_id=480, primary="https://worldchain-mainnet.gateway.tenderly.co",
                       fallbacks=["https://480.rpc.thirdweb.com",
                                  "https://sparkling-autumn-dinghy.worldchain-mainnet.quiknode.pro"],
                       window_s=3600, end_tag="latest", head_margin=5, batch=4, seg_blocks=300, nominal_interval=2.0,
                       sentinel="EVM_CENSUS_WORLDCHAIN", extra_logs={}, extra_data_text=False),
    "zksync": dict(chain_id=324, primary="https://mainnet.era.zksync.io",
                   fallbacks=["https://zksync.drpc.org"],
                   window_s=3600, end_tag="latest", head_margin=5, batch=10, seg_blocks=200, nominal_interval=6.0,
                   sentinel="EVM_CENSUS_ZKSYNC", extra_logs={}, extra_data_text=False),
    "soneium": dict(chain_id=1868, primary="https://soneium-rpc.publicnode.com",
                    fallbacks=["https://rpc.soneium.org"],
                    window_s=3600, end_tag="latest", head_margin=5, batch=4, seg_blocks=300, nominal_interval=2.0,
                    sentinel="EVM_CENSUS_SONEIUM", extra_logs={}, extra_data_text=False),
}

# token_prices.py: rpc = endpoints for eth_call decimals()/symbol()/name() (first one first), llama = DefiLlama coins
# API chain prefix, native = DefiLlama coin ids of the native gas token for the 5-minute chart.
TOKEN_CFG = {
    "ink": dict(rpc=["https://ink-rpc.publicnode.com", "https://rpc-gel.inkonchain.com"], llama="ink",
                native=["coingecko:ethereum"]),
    "mantle": dict(rpc=["https://mantle-rpc.publicnode.com", "https://rpc.mantle.xyz"], llama="mantle",
                   native=["coingecko:mantle"]),
    "abstract": dict(rpc=["https://api.mainnet.abs.xyz", "https://abstract.drpc.org"], llama="abstract",
                     native=["coingecko:ethereum"]),
    # worldchain: the Alchemy public endpoint first (it refuses eth_getBlockReceipts but serves eth_call batches).
    # Run 1 (04:20Z, Tenderly gateway first: HTTP 429 to 60-call eth_call batches) and run 2 (04:25Z, thirdweb first:
    # per-item rate-limit errors, then Tenderly 429) were stopped; logs in collect/token_prices.attempt1.log / attempt2.log.
    "worldchain": dict(rpc=["https://worldchain-mainnet.g.alchemy.com/public", "https://480.rpc.thirdweb.com"], llama="wc",
                       native=["coingecko:ethereum"]),
    "zksync": dict(rpc=["https://mainnet.era.zksync.io", "https://zksync.drpc.org"], llama="era",
                   native=["coingecko:ethereum"]),
    "soneium": dict(rpc=["https://soneium-rpc.publicnode.com", "https://rpc.soneium.org"], llama="soneium",
                    native=["coingecko:ethereum"]),
}

# DefiLlama per-chain DEX overview slug for fetch_defillama.py
DEFILLAMA_SLUG = {"ink": "ink", "mantle": "mantle", "abstract": "abstract", "worldchain": "world-chain",
                  "zksync": "zksync-era", "soneium": "soneium"}
