import pytest

from brownie import CashflowToken, accounts

@pytest.fixture
def token():
    return accounts[0].deploy(CashflowToken, "Test CFT", "tCFT", 0, 100)

def test_redeem_ETH(token):
    token.depositETH({"from": accounts[1], "value": "10 ether"})
    token.redeem(50, {"from": accounts[0]})
    initialRedeemAmount = accounts[0].balance()

    assert token.balanceOf(accounts[0].address) == 50
    assert token.ethPayouts(accounts[0].address) == "5 ether"
    assert token.balance() == "10 ether"

    token.withdrawTo(accounts[0].address)
    assert token.balance() == "5 ether"
    assert token.ethPayouts(accounts[0].address) == 0
    assert accounts[0].balance() - initialRedeemAmount == "5 ether"

    token.redeem(25, {"from": accounts[0]})
    assert token.ethPayouts(accounts[0].address) == "2.5 ether"
    token.redeem(25, {"from": accounts[0]})
    assert token.ethPayouts(accounts[0].address) == "5 ether"


def test_redeem_token(token):
    otherToken = accounts[1].deploy(CashflowToken, "Other Token", "OT", 0, 1000)
    otherToken.transfer(token.address, 100, {"from": accounts[1]})
    assert otherToken.balanceOf(token.address) == 100
    assert otherToken.balanceOf(accounts[0].address) == 0

    token.addPayoutToken(otherToken)
    token.redeem(50, {"from": accounts[0]})
    assert token.erc20Payouts(otherToken, accounts[0]) == 50
    token.redeem(25, {"from": accounts[0]})
    assert token.erc20Payouts(otherToken, accounts[0]) == 75

    token.withdrawTo(accounts[0].address)
    assert otherToken.balanceOf(token.address) == 25
    assert otherToken.balanceOf(accounts[0].address) == 75

    otherToken.transfer(token.address, 75, {"from": accounts[1]})
    token.redeem(5, {"from": accounts[0]})
    assert token.erc20Payouts(otherToken, accounts[0]) == 20
    token.withdrawTo(accounts[0].address)
    assert otherToken.balanceOf(token.address) == 80
    assert otherToken.balanceOf(accounts[0].address) == 95

