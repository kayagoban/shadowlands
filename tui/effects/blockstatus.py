from tui.effects.cursor import Cursor
from asciimatics.renderers import DynamicRenderer

#debug(self._screen._screen); import pdb; pdb.set_trace()

class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        if not self.node.syncing:
            images = ['[synced: block ' + self.node.block + ']'
                     ]
        else:
            images = [ '[syncing:  ' + str(self.node.blocksBehind) + ' blocks to ' + str(self.node.syncing['highestBlock']) + ']' ]
        return images, None


class BlockStatusCursor(Cursor):

    def __init__(self, screen, node, x, y, **kwargs):
        super(BlockStatusCursor, self).__init__(screen, BlockStatusRenderer(node), x, y, **kwargs)

    def _update(self, frame_no):
        if frame_no % 100 == 0:
            self.reset()
            
        super(BlockStatusCursor, self)._update(frame_no)
        return


