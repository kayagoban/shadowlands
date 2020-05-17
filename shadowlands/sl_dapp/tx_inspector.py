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
            TxDetail(self, 15, 71, title=self.tx['rx'].hash.hex().replace('0x',''))
        )

class TxDetail(SLFrame):
    def initialize(self):
        self.add_divider()

        top_buttons = [
           ("Copy TxHash", lambda: self.copy_to_clipboard(self.dapp.tx['rx'].hash.hex()), 2)
        ]

        if self.dapp.tx['rx']['from'] == self.dapp.node.credstick.address:
            top_buttons.append( ("Resubmit Tx", self.resend_tx, 0))
            top_buttons.append( ("Nuke Tx", self.nuke_tx, 1))
 
        self.add_button_row(top_buttons, layout=[30, 30, 40], add_divider=False)
        self.add_divider()


        try:
            nname = self.dapp.node.NETWORKDICT[self.dapp.tx['chain_id']]
        except KeyError:
            nname = "Unknown"


        decimalstr = "{:f}".format(Decimal(self.dapp.tx['rx'].gasPrice) / GWEI)
        self.add_label_row([
            ("Nonce: {}".format(self.dapp.tx['rx'].nonce), 0),
            ("Gas Price: {} Gwei".format(decimalstr[:6]), 1),
            ("Network: {}".format(nname), 2)
            ],
            layout=[25, 45, 30]
        )
        formatted_value = "{:f}".format(Decimal(self.dapp.tx['rx'].value) / ETH)
        self.add_label("Value: {} ETH".format(formatted_value[:13]))

        # 'from' is a python keyword so we must access the item
        # using bracket notation
        self.add_label_with_button("From: {}".format(self.dapp.tx['rx']['from']), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx['rx']['from']), add_divider=False)
        self.add_label_with_button("To:   {}".format(self.dapp.tx['rx'].to), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx['rx'].to))
        self.add_label_with_button("Input data: {}".format(self.dapp.tx['rx'].input[:12]), "Copy", lambda: self.copy_to_clipboard(self.dapp.tx['rx'].input))
        self.add_label_with_button("Gas Limit: {} Gwei".format(self.dapp.tx['rx'].gas), "Back", self.close, add_divider=False)

    # 0 eth tx from and to current address
    def nuke_tx(self):
        tx_dict = self.dapp.node.build_send_tx(
            0,
            self.dapp.node.credstick.address,
            None,
            nonce=self.dapp.tx['rx'].nonce
        )

        self.dapp.add_resend_dialog(
            tx_dict,
            "Overwrite nonce {} Tx with No-Op".format(self.dapp.tx.nonce)
        )
        self.close()

    def resend_tx(self):
        old_tx = self.dapp.tx

        tx_dict = dict(
            chainId = int(old_tx['chain_id']),
            nonce = old_tx['rx'].nonce,
            gasPrice = None,
            gas = old_tx['rx'].gas,
            to=old_tx['rx'].to,
            value=old_tx['rx'].value,
            data=old_tx['rx'].input
        )

        self.dapp.add_resend_dialog(tx_dict, "Resend Tx with different gas price")
        self.close()


