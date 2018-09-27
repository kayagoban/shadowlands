from shadowlands.sl_dapp import SLDapp, SLFrame
from asciimatics.widgets import Layout, Label, Button, Divider
from pathlib import Path
from shadowlands.tui.debug import debug
import pdb

class DappBrowser(SLDapp):
    def initialize(self):
        self.add_frame(DappBrowserFrame, height=15, width=61, title="Run local Dapp")

class DappBrowserFrame(SLFrame):
    def initialize(self):
        self.add_label("Dapps directory:")
        self.add_path_selector(self._select_dir_fn, "Change")
        self.add_divider(draw_line=True)
        self.add_label("Your Dapps:")
        #debug(); pdb.set_trace()
        options = self._dapps_in_path
        '''[
            ("superDapp", "/full/path/to/app1"),
            ("FreeEthGiveawayDapp", "/full/path/blah"),
            ("OtherDApp", "/full/pats/blah"),
            ("AmazongDApp", "/fussll/path/blah")
        ]'''
        self._listbox_value = self.add_listbox(4, options, on_select=self._run_dapp)
        self.add_button(self.close, "Cancel", layout_distribution=[80, 20], layout_index=1)

    def _select_dir_fn(self):
        self.dapp.add_frame(DirPickerFrame, height=21, width=55, title="Choose local Dapp directory")

    def add_path_selector(self, button_fn, text):
        layout = Layout([80, 20])
        self.add_layout(layout)
        layout.add_widget(Label(lambda: self.dapp.config.sl_dapp_path), 0)
        layout.add_widget(Button(text, button_fn), 1)
        layout.add_widget(Divider(draw_line=False))

    def _dapps_in_path(self):
        chosen_path = self.dapp.config._sl_dapp_path
        gl = sorted(chosen_path.glob("*"))
        return [(x.name, x) for x in gl if x.is_dir() and self._is_dapp(x) is True]

    def _is_dapp(self, dirpath):
        return True

    def _run_dapp(self):
        #debug(); pdb.set_trace()
        pass



class DirPickerFrame(SLFrame):
    def initialize(self):
        self.browser_value = self.add_file_browser(self._select_fn, path=self.dapp.config.sl_dapp_path, height=17)
        self.add_ok_cancel_buttons(self._select_fn, ok_text="Select")

    def _select_fn(self):
        self.dapp.config.sl_dapp_path = self.browser_value()
        self._scene.reset()
        self.close()
        #self.dapp.add_message_dialog(self.browser_value())


