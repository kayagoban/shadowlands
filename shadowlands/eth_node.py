import sys, time, os
from decimal import Decimal
from web3.exceptions import UnhandledRequest, BadFunctionCallOutput, ValidationError, StaleBlockchain
from websockets.exceptions import InvalidStatusCode, ConnectionClosed
from web3.utils.threads import Timeout
from web3.middleware import geth_poa_middleware
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS
import threading

import logging


import pdb
from shadowlands.tui.debug import debug

logging.basicConfig(level = logging.DEBUG, filename = "shadowlands.eth_node.log")

#debug(); #pdb.set_trace()
   
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
    def ens(self):
        return self._ns

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
 
        for mod in ['web3', 'web3.auto', 'web3.auto.infura']:
            try:
                del(sys.modules[mod])
            except KeyError:
                pass

    def _update_status(self):
            logging.debug("eth_node update_status")
            self._best_block = str(self._w3.eth.blockNumber)
            self._syncing = self._w3.eth.syncing
            if self._syncing:
                self._blocks_behind = self._syncing['highestBlock'] - self._syncing['currentBlock']


            if self._credstick:
                #logging.debug("Query eth.getBalance")
                self._wei_balance = self._w3.eth.getBalance(self._credstick.addressStr())
                if self._network == '1':
                    try:
                        self._ens_domain = self._ns.name(self._credstick.addressStr())
                    except BadFunctionCallOutput:
                        self._ens_domain = 'Unknown'
                else:
                    self._ens_domain = 'Unknown'

    def is_connected_with(self, _w3, connection_type, _heart_rate):
        if not _w3.isConnected():
            return False

        self._w3 = _w3

        if self._w3.version.network == '4':
            self._w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self._network = self.w3.version.network

        self._ns = ENS.fromWeb3(_w3)

        # If parity client...
        # Monkey patch the txpool object so we can get parity txPool info
        # self.w3.txpool = ParityCompatibleTxPool(self._w3)
        # import pdb; pdb.set_trace()

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
        #debug(); pdb.set_trace()
        self.cleanout_w3()
        if not custom_uri:
            custom_uri = self._sl_config.websocket_uri
        _w3 = self.w3_websocket(custom_uri)
        if self.is_connected_with(_w3, 'Custom websocket', 1):
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
            path = self._sl_config.ipc_path
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
            custom_uri = self._sl_config.http_uri
        w3 = Web3(Web3.HTTPProvider(custom_uri))
        if self.is_connected_with(w3, 'Custom HTTP', 2):
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
        logging.debug("eth_node poll()")
        #pdb.set_trace()
        try: 
            self._w3.isConnected()
            self._update_status()

        except (AttributeError, UnhandledRequest, Timeout, InvalidStatusCode, ConnectionClosed, TimeoutError, OSError, StaleBlockchain):
            self.connect_config_default() or self.connect_w3_local() or self.connect_w3_public_infura()
        except ValueError:
            logging.debug("eth_node: Value Error in poll()")
            self.stop_thread()
            exit()



    def heartbeat(self):
        logging.debug("eth_node heartbeat()")
        while True:
            try:
                logging.debug("eth_node call poll() from  hearttbeat()")
                self.poll()
            except Timeout:
                logging.debug("eth_node timeout in hearttbeat()")

            for i in range(self._heart_rate):
                time.sleep(1)
                if self._thread_shutdown:
                    logging.debug("eth_node thread_shutdown")
                    return

    def start_heartbeat_thread(self):
        logging.debug("eth_node start_heartbeat_thread()")
        self._heartbeat_thread = threading.Thread(target=self.heartbeat)
        self._heartbeat_thread.start()

    def stop_thread(self):
        logging.debug("eth_node stop_thread()")
        if self._heartbeat_thread == None:
            return

        self._thread_shutdown = True
        self._heartbeat_thread.join()

    def push(self, contract_function, gas_price, gas_limit=None, value=0):

        tx = contract_function.buildTransaction(self.defaultTxDict(gas_price, gas_limit=gas_limit, value=value))
        signed_tx = self._credstick.signTx(tx)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return encode_hex(rx)


    def push_wait_for_receipt(self, contract_function, gas_price, gas_limit=None, value=None):
        rx = self.push(contract_function, gas_price, gas_limit=gas_limit, value=value)
        return self.w3.eth.waitForTransactionReceipt(rx)

    def send_ether(self,destination, amount, gas_price):
        tx_dict = self.build_send_tx(amount, destination, gas_price)
        signed_tx = self._credstick.signTx(tx_dict)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return encode_hex(rx)

    def build_send_tx(self,amt, recipient, gas_price):
        return  dict(
            chainId=int(self._network),
            nonce=self.w3.eth.getTransactionCount(self.credstick.addressStr()),
            gasPrice=gas_price,
            gas=100000,
            to=recipient,
            value=self.w3.toWei(amt, 'ether'),
            data=b''
        )

    def defaultTxDict(self, gas_price, gas_limit=None, value=0):
        txdict = dict(
            chainId=int(self._network),
            nonce=self.w3.eth.getTransactionCount(self.credstick.addressStr()),
            gasPrice=int(gas_price),
            value=value
        ) 
        if gas_limit:
            txdict['gas'] = gas_limit
        return txdict


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


