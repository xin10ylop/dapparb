// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/// Raw transfer-behaviour probe, run only inside eth_call with state overrides.
/// The same runtime code is placed at the batcher address and at every holder address.
/// `run` (at the batcher) calls `probeOne` on each holder; `probeOne` executes with msg.sender-of-transfer = holder.
/// Nothing reverts: every external interaction is a low-level call and every result is returned as raw data.
contract TransferProbe {
    struct Item {
        address holder;
        address token;
    }

    uint256 internal constant PROBE_GAS = 1_500_000;

    /// @return ok   per item: whether the call into the holder's probeOne returned normally
    /// @return data per item: abi-encoded probeOne result (or the raw revert data when ok == false)
    function run(Item[] calldata items, address recipient, uint256 bps)
        external
        returns (bool[] memory ok, bytes[] memory data)
    {
        ok = new bool[](items.length);
        data = new bytes[](items.length);
        for (uint256 i = 0; i < items.length; i++) {
            (ok[i], data[i]) = items[i].holder.call{gas: PROBE_GAS + 300_000}(
                abi.encodeWithSelector(this.probeOne.selector, items[i].token, recipient, bps)
            );
        }
    }

    function _bal(address token, address who) internal view returns (bool ok, uint256 v) {
        (bool s, bytes memory r) = token.staticcall{gas: 200_000}(abi.encodeWithSelector(0x70a08231, who));
        if (s && r.length >= 32) return (true, abi.decode(r, (uint256)));
        return (false, 0);
    }

    /// Executed at the holder address (its code replaced by this contract).
    function probeOne(address token, address recipient, uint256 bps)
        external
        returns (
            bool balOk,
            uint256 holderBefore,
            uint256 amount,
            uint256 recipientBefore,
            bool callSuccess,
            bytes memory retData,
            uint256 gasUsed,
            uint256 recipientAfter,
            uint256 holderAfter
        )
    {
        (balOk, holderBefore) = _bal(token, address(this));
        amount = holderBefore * bps / 10_000;
        (, recipientBefore) = _bal(token, recipient);
        uint256 g0 = gasleft();
        (callSuccess, retData) = token.call{gas: PROBE_GAS}(abi.encodeWithSelector(0xa9059cbb, recipient, amount));
        gasUsed = g0 - gasleft();
        (, recipientAfter) = _bal(token, recipient);
        (, holderAfter) = _bal(token, address(this));
    }
}
