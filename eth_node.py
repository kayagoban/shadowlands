import sys, time, os
from web3.exceptions import UnhandledRequest
from web3.auto import w3
from enum import Enum
from eth_utils import decode_hex, encode_hex


localNode = True
block = ""
nodeVersion = ""
network = None
syncing = {}
blocksBehind = None
weiBalance = None
ethAddress = None

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
    if weiBalance:
        return str(w3.fromWei(weiBalance, 'ether'))
    else:
        return 'Unknown'

def connect():
    global w3, localNode, nodeVersion, network

    connected = w3.isConnected()
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
    else:
        localNode = False
        del sys.modules['web3.auto']
        os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
        from web3.auto.infura import w3

    if not w3.isConnected():
        print("Sorry chummer, couldn't connect to an Ethereum node.")
        exit()

    nodeVersion = w3.version.node
    network = w3.version.network

def poll():
    global block, blocksBehind, syncing, weiBalance
    syncing = w3.eth.syncing

    if syncing:
        blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
    else:
        block = str(w3.eth.blockNumber)

    if ethAddress:
        weiBalance = w3.eth.getBalance(ethAddress)


def heartbeat():
    while True:
        #       assert w3.isConnected()
        poll()

        if localNode:
            time.sleep(.5)
        else:
            time.sleep(13)

        if shutdown:
            break




