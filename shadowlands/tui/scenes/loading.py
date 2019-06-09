from asciimatics.renderers import StaticRenderer, FigletText
from asciimatics.scene import Scene
from shadowlands.tui.effects.materialize import Materialize
from shadowlands.tui.effects.dynamic_cursor import DynamicSourceCursor
from shadowlands.tui.effects.cursor import Cursor
from shadowlands.tui.renderers import BlockStatusRenderer, NetworkStatusRenderer, CredstickNameRenderer
from shadowlands.tui.effects.credstick_watcher import CredstickWatcher
from shadowlands.tui.effects.listeners import LoadingScreenListener
from shadowlands.version import SL_VERSION


class LoadingScene(Scene):
    def __init__(self, screen, _name, interface):
        version = ""
        for char in SL_VERSION:
            version += char + " "
        version = version.replace("v ", "v")

        effects = [
            DynamicSourceCursor(screen, BlockStatusRenderer(interface.node), 0, 0, speed=4, no_blink=True),
            Materialize(screen, StaticRenderer(['${7,1}N${2,2}etwork:' ]), 41, 0, signal_acceleration_factor=2),
            DynamicSourceCursor(screen, NetworkStatusRenderer(interface.node), 51, 0, speed=4),
            Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.0),
            Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\t{}'.format(version)]), 10, 9, signal_acceleration_factor=1.0,),
            DynamicSourceCursor(screen, CredstickNameRenderer(interface, add_padding=False), 0, 13, speed=6, no_blink=False),

            CredstickWatcher(screen, interface),
            LoadingScreenListener(screen, interface)
        ]

        super(LoadingScene, self).__init__(effects, -1, name=_name)

