
ERC20 = {
    'WETH': Weth
}


# send_erc20('WETH', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5', 0.01) 
def send_erc20(token, destination, amount, gas_price):

    # NOTE
    # We borrow the web3 toWei method here.  We can do this because we assert 18
    # decimal places on all ERC contracts - or else they cannot load.
    # If I am able to figure out how to reliably get Decimal conversion working
    # for variable decimal place values on ERC20s, this can change.  So far things
    # are looking murky and I know I can trust the web3 code. (I hope)
    value = node.w3.toWei(amount, 'ether')

    return push(
        ERC20[token].transfer(destination, value), gas_price
    )


