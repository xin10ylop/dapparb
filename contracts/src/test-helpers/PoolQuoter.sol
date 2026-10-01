// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IV3LikePool {
    function swap(address recipient, bool zeroForOne, int256 amountSpecified, uint160 sqrtPriceLimitX96, bytes calldata data)
        external
        returns (int256 amount0, int256 amount1);
}

/// @notice Exact-input quote on any Uniswap-V3-style pool (Uniswap V3 and clones, Slipstream, PancakeSwap V3 and
/// clones) by calling swap and reverting inside the callback with the pool's deltas. Used only through eth_call with a
/// state override (never deployed); it lets the bot check its local math on pools that have no official quoter.
contract PoolQuoter {
    uint160 internal constant MIN_SQRT_RATIO_PLUS_ONE = 4295128740;
    uint160 internal constant MAX_SQRT_RATIO_MINUS_ONE = 1461446703485210103287273052203988822378723970341;

    /// @return amountOut output for `amountIn` of the input token; amountInUsed < amountIn when the pool ran out of range
    function quote(address pool, bool zeroForOne, uint256 amountIn) external returns (uint256 amountOut, uint256 amountInUsed) {
        try IV3LikePool(pool).swap(address(this), zeroForOne, int256(amountIn), zeroForOne ? MIN_SQRT_RATIO_PLUS_ONE : MAX_SQRT_RATIO_MINUS_ONE, "") {
            revert("no callback");
        } catch (bytes memory r) {
            if (r.length != 64) {
                assembly {
                    revert(add(r, 32), mload(r))
                }
            }
            (int256 a0, int256 a1) = abi.decode(r, (int256, int256));
            (int256 inDelta, int256 outDelta) = zeroForOne ? (a0, a1) : (a1, a0);
            return (uint256(-outDelta), uint256(inDelta));
        }
    }

    function _bounce(int256 a0, int256 a1) private pure {
        assembly {
            let p := mload(0x40)
            mstore(p, a0)
            mstore(add(p, 32), a1)
            revert(p, 64)
        }
    }

    function uniswapV3SwapCallback(int256 a0, int256 a1, bytes calldata) external pure {
        _bounce(a0, a1);
    }

    function pancakeV3SwapCallback(int256 a0, int256 a1, bytes calldata) external pure {
        _bounce(a0, a1);
    }
}
