// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test, console2} from "forge-std/Test.sol";
import {ArbExecutor} from "../src/ArbExecutor.sol";
import {IERC20, IV3Pool} from "../src/interfaces/IPools.sol";

/// @notice Fork tests for the Uniswap V4 hop: nested (inside a V3 flash swap) and as the flash hop itself,
///         including native-ETH pools bridged through WETH.
contract ArbExecutorV4Test is Test {
    address constant WETH = 0x4200000000000000000000000000000000000006;
    address constant CBBTC = 0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf;
    address constant USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913;
    address constant POOL_MANAGER = 0x498581fF718922c3f8e6A244956aF099B2652b2b;

    uint8 constant KIND_V3 = 2;
    uint8 constant KIND_V4 = 4;

    ArbExecutor exec;
    address v3WethCbbtc;

    function setUp() public {
        vm.createSelectFork(vm.envOr("BASE_RPC_URL", string("https://base-rpc.publicnode.com")));
        exec = new ArbExecutor(
            0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb,
            0xA238Dd80C259a72e81d7e4664a9801593F98d1c5,
            0xBA12222222228d8Ba445958a75a0704d566BF2C8,
            WETH
        );
        // resolve the Uniswap V3 WETH/cbBTC 0.05% pool from the factory
        (bool ok, bytes memory ret) = 0x33128a8fC17869897dcE68Ed026d694621f6FDfD.staticcall(
            abi.encodeWithSignature("getPool(address,address,uint24)", WETH, CBBTC, uint24(500))
        );
        require(ok, "factory");
        v3WethCbbtc = abi.decode(ret, (address));
        require(v3WethCbbtc != address(0), "no v3 pool");
    }

    // sell `amount` of token0 into a V3 pool (moves its price)
    function _push(address pool, address token0, uint256 amount) internal {
        deal(token0, address(this), amount);
        IV3Pool(pool).swap(address(this), true, int256(amount), 4295128740, abi.encode(token0));
    }

    function uniswapV3SwapCallback(int256 a0, int256 a1, bytes calldata data) external {
        address token = abi.decode(data, (address));
        IERC20(token).transfer(msg.sender, a0 > 0 ? uint256(a0) : uint256(a1));
    }

    function _v4Hop(bool zeroForOne, address cIn, address cOut, uint24 fee, int24 ts) internal pure returns (ArbExecutor.Hop memory) {
        return ArbExecutor.Hop({pool: POOL_MANAGER, kind: KIND_V4, zeroForOne: zeroForOne, tokenIn: cIn, tokenOut: cOut, amountOut: 0, feeBps: 0, fee: fee, tickSpacing: ts, hooks: address(0)});
    }

    function _v3Hop(address pool, bool zeroForOne, address tIn, address tOut) internal pure returns (ArbExecutor.Hop memory) {
        return ArbExecutor.Hop({pool: pool, kind: KIND_V3, zeroForOne: zeroForOne, tokenIn: tIn, tokenOut: tOut, amountOut: 0, feeBps: 0, fee: 0, tickSpacing: 0, hooks: address(0)});
    }

    /// V3 pool: WETH is token0 (0x42.. < 0xcb..). Selling 100 WETH into it makes cbBTC expensive there.
    /// Route: hop0 V3 flash: cbBTC -> WETH (sell cbBTC where it is expensive); hop1 V4 native pool: ETH -> cbBTC
    /// (buy it back at the fair price; the contract unwraps WETH to settle native ETH). Profit lands in WETH.
    function test_v4_nestedHop_nativeEthInput() public {
        _push(v3WethCbbtc, WETH, 100 ether);
        ArbExecutor.Hop[] memory hops = new ArbExecutor.Hop[](2);
        hops[0] = _v3Hop(v3WethCbbtc, false, CBBTC, WETH);
        // V4 key: currency0 = native (address(0)), currency1 = cbBTC, fee 500, tickSpacing 10
        hops[1] = _v4Hop(true, address(0), CBBTC, 500, 10);
        uint256 profit = exec.execute(hops, 0.05e8, 1, 0); // 0.05 cbBTC; the cycle starts and ends in cbBTC
        console2.log("V3(flash) -> V4(native ETH) profit (cbBTC sats):", profit);
        assertGt(profit, 0);
        assertEq(IERC20(CBBTC).balanceOf(address(exec)), profit, "profit is held in cbBTC");
        assertEq(IERC20(WETH).balanceOf(address(exec)), 0, "no WETH left");
        assertEq(address(exec).balance, 0, "no stray ETH");
    }

    /// Route with the V4 pool as the flash hop: hop0 V4 native pool ETH -> cbBTC (output taken first),
    /// hop1 V3: cbBTC -> WETH where cbBTC is expensive, then the V4 input is settled from the WETH proceeds.
    function test_v4_flashHop_nativeEthInput() public {
        _push(v3WethCbbtc, WETH, 100 ether);
        ArbExecutor.Hop[] memory hops = new ArbExecutor.Hop[](2);
        hops[0] = _v4Hop(true, address(0), CBBTC, 500, 10);
        hops[1] = _v3Hop(v3WethCbbtc, false, CBBTC, WETH);
        uint256 profit = exec.execute(hops, 1 ether, 1, 0);
        console2.log("V4(flash, native ETH) -> V3 profit wei WETH:", profit);
        assertGt(profit, 0);
        assertEq(IERC20(CBBTC).balanceOf(address(exec)), 0);
        assertEq(address(exec).balance, 0);
    }

    /// ERC20-only V4 pool (USDC/cbBTC 0.05%, tickSpacing 10) as the flash hop, closed on the same V3 pool via WETH? No:
    /// keep it a 2-hop USDC cycle: hop0 V4 USDC -> cbBTC, hop1 V3 cbBTC -> USDC (Uniswap V3 cbBTC/USDC 0.05%, pushed).
    function test_v4_flashHop_erc20() public {
        (bool ok, bytes memory ret) = 0x33128a8fC17869897dcE68Ed026d694621f6FDfD.staticcall(
            abi.encodeWithSignature("getPool(address,address,uint24)", USDC, CBBTC, uint24(500))
        );
        require(ok, "factory");
        address v3UsdcCbbtc = abi.decode(ret, (address));
        require(v3UsdcCbbtc != address(0), "no v3 usdc/cbbtc pool");
        // token0 of that pool is USDC (0x83.. < 0xcb..). Sell 300k USDC into it → cbBTC expensive there.
        _push(v3UsdcCbbtc, USDC, 300_000e6);
        ArbExecutor.Hop[] memory hops = new ArbExecutor.Hop[](2);
        hops[0] = _v4Hop(true, USDC, CBBTC, 500, 10); // buy cbBTC at fair price on V4
        hops[1] = _v3Hop(v3UsdcCbbtc, false, CBBTC, USDC); // sell it where it is expensive
        uint256 profit = exec.execute(hops, 5_000e6, 1, 0);
        console2.log("V4(flash, ERC20) -> V3 profit USDC:", profit);
        assertGt(profit, 0);
        assertEq(IERC20(CBBTC).balanceOf(address(exec)), 0);
    }

    function test_v4_unlockCallbackRejectsStrangers() public {
        vm.expectRevert(ArbExecutor.BadCaller.selector);
        exec.unlockCallback(abi.encode(uint8(1)));
    }
}
