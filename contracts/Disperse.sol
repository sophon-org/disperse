// SPDX-License-Identifier: UNLICENSED

pragma solidity 0.8.28;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/// @title Disperse Contract
/// @notice Allows batch distribution of ETH and ERC20 tokens
/// @dev Provides multiple methods for efficient token distribution
contract Disperse is ReentrancyGuard {
    using SafeERC20 for IERC20;

    /// @notice Error thrown when recipients and values arrays have different lengths
    error ArrayLengthMismatch();

    /// @notice Error thrown when a transfer operation fails
    error TransferFailed();

    /// @notice Error thrown when a recipient address is invalid
    error InvalidRecipient();

    /// @notice Error thrown when a value is invalid
    error InvalidValue();

    /// @notice Distributes ETH to multiple recipients in a single transaction
    /// @param recipients Array of recipient addresses
    /// @param values Array of ETH amounts to send to each recipient
    /// @dev Any remaining ETH is returned to the sender
    function disperseEther(address[] calldata recipients, uint256[] calldata values) external payable nonReentrant {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        bool success;
        for (uint256 i; i < len; i++) {
            address recipient = recipients[i];
            uint256 value = values[i];
            if (recipient == address(0)) revert InvalidRecipient();
            if (value == 0) revert InvalidValue();

            (success,) = recipient.call{value: value}("");
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
    function disperseToken(IERC20 token, address[] calldata recipients, uint256[] calldata values)
        external
        nonReentrant
    {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        uint256 i;
        uint256 total;
        for (i = 0; i < len; i++) {
            total += values[i];
        }

        token.safeTransferFrom(msg.sender, address(this), total);

        for (i = 0; i < len; i++) {
            address recipient = recipients[i];
            uint256 value = values[i];
            if (recipient == address(0)) revert InvalidRecipient();
            if (value == 0) revert InvalidValue();

            token.safeTransfer(recipient, value);
        }
    }

    /// @notice Distributes ERC20 tokens directly from sender to recipients
    /// @param token The ERC20 token to distribute
    /// @param recipients Array of recipient addresses
    /// @param values Array of token amounts to send to each recipient
    /// @dev More gas efficient as it skips the intermediate transfer to this contract
    function disperseTokenSimple(IERC20 token, address[] calldata recipients, uint256[] calldata values)
        external
        nonReentrant
    {
        uint256 len = recipients.length;
        if (len != values.length) revert ArrayLengthMismatch();

        for (uint256 i; i < len; i++) {
            address recipient = recipients[i];
            uint256 value = values[i];
            if (recipient == address(0)) revert InvalidRecipient();
            if (value == 0) revert InvalidValue();

            token.safeTransferFrom(msg.sender, recipient, value);
        }
    }
}
