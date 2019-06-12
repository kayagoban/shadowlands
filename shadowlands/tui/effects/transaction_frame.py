from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from shadowlands.tui.effects.gas_price_picker import GasPricePicker
from decimal import Decimal, InvalidOperation

# This has everything you need for a base transaction widget collection
# most importantly, all the hoopla that takes care of gas prices
class TransactionFrame(Frame):
   
    def __init__(self, screen, x, y, interface, tx_func=None, cancel_func=None, **kwargs):
        super(TransactionFrame, self).__init__(screen, x, y, can_scroll=False, has_shadow=True, is_modal=True, **kwargs)
        self.set_theme('shadowlands')
        self._interface = interface
        self._screen = screen
        self._gas_price_wei = None
        self._tx_func = tx_func

        # subclass sets this to Decimal(something)
        self.estimated_gas = None

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        self.nonce_text = Text("     Nonce:", "nonce", default_value=str(self._interface.node.next_nonce()))
        layout.add_widget(self.nonce_text)
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(GasPricePicker(on_change=self._on_option_change, interface=interface))
        custgas = Text("   CustGas:", "custgas", on_change=self._on_text_change)
        custgas._is_disabled = True
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(custgas)
        layout.add_widget(Divider(draw_line=False))

        layout.add_widget(Label("", name='gas_est_label'))
        layout.add_widget(Divider(draw_line=False))

        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Sign Tx", self.validate), 0)
        layout2.add_widget(Button("Cancel", cancel_func), 3)

        self._on_option_change()

    def validate(self):
        self._tx_func(self._gas_price_wei, int(self.nonce_text._value))

    def fix(self):
        # manually call the radiobutton callback
        # to set the gas estimate label
        if not self.estimated_gas:
            raise Exception("Must set self.estimated_gas before calling fix()")
        self._on_option_change()
        super(TransactionFrame, self).fix()
    

    # called when custom gas Text value changes
    def _on_text_change(self):
        gas_price_gwei = None
        custgas = self.find_widget('custgas')
        try:
            gas_price_gwei = Decimal(custgas._value)
        except InvalidOperation:
            # Let it blow up later down the line
            gas_price_gwei = custgas._value
            

        self._update_gastimate_label(gas_price_gwei)


    # called when the gas price radiobutton changes.
    def _on_option_change(self):
        gasoptions = self.find_widget('gasoptions')
        custgas = self.find_widget('custgas')
        if gasoptions._value == '0':
            custgas._is_disabled = False
            self._gas_price_wei = None
            self._update_gastimate_label(custgas._value)
        else:
            custgas._is_disabled = True
            self._update_gastimate_label(gasoptions._value)


    def _update_gastimate_label(self, gas_price_gwei):
        gastimate_label = self.find_widget('gas_est_label')
 
        #if not gas_price_gwei or gas_price_gwei == ''
        #    gastimate_label._text = "" 
        #elif gas_price_gwei == ''
        #    gastimate_label._text = "" 
        #    return

        try:
            self._gas_price_wei = self._interface.node.w3.toWei(gas_price_gwei, 'gwei')
            gastimate_label._text = self._cost_estimate_string(self._gas_price_wei)
        except:
            self._gas_price_wei = None
            gastimate_label._text = "" 

 
    def _cost_estimate_string(self, gas_price_wei):

        eth_price_curr = self._interface.node.eth_price
        if eth_price_curr == None:
            return 'Ether Price Feed offline - No Tx Cost estimate'

        gas_price_eth = self._interface.node.w3.fromWei(gas_price_wei, 'ether')

        decimal_places = 3

        cost_estimate = str(eth_price_curr * gas_price_eth * self.estimated_gas)[0:8]
        return "Estimated Tx cost: USD {}".format(cost_estimate)


