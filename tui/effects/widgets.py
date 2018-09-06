from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from tui.errors import ExitTuiError
from decimal import Decimal
from credstick import SignTxError
from binascii import Error

from tui.debug import debug
import pdb

# Make sure the widget frame is_modal or claimed_focus.
# otherwise the text is not swallowed and our menus are buggered.
# "return None if claimed_focus or self._is_modal else old_event" - widgets.py:882


#debug(self._screen._screen); import pdb; pdb.set_trace()


#debug(); pdb.set_trace()


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
                (str(gas_price_gwei) + ' gwei  |from w3.gasPrice()' , gas_price_gwei), 
                (str(round(gas_price_gwei_m20, 3)) + ' gwei (-20%)', gas_price_gwei_m20), 
                ('Enter custom gas price', 3)
        ]

        super(GasPricePicker, self).__init__(_options, on_change=on_change, label=' Gas Price:', name='gasoptions', **kwargs)

        # preset the value to the first option value
        #self._value = self._options[0][1]
   


# This has everything you need for a base transaction widget collection
# most importantly, all the hoopla that takes care of gas prices
class TransactionFrame(Frame):
   
    def __init__(self, screen, x, y, interface, ok_func=None, cancel_func=None, **kwargs):
        super(TransactionFrame, self).__init__(screen, x, y, can_scroll=False, has_shadow=True, is_modal=True, **kwargs)
        self.set_theme('shadowlands')
        self._interface = interface
        self._screen = screen
        self._gas_price_wei = None

        # subclass sets this to Decimal(something)
        self.estimated_gas = None

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

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
        layout2.add_widget(Button("Sign Tx", ok_func), 0)
        layout2.add_widget(Button("Cancel", cancel_func), 3)

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
        except:
            pass
            #debug(self._screen._screen); import pdb; pdb.set_trace()

        self._update_gastimate_label(gas_price_gwei)


    # called when the gas price radiobutton changes.
    def _on_option_change(self):
        gasoptions = self.find_widget('gasoptions')
        custgas = self.find_widget('custgas')
        if gasoptions._value == 3:
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
            #debug(self._screen._screen); import pdb; pdb.set_trace()
            self._gas_price_wei = None
            gastimate_label._text = "" 

 
    def _cost_estimate_string(self, gas_price_wei):

        try:
            eth_price_usd = self._interface.prices()['ETH']['USD']
        except Exception:
            return 'Ether Price Feed offline - No Tx Cost estimate'
        gas_price_eth = self._interface.node.w3.fromWei(gas_price_wei, 'ether')
        cost_estimate = str(round((Decimal(eth_price_usd) * gas_price_eth * self.estimated_gas), 3))
            #debug(self._screen._screen); import pdb; pdb.set_trace()
#            debug(self._screen._screen); import pdb; pdb.set_trace()
        return "Estimated Tx cost: USD $" + cost_estimate




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
            chaddr =  self._interface.node.w3.toChecksumAddress(address)
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
 
    def _ok(self):

        address_text = self.find_widget('address')
        amount_text = self.find_widget('amount')

        #debug(self._screen._screen); import pdb; pdb.set_trace()
        if not self._validations(address_text._value, amount_text._value):
            return

        try:
            self._interface._dapp.send_ether(address_text._value, Decimal(amount_text._value), self._gas_price_wei)
        except SignTxError:
            self._scene.add_effect( MessageDialog(self._screen,"Credstick refused to sign Tx"))
            return

        #debug(self._screen._screen); import pdb; pdb.set_trace()
        self._scene.remove_effect(self)
        raise NextScene("Main")

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene("Main")


class MessageDialog(Frame):
    def __init__(self, screen, message, height=3, width=30, **kwargs):
        super(MessageDialog, self).__init__(screen, height, width, has_shadow=True, is_modal=True, name="message", title=message, can_scroll=False, **kwargs)
        self.set_theme('shadowlands')

        layout2 = Layout([100], fill_frame=True)
        self.add_layout(layout2)

        layout2.add_widget(Divider(draw_line=False))
        layout2.add_widget(Button("Ok", self._cancel), 0)
        self.fix()

    def _cancel(self):
        self._destroy_window_stack()
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
 

 
class NetworkOptions(Frame):
    def __init__(self, screen, interface):
        super(NetworkOptions, self).__init__(screen, 13, 34, y=2, has_shadow=True, is_modal=True, name="networkopts", title="Network Options", can_scroll=False)
        self.set_theme('shadowlands')
        self._interface = interface

        #debug(); pdb.set_trace()
    
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=False))

        self._node = self._interface.node

        options = [
            ('Local node', self._node.connect_w3_local), 
            ('Public infura', self._node.connect_w3_public_infura),
            ('Custom http', self._node.connect_w3_custom_http), 
            ('Custom websocket', self._node.connect_w3_custom_websocket),
            ('Custom ipc', self._node.connect_w3_custom_ipc),
            ('Custom Infura API Key', self._node.connect_w3_custom_infura),
            ('Geth dev PoA', self._node.connect_w3_gethdev_poa),
        ]
        radiobuttons = RadioButtons(options,name='netpicker')
        for i, option in enumerate(options):
            if option[1] == self._interface._config.default_method:
                radiobuttons._value = option[1]
                radiobuttons._selection = i

        layout.add_widget(radiobuttons)

        layout2 = Layout([1, 1])
        self.add_layout(layout2)

        layout2.add_widget(Button("Cancel", self._cancel), 1)
        layout2.add_widget(Button("Connect", self._ok), 0)
        self.fix()

    def _ok(self):
        network_option = self.find_widget('netpicker')
        connect_fn = network_option._value

        if connect_fn == self._node.connect_w3_custom_http:
            self._prompt_custom_http_uri()
        elif connect_fn():
            self._scene.add_effect( MessageDialog(self._screen, f"{self._interface.node.network_name} connected", destroy_window=self))
        else:
            self._scene.add_effect( MessageDialog(self._screen, "Connection failure", destroy_window=self))

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene("Main")

    def _prompt_custom_http_uri(self):
        dialog = TextRequestDialog(
            self._screen, 
            label_prompt_text="Ex: http://127.0.0.1:8023", 
            continue_button_text="Connect", 
            name="dialog_custom_http_uri", 
            title="Custom HTTP URI", 
            text_label="URI",
            text_default_value=self._interface._config.http_uri,
            destroy_window=self,
            continue_function=self._custom_http_continue_function,
            next_scene="Main"
        )
        self._scene.add_effect(dialog)

    def _custom_http_continue_function(self, text, calling_frame):
        network_option = self.find_widget('netpicker')
        connect_fn = network_option._value
        if connect_fn(text):
            self._scene.add_effect( MessageDialog(self._screen, f"{self._interface.node.network_name} connected", destroy_window=calling_frame))
        else:
            self._scene.add_effect( MessageDialog(self._screen, "Connection failure", destroy_window=calling_frame))


# This is a reusable dialog with a text field.
# continue function will be passed the string argument with the value
# of the text field, and this frame object so that it can be referenced
# for later removal.
# like so:
# continue_function(returned_text, text_request_dialog_object)
class TextRequestDialog(Frame):
    def __init__(self, screen, label_prompt_text=None, continue_button_text=None, continue_function=None, text_label=None, text_default_value=None, label_align="^", next_scene=None, **kwargs):
        super(TextRequestDialog, self).__init__(screen, 10, 46, has_shadow=True, is_modal=True, can_scroll=False, **kwargs)
        self.set_theme('shadowlands')
        self._continue_function = continue_function
        self._next_scene = next_scene

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Label(label_prompt_text, 2, align=label_align))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text(text_label, "text_field", default_value=text_default_value))
 

        layout2 = Layout([1, 1], fill_frame=False)
        self.add_layout(layout2)
        layout2.add_widget(Button(continue_button_text, self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 1)
        self.fix()

    def _ok(self):
        text = self.find_widget('text_field')
        self._continue_function(text._value, self)
        #self._destroy_window_stack()
        raise NextScene(self._next_scene)

    def _cancel(self):
        self._destroy_window_stack()
        raise NextScene(self._next_scene)

