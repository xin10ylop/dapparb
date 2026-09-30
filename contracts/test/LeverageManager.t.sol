// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test, console2} from "forge-std/Test.sol";
import {LeverageManager} from "../src/LeverageManager.sol";
import {IPool, IVariableDebtToken, IAToken} from "../src/interfaces/IAave.sol";
import {IERC20} from "../src/interfaces/IPools.sol";

interface ISwapRouter02 {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
}

/// @notice Fork tests on Base: Aave V3 + Uniswap V3 SwapRouter02.
contract LeverageManagerTest is Test {
    address constant WETH = 0x4200000000000000000000000000000000000006;
    address constant USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913;
    address constant AAVE_POOL = 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5;
    address constant ROUTER = 0x2626664c2603336E57B271c5C0b26F421741e481;

    LeverageManager lev;
    address user = makeAddr("user");
    IVariableDebtToken vdUSDC;
    IVariableDebtToken vdWETH;
    IAToken aWETH;
    IAToken aUSDC;

    function setUp() public {
        vm.createSelectFork(vm.envOr("BASE_RPC_URL", string("https://base-rpc.publicnode.com")));
        lev = new LeverageManager(AAVE_POOL);
        IPool.ReserveData memory rUSDC = IPool(AAVE_POOL).getReserveData(USDC);
        IPool.ReserveData memory rWETH = IPool(AAVE_POOL).getReserveData(WETH);
        vdUSDC = IVariableDebtToken(rUSDC.variableDebtTokenAddress);
        vdWETH = IVariableDebtToken(rWETH.variableDebtTokenAddress);
        aWETH = IAToken(rWETH.aTokenAddress);
        aUSDC = IAToken(rUSDC.aTokenAddress);
    }

    function _swapCalldata(address tokenIn, address tokenOut, uint24 fee, uint256 amountIn) internal view returns (bytes memory) {
        return abi.encodeWithSelector(
            ISwapRouter02.exactInputSingle.selector,
            ISwapRouter02.ExactInputSingleParams({
                tokenIn: tokenIn,
                tokenOut: tokenOut,
                fee: fee,
                recipient: address(lev),
                amountIn: amountIn,
                amountOutMinimum: 0,
                sqrtPriceLimitX96: 0
            })
        );
    }

    function _openLong(uint256 userUsdc, uint256 flashUsdc, uint256 minHf) internal {
        deal(USDC, user, userUsdc);
        vm.startPrank(user);
        IERC20(USDC).approve(address(lev), userUsdc);
        vdUSDC.approveDelegation(address(lev), flashUsdc);
        lev.open(
            LeverageManager.OpenParams({
                collateralAsset: WETH,
                debtAsset: USDC,
                userAmount: userUsdc,
                flashAmount: flashUsdc,
                minHealthFactor: minHf,
                swap: LeverageManager.Swap({
                    target: ROUTER,
                    spender: ROUTER,
                    data: _swapCalldata(USDC, WETH, 500, userUsdc + flashUsdc),
                    minOut: 1e18
                })
            })
        );
        vm.stopPrank();
    }

    function test_openLong_2x() public {
        _openLong(2000e6, 2000e6, 1.2e18);
        uint256 coll = aWETH.balanceOf(user);
        uint256 debt = vdUSDC.balanceOf(user);
        (,,,,, uint256 hf) = IPool(AAVE_POOL).getUserAccountData(user);
        console2.log("aWETH collateral (wei):", coll);
        console2.log("USDC variable debt:", debt);
        console2.log("health factor (1e18):", hf);
        assertGt(coll, 1.2e18, "should hold > 1.2 WETH of collateral for $4000 at ~$2700/ETH");
        assertApproxEqAbs(debt, 2000e6, 1, "debt must equal the flash amount, no premium in mode 2");
        assertGt(hf, 1.2e18);
        assertEq(IERC20(WETH).balanceOf(address(lev)), 0, "manager keeps nothing");
        assertEq(IERC20(USDC).balanceOf(address(lev)), 0, "manager keeps nothing");
    }

    function test_openLong_revertsOnLowHealthFactor() public {
        // 2x leverage yields HF ≈ 1.66 on Base WETH (LT ~83%); demanding 2.0 must trip our guard, not Aave's.
        deal(USDC, user, 2000e6);
        vm.startPrank(user);
        IERC20(USDC).approve(address(lev), 2000e6);
        vdUSDC.approveDelegation(address(lev), 2000e6);
        vm.expectPartialRevert(LeverageManager.HealthFactorTooLow.selector);
        lev.open(
            LeverageManager.OpenParams({
                collateralAsset: WETH,
                debtAsset: USDC,
                userAmount: 2000e6,
                flashAmount: 2000e6,
                minHealthFactor: 2e18,
                swap: LeverageManager.Swap({target: ROUTER, spender: ROUTER, data: _swapCalldata(USDC, WETH, 500, 4000e6), minOut: 1e18})
            })
        );
        vm.stopPrank();
    }

    function test_openLong_aaveRejectsExcessiveLeverage() public {
        // 7x: Aave's own collateral check rejects the borrow before our guard runs; either way nothing is opened.
        deal(USDC, user, 1000e6);
        vm.startPrank(user);
        IERC20(USDC).approve(address(lev), 1000e6);
        vdUSDC.approveDelegation(address(lev), 6000e6);
        vm.expectRevert();
        lev.open(
            LeverageManager.OpenParams({
                collateralAsset: WETH,
                debtAsset: USDC,
                userAmount: 1000e6,
                flashAmount: 6000e6,
                minHealthFactor: 1.05e18,
                swap: LeverageManager.Swap({target: ROUTER, spender: ROUTER, data: _swapCalldata(USDC, WETH, 500, 7000e6), minOut: 1e18})
            })
        );
        vm.stopPrank();
        assertEq(aWETH.balanceOf(user), 0);
        assertEq(vdUSDC.balanceOf(user), 0);
    }

    function test_openShort() public {
        deal(WETH, user, 1e18);
        vm.startPrank(user);
        IERC20(WETH).approve(address(lev), 1e18);
        vdWETH.approveDelegation(address(lev), 1e18);
        lev.open(
            LeverageManager.OpenParams({
                collateralAsset: USDC,
                debtAsset: WETH,
                userAmount: 1e18,
                flashAmount: 1e18,
                minHealthFactor: 1.2e18,
                swap: LeverageManager.Swap({target: ROUTER, spender: ROUTER, data: _swapCalldata(WETH, USDC, 500, 2e18), minOut: 4000e6})
            })
        );
        vm.stopPrank();
        uint256 coll = aUSDC.balanceOf(user);
        uint256 debt = vdWETH.balanceOf(user);
        console2.log("aUSDC collateral:", coll);
        console2.log("WETH variable debt (wei):", debt);
        assertGt(coll, 4000e6);
        assertApproxEqAbs(debt, 1e18, 1);
    }

    function test_closeLong_roundTrip() public {
        _openLong(2000e6, 2000e6, 1.2e18);
        uint256 debt = vdUSDC.balanceOf(user);
        uint256 coll = aWETH.balanceOf(user);
        // sell enough WETH to cover debt + 0.05% premium with margin: ~ (debt*1.0005)/price * 1.03
        uint256 toSwap = (coll * 55) / 100; // ~55% of collateral ≈ $2200 worth at 2x leverage
        vm.startPrank(user);
        aWETH.approve(address(lev), coll);
        lev.close(
            LeverageManager.CloseParams({
                collateralAsset: WETH,
                debtAsset: USDC,
                debtToRepay: debt,
                collateralToWithdraw: coll,
                swap: LeverageManager.Swap({target: ROUTER, spender: ROUTER, data: _swapCalldata(WETH, USDC, 500, toSwap), minOut: debt}),
                collateralToSwap: toSwap
            })
        );
        vm.stopPrank();
        assertEq(vdUSDC.balanceOf(user), 0, "debt fully repaid");
        assertEq(aWETH.balanceOf(user), 0, "collateral fully withdrawn");
        uint256 wethBack = IERC20(WETH).balanceOf(user);
        uint256 usdcBack = IERC20(USDC).balanceOf(user);
        console2.log("returned WETH (wei):", wethBack);
        console2.log("returned USDC:", usdcBack);
        assertEq(wethBack, coll - toSwap);
        assertGt(usdcBack, 0, "surplus USDC from the swap comes back");
        // round trip cost: started with 2000 USDC; ended with wethBack (worth ~0.66*2700 = $1790) + usdcBack
        assertEq(IERC20(WETH).balanceOf(address(lev)), 0);
        assertEq(IERC20(USDC).balanceOf(address(lev)), 0);
    }

    function test_callbackRejectsStrangers() public {
        vm.expectRevert(LeverageManager.NotPool.selector);
        lev.executeOperation(USDC, 1, 0, address(lev), "");
        // even the pool cannot call outside an open/close (transient flag unset)
        vm.prank(AAVE_POOL);
        vm.expectRevert(LeverageManager.NotPool.selector);
        lev.executeOperation(USDC, 1, 0, address(lev), abi.encode(uint8(1)));
    }
}
