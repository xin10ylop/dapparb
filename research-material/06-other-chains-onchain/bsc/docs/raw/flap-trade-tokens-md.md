> For the complete documentation index, see [llms.txt](https://docs.flap.sh/flap/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.flap.sh/flap/developers/wallet-and-terminal-and-bot-developers/trade-tokens.md).

# Trade Tokens

## Get A Quote

{% hint style="warning" %}
If a token is already migrated, you can still get a quote using the following method. However, we will always use the pool that the token has migrated to, this may not be the best quote.\
\
You can also do an off-chain quote to save the RPC calls. Check the end of this document to learn more about the off-chain quote.
{% endhint %}

To get a quote , we call the `quoteExactInput` function:

```solidity
/// @notice Parameters for quoting the output amount for a given input
struct QuoteExactInputParams {
    /// @notice The address of the input token (use address(0) for native asset)
    address inputToken;
    /// @notice The address of the output token (use address(0) for native asset)
    address outputToken;
    /// @notice The amount of input token to swap (in input token decimals)
    uint256 inputAmount;
}

/// @notice Quote the output amount for a given input
/// @param params The quote parameters
/// @return outputAmount The quoted output amount
/// @dev refer to the swapExactInput method for the scenarios
function quoteExactInput(QuoteExactInputParams calldata params) external returns (uint256 outputAmount);
```

Note: the `quoteExactInput` method is not a view function, but we don’t need to send a transaction to get the quote (an `eth_call` or the simulation in viem will do the work) .

Here are the possible scenarios:

* **When the quote token is the native gas token (BNB or ETH):**
  * buy a token:
    * `inputToken` is zero address, representing the gas token
    * `outputToken` is the token you wanna buy
  * sell a token:
    * `inputToken` is the token you wanna sell
    * `outputToken` is zero address, representing the gas token
* **When the quote token is not the native gas token (taking USD1 as an example)** :
  * buy a token with USD1:
    * `inputToken` is USD1 address
    * `outputToken` is the token you wanna buy
  * **buy with native gas token** (only when the token’s `nativeToQuoteSwap` is enabled , check below to inspect if a token’s quote token supports `nativeToQuoteSwap` ):
    * `inputToken` is zero address, representing the gas token
    * `outputToken` is the token you wanna buy
    * under the hood, we will help you swap BNB for for USD1 on PancakeSwap as an intermediate step in the contract.
  * sell a token:
    * `inputToken` is the token you wanna sell
    * `outputToken` is USD1
  * Sell directly from token to BNB is also supported, but we will not support this in our UI.

## Swap

To swap we call the `swapExactInput` method:

```solidity
/// @notice Parameters for swapping exact input amount for output token
struct ExactInputParams {
    /// @notice The address of the input token (use address(0) for native asset)
    address inputToken;
    /// @notice The address of the output token (use address(0) for native asset)
    address outputToken;
    /// @notice The amount of input token to swap (in input token decimals)
    uint256 inputAmount;
    /// @notice The minimum amount of output token to receive
    uint256 minOutputAmount;
    /// @notice Optional permit data for the input token (can be empty)
    bytes permitData;
}

/// @notice Swap exact input amount for output token
/// @param params The swap parameters
/// @return outputAmount The amount of output token received
/// @dev Here are some possible scenarios:
///   If the token's reserve is BNB or ETH (i.e: the quote token is the native gas token):
///      - BUY: input token is address(0), output token is the token address
///      - SELL: input token is the token address, output token is address(0)
///   If the token's reserve is another ERC20 token (eg. USD*, i.e, the quote token is an ERC20 token):
///      - BUY with USD*: input token is the USD* address, output token is the token address
///      - SELL for USD*: input token is the token address, output token is the USD* address
///      - BUY with BNB or ETH: input token is address(0), output token is the token address.
///        (Note: this requires an internal swap to convert BNB/ETH to USD*, nativeToQuoteSwap must be anabled for this quote token)
/// Note: Currently, this method only supports trading tokens that are still in the bonding curve state.
///       However, in the future, we may also support trading tokens that are already in DEX state.
function swapExactInput(ExactInputParams calldata params) external payable returns (uint256 outputAmount);
```

This is quite straightforward after getting a quote.

#### How to construct the permitData in ExactInputParams ?

When selling the tokens, you can use our permitData field to save an approve transaction. The permitData field is the abi encoding of each field from the Permit struct plus the EIP712 signature. Check the `genPermitData` below :

```typescript

import { Account, Address, createWalletClient, encodeAbiParameters, encodeDeployData, encodeFunctionData, formatEther, getContract, getContractAddress, HDAccount, Hex, hexToBigInt, http, keccak256, parseEther, parseGwei, parseSignature, parseTransaction, parseUnits, PublicClient, serializeTransaction, toBytes, toHex } from 'viem';

// generate ERC20 permit data for token (returns all fields, not abi encoded)
async function genPermitDataNoPack(account: Account, token: `0x${string}`, spender: `0x${string}`, amount: bigint, client: PublicClient) {
  const tokenInst = getContract({
    abi: [
      {
        type: "function",
        name: "name",
        inputs: [],
        outputs: [{ name: "", type: "string" }],
        stateMutability: "view"
      },
      {
        type: "function",
        name: "nonces",
        inputs: [{ name: "", type: "address" }],
        outputs: [{ name: "", type: "uint256" }],
        stateMutability: "view"
      },
      {
        type: "function",
        name: "permit",
        inputs: [
          { name: "owner", type: "address" },
          { name: "spender", type: "address" },
          { name: "value", type: "uint256" },
          { name: "deadline", type: "uint256" },
          { name: "v", type: "uint8" },
          { name: "r", type: "bytes32" },
          { name: "s", type: "bytes32" }
        ],
        outputs: [],
        stateMutability: "nonpayable"
      }
    ],
    address: token,
    client,
  });

  const nonce = await tokenInst.read.nonces([account.address]) as bigint;
  const name = await tokenInst.read.name() as string;
  const deadline = BigInt(Date.now() + 10 * 60 * 1000); // 10 minutes ttl

  const sig = await (account as HDAccount).signTypedData({
    domain: {
      name,
      version: "1",
      chainId: bsc.id, // or bsc.id for mainnet
      verifyingContract: token as `0x${string}`
    },
    types: {
      Permit: [
        { name: "owner", type: "address" },
        { name: "spender", type: "address" },
        { name: "value", type: "uint256" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
      ]
    },
    primaryType: "Permit",
    message: {
      owner: account.address,
      spender: spender,
      value: amount,
      nonce,
      deadline,
    }
  });

  const { r, s, v } = parseSignature(sig) as { r: `0x${string}`, s: `0x${string}`, v: bigint, yParity: number };

  return {
    owner: account.address,
    spender,
    value: amount,
    nonce,
    deadline,
    v: Number(v),
    r,
    s
  };
}

// generate ERC20 permit data for token (returns abi encoded data)
async function genPermitData(account: Account, token: `0x${string}`, amount: bigint, client: PublicClient) {
  const permitFields = await genPermitDataNoPack(account, token, flapConfig.portal, amount, client);
  const data = encodeAbiParameters([
            { name: "owner", type: "address" },
            { name: "spender", type: "address" },
            { name: "value", type: "uint256" },
            { name: "deadline", type: "uint256" },
            { name: "v", type: "uint8" },
            { name: "r", type: "bytes32" },
            { name: "s", type: "bytes32" }
          ],
          [permitFields.owner, permitFields.spender, permitFields.value, permitFields.deadline, permitFields.v, permitFields.r, permitFields.s]);
  return data;
}
```

## Events

### `TokenBought`

Emitted when a user buys tokens through the Portal.

```solidity
event TokenBought(
    uint256 ts,
    address token,
    address buyer,
    uint256 amount,
    uint256 eth,
    uint256 fee,
    uint256 postPrice
);
```

**Parameters:**

* `ts`: Timestamp of the trade.
* `token`: Address of the token bought.
* `buyer`: Address of the buyer.
* `amount`: Amount of tokens bought.
* `eth`: Amount of ETH (or quote token) spent.
* `fee`: Amount of ETH (or quote token) spent as a fee.
* `postPrice`: Price of the token after this trade.

**When emitted:**\
Whenever a user successfully buys tokens via the Portal.

### `TokenSold`

Emitted when a user sells tokens through the Portal.

```solidity
event TokenSold(
    uint256 ts,
    address token,
    address seller,
    uint256 amount,
    uint256 eth,
    uint256 fee,
    uint256 postPrice
);
```

**Parameters:**

* `ts`: Timestamp of the trade.
* `token`: Address of the token sold.
* `seller`: Address of the seller.
* `amount`: Amount of tokens sold.
* `eth`: Amount of ETH (or quote token) received.
* `fee`: Amount of ETH (or quote token) deducted as a fee.
* `postPrice`: Price of the token after this trade.

**When emitted:**\
Whenever a user successfully sells tokens via the Portal.

### `LaunchedToDEX`

Emitted when a token finishes its bonding-curve phase and is launched to the target DEX.

```solidity
event LaunchedToDEX(address token, address pool, uint256 amount, uint256 eth);
```

**Parameters:**

* `token`: Address of the token being migrated.
* `pool`: Compatibility field for the DEX target.
* `amount`: Amount of token liquidity added.
* `eth`: Amount of quote-token liquidity added.

{% hint style="info" %}
For classic `V2_MIGRATOR` and `V3_MIGRATOR` launches, `pool` is the actual pool address.

For `PCS_INFINITY_CL_MIGRATOR`, `pool` is the PancakeSwap Infinity vault address.

For `V4_UNI_MIGRATOR`, `pool` is the Uniswap PoolManager address.

This is kept mainly for compatibility with older indexers. For these two CL-style migrators, the actual pool identifier should be read from `FlapTokenCLPoolCreated`.
{% endhint %}

### `FlapTokenCLPoolCreated`

This event is only relevant for the concentrated-liquidity launch paths: **PancakeSwap Infinity CL** and **Uniswap v4**.

```solidity
/// @notice emitted when a new CL pool is created for a token
/// @param token The address of the token
/// @param poolId The ID of the created CL pool
/// @param sqrtPriceX96 The initial sqrt price used to initialize the CL pool
event FlapTokenCLPoolCreated(address token, bytes32 poolId, uint160 sqrtPriceX96);
```

**Parameters:**

* `token`: Address of the launched token.
* `poolId`: The CL pool ID. For `PCS_INFINITY_CL_MIGRATOR` and `V4_UNI_MIGRATOR`, this is the value you should index and store as the real pool identifier.
* `sqrtPriceX96`: The initial sqrt price used to initialize the CL pool.

**When emitted:**\
Emitted when the token is launched through `PCS_INFINITY_CL_MIGRATOR` or `V4_UNI_MIGRATOR` and the CL pool is initialized.

### FlapTokenProgressChanged

{% hint style="warning" %}
This event is available since v4.12.1
{% endhint %}

Whenever a token's progress changes, the `FlapTokenProgressChanged` event will be emitted. Note that the `newProgress` is in `wad` (i.e, with 18 decimals, 1 ether = 100%).

```solidity
/// @notice emitted when the progress of a token changes
/// @param token The address of the token
/// @param newProgress The new progress value in Wad
event FlapTokenProgressChanged(address token, uint256 newProgress);
```

## How To Do An Off-Chain Quote?

### \[Off-Chain Quote] 1. The Preliminary

The preliminary steps to quote off-chain is to get the info of a token first. You can either use the methods provided by our smart contract (i.e: [getTokenV6 or getTokenV7](https://github.com/flap-sh/gitbook/tree/main/developers/wallet-and-terminal-and-bot-developers/inspect-a-token/README.md) ), or you can build your indexer by indexing the following events:

* `TokenCreated`: This event gives us the basic info of the token
* `TokenCurveSet` and `TokenCurveSetV2`: We use these events to determine our bonding curve parameters.
* `TokenDexSupplyThreshSet`: this event gives us the circulating supply threshold for the token be migrated.
* `FlapTokenCirculatingSupplyChanged`: This event gives us the current circulating supply of the token.
* `LaunchedToDEX` : This event indicates that the token has been launched to a decentralized exchange (DEX), and the bonding curve equation ceases to be valid. For `PCS_INFINITY_CL_MIGRATOR` and `V4_UNI_MIGRATOR`, note that the `pool` field is a compatibility address (Infinity vault / PoolManager) rather than the final CL pool ID.
* `FlapTokenTaxSet` : (optional), if a token does not emit this event, the tax is 0 or it is not a tax token.
* `FlapTokenProgressChanged` : emitted when the bonding curve progress of a token changes
* `FlapTokenCLPoolCreated` : For `PCS_INFINITY_CL_MIGRATOR` and `V4_UNI_MIGRATOR`, use this event's `poolId` as the real CL pool identifier.

### \[Off-Chain Quote] 2. The Curve Library

With the bonding curve parameters (either a single `r` from `TokenCurveSet` or the full set (`r`, `h`, `k`) from `TokenCurveSetV2`), you can construct a curve instance. Here are the reference typescript and solidity code. You can always feed the code to your AI (Claude or others), and ask them to help you to convert to your preferred programming language:

* The legacy curve is a special case of the new curve where h = 0. For constructing a legacy curve, we can pass only `r` as the parameter.
* For latest curve, we should pass all the parameters (`r`, `h`, `k`).

```tsx

import { Decimal } from "decimal.js";

const BILLION: Decimal = new Decimal("1000000000");

// The latest curve is CDPV2
export class CDPV2 {
  // the initial virtual reserve
  private r: number;
  private h: number;
  private k: number;

  static defaultDexSupplyThreshold() {
    return new Decimal(8e8);
  }

  static getCurve(r: number, h?: number, k?: number): CDPV2 {
    if (h == null) {
      return new CDPV2(r, 0, 1e9 * r);
    }
    return new CDPV2(r, h, k);
  }

  constructor(r: number, h: number = 0, k: number = 0) {
    this.r = r;
    this.h = h;
    this.k = k;
  }

  estimateSupply(reserve: string): Decimal {
    // s = 1e9 + h - k/(r + eth)
    if (!reserve) return new Decimal(0);
    return new Decimal(BILLION).add(this.h).sub(
            new Decimal(this.k).div(new Decimal(reserve).add(this.r))
    );
  }

  estimateReserve(amount: string): Decimal {
    // eth = k/(h + 1e9 - s) - r
    if (!amount) return new Decimal(0);
    return new Decimal(this.k)
            .div(new Decimal(BILLION).add(this.h).sub(new Decimal(amount)))
            .sub(this.r);
  }

  mc(reserve: string): Decimal {
    return this.fdv(this.totalSupply(reserve).toString());
  }

  price(supply: string): Decimal {
    // Price: k/(h + 1e9 - s)^2
    const denominator = new Decimal(BILLION).add(this.h).sub(new Decimal(supply || 0));
    return new Decimal(this.k).div(denominator.pow(2));
  }

  fdv(supply: string): Decimal {
    return this.price(supply).mul(new Decimal(BILLION));
  }
}
```

The solidity version of the curve lib:

```solidity
// SPDX-License-Identifier: MIT

pragma solidity ^0.8.13;

import {FixedPointMathLib} from "solady/utils/FixedPointMathLib.sol";

/// @title constant product bonding curve
/// @author The Flap Team
/// @dev v2
///
/// Spec:
///   - max supply: 1 Billion tokens
///   - The constant product equation is :
///         (1e9 + h  - s) * (eth + r) = k
///      - s is the current circulating supply of the token
///      - eth is the current eth reserve
///      - special case: When h = 0, k = r * 1e9
///   - estimateSupply(estimate s given eth): s = 1e9 + h - k/(r + eth)
///   - estimateReserve(estimate eth given s): eth =  k/(h + 1e9 - s) - r
///   - price estimation:  k/(h + 1e9 - s)**2
library LibCurve {
  /// @notice The curve type is represented by a struct
  /// refer to Uniswap V3 white paper.
  struct Curve {
    uint256 r; // Virtual ETH reserve
    uint256 h; // Virtual token reserve
    uint256 k; // The square of the virtual Liquidity
  }

  // The total supply of the token
  uint256 public constant TOTAL_SUPPLY = 1_000_000_000 ether;

  // custom error type

  /// @notice error if the new supply is greater than the total supply
  error SupplyExceedsTotalSupply(uint256 newSupply);

  /// @notice error if reserve is greater than the max reserve
  error ReserveExceedsMaxReserve(uint256 reserve);

  // @notice Return the estimate supply given the reserve amount
  /// @param reserve  The reserve amount
  /// @dev The resulting supply is rounded down and may even subtract small amount
  ///
  ///      This function is used when a user wants to buy tokens,
  ///      a rounded down value is more favorable to the protocol.
  function estimateSupply(Curve memory curve, uint256 reserve) internal pure returns (uint256 supply) {
    // s = 1e9 + h - k/(r + eth)
    // Round down for protocol safety when buying
    supply = TOTAL_SUPPLY + curve.h - FixedPointMathLib.divWadUp(curve.k, curve.r + reserve);
  }

  /// @notice estimate the reserve given the supply
  /// @dev This function returns a roundup value, because we want the following invariant to hold:
  ///         currReserve >= estimateReserve_without_roudup(currSupply)
  ///
  ///      This function is used when a user wants to sell tokens, a rounded up value
  ///      is more favorable to the protocol.
  function estimateReserve(Curve memory curve, uint256 supply) internal pure returns (uint256 reserve) {
    if (supply > TOTAL_SUPPLY) {
      revert SupplyExceedsTotalSupply(supply);
    }

    // eth = k/(h + 1e9 - s) - r
    // Round up for protocol safety when selling
    reserve = FixedPointMathLib.divWadUp(curve.k, TOTAL_SUPPLY + curve.h - supply) - curve.r;
  }

  /// @notice price (wei) of a token (1e18) if you buy/sell inifinitesimal amount at current supply
  function price(Curve memory curve, uint256 supply) internal pure returns (uint256) {
    // Price: k/(h + 1e9 - s)^2
    uint256 denominator = TOTAL_SUPPLY + curve.h - supply;

    if (denominator < 1e9 + 1) {
      return type(uint256).max;
    }

    // Calculate (h + 1e9 - s)^2 using mulWad for precision
    uint256 denominator_squared = FixedPointMathLib.mulWad(denominator, denominator);
    return FixedPointMathLib.divWad(curve.k, denominator_squared);
  }

  // helper from r to curve
  function fromR(uint256 r) internal pure returns (Curve memory) {
    // legacy curve: h = 0 and k = r * TOTAL_SUPPLY
    return Curve({r: r, h: 0, k: FixedPointMathLib.mulWad(r, TOTAL_SUPPLY)});
  }

  // helper from r,h,k to curve
  function fromRHK(uint256 r, uint256 h, uint256 k) internal pure returns (Curve memory) {
    return Curve({r: r, h: h, k: k});
  }

  /// @notice Return the estimate supply given the reserve amount with support for different reserve token decimals
  /// @param curve The curve parameters
  /// @param reserve The reserve amount
  /// @param reserveDecimals The number of decimals of the reserve token (must be <= 18)
  /// @dev The resulting supply is rounded down, same as estimateSupply
  ///      This function is used when a user wants to buy tokens,
  ///      a rounded down value is more favorable to the protocol.
  function estimateSupplyV2(Curve memory curve, uint256 reserve, uint8 reserveDecimals)
  internal
  pure
  returns (uint256 supply)
  {
    if (reserveDecimals > 18) {
      revert("Reserve decimals must be <= 18");
    }

    if (reserveDecimals == 18) {
      // If reserve token has 18 decimals, use the original estimateSupply function
      return estimateSupply(curve, reserve);
    }

    // Adjust the reserve to 18 decimals
    uint256 scaleFactor = 10 ** (18 - reserveDecimals);
    uint256 scaledReserve = reserve * scaleFactor;

    // Use the adjusted reserve amount
    supply = TOTAL_SUPPLY + curve.h - FixedPointMathLib.divWadUp(curve.k, curve.r + scaledReserve);
  }

  /// @notice Estimate the reserve given the supply with support for different reserve token decimals
  /// @param curve The curve parameters
  /// @param supply The token supply
  /// @param reserveDecimals The number of decimals of the reserve token (must be <= 18)
  /// @dev This function returns a roundup value, same as estimateReserve
  ///      This function is used when a user wants to sell tokens, a rounded up value
  ///      is more favorable to the protocol.
  function estimateReserveV2(Curve memory curve, uint256 supply, uint8 reserveDecimals)
  internal
  pure
  returns (uint256 reserve)
  {
    if (reserveDecimals > 18) {
      revert("Reserve decimals must be <= 18");
    }

    if (supply > TOTAL_SUPPLY) {
      revert SupplyExceedsTotalSupply(supply);
    }

    if (reserveDecimals == 18) {
      // If reserve token has 18 decimals, use the original estimateReserve function
      return estimateReserve(curve, supply);
    }

    // Calculate the reserve in 18 decimals
    uint256 scaledReserve = FixedPointMathLib.divWadUp(curve.k, TOTAL_SUPPLY + curve.h - supply) - curve.r;

    // Convert the reserve from 18 decimals to the actual reserve decimals
    uint256 scaleFactor = 10 ** (18 - reserveDecimals);

    // Divide scaled reserve by scaleFactor (rounding up)
    // For rounding up division: (a + b - 1) / b
    reserve = (scaledReserve + scaleFactor - 1) / scaleFactor;
  }
}
```

Note that the curve has the following methods:

* `estimateSupply(reserve: string)`: Estimates the token circulating supply given the reserve amount.
* `estimateReserve(amount: string)`: Estimates the reserve amount given the token’s circulating supply.

### \[Off-Chain Quote] 3. Quote With The Curve Instance

We will use the typescript pseudo code to demonstrate how to quote with the curve instance.

**Case1: Buy 1 BNB Value of Token**

```tsx

//// Values From your Indexer or getTokenV6/V7

// current circulating supply 
// This can be obtained from getTokenV6 or the FlapTokenCirculatingSupplyChanged event.
let curr_circulating_supply;
// The circulating supply threshold for the token to be migrated to DEX
// Typicially, this is 800M 
// This can be obtained from getTokenV6 or the TokenDexSupplyThreshSet event. 
let dex_supply_threshold = 800_000_000;

// The input bnb amount 
let input_bnb = 1;

//// Compute the Quote 

// We cannot buy more than the dex_supply_threshold on the bonding curve 
// The max_reserve is the cap of the reserve 
let max_reserve = curve.estimateReserve(dex_supply_threshold);
// We estimate the current reserve from the circulating supply  
let curr_reserve = curve.estimateReserve(curr_circulating_supply);

// protocol fee on BNB chain is 1% 
let fee = 0.01; // 1% fee 

// Charge a 1% fee on the input bnb. 
let input_after_fee = input_bnb * (0.99);

// If the user pays more than required, we will automatically refund the user 
let new_reserve = curr_reserve + min(input_after_fee, max_reserve - curr_reserve);
// estimate new circulating supply from new reserve 
let new_circulating_supply = curve.estimateSupply(new_reserve);

// The diff of circulating supply is the output token amount 
let output_amt = new_circulating_supply - curr_circulating_supply; 
```

**Case 2: Sell 1M token for bnb**

```tsx

//// From Indexer Or getTokenV6/V7 

// current circulating supply 
let curr_circulating_supply;
// The circulating supply threshold for the token to be migrated to DEX
// Typicially, this is 800M 
// This can be obtained from getTokenV6/V7 or the TokenDexSupplyThreshSet event.
let dex_supply_threshold;

// BNB fee 
let fee = 0.01; // 1% fee

// The input token amount
let input_token_amt = 1_000_000;

// estimate the current reserve 
let curr_reserve = curve.estimateReserve(curr_circulating_supply);

// estimate the new resereve 
let new_reserve = curve.estimateReserve(curr_circulating_supply - input_token_amt);

// The diff is the output amount without deducting the fee 
let output_eth_before_fee =  curr_reserve - new_reserve;


// we take 1% fee from the quote token 
let output_eth = output_eth_before_fee * (0.99);
```

### \[Off-Chain Quote] 4. Quote for tax tokens

If a token has tax, we also charge the tax on the bonding curve. For off-chain quotes, this means you should **add the tax rate to the protocol fee**.

* Effective fee = protocol fee (1%) + token tax rate
* Tax rate can be read from `getTokenV6` / `getTokenV7`, or indexed from the `FlapTokenTaxSet` event

Below are the same examples as above, updated for tax tokens. You can also read the dedicated tax guide at [developers/basic-and-mechanism/flap-tax-token/prebond-tax.md](/flap/developers/basic-and-mechanism/flap-tax-token/prebond-tax.md).

**Case 1: Buy 1 BNB value of token (tax token)**

```tsx
//// Values From your Indexer or getTokenV6/V7

// current circulating supply 
// This can be obtained from getTokenV6 or the FlapTokenCirculatingSupplyChanged event.
let curr_circulating_supply;
// The circulating supply threshold for the token to be migrated to DEX
// Typicially, this is 800M 
// This can be obtained from getTokenV6 or the TokenDexSupplyThreshSet event. 
let dex_supply_threshold = 800_000_000;
// The token's tax rate
// This can be obtained from getTokenV6 or the FlapTokenTaxSet event from the Portal
let tax = 0;

// The input bnb amount 
let input_bnb = 1;

//// Compute the Quote 

// We cannot buy more than the dex_supply_threshold on the bonding curve 
// The max_reserve is the cap of the reserve 
let max_reserve = curve.estimateReserve(dex_supply_threshold);
// We estimate the current reserve from the circulating supply  
let curr_reserve = curve.estimateReserve(curr_circulating_supply);

// Effective fee = 1% protocol fee + tax
let fee = 0.01 + tax;

// Charge the fee on the input bnb. 
let input_after_fee = input_bnb * (1 - fee);

// If the user pays more than required, we will automatically refund the user 
let new_reserve = curr_reserve + min(input_after_fee, max_reserve - curr_reserve);
// estimate new circulating supply from new reserve 
let new_circulating_supply = curve.estimateSupply(new_reserve);

// The diff of circulating supply is the output token amount 
let output_amt = new_circulating_supply - curr_circulating_supply; 
```

**Case 2: Sell 1M token for BNB (tax token)**

```tsx
//// From Indexer Or getTokenV6/V7 

// current circulating supply 
let curr_circulating_supply;
// The circulating supply threshold for the token to be migrated to DEX
// Typicially, this is 800M 
// This can be obtained from getTokenV6/V7 or the TokenDexSupplyThreshSet event.
let dex_supply_threshold;
// The token's tax rate 
// This can be obtained from getTokenV6 or the FlapTokenTaxSet event from the Portal 
let tax = 0.03;

// BNB fee 
// Effective fee: 1% protocol + tax
let fee = 0.01 + tax;

// The input token amount
let input_token_amt = 1_000_000;

// estimate the current reserve 
let curr_reserve = curve.estimateReserve(curr_circulating_supply);

// estimate the new reserve 
let new_reserve = curve.estimateReserve(curr_circulating_supply - input_token_amt);

// The diff is the output amount without deducting the fee 
let output_eth_before_fee =  curr_reserve - new_reserve;

// apply the fee on the quote token 
let output_eth = output_eth_before_fee * (1 - fee);
```
