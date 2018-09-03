from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from tui.effects.widgets import SendBox, QuitDialog
from tui.errors import ExitTuiError
from tui.debug import debug

class MainMenuListener(Effect):
    def __init__(self, screen, interface, **kwargs):
        super(MainMenuListener, self).__init__(screen, **kwargs)
        self._interface = interface

    def _update(self, frame_no):
        pass
        #if self._interface.credstick != None:
        #    raise NextScene("Main")

    def reset(self):
        pass


    def stop_frame(self):
        pass
 
    def process_event(self, event):

        if type(event) != KeyboardEvent:
            return event

        # if event.key_code == -1:    # esc.  for some reason esc has lag.

        # Q, q for quit
        if event.key_code in [113, 81]:
            self._scene.add_effect(QuitDialog(self._screen))
        # S, s  for send
        elif event.key_code in [115, 83]:
            self._scene.add_effect(SendBox(self._screen, self._interface))
        else:
            return None
