from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from tui.errors import ExitTuiError
from tui.debug import debug
from decimal import Decimal

#debug(self._screen._screen); import pdb; pdb.set_trace()

# Make sure the widget frame is_modal or claimed_focus.
# otherwise the text is not swallowed and our menus are buggered.
# "return None if claimed_focus or self._is_modal else old_event" - widgets.py:882
class SendBox(Frame):
    def __init__(self, screen, interface):
        super(SendBox, self).__init__(screen, 15, 53, has_shadow=True, is_modal=True, name="sendbox", title="Send Crypto", can_scroll=False)
        self.set_theme('shadowlands')
        self._interface = interface
        self._screen = screen

        #self.set_theme('green')

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("To Address:", "address"))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text("    Amount:", "amount"))
        layout.add_widget(Divider(draw_line=False))
        currency_options = [("ETH", 0), ("WETH", 1), ("DAI", 2)]
        layout.add_widget(ListBox(1, currency_options, label="  Currency:",  name="currency"))
        layout.add_widget(Divider(draw_line=False))


        gas_price = self._interface.node.w3.fromWei(self._interface.node.w3.eth.gasPrice, 'gwei')

        layout.add_widget(RadioButtons(
            [
                (str(round(gas_price - gas_price * Decimal(.2), 2)), 0), 
                (str(gas_price) + ' gwei (<2 min)' , 1), 
                (str(round(gas_price + gas_price * Decimal(.2), 2)), 2),
                ('Enter custom gas price', 3)
            ], label='Gas Price:', name='gasoptions'))

        custgas = Text("Custom Gas (gwei):", "custgas")
        custgas._is_disabled = True
        layout.add_widget(custgas)
 
        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Sign Tx", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
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
 


