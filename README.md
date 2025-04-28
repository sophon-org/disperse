# Disperse

A gas-efficient contract for distributing ETH and ERC20 tokens to multiple recipients in a single transaction.

## Overview

The Disperse contract provides utility functions for batch distribution of both ETH and ERC20 tokens. This is particularly useful for:

- Distributing airdrops
- Paying multiple team members
- Distributing rewards or dividends
- Any scenario where you need to send tokens to multiple addresses efficiently

## Features

- **ETH Distribution**: Send ETH to multiple recipients in one transaction
- **ERC20 Distribution**: Two different methods for distributing ERC20 tokens:
  - `disperseToken`: Tokens are transferred to the contract first, then to recipients
  - `disperseTokenSimple`: Direct transfer from sender to recipients (more gas efficient)
- **Security**: Implements ReentrancyGuard to prevent reentrancy attacks
- **Safety**: Validates recipient addresses and amounts, rejecting zero addresses and zero values
- **Efficiency**: Custom error definitions for better gas efficiency

## Technical Details

- Solidity Version: 0.8.28
- EVM Target: Cancun
- OpenZeppelin Dependencies: ReentrancyGuard, SafeERC20

## Installation

```bash
# Clone the repository
git clone https://github.com/sophon-org/disperse.git
cd disperse

# Install dependencies
npm install
```

## Testing

Tests are written using the Brownie framework.

```bash
# Run tests
npm test
```

## Usage

### Deploy the Contract

```python
from brownie import accounts, Disperse

# Deploy using account 0
disperse = Disperse.deploy({'from': accounts[0]})
```

### Distribute ETH

```python
# Define recipients and amounts
recipients = [address1, address2, address3]
values = [amount1, amount2, amount3]
total = sum(values)

# Send ETH to multiple recipients
disperse.disperseEther(recipients, values, {"from": sender, "value": total})
```

### Distribute ERC20 Tokens

```python
# Approve the disperse contract to spend your tokens
token.approve(disperse.address, total_amount, {"from": sender})

# Method 1: Using disperseToken (two-step transfer)
disperse.disperseToken(token.address, recipients, values, {"from": sender})

# Method 2: Using disperseTokenSimple (direct transfer, more gas efficient)
disperse.disperseTokenSimple(token.address, recipients, values, {"from": sender})
```

## Gas Efficiency

The `disperseTokenSimple` function is designed to be more gas efficient than `disperseToken` as it transfers tokens directly from the sender to each recipient, eliminating the intermediate transfer to the contract.

## License

GPL-3 License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.