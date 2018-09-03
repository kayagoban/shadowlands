from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
from tui.effects.widgets import SendBox, QuitDialog
from tui.errors import ExitTuiError

class MainMenuListener(Effect):
    def __init__(self, screen, **kwargs):
        super(MainMenuListener, self).__init__(screen, **kwargs)

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

        # Escape is -1             113 is  q for quit
        if event.key_code == -1:    # or event.key_code == 113:
            self._scene.add_effect(QuitDialog(self._screen))
        # S, s  for send
        elif event.key_code in [115, 83]:
            self._scene.add_effect(SendBox(self._screen))
        else:
            return None
