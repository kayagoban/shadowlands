import sys, time, os
from decimal import Decimal
from web3.exceptions import BadFunctionCallOutput, ValidationError, StaleBlockchain
from requests.exceptions import ConnectionError
from websockets.exceptions import InvalidStatusCode, ConnectionClosed
#from web3.utils.threads import Timeout
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
import schedule

from time import sleep
import logging
import traceback
   
logging.basicConfig(level = logging.DEBUG, filename = "shadowlands.log")

class NodeConnectionError(Exception):
    pass

class ENSNotSetError(Exception):
    pass
 

class Node():

    NETWORKDICT = {
        1: 'MainNet',
        2: 'Morden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan'
    }

    def __init__(self, sl_config=None):

        self.thread_shutdown = False
        self.credstick = None
        self.ns = None
        self.best_block = '...' 
        self.blocks_behind = None
        self.erc20_balances = None
        self.syncing_hash = None 
        self.heartbeat_thread = None
        self.config = sl_config
        self.w3 = None
        self.network = None

        self._ens_domain = None
        self._wei_balance = None
        self._client_name = None
        self._heart_rate = 1
        self._connection_type = None
        self._localNode = None
        self._block_listener = None
        self._sai_pip = None
        self.eth_price = None
        self.update_sem = threading.Semaphore(value=2)
        self.update_lock = threading.Lock()

        self.start_heartbeat_thread()

    @property
    def network_name(self):
        if self.network is None:
            return None
        try:
            return self.NETWORKDICT[self.network]
        except KeyError:
            return str(self.network)

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
    def ens_domain(self):
        if self.credstick:
            return self._ens_domain
        else:
            return None

    def cleanout_w3(self):
        self._localNode = None
        self.network = None
        self.syncing_hash = None
        self.ens = None
        self._ens_domain = None
        self.w3 = None

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
        # semaphore only allows one thread to wait on update
  
        self.update_sem.acquire(blocking=False)
 
        with self.update_lock:
          if self.credstick:
            self._wei_balance = self.w3.eth.getBalance(self.credstick.addressStr())
            self.erc20_balances = Erc20.balances(self, self.credstick.address)
            if self.network == '1':
                try:
                    self._ens_domain = self.ens.name(self.credstick.addressStr())
                    self.eth_price = self.w3.fromWei(self._sai_pip.eth_price(), 'ether')
                except BadFunctionCallOutput:
                    self._ens_domain = 'Unknown'
            else:
                self._ens_domain = 'Unknown'

          self.best_block = str(self.w3.eth.blockNumber)

          self.syncing_hash = self.w3.eth.syncing
          if self.syncing_hash not in (None, False):
              self.blocks_behind = self.syncing_hash['highestBlock'] - self.syncing_hash['currentBlock']
          else:
              self.blocks_behind = None

        self.update_sem.release()



    def _update_status(self):
        logging.debug("eth_node update_status")

        try:
            threading.Thread(target=self._update).start()
            #self._update()
        except (Exception) as e:
            #logging.info(str(e.__traceback__))
            logging.info("eth_node _update_status: {}".format(traceback.format_exc()))



    def is_connected_with(self, _w3, connection_type, _heart_rate, _bg_w3=None):
        if not _w3.isConnected():
            return False

        self.w3 = _w3

        self.network = self.w3.eth.chainId

        if self.network == 4:
            self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        self.ens = ENS.fromWeb3(_w3)

        if self.network == 1 and self._sai_pip is None:
            self._sai_pip = SaiPip(self)

        self._heart_rate = _heart_rate
        self._connection_type = connection_type


        try:
            self._update_status()
        except (StaleBlockchain):
            return False

        logging.debug("is connected with " + connection_type + " every " + str(_heart_rate) + " seconds.")

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

    def connect_w3_infura(self):
      self.cleanout_w3()
      from web3.auto.infura import w3 as bg_w3
      from web3.auto.infura import w3
      if self.is_connected_with(w3, 'Infura', 14, _bg_w3 = bg_w3):
        self.config.default_method = self.connect_w3_infura.__name__
        return True
      return False


    def connect_w3_public_infura(self):
        self.cleanout_w3()
        from web3.auto.infura import w3
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
        #from web3.auto.infura import w3
        proj_id = os.environ.get('WEB3_INFURA_PROJECT_ID')
        proj_secret = os.environ.get('WEB3_INFURA_API_SECRET')
        uri = f"wss://:{proj_secret}@mainnet.infura.io/ws/v3/{proj_id}"
        w3 = Web3(Web3.WebsocketProvider(uri, websocket_kwargs={'ping_interval': None}))
        #wss://:1f32c7000d4146bea9f78017427ae53a@mainnet.infura.io/ws/v3/3404d141198b45b191c7af24311cd9ea
        #ping_interval to None k

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
      # (ConnectionError, AttributeError, Timeout, InvalidStatusCode, ConnectionClosed, TimeoutError, OSError, StaleBlockchain, ValueError)

      logging.debug("eth_node poll()")
      if self.w3 != None:
          if self.w3.isConnected():
              self._update_status()
      else:
        logging.info("eth_node poll: {}".format(traceback.format_exc()))
        self.connect_config_default() or self.connect_w3_local()
      logging.debug("eth_node poll() finished")

 
    def heartbeat(self):
      self.poll()
      self._block_listener = BlockListener(self, self.config)

      # Eth node heartbeat
      #schedule.every(15).to(20).seconds.do(self.poll)
      #schedule.every(15).to(20).seconds.do(self._block_listener.listen)
      while True:
        schedule.run_pending()
        sleep(.2)
        if self.thread_shutdown:
          logging.debug("eth_node thread_shutdown")
          return


    def start_heartbeat_thread(self):
      logging.debug("eth_node start_heartbeat_thread()")
      self.heartbeat_thread = threading.Thread(target=self.heartbeat)
      self.heartbeat_thread.start()

    def stop_thread(self):
        logging.debug("eth_node stop_thread()")

        if self._block_listener is not None:
            self._block_listener.shutdown = True

        if self.heartbeat_thread is not None:
            self.thread_shutdown = True
            self.heartbeat_thread.join()

    def push_raw(self, tx):
        self.credstick.signTx(tx_dict)
        rx = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.config.txqueue_mutate('add', self.network, self.w3.eth.getTransaction(rx))
        logging.info("%s | added tx %s", time.ctime(), rx.hex())
        return encode_hex(rx)
     
    def send_ether(self, destination, amount, gas_price, nonce=None):
        target = self.ens.resolve(destination) or destination
        tx_dict = self.build_send_tx(amount, target, gas_price, nonce=nonce)
        return self.push_raw(tx_dict)


    def push(self, contract_function, gas_price, gas_limit=None, value=0, nonce=None):
        tx = contract_function.buildTransaction(self.defaultTxDict(gas_price, gas_limit=gas_limit, value=value, nonce=nonce))
        logging.info("Tx submitted to credstick: {}".format(tx))
        return self.push_raw(tx)
        

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
            chainId=int(self.network),
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
            chainId=int(self.network),
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

