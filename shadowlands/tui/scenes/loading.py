from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from shadowlands.tui.effects.materialize import Materialize
from shadowlands.tui.effects.cursor import LoadingScreenCursor
from shadowlands.tui.effects.dynamic_cursor import DynamicSourceCursor
from shadowlands.tui.renderers import BlockStatusRenderer, NetworkStatusRenderer
from shadowlands.tui.effects.credstick_watcher import CredstickWatcher
from shadowlands.version import SL_VERSION


PROMPT='''Welcome, chummer.  Insert your credstick to begin...
A credstick, like a Trezor or a Ledger.   You know, what the bakebrains call a 'hardware wallet'. No creds, no joy, dataslave.
If you have cyberware installed in your finger, I guess you could try plugging that in...
Or just keep hitting the enter button.  Have fun with that.'''

class LoadingScene(Scene):
    def __init__(self, screen, _name, interface):
        version = ""
        for char in SL_VERSION:
            version += char + " "
        version.replace("v ", "v")

        effects = [

            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0, speed=4, no_blink=True),
            Materialize(screen, StaticRenderer(['${7,1}N${2,2}etwork:' ]), 41, 0, signal_acceleration_factor=2),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 51, 0, speed=4),
            Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\t{}'.format(version)]), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),

            CredstickWatcher(screen, interface, start_frame=90),
            Materialize(screen, StaticRenderer(['Welcome, chummer.  Insert your credstick to begin...']), 0, 13, start_frame=95), 
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=95, speed=4, no_blink=False, thread=True), 

        ]

        super(LoadingScene, self).__init__(effects, -1, name=_name)

