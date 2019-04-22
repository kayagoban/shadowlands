from shadowlands.tui.effects.transaction_frame import TransactionFrame
from shadowlands.tui.effects.message_dialog import MessageDialog
from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from decimal import Decimal
from asciimatics.exceptions import NextScene
from shadowlands.credstick import SignTxError
import pyperclip

from shadowlands.tui.debug import debug
import pdb

from shadowlands.contract.erc20 import Erc20

from decimal import Decimal
import logging

from shadowlands.sl_frame import AskClipboardFrame

class SendBox(TransactionFrame):

        #debug(self._screen._screen); import pdb; pdb.set_trace()

    def __init__(self, screen, interface):
        super(SendBox, self).__init__(screen, 20, 59, interface, tx_func=self._ok, cancel_func=self._cancel, name="sendbox", title="Send Crypto")

        layout = Layout([100])#, fill_frame=True)
        self.prepend_layout(layout)
        layout.add_widget(Text("To Address:", "address"))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text("    Amount:", "amount"))
        layout.add_widget(Divider(draw_line=False))

        balances = [{'name':'ETH', 'balance': interface.node.eth_balance}]
        balances += [x for x in interface.node.erc20_balances if x['balance'] > 0]

        currency_options = [(x['name'], x) for x in balances]

        logging.info(currency_options)
        logging.info(currency_options)

        self.estimated_gas = Decimal(21000)

        self.currency_listbox = ListBox(1, currency_options, label="  Currency:",  name="currency")
        layout.add_widget(self.currency_listbox)

        self.currency_balance_label = Label(self.currency_balance)
        layout.add_widget(self.currency_balance_label)

        layout.add_widget(Divider(draw_line=False))
        self.fix()

    def currency_balance(self):
        return "     (bal): " + str(round(self.currency_listbox.value['balance'], 8))


    def _validations(self, address, value):
        errors = []

        if self._gas_price_wei == None:
            errors.append("No Gas Price set")

        try:
            chaddr = self._interface.node.w3.toChecksumAddress(address)
        except:
            errors.append("Invalid send-to Address")

        try:
            amount = Decimal(value)
            if amount <= 0:
                errors.append("Zero or less than zero send amount")
            elif amount > self.currency_listbox.value['balance']:
                errors.append("Send amount more than balance")
        except:
            errors.append("Invalid send Amount")

        if len(errors) == 0:
            return True
        else:
            for i in errors:
                self._scene.add_effect( MessageDialog(self._screen, i))
            return False
 
    def _ok(self, gas_price_wei, nonce=None):
        #debug(); pdb.set_trace()

        address_text = self.find_widget('address')
        amount_text = self.find_widget('amount')

        if not self._validations(address_text._value, amount_text._value):
            return

        try:
            #rx = self._interface.node.send_ether(address_text._value, Decimal(amount_text._value), gas_price_wei)
            if self.currency_listbox.value['name'] == 'ETH':
                rx = self._interface.node.send_ether(address_text._value, Decimal(amount_text._value), gas_price_wei, nonce)
            else:
                rx = self._interface.node.send_erc20(self.currency_listbox.value['name'], address_text._value, Decimal(amount_text._value), gas_price_wei, nonce)

            #pyperclip.copy(rx)
            #self._scene.add_effect( MessageDialog(self._screen,"Tx submitted.", width = 20))
            #self._scene.add_effect(AskClipboardFrame, height=3, width=65, title="Tx Submitted.  Copy TxHash to clipboard?") )

        except SignTxError:
            self._scene.add_effect( MessageDialog(self._screen,"Credstick refused to sign Tx"))
        except ValueError as e:
            self._scene.add_effect( MessageDialog(self._screen, str(e), width = 70))


        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)

        #debug(self._screen._screen); import pdb; pdb.set_trace()
 
