#!/usr/bin/env python

from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from tui.effect_materialize import Materialize
import sys
from tui import debug

def loading_screen(screen):
    # Typical terminals are 80x24 on UNIX and 80x25 on Windows
    #if screen.width != 80 or screen.height not in (24, 25):
    _image = '''
╔═ Ledger Nano S ═══════════════════════════════════════╗
║
║  Address: 0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898
║
║  Ξth: 0.06040540066484375
║  Dai:
║
╚═══════════════════════════════════════════════════════╝
'''

    _node='Connected to infura node at Geth/v1.8.13-patched-infura-omnibus-b59d4428/linux-amd64/go1.9.2'
    _sync='[synced: block 6230988]\t\tNetwork: MainNet'
    _pubterm='p u b l i c    t e r m i n a l\t\t\tv0 . 0 1'

    effects = [
        Materialize(screen, StaticRenderer([_node]), 0, 0),
        Materialize(screen, StaticRenderer([_sync]), 0, 1, start_frame=10),
        Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 3, signal_acceleration_factor=1.1, start_frame=15),
        Materialize(screen, StaticRenderer([_pubterm]), 10, 10, signal_acceleration_factor=1.0005,start_frame=35),
        #Materialize(screen, StaticRenderer([_image]), 20, 20, Screen.COLOUR_GREEN, -0.005, 1.4)# , start_frame=0, stop_frame=5000),
        #UnicodeNoise( screen, BasicText(), stop_frame=300 ),
    ]
    #import pdb; pdb.set_trace()
    screen.play([Scene(effects, -1)], stop_on_resize=True)

     #debug(self._screen._screen); import pdb; pdb.set_trace()


while True:
    try:
        Screen.wrapper(loading_screen)
        sys.exit(0)
    except ResizeScreenError:
        pass




'''
        self._plain_image = [" " * self._width for _ in range(self._height)]
        self._colour_map = [[(None, 0, 0) for _ in range(self._width)]
                            for _ in range(self._height)]
''' 



