from asciimatics.effects import Effect
from asciimatics.exceptions import NextScene
from asciimatics.event import KeyboardEvent
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

        # Escape   and q for quit
        if event.key_code == -1 or event.key_code == 113:
            raise ExitTuiError
        else:
            return event
