from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.contract.sloader import SLoader

from eth_utils import decode_hex
from shadowlands.tui.debug import debug
from decimal import Decimal
import pdb

GWEI = Decimal(10**9)
ETH = Decimal(10**18)

class TxInspector(SLDapp):
    def __init__(self, screen, scene, eth_node, config, price_poller, tx_index, **kwargs):
        self.tx = config.txqueue(eth_node.network)[tx_index]
        super(TxInspector, self).__init__(
            screen, scene, eth_node, config, price_poller, **kwargs
        )
 
    def initialize(self):
        self.add_frame(TxDetail, height=21, width=71, title='Pending Tx Detail')

class TxDetail(SLFrame):
    def initialize(self):
        #self.add_label("Tx Hash:", add_divider=False)
        self.add_label(self.dapp.tx.hash.hex(), add_divider=False)
        self.add_divider(draw_line=True)
        self.add_label("Network: {}".format(self.dapp.node.NETWORKDICT[self.dapp.tx['chainId']]))
        self.add_label("From: {}".format(self.dapp.tx['from']))
        self.add_label("To: {}".format(self.dapp.tx.to))
        self.add_label("Nonce: {}".format(self.dapp.tx.nonce))
        self.add_label("Value: {} ETH".format(
            Decimal(self.dapp.tx.value) / ETH))
        self.add_label("Gas Price: {} Gwei".format(Decimal(self.dapp.tx.gasPrice) / GWEI ))
        self.add_label("Gas Limit: {} Gwei".format(self.dapp.tx.gas))
        #debug(); pdb.set_trace()
        #self.checksum = self.add_textbox("SHA256:")
        self.add_divider(draw_line=True)
        self.add_button_row([
            ("Nuke Tx", self.close, 0),
            ("Resend Tx", self.close, 1),
            ("Close", self.close, 3)
        ])
