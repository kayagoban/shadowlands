from contract.weth import Weth
from web3.auto import w3
from eth_utils import decode_hex, encode_hex
from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError
import eth_node 

#from eth_node import networkName, ethAddress

credstick = None

# import pdb; pdb.set_trace()

class ContractConfigError(Exception):
    pass

class OpenContractError(Exception):
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
    return _contract

def send_weth():
    #import pdb; pdb.set_trace()
    weth = load_contract(Weth)
    tx = weth.functions.transfer('0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 1000).buildTransaction(defaultTxDict())
    signed_tx = credstick.signTx(tx)
    rx = transact(signed_tx)


def send_ether():
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

