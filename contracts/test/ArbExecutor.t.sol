// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Test, console2} from "forge-std/Test.sol";
import {ArbExecutor} from "../src/ArbExecutor.sol";
import {IERC20, IV3Pool, IV2Pair, IAeroPool} from "../src/interfaces/IPools.sol";

/// @notice Fork tests against live Base pools. We manufacture a price discrepancy by pushing one pool with a
///         large swap, then verify the executor captures it atomically through every supported pool kind and
///         both funding paths (flash swap / flash loan), and that all guards revert correctly.
contract ArbExecutorTest is Test {
    // Base
    address constant WETH = 0x4200000000000000000000000000000000000006;
    address constant USDC = 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913;
    address constant MORPHO = 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb;
    address constant AAVE = 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5;
    address constant BALANCER = 0xBA12222222228d8Ba445958a75a0704d566BF2C8;

    address constant UNIV3_500 = 0xd0b53D9277642d899DF5C87A3966A349A798F224; // WETH/USDC 0.05%
    address constant UNIV3_3000 = 0x6c561B446416E1A00E8E93E221854d6eA4171372; // WETH/USDC 0.3%
    address constant AERO_CL_100 = 0xb2cc224c1c9feE385f8ad6a55b4d94E92359DC59; // Slipstream ts=100
    address constant PANCAKE_V3_500 = 0xB775272E537cc670C65DC852908aD47015244EaF;
    address constant UNIV2 = 0x88A43bbDF9D098eEC7bCEda4e2494615dfD9bB9C; // WETH/USDC 0.3%
    address constant AERO_V2 = 0xcDAC0d6c6C59727a65F871236188350531885C43; // volatile WETH/USDC
    address constant SUSHI_V2 = 0x2F8818D1B0f3e3E295440c1C0cDDf40aAA21fA87;

    uint8 constant KIND_UNIV2 = 0;
    uint8 constant KIND_AERO_V2 = 1;
    uint8 constant KIND_V3 = 2;
    uint8 constant KIND_PANCAKE_V3 = 3;

    ArbExecutor exec;
    address bot = makeAddr("bot");

    function setUp() public {
        string memory rpc = vm.envOr("BASE_RPC_URL", string("https://base-rpc.publicnode.com"));
        vm.createSelectFork(rpc);
        exec = new ArbExecutor(MORPHO, AAVE, BALANCER);
        exec.setExecutor(bot, true);
        // WETH/USDC token ordering: WETH (0x42..) < USDC (0x83..) so WETH is token0 in every pool.
        assertEq(IV3Pool(UNIV3_500).token0(), WETH);
        assertEq(IV2Pair(UNIV2).token0(), WETH);
    }

    // ------------------------------------------------------------------ helpers

    /// @dev Sell `amount` WETH into a V3 pool to depress its ETH price (creates the discrepancy).
    function _pushV3(address pool, uint256 amount) internal {
        deal(WETH, address(this), amount);
        IV3Pool(pool).swap(address(this), true, int256(amount), 4295128740, abi.encode(WETH));
    }

    /// @dev Sell `amount` WETH into a V2 pair.
    function _pushV2(address pair, uint256 amount, bool aero) internal {
        deal(WETH, address(this), amount);
        IERC20(WETH).transfer(pair, amount);
        uint256 out;
        if (aero) {
            out = IAeroPool(pair).getAmountOut(amount, WETH);
        } else {
            (uint112 r0, uint112 r1,) = IV2Pair(pair).getReserves();
            uint256 inFee = amount * 9970;
            out = (inFee * r1) / (uint256(r0) * 10_000 + inFee);
        }
        IV2Pair(pair).swap(0, out, address(this), "");
    }

    // test contract pays for its own push swaps
    function uniswapV3SwapCallback(int256 a0, int256 a1, bytes calldata data) external {
        address token = abi.decode(data, (address));
        uint256 owed = a0 > 0 ? uint256(a0) : uint256(a1);
        IERC20(token).transfer(msg.sender, owed);
    }

    function pancakeV3SwapCallback(int256 a0, int256 a1, bytes calldata data) external {
        address token = abi.decode(data, (address));
        uint256 owed = a0 > 0 ? uint256(a0) : uint256(a1);
        IERC20(token).transfer(msg.sender, owed);
    }

    function _hop(address pool, uint8 kind, bool z4o, address tIn, address tOut, uint16 fee) internal pure returns (ArbExecutor.Hop memory) {
        return ArbExecutor.Hop({pool: pool, kind: kind, zeroForOne: z4o, tokenIn: tIn, tokenOut: tOut, amountOut: 0, feeBps: fee});
    }

    /// @dev After pushing WETH into `cheap` (ETH is now cheaper there), the arb is:
    ///      buy WETH with USDC on `cheap` ... but we want to start & end in WETH, so:
    ///      hop0: sell WETH for USDC on `rich` (where ETH is still expensive), hop1: buy WETH with USDC on `cheap`.
    function _route(address rich, uint8 richKind, uint16 richFee, address cheap, uint8 cheapKind, uint16 cheapFee)
        internal
        pure
        returns (ArbExecutor.Hop[] memory hops)
    {
        hops = new ArbExecutor.Hop[](2);
        hops[0] = _hop(rich, richKind, true, WETH, USDC, richFee); // WETH -> USDC
        hops[1] = _hop(cheap, cheapKind, false, USDC, WETH, cheapFee); // USDC -> WETH
    }

    // ------------------------------------------------------------------ flash-swap paths

    function test_flashSwap_V3_to_V3() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 20 ether, 1, 0);
        console2.log("V3->V3 profit (wei WETH):", profit);
        assertGt(profit, 0);
        assertEq(IERC20(WETH).balanceOf(address(exec)), profit);
    }

    function test_flashSwap_V3_to_PancakeV3() public {
        _pushV3(PANCAKE_V3_500, 30 ether);
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, PANCAKE_V3_500, KIND_PANCAKE_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 3 ether, 1, 0);
        console2.log("V3->PancakeV3 profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_PancakeV3_first() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(PANCAKE_V3_500, KIND_PANCAKE_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 2 ether, 1, 0);
        console2.log("PancakeV3(first)->V3 profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_V2_to_V3() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(UNIV2, KIND_UNIV2, 30, UNIV3_500, KIND_V3, 0);
        (uint112 r0,,) = IV2Pair(UNIV2).getReserves();
        uint256 amountIn = uint256(r0) / 100; // 1% of the pair's WETH reserve keeps price impact below the V3 discrepancy
        vm.prank(bot);
        uint256 profit = exec.execute(hops, amountIn, 1, 0);
        console2.log("UniV2(flash)->V3 profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_V3_to_V2() public {
        _pushV2(UNIV2, 40 ether, false);
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, UNIV2, KIND_UNIV2, 30);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 5 ether, 1, 0);
        console2.log("V3(flash)->UniV2 profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_Aero_to_V3() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_V2, KIND_AERO_V2, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 10 ether, 1, 0);
        console2.log("Aero(flash,hook)->V3 profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_V3_to_Aero() public {
        _pushV2(AERO_V2, 100 ether, true);
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, AERO_V2, KIND_AERO_V2, 0);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 10 ether, 1, 0);
        console2.log("V3(flash)->Aero profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashSwap_V2_to_V2() public {
        _pushV2(UNIV2, 40 ether, false);
        ArbExecutor.Hop[] memory hops = _route(AERO_V2, KIND_AERO_V2, 0, UNIV2, KIND_UNIV2, 30);
        vm.prank(bot);
        uint256 profit = exec.execute(hops, 3 ether, 1, 0);
        console2.log("Aero(flash)->UniV2 profit:", profit);
        assertGt(profit, 0);
    }

    function test_threeHop_triangle() public {
        // WETH -> USDC (UniV3 500) -> WETH (UniV2)  is 2 hops; make a 3-hop: WETH->USDC (rich V3), USDC->WETH (pushed V3), then WETH->WETH? no.
        // Use: hop0 AeroCL WETH->USDC, hop1 UniV3_3000 USDC->WETH (pushed cheap), hop2 UniV3_500 WETH->USDC? ends in USDC, not WETH.
        // A true 3-hop cycle needs 3 tokens; keep it as a 3-hop with a round trip through a second USDC pool:
        _pushV3(UNIV3_3000, 150 ether);
        ArbExecutor.Hop[] memory hops = new ArbExecutor.Hop[](3);
        hops[0] = _hop(UNIV3_500, KIND_V3, true, WETH, USDC, 0); // WETH->USDC at fair price
        hops[1] = _hop(UNIV3_3000, KIND_V3, false, USDC, WETH, 0); // USDC->WETH cheap (pushed)
        hops[2] = _hop(UNIV2, KIND_UNIV2, true, WETH, USDC, 30); // WETH->USDC ... ends in USDC: route invalid
        vm.prank(bot);
        vm.expectRevert(ArbExecutor.BadRoute.selector);
        exec.execute(hops, 1 ether, 1, 0);
    }

    // ------------------------------------------------------------------ flash-loan paths

    function test_flashLoan_Morpho() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.executeFlashLoan(0, hops, 20 ether, 1, 0);
        console2.log("Morpho flash loan profit:", profit);
        assertGt(profit, 0);
    }

    function test_flashLoan_Aave() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        uint256 profit = exec.executeFlashLoan(1, hops, 20 ether, 1, 0);
        console2.log("Aave flash loan profit (after 0.05% premium):", profit);
        assertGt(profit, 0);
    }

    function test_flashLoan_Balancer() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        uint256 vaultWeth = IERC20(WETH).balanceOf(BALANCER);
        uint256 amt = vaultWeth < 20 ether ? vaultWeth / 2 : 20 ether;
        vm.prank(bot);
        uint256 profit = exec.executeFlashLoan(2, hops, amt, 1, 0);
        console2.log("Balancer flash loan amount / profit:", amt, profit);
        assertGt(profit, 0);
    }

    // ------------------------------------------------------------------ guards

    function test_revert_noOpportunity() public {
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, AERO_CL_100, KIND_V3, 0);
        vm.prank(bot);
        vm.expectRevert(); // InsufficientProfit or a pool-level revert; either way nothing leaves the contract
        exec.execute(hops, 1 ether, 1, 0);
        assertEq(IERC20(WETH).balanceOf(address(exec)), 0);
    }

    function test_revert_minProfitEnforced() public {
        _pushV3(UNIV3_500, 300 ether);
        ArbExecutor.Hop[] memory hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        vm.expectPartialRevert(ArbExecutor.InsufficientProfit.selector);
        exec.execute(hops, 20 ether, 1_000_000 ether, 0);
    }

    function test_revert_lossCoveredByBalance_isExplicit() public {
        // Contract already holds WETH; a losing cycle must revert with InsufficientProfit(negative), not panic.
        deal(WETH, address(exec), 5 ether);
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, UNIV3_3000, KIND_V3, 0);
        vm.prank(bot);
        vm.expectPartialRevert(ArbExecutor.InsufficientProfit.selector);
        exec.execute(hops, 1 ether, 0, 0);
        assertEq(IERC20(WETH).balanceOf(address(exec)), 5 ether, "revert must restore balance");
    }

    function test_revert_cannotRepay_isExplicit() public {
        // No discrepancy: hop 1 returns less WETH than hop 0 demands → explicit CannotRepay from inside the callback.
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, UNIV3_3000, KIND_V3, 0);
        vm.prank(bot);
        vm.expectPartialRevert(ArbExecutor.CannotRepay.selector);
        exec.execute(hops, 1 ether, 1, 0);
    }

    function test_gas_execute_paths() public {
        _pushV3(UNIV3_500, 150 ether);
        _pushV2(UNIV2, 5 ether, false);
        _pushV2(AERO_V2, 10 ether, true);
        uint256 g;
        ArbExecutor.Hop[] memory hops;

        hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        g = gasleft();
        exec.execute(hops, 1 ether, 1, 0);
        console2.log("gas execute V3->V3      :", g - gasleft());

        hops = _route(UNIV3_3000, KIND_V3, 0, UNIV2, KIND_UNIV2, 30);
        vm.prank(bot);
        g = gasleft();
        exec.execute(hops, 0.2 ether, 1, 0);
        console2.log("gas execute V3->UniV2   :", g - gasleft());

        hops = _route(UNIV3_3000, KIND_V3, 0, AERO_V2, KIND_AERO_V2, 0);
        vm.prank(bot);
        g = gasleft();
        exec.execute(hops, 0.5 ether, 1, 0);
        console2.log("gas execute V3->Aero    :", g - gasleft());

        hops = _route(SUSHI_V2, KIND_UNIV2, 30, UNIV3_500, KIND_V3, 0);
        (uint112 r0,,) = IV2Pair(SUSHI_V2).getReserves();
        vm.prank(bot);
        g = gasleft();
        exec.execute(hops, uint256(r0) / 2000, 1, 0);
        console2.log("gas execute SushiV2->V3 :", g - gasleft());

        hops = _route(AERO_CL_100, KIND_V3, 0, UNIV3_500, KIND_V3, 0);
        vm.prank(bot);
        g = gasleft();
        exec.executeFlashLoan(0, hops, 1 ether, 1, 0);
        console2.log("gas flashLoan(Morpho) V3->V3:", g - gasleft());
    }

    function test_revert_notExecutor() public {
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, AERO_CL_100, KIND_V3, 0);
        vm.prank(makeAddr("stranger"));
        vm.expectRevert(ArbExecutor.NotExecutor.selector);
        exec.execute(hops, 1 ether, 1, 0);
    }

    function test_revert_expired() public {
        ArbExecutor.Hop[] memory hops = _route(UNIV3_500, KIND_V3, 0, AERO_CL_100, KIND_V3, 0);
        vm.prank(bot);
        vm.expectRevert(abi.encodeWithSelector(ArbExecutor.Expired.selector, block.number, block.number - 1));
        exec.execute(hops, 1 ether, 1, block.number - 1);
    }

    function test_revert_callbackFromStranger() public {
        vm.expectRevert(ArbExecutor.BadCaller.selector);
        exec.uniswapV3SwapCallback(1, -1, abi.encode(uint8(2), WETH));
        vm.expectRevert(ArbExecutor.BadCaller.selector);
        exec.uniswapV2Call(address(this), 1, 0, "");
        vm.expectRevert(ArbExecutor.BadCaller.selector);
        exec.hook(address(this), 1, 0, "");
        vm.expectRevert(ArbExecutor.BadCaller.selector);
        exec.onMorphoFlashLoan(1, "");
    }

    function test_withdraw_onlyOwner() public {
        deal(WETH, address(exec), 1 ether);
        vm.prank(bot);
        vm.expectRevert(ArbExecutor.NotOwner.selector);
        exec.withdraw(WETH, 1 ether, bot);
        address sink = makeAddr("sink");
        exec.withdraw(WETH, 1 ether, sink);
        assertEq(IERC20(WETH).balanceOf(sink), 1 ether);
    }
}
