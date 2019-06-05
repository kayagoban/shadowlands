from shadowlands.tui.effects.message_dialog import MessageDialog
from shadowlands.tui.effects.transaction_frame import TransactionFrame

from shadowlands.tui.debug import debug
from shadowlands.credstick import SignTxError
import pdb

from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons, CheckBox, QRCode
)
from asciimatics.exceptions import NextScene

from shadowlands.sl_frame import AskClipboardFrame, SLFrame

import threading
from decimal import Decimal
import logging

class SLTransactionFrame(TransactionFrame):
    def __init__(self, dapp, x, y, tx_fn=None, tx_value=0, gas_limit=300000,  **kwargs):
        super(SLTransactionFrame, self).__init__(dapp._screen, x, y, dapp, self._ok_fn, self.close, **kwargs) 
        self.dapp = dapp
        self._tx_fn = tx_fn
        self.estimated_gas = gas_limit

        layout = Layout([100])
        self.prepend_layout(layout)

        # TODO raise an exception if tx_value is not already a Decimal
        self.tx_value = Decimal(tx_value)
        layout.add_widget(Label("You will send {} ETH".format(self.tx_value)))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Label("Estimated Gas for Tx: {}".format(self.estimated_gas)))
        layout.add_widget(Divider(draw_line=False))
        self.fix()

     

    def _ok_fn(self, gas_price_wei, nonce=None):
        try:
            self.dapp.rx = self.dapp.node.push(
                self._tx_fn, 
                gas_price_wei, 
                self.estimated_gas, 
                value=self.dapp.node.w3.toWei(Decimal(self.tx_value), 'ether'),
                nonce=nonce
            )
        except ValueError as e:
            logging.info("Error creating tx: {}".format(e))
            self.dapp.add_message_dialog("{}".format(e.args[0]['message']), destroy_window=self)
            return
        except (SignTxError) as e:
            logging.info("SignTxError: {}".format(e))
            self.dapp.add_message_dialog("Credstick did not sign Transaction", destroy_window=self)
            return
        except (OSError):
            self.dapp.add_message_dialog("Your credstick generated an error.", destroy_window=self)
            return

        #self.dapp.add_sl_frame(AskClipboardFrame(self.dapp, 3, 65, title="Tx Submitted.  Copy TxHash to clipboard?"))
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    def close(self):
        # deregister from new_block callbacks
        self.dapp.remove_block_listener(self)
        self._destroy_window_stack()
        raise NextScene(self._scene.name)
        
    # duck typed to SLFrame
    def _new_block_callback(self):
        pass

