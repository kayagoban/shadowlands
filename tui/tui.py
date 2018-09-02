from asciimatics.exceptions import NextScene, ResizeScreenError
#from asciimatics.effects import Print
#from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from tui.scenes.loading import LoadingScene
from tui.errors import ExitTuiError
from tui.scenes.main import MainScene
from tui.debug import debug
import sys

#debug(self._screen._screen); import pdb; pdb.set_trace()
#debug(screen._screen); import pdb; pdb.set_trace()

class Interface():
    def __init__(self, _eth_node, _dapp, _credstick=None):
        self.credstick = _credstick
        self.node = _eth_node
        self.dapp = _dapp
        self._screen = None
        self._prices = None

    # Callback from the credstick_finder thread.
    # the credstick watcher effect will see this
    # and switch to the main scene.
    def set_credstick(self, _credstick):
        self.credstick = _credstick

    # make this a pythonic attribute
    def prices(self):
        if not self._prices:
            raise Exception
        return self._prices

    def update_prices(self, _prices):
        self._prices = _prices
        #debug(self._screen._screen); import pdb; pdb.set_trace()

        # reset price cursor print effect


    def tui(self, screen):
        self._screen = screen

        # We re-use these two effects, which is why we define
        # them here.
        scenes = [
            LoadingScene(screen, "LoadingScene", self),
            MainScene(screen, "Main", self)
        ]

        screen.play(scenes, stop_on_resize=True)


    def load(self):
        while True:
            try:
                Screen.wrapper(self.tui)
                break
            except ResizeScreenError:
                pass
            except ExitTuiError:
                print("Shutting it all down...")
                break

