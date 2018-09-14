from abc import ABC, abstractmethod
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, Label
from asciimatics.exceptions import NextScene
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from shadowlands.tui.effects.widgets import MessageDialog, TransactionFrame
from decimal import Decimal

from shadowlands.tui.debug import debug
import pdb

class SLDapp(Effect):
    def __init__(self, screen, scene, eth_node, config, price_poller):
        self._screen = screen
        self._scene = scene
        self._node = eth_node
        self._config = config
        self._price_poller = price_poller
        self.initialize()

    @property
    def node(self):
        return self._node

    @property
    def config(self):
        return self._config
        
    @property
    def price_poller(self):
        return self._price_poller


    @abstractmethod
    def initialize(self):
        pass

    def add_frame(self, cls, height=None, width=None, title=None):
        # we are adding SLFrame effects.  asciimatics can do a lot more
        # than this, but we're hiding away the functionality for the 
        # sake of simplicity.
        self._scene.add_effect(cls(self, height, width, title=title))

    def add_message_dialog(self, message):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, destroy_window=None))

    def add_yes_no_dialog(self, question, yes_fn=None, no_frame=None):
        preferred_width= len(question) + 6
        self._scene.add_effect( YesNoDialog(self._screen, question, width=preferred_width, destroy_window=None))

    def add_transaction_dialog(self, tx_fn=None, tx_value=0, destroy_window=None, title="Sign & Send Transaction"):
        #debug(); pdb.set_trace()
        self._scene.add_effect( 
            SLTransactionFrame(self._screen, 16, 59, self, tx_fn, destroy_window=destroy_window, title=title, tx_value=tx_value) 
        )


    def quit(self):
        # Remove all owned windows
        self._screen.remove_effect(self)
        raise NextScene

    def _update():
        pass
    def reset():
        pass
    def stop_frame():
        pass


class SLTransactionFrame(TransactionFrame):
    def __init__(self, screen, x, y, dapp=None, tx_fn=None, tx_value=0, **kwargs):
        super(SLTransactionFrame, self).__init__(screen, x, y, dapp, self._ok_fn, self._cancel_fn, **kwargs) 
        self.dapp = dapp
        self._tx_fn = tx_fn
        #self.estimated_gas = tx_fn.gasEstimate()
        try:
            self.estimated_gas = tx_fn().estimateGas()
        except ValueError:
            self.estimated_gas = 1000000



        layout = Layout([100])
        self.prepend_layout(layout)

        self.tx_value = Decimal(tx_value)
        layout.add_widget(Label(f"You will send {self.tx_value} ETH"))
        layout.add_widget(Divider(draw_line=False))

        layout.add_widget(Label(f"Estimated Gas for Tx: {self.estimated_gas}"))
        layout.add_widget(Divider(draw_line=False))
 
        self.fix()

    def _ok_fn(self, gas_price_wei):
        self.dapp.node.push(
            self._tx_fn(), gas_price_wei, self.estimated_gas, value=self.dapp.node.w3.toWei(Decimal(self.tx_value), 'ether')
        )
        self._destroy_window_stack()
        raise NextScene

    def _cancel_fn(self):
        self._destroy_window_stack()
        raise NextScene




class SLFrame(Frame):
    def __init__(self, dapp, height, width, **kwargs):
        self._dapp = dapp
        self._screen = dapp._screen

        super(SLFrame, self).__init__(self._screen,
                                      height,
                                      width,
                                      can_scroll=False,
                                      is_modal=True,
                                      **kwargs)
                                      #hover_focus=True,
        self.set_theme('shadowlands')
        self.initialize()
        self.fix()

    def add_ok_cancel_buttons(self, ok_fn, cancel_fn, ok_text="OK"):
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button(ok_text, ok_fn), 0)
        layout.add_widget(Button("Cancel", cancel_fn), 3)
 
    # named arguments will be passed on to the asciimatics Text() constructor
    def add_textbox(self, label_text, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        text_widget = Text(label_text, **kwargs)
        layout.add_widget(text_widget)
        layout.add_widget(Divider(draw_line=False))
        return lambda: text_widget._value
         
    def add_label(self, label_text):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Label(label_text)) 
        layout.add_widget(Divider(draw_line=False))

    def close(self):
        self._destroy_window_stack()
        raise NextScene

    @property
    def dapp(self):
        return self._dapp



class ExitDapp(Exception):
    pass

class NextFrame(NextScene):
    pass

class RunDapp(Exception):
    pass

