from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from shadowlands.tui.effects.widgets import QuitDialog
from shadowlands.tui.effects.send_box import SendBox 
from shadowlands.tui.effects.message_dialog import MessageDialog

from shadowlands.sl_dapp.network_connection import NetworkConnection
from shadowlands.sl_dapp.dapp_browser import DappBrowser
from shadowlands.sl_dapp.sl_network_dapp import SLNetworkDapp
from shadowlands.sl_dapp.hd_addresses import HDAddressPicker
from shadowlands.sl_dapp.release import ReleaseVersion
from shadowlands.sl_dapp.network_connection import NetworkConnection
from shadowlands.sl_dapp.tx_inspector import TxInspector
from shadowlands.sl_dapp.token_adder import TokenAdder
from shadowlands.sl_dapp.token_remover import TokenRemover
from shadowlands.sl_dapp.token_uniswapper import TokenUniswapper

from shadowlands.credstick import DeriveCredstickAddressError

from shadowlands.tui.errors import ExitTuiError, PriceError
import importlib
import pyperclip


from shadowlands.tui.debug import debug
import pdb


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
            NetworkConnection(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
 
            #self._scene.add_effect(NetworkOptions(self._screen, self._interface))

        return None



class MainMenuListener(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(MainMenuListener, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        pass

    def reset(self):
        '''
        Here we allow a dapp to be loaded from the command line
        '''
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
            self._interface._block_callback_watcher
        )
        pass


    def stop_frame(self):
        pass
 
    def process_event(self, event):

        #ord('C')

        if type(event) != KeyboardEvent:
            return event

        # if event.key_code == -1:    # esc.  for some reason esc has lag.

        # Q, q for quit
        if event.key_code in [113, 81]:
            self._scene.add_effect(QuitDialog(self._screen))
        # S, s  for send
        elif event.key_code in [115, 83]:
            if self._interface.node.eth_balance is None:
                self._scene.add_effect(MessageDialog(self._screen, "Cannot Send without Ether", 3, 35) )
                return

            self._scene.add_effect(SendBox(self._screen, self._interface))
        ## Tokens
        # Uniswap
        elif event.key_code in [ord('U'), ord('u')]:
            if self._interface.node.erc20_balances is None:
                self._scene.add_effect(MessageDialog(self._screen, "Need ERC20 balance data.", 3, 35) )
                return


            TokenUniswapper(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
        # T, t for tokens
        elif event.key_code in [ord('a'), ord('A')]:
            TokenAdder(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
        # T, t for tokens
        elif event.key_code in [ord('R'), ord('r')]:
            TokenRemover(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )

        elif event.key_code in [ord('B')]:
            debug(); pdb.set_trace()
 
        # C, c  for copy
        elif event.key_code in [67, 99]:
            pyperclip.copy(self._interface.credstick.addressStr())
            self._scene.add_effect(MessageDialog(self._screen, "Address copied to clipboard", 3, 35) )
        # E, e for ens
        #elif event.key_code in [ord('e'), ord('E')]:
        #    SLNetworkDapp(
        #        self._screen, 
        #        self._scene, 
        #        self._interface.node,
        #        self._interface.config,
        #        'ens.shadowlands'
        #    )
        # N, n for network
        elif event.key_code in [78, 110]:
            #self._scene.add_effect(NetworkOptions(self._screen, self._interface))
            NetworkConnection(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
 
        # D, d for Deploy
        elif event.key_code in [ord('D'), ord('d')]:
            DappBrowser(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
        elif event.key_code is 18:
            # super top secret shadowlands release management dapp. (ctrl-r)
            ReleaseVersion(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
            )
        elif event.key_code in [104, 72]:
            # Test to see if we're able to derive before launching this..
            HDAddressPicker(
                self._screen, 
                self._scene, 
                self._interface.node,
                self._interface.config,
                self._interface._block_callback_watcher
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
                self._interface._block_callback_watcher,
                int(chr(event.key_code))
            )

        else:
            return None



