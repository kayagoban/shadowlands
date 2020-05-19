from decimal import Decimal
from web3.exceptions import BadFunctionCallOutput, ValidationError, StaleBlockchain
from requests.exceptions import ConnectionError
from websockets.exceptions import InvalidStatusCode, ConnectionClosed
from shadowlands.sl_contract import SLContract
import schedule

import pdb
from shadowlands.tui.debug import debug, end_debug
import threading

from time import sleep
import logging
import traceback

from .connection import Connect
from .transaction import Transact

   
logging.basicConfig(level = logging.DEBUG, filename = "shadowlands.log")

class NodeConnectionError(Exception):
    pass

class ENSNotSetError(Exception):
    pass
 

class Node(Connect, Transact):

    NETWORKDICT = {
        1: 'MainNet',
        2: 'Morden',
        3: 'Ropsten',
        4: 'Rinkeby',
        42: 'Kovan'
    }

    def __init__(self, sl_config=None):
        super().__init__()

        self.config = sl_config

        self._client_name = None

        self._block_listener = None
        self.eth_price = None
        self.update_sem = threading.Semaphore(value=2)
        self.update_lock = threading.Lock()

        self.start_heartbeat_thread()


from eth_utils import decode_hex, encode_hex
import time

class Transact():

    def __init__(self):
        self.credstick = None

    def push_raw(self, signed_tx):
        w3 = self.w3_getter()
        rx = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.config.txq_add(self.network, w3.eth.getTransaction(rx))
        logging.info("%s | added tx %s", time.ctime(), rx.hex())
        schedule.do(self.poll)
        return encode_hex(rx)


    def _push_next(self):
        txqe = self.config.txq_next()
        rx = self.push_raw(txqe['sx'])
        index = self.config._txqueue.index(txqe)
        txq_update(index, rx)


    def _sign_and_schedule(tx):
        logging.info("Tx submitted to credstick: {}".format(tx))
        signed_tx = self.credstick.signTx(tx)
        self.config.add_tx
        scheduler.do(self._push_next)

   
    def push(self, contract_function, gas_price, gas_limit=None, value=0, nonce=None):
        tx = contract_function.buildTransaction(self.defaultTxDict(gas_price, gas_limit=gas_limit, value=value, nonce=nonce))
        self._sign_and_schedule(tx)


    def send_ether(self, destination, amount, gas_price, nonce=None):
        target = self.ens.resolve(destination) or destination
        tx_dict = self.build_send_tx(amount, target, gas_price, nonce=nonce)
        self._sign_and_schedule(tx)

 
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


    def next_nonce(self):
      '''
      Find next nonce (according to our internally kept txqueue)
      '''
      tx_count = self.w3.eth.getTransactionCount(self.credstick.address)
      pending_txs = [x for x in self.config.txqueue(self.network) if x['from'] == self.credstick.address] 

      if len(pending_txs) > 0:
          sorted_txs = sorted(pending_txs, key=lambda x: x.nonce)
          return sorted_txs[0]['nonce'] + 1
      return tx_count 

import threading
from web3 import Web3
from ens import ENS
from shadowlands.block_listener import BlockListener
#from web3.utils.threads import Timeout
from shadowlands.sl_contract.erc20 import Erc20
import sys, os
import logging

class Connect():

    def __init__(self):
      self.w3 = None
      self._sai_pip = None

      self.thread_shutdown = False
      self.ns = None
      self.best_block = '...' 
      self.blocks_behind = None
      self.erc20_balances = None
      self.syncing_hash = None 
      self.heartbeat_thread = None
      self._ens_domain = None
      self._wei_balance = None
      self.network = None

      self.connection_type = None

    @property
    def network_name(self):
        if self.network is None:
            return None
        try:
            return self.NETWORKDICT[self.network]
        except KeyError:
            return str(self.network)

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

        for mod in ['web3', 'web3.auto', 'web3.auto.infura']:
            try:
                del(sys.modules[mod])
            except KeyError:
                pass


    def _update(self):
        w3 = self.w3_getter()
        # semaphore only allows one thread to wait on update
        self.update_sem.acquire(blocking=False)
 
        with self.update_lock:
          if self.credstick:
            self._wei_balance = w3.eth.getBalance(self.credstick.addressStr())
            self.erc20_balances = Erc20.balances(self, self.credstick.address)
            if self.network == '1':
                try:
                    self.ens = ENS.fromWeb3(_w3)
                    self._ens_domain = self.ens.name(self.credstick.addressStr())
                    self.eth_price = w3.fromWei(self._sai_pip.eth_price(), 'ether')
                except BadFunctionCallOutput:
                    self._ens_domain = 'Unknown'
            else:
                self._ens_domain = 'Unknown'

          #self.best_block = str(self.w3.eth.blockNumber)
          self.best_block = str(w3.eth.blockNumber)

          self.syncing_hash = w3.eth.syncing
          if self.syncing_hash not in (None, False):
              self.blocks_behind = self.syncing_hash['highestBlock'] - self.syncing_hash['currentBlock']
          else:
              self.blocks_behind = None

        self.update_sem.release()


    def _update_status(self):
        logging.debug("eth_node update_status")

        try:
            #threading.Thread(target=self._update).start()
            self._update()
        except (Exception) as e:
            #logging.info(str(e.__traceback__))
            logging.info("eth_node _update_status: {}".format(traceback.format_exc()))



    def is_connected_with(self, _w3, connection_type, _heart_rate, _bg_w3=None):
        if not _w3.isConnected():
            return False

        self.w3 = _w3

        self.network = self.w3.eth.chainId

        if self.network == 1 and self._sai_pip is None:
            self._sai_pip = SaiPip(self)

        self._heart_rate = _heart_rate
        self._connection_type = connection_type


        if self.network == 4:
            from web3.middleware import geth_poa_middleware
            self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)

        try:
            self._update_status()
        except (StaleBlockchain):
            return False

        logging.debug("is connected with " + connection_type + " every " + str(_heart_rate) + " seconds.")

        return True



    def connect_w3_local(self):
        self.cleanout_w3()
        from web3.auto import w3
        if self.is_connected_with(w3, 'Local node', 3):
            self.config.default_method = self.connect_w3_local.__name__
            return True
        return False


    def connect_w3_websocket(self, uri=None, kwargs={}):
        self.cleanout_w3()
        from web3 import Web3
        return Web3(Web3.WebsocketProvider(uri, websocket_kwargs=kwargs))

    def connect_w3_custom_infura(self):
        args = self.config.connection_args
        proj_id = args[0]  
        proj_secret = args[1]
        uri = f"wss://:{proj_secret}@ropsten.infura.io/ws/v3/{proj_id}"
        return self.w3_websocket(uri)

        # if no connection, wipe the config
        if self.is_connected_with(w3, 'Custom infura', 18):
            self.config.connection_strategy = None
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

    def w3_getter(self):
      return self.bg_w3

    def poll(self):
      # (ConnectionError, AttributeError, Timeout, InvalidStatusCode, ConnectionClosed, TimeoutError, OSError, StaleBlockchain, ValueError)
      logging.debug("eth_node poll()")
      w3 = self.w3_getter()
      self._update_status()
      logging.debug("eth_node poll() finished")


    def heartbeat(self):
      block_listener = BlockListener(self, self.config)
      schedule.every(15).to(20).seconds.do(self.poll)
      schedule.every(15).to(20).seconds.do(block_listener.listen)
      while True:
        if not self.ensure_w3():
          sleep(.3)
          continue
        schedule.run_pending()
        if self.thread_shutdown:
          logging.debug("eth_node thread_shutdown")
          return
        sleep(.3)

    def ensure_w3(self):
        try:
            if self.bg_w3().isConnected():
              return True
            fn = self.__getattribute__(self.config.connection_strategy)
        except (AttributeError, TypeError):
            logging.debug("eth_node thread_shutdown")
        return fn()

      
    def start_heartbeat_thread(self):
      logging.debug("eth_node start_heartbeat_thread()")
      self.heartbeat_thread = threading.Thread(target=self.heartbeat)
      self.heartbeat_thread.start()


    def stop_thread(self):
        logging.debug("eth_node stop_thread()")

        if self.heartbeat_thread is not None:
            self.thread_shutdown = True
            self.heartbeat_thread.join()




