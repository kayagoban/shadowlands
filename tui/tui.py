from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.effects import Print
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from tui.effects.materialize import Materialize
from tui.effects.cursor import LoadingScreenCursor
from tui.blockstatus import BlockStatusCursor
from tui.networkstatus import NetworkStatusCursor
from tui.debug import debug
import sys
from time import sleep

#debug(self._screen._screen); import pdb; pdb.set_trace()
#debug(screen._screen); import pdb; pdb.set_trace()

class Interface():
    def __init__(self, _eth_node, _dapp, _credstick=None):
        self.credstick = _credstick
        self.node = _eth_node
        self.dapp = _dapp
        self.prices = None


        self._screen = None

        # effects
        self.effect_blockstatus = None 

        # scenes
        self.scene_loading_screen = None

    def set_credstick(self, _credstick):
        self.credstick = _credstick

    def update_prices(self, _prices):
        self.prices = _prices
        # reset price cursor print effect


    def _tui(self, screen):
        self._screen = screen


        self.effect_blockstatus = BlockStatusCursor(
            screen, self.node, 0, 0, speed=4, no_blink=True)

        self.effect_networkstatus = NetworkStatusCursor(
            screen, self.node, 60, 0, speed=4, no_blink=True)

        self.scene_loading_screen = Scene([], -1, name="LoadingScreen")

        self.scene_loading_screen.add_effect(self.effect_blockstatus)
        self.scene_loading_screen.add_effect(self.effect_networkstatus)

        scenes = [
            self.scene_loading_screen
        ]

        screen.play(scenes, stop_on_resize=True)


    def load(self):
        while True:
            try:
                Screen.wrapper(self._tui)
                sys.exit(0)
            except ResizeScreenError:
                pass

