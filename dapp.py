from contract import Contract
from contract.weth import Weth
from contract.ens import Ens
from contract.ens_registry import EnsRegistry
from contract.ens_resolver import EnsResolver
from contract.ens_reverse_resolver import EnsReverseResolver
from eth_utils import decode_hex, encode_hex
from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
import eth_node 


ERC20 = {
    'WETH': Weth
}

credstick = None

node = None

def register_node_on_contracts():
    Contract.node = node

# import pdb; pdb.set_trace()


# reveal_bid('ceilingcat', '0.01', 'burly jumper knife')
def ens_reveal_bid(name, bid_amount, secret, gas_price):
    return push(
        Ens.unsealBid(name, bid_amount, secret), gas_price
    )

# ens_finalize_auction(name)
def ens_finalize_auction(name, gas_price):
    return push(
        Ens.finalizeAuction(name), gas_price
    )

# Sets the resolver on your name record.  No idea why we have to do this - there should 
# only be one resolver per ENS registrar.  But who am I to question the gods?
#
# Both of these invocations have the same precise effect.  the .eth domain will be added
# if it is not already in the string.
#
# register_ens_resolver('ceilingcat')
# register_ens_resolver('ceilingcat.eth')
def register_ens_resolver(name, gas_price):
    return push( 
        EnsRegistry.set_resolver(name), gas_price
    )

# Sets the address that your name resolves to.  Will fail if your credstick does not
# own the name.
#
# set_ens_resolver_address('ceilingcat', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5')
# set_ens_resolver_address('ceilingcat.eth', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5')
def set_ens_resolver_address(name, address_target, gas_price):
    return push(
        EnsResolver.set_address(name, address_target), gas_price
    )

# Sets the reverse record for the name given to the address of your credstick,
# if indeed you own the name.  This is how you set your nick.
# 
# set_ens_reverse_lookup('ceilingcat')
# set_ens_reverse_lookup('ceilingcat.eth')
def set_ens_reverse_lookup(name, gas_price):
    return push(
        EnsReverseResolver.set_name(name), gas_price
    )
 

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


# send_ether('0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5', 0.01) 
def send_ether(destination, amount, gas_price):
    tx_dict = build_send_tx(amount, destination, gas_price)
    signed_tx = credstick.signTx(tx_dict)
    rx = node.w3.eth.sendRawTransaction(signed_tx.rawTransaction)


def push( contract_function, gas_price ):
    tx = contract_function.buildTransaction(defaultTxDict(gas_price))
    signed_tx = credstick.signTx(tx)

    # TODO wrap in a try to catch credstick exception if user chooses
    # not to verify transaction on credstick. (CommException on ledger, etc)
    rx = node.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    
    return rx

def build_send_tx(amt, recipient, gas_price):
    return  dict(
        nonce=node.w3.eth.getTransactionCount(eth_node.ethAddress),
        gasPrice=gas_price,
        gas=100000,
        to=decode_hex(recipient),
        value=node.w3.toWei(amt, 'ether'),
        data=b''
    )

def defaultTxDict(gas_price):
    _dict = dict(
        nonce=node.w3.eth.getTransactionCount(eth_node.ethAddress),
        gasPrice=int(gas_price),
        gas=800000,
        value=0
    ) 

    return _dict

