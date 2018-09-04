import sys, time, os
from web3.exceptions import UnhandledRequest
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS


web3_obj = None
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
    networkStr = networkDict[network] +  ' ('
    if localNode:
        networkStr += 'local'
    else:
        networkStr += 'infura'
    networkStr += ' ' + client_name + ')'
    return networkStr 


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

def connect_w3_public_infura():
    global localNode, w3

    from web3 import Web3
    w3 = Web3(Web3.WebsocketProvider("wss://mainnet.infura.io/ws"))
    if w3.isConnected():
        localNode = False
        return True
    return False

def connect_w3_custom_infura():
    global localNode, w3

    os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
    from web3.auto.infura import w3
    if w3.isConnected():
        localNode = False
        return True
    return False

def connect_w3_local():
    global localNode, w3

    from web3.auto import w3
    if w3.isConnected():
        localNode = True
        return True
    return False
 

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
            connect()
        except:
            pass
        pass


def heartbeat():
    global shutdown
    while True:
        poll()

        if localNode:
            time.sleep(.5)
            if shutdown:
                return
        else:
            for i in range(8):
                time.sleep(2)
                if shutdown:
                    return

