// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.23;


interface IERC20 {
    function transfer(address to, uint256 value) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 value
    ) external returns (bool);
}

contract Disperse {
    function disperseEther(
        address[] calldata recipients,
        uint256[] calldata values
    ) external payable {
        uint256 len = recipients.length;
        require(len == values.length, "mismatch");

        bool success;
        for (uint256 i; i < len;) {
            (success, ) = recipients[i].call{ value: values[i] }("");
            require(success, "failed");

            unchecked { i++; }
        }

        uint256 balance = address(this).balance;
        if (balance != 0) {
            (success, ) = msg.sender.call{ value: balance }("");
            require(success, "failed");
        }
    }

    function disperseToken(
        IERC20 token,
        address[] calldata recipients,
        uint256[] calldata values
    ) external {
        uint256 len = recipients.length;
        require(len == values.length, "mismatch");

        uint256 i;
        uint256 total;
        for (i = 0; i < len;) {
            total += values[i];
            unchecked { i++; }
        }

        require(token.transferFrom(msg.sender, address(this), total));

        for (i = 0; i < len;) {
            require(token.transfer(recipients[i], values[i]));
            unchecked { i++; }
        }
    }

    function disperseTokenSimple(
        IERC20 token,
        address[] calldata recipients,
        uint256[] calldata values
    ) external {
        uint256 len = recipients.length;
        require(len == values.length, "mismatch");

        for (uint256 i; i < len;) {
            require(token.transferFrom(msg.sender, recipients[i], values[i]));
            unchecked { i++; }
        }
    }
}
