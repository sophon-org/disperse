import pytest
from brownie import accounts, reverts, Disperse, MockERC20, Wei

@pytest.fixture(scope="module")
def disperse():
    return Disperse.deploy({'from': accounts[0]})

@pytest.fixture(scope="module")
def token():
    return MockERC20.deploy({'from': accounts[0]})

def test_disperse_ether(disperse):
    """Test ETH distribution to multiple recipients"""
    recipients = [accounts[1], accounts[2], accounts[3]]
    values = [Wei("0.1 ether"), Wei("0.2 ether"), Wei("0.3 ether")]
    total_value = sum(values)
    
    # Get initial balances
    initial_balances = [account.balance() for account in recipients]
    
    # Disperse ETH
    disperse.disperseEther(recipients, values, {"from": accounts[0], "value": total_value})
    
    # Check if recipients received correct amounts
    for i, account in enumerate(recipients):
        assert account.balance() == initial_balances[i] + values[i]

def test_disperse_ether_with_refund(disperse):
    """Test ETH distribution with excess ETH being refunded"""
    recipients = [accounts[1], accounts[2]]
    values = [Wei("0.1 ether"), Wei("0.2 ether")]
    excess_amount = Wei("0.1 ether")
    total_sent = sum(values) + excess_amount
    
    # Get initial balances
    initial_balances = [account.balance() for account in recipients]
    initial_sender_balance = accounts[0].balance()
    
    # Disperse ETH with excess
    tx = disperse.disperseEther(recipients, values, {"from": accounts[0], "value": total_sent})
    gas_used = tx.gas_used * tx.gas_price
    
    # Check if recipients received correct amounts
    for i, account in enumerate(recipients):
        assert account.balance() == initial_balances[i] + values[i]
    
    # Check if sender got refund (accounting for gas costs)
    assert accounts[0].balance() == initial_sender_balance - sum(values) - gas_used

def test_disperse_ether_array_mismatch(disperse):
    """Test array length mismatch error"""
    recipients = [accounts[1], accounts[2], accounts[3]]
    values = [Wei("0.1 ether"), Wei("0.2 ether")]  # One less value
    
    with reverts():
        disperse.disperseEther(recipients, values, {"from": accounts[0], "value": sum(values)})

def test_disperse_token(disperse, token):
    """Test ERC20 token distribution to multiple recipients"""
    recipients = [accounts[1], accounts[2], accounts[3]]
    values = [100, 200, 300]
    total_value = sum(values)
    
    # Approve tokens for disperse contract
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    # Get initial balances
    initial_balances = [token.balanceOf(account) for account in recipients]
    
    # Disperse tokens
    disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})
    
    # Check if recipients received correct amounts
    for i, account in enumerate(recipients):
        assert token.balanceOf(account) == initial_balances[i] + values[i]

def test_disperse_token_array_mismatch(disperse, token):
    """Test array length mismatch error for token distribution"""
    recipients = [accounts[1], accounts[2], accounts[3]]
    values = [100, 200]  # One less value
    
    token.approve(disperse.address, sum(values), {"from": accounts[0]})
    
    with reverts():
        disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})

def test_disperse_token_simple(disperse, token):
    """Test direct ERC20 token distribution"""
    recipients = [accounts[1], accounts[2], accounts[3]]
    values = [100, 200, 300]
    total_value = sum(values)
    
    # Approve tokens for disperse contract
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    # Get initial balances
    initial_balances = [token.balanceOf(account) for account in recipients]
    
    # Disperse tokens using the simple method
    disperse.disperseTokenSimple(token.address, recipients, values, {"from": accounts[0]})
    
    # Check if recipients received correct amounts
    for i, account in enumerate(recipients):
        assert token.balanceOf(account) == initial_balances[i] + values[i]

def test_insufficient_approval(disperse, token):
    """Test disperseToken with insufficient approval"""
    recipients = [accounts[1], accounts[2]]
    values = [100, 200]
    total_value = sum(values)
    
    # Approve less than needed
    insufficient_amount = total_value - 50
    token.approve(disperse.address, insufficient_amount, {"from": accounts[0]})
    
    with reverts():  # This will revert due to insufficient allowance
        disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})

def test_insufficient_balance(disperse, token):
    """Test disperseToken with insufficient balance"""
    # Transfer all tokens from account 1 to account 0
    token.transfer(accounts[1], token.balanceOf(accounts[0]), {"from": accounts[0]})
    
    recipients = [accounts[2], accounts[3]]
    values = [100, 200]
    total_value = sum(values)
    
    # Approve tokens (account 0 has none)
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    with reverts():  # This will revert due to insufficient balance
        disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})

def test_zero_address_check_ether(disperse):
    """Test that zero address is rejected in disperseEther"""
    recipients = [accounts[1], "0x0000000000000000000000000000000000000000"]
    values = [Wei("0.1 ether"), Wei("0.2 ether")]
    total_value = sum(values)
    
    with reverts():  # This should revert with InvalidRecipient
        disperse.disperseEther(recipients, values, {"from": accounts[0], "value": total_value})

def test_zero_address_check_token(disperse, token):
    """Test that zero address is rejected in disperseToken"""
    recipients = [accounts[1], "0x0000000000000000000000000000000000000000"]
    values = [100, 200]
    total_value = sum(values)
    
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    with reverts():  # This should revert with InvalidRecipient
        disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})

def test_zero_address_check_token_simple(disperse, token):
    """Test that zero address is rejected in disperseTokenSimple"""
    recipients = [accounts[1], "0x0000000000000000000000000000000000000000"]
    values = [100, 200]
    total_value = sum(values)
    
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    with reverts():  # This should revert with InvalidRecipient
        disperse.disperseTokenSimple(token.address, recipients, values, {"from": accounts[0]})

def test_zero_value_check_ether(disperse):
    """Test that zero value is rejected in disperseEther"""
    recipients = [accounts[1], accounts[2]]
    values = [Wei("0.1 ether"), 0]
    total_value = sum(values)
    
    with reverts():  # This should revert with InvalidValue
        disperse.disperseEther(recipients, values, {"from": accounts[0], "value": total_value})

def test_zero_value_check_token(disperse, token):
    """Test that zero value is rejected in disperseToken"""
    recipients = [accounts[1], accounts[2]]
    values = [100, 0]
    total_value = sum(values)
    
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    with reverts():  # This should revert with InvalidValue
        disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})

def test_zero_value_check_token_simple(disperse, token):
    """Test that zero value is rejected in disperseTokenSimple"""
    recipients = [accounts[1], accounts[2]]
    values = [100, 0]
    total_value = sum(values)
    
    token.approve(disperse.address, total_value, {"from": accounts[0]})
    
    with reverts():  # This should revert with InvalidValue
        disperse.disperseTokenSimple(token.address, recipients, values, {"from": accounts[0]})
        
def test_gas_comparison(disperse, token):
    """Compare gas usage between disperseToken and disperseTokenSimple"""
    recipients = [accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]]
    values = [100, 200, 300, 400, 500]
    total_value = sum(values)
    
    # Reset balances before gas comparison test
    # First, transfer any existing balance from the test addresses back to accounts[0]
    for acc in recipients:
        if token.balanceOf(acc) > 0:
            token.transfer(accounts[0], token.balanceOf(acc), {"from": acc})
    
    # Approve tokens for both methods
    token.approve(disperse.address, total_value * 2, {"from": accounts[0]})
    
    # Measure gas for disperseToken
    tx1 = disperse.disperseToken(token.address, recipients, values, {"from": accounts[0]})
    gas_disperseToken = tx1.gas_used
    
    # Reset balances for the second test
    for acc in recipients:
        if token.balanceOf(acc) > 0:
            token.transfer(accounts[0], token.balanceOf(acc), {"from": acc})
    
    # Measure gas for disperseTokenSimple
    tx2 = disperse.disperseTokenSimple(token.address, recipients, values, {"from": accounts[0]})
    gas_disperseTokenSimple = tx2.gas_used
    
    # Note: This doesn't assert anything, but prints gas comparison for analysis
    print(f"Gas used by disperseToken: {gas_disperseToken}")
    print(f"Gas used by disperseTokenSimple: {gas_disperseTokenSimple}")
    print(f"Gas saving with simple method: {gas_disperseToken - gas_disperseTokenSimple}")

