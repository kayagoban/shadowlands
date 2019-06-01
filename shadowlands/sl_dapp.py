from time import sleep
from abc import ABC, abstractmethod
from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons, CheckBox, QRCode
)
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent, MouseEvent
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from shadowlands.credstick import SignTxError
from shadowlands.tui.effects.message_dialog import MessageDialog
from decimal import Decimal
import pyperclip

from shadowlands.tui.debug import debug, end_debug

from shadowlands.sl_frame import SLFrame, SLWaitFrame, AskClipboardFrame

from shadowlands.uniswap_frame import UniswapFrame

from shadowlands.sl_transaction_frame import SLTransactionFrame

import pdb

class SLDapp():
    def __init__(self, screen, scene, eth_node, config, destroy_window=None):
        self._config_key = self.__module__
        self._screen = screen
        self._scene = scene
        self._node = eth_node
        self._config = config
        self.initialize()

        if destroy_window is not None:
            destroy_window.close()

    @property
    def node(self):
        return self._node

    @property
    def w3(self):
        return self._node.w3

    @property
    def config(self):
        return self._config
        
    @property
    def config_key(self):
        return self._config_key

    @config_key.setter
    def config_key(self, key):
        self._config_key = key

    @property
    def config_properties(self):
        return self.config.dapp_config(self.config_key)

    def save_config_property(self, property_key, value):
        properties = dict(self.config_properties)
        properties[property_key] = value
        self.config.set_dapp_config(self.config_key, properties)

    def load_config_property(self, property_key):
        return self.config_properties[property_key]

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

    def show_wait_frame(self, message="Please wait a moment..."):
        preferred_width= len(message) + 6
        self.waitframe = SLWaitFrame(self, message, 3, preferred_width)
        self._scene.add_effect( self.waitframe ) 

    def hide_wait_frame(self):
        try:
            self._scene.remove_effect( self.waitframe ) 
        except:
            # We need to be able to call this method without consequence
            pass
        # This should be called in a thread, so sleeping is an OK thing to do.
        # Should give the time for the UI to finish its current pass and remove the 
        # wait frame.
        sleep(0.5)


    def add_message_dialog(self, message, **kwargs):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, **kwargs))

    def add_transaction_dialog(self, tx_fn, title="Sign & Send Transaction", tx_value=0, destroy_window=None, gas_limit=None, **kwargs):
        self._scene.add_effect( 
            SLTransactionFrame(self, 20, 59, tx_fn, destroy_window=destroy_window, title=title, gas_limit=gas_limit, tx_value=tx_value, **kwargs) 
        )

    def add_uniswap_frame(self, token_address, action='buy', buy_amount='', sell_amount=''):
        self._scene.add_effect(UniswapFrame(self, 17, 46, token_address, action=action, buy_amount=buy_amount, sell_amount=sell_amount) )


    def add_send_dialog(self, tx_dict, title="Sign & Send"):
        # This class is duck typed to web3.py contract functions.
        class TransactionFunction():
            def __init__(self, dict):
                self._dict = dict
            def buildTransaction(self, tx_dict):
                self._dict['gasPrice'] = tx_dict['gasPrice']
                self._dict['gas'] = tx_dict['gas']
                self._dict['value'] = tx_dict['value']
                self._dict['data'] = '0x'
                self._dict['chainId'] = tx_dict['chainId']
                return self._dict

        tx_fn = TransactionFunction(tx_dict)

        self._scene.add_effect( 
            SLTransactionFrame(
                self, 20, 59, tx_fn, title=title, 
                gas_limit=tx_dict['gas'], 
                tx_value=self.node.w3.fromWei(tx_dict['value'], 'ether') 
            )
        )
 

    def add_transaction_wait_dialog(self, tx_fn, wait_message, title="Sign & Send Transaction", tx_value=0, destroy_window=None, gas_limit=None, receipt_proc=None, **kwargs):
        self._scene.add_effect( 
            SLTransactionWaitFrame(self, 16, 59, wait_message, tx_fn=tx_fn, gas_limit=gas_limit, receipt_proc=receipt_proc, **kwargs) 
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

    


class ExitDapp(Exception):
    pass

class RunDapp(Exception):
    pass
