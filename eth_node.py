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


def connect():
    global w3, localNode, nodeVersion, network, web3_obj, ns, client_name

    try:
        del(sys.modules['web3.auto'])
        del(sys.modules['web3.auto.infura'])
    except KeyError:
        pass

    from web3.auto import w3
    connected = w3.isConnected()

    localNode = True
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
        client_name = 'Parity'
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
        localNode = True
        client_name = 'Geth'
    else:
        try:
            del sys.modules['web3.auto']
        except KeyError:
            pass
        os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
        from web3.auto.infura import w3
        if w3.isConnected():
            localNode = False
            if w3.version.node.startswith('Parity'):
                client_name = 'Parity'
            elif w3.version.node.startswith('Geth'):
                client_name = 'Geth'
       
       #    enode = w3.admin.nodeInfo['enode']
 

        #localNode = None
        #network = None
        #syncing = {}
        #domain = None
        #return
        #raise Exception
        #pass


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



        


