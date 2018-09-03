from asciimatics.widgets import Frame, Layout, Text, Button
from asciimatics.exceptions import NextScene
from tui.debug import debug

class SendBox(Frame):
    def __init__(self, screen):
        super(SendBox, self).__init__(screen, 15, 45, has_shadow=True, name="sendbox", title="Send Ether", can_scroll=False)
        self.set_theme('green')

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        address_text = Text("To Address:", "address")
        address_text._value = "0xdeadbeef"
        layout.add_widget(address_text)

        layout2 = Layout([1, 1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("Sign Tx", self._ok), 0)
        layout2.add_widget(Button("Cancel", self._cancel), 3)
        self.fix()

    def _ok(self):
        #self.save()
        self._scene.remove_effect(self)
        raise NextScene("Main")

    def _cancel(self):
        self._scene.remove_effect(self)
        raise NextScene("Main")


