from asciimatics.renderers import StaticRenderer
from asciimatics.widgets import Frame, Layout, Text, Button
from asciimatics.scene import Scene
from shadowlands.tui.effects.materialize import Materialize
from shadowlands.tui.effects.dynamic_cursor import DynamicSourceCursor
from shadowlands.tui.effects.listeners import MainMenuListener
from shadowlands.tui.renderers import BlockStatusRenderer, NetworkStatusRenderer, AddressRenderer, CredstickNameRenderer, EthBalanceRenderer, EthValueRenderer, ENSRenderer
from shadowlands.tui.debug import debug


#debug(screen._screen); import pdb; pdb.set_trace()
#from tui.effects.cursor import LoadingScreenCursor
class MainScene(Scene):
    #MENU_TOP='''══════════════════════════════════════════════════════════════╗'''
    MENU_TOP='''═══════════════════════════════════════════════╗'''

    MENU_FRAME = '''
╔═
║
║  ${7,1}A${2,2}ddress:
║
║  Ξth:
║
║  ${7,1}V${2,2}alue:
╚═════════════════════════════════════╩════════════════════════════════════════╝
'''
    ENS='''║  ${7,1}E${2,2}NS:'''

    MENU_ITEMS='''
${7,1}S${2,2} ║ ${7,1}C${2,2} ║ ${7,1}T${2,2} ║ ${7,1}D${2,2} 
e ║ o ║ o ║ a
n ║ p ║ k ║ p
d ║ y ║ e ║ p
      ║ n ║ s
      ║ s
'''


    TXDISPLAY='''
T${7,1}x${2,2}
─╖
${7,1}0${2,2}║  0x80fbe87fc0221221644987b1d67837be4a30b1c3cc3461554c314b8a72d47ba0
─╢
${7,1}1${2,2}║  0x99ea696d40c0b4e9f765612969a52d5a477cbabc0eb11370a8814d640e6b2e00
'''



    def __init__(self, screen, _name, interface):

        #debug(screen._screen); import pdb; pdb.set_trace()

        effects = [
            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0),
            Materialize(screen, StaticRenderer(['${7,1}N${2,2}etwork:' ]), 41, 0, signal_acceleration_factor=2, stop_frame = 100),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 51, 0),
            Materialize(screen, StaticRenderer([self.MENU_FRAME]), 0, 2, signal_acceleration_factor=1.05, stop_frame = 100),
            Materialize(screen, StaticRenderer([self.MENU_TOP]), 32, 3, signal_acceleration_factor=1.05, stop_frame=100),
            DynamicSourceCursor(screen, CredstickNameRenderer(interface), 3, 3),
            Materialize(screen, StaticRenderer([self.ENS]), 38, 9, signal_acceleration_factor=1.05, stop_frame=100),
            Materialize(screen, StaticRenderer([self.MENU_ITEMS]), 65, 3, signal_acceleration_factor=1.05, start_frame=10, stop_frame=100),
            DynamicSourceCursor(screen, AddressRenderer(interface), 12, 5),
            DynamicSourceCursor(screen, EthBalanceRenderer(interface), 8, 7),
            DynamicSourceCursor(screen, EthValueRenderer(interface), 10, 9),
            DynamicSourceCursor(screen, ENSRenderer(interface), 46, 9),
            MainMenuListener(screen, interface)




            #Materialize(screen, StaticRenderer([self.CREDSTICK_DISPLAY]), 0, 14, signal_acceleration_factor=1.05),
 
            #Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            #Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=75, speed=4, no_blink=False, thread=True)
        ]

        super(MainScene, self).__init__(effects, -1, name=_name)

        #debug(screen._screen); import pdb; pdb.set_trace()



