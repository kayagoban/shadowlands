from contract.weth import Weth
from web3.auto import w3
from eth_utils import decode_hex, encode_hex
from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError
import eth_node 

#from eth_node import networkName, ethAddress

ERC20 = {
    'WETH': Weth
}

credstick = None

# import pdb; pdb.set_trace()

class ContractConfigError(Exception):
    pass

class OpenContractError(Exception):
    pass

class NonStandardContractDecimalsError(Exception):
    pass


def load_contract(contract_class, network = 'MAINNET'):
    try:
        _address = contract_class.__dict__[eth_node.networkName().upper()]
        _abi = contract_class.__dict__['ABI']
    except:
        raise ContractConfigError('Could not find that contract definition for the current network')


    try:
        _contract = w3.eth.contract(_address, abi=_abi)
    except:
        raise OpenContractError('Could not open the Dapp contract')

    if _contract.functions.decimals().call() != 18:
        raise NonStandardContractDecimalsError('Shadowlands assumes 18 decimal places on ERC20 contracts in its conversion methods.  Refusing to load contract for the safety of the user.')

    return _contract

# send_erc20('WETH', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5', 0.01) 
def send_erc20(token, destination, amount):
    #    import pdb; pdb.set_trace()

    weth = load_contract(ERC20[token])

    # NOTE
    # We borrow the web3 toWei method here.  We can do this because we assert 18
    # decimal places on all ERC contracts - or else they cannot load.
    # If I am able to figure out how to reliably get Decimal conversion working
    # for variable decimal place values on ERC20s, this can change.  So far things
    # are looking murky and I know I can trust the web3 code.
    value = w3.toWei(amount, 'ether')

    tx = weth.functions.transfer(destination, value).buildTransaction(defaultTxDict())
    signed_tx = credstick.signTx(tx)
    rx = transact(signed_tx)


# send_ether('0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5', 0.01) 
def send_ether(destination, amount):
    tx_dict = build_send_tx(0.00001, '0x1545fed39abc1b82c4711d8888fb35a87304817a')
    print("Unsigned transaction: ", tx_dict)
    signed_tx = credstick.signTx(tx_dict)
    print("Signed tx: ", signed_tx)
    rx = transact(signed_tx)
    print("tx receipt: ", rx)


def build_send_tx(amt, recipient):
    return  dict(
        nonce=w3.eth.getTransactionCount(eth_node.ethAddress),
        gasPrice=w3.eth.gasPrice,
        gas=100000,
        to=decode_hex(recipient),
        value=w3.toWei(amt, 'ether'),
        data=b''
    )

def transact(signed_txn):
    return w3.eth.sendRawTransaction(signed_txn.rawTransaction)

def defaultTxDict():
    return dict(
        nonce=w3.eth.getTransactionCount(eth_node.ethAddress),
        gasPrice=w3.eth.gasPrice,
        gas=800000,
        value=0
    ) 
 
def wethContract():
    return w3.eth.contract(address=dapp_addr.WETH_KOVAN, dapp_abi=WETH)

