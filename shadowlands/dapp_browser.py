from shadowlands.sl_dapp import SLDapp, SLFrame
from asciimatics.widgets import Layout, Label, Button
from shadowlands.tui.effects.widgets import LiveLabel

class DappBrowser(SLDapp):

    def initialize(self):
        self.add_frame(DappBrowserFrame, height=15, width=60, title="Local Dapps")

class DappBrowserFrame(SLFrame):
    def initialize(self):
        self.add_label("dapps directory:")
        self.add_path_selector(self._select_fn, "Change")

    def _select_fn(self):
        self.dapp.add_frame(DirPickerFrame, height=21, width=74, title="Choose local Dapp directory")

    def add_path_selector(self, button_fn, text):
        layout = Layout([80, 20])
        self.add_layout(layout)
        layout.add_widget(Label(lambda: self.dapp.config.sl_dapp_path), 0)
        layout.add_widget(Button(text, button_fn), 1)
 

class DirPickerFrame(SLFrame):
    def initialize(self):
        self.browser_value = self.add_file_browser(self._select_fn, path=self.dapp.config.sl_dapp_path, height=17)
        self.add_ok_cancel_buttons(self._select_fn, ok_text="Select")

    def _select_fn(self):
        self.dapp.config.sl_dapp_path = self.browser_value()
        self.close()
        #self.dapp.add_message_dialog(self.browser_value())


