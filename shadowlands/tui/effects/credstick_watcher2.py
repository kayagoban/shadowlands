from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from shadowlands.credstick import Credstick
import logging
#from shadowlands.tui.scenes.loading import LoadingScene

# This effect does nothing but watch the credstick
# to see when it is removed.

# There is almost certainly a better way to do this,
# but it's not possible to raise an error from a 
# separate thread.  Hence the hack.

class CredstickWatcher2(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(CredstickWatcher2, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        if self._interface._credstick_removed:
        #if not self._interface.credstick or not self._interface.node.w3 or self._interface.node.erc20_balances is None:
            logging.debug("credstick removed - switching back to Loading Scene")
            #self._screen._scenes = []
            #self._interface._loading_scene = True
            self._interface._credstick_removed = False
            raise NextScene("LoadingScene")

    def reset(self):
        pass


    def stop_frame(self):
        pass

    def process_event(self, event):
        return event


