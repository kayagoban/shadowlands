from shadowlands.tui.effects.transaction_frame import TransactionFrame
from shadowlands.tui.effects.message_dialog import MessageDialog
from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from decimal import Decimal
from asciimatics.exceptions import NextScene
from shadowlands.credstick import SignTxError
import pyperclip

from shadowlands.tui.debug import debug
import pdb

from shadowlands.sl_contract.erc20 import Erc20

from decimal import Decimal
import logging

from shadowlands.sl_frame import AskClipboardFrame

class SendBox(TransactionFrame):

        #debug(self._screen._screen); import pdb; pdb.set_trace()

    def __init__(self, screen, interface):
        super(SendBox, self).__init__(screen, 21, 59, interface, tx_func=self._ok, cancel_func=self._cancel, name="sendbox", title="Send Crypto")

        layout = Layout([100])#, fill_frame=True)
        self.prepend_layout(layout)
        layout.add_widget(Text("To Address:", "address"))
        layout.add_widget(Divider(draw_line=False))
        self.everything_checkbox = CheckBox("Send Everything", on_change=self.checkbox_change)
        self.amount_text = Text("    Amount:", "amount", on_change=self.amount_change)
        layout.add_widget(self.amount_text)
        layout.add_widget(self.everything_checkbox)
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

    def amount_change(self):
        if self.everything_checkbox._value == True:
            self.amount_text._value = "All of selected currency"

    def checkbox_change(self):
        if self.everything_checkbox._value == True:
            self.amount_text._value = "All of selected currency"
        else:
            self.amount_text._value = ""


    def currency_balance(self):
        return "     (bal): " + str(round(self.currency_listbox.value['balance'], 8))


    def _validations(self, address, value):
        errors = []

        if self._gas_price_wei == None:
            errors.append("No Gas Price set")

        if self.everything_checkbox._value == False:
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

        address_text = self.find_widget('address')
        amount_text = self.find_widget('amount')

        if not self._validations(address_text._value, amount_text._value):
            return

        if self.everything_checkbox._value == True:
            if self.currency_listbox.value['name'] != 'ETH':
                amount = [x['balance'] for x in self._interface.node.erc20_balances if x['name'] == self.currency_listbox.value['name'] ][0]
            else:
                #21000 gas to send eth, times gas price
                amount = (Decimal(self._interface.node._wei_balance) - (Decimal(21000) * Decimal(gas_price_wei))) / Decimal(10 ** 18)
                #debug(); pdb.set_trace()
        else:
            amount = amount_text._value


        try:
            if self.currency_listbox.value['name'] == 'ETH':
                rx = self._interface.node.send_ether(address_text._value, Decimal(amount), gas_price_wei, nonce)
            else:
                rx = self._interface.node.send_erc20(self.currency_listbox.value['name'], address_text._value, amount, gas_price_wei, nonce)

            #pyperclip.copy(rx)
            #self._scene.add_effect( MessageDialog(self._screen,"Tx submitted.", width = 20))
            #self._scene.add_effect(AskClipboardFrame, height=3, width=65, title="Tx Submitted.  Copy TxHash to clipboard?") )

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
 
