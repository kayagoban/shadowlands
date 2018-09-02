import sys, time, os
from web3.exceptions import UnhandledRequest
from web3.auto import w3
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS


web3_obj = None
localNode = True
block = ""
nodeVersion = ""
network = None
syncing = {}
blocksBehind = None
weiBalance = None
ethAddress = None
domain = None


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
    return networkDict[network]


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


def connect():
    global w3, localNode, nodeVersion, network, web3_obj, ns

    try:
        del(sys.modules['web3.auto'])
        del(sys.modules['web3.auto.infura'])
    except KeyError:
        pass

    connected = w3.isConnected()
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
    else:
        localNode = False
        try:
            del sys.modules['web3.auto']
        except KeyError:
            pass
        os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
        from web3.auto.infura import w3

    if not w3.isConnected():
        raise Exception

    nodeVersion = w3.version.node
    network = w3.version.network
    web3_obj = w3
    ns = ENS.fromWeb3(w3)


def poll():
    global block, blocksBehind, syncing, weiBalance, domain, network

    try: 
        syncing = w3.eth.syncing
        network = w3.version.network

        if syncing:
            blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
        else:
            block = str(w3.eth.blockNumber)
        if ethAddress:
            weiBalance = w3.eth.getBalance(ethAddress)
            domain = ns.name(ethAddress)
    except:
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
        #       assert w3.isConnected()
        poll()

        if localNode:
            time.sleep(.5)
            if shutdown:
                return
        else:
            for i in range(7):
                time.sleep(2)
                if shutdown:
                    return



        


