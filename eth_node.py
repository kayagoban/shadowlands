import sys, time, os
from web3.exceptions import UnhandledRequest
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS
from web3.txpool import TxPool


import pdb


'''
txpool info

infura complains:
requests.exceptions.HTTPError: 405 Client Error: Method Not Allowed for url: https://mainnet.infura.io/

parity complains:
    ValueError: {'code': -32601, 'message': 'Method not found'}

possible we can handle parity.  public infura connections not so.
'''

'''
{"method":"parity_localTransactions","params":[],"id":1,"jsonrpc":"2.0"}'
"method":"parity_futureTransactions","params":[],"id":1,"jsonrpc":"2.0"}
"method":"parity_allTransactions","params":[],"id":1,"jsonrpc":"2.0"}
'''

class ParityCompatibleTxPool(TxPool):
    @property
    def parity_local_transactions(self):
        return self.web3.manager.request_blocking("parity_localTransactions", [])

    @property
    def parity_all_transactions(self):
        return self.web3.manager.request_blocking("parity_allTransactions", [])


class NodeConnectionError(Exception):
    pass

class ENSNotSetError(Exception):
    pass


class Node():

    NETWORKDICT = {
        '1': 'MainNet',
        '2': 'Morden',
        '3': 'Ropsten',
        '4': 'Rinkeby',
        '42': 'Kovan'
    }


    def __init__(self, sl_config=None):

        self._sl_config = sl_config

        self._w3 = None
        self._block = ""
        self._nodeVersion = ""
        self._network = None
        self._syncing = {}
        self._blocksBehind = None
        self._weiBalance = None
        self._ethAddress = None
        self._credstick = None
        self._domain = None
        self._client_name = None
        self._heart_rate = 1
        self._network_name = None

        self._localNode = None
        # Flag to shut down heartbeat thread
        self._shutdown = False

    @property
    def w3(self):
        return self._w3

    @property
    def block(self):
        return self._block

    @property
    def credstick(self):
        return self._credstick

    @credstick.setter
    def credstick(self, credstick):
        self._credstick = credstick

    @property
    def networkName(self):
        if self._network is None:
            raise NodeConnectionError
        return f"{network_name}, {networkDict[network]}"

    @property
    def ethBalanceStr(self):
        if self._network is None:
            raise NodeConnectionError
        if self._weiBalance:
            return str(self.w3.fromWei(self._weiBalance, 'ether'))
        else:
            raise NodeConnectionError

    @property
    def syncingHash(self):
        if self._syncing == {}:
            raise NodeConnectionError
        return self._syncing

    @property
    def ens_domain(self):
        if not self._domain:
            raise ENSNotSetError
        return self._domain


    def cleanout_w3(self):
        try:
            del(sys.modules['web3.auto'])
            del(sys.modules['web3.auto.infura'])
            del(sys.modules['web3.auto.gethdev'])
            del(sys.modules['web3'])
        except KeyError:
            pass

    def find_parity_tx(self, tx_hash):
        for txdata in self.w3.txpool.parity_all_transactions:
            if txdata['hash'] == mytx:
                return txdata


    def is_connected_with(self, _w3, name, _heart_rate):

        if _w3.isConnected():
            self._network_name = name
            self._w3 = _w3
            self._nodeVersion = self.w3.version.node
            self._network = self.w3.version.network
            self._ns = ENS.fromWeb3(self.w3)
            self._heart_rate = _heart_rate
            # Monkey patch the txpool object so we can get parity txPool info
            self.w3.txpool = ParityCompatibleTxPool(self.w3)

            return True
        return False


    def connect_default(self):
        try:
            fn = self._sl_config.default_method()
        except (AttributeError, TypeError):
            return False
        return fn()


    def connect_w3_local(self):

        pdb.set_trace()
        self.cleanout_w3()
        from web3.auto import w3
        if self.is_connected_with(w3, 'Local node', 1):
            self._sl_config.default_method = self.connect_w3_local
            return True
        return False


    def w3_websocket(self, uri=None):
        from web3 import Web3
        return Web3(Web3.WebsocketProvider(uri))


    def connect_w3_public_infura(self):
        self.cleanout_w3()
        _w3 = w3_websocket("wss://mainnet.infura.io/ws")
        if self.is_connected_with(_w3, 'Public infura', 18):
            self._sl_config.default_method = self.connect_w3_public_infura
            return True
        return False


    def connect_w3_custom_websocket(self, custom_uri=None):
        self.cleanout_w3()
        if not custom_uri:
            custom_uri = sl_config.websocket_uri
        _w3 = w3_websocket(custom_uri)
        if self.is_connected_with(_w3, 'Custom websocket', 2):
            self._sl_config.websocket_uri = custom_uri
            self._sl_config.default_method = self.connect_w3_custom_websocket
            return True
        return False


    def connect_w3_custom_infura(self):
        self.cleanout_w3()
        from web3.auto.infura import w3
        if self.is_connected_with(w3, 'Custom infura', 18):
            self._sl_config.default_method = self.connect_w3_custom_infura
            return True
        return False


    def connect_w3_custom_ipc(self, path=None):
        self.cleanout_w3()
        from web3 import Web3
        if not path:
            path = sl_config.ipc_path
        w3 = Web3(Web3.IPCProvider(path))
        if self.is_connected_with(w3, 'Custom IPC', 1):
            self._sl_config.ipc_path = path
            self._sl_config.default_method = self.connect_w3_custom_ipc
            return True
        return False


    def connect_w3_custom_http(self, custom_uri=None):
        self.cleanout_w3()
        from web3 import Web3
        if not custom_uri:
            custom_uri = sl_config.http_uri
        w3 = Web3(Web3.HTTPProvider(custom_uri))
        if self.is_connected_with(w3, 'Custom HTTP', 1):
            self._sl_config.http_uri = custom_uri
            self._sl_config.default_method = self.connect_w3_custom_http
            return True
        return False


    def connect_w3_gethdev_poa(self):
        self.cleanout_w3()
        from web3.auto.gethdev import w3
        if self.is_connected_with(w3, 'Gethdev PoA', 1):
            self._sl_config.default_method = self.connect_w3_gethdev_poa
            return True
        return False



    def poll(self):
        try: 
            self._syncing = self.w3.eth.syncing

            if self._syncing:
                self._blocksBehind = syncing['highestBlock'] - syncing['currentBlock']
            else:
                self._block = str(self.w3.eth.blockNumber)
            if ethAddress:
                self._weiBalance = self.w3.eth.getBalance(ethAddress)
                self._domain = ns.name(ethAddress)
        except:
            #import traceback
            #print(traceback.print_exc())
            self._localNode = None
            self._network = None
            self._syncing = {}
            self._domain = None
            try:
                self.connect_default() or self.connect_w3_local() or self.connect_w3_public_infura()
            except:
                import traceback
                print(traceback.print_exc())
            pass


    def heartbeat(self):
        while True:
            self.poll()

            for i in range(heart_rate):
                time.sleep(1)
                if self._shutdown:
                    return


    def push(self, contract_function, gas_price ):

        tx = contract_function.buildTransaction(defaultTxDict(gas_price))
        signed_tx = self._credstick.signTx(tx)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return rx


# send_ether('0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5', 0.01) 
    def send_ether(self,destination, amount, gas_price):

        tx_dict = build_send_tx(amount, destination, gas_price)
        signed_tx = self._credstick.signTx(tx_dict)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)


    def build_send_tx(self,amt, recipient, gas_price):
        return  dict(
            nonce=self.w3.eth.getTransactionCount(self._ethAddress),
            gasPrice=gas_price,
            gas=100000,
            to=decode_hex(recipient),
            value=self.w3.toWei(amt, 'ether'),
            data=b''
        )

    def defaultTxDict(self,gas_price):
        return dict(
            nonce=self.w3.eth.getTransactionCount(self._ethAddress),
            gasPrice=int(gas_price),
            gas=800000,
            value=0
        ) 

