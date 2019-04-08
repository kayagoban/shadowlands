from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from shadowlands.tui.effects.widgets import QuitDialog, ValueOptions
from shadowlands.tui.effects.send_box import SendBox 
from shadowlands.tui.effects.message_dialog import MessageDialog
from shadowlands.tui.effects.network_options import NetworkOptions
from shadowlands.dapp_browser import DappBrowser
from shadowlands.qrcode import QRCodeDisplay 
from shadowlands.hd_addresses import HDAddressPicker
from shadowlands.release import ReleaseVersion
from shadowlands.tui.errors import ExitTuiError, PriceError
from shadowlands.sl_network_dapp import SLNetworkDapp
from shadowlands.tx_inspector import TxInspector
from shadowlands.credstick import DeriveCredstickAddressError
from shadowlands.tui.debug import debug
import importlib


import pdb
import pyperclip

#debug(self._screen._screen); import pdb; pdb.set_trace()

class LoadingScreenListener(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(LoadingScreenListener, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        pass

    def reset(self):
        pass


    def stop_frame(self):
        pass
 
    def process_event(self, event):
        if type(event) != KeyboardEvent:
            return event

        if event.key_code == -1 or event.key_code == 113:
            raise ExitTuiError
        elif event.key_code == ord('N') or event.key_code == ord('n'):
            self._scene.add_effect(NetworkOptions(self._screen, self._interface))

        return None



class MainMenuListener(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(MainMenuListener, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        pass

    def reset(self):
        #debug(); pdb.set_trace()
        if not self._interface._load_dapp:
            return

        dapp_module = importlib.import_module(self._interface._load_dapp)
        try:
            Dapp = getattr(dapp_module, 'Dapp')
        except AttributeError:
            self.dapp.add_message_dialog("Possible module name conflict.")
            return
        Dapp(
            self._screen, 
            self._scene, 
            self._interface.node,
            self._interface.config,
            self._interface.price_poller
        )
        pass


    def stop_frame(self):
        pass
 
    def process_event(self, event):

        #ord('C')

        if type(event) != KeyboardEvent:
            return event

        #debug(); pdb.set_trace()

        # if event.key_code == -1:    # esc.  for some reason esc has lag.

        # Q, q for quit
        if event.key_code in [113, 81]:
            self._scene.add_effect(QuitDialog(self._screen))
        # S, s  for send
        elif event.key_code in [115, 83]:
            self._scene.add_effect(SendBox(self._screen, self._interface))
        # C, c  for copy
        elif event.key_code in [67, 99]:
            pyperclip.copy(self._interface.credstick.addressStr())
            self._scene.add_effect(MessageDialog(self._screen, "Address copied to clipboard", 3, 35) )
        elif event.key_code in [ord('r'), ord('R')]:
            QRCodeDisplay(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        # E, e for ens
        elif event.key_code in [ord('e'), ord('E')]:
            SLNetworkDapp(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller,
                'ens.shadowlands'
            )
        # N, n for network
        elif event.key_code in [78, 110]:
            self._scene.add_effect(NetworkOptions(self._screen, self._interface))
        elif event.key_code in [86, 118]:
            # V, v for value
            #debug(); import pdb; pdb.set_trace()
            try:
                self._interface.price_poller.eth_prices
                self._scene.add_effect(ValueOptions(self._screen, self._interface))
            except (PriceError):
                self._scene.add_effect(MessageDialog(self._screen, "Price feed unavailable, try later", 3, 44) )
        # D, d for Deploy
        elif event.key_code in [ord('D'), ord('d')]:
            DappBrowser(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        elif event.key_code is 18:
            # super top secret shadowlands release management dapp. (ctrl-r)
            ReleaseVersion(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        elif event.key_code in [ord('H'), ord('h')]:
            # Test to see if we're able to derive before launching this..
            try:
                #debug(); pdb.set_trace()
                address = self._interface.node.credstick.derive()
            except DeriveCredstickAddressError:
                self._scene.add_effect(MessageDialog(self._screen, "Cannot derive addresses from Credstick.  Try restarting Shadowlands.", 3, 65) )
                return None
 
            # HD Addresses
            HDAddressPicker(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
 
        elif event.key_code in [ 
            ord('0'), ord('1'), ord('2'), ord('3'), ord('4')
        ]:
            ''' 
            TODO allow ctrl-0 through ctrl-4, and pass through
            these chars on SLDapp API frames, so that txs can
            be inspected even when using 3rd party dapps.
            '''
            TxInspector(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller,
                int(chr(event.key_code))
            )

        else:
            return None



