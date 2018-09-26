from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from shadowlands.credstick import Credstick

# This effect does nothing but watch the credstick
# to see when it is defined.

# There is almost certainly a better way to do this,
# but it's not possible to raise an error from a 
# separate thread.  Hence the hack.

class CredstickWatcher(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(CredstickWatcher, self).__init__(screen, **kwargs)
        self._interface = interface
        self.detect_thread_started = False

    def _update(self, frame_no):
        if not self.detect_thread_started:
            # Now that we have the screen, we can 
            # Start the credstick watcher thread.
            # The trezor needs UI elements, otherwise we could have
            # done this in a better place.
            Credstick.interface = self._interface
            Credstick.eth_node = self._interface._node
            Credstick.start_detect_thread()
            self.detect_thread_started = True


        if self._interface.credstick != None:
            # deleting the loading scene entirely.
            # This makes sure the loading screen does not come back upon resize.
            self._screen._scenes = [self._screen._scenes[1]]
            self._interface._loading_scene = False
            raise NextScene

    def reset(self):
        pass


    def stop_frame(self):
        pass

    def process_event(self, event):
        return None


