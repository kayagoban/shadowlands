import sys, time, os
from web3.exceptions import UnhandledRequest
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS
import threading

import pdb
import tui.debug

#debug(); 
#pdb.set_trace()
   
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
        self._heartbeat_thread = None
        self._w3 = None
        self._ns = None
        self._ens_domain = None
        self._nodeVersion = ""
        self._network = None
        self._syncing = None 
        self._best_block = None
        self._blocks_behind = None
        self._wei_balance = None
        self._credstick = None
        self._client_name = None
        self._heart_rate = 1
        self._connection_type = None
        self._localNode = None
        self._thread_shutdown = False

    @property
    def w3(self):
        return self._w3

    @property
    def best_block(self):
        return self._best_block

    @property
    def blocks_behind(self):
        return self._blocks_behind

    @property
    def credstick(self):
        return self._credstick

    @credstick.setter
    def credstick(self, credstick):
        self._credstick = credstick

    @property
    def network_name(self):
        if self._network is None:
            return None
        return self.NETWORKDICT[self._network]

    @property
    def connection_type(self):
        return self._connection_type

    @property
    def eth_balance(self):
        if self._wei_balance:
            return self.w3.fromWei(self._wei_balance, 'ether')
        else:
            return None

    @property
    def syncing_hash(self):
        return self._syncing

    @property
    def ens_domain(self):
        if self._credstick:
            return self._ens_domain
        else:
            return None


    @property
    def heartbeat_thread(self):
        return self._heartbeat_thread

    @property 
    def thread_shutdown(self):
        pass

    @thread_shutdown.setter
    def thread_shutdown(self, bool_value):
        self._thread_shutdown = bool_value

    def cleanout_w3(self):
        self._localNode = None
        self._network = None
        self._syncing = None
        self._ns = None
        self._ens_domain = None
        self._w3 = None
 
        for mod in ['web3', 'web3.auto', 'web3.auto.infura', 'web3.auto.gethdev']:
            try:
                del(sys.modules[mod])
            except KeyError:
                pass

    def _update_status(self):
            self._nodeVersion = self._w3.version.node
            self._network = self._w3.version.network
            self._best_block = str(self._w3.eth.blockNumber)
            self._syncing = self._w3.eth.syncing
            if self._syncing:
                self._blocks_behind = self._syncing['highestBlock'] - self._syncing['currentBlock']

            self._ns = ENS.fromWeb3(self._w3)

            if self._credstick:
                self._wei_balance = self._w3.eth.getBalance(self._credstick.addressStr())
                self._ens_domain = self._ns.name(self._credstick.addressStr())


    def is_connected_with(self, _w3, connection_type, _heart_rate):
        if not _w3.isConnected():
            return False

        self._w3 = _w3
        # Monkey patch the txpool object so we can get parity txPool info
        self.w3.txpool = ParityCompatibleTxPool(self._w3)
        self._heart_rate = self._heart_rate
        self._connection_type = connection_type

        try:
            self._update_status()
        except UnhandledRequest:
            return False

        return True

    def connect_config_default(self):
        try:
            fn = self.__getattribute__(self._sl_config.default_method)
        except (AttributeError, TypeError):
            return False
        return fn()


    def connect_w3_local(self):

        self.cleanout_w3()
        from web3.auto import w3
        if self.is_connected_with(w3, 'Local node', 1):
            self._sl_config.default_method = self.connect_w3_local.__name__
            return True
        return False


    def w3_websocket(self, uri=None):
        from web3 import Web3
        return Web3(Web3.WebsocketProvider(uri))


    def connect_w3_public_infura(self):
        self.cleanout_w3()
        _w3 = self.w3_websocket("wss://mainnet.infura.io/ws")
        if self.is_connected_with(_w3, 'Public infura', 18):
            self._sl_config.default_method = self.connect_w3_public_infura.__name__
            return True
        return False


    def connect_w3_custom_websocket(self, custom_uri=None):
        self.cleanout_w3()
        if not custom_uri:
            custom_uri = sl_config.websocket_uri
            _w3 = self.w3_websocket(custom_uri)
            if self.is_connected_with(_w3, 'Custom websocket', 2):
                self._sl_config.websocket_uri = custom_uri
                self._sl_config.default_method = self.connect_w3_custom_websocket.__name__
                return True
        return False


    def connect_w3_custom_infura(self):
        self.cleanout_w3()
        from web3.auto.infura import w3
        if self.is_connected_with(w3, 'Custom infura', 18):
            self._sl_config.default_method = self.connect_w3_custom_infura.__name__
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
                self._sl_config.default_method = self.connect_w3_custom_ipc.__name__
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
                self._sl_config.default_method = self.connect_w3_custom_http.__name__
                return True
        return False


    def connect_w3_gethdev_poa(self):
        self.cleanout_w3()
        from web3.auto.gethdev import w3
        if self.is_connected_with(w3, 'Gethdev PoA', 1):
            self._sl_config.default_method = self.connect_w3_gethdev_poa.__name__
            return True
        return False


    def poll(self):
        #pdb.set_trace()
        try: 
            self._w3.isConnected()
            self._update_status()

        except (AttributeError, UnhandledRequest):
            self.connect_config_default() or self.connect_w3_local() or self.connect_w3_public_infura()


    def heartbeat(self):
        while True:
            self.poll()

            for i in range(self._heart_rate):
                time.sleep(1)
                if self._thread_shutdown:
                    return

    def start_heartbeat_thread(self):
        self._heartbeat_thread = threading.Thread(target=self.heartbeat)
        self._heartbeat_thread.start()

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
            nonce=self.w3.eth.getTransactionCount(self._eth_address),
            gasPrice=gas_price,
            gas=100000,
            to=decode_hex(recipient),
            value=self.w3.toWei(amt, 'ether'),
            data=b''
        )

    def defaultTxDict(self,gas_price):
        return dict(
            nonce=self.w3.eth.getTransactionCount(self._eth_address),
            gasPrice=int(gas_price),
            gas=800000,
            value=0
        ) 

    def find_parity_tx(self, tx_hash):
        for txdata in self.w3.txpool.parity_all_transactions:
            if txdata['hash'] == mytx:
                return txdata




from web3.txpool import TxPool

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


