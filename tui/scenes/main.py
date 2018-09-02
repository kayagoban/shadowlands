from asciimatics.renderers import StaticRenderer
from asciimatics.scene import Scene
from tui.effects.materialize import Materialize
from tui.effects.dynamic_cursor import DynamicSourceCursor
from tui.effects.listeners import MainMenuListener
from tui.renderers import BlockStatusRenderer, NetworkStatusRenderer, AddressRenderer
from tui.debug import debug


#from tui.effects.cursor import LoadingScreenCursor

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

    def __init__(self, screen, _name, interface):
        #debug(screen._screen); import pdb; pdb.set_trace()



        effects = [
            MainMenuListener(screen),
            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0, speed=4, no_blink=True),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 60, 0, speed=4, no_blink=True),
            Materialize(screen, StaticRenderer([self.CREDSTICK_DISPLAY]), 0, 2, signal_acceleration_factor=1.05),
            DynamicSourceCursor(screen, AddressRenderer(interface.credstick), 3, 6, speed=2, no_blink=True)
 
            #Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            #Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=75, speed=4, no_blink=False, thread=True)
        ]

        super(MainScene, self).__init__(effects, -1, name=_name)

