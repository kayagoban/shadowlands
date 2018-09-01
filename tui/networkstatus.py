from tui.effects.cursor import Cursor
from asciimatics.renderers import DynamicRenderer

#debug(self._screen._screen); import pdb; pdb.set_trace()

class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        return ['Network: ' + self.node.networkName()], None


class NetworkStatusCursor(Cursor):
    def __init__(self, screen, node, x, y, **kwargs):
        super(NetworkStatusCursor, self).__init__(screen, NetworkStatusRenderer(node), x, y, **kwargs)

