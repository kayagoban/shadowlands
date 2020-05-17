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

