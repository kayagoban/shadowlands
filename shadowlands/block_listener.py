import asyncio

from shadowlands.tui.debug import debug
import pdb
from collections import deque

import logging
import time
import threading

from shadowlands.tui.debug import debug
import pdb

logging.basicConfig(level = logging.DEBUG, filename = "shadowlands.log")

class BlockListener():

    def __init__(self, node, config):
        self.config = config
        self.node = node

    def handle_event(self, event, w3):
        # dedupe txqueue addresses
        addresses = set([x['from'] for x in self.config.txqueue(self.node.network)])
        if len(addresses) > 0:
            logging.info("block listener checking addresses: {}".format(addresses))
        for x in addresses:
            expired_txs = [y for y in self.config.txqueue(self.node.network) if y['rx']['from'] == x and y['rx'].nonce <= (w3.eth.getTransactionCount(x) - 1)]
            for y in expired_txs:
                self.config.txq_remove(self.node.network, y)
                logging.info("tx {} expired".format(y['rx'].hash.hex()))


    def listen(self):
        w3 = self.node.w3_getter()
        logging.debug("listen()")
        block_filter = w3.eth.filter('latest')
        for event in block_filter.get_new_entries():
          self.handle_event(event, w3)

        logging.debug("end listen()")


