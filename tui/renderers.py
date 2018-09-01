from asciimatics.renderers import DynamicRenderer


class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        return ['Network: ' + self.node.networkName()], None


class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 40)
        self.node = _node

    def _render_now(self):
        if not self.node.syncing:
            images = ['[synced: block ' + self.node.block + ']'
                     ]
        else:
            images = [ '[syncing:  ' + str(self.node.blocksBehind) + ' blocks to ' + str(self.node.syncing['highestBlock']) + ']' ]
        return images, None



