import asyncio

from shadowlands.tui.debug import debug
import pdb
from collections import deque

import logging
import time
logging.basicConfig(level = logging.INFO, filename = "shadowlands.eth_node.log")

from shadowlands.tui.debug import debug
import pdb


class BlockListener():

    def __init__(self, node, config):
        self.config = config
        self.node = node
        self.shutdown = False

        # on startup, examine the  txqueue and 
        # refresh it to find if any of the txs
        # have been confirmed whilst we were 
        # away.  If so, clean out the txqueue
        # appropriately.
        self.remove_mined_txs()


    def remove_mined_txs(self):
        mined_txs = []

        for tx in self.config.txqueue(self.node.network):
            fresh_tx = self.node.w3.eth.getTransaction(tx.hash)

            if fresh_tx is None:
                continue
            elif fresh_tx.blockNumber is not None:
                mined_txs.append(tx)

        for tx in mined_txs:
            self.config.txqueue_remove(self.node.network, tx)
            logging.info("removing tx")

    ''' 
    This method cleans the txqueue of txs which have been confirmed or which are no longer possible to confirm.
    new_txs is a list of tx hashes which have been mined.
    '''
    def clean_txqueue(self, new_txs):
        intersection = [x for x in self.config.txqueue(self.node.network) if x.hash in new_txs] 

        for match in intersection:
            nonce = match.nonce
            address = match["from"]

            # grabs all txs in txqueue with same 'from address' as 
            # mined txs, and the same nonce or lower.
            smaller_nonces = [
                x for x 
                in self.config.txqueue(self.node.network)
                if x['from'] == address
                and x.nonce <= nonce
            ] 

            for x in smaller_nonces:
                self.config.txqueue_remove(self.node.network, x)
                logging.info("removing tx")

    def handle_event(self, event):
        be = self.node.w3.eth.getBlock(event)
        txs = be['transactions']
        self.clean_txqueue(txs)


    async def asyncio_log_loop(self, event_filter, poll_interval):
        while True:
            logging.info("log_loop")
            for event in event_filter.get_new_entries():
                self.handle_event(event)
            await asyncio.sleep(poll_interval)


    def listen(self, poll_interval):
        block_filter = self.node.w3.eth.filter('latest')

        try:
            while True:
                logging.info("%s | block_listener get_new_entries ", time.ctime())
                for i in range(poll_interval):
                    if self.shutdown == True:
                        return
                    time.sleep(1)
                for event in block_filter.get_new_entries():
                    self.handle_event(event)
        except Exception as e:
            logging.debug(e)
