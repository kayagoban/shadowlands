import sys, time, os
from web3.exceptions import UnhandledRequest
from web3.auto import w3
from enum import Enum

localNode = True
block = ""
nodeVersion = ""
network = None
syncing = {}
blocksBehind = None
ethBalance = None
ethAddress = None

def ethBalanceStr():
    if shadownode.ethBalance:
        return str(w3.fromWei(shadownode.ethBalance, 'ether'))
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
    global block, blocksBehind, syncing, ethBalance
    syncing = w3.eth.syncing

    if syncing:
        blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
    else:
        block = str(w3.eth.blockNumber)

    if ethAddress:
        ethBalance = w3.fromWei(w3.eth.getBalance(ethAddress), 'ether')


def heartbeat():
    while True:
        #       assert w3.isConnected()
        poll()

        if localNode:
            time.sleep(.5)
        else:
            time.sleep(13)


