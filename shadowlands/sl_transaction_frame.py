from shadowlands.tui.effects.widgets import MessageDialog, TransactionFrame

from shadowlands.tui.debug import debug
from shadowlands.credstick import SignTxError
import pdb

from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons, CheckBox, QRCode
)
from asciimatics.exceptions import NextScene

from shadowlands.sl_frame import AskClipboardFrame

import threading
from decimal import Decimal

class SLTransactionFrame(TransactionFrame):
    def __init__(self, dapp, x, y, tx_fn=None, tx_value=0, gas_limit=None, **kwargs):
        super(SLTransactionFrame, self).__init__(dapp._screen, x, y, dapp, self._ok_fn, self._cancel_fn, **kwargs) 
        self.dapp = dapp
        self._tx_fn = tx_fn

        if gas_limit is not None:
            self.estimated_gas = gas_limit
        else:
            try:
                self.estimated_gas = tx_fn().estimateGas()
            except ValueError:
                self.estimated_gas = 1000000

        layout = Layout([100])
        self.prepend_layout(layout)

        # TODO raise an exception if tx_value is not already a Decimal
        self.tx_value = Decimal(tx_value)
        layout.add_widget(Label("You will send {} ETH".format(self.tx_value)))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Label("Estimated Gas for Tx: {}".format(self.estimated_gas)))
        layout.add_widget(Divider(draw_line=False))
        self.fix()


    def _ok_fn(self, gas_price_wei):
        try:
            self.dapp.rx = self.dapp.node.push(
                self._tx_fn(), gas_price_wei, self.estimated_gas, value=self.dapp.node.w3.toWei(Decimal(self.tx_value), 'ether')
            )

        except (SignTxError):
            self.dapp.add_message_dialog("Credstick did not sign Transaction", destroy_window=self)
            return

        self.dapp.add_frame(AskClipboardFrame, height=3, width=65, title="Tx Submitted.  Copy TxHash to clipboard?")
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    def _cancel_fn(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)



class SLTransactionWaitFrame(SLTransactionFrame):

    def __init__(self, dapp, x, y,  wait_message, tx_fn=None, tx_value=0, gas_limit=None, receipt_proc=None, **kwargs):
        super(SLTransactionWaitFrame, self).__init__(dapp, x, y, tx_fn=tx_fn, gas_limit=gas_limit, tx_value=tx_value, **kwargs) 
 
        self.wait_message = wait_message
        self.receipt_proc = receipt_proc
 
    def _ok_fn(self, gas_price_wei):
        self.dapp.show_wait_frame(self.wait_message)

        self._transaction_thread(gas_price_wei=gas_price_wei)

        
        threading.Thread(target=self._transaction_thread, kwargs={'gas_price_wei': gas_price_wei}).start()


    def _transaction_thread(self, gas_price_wei=None):
        try:
            value = self.dapp.node.w3.toWei(Decimal(self.tx_value), 'ether')
            rxo = self.dapp.node.push_wait_for_receipt(
                self._tx_fn(), gas_price_wei, 
                self.estimated_gas, value=value
            )
            self.receipt_proc(rxo)


        except (SignTxError):
            self.dapp.add_message_dialog("Credstick did not sign Transaction", destroy_window=self)
            return

        self.dapp.hide_wait_frame()
        self.close()



