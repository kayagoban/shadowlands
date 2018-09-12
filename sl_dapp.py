from abc import ABC, abstractmethod
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, Label
from asciimatics.exceptions import NextScene
from asciimatics.scene import Scene
from asciimatics.effects import Effect
from tui.effects.widgets import MessageDialog

class SLDapp(Effect):
    def __init__(self, screen, scene, eth_node):
        self._screen = screen
        self._scene = scene
        self._node = eth_node
        self._active_frame = None
        self.initialize()

    @property
    def node(self):
        return self._node

    @abstractmethod
    def initialize(self):
        pass

    def add_frame(self, cls, height=None, width=None, title=None):
        # we are adding SLFrame effects.  asciimatics can do a lot more
        # than this, but we're hiding away the functionality for the 
        # sake of simplicity.
        self._scene.add_effect(cls(self, height, width, title=title))

    def add_message_dialog(self, message):
        preferred_width= len(message) + 6
        self._scene.add_effect( MessageDialog(self._screen, message, width=preferred_width, destroy_window=None))

    def add_yes_no_dialog(self, question, yes_fn=None, no_frame=None):
        preferred_width= len(question) + 6
        self._scene.add_effect( YesNoDialog(self._screen, question, width=preferred_width, destroy_window=None))

    def quit(self):
        # Remove all owned windows
        self._screen.remove_effect(self)
        raise NextScene

    def _update():
        pass
    def reset():
        pass
    def stop_frame():
        pass



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
         
    def add_label(self, label_text):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Label(label_text)) 
        layout.add_widget(Divider(draw_line=False))

    def close(self):
        self._destroy_window_stack()
        raise NextScene

    @property
    def dapp(self):
        return self._dapp

class ExitDapp(Exception):
    pass

class NextFrame(NextScene):
    pass

class RunDapp(Exception):
    pass

