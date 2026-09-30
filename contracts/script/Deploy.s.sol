// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Script, console2} from "forge-std/Script.sol";
import {ArbExecutor} from "../src/ArbExecutor.sol";

/// @notice Deploys ArbExecutor with the chain's flash-loan providers.
///         forge script script/Deploy.s.sol --rpc-url base --broadcast --private-key $PRIVATE_KEY
///         Optional env: EXECUTOR_BOT (hot wallet allowed to call execute; owner keeps withdraw rights).
contract Deploy is Script {
    struct Providers {
        address morpho;
        address aave;
        address balancer;
    }

    function providers(uint256 chainId) internal pure returns (Providers memory) {
        if (chainId == 8453) {
            return Providers({
                morpho: 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb,
                aave: 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5,
                balancer: 0xBA12222222228d8Ba445958a75a0704d566BF2C8
            });
        }
        if (chainId == 42161) {
            return Providers({
                morpho: 0x6c247b1F6182318877311737BaC0844bAa518F5e,
                aave: 0x794a61358D6845594F94dc1DB02A252b5b4814aD,
                balancer: 0xBA12222222228d8Ba445958a75a0704d566BF2C8
            });
        }
        if (chainId == 1) {
            return Providers({
                morpho: 0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb,
                aave: 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2,
                balancer: 0xBA12222222228d8Ba445958a75a0704d566BF2C8
            });
        }
        revert("unsupported chain");
    }

    function weth(uint256 chainId) internal pure returns (address) {
        if (chainId == 8453) return 0x4200000000000000000000000000000000000006;
        if (chainId == 42161) return 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
        if (chainId == 1) return 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
        revert("unsupported chain");
    }

    function run() external {
        Providers memory p = providers(block.chainid);
        vm.startBroadcast();
        ArbExecutor exec = new ArbExecutor(p.morpho, p.aave, p.balancer, weth(block.chainid));
        address bot = vm.envOr("EXECUTOR_BOT", address(0));
        if (bot != address(0)) exec.setExecutor(bot, true);
        vm.stopBroadcast();
        console2.log("ArbExecutor deployed at", address(exec));
        console2.log("owner", exec.owner());
        if (bot != address(0)) console2.log("executor bot", bot);
    }
}
