from abc import ABC, abstractmethod
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button
from asciimatics.exceptions import NextScene
from asciimatics.scene import Scene
from tui.effects.widgets import MessageDialog

class SLDapp(ABC):
    def __init__(self, eth_node):
        self._node = eth_node
        self._screen = None
        self._scenes = []

    # This is called by the Shadowlands application
    def tui(self, screen):
        self._screen = screen
        self.initialize()
        screen.play(self._scenes, stop_on_resize=True)

    @property
    def node(self):
        return self._node

    @abstractmethod
    def initialize(self):
        pass

    def add_frame(self, cls, name=None, height=None, width=None, title=None):
        # we are actually adding scenes, one frame object (effect) per scene.  asciimatics can do a lot more
        # than this, but we're hiding away the functionality for the sake of simplicity.
        self._scenes.append(
           Scene([cls(self, height, width, title=title)], -1, name=name)
        )




class SLFrame(Frame):
    def __init__(self, dapp, height, width, **kwargs):
        self._dapp = dapp
        self._screen = dapp._screen

        super(SLFrame, self).__init__(self._screen,
                                      height,
                                      width,
                                      can_scroll=False,
                                      is_modal=True,
                                      **kwargs)
                                      #hover_focus=True,
        self.set_theme('shadowlands')
        self.initialize()
        self.fix()


    def add_ok_cancel_buttons(self, ok_fn, cancel_fn):
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button("OK", ok_fn), 0)
        layout.add_widget(Button("Cancel", cancel_fn), 3)
 
    # named arguments will be passed on to the asciimatics Text() constructor
    def add_textbox(self, name, label_text, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        text_widget = Text(label_text, name, **kwargs)
        layout.add_widget(text_widget)
        layout.add_widget(Divider(draw_line=False))
        return lambda: text_widget._value
         
    def add_message_dialog(self, message, next_frame):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, destroy_window=None, next_scene=next_frame))




class ExitDapp(Exception):
    pass

class NextFrame(NextScene):
    pass

class RunDapp(Exception):
    pass

