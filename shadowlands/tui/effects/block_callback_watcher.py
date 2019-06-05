from asciimatics.effects import Effect
#from asciimatics.exceptions import NextScene
from shadowlands.tui.debug import debug, end_debug
import pdb


class BlockCallbackWatcher(Effect):
    def __init__(self, screen, interface, **kwargs):
        self.dapps = []
        self.node = interface.node
        self.current_block = interface.node.best_block

        super(BlockCallbackWatcher, self).__init__(screen, **kwargs)

    def _update(self, frame_no):
        new_block = self.node.best_block
        if self.current_block == new_block:
            return
        else:
            self.current_block = new_block
            self.run_callbacks()

    def run_callbacks(self):
        for dapp in self.dapps:
            dapp._new_block_callback()

    def register_dapp(self, dapp):
        self.dapps.append(dapp)

    def unregister_dapp(self, dapp):
        self.dapps.remove(dapp)


    # implementation required by superclass

    def reset(self):
        pass

    def stop_frame(self):
        pass

    def process_event(self, event):
        return event


