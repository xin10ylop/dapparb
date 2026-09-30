URL: https://github.com/bnb-chain/bsc-mev-info/blob/c6ceebbd4ae3c9b33ce139af5005a73857ae67e3/README.md
TITLE: bsc-mev-info README
PUBLISHER: bnb-chain/bsc-mev-info
FETCHED_AT_UTC: 2026-09-30T21:23:54Z (git clone --depth 1 of https://github.com/bnb-chain/bsc-mev-info)
GIT_COMMIT: c6ceebbd4ae3c9b33ce139af5005a73857ae67e3 (commit date 2026-09-17T17:55:59+08:00)
RAW_SHA256: c441b86abfde86498dee0354f4fa4efea64fc1133c63a5d143e2dc981f3d783b
RAW_FILE: raw/bsc-mev-info-readme.md
CONVERSION: verbatim
==============================================================================
# BSC-Mev-Info

BSC-Mev-Info serves as the mev information publicity office, which can publicize the address and domain name information 
of validators and builders.

## Usage

For validators:
1. Add your validator's consensus address and public RPC URL in the `{validator-alias}.toml` file, see an example at mainnet/validators/example.toml.
2. Put the file in specific directory.
3. Submit a PR to the main branch.

For builders:
1. Add your builder's bid address and public RPC URL in the `{builder-alias}.toml` file, see an example at mainnet/builders/example.toml.
2. Put the file in specific directory.
3. Submit a PR to the main branch.
