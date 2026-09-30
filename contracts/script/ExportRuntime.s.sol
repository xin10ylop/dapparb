// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Script} from "forge-std/Script.sol";
import {ArbExecutor} from "../src/ArbExecutor.sol";

/// @notice Deploys ArbExecutor in a local simulation (no broadcast) and writes its runtime bytecode, with the
///         chain's immutables baked in, to a file the bot injects via eth_call state override for dry runs.
///         forge script script/ExportRuntime.s.sol --rpc-url base --sig "run(string)" ../bot/src/exec/artifacts/ArbExecutor.base.runtime.hex
contract ExportRuntime is Script {
    function run(string memory outPath) external {
        (address morpho, address aave, address balancer) = block.chainid == 8453
            ? (0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb, 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5, 0xBA12222222228d8Ba445958a75a0704d566BF2C8)
            : block.chainid == 42161
                ? (0x6c247b1F6182318877311737BaC0844bAa518F5e, 0x794a61358D6845594F94dc1DB02A252b5b4814aD, 0xBA12222222228d8Ba445958a75a0704d566BF2C8)
                : (0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb, 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2, 0xBA12222222228d8Ba445958a75a0704d566BF2C8);
        address weth = block.chainid == 8453
            ? 0x4200000000000000000000000000000000000006
            : block.chainid == 42161 ? 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 : 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
        ArbExecutor exec = new ArbExecutor(morpho, aave, balancer, weth);
        vm.writeFile(outPath, vm.toString(address(exec).code));
    }
}
