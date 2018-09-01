from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from tui.effects.materialize import Materialize
from tui.effects.cursor import LoadingScreenCursor
from tui.effects.blockstatus import BlockStatusCursor
from tui.effects.networkstatus import NetworkStatusCursor

PROMPT='''Welcome, chummer.  Insert your credstick to begin...
A credstick, like a Trezor or a Ledger.   You know, what the bakebrains call a 'hardware wallet'. No creds, no joy, dataslave.
If you have cyberware installed in your finger, I guess you could try plugging that in...
Or just keep hitting the enter button.  Have fun with that.'''

class LoadingScene(Scene):
    def __init__(self, screen, name, blockstatus_effect, networkstatus_effect):
        effects = [
            blockstatus_effect,
            networkstatus_effect,
            Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 10, signal_acceleration_factor=1.0005,start_frame=35)
        ]

        super(LoadingScene, self).__init__(effects, -1, name)

