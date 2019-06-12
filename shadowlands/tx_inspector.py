from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.sl_contract.sloader import SLoader

from eth_utils import decode_hex
from decimal import Decimal
from shadowlands.tui.debug import debug
import pdb
import pyperclip

GWEI = Decimal(10**9)
ETH = Decimal(10**18)

class TxInspector(SLDapp):
    def __init__(self, screen, scene, eth_node, config, block_watcher, tx_index, **kwargs):
        if len(config.txqueue(eth_node.network)) < 1:
            return

        self.tx = config.txqueue(eth_node.network)[tx_index]
        super(TxInspector, self).__init__(
            screen, scene, eth_node, config, block_watcher, **kwargs
        )
 
    def initialize(self):
        self.add_sl_frame(
            TxDetail(self, 15, 71, title=self.tx.hash.hex().replace('0x',''))
        )

class TxDetail(SLFrame):
    def initialize(self):
        self.add_divider()

        top_buttons = [
           ("Copy TxHash", lambda: self.copy_to_clipboard(self.dapp.tx.hash.hex()), 2)
        ]

        if self.dapp.tx['from'] == self.dapp.node.credstick.address:
            top_buttons.append( ("Resubmit Tx", self.resend_tx, 0))
            top_buttons.append( ("Nuke Tx", self.nuke_tx, 1))
 
        self.add_button_row(top_buttons, layout=[30, 30, 40], add_divider=False)
        self.add_divider()


        try:
            nname = self.dapp.node.NETWORKDICT[self.dapp.tx['chainId']]
        except KeyError:
            nname = "Unknown"


        decimalstr = "{:f}".format(Decimal(self.dapp.tx.gasPrice) / GWEI)
        self.add_label_row([
            ("Nonce: {}".format(self.dapp.tx.nonce), 0),
            ("Gas Price: {} Gwei".format(decimalstr[:6]), 1),
            ("Network: {}".format(nname), 2)
            ],
            layout=[25, 45, 30]
        )
        formatted_value = "{:f}".format(Decimal(self.dapp.tx.value) / ETH)
        self.add_label("Value: {} ETH".format(formatted_value[:13]))

        # 'from' is a python keyword so we must access the item
        # using bracket notation
        self.add_label_with_button("From: {}".format(self.dapp.tx['from']), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx['from']), add_divider=False)
        self.add_label_with_button("To:   {}".format(self.dapp.tx.to), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx.to))
        self.add_label_with_button("Input data: {}".format(self.dapp.tx.input[:12]), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx.input))
        self.add_label_with_button("Gas Limit: {} Gwei".format(self.dapp.tx.gas), "Back", self.close, add_divider=False)

    # 0 eth tx from and to current address
    def nuke_tx(self):
        tx_dict = self.dapp.node.build_send_tx(
            0,
            self.dapp.node.credstick.address,
            None,
            nonce=self.dapp.tx.nonce
        )

        self.dapp.add_resend_dialog(
            tx_dict,
            "Overwrite nonce {} Tx with No-Op".format(self.dapp.tx.nonce)
        )
        self.close()

    def resend_tx(self):
        old_tx = self.dapp.tx

        tx_dict = dict(
            chainId = int(old_tx.chainId),
            nonce = old_tx.nonce,
            gasPrice = None,
            gas = old_tx.gas,
            to=old_tx.to,
            value=old_tx.value,
            data=old_tx.input
        )

        self.dapp.add_resend_dialog(tx_dict, "Resend Tx with different gas price")

        self.close()


