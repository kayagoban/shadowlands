#!/usr/bin/env python

from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.effects import Print
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from tui.effects.materialize import Materialize
from tui.effects.cursor import LoadingScreenCursor
from blockies import create_blockie

blockie = create_blockie('0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359')
# `rows` contains ansi escaped strings
#for row in rows:
#    print(row)

from tui.debug import debug
import sys

 
dapp_menu = '''
╔═ Dapps ═══════════════════════════════════════════╗
║
║  Trade Ether for Dai                      (Oasis)
║  Borrow Dai against Eth with a CDP Loan   (Maker)
║  Manage ethereum names                    (ENS)
║  Shadowland BBS Forum
║  Chat on the whispernet
╚═══════════════════════════════════════════════════╝
'''

class CredstickMenu(Materialize):

    def process_event(self, event):
       #debug(self._screen._screen); import pdb; pdb.set_trace()
        #D for dapp
        if type(event) != KeyboardEvent:
            return None

        if event.key_code == 100:
            print(blockie)
            self._scene.add_effect(
                Print(self._screen, StaticRenderer(blockie), 15, 7)
                #Materialize(self._screen, StaticRenderer([dapp_menu]), 15, 7)
                )
        else:
            return None


def menu(screen):

    # Typical terminals are 80x24 on UNIX and 80x25 on Windows
    # if screen.width != 80 or screen.height not in (24, 25):

    credstick_display2 = '''
╔═ Ledger Nano S ══════════════════════════════════════════════════════════════╗
║                                                            ${7,1}S${2,2} ║ ${7,1}C${2,2} ║ ${7,1}T${2,2} ║ ${7,1}D${2,2}
║  ${7,1}A${2,2}ddress: 0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898       e ║ o ║ o ║ a
║                                                            n ║ p ║ k ║ p
║  Ξth: 2993450.06040540066484375                            d ║ y ║ e ║ p
║                                                                  ║ n ║ s
║  $96.27  ║  £53.03  ║  €104.23  ║   ${7,1}E${2,2}NS: kayagoban.eth             s  
╚══════════╩══════════╩═══════════╩════════════════════════════════════════════╝

'''


    credstick_display = '''
╔═ Ledger Nano S ══════════════════════════════════════════════════════════════╗
║                                                            ${7,1}S${2,2} ║ ${7,1}C${2,2} ║ ${7,1}H${2,2} ║ ${7,1}T${2,2} ║ ${7,1}D${2,2}
║  Address: 0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898       e ║ o ║ D ║ o ║ a
║                                                            n ║ p ║ p ║ k ║ p
║  Ξth: 2993450.06040540066484375                            d ║ y ║ a ║ e ║ p
║                                                                  ║ t ║ n ║ s
║  $96.27  ║  £53.03  ║  €104.23  ║   ${7,1}E${2,2}NS: kayagoban.eth             h ║ s  
╚══════════╩══════════╩═══════════╩════════════════════════════════════════════╝

'''

#║  USD $96.27 ║  GBP £53.03  ║ EUR €104.23  ║        

    node='Connected to infura node at Geth/v1.8.13-patched-infura-omnibus-b59d4428/linux-amd64/go1.9.2'
    sync='[synced: block 6230988]      Network: MainNet       Remote Node: infura at Geth/v1.8.13-patch...'
    pubterm='p u b l i c    t e r m i n a l\t\t\tv0 . 0 1'
    prompt='''Welcome, chummer.  Insert your credstick to begin...
A credstick, like a Trezor or a Ledger.   You know, what the bakebrains call a 'hardware wallet'. No creds, no joy, dataslave.
If you have cyberware installed in your finger, I guess you could try plugging that in...
Or just keep hitting the enter button.  Have fun with that.'''

    loading_screen_effects = [
        Materialize(screen, StaticRenderer([node]), 0, 0),
        Materialize(screen, StaticRenderer([sync]), 0, 1, start_frame=10),
        Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 3, signal_acceleration_factor=1.1, start_frame=15),
        Materialize(screen, StaticRenderer([pubterm]), 10, 10, signal_acceleration_factor=1.0005,start_frame=35),
        LoadingScreenCursor(screen, StaticRenderer([prompt]), 0, 14, start_frame=75),
        #Materialize(screen, StaticRenderer([_image]), 20, 20, Screen.COLOUR_GREEN, -0.005, 1.4)# , start_frame=0, stop_frame=5000),
        #UnicodeNoise( screen, BasicText(), stop_frame=300 ),
    ]

    main_menu_effects = [
        Materialize(screen, StaticRenderer([node]), 0, 0),
        Materialize(screen, StaticRenderer([sync]), 0, 1),
        CredstickMenu(screen, StaticRenderer([credstick_display2]), 0, 3),
    ]

    main_menu_effects2 = [
        Materialize(screen, StaticRenderer([sync]), 0, 0),
        CredstickMenu(screen, StaticRenderer([credstick_display2]), 0, 3),
    ]


    #Materialize(screen, StaticRenderer([dapp_menu]), 0, 7),

    scenes = [
        Scene(loading_screen_effects, -1, name="LoadingScreen"),
        Scene(main_menu_effects2, -1, name="MainMenu"),
    ]

    screen.play(scenes, stop_on_resize=True)

while True:
    try:
        Screen.wrapper(menu)
        sys.exit(0)
    except ResizeScreenError:
        pass




'''
        self._plain_image = [" " * self._width for _ in range(self._height)]
        self._colour_map = [[(None, 0, 0) for _ in range(self._width)]
                            for _ in range(self._height)]
'''



