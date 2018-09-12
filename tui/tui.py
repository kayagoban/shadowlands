from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.screen import Screen
from tui.scenes.loading import LoadingScene
from sl_dapp import ExitDapp, RunDapp
from tui.errors import ExitTuiError, PriceError
from tui.scenes.main import MainScene
from tui.debug import debug
import sys

#debug(self._screen._screen); import pdb; pdb.set_trace()
#debug(screen._screen); import pdb; pdb.set_trace()

class Interface():
    
    CURR_SYMBOLS = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€',
        'BTC': 'Ƀ',
        'CHF': '',
        'AUD': '$',
        'RUB': '₽',
        'JPY': '¥',
        'CNY': '¥',
        'SGD': '$'

    }


    def __init__(self, _eth_node, config):
        self.node = _eth_node
        self._config = config
        self._screen = None
        self._price = None
        self._prices = None
        self._credstick = None
        self._scenes = []

    @property
    def credstick(self):
        return self._credstick

    @credstick.setter
    def credstick(self, credstick):
        self._credstick = credstick

    # make this a pythonic attribute
    def price(self):
        try:
            return self._prices['ETH'][self._config.displayed_currency]
        except TypeError:
            raise PriceError

    def curr_symbol(self):
        return self.CURR_SYMBOLS[self._config.displayed_currency]

    def update_prices(self, _prices):
        self._prices = _prices
        #debug(self._screen._screen); import pdb; pdb.set_trace()

        # reset price cursor print effect

    def tui(self, screen):
        self._screen = screen

        scenes = [
            LoadingScene(self._screen, "LoadingScene", self),
            MainScene(self._screen, "Main", self)
        ]
        # We re-use these two effects, which is why we define
        # them here.

        screen.play(scenes, stop_on_resize=True)

    def dapp_tui(self, screen):
        self._screen = screen
        # We re-use these two effects, which is why we define
        # them here.
        screen.play(dapp.scenes, stop_on_resize=True)


    def load(self):
        current_dapp = None

        while True:
            try:
                raise RunDapp
                Screen.wrapper(self.tui)
                break
            except ResizeScreenError:
                pass
            except RunDapp:
                print("switching to dapp...")
                # load dapp from wherever it is
                from dapp import Dapp
                current_dapp = Dapp(self.node)         
                try:
                    Screen.wrapper(current_dapp.tui)
                except ExitDapp:
                    del(sys.modules['dapp'])
            except ExitTuiError:
                print("Shutting it all down...")
                break

