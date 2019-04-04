from asciimatics.renderers import StaticRenderer
from asciimatics.widgets import Frame, Layout, Text, Button
from asciimatics.scene import Scene
from asciimatics.effects import Print
from shadowlands.tui.effects.materialize import Materialize
from shadowlands.tui.effects.dynamic_cursor import DynamicSourceCursor
from shadowlands.tui.effects.listeners import MainMenuListener
from shadowlands.tui.renderers import (
    BlockStatusRenderer, NetworkStatusRenderer, AddressRenderer, 
    CredstickNameRenderer, EthBalanceRenderer, EthValueRenderer, 
    ENSRenderer, QRCodeRenderer, HDPathRenderer
)

from shadowlands.tui.debug import debug
import pdb



#from tui.effects.cursor import LoadingScreenCursor
class MainScene(Scene):
    #MENU_TOP='''══════════════════════════════════════════════════════════════╗'''
    MENU_TOP='''═══════════════════════════════════════════════╗'''

    MENU_FRAME = '''
╔═
║
║  Ethereum Address:
║
║  ${7,1}H${2,2}D Path:
║
║  Reverse ${7,1}E${2,2}NS:
║
║  Ξth:
║
║  ${7,1}V${2,2}alue:
║
║
╠════════════════════════════╗
║ ${7,1}C${2,2}opy address to clipboard
║ ${7,1}S${2,2}end Ether or tokens
║ ${7,1}D${2,2}apps menu
║ ${7,1}Q${2,2}uit
╚
'''
#╚══════════════════════════════════════════════════════════════════════════════╝
#╚═════════════════════════════════════╩════════════════════════════════════════╝
    ENS='''║  ${7,1}E${2,2}NS:'''

    MENU_ITEMS='''
   Q ${7,1}C${2,2} ║ ${7,1}S${2,2} ║ ${7,1}D${2,2} 
   R ║ o ║ e ║ a
   c ║ p ║ n ║ p
   o ║ y ║ d ║ p
   d        ║ s
   e   
'''


    def __init__(self, screen, _name, interface):

        #debug(screen._screen); import pdb; pdb.set_trace()

        #debug(); pdb.set_trace()

        effects = [
            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0),
            Materialize(screen, StaticRenderer(['${7,1}N${2,2}etwork:' ]), 41, 0, signal_acceleration_factor=2, stop_frame = 100),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 51, 0),
            Materialize(screen, StaticRenderer([self.MENU_FRAME]), 0, 2, signal_acceleration_factor=1.05, stop_frame = 100),
            Materialize(screen, StaticRenderer([self.MENU_TOP]), 32, 3, signal_acceleration_factor=1.05, stop_frame=100),
            DynamicSourceCursor(screen, CredstickNameRenderer(interface), 3, 3),
            #Materialize(screen, StaticRenderer([self.ENS]), 38, 9, signal_acceleration_factor=1.05, stop_frame=100),
            #Materialize(screen, StaticRenderer([self.MENU_ITEMS]), 65, 3, signal_acceleration_factor=1.05, start_frame=10, stop_frame=100),
            Materialize(screen, QRCodeRenderer(interface), 48, 7, signal_acceleration_factor=1.2, stop_frame=120),
            DynamicSourceCursor(screen, AddressRenderer(interface), 22, 5),
            DynamicSourceCursor(screen, HDPathRenderer(interface), 13, 7),
            DynamicSourceCursor(screen, EthBalanceRenderer(interface), 8, 11),
            DynamicSourceCursor(screen, EthValueRenderer(interface), 10, 13),
            DynamicSourceCursor(screen, ENSRenderer(interface), 16, 9),
            MainMenuListener(screen, interface)


            #Materialize(screen, StaticRenderer([self.CREDSTICK_DISPLAY]), 0, 14, signal_acceleration_factor=1.05),
 
            #Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            #Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=75, speed=4, no_blink=False, thread=True)
        ]

        super(MainScene, self).__init__(effects, -1, name=_name)

        #debug(screen._screen); import pdb; pdb.set_trace()

 


