from asciimatics.widgets import Frame, Layout, Text, Button, CheckBox, Divider, ListBox, RadioButtons, Label
from asciimatics.exceptions import NextScene

# This is a reusable dialog with a text field.
# continue function will be passed the string argument with the value
# of the text field, and this frame object so that it can be referenced
# for later removal.
# like so:
# continue_function(returned_text, text_request_dialog_object)
class TextRequestDialog(Frame):
    def __init__(self, screen, height=10, width=46, label_prompt_text=None, label_height=2, continue_button_text=None, continue_function=None, text_label=None, text_default_value=None, label_align="^", next_scene=None, hide_char=None, title=None, reset_scene=True, **kwargs):
        super(TextRequestDialog, self).__init__(screen, height, width, has_shadow=True, is_modal=True, can_scroll=False, title=title, **kwargs)
        self.set_theme('shadowlands')
        self._continue_function = continue_function
        self._next_scene = next_scene
        self._reset_scene = reset_scene

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Label(label_prompt_text, label_height, align=label_align))
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(Text(text_label, "text_field", default_value=text_default_value, hide_char=hide_char))
 

        layout2 = Layout([1, 1], fill_frame=False)
        self.add_layout(layout2)
        layout2.add_widget(Button(continue_button_text, self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 1)
        self.fix()

    def _ok(self):
        text = self.find_widget('text_field')
        self._continue_function(text._value, self)
        #self._destroy_window_stack()
        if self._reset_scene:
            raise NextScene(self._scene.name)
        #self._scene.remove_effect(self)
        #self._screen.reset()

    def _cancel(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

