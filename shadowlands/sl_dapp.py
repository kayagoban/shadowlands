from abc import ABC, abstractmethod
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons
from asciimatics.exceptions import NextScene
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from shadowlands.credstick import SignTxError
from shadowlands.tui.effects.widgets import MessageDialog, TransactionFrame
from decimal import Decimal

from shadowlands.tui.debug import debug
import pdb

class SLDapp(Effect):
    def __init__(self, screen, scene, eth_node, config, price_poller, destroy_window=None):
        self._screen = screen
        self._scene = scene
        self._node = eth_node
        self._config = config
        self._price_poller = price_poller
        # Prepare a wait frame that we can show and unshow as we please.
        message = "Cooking up some data..."
        preferred_width= len(message) + 6
        self.waitframe = SLWaitFrame(self, message, 3, preferred_width)

        self.initialize()

        if destroy_window is not None:
            destroy_window.close()

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

    # cls is a custom subclass of SLFrame
    def add_frame(self, cls, height=None, width=None, title=None, **kwargs):
        # we are adding SLFrame effects.  asciimatics can do a lot more
        # than this, but we're hiding away the functionality for the 
        # sake of simplicity.
        frame = cls(self, height, width, title=title, **kwargs)
        self._scene.add_effect(frame)
        return frame 

    def show_wait_frame(self):
        self._scene.add_effect( self.waitframe ) 

    def hide_wait_frame(self):
        try:
            self._scene.remove_effect( self.waitframe ) 
        except:
            # We need to be able to call this method without consequence
            pass


    def add_message_dialog(self, message, **kwargs):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, **kwargs))

    def add_transaction_dialog(self, tx_fn=None, tx_value=0, destroy_window=None, title="Sign & Send Transaction", **kwargs):
        #debug(); pdb.set_trace()
        self._scene.add_effect( 
            SLTransactionFrame(self._screen, 16, 59, self, tx_fn, destroy_window=destroy_window, title=title, tx_value=tx_value, **kwargs) 
        )

    def quit(self):
        # Remove all owned windows
        self._scene.remove_effect(self)
        raise NextScene(self._scene.name)

    def _update():
        pass
    def reset():
        pass
    def stop_frame():
        pass



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

    def add_button(self, ok_fn, text, layout_distribution=[100], layout_index=0):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        layout.add_widget(Button(text, ok_fn), layout_index)
        layout.add_widget(Divider(draw_line=False))

    def add_ok_cancel_buttons(self, ok_fn, cancel_fn=None, ok_text="OK"):
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button(ok_text, ok_fn), 0)
        if cancel_fn is None:
            cancel_fn = self.close
        layout.add_widget(Button("Cancel", cancel_fn), 3)
 
    # named arguments will be passed on to the asciimatics Text() constructor
    def add_textbox(self, label_text, default_value=None, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        text_widget = Text(label_text, **kwargs)
        if default_value is not None:
            text_widget._value = default_value
        layout.add_widget(text_widget)
        layout.add_widget(Divider(draw_line=False))
        return lambda: text_widget._value

    def add_divider(self, draw_line=False, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=draw_line, **kwargs))

    def add_radiobuttons(self, options, default_value=None, layout_distribution=[100], layout_index=0, **kwargs):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        radiobuttons_widget = RadioButtons(options, **kwargs)
        layout.add_widget(radiobuttons_widget, layout_index)
        layout.add_widget(Divider(draw_line=False))
        if default_value is not None:
            radiobuttons_widget._value = default_value
        return lambda: radiobuttons_widget.value


    def add_listbox(self, height, options, on_select=None, layout_distribution=[100], layout_index=0, **kwargs):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        list_widget = ListBox(height, options, on_select=on_select, **kwargs)
        layout.add_widget(list_widget, layout_index)
        layout.add_widget(Divider(draw_line=False))
        return lambda: list_widget.value
         
    def add_label(self, label_text, layout_distribution=[100], layout_index=0,):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        layout.add_widget(Label(label_text), layout_index) 
        layout.add_widget(Divider(draw_line=False))

    def add_file_browser(self, on_select_fn, path='/', height=15, on_change_fn=None):
        layout = Layout([100])
        self.add_layout(layout)
        browser = FileBrowser(height, path, on_select=on_select_fn, on_change=on_change_fn)
        layout.add_widget(browser)
        layout.add_widget(Divider(draw_line=False))
        return lambda: browser._value

    def close(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    @property
    def dapp(self):
        return self._dapp
    

class SLWaitFrame(SLFrame):
    def initialize(self):
        self.add_label(self.message)

    def __init__(self, dapp, wait_message, height, width, **kwargs):
        self.message = wait_message
        super(SLWaitFrame, self).__init__(dapp, height, width, **kwargs)

    def process_event(self, event):
        # Swallows every damn thing
        return None

class SLTransactionFrame(TransactionFrame):
    def __init__(self, screen, x, y, dapp=None, tx_fn=None, tx_value=0, gas_limit=None, **kwargs):
        super(SLTransactionFrame, self).__init__(screen, x, y, dapp, self._ok_fn, self._cancel_fn, **kwargs) 
        self.dapp = dapp
        self._tx_fn = tx_fn

        #debug(); pdb.set_trace()
        if gas_limit is not None:
            self.estimated_gas = gas_limit
        else:
            try:
                self.estimated_gas = tx_fn().estimateGas()
            except ValueError:
                self.estimated_gas = 1000000

        layout = Layout([100])
        self.prepend_layout(layout)

        self.tx_value = Decimal(tx_value)
        layout.add_widget(Label("You will send {} ETH.format".format(self.tx_value)))
        layout.add_widget(Divider(draw_line=False))

        layout.add_widget(Label("Estimated Gas for Tx: {}".format(self.estimated_gas)))
        layout.add_widget(Divider(draw_line=False))
 
        self.fix()

    def _ok_fn(self, gas_price_wei):
        try:
            self.dapp.node.push(
                self._tx_fn(), gas_price_wei, self.estimated_gas, value=self.dapp.node.w3.toWei(Decimal(self.tx_value), 'ether')
            )
        except (SignTxError):
            self.dapp.add_message_dialog("Credstick did not sign Transaction", destroy_window=self)
            return

        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    def _cancel_fn(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)



class ExitDapp(Exception):
    pass

class RunDapp(Exception):
    pass
