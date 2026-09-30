// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IERC20} from "./interfaces/IPools.sol";
import {IPool, IAToken} from "./interfaces/IAave.sol";

/// @title LeverageManager
/// @notice One-transaction leveraged long/short positions on Aave V3 using Aave's own flash loan with
///         `interestRateMode = 2`: the flash-borrowed amount is NOT repaid inside the transaction but becomes
///         variable-rate debt of the user (no flash premium in this mode). The user must first call
///         `approveDelegation(address(this), amount)` on the debt asset's VariableDebtToken.
///
///         Long ETH (video example):  user supplies 2000 USDC, flash-borrows 2000 USDC as debt, swaps 4000 USDC
///         → WETH, and supplies all WETH as collateral. Result: WETH collateral, USDC debt, 2x long.
///         Short ETH:                 user supplies 1 WETH, flash-borrows 1 WETH as debt, swaps 2 WETH → USDC,
///         supplies USDC. Result: USDC collateral, WETH debt, net short.
///
///         `close` flash-borrows the debt asset (mode 0, repaid with premium), repays the user's debt, pulls the
///         user's aTokens (user must `approve` this contract on the aToken), withdraws the collateral, swaps enough
///         to repay the flash loan, and returns everything else to the user.
///
///         Swaps are delegated to any router/aggregator via (target, calldata) so quotes can come from Uniswap,
///         Aerodrome, 1inch, Odos, etc. A minimum output guards against a bad route.
/// @dev    This contract never holds user funds between transactions and has no privileged roles.
///         RISK: leverage on volatile collateral can be liquidated. `minHealthFactor` is enforced after opening.
contract LeverageManager {
    IPool public immutable POOL;

    error NotPool();
    error BadInitiator();
    error SwapFailed();
    error InsufficientOutput(uint256 got, uint256 want);
    error HealthFactorTooLow(uint256 hf, uint256 min);
    error TransferFailed();
    error Unauthorized();

    event Opened(address indexed user, address collateral, address debt, uint256 userAmount, uint256 flashAmount, uint256 collateralSupplied, uint256 healthFactor);
    event Closed(address indexed user, address collateral, address debt, uint256 debtRepaid, uint256 collateralReturned);

    struct Swap {
        address target; // router / aggregator
        address spender; // address to approve for tokenIn (usually == target)
        bytes data; // full calldata for an exact-input swap that sends output to this contract
        uint256 minOut;
    }

    struct OpenParams {
        address collateralAsset; // asset supplied to Aave (e.g. WETH for a long)
        address debtAsset; // asset flash-borrowed and left as debt (e.g. USDC for a long)
        uint256 userAmount; // user's own contribution in debtAsset (long) — swapped together with the flash amount
        uint256 flashAmount; // borrowed on the user's behalf
        uint256 minHealthFactor; // 1e18 = 1.0
        Swap swap; // debtAsset -> collateralAsset for (userAmount + flashAmount)
    }

    struct CloseParams {
        address collateralAsset;
        address debtAsset;
        uint256 debtToRepay; // amount of debtAsset to flash-borrow and repay (type(uint).max not supported; pass exact)
        uint256 collateralToWithdraw; // aTokens pulled from the user
        Swap swap; // collateralAsset -> debtAsset for `collateralToSwap`
        uint256 collateralToSwap; // how much of the withdrawn collateral to sell to cover the flash loan + premium
    }

    uint8 private constant ACTION_OPEN = 1;
    uint8 private constant ACTION_CLOSE = 2;

    // transient re-entrancy guard for the flash-loan callback
    bytes32 private constant T_EXPECTED = keccak256("lev.expected");

    constructor(address pool) {
        POOL = IPool(pool);
    }

    // ------------------------------------------------------------------------------------------ open

    /// @notice Open a leveraged position for msg.sender. Requires prior:
    ///         debtAsset.approve(this, userAmount) and VariableDebtToken(debtAsset).approveDelegation(this, flashAmount).
    function open(OpenParams calldata p) external {
        if (p.userAmount > 0) _pull(p.debtAsset, msg.sender, p.userAmount);
        address[] memory assets = new address[](1);
        uint256[] memory amounts = new uint256[](1);
        uint256[] memory modes = new uint256[](1);
        assets[0] = p.debtAsset;
        amounts[0] = p.flashAmount;
        modes[0] = 2; // variable debt opened for onBehalfOf; nothing to repay here
        _tstore(T_EXPECTED, bytes32(uint256(1)));
        POOL.flashLoan(address(this), assets, amounts, modes, msg.sender, abi.encode(ACTION_OPEN, msg.sender, p), 0);
        _tstore(T_EXPECTED, bytes32(0));
        (,,,,, uint256 hf) = POOL.getUserAccountData(msg.sender);
        if (hf < p.minHealthFactor) revert HealthFactorTooLow(hf, p.minHealthFactor);
    }

    // ----------------------------------------------------------------------------------------- close

    /// @notice Unwind: requires aToken(collateralAsset).approve(this, collateralToWithdraw).
    function close(CloseParams calldata p) external {
        _tstore(T_EXPECTED, bytes32(uint256(1)));
        POOL.flashLoanSimple(address(this), p.debtAsset, p.debtToRepay, abi.encode(ACTION_CLOSE, msg.sender, p), 0);
        _tstore(T_EXPECTED, bytes32(0));
    }

    // -------------------------------------------------------------------------------------- callbacks

    /// @dev Aave V3 multi-asset `flashLoan` callback (used by `open`, mode 2 → debt stays with the user).
    function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    ) external returns (bool) {
        return _onFlashLoan(assets[0], amounts[0], premiums[0], initiator, params);
    }

    /// @dev Aave V3 `flashLoanSimple` callback (used by `close`, repaid with premium).
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params)
        external
        returns (bool)
    {
        return _onFlashLoan(asset, amount, premium, initiator, params);
    }

    function _onFlashLoan(address, uint256 amount, uint256 premium, address initiator, bytes calldata params)
        internal
        returns (bool)
    {
        if (msg.sender != address(POOL)) revert NotPool();
        if (initiator != address(this)) revert BadInitiator();
        if (_tload(T_EXPECTED) != bytes32(uint256(1))) revert NotPool();
        _tstore(T_EXPECTED, bytes32(0));

        uint8 action = abi.decode(params, (uint8));
        if (action == ACTION_OPEN) {
            (, address user, OpenParams memory p) = abi.decode(params, (uint8, address, OpenParams));
            uint256 amountIn = p.userAmount + amount;
            uint256 got = _swap(p.debtAsset, amountIn, p.collateralAsset, p.swap);
            _approve(p.collateralAsset, address(POOL), got);
            POOL.supply(p.collateralAsset, got, user, 0);
            // mode 2: debt already assigned to `user`; nothing to approve back to the pool.
            (,,,,, uint256 hf) = POOL.getUserAccountData(user);
            emit Opened(user, p.collateralAsset, p.debtAsset, p.userAmount, amount, got, hf);
        } else {
            (, address user, CloseParams memory p) = abi.decode(params, (uint8, address, CloseParams));
            _approve(p.debtAsset, address(POOL), amount);
            POOL.repay(p.debtAsset, amount, 2, user);
            address aToken = POOL.getReserveData(p.collateralAsset).aTokenAddress;
            if (!IAToken(aToken).transferFrom(user, address(this), p.collateralToWithdraw)) revert TransferFailed();
            uint256 withdrawn = POOL.withdraw(p.collateralAsset, p.collateralToWithdraw, address(this));
            uint256 owed = amount + premium;
            uint256 got = _swap(p.collateralAsset, p.collateralToSwap, p.debtAsset, p.swap);
            if (got < owed) revert InsufficientOutput(got, owed);
            _approve(p.debtAsset, address(POOL), owed);
            // leftovers back to the user
            if (got > owed) _push(p.debtAsset, user, got - owed);
            if (withdrawn > p.collateralToSwap) _push(p.collateralAsset, user, withdrawn - p.collateralToSwap);
            emit Closed(user, p.collateralAsset, p.debtAsset, amount, withdrawn - p.collateralToSwap);
        }
        return true;
    }

    // -------------------------------------------------------------------------------------- internals

    function _swap(address tokenIn, uint256 amountIn, address tokenOut, Swap memory s) internal returns (uint256 got) {
        _approve(tokenIn, s.spender, amountIn);
        uint256 before = IERC20(tokenOut).balanceOf(address(this));
        (bool ok,) = s.target.call(s.data);
        if (!ok) revert SwapFailed();
        got = IERC20(tokenOut).balanceOf(address(this)) - before;
        if (got < s.minOut) revert InsufficientOutput(got, s.minOut);
        _approve(tokenIn, s.spender, 0);
    }

    function _pull(address token, address from, uint256 amount) internal {
        if (!IERC20(token).transferFrom(from, address(this), amount)) revert TransferFailed();
    }

    function _push(address token, address to, uint256 amount) internal {
        (bool ok, bytes memory ret) = token.call(abi.encodeWithSelector(IERC20.transfer.selector, to, amount));
        if (!ok || (ret.length != 0 && !abi.decode(ret, (bool)))) revert TransferFailed();
    }

    function _approve(address token, address spender, uint256 amount) internal {
        (bool ok, bytes memory ret) = token.call(abi.encodeWithSelector(IERC20.approve.selector, spender, amount));
        if (!ok || (ret.length != 0 && !abi.decode(ret, (bool)))) revert TransferFailed();
    }

    function _tstore(bytes32 slot, bytes32 value) internal {
        assembly ("memory-safe") {
            tstore(slot, value)
        }
    }

    function _tload(bytes32 slot) internal view returns (bytes32 value) {
        assembly ("memory-safe") {
            value := tload(slot)
        }
    }
}
