import sys, time, os
from decimal import Decimal
from web3.exceptions import UnhandledRequest, BadFunctionCallOutput, ValidationError, StaleBlockchain
from requests.exceptions import ConnectionError
from websockets.exceptions import InvalidStatusCode, ConnectionClosed
from web3.utils.threads import Timeout
from web3.middleware import geth_poa_middleware
from enum import Enum
from eth_utils import decode_hex, encode_hex
from ens import ENS
import threading
import asyncio
from shadowlands.block_listener import BlockListener
import pdb
from shadowlands.tui.debug import debug, end_debug
from shadowlands.sl_contract.erc20 import Erc20
from shadowlands.sl_contract import SLContract

import logging
import traceback
   
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
        self._block_listener = None
        self._erc20_balances = None
        self._sai_pip = None
        self._eth_usd = None

    @property
    def config(self):
        return self._sl_config

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
    def eth_price(self):
        return self._eth_usd

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
        try:
            return self.NETWORKDICT[self._network]
        except KeyError:
            return str(self._network)

    @property
    def network(self):
        if self._network is None:
            return None
        return self._network

    @property
    def connection_type(self):
        return self._connection_type

    @property
    def eth_balance(self):
        if self._wei_balance and self.w3 is not None:
            return self.w3.fromWei(self._wei_balance, 'ether')
        else:
            return None

    @property
    def erc20_balances(self):
        return self._erc20_balances 

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

        if self._block_listener:
            self._block_listener.shutdown = True
            self._block_listener = None

        for mod in ['web3', 'web3.auto', 'web3.auto.infura']:
            try:
                del(sys.modules[mod])
            except KeyError:
                pass


    def _force_update(self):
        try:
            self._update()
        except (TypeError, Exception) as e:
            logging.info("ERROR IN  eth_node _update_status")
 

    def _update(self):
        if self._credstick:
            self._wei_balance = self._w3.eth.getBalance(self._credstick.addressStr())
            # Trying to catch a wily web3.py bug.
            # Sometimes when using the websockets middleware,
            # strange responses start coming back.
            if self._wei_balance.__class__ != int:
                logging.debug("w3.eth.getBalance returned something other than an int! = {}".format(self._wei_balance))

            self._erc20_balances = Erc20.balances(self, self.credstick.address)
            if self._network == '1':
                try:
                    self._ens_domain = self.ens.name(self._credstick.addressStr())
                    self._eth_usd = self.w3.fromWei(self._sai_pip.eth_price(), 'ether')
                except BadFunctionCallOutput:
                    self._ens_domain = 'Unknown'
            else:
                self._ens_domain = 'Unknown'

        self._best_block = str(self._w3.eth.blockNumber)

        self._syncing = self._w3.eth.syncing
        if self._syncing not in (None, False):
            self._blocks_behind = self._syncing['highestBlock'] - self._syncing['currentBlock']
        else:
            self._blocks_behind = None


    def _update_status(self):
        logging.debug("eth_node update_status")

        try:
            self._update()
        except (Exception) as e:
            #logging.info(str(e.__traceback__))
            logging.info("eth_node _update_status: {}".format(traceback.format_exc()))



    def is_connected_with(self, _w3, connection_type, _heart_rate):
        if not _w3.isConnected():
            return False

        self._w3 = _w3

        if self._w3.version.network == '4':
            self._w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self._network = self.w3.version.network

        self._ns = ENS.fromWeb3(_w3)

        if self._network == '1' and self._sai_pip is None:
            self._sai_pip = SaiPip(self)

        self._heart_rate = _heart_rate
        self._connection_type = connection_type


        try:
            self._update_status()
        except (UnhandledRequest, StaleBlockchain):
            return False

        if self._block_listener is None:
            logging.info("start block listener")
            self._block_listener = BlockListener(self, self.config)

        return True


    def connect_config_default(self):
        try:
            fn = self.__getattribute__(self.config.default_method)
        except (AttributeError, TypeError):
            return False
        return fn()


    def connect_w3_local(self):
        self.cleanout_w3()
        from web3.auto import w3
        if self.is_connected_with(w3, 'Local node', 3):
            self.config.default_method = self.connect_w3_local.__name__
            return True
        return False


    def w3_websocket(self, uri=None):
        from web3 import Web3
        return Web3(Web3.WebsocketProvider(uri))


    #def connect_w3_public_infura(self):
    #    self.cleanout_w3()
    #    _w3 = self.w3_websocket("wss://mainnet.infura.io/ws")
    #    if self.is_connected_with(_w3, 'Public infura', 18):
    #        self.config.default_method = self.connect_w3_public_infura.__name__
    #        return True
    #    return False

    def connect_w3_public_infura(self):
        self.cleanout_w3()
        from web3.auto.infura import w3
        #_w3 = self.w3_websocket("wss://mainnet.infura.io/ws")
        if self.is_connected_with(w3, 'Public infura', 18):
            self.config.default_method = self.connect_w3_public_infura.__name__
            return True
        return False



    def connect_w3_custom_websocket(self, custom_uri=None):
        self.cleanout_w3()
        if not custom_uri:
            custom_uri = self.config.websocket_uri
        _w3 = self.w3_websocket(custom_uri)
        if self.is_connected_with(_w3, 'Custom websocket', 3):
            self.config.websocket_uri = custom_uri
            self.config.default_method = self.connect_w3_custom_websocket.__name__
            return True
        return False


    def connect_w3_custom_infura(self):
        self.cleanout_w3()
        from web3.auto.infura import w3
        if self.is_connected_with(w3, 'Custom infura', 18):
            self.config.default_method = self.connect_w3_custom_infura.__name__
            return True
        return False


    def connect_w3_custom_ipc(self, path=None):
        self.cleanout_w3()
        from web3 import Web3
        if not path:
            path = self.config.ipc_path
        w3 = Web3(Web3.IPCProvider(path))
        if self.is_connected_with(w3, 'Custom IPC', 3):
            self.config.ipc_path = path
            self.config.default_method = self.connect_w3_custom_ipc.__name__
            return True
        return False


    def connect_w3_custom_http(self, custom_uri=None):
        self.cleanout_w3()
        from web3 import Web3
        if not custom_uri:
            custom_uri = self.config.http_uri
        w3 = Web3(Web3.HTTPProvider(custom_uri))
        if self.is_connected_with(w3, 'Custom HTTP', 3):
            self.config.http_uri = custom_uri
            self.config.default_method = self.connect_w3_custom_http.__name__
            return True
        return False


    def connect_w3_gethdev_poa(self):
        self.cleanout_w3()
        from web3.auto.gethdev import w3
        if self.is_connected_with(w3, 'Gethdev PoA', 2):
            self.config.default_method = self.connect_w3_gethdev_poa.__name__
            return True
        return False


    def poll(self):
        logging.debug("eth_node poll()")
        try: 
            if self._w3.isConnected():
                self._update_status()

        except (ConnectionError, AttributeError, UnhandledRequest, Timeout, InvalidStatusCode, ConnectionClosed, TimeoutError, OSError, StaleBlockchain, ValueError) as e:
            logging.info("eth_node poll: {}".format(traceback.format_exc()))
            self.connect_config_default() or self.connect_w3_local()

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

        # Uncomment to run eth_node unthreaded for debugging
        #self.heartbeat()

        self._heartbeat_thread = threading.Thread(target=self.heartbeat)
        self.heartbeat_thread.start()

    def stop_thread(self):
        logging.debug("eth_node stop_thread()")

        if self._block_listener is not None:
            self._block_listener.shutdown = True

        if self._heartbeat_thread is not None:
            self._thread_shutdown = True
            self._heartbeat_thread.join()

    def push(self, contract_function, gas_price, gas_limit=None, value=0, nonce=None):
        tx = contract_function.buildTransaction(self.defaultTxDict(gas_price, gas_limit=gas_limit, value=value, nonce=nonce))
        logging.info("Tx submitted to credstick: {}".format(tx))
        signed_tx = self._credstick.signTx(tx)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.config.txqueue_add(self.network, self.w3.eth.getTransaction(rx))
        logging.info("%s | added tx %s", time.ctime(), rx.hex())
        return encode_hex(rx)

    def send_ether(self, destination, amount, gas_price, nonce=None):
        target = self.ens.resolve(destination) or destination
        tx_dict = self.build_send_tx(amount, target, gas_price, nonce=nonce)
        signed_tx = self._credstick.signTx(tx_dict)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        logging.info("%s | added tx %s", time.ctime(), rx.hex())
        self.config.txqueue_add(self.network, self.w3.eth.getTransaction(rx))
        return encode_hex(rx)

    def send_erc20(self, token, destination, amount, gas_price, nonce=None):
        contract_fn = token.transfer(destination, token.convert_to_integer(amount))
        rx = self.push(contract_fn, gas_price, gas_limit=150000, value=0, nonce=nonce)
        return rx


    def build_send_tx(self, amt, recipient, gas_price, gas_limit=21000, nonce=None, data=b'', convert_wei=True):
        _nonce = nonce or self.next_nonce()

        if convert_wei:
            value = self.w3.toWei(amt, 'ether')
        else:
            value = amt

        return  dict(
            chainId=int(self._network),
            nonce=_nonce,
            gasPrice=gas_price,
            gas=gas_limit,
            to=recipient,
            value=value,
            data=data
        )

    def defaultTxDict(self, gas_price, gas_limit=None, nonce=None, value=0):
        _nonce = nonce or self.next_nonce()

        txdict = dict(
            chainId=int(self._network),
            nonce=_nonce,
            gasPrice=int(gas_price),
            value=value
        ) 
        if gas_limit:
            txdict['gas'] = gas_limit
        #debug(); pdb.set_trace()
        return txdict

    '''
    Find next nonce (according to our internally kept txqueue)
    '''
    def next_nonce(self):
        tx_count = self.w3.eth.getTransactionCount(self.credstick.address)
        pending_txs = [x for x in self.config.txqueue(self.network) if x['from'] == self.credstick.address] 

        if len(pending_txs) > 0:
            sorted_txs = sorted(pending_txs, key=lambda x: x.nonce)
            return sorted_txs[0]['nonce'] + 1

        return tx_count 




class SaiPip(SLContract):

    def read(self):
        return self.functions.read().call()

    def eth_price(self):
        result = self.functions.read().call()
        int_price = int.from_bytes(result, byteorder='big')
        return Decimal(int_price)

    MAINNET='0x729D19f657BD0614b4985Cf1D82531c67569197B'
    KOVAN='0xa944bd4b25c9f186a846fd5668941aa3d3b8425f'
    ABI='''
    [{"constant":false,"inputs":[{"name":"owner_","type":"address"}],"name":"setOwner","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wut","type":"bytes32"}],"name":"poke","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"read","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"peek","outputs":[{"name":"","type":"bytes32"},{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"authority_","type":"address"}],"name":"setAuthority","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"void","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"authority","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":true,"inputs":[{"indexed":true,"name":"sig","type":"bytes4"},{"indexed":true,"name":"guy","type":"address"},{"indexed":true,"name":"foo","type":"bytes32"},{"indexed":true,"name":"bar","type":"bytes32"},{"indexed":false,"name":"wad","type":"uint256"},{"indexed":false,"name":"fax","type":"bytes"}],"name":"LogNote","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"authority","type":"address"}],"name":"LogSetAuthority","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"}],"name":"LogSetOwner","type":"event"}]'''

