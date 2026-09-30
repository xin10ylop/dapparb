// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IERC20, IV3Pool} from "../interfaces/IPools.sol";

/// @dev Test helper: sells `amount` of token0 into a V3 pool to move its price (used to manufacture arbs on forks).
contract Pusher {
    function push(address pool, uint256 amount) external {
        IV3Pool(pool).swap(address(this), true, int256(amount), 4295128740, abi.encode(IV3Pool(pool).token0()));
    }

    function uniswapV3SwapCallback(int256 a0, int256 a1, bytes calldata data) external {
        address token = abi.decode(data, (address));
        IERC20(token).transfer(msg.sender, a0 > 0 ? uint256(a0) : uint256(a1));
    }
}
