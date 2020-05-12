import asyncio

from shadowlands.tui.debug import debug
import pdb
from collections import deque

import logging
import time
import threading

from shadowlands.tui.debug import debug
import pdb


class BlockListener():

    def __init__(self, node, config):
        self.config = config
        self.node = node
        self.shutdown = False

        # send fake event to clean up any malingering txs in queue
        self.handle_event(None)
        
        # on startup, examine the  txqueue and 
        # refresh it to find if any of the txs
        # have been confirmed whilst we were 
        # away.  If so, clean out the txqueue
        # appropriately.
        #self.remove_mined_txs()

    def shut_down(self):
        self.shutdown = True
        self.thread.join()


    def handle_event(self, event):
        # dedupe txqueue addresses
        addresses = set([x['from'] for x in self.config.txqueue(self.node.network)])
        if len(addresses) > 0:
            logging.info("block listener checking addresses: {}".format(addresses))
        for x in addresses:
            expired_txs = [y for y in self.config.txqueue(self.node.network) if y['from'] == x and y.nonce <= (self.node.w3.eth.getTransactionCount(x) - 1)]
            for y in expired_txs:
                self.config.txqueue_remove(self.node.network, y)
                logging.info("tx {} expired".format(y.hash.hex()))


    def listen(self):
        block_filter = self.node.w3.eth.filter('latest')
        for event in block_filter.get_new_entries():
          self.handle_event(event)


