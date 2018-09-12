from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene

# This effect does nothing but watch the credstick
# to see when it is defined.

# There is almost certainly a better way to do this,
# but it's not possible to raise an error from a 
# separate thread.  Hence the hack.

class CredstickWatcher(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(CredstickWatcher, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        if self._interface.credstick != None:
            self._screen._scenes = [self._screen._scenes[1]]
            raise NextScene
            #raise NextScene("Main")

    def reset(self):
        pass


    def stop_frame(self):
        pass
