import sys, time, os
from web3.exceptions import UnhandledRequest
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS

import pdb

localNode = None
block = ""
nodeVersion = ""
network = None
syncing = {}
blocksBehind = None
weiBalance = None
ethAddress = None
domain = None
client_name = None
heart_rate = 1

custom_http_uri = None
custom_websocket_uri = None

network_name = None

# Flag to shut down heartbeat thread
shutdown = False

networkDict = {
    '1': 'MainNet',
    '2': 'Morden',
    '3': 'Ropsten',
    '4': 'Rinkeby',
    '42': 'Kovan'
}

def networkName():
    if network is None:
        raise Exception
    return network_name

def ethBalanceStr():
    if network is None:
        raise Exception
    if weiBalance:
        return str(w3.fromWei(weiBalance, 'ether'))
    else:
        return 'Unknown'

def syncingHash():
    global syncing

    if syncing == {}:
        raise Exception

    return syncing

def ens_domain():
    global domain
    
    if not domain:
        raise Exception

    return domain


def cleanout_w3():
    try:
        del(sys.modules['web3.auto'])
        del(sys.modules['web3.auto.infura'])
        del(sys.modules['web3'])
    except KeyError:
        pass


def is_connected_with(_w3, name, _heart_rate):
    global w3, network_name, nodeVersion, network, web3_obj, ns, localNode, heart_rate

    #pdb.set_trace()

    if _w3.isConnected():
        network_name = name
        w3 = _w3
        nodeVersion = w3.version.node
        network = w3.version.network
        web3_obj = w3
        ns = ENS.fromWeb3(w3)
        heart_rate = _heart_rate

        return True
    return False


def w3_websocket(uri=None):
    from web3 import Web3
    return Web3(Web3.WebsocketProvider(uri))

def connect_w3_public_infura():
    cleanout_w3()
    _w3 = w3_websocket("wss://mainnet.infura.io/ws")
    return is_connected_with(_w3, 'Public infura', 18)

def connect_w3_custom_websocket():
    cleanout_w3()
    _w3 = w3_websocket("wss://mainnet.infura.io/ws")
    return is_connected_with(_w3, 'Custom websocket', 18)


def connect_w3_custom_infura():
    cleanout_w3()
    os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
    from web3.auto.infura import w3
    #pdb.set_trace()
    return is_connected_with(w3, 'Custom infura', 18)

def connect_w3_local():
    cleanout_w3()
    from web3.auto import w3
    return is_connected_with(w3, 'Local node', 1.5)

def connect_w3_custom_http():
    cleanout_w3()
    from web3 import Web3
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"), 3)
    return is_connected_with(w3, 'Custom HTTP')

def connect_w3_custom_ipc():
    cleanout_w3()
    from web3 import Web3
    w3 = Web3(Web3.IPCProvider("~/Library/Ethereum/geth.ipc"))
    return is_connected_with(w3, 'Custom IPC', 1)

def connect_w3_gethdev_poa():
    cleanout_w3()
    from web3.auto.gethdev import w3
    return is_connected_with(w3, 'Gethdev PoA', 1)


def connect():
    global w3, nodeVersion, network, web3_obj, ns, client_name

    for connect_w3 in [ connect_w3_local, connect_w3_public_infura ]:
        cleanout_w3()
        if connect_w3():
            break

    if w3.version.node.startswith('Parity'):
        client_name = 'Parity'
    elif w3.version.node.startswith('Geth'):
        client_name = 'Geth'

    nodeVersion = w3.version.node
    network = w3.version.network
    web3_obj = w3
    ns = ENS.fromWeb3(w3)


def poll():
    global block, blocksBehind, syncing, weiBalance, domain, network

    try: 
        syncing = w3.eth.syncing

        if syncing:
            blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
        else:
            block = str(w3.eth.blockNumber)
        if ethAddress:
            weiBalance = w3.eth.getBalance(ethAddress)
            domain = ns.name(ethAddress)
    except:
        localNode = None
        network = None
        syncing = {}
        domain = None
        try:
            connect_w3_local() or connect_w3_public_infura()
        except:
            pass
        pass


def heartbeat():
    global shutdown
    while True:
        poll()

        for i in range(heart_rate):
            time.sleep(1)
            if shutdown:
                return

