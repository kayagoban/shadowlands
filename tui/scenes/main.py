from asciimatics.renderers import StaticRenderer
from asciimatics.scene import Scene
from tui.effects.materialize import Materialize
from tui.effects.blockstatus import BlockStatusCursor
from tui.effects.networkstatus import NetworkStatusCursor


#from tui.effects.cursor import LoadingScreenCursor

class MainScene(Scene):
    def __init__(self, screen, _name, node):
        effects = [
            BlockStatusCursor(screen, node, 0, 0, speed=4, no_blink=True),
            NetworkStatusCursor(screen, node, 60, 0, speed=4, no_blink=True)
            #Materialize(screen, FigletText('Shadowlands', 'slant'), 0, 2, signal_acceleration_factor=1.1, start_frame=15),
            #Materialize(screen, StaticRenderer([ 'p u b l i c    t e r m i n a l\t\t\tv0 . 0 1']), 10, 9, signal_acceleration_factor=1.0005,start_frame=35),
            #LoadingScreenCursor(screen, StaticRenderer([PROMPT]), 0, 13, start_frame=75, speed=4, no_blink=False, thread=True)
        ]

        super(MainScene, self).__init__(effects, -1, name=_name)

