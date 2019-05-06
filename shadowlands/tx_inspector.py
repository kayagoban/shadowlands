from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.contract.sloader import SLoader

from eth_utils import decode_hex
from decimal import Decimal
from shadowlands.tui.debug import debug
import pdb
import pyperclip

GWEI = Decimal(10**9)
ETH = Decimal(10**18)

class TxInspector(SLDapp):
    def __init__(self, screen, scene, eth_node, config, tx_index, **kwargs):
        if len(config.txqueue(eth_node.network)) < 1:
            return

        self.tx = config.txqueue(eth_node.network)[tx_index]
        super(TxInspector, self).__init__(
            screen, scene, eth_node, config, **kwargs
        )
 
    def initialize(self):
        self.add_frame(TxDetail, height=22, width=71, title='Pending Tx Detail')

class TxDetail(SLFrame):
    def initialize(self):
        self.add_label(self.dapp.tx.hash.hex(), add_divider=False)
        self.add_button(lambda: self.copy_to_clipboard(self.dapp.tx.hash.hex()), "Copy TxHash", layout_distribution=[70, 30], layout_index=1)
        #self.add_divider(draw_line=True)
        self.add_label("Network: {}".format(self.dapp.node.NETWORKDICT[self.dapp.tx['chainId']]))
        # 'from' is a python keyword so we must access the item
        # using bracket notation
        self.add_label_with_button("From: {}".format(self.dapp.tx['from']), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx['from']))
        self.add_label_with_button("To: {}".format(self.dapp.tx.to), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx.to))
        self.add_label("Nonce: {}".format(self.dapp.tx.nonce))
        self.add_label("Value: {} ETH".format(
            Decimal(self.dapp.tx.value) / ETH))
        self.add_label_with_button("Input data: {}".format(self.dapp.tx.input), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx.input))
        self.add_label("Gas Price: {} Gwei".format(Decimal(self.dapp.tx.gasPrice) / GWEI ))
        self.add_label("Gas Limit: {} Gwei".format(self.dapp.tx.gas), add_divider=False)
        #debug(); pdb.set_trace()
        #self.checksum = self.add_textbox("SHA256:")
        self.add_divider()
        self.add_divider()
        #self.add_divider(draw_line=True)
        self.add_button_row([
            ("Resubmit Tx", self.resend_tx, 0),
            ("Nuke Tx", self.nuke_tx, 1),
            ("Back", self.close, 3)
        ],
        layout=[25, 25, 35, 18])

    # 0 eth tx from and to current address
    def nuke_tx(self):
        #debug(); pdb.set_trace()
        tx_dict = self.dapp.node.build_send_tx(
            0,
            self.dapp.node.credstick.address,
            None,
            nonce=self.dapp.tx.nonce
        )

        self.dapp.add_send_dialog(
            tx_dict,
            "Overwrite nonce {} Tx with No-Op".format(self.dapp.tx.nonce)
        )
        self.close()

    def resend_tx(self):
        old_tx = self.dapp.tx

        #debug(); pdb.set_trace()

        tx_dict = dict(
            #chainId = old_tx.chainId,
            nonce = old_tx.nonce,
            gasPrice = None,
            gas = old_tx.gas,
            to=old_tx.to,
            value=old_tx.value,
            data=old_tx.input
        )

        self.dapp.add_send_dialog(tx_dict, "Resend Tx with different gas price")

        self.close()


