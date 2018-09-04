from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from tui.errors import ExitTuiError
from tui.debug import debug
from decimal import Decimal


# Make sure the widget frame is_modal or claimed_focus.
# otherwise the text is not swallowed and our menus are buggered.
# "return None if claimed_focus or self._is_modal else old_event" - widgets.py:882


#debug(self._screen._screen); import pdb; pdb.set_trace()




class GasPricePicker(RadioButtons):
    def __init__(self, on_change=None, interface=None, **kwargs):
        """
        :param options: A list of (text, value) tuples for each radio button.
        :param label: An optional label for the widget.
        :param name: The internal name for the widget.
        :param on_change: Optional function to call when text changes.

        Also see the common keyword arguments in :py:obj:`.Widget`.
        """
        self._interface = interface

        gas_price_wei = self._interface.node.w3.eth.gasPrice
        gas_price_minus_20_percent = gas_price_wei - gas_price_wei * Decimal(.2)
        gas_price_gwei = self._interface.node.w3.fromWei(gas_price_wei, 'gwei')
        gas_price_gwei_m20 = self._interface.node.w3.fromWei(gas_price_minus_20_percent, 'gwei')

        _options = [
                (str(gas_price_gwei) + ' gwei  |from w3.gasPrice()' , gas_price_wei), 
                (str(round(gas_price_gwei_m20, 3)) + ' gwei (-20%)', gas_price_minus_20_percent), 
                ('Enter custom gas price', 3)
        ]

        super(GasPricePicker, self).__init__(_options, on_change=on_change, label=' Gas Price:', name='gasoptions', **kwargs)
   


# This has everything you need for a base transaction widget collection
# most importantly, all the hoopla that takes care of gas prices
class TransactionFrame(Frame):
   
    def __init__(self, screen, x, y, interface, ok_func=None, cancel_func=None, **kwargs):
        super(TransactionFrame, self).__init__(screen, x, y, can_scroll=False, has_shadow=True, is_modal=True, **kwargs)
        self.set_theme('shadowlands')
        self._interface = interface
        self._screen = screen
        self.gas_cost = None

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        layout.add_widget(GasPricePicker(on_change=self._on_option_change, interface=interface))
        custgas = Text("CustGas:", "custgas", on_change=self._on_text_change)
        custgas._is_disabled = True
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(custgas)
        layout.add_widget(Divider(draw_line=False))

        layout.add_widget(Label("", name='gas_est_label'))
        layout.add_widget(Divider(draw_line=False))

        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Sign Tx", ok_func), 0)
        layout2.add_widget(Button("Cancel", cancel_func), 3)

    def _on_text_change(self):
        custgas = self.find_widget('custgas')
        gastimate_label = self.find_widget('gas_est_label')
        try:
            gas_price_wei = self._interface.node.w3.toWei(Decimal(custgas._value), 'gwei')
            gastimate_label._text = self._cost_estimate_string(gas_price_wei)
        except:
            gastimate_label._text = "" 


    # called when the gas price radiobutton changes.
    def _on_option_change(self):
        gasoptions = self.find_widget('gasoptions')
        custgas = self.find_widget('custgas')
        gastimate_label = self.find_widget('gas_est_label')

        if gasoptions._value == 3:
            custgas._is_disabled = False
            try:
                gas_price_wei = self._interface.node.w3.toWei(Decimal(custgas._value), 'gwei')
                gastimate_label._text = self._cost_estimate_string(gas_price_wei)
            except:
                gastimate_label._text = ''
        else:
            custgas._is_disabled = True
            gastimate_label._text = self._cost_estimate_string(gasoptions._value)

 
    def _cost_estimate_string(self, gas_price_wei):
        # normal eth transaction costs 21000.
        estimated_gas = Decimal(21000)
        wei_gas_cost = gas_price_wei * estimated_gas

        try:
            #debug(self._screen._screen); import pdb; pdb.set_trace()
            eth_price_usd = self._interface.prices()['ETH']['USD']
            gas_price_eth = self._interface.node.w3.fromWei(gas_price_wei, 'ether')
            cost_estimate = str(round((Decimal(eth_price_usd) * gas_price_eth * estimated_gas), 3))
        except:
            cost_estimate = 'Error estimating cost'
        return "Estimated Tx cost: USD $" + cost_estimate







class SendBox(TransactionFrame):

        #debug(self._screen._screen); import pdb; pdb.set_trace()

    def __init__(self, screen, interface):
        super(SendBox, self).__init__(screen, 17, 59, interface, ok_func=self._ok, cancel_func=self._cancel, name="sendbox", title="Send Crypto")

        layout = Layout([100])#, fill_frame=True)
        #self.add_layout(layout)
        self.prepend_layout(layout)
        layout.add_widget(Text("To Address:", "address"))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text("    Amount:", "amount"))
        layout.add_widget(Divider(draw_line=False))
        #currency_options = [("ETH", 0), ("WETH", 1), ("DAI", 2)]
        currency_options = [("ETH", 0)]
        layout.add_widget(ListBox(1, currency_options, label="  Currency:",  name="currency"))
        layout.add_widget(Divider(draw_line=False))

        self.fix()

 
    def _ok(self):
        debug(self._screen._screen); import pdb; pdb.set_trace()
        self._scene.remove_effect(self)
        raise NextScene("Main")

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene("Main")






class QuitDialog(Frame):
    def __init__(self, screen):
        super(QuitDialog, self).__init__(screen, 3, 30, has_shadow=True, is_modal=True, name="quitbox", title="Really quit?", can_scroll=False)
        self.set_theme('shadowlands')

        layout2 = Layout([1, 1], fill_frame=True)
        self.add_layout(layout2)

        layout2.add_widget(Button("Yes", self._ok), 1)
        layout2.add_widget(Button("No", self._cancel), 0)
        self.fix()

    def _ok(self):
        raise ExitTuiError 

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene("Main")

    def process_event(self, event):

        if type(event) != KeyboardEvent:
            return event

        if event.key_code in [121, 89]:
            self._ok() 
        elif event.key_code in [110, 78]:
            self._cancel()

        super(QuitDialog, self).process_event(event)
 


