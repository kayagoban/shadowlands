from asciimatics.renderers import StaticRenderer
from asciimatics.widgets import Frame
from asciimatics.scene import Scene
from tui.effects.materialize import Materialize
from tui.effects.dynamic_cursor import DynamicSourceCursor
from tui.effects.listeners import MainMenuListener
from tui.renderers import BlockStatusRenderer, NetworkStatusRenderer, AddressRenderer, CredstickNameRenderer, EthBalanceRenderer, EthValueRenderer, ENSRenderer
from tui.debug import debug


#from tui.effects.cursor import LoadingScreenCursor

class SendBox(Frame):
    def __init__(self, screen):
        super(SendBox, self).__init__(screen, 10, 15, has_shadow=True, name="Send")
#        debug(screen._screen); import pdb; pdb.set_trace()
        self.set_theme('green')


class MainScene(Scene):

    CREDSTICK_DISPLAY = '''
╔═ Ledger Nano S ══════════════════════════════════════════════════════════════╗
║                                                                ${7,1}S${2,2} ║ ${7,1}C${2,2} ║ ${7,1}T${2,2} ║ ${7,1}D${2,2}
║  ${7,1}A${2,2}ddress:                                                      e ║ o ║ o ║ a
║                                                                n ║ p ║ k ║ p
║  Ξth:                                                          d ║ y ║ e ║ p
║                                                                      ║ n ║ s
║  ${7,1}V${2,2}alue:                             ║  ${7,1}E${2,2}NS:                          ║ s
╚═════════════════════════════════════╩════════════════════════════════════════╝
'''
    MENU_TOP='''══════════════════════════════════════════════════════════════╗'''

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

    def __init__(self, screen, _name, interface):

        #debug(screen._screen); import pdb; pdb.set_trace()

        effects = [
            MainMenuListener(screen),
            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0, refresh_period=220),
            Materialize(screen, StaticRenderer(['${7,1}N${2,2}etwork:' ]), 45, 0, signal_acceleration_factor=2),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 55, 0, refresh_period=250),
            Materialize(screen, StaticRenderer([self.MENU_FRAME]), 0, 2, signal_acceleration_factor=1.05),
            Materialize(screen, StaticRenderer([self.MENU_TOP]), 17, 3, signal_acceleration_factor=1.05),
            DynamicSourceCursor(screen, CredstickNameRenderer(interface), 3, 3),
            Materialize(screen, StaticRenderer([self.ENS]), 38, 9, signal_acceleration_factor=1.05),
            Materialize(screen, StaticRenderer([self.MENU_ITEMS]), 65, 3, signal_acceleration_factor=1.05, start_frame=40),
            DynamicSourceCursor(screen, AddressRenderer(interface), 12, 5, start_frame=40, refresh_period=200),
            DynamicSourceCursor(screen, EthBalanceRenderer(interface), 8, 7, start_frame=55, refresh_period=300),
            DynamicSourceCursor(screen, EthValueRenderer(interface), 10, 9, start_frame=65, refresh_period=340),
            DynamicSourceCursor(screen, ENSRenderer(interface), 46, 9, start_frame=70, refresh_period=500),
            SendBox(screen)
            #Materialize(screen, StaticRenderer([self.CREDSTICK_DISPLAY]), 0, 14, signal_acceleration_factor=1.05),
 
            #Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            #Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=75, speed=4, no_blink=False, thread=True)
        ]

        super(MainScene, self).__init__(effects, -1, name=_name)

