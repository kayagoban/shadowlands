#!/usr/bin/env python

from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene, ResizeScreenError
from asciimatics.effects import Print
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from tui.effects.materialize import Materialize
from tui.effects.cursor import LoadingScreenCursor
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
            self._scene.add_effect(
                Materialize(self._screen, StaticRenderer([dapp_menu]), 15, 7)
                )
        else:
            return None


def menu(screen):

    # Typical terminals are 80x24 on UNIX and 80x25 on Windows
    # if screen.width != 80 or screen.height not in (24, 25):

    credstick_display = '''
╔═ Ledger Nano S ══════════════════════════════════════════════════════════════╗
║                                                                ${7,1}S${2,2} ║ ${7,1}C${2,2} ║ ${7,1}T${2,2} ║ ${7,1}D${2,2}
║  ${7,1}A${2,2}ddress: 0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898           e ║ o ║ o ║ a
║                                                                n ║ p ║ k ║ p
║  Ξth: 2993450.06040540066484375                                d ║ y ║ e ║ p
║                                                                      ║ n ║ s
║  ${7,1}V${2,2}alue: USD $96.27                  ║  ${7,1}E${2,2}NS: kayagoban.eth            ║ s
╚═════════════════════════════════════╩════════════════════════════════════════╝

'''
    txdisplay = '''
     T${7,1}x${2,2}
     ║║
 ${7,1}1${2,2}│ ${7,1}0${2,2}║║
 ═╪══╣╠
 5│ b║║
 1│ 8║║
 a│ b║║
 c│ f║║
 9│ 2║║
 9│ 5║║
     ╝╚
'''

    alttxdisplay='''
T${7,1}x${2,2}
─╖
${7,1}0${2,2}║  0x80fbe87fc0221221644987b1d67837be4a30b1c3cc3461554c314b8a72d47ba0
─╢
${7,1}1${2,2}║  0x99ea696d40c0b4e9f765612969a52d5a477cbabc0eb11370a8814d640e6b2e00
'''


#║  USD $96.27 ║  GBP £53.03  ║ EUR €104.23  ║

    node='Connected to infura node at Geth/v1.8.13-patched-infura-omnibus-b59d4428/linux-amd64/go1.9.2'
    sync='[synced: block 6230988]                               ${7,1}N${2,2}etwork: MainNet (local)'
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
        LoadingScreenCursor(screen, StaticRenderer([prompt]), 0, 14, start_frame=75, speed=2, no_blink=False),
    ]

    #UnicodeNoise( screen, BasicText(), stop_frame=300 ),

    main_menu_effects2 = [
        Materialize(screen, StaticRenderer([sync]), 0, 0),
        CredstickMenu(screen, StaticRenderer([credstick_display]), 0, 2),
        Materialize(screen, StaticRenderer([alttxdisplay]), 0 , 18),
        #Materialize(screen, StaticRenderer([txdisplay]), screen.width // 2 - 4 , 13),
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



