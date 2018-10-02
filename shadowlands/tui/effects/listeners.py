from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from shadowlands.tui.effects.widgets import SendBox, QuitDialog, MessageDialog, NetworkOptions, ValueOptions
from shadowlands.dapp_browser import DappBrowser
from shadowlands.hd_addresses import HDAddressPicker
from shadowlands.deploy import Deployer
from shadowlands.release import ReleaseVersion
from shadowlands.tui.errors import ExitTuiError, PriceError
from shadowlands.tui.debug import debug
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
        # N, n for network
        elif event.key_code in [78, 110]:
            self._scene.add_effect(NetworkOptions(self._screen, self._interface))
        # E, e for ENS
        elif event.key_code in [69, 101]:
            Dapp(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        # V, v for value
        elif event.key_code in [86, 118]:
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
        elif event.key_code in [ord('Y')]:
           Deployer(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        elif event.key_code is 18:
            # super top secret shadowlands release management dapp.
            ReleaseVersion(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
        elif event.key_code in [ord('A'), ord('a')]:
            # HD Addresses
            HDAddressPicker(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface.price_poller
            )
 
        else:
            return None
