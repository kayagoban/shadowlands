from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from shadowlands.tui.errors import ExitTuiError
from decimal import Decimal
from shadowlands.credstick import SignTxError
import pyperclip

from web3.exceptions import UnhandledRequest, BadFunctionCallOutput, StaleBlockchain
from websockets.exceptions import InvalidStatusCode, ConnectionClosed
#from web3.utils import threads
#from threads import Timeout

from decimal import InvalidOperation
from binascii import Error


from shadowlands.tui.debug import debug
# Make sure the widget frame is_modal or claimed_focus.
# otherwise the text is not swallowed and our menus are buggered.
# "return None if claimed_focus or self._is_modal else old_event" - widgets.py:882


#debug(self._screen._screen); import pdb; pdb.set_trace()


#debug(); pdb.set_trace()





class ValueOptions(Frame):
    def __init__(self, screen, interface):
        super(ValueOptions, self).__init__(screen, 15, 24, y=2, has_shadow=True, is_modal=True, name="valueopts", title="Value display", can_scroll=False)
        self.set_theme('shadowlands')
        self._interface = interface

    
        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=False))

        self._node = self._interface.node

        options = []
        currencies = self._interface.price_poller.eth_prices
        for k in currencies.keys():
            options.append( (k, k) )

        #debug(); pdb.set_trace()

        radiobuttons = RadioButtons(options,name='valuepicker')

        # Set radiobox to match stored options
        for i, option in enumerate(options):
            if option[1] == self._interface._config.displayed_currency:
                radiobuttons._value = option[1]
                radiobuttons._selection = i

        layout.add_widget(radiobuttons)

        layout2 = Layout([1, 1])
        self.add_layout(layout2)

        layout2.add_widget(Button("Cancel", self._cancel), 1)
        layout2.add_widget(Button("Select", self._ok), 0)
        self.fix()

    def _ok(self):
        options = self.find_widget('valuepicker')
        self._interface._config.displayed_currency = options._value
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    def _cancel(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)



class YesNoDialog(Frame):
    def __init__(self, screen, height, width, yes_callback=None, no_callback=None, yes_text="Yes", no_text="No",  **kwargs):
        super(YesNoDialog, self).__init__(screen, 3, width, **kwargs)
        self.set_theme('shadowlands')

        layout2 = Layout([1, 1], fill_frame=True)
        self.add_layout(layout2)

        layout2.add_widget(Button("Yes", yes_callback), 1)
        layout2.add_widget(Button("No", no_callback), 0)
        self.fix()


class QuitDialog(YesNoDialog):
    def __init__(self, screen):
        super(QuitDialog, self).__init__(screen, 3, 30, yes_callback=self._ok, no_callback=self._cancel,  has_shadow=True, is_modal=True, name="quitbox", title="Really quit?", can_scroll=False)

    def _ok(self):
        raise ExitTuiError 

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)
        #raise NextScene("Main")

    def process_event(self, event):
        if type(event) != KeyboardEvent:
            return event

        if event.key_code in [121, 89]:
            self._ok() 
        elif event.key_code in [110, 78]:
            self._cancel()

        super(QuitDialog, self).process_event(event)
 

