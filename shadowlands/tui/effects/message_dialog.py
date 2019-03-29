from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from asciimatics.exceptions import NextScene

class MessageDialog(Frame):
    def __init__(self, screen, message, height=3, width=30, next_scene="Main", **kwargs):
        super(MessageDialog, self).__init__(screen, height, width, has_shadow=True, is_modal=True, name="message", title=message, can_scroll=False,  **kwargs)
        self._next_scene = next_scene
        self.set_theme('shadowlands')

        layout2 = Layout([100], fill_frame=True)
        self.add_layout(layout2)

        layout2.add_widget(Divider(draw_line=False))
        layout2.add_widget(Button("Ok", self._cancel), 0)
        self.fix()

    def _cancel(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)
        #self._scene.reset()
        #raise NextScene(self._next_scene)


