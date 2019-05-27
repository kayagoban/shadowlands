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
        
        self.thread = threading.Thread(target=self.listen, args=([6]))
        #self.listen(6)
        self.thread.start()

 
        # on startup, examine the  txqueue and 
        # refresh it to find if any of the txs
        # have been confirmed whilst we were 
        # away.  If so, clean out the txqueue
        # appropriately.
        #self.remove_mined_txs()

    def shut_down(self):
        self.shutdown = True
        self.thread.join()

    def remove_mined_txs(self):
        mined_txs = []

        for tx in self.config.txqueue(self.node.network):
            fresh_tx = self.node.w3.eth.getTransaction(tx.hash)

            if fresh_tx is None:
                mined_txs.append(tx)
            elif fresh_tx.blockNumber is not None:
                mined_txs.append(tx)

        for tx in mined_txs:
            self.config.txqueue_remove(self.node.network, tx)
            logging.info("removing tx {}({})".format(tx.nonce, tx.hash.hex()))

    ''' 
    This method cleans the txqueue of txs which have been confirmed or which are no longer possible to confirm.
    new_txs is a list of tx hashes which have been mined.
    '''
    def clean_txqueue(self, new_txs):
        logging.info("block_listener clean_txqueue ({})".format(time.ctime()), poll_interval)
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
        txs = [ self.node.w3.eth.getTransaction(x.hash) for x in self.config.txqueue(self.node.network)]
        logging.debug("examining txs for potential removal: {}".format(txs))
        for tx in txs:
            if tx.blockNumber is not None:
                # remove tx and any txs for this address with lesser nonces.
                smaller_nonces = [
                    x for x 
                    in self.config.txqueue(self.node.network)
                    if x['from'] == tx['from']
                    and x.nonce <= tx.nonce
                ] 

                for y in smaller_nonces:
                    self.config.txqueue_remove(self.node.network, y)
                    logging.info("{} mined in block {}".format(y.hash.hex(), y.blockNumber))


    def listen(self, poll_interval):
        block_filter = self.node.w3.eth.filter('latest')
        try:
            while True:
                for i in range(poll_interval):
                    if self.shutdown == True:
                        return
                    time.sleep(1)
                for event in block_filter.get_new_entries():
                    self.handle_event(event)
        except (Exception) as e:
            logging.debug("Error in block_listener: {}".format(e))


