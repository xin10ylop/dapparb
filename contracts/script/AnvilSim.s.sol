// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;
import {Script, console2} from "forge-std/Script.sol";
import {ArbExecutor} from "../src/ArbExecutor.sol";
import {Pusher} from "../src/test-helpers/Pusher.sol";
import {IERC20} from "../src/interfaces/IPools.sol";
contract AnvilSim is Script {
    function run() external {
        vm.startBroadcast();
        ArbExecutor exec = new ArbExecutor(0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb, 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5, 0xBA12222222228d8Ba445958a75a0704d566BF2C8);
        Pusher pusher = new Pusher();
        vm.stopBroadcast();
        console2.log("EXEC", address(exec));
        console2.log("PUSHER", address(pusher));
    }
}
