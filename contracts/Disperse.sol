// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.28;

/// @title IERC20Stub Interface
/// @notice Basic interface for ERC20 token transfer functions
interface IERC20Stub {
    /// @notice Transfer tokens to a specified address
    /// @param to Address to transfer to
    /// @param value Amount to transfer
    /// @return Success status
    function transfer(address to, uint256 value) external returns (bool);

    /// @notice Transfer tokens from one address to another
    /// @param from Address to transfer from
    /// @param to Address to transfer to
    /// @param value Amount to transfer
    /// @return Success status
    function transferFrom(address from, address to, uint256 value) external returns (bool);
}

/// @title Disperse Contract
/// @notice Allows batch distribution of ETH and ERC20 tokens
/// @dev Provides multiple methods for efficient token distribution
contract Disperse {
    /// @notice Error thrown when recipients and values arrays have different lengths
    error ArrayLengthMismatch();

    /// @notice Error thrown when a transfer operation fails
    error TransferFailed();

    /// @notice Distributes ETH to multiple recipients in a single transaction
    /// @param recipients Array of recipient addresses
    /// @param values Array of ETH amounts to send to each recipient
    /// @dev Any remaining ETH is returned to the sender
    function disperseEther(address[] calldata recipients, uint256[] calldata values) external payable {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        bool success;
        for (uint256 i; i < len; i++) {
            (success,) = recipients[i].call{value: values[i]}("");
            if (!success) revert TransferFailed();
        }

        uint256 balance = address(this).balance;
        if (balance != 0) {
            (success,) = msg.sender.call{value: balance}("");
            if (!success) revert TransferFailed();
        }
    }

    /// @notice Distributes ERC20 tokens to multiple recipients in a single transaction
    /// @param token The ERC20 token to distribute
    /// @param recipients Array of recipient addresses
    /// @param values Array of token amounts to send to each recipient
    /// @dev Transfers total tokens to this contract first, then distributes to recipients
    function disperseToken(IERC20Stub token, address[] calldata recipients, uint256[] calldata values) external {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        uint256 i;
        uint256 total;
        for (i = 0; i < len; i++) {
            total += values[i];
        }

        if (!token.transferFrom(msg.sender, address(this), total)) revert TransferFailed();

        for (i = 0; i < len; i++) {
            if (!token.transfer(recipients[i], values[i])) revert TransferFailed();
        }
    }

    /// @notice Distributes ERC20 tokens directly from sender to recipients
    /// @param token The ERC20 token to distribute
    /// @param recipients Array of recipient addresses
    /// @param values Array of token amounts to send to each recipient
    /// @dev More gas efficient as it skips the intermediate transfer to this contract
    function disperseTokenSimple(IERC20Stub token, address[] calldata recipients, uint256[] calldata values) external {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        for (uint256 i; i < len; i++) {
            if (!token.transferFrom(msg.sender, recipients[i], values[i])) revert TransferFailed();
        }
    }
}
