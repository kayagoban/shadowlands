import asyncio

from shadowlands.tui.debug import debug
import pdb
from collections import deque

import logging
import time
logging.basicConfig(level = logging.INFO, filename = "shadowlands.eth_node.log")


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
        #pdb.set_trace()

        self.remove_mined_txs()

        #pdb.set_trace()
        #logging.info("new event loop")
        #loop = asyncio.new_event_loop()
        #loop = asyncio.get_event_loop()
        #asyncio.set_event_loop(loop)
        
        #try:
        #    loop.run_until_complete(
        #        asyncio.gather(
        #            self.log_loop(block_filter, 12)
        #        ))
        #except Exception as e:
        #    pdb.set_trace()
        #    print(e)
        #
        #finally:
        #    loop.close()


    def remove_mined_txs(self):
        mined_txs = []
        #pdb.set_trace()

        #rgging.info("removing tx")
        for tx in self.config.txqueue:
            fresh_tx = self.node.w3.eth.getTransaction(tx.hash)

            if fresh_tx is None:
                continue
            elif fresh_tx.blockNumber is not None:
                mined_txs.append(tx)
                #for tx in self.config.txqueue:
                #    if tx.hash == fresh_tx.hash:
                #        self.config.txqueue_remove(tx) 
                #self.config.txqueue.remove(tx)

        for tx in mined_txs:
            self.config.txqueue_remove(tx)
            logging.info("removing tx")

        #pdb.set_trace()
        #fresh_tx.block
                
        #config.clean_txqueue(
        #    [x.hash for x in config.txqueue ]
        #)


    ''' 
    This method cleans the txqueue of txs which have been confirmed or which are no longer possible to confirm.
    new_txs is a list of tx hashes which have been mined.
    '''
    def clean_txqueue(self, new_txs):
        intersection = [x for x in self.config.txqueue if x.hash in new_txs] 

        for match in intersection:
            nonce = match.nonce
            address = match["from"]

            # grabs all txs in txqueue with same 'from address' as mined tx, and the same nonce or lower.
            #pdb.set_trace()
            smaller_nonces = [
                x for x 
                in self.config.txqueue 
                if x['from'] == address
                and x.nonce <= nonce
            ] 

            for x in smaller_nonces:
                self.config.txqueue_remove(x)
                logging.info("removing tx")

    def handle_event(self, event):
        #pdb.set_trace()
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
