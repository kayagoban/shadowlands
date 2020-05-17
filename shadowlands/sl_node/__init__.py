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


