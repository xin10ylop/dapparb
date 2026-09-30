// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IERC20, IV3Pool, IV2Pair, IAeroPool, IMorpho, IAaveV3Pool, IBalancerVault} from "./interfaces/IPools.sol";

/// @title ArbExecutor
/// @notice Atomic multi-hop DEX arbitrage executor.
///         Route = ordered hops that start and end in the same token. Hop 0 is executed as a *flash swap*:
///         the pool sends us its output first and only demands payment in its callback, inside which we run
///         the remaining hops and pay hop 0 back from the proceeds. No flash loan fee, no extra protocol.
///         `executeFlashLoan` is an alternative entry that borrows from Morpho Blue (0 fee) / Aave V3 (0.05%)
///         / Balancer V2 (0 fee) and runs every hop as a normal swap.
///         If the cycle does not return at least `amountIn + minProfit`, the whole transaction reverts.
/// @dev    Supported pool kinds: Uniswap V2 & forks (uniswapV2Call / pancakeCall), Aerodrome V2-style (hook),
///         Uniswap V3 & forks incl. Slipstream (uniswapV3SwapCallback), PancakeSwap V3 (pancakeV3SwapCallback).
///         Callback authenticity is enforced with transient storage: only the pool we are currently calling may
///         re-enter, and only once.
contract ArbExecutor {
    // ---------------------------------------------------------------------------------------------
    // Types
    // ---------------------------------------------------------------------------------------------

    uint8 internal constant KIND_UNIV2 = 0; // getReserves()+local math, callback uniswapV2Call / pancakeCall
    uint8 internal constant KIND_AERO_V2 = 1; // pool.getAmountOut(), callback hook
    uint8 internal constant KIND_V3 = 2; // uniswapV3SwapCallback (UniV3, SushiV3, Slipstream)
    uint8 internal constant KIND_PANCAKE_V3 = 3; // pancakeV3SwapCallback

    uint8 internal constant PROVIDER_MORPHO = 0;
    uint8 internal constant PROVIDER_AAVE = 1;
    uint8 internal constant PROVIDER_BALANCER = 2;

    struct Hop {
        address pool;
        uint8 kind;
        bool zeroForOne; // tokenIn == token0
        address tokenIn;
        address tokenOut;
        uint256 amountOut; // V2 hop 0 only: exact output to request (computed off-chain); otherwise 0
        uint16 feeBps; // KIND_UNIV2 only: LP fee in bps (30 = 0.30%)
    }

    uint8 internal constant MODE_FLASH = 1; // hop-0 callback: run remaining hops then repay
    uint8 internal constant MODE_PAY = 2; // nested V3 hop callback: just pay what the pool asks

    uint160 internal constant MIN_SQRT_RATIO_PLUS_ONE = 4295128740;
    uint160 internal constant MAX_SQRT_RATIO_MINUS_ONE = 1461446703485210103287273052203988822378723970341;

    // transient slots
    bytes32 internal constant T_EXPECTED_CALLER = keccak256("arb.expectedCaller");
    bytes32 internal constant T_FLASH_RESULT = keccak256("arb.flashResult");

    // ---------------------------------------------------------------------------------------------
    // Errors / events
    // ---------------------------------------------------------------------------------------------

    error NotOwner();
    error NotExecutor();
    error BadCaller();
    error BadRoute();
    error Expired(uint256 blockNumber, uint256 maxBlock);
    /// @param got Signed balance change of the profit token (negative when the cycle lost money that was
    ///            covered by funds already held by the contract).
    error InsufficientProfit(int256 got, uint256 want);
    error CannotRepay(uint256 have, uint256 owed);
    error TransferFailed();
    error BadProvider();

    event Executed(address indexed token, uint256 amountIn, uint256 profit, uint8 hops);
    event ExecutorSet(address indexed executor, bool allowed);

    // ---------------------------------------------------------------------------------------------
    // Storage
    // ---------------------------------------------------------------------------------------------

    address public owner;
    mapping(address => bool) public executors;

    address public immutable MORPHO;
    address public immutable AAVE_POOL;
    address public immutable BALANCER_VAULT;

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier onlyExecutor() {
        if (!executors[msg.sender] && msg.sender != owner) revert NotExecutor();
        _;
    }

    constructor(address morpho, address aavePool, address balancerVault) {
        owner = msg.sender;
        executors[msg.sender] = true;
        MORPHO = morpho;
        AAVE_POOL = aavePool;
        BALANCER_VAULT = balancerVault;
    }

    receive() external payable {}

    // ---------------------------------------------------------------------------------------------
    // Admin
    // ---------------------------------------------------------------------------------------------

    function setExecutor(address executor, bool allowed) external onlyOwner {
        executors[executor] = allowed;
        emit ExecutorSet(executor, allowed);
    }

    function transferOwnership(address newOwner) external onlyOwner {
        owner = newOwner;
    }

    function withdraw(address token, uint256 amount, address to) external onlyOwner {
        if (token == address(0)) {
            (bool ok,) = to.call{value: amount}("");
            if (!ok) revert TransferFailed();
        } else {
            _safeTransfer(token, to, amount);
        }
    }

    /// @notice Arbitrary call for rescuing stuck approvals/tokens. Owner only.
    function rescue(address target, bytes calldata data) external onlyOwner returns (bytes memory) {
        (bool ok, bytes memory ret) = target.call(data);
        if (!ok) revert TransferFailed();
        return ret;
    }

    // ---------------------------------------------------------------------------------------------
    // Entry points
    // ---------------------------------------------------------------------------------------------

    /// @notice Execute a flash-swap arbitrage cycle.
    /// @param hops      Route; hops[0].tokenIn must equal hops[last].tokenOut.
    /// @param amountIn  Amount of hops[0].tokenIn to sell into hops[0].pool.
    /// @param minProfit Revert unless the cycle returns at least amountIn + minProfit.
    /// @param maxBlock  Revert if included after this block (0 = no limit).
    function execute(Hop[] calldata hops, uint256 amountIn, uint256 minProfit, uint256 maxBlock)
        external
        onlyExecutor
        returns (uint256 profit)
    {
        if (maxBlock != 0 && block.number > maxBlock) revert Expired(block.number, maxBlock);
        uint256 n = hops.length;
        if (n < 2 || hops[0].tokenIn != hops[n - 1].tokenOut) revert BadRoute();

        address token = hops[0].tokenIn;
        uint256 balBefore = IERC20(token).balanceOf(address(this));

        Hop calldata h0 = hops[0];
        bytes memory data = abi.encode(MODE_FLASH, hops, amountIn);
        _tstore(T_EXPECTED_CALLER, bytes32(uint256(uint160(h0.pool))));

        if (h0.kind == KIND_V3 || h0.kind == KIND_PANCAKE_V3) {
            IV3Pool(h0.pool).swap(
                address(this),
                h0.zeroForOne,
                int256(amountIn),
                h0.zeroForOne ? MIN_SQRT_RATIO_PLUS_ONE : MAX_SQRT_RATIO_MINUS_ONE,
                data
            );
        } else {
            uint256 out = h0.amountOut;
            if (out == 0) out = _v2QuoteOut(h0.pool, h0.kind, h0.zeroForOne, h0.tokenIn, h0.feeBps, amountIn);
            IV2Pair(h0.pool).swap(h0.zeroForOne ? 0 : out, h0.zeroForOne ? out : 0, address(this), data);
        }
        _tstore(T_EXPECTED_CALLER, bytes32(0));

        uint256 balAfter = IERC20(token).balanceOf(address(this));
        if (balAfter < balBefore + minProfit) {
            revert InsufficientProfit(int256(balAfter) - int256(balBefore), minProfit);
        }
        profit = balAfter - balBefore;
        emit Executed(token, amountIn, profit, uint8(n));
    }

    /// @notice Execute a cycle funded by an external flash loan (all hops run as normal swaps).
    function executeFlashLoan(uint8 provider, Hop[] calldata hops, uint256 amountIn, uint256 minProfit, uint256 maxBlock)
        external
        onlyExecutor
        returns (uint256 profit)
    {
        if (maxBlock != 0 && block.number > maxBlock) revert Expired(block.number, maxBlock);
        uint256 n = hops.length;
        if (n < 2 || hops[0].tokenIn != hops[n - 1].tokenOut) revert BadRoute();
        address token = hops[0].tokenIn;
        uint256 balBefore = IERC20(token).balanceOf(address(this));
        bytes memory data = abi.encode(hops, amountIn);

        if (provider == PROVIDER_MORPHO) {
            _tstore(T_EXPECTED_CALLER, bytes32(uint256(uint160(MORPHO))));
            IMorpho(MORPHO).flashLoan(token, amountIn, data);
        } else if (provider == PROVIDER_AAVE) {
            _tstore(T_EXPECTED_CALLER, bytes32(uint256(uint160(AAVE_POOL))));
            IAaveV3Pool(AAVE_POOL).flashLoanSimple(address(this), token, amountIn, data, 0);
        } else if (provider == PROVIDER_BALANCER) {
            _tstore(T_EXPECTED_CALLER, bytes32(uint256(uint160(BALANCER_VAULT))));
            address[] memory tokens = new address[](1);
            uint256[] memory amounts = new uint256[](1);
            tokens[0] = token;
            amounts[0] = amountIn;
            IBalancerVault(BALANCER_VAULT).flashLoan(address(this), tokens, amounts, data);
        } else {
            revert BadProvider();
        }
        _tstore(T_EXPECTED_CALLER, bytes32(0));

        uint256 balAfter = IERC20(token).balanceOf(address(this));
        if (balAfter < balBefore + minProfit) {
            revert InsufficientProfit(int256(balAfter) - int256(balBefore), minProfit);
        }
        profit = balAfter - balBefore;
        emit Executed(token, amountIn, profit, uint8(n));
    }

    // ---------------------------------------------------------------------------------------------
    // Flash-loan provider callbacks
    // ---------------------------------------------------------------------------------------------

    /// @dev Morpho Blue: repay by approving `assets` (Morpho pulls via transferFrom). Zero fee.
    function onMorphoFlashLoan(uint256 assets, bytes calldata data) external {
        _checkCaller();
        (Hop[] memory hops, uint256 amountIn) = abi.decode(data, (Hop[], uint256));
        _runAll(hops, amountIn);
        _approve(hops[0].tokenIn, MORPHO, assets);
    }

    /// @dev Aave V3: repay amount + premium via approval.
    function executeOperation(address asset, uint256 amount, uint256 premium, address, bytes calldata params)
        external
        returns (bool)
    {
        _checkCaller();
        (Hop[] memory hops, uint256 amountIn) = abi.decode(params, (Hop[], uint256));
        _runAll(hops, amountIn);
        _approve(asset, AAVE_POOL, amount + premium);
        return true;
    }

    /// @dev Balancer V2: repay by transferring back to the vault.
    function receiveFlashLoan(address[] memory tokens, uint256[] memory amounts, uint256[] memory feeAmounts, bytes memory userData)
        external
    {
        _checkCaller();
        (Hop[] memory hops, uint256 amountIn) = abi.decode(userData, (Hop[], uint256));
        _runAll(hops, amountIn);
        _safeTransfer(tokens[0], BALANCER_VAULT, amounts[0] + feeAmounts[0]);
    }

    // ---------------------------------------------------------------------------------------------
    // Pool callbacks
    // ---------------------------------------------------------------------------------------------

    function uniswapV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
        _v3Callback(amount0Delta, amount1Delta, data);
    }

    function pancakeV3SwapCallback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) external {
        _v3Callback(amount0Delta, amount1Delta, data);
    }

    function uniswapV2Call(address, uint256 amount0, uint256 amount1, bytes calldata data) external {
        _v2Callback(amount0, amount1, data);
    }

    function pancakeCall(address, uint256 amount0, uint256 amount1, bytes calldata data) external {
        _v2Callback(amount0, amount1, data);
    }

    /// @dev Aerodrome / Velodrome flash-swap callback.
    function hook(address, uint256 amount0, uint256 amount1, bytes calldata data) external {
        _v2Callback(amount0, amount1, data);
    }

    // ---------------------------------------------------------------------------------------------
    // Internals
    // ---------------------------------------------------------------------------------------------

    function _v3Callback(int256 amount0Delta, int256 amount1Delta, bytes calldata data) internal {
        _checkCaller();
        uint8 mode = abi.decode(data, (uint8));
        if (mode == MODE_PAY) {
            (, address tokenIn) = abi.decode(data, (uint8, address));
            uint256 owed = amount0Delta > 0 ? uint256(amount0Delta) : uint256(amount1Delta);
            _safeTransfer(tokenIn, msg.sender, owed);
            return;
        }
        (, Hop[] memory hops, uint256 amountIn) = abi.decode(data, (uint8, Hop[], uint256));
        uint256 received = uint256(-(hops[0].zeroForOne ? amount1Delta : amount0Delta));
        _runRest(hops, received);
        // repay hop 0 exactly what it asks for (== amountIn for exact-input swaps)
        uint256 owed0 = amount0Delta > 0 ? uint256(amount0Delta) : uint256(amount1Delta);
        if (owed0 != amountIn) revert BadRoute();
        _repay(hops[0].tokenIn, msg.sender, owed0);
    }

    function _v2Callback(uint256 amount0, uint256 amount1, bytes calldata data) internal {
        _checkCaller();
        (uint8 mode, Hop[] memory hops, uint256 amountIn) = abi.decode(data, (uint8, Hop[], uint256));
        if (mode != MODE_FLASH) revert BadRoute();
        uint256 received = hops[0].zeroForOne ? amount1 : amount0;
        _runRest(hops, received);
        _repay(hops[0].tokenIn, msg.sender, amountIn);
    }

    /// @dev Run hops[1..n-1] as normal swaps starting with `amount` of hops[1].tokenIn.
    function _runRest(Hop[] memory hops, uint256 amount) internal {
        uint256 n = hops.length;
        for (uint256 i = 1; i < n; ++i) {
            amount = _swap(hops[i], amount);
        }
    }

    /// @dev Run hops[0..n-1] as normal swaps (flash-loan path).
    function _runAll(Hop[] memory hops, uint256 amount) internal {
        uint256 n = hops.length;
        for (uint256 i = 0; i < n; ++i) {
            amount = _swap(hops[i], amount);
        }
    }

    function _swap(Hop memory h, uint256 amountIn) internal returns (uint256 amountOut) {
        if (h.kind == KIND_V3 || h.kind == KIND_PANCAKE_V3) {
            _tstore(T_EXPECTED_CALLER, bytes32(uint256(uint160(h.pool))));
            (int256 a0, int256 a1) = IV3Pool(h.pool).swap(
                address(this),
                h.zeroForOne,
                int256(amountIn),
                h.zeroForOne ? MIN_SQRT_RATIO_PLUS_ONE : MAX_SQRT_RATIO_MINUS_ONE,
                abi.encode(MODE_PAY, h.tokenIn)
            );
            amountOut = uint256(-(h.zeroForOne ? a1 : a0));
        } else {
            uint256 out = _v2QuoteOut(h.pool, h.kind, h.zeroForOne, h.tokenIn, h.feeBps, amountIn);
            _safeTransfer(h.tokenIn, h.pool, amountIn);
            IV2Pair(h.pool).swap(h.zeroForOne ? 0 : out, h.zeroForOne ? out : 0, address(this), "");
            amountOut = out;
        }
    }

    function _v2QuoteOut(address pool, uint8 kind, bool zeroForOne, address tokenIn, uint16 feeBps, uint256 amountIn)
        internal
        view
        returns (uint256)
    {
        if (kind == KIND_AERO_V2) {
            return IAeroPool(pool).getAmountOut(amountIn, tokenIn);
        }
        (uint112 r0, uint112 r1,) = IV2Pair(pool).getReserves();
        (uint256 rIn, uint256 rOut) = zeroForOne ? (uint256(r0), uint256(r1)) : (uint256(r1), uint256(r0));
        uint256 amountInWithFee = amountIn * (10_000 - feeBps);
        return (amountInWithFee * rOut) / (rIn * 10_000 + amountInWithFee);
    }

    /// @dev Repay the flash-swap pool; surfaces a precise error when the cycle came back short so that
    ///      off-chain simulation can distinguish "unprofitable" from a genuine transfer failure.
    function _repay(address token, address to, uint256 owed) internal {
        uint256 have = IERC20(token).balanceOf(address(this));
        if (have < owed) revert CannotRepay(have, owed);
        _safeTransfer(token, to, owed);
    }

    /// @dev Only the contract we are currently calling may call back, and only once.
    function _checkCaller() internal {
        if (_tload(T_EXPECTED_CALLER) != bytes32(uint256(uint160(msg.sender)))) revert BadCaller();
        _tstore(T_EXPECTED_CALLER, bytes32(0));
    }

    function _safeTransfer(address token, address to, uint256 amount) internal {
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
