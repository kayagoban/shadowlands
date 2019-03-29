from shadowlands.tui.effects.transaction_frame import TransactionFrame
from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from decimal import Decimal
from asciimatics.exceptions import NextScene

import pdb

class SendBox(TransactionFrame):

        #debug(self._screen._screen); import pdb; pdb.set_trace()

    def __init__(self, screen, interface):
        super(SendBox, self).__init__(screen, 17, 59, interface, ok_func=self._ok, cancel_func=self._cancel, name="sendbox", title="Send Crypto")

        layout = Layout([100])#, fill_frame=True)
        self.prepend_layout(layout)
        layout.add_widget(Text("To Address:", "address"))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text("    Amount:", "amount"))
        layout.add_widget(Divider(draw_line=False))

        #currency_options = [("ETH", 0), ("WETH", 1), ("DAI", 2)]
        currency_options = [("ETH", 0)]

        self.estimated_gas = Decimal(21000)

        layout.add_widget(ListBox(1, currency_options, label="  Currency:",  name="currency"))
        layout.add_widget(Divider(draw_line=False))
        self.fix()

    def _validations(self, address, value):
        errors = []

        if self._gas_price_wei == None:
            errors.append("No Gas Price set")

        try:
            chaddr = self._interface.node.w3.toChecksumAddress(address)
        except:
            errors.append("Invalid send-to Address")

        try:
            Decimal(value)
        except:
            errors.append("Invalid send Amount")

        if len(errors) == 0:
            return True
        else:
            for i in errors:
                self._scene.add_effect( MessageDialog(self._screen, i))
            return False
 
    #debug(); import pdb; pdb.set_trace()
    def _ok(self, gas_price_wei):

        address_text = self.find_widget('address')
        amount_text = self.find_widget('amount')

        #debug(self._screen._screen); import pdb; pdb.set_trace()
        if not self._validations(address_text._value, amount_text._value):
            return

        try:
            rx = self._interface.node.send_ether(address_text._value, Decimal(amount_text._value), gas_price_wei)
            pyperclip.copy(rx)
            self._scene.add_effect( MessageDialog(self._screen,"Tx submitted.  TxHash copied to clipboard.", width = 45))
        except SignTxError:
            self._scene.add_effect( MessageDialog(self._screen,"Credstick refused to sign Tx"))
        except ValueError as e:
            self._scene.add_effect( MessageDialog(self._screen, str(e), width = 70))

        self._scene.remove_effect(self)
        raise NextScene

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene

        #debug(self._screen._screen); import pdb; pdb.set_trace()
 
