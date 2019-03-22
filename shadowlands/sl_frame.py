from asciimatics.event import KeyboardEvent, MouseEvent

from asciimatics.exceptions import NextScene

from asciimatics.widgets import (
    Frame, ListBox, Layout, Divider, Text, Button, Label, FileBrowser, RadioButtons, CheckBox, QRCode
)

import pyperclip


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


    # Ctrl-d drops you into a pdb session.
    # look around, have fun.
    # executing the next line will get you back to the dapp.
    def process_event(self, event):
        if isinstance(event, MouseEvent):
            return None

        if event.key_code is 4:
            # drop to debug console
            debug(); pdb.set_trace()
            # go back to the dapp
            end_debug(); raise NextScene(self._scene.name)

        return super(SLFrame, self).process_event(event)


    def add_button(self, ok_fn, text, layout_distribution=[100], layout_index=0, add_divider=True):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        layout.add_widget(Button(text, ok_fn), layout_index)
        if add_divider:
            layout.add_widget(Divider(draw_line=False))

    def add_qrcode(self, data):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(QRCode(data))

    def add_checkbox(self, text, on_change=None, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        box = CheckBox(text, None, None, on_change, **kwargs)
        layout.add_widget(box)
        return lambda: box._value

    def add_ok_cancel_buttons(self, ok_fn, cancel_fn=None, ok_text="OK", cancel_text="Cancel", ok_index=0, cancel_index=3):
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button(ok_text, ok_fn), ok_index)
        if cancel_fn is None:
            cancel_fn = self.close
        layout.add_widget(Button(cancel_text, cancel_fn), cancel_index)
 
    # named arguments will be passed on to the asciimatics Text() constructor
    def add_textbox(self, label_text, default_value=None, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        text_widget = Text(label_text, **kwargs)
        if default_value is not None:
            text_widget._value = default_value
        layout.add_widget(text_widget)
        layout.add_widget(Divider(draw_line=False))
        return lambda: text_widget._value

    def add_divider(self, draw_line=False, **kwargs):
        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Divider(draw_line=draw_line, **kwargs))

    def add_radiobuttons(self, options, default_value=None, layout_distribution=[100], layout_index=0, **kwargs):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        radiobuttons_widget = RadioButtons(options, **kwargs)
        layout.add_widget(radiobuttons_widget, layout_index)
        layout.add_widget(Divider(draw_line=False))
        if default_value is not None:
            radiobuttons_widget._value = default_value
        return lambda: radiobuttons_widget.value


    def add_listbox(self, height, options, on_select=None, layout_distribution=[100], layout_index=0, **kwargs):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        list_widget = ListBox(height, options, on_select=on_select, **kwargs)
        layout.add_widget(list_widget, layout_index)
        layout.add_widget(Divider(draw_line=False))
        return lambda: list_widget.value
         
    def add_label(self, label_text, layout_distribution=[100], layout_index=0, add_divider=True):
        layout = Layout(layout_distribution)
        self.add_layout(layout)
        layout.add_widget(Label(label_text), layout_index) 
        if add_divider:
            layout.add_widget(Divider(draw_line=False))

    def add_label_pair(self, label0_text, label1_text, add_divider=True):
        layout = Layout([1, 1])
        self.add_layout(layout)
        layout.add_widget(Label(label0_text), 0) 
        layout.add_widget(Label(label1_text), 1) 
        if add_divider:
            layout.add_widget(Divider(draw_line=False))

    def add_label_quad(self, label0_text, label1_text, label2_text, label3_text, add_divider=True):
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Label(label0_text), 0) 
        layout.add_widget(Label(label1_text), 1) 
        layout.add_widget(Label(label2_text), 2) 
        layout.add_widget(Label(label3_text), 3) 
        if add_divider:
            layout.add_widget(Divider(draw_line=False))


    def add_file_browser(self, on_select_fn, path='/', height=15, on_change_fn=None):
        layout = Layout([100])
        self.add_layout(layout)
        browser = FileBrowser(height, path, on_select=on_select_fn, on_change=on_change_fn)
        layout.add_widget(browser)
        layout.add_widget(Divider(draw_line=False))
        return lambda: browser._value

    def close(self):
        self._destroy_window_stack()
        raise NextScene(self._scene.name)

    @property
    def dapp(self):
        return self._dapp




class SLWaitFrame(SLFrame):
    def initialize(self):
        self.add_label(self.message)

    def __init__(self, dapp, wait_message, height, width, **kwargs):
        self.message = wait_message
        super(SLWaitFrame, self).__init__(dapp, height, width, **kwargs)

    def process_event(self, event):
        # Swallows every damn event while the user twiddles his thumbs
        return None


 
class AskClipboardFrame(SLFrame):
    def initialize(self):
        self.add_ok_cancel_buttons(self._copy_digest, cancel_fn=self.close)
    def _copy_digest(self):
        pyperclip.copy(self.dapp.rx)
        self.dapp.rx = None
        self.close()


