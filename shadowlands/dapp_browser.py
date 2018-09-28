from shadowlands.sl_dapp import SLDapp, SLFrame
from asciimatics.widgets import Layout, Label, Button, Divider, TextBox
from asciimatics.effects import Print
from asciimatics.renderers import StaticRenderer
from pathlib import Path
from shadowlands.tui.debug import debug
import sys, textwrap, os, types, importlib, re
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
        options = self._dapps_in_path
        self._listbox_value = self.add_listbox(4, options, on_select=self._run_dapp)
        self.add_button(self.close, "Cancel", layout_distribution=[80, 20], layout_index=1)

    def _select_dir_fn(self):
        self.dapp.add_frame(DirPickerFrame, height=21, width=70, title="Choose local Dapp directory")

    def add_path_selector(self, button_fn, text):
        layout = Layout([80, 20])
        self.add_layout(layout)
        layout.add_widget(Label(lambda: self.dapp.config.sl_dapp_path), 0)
        layout.add_widget(Button(text, button_fn), 1)
        layout.add_widget(Divider(draw_line=False))

    def _dapps_in_path(self):
        chosen_path = Path(self.dapp.config._sl_dapp_path)
        gl = sorted(chosen_path.glob("*"))
        return [(x.name, x.name) for x in gl if x.is_dir() and self._is_dapp(x) is True]

    def _is_dapp(self, dirpath):
        if not dirpath.joinpath('__init__.py').exists():
            return False
        file_text = open(dirpath.joinpath('__init__.py'), 'r').read()
        if re.search(r'class Dapp', file_text) is not None:
            return True
        return False


    def reload_package(self, package):
        assert(hasattr(package, "__package__"))
        fn = package.__file__
        fn_dir = os.path.dirname(fn) + os.sep
        module_visit = {fn}
        del fn

        def reload_recursive_ex(module):
            importlib.reload(module)

            for module_child in vars(module).values():
                if isinstance(module_child, types.ModuleType):
                    fn_child = getattr(module_child, "__file__", None)
                    if (fn_child is not None) and fn_child.startswith(fn_dir):
                        if fn_child not in module_visit:
                            module_visit.add(fn_child)
                            reload_recursive_ex(module_child)

        return reload_recursive_ex(package)

    def _run_dapp(self):
        dapp_name = self._listbox_value()
        dapp_module = importlib.import_module(dapp_name)

        # we force a reload (twice) in case they just made a change..
        self.reload_package(dapp_module)
        self.reload_package(dapp_module)

        try:
            Dapp = getattr(dapp_module, 'Dapp')
        except AttributeError:
            self.dapp.add_message_dialog("Possible module name conflict.")
            return

        Dapp(
            self.dapp._screen, 
            self.dapp._scene, 
            self.dapp._node,
            self.dapp._config,
            self.dapp._price_poller,
            destroy_window=self
        )

        #import traceback
        #self.dapp.tb_str = traceback.format_exc(limit=10)
        #self.dapp.add_frame(ErrorFrame, height=23, width=80, title="The Dapp exited with an Exception")


class DirPickerFrame(SLFrame):
    def initialize(self):
        self.browser_value = self.add_file_browser(self._select_fn, path=self.dapp.config.sl_dapp_path, height=17)
        self.add_ok_cancel_buttons(self._select_fn, ok_text="Select")

    def _select_fn(self):
        self.dapp.config.sl_dapp_path = self.browser_value()
        self.close()



class ErrorFrame(SLFrame):
    def initialize(self):
        layout = Layout([100])
        self.add_layout(layout)
        text_widget = TextBox(20)
        layout.add_widget(text_widget, 0)
        text_widget._value = self.dapp.tb_str.split('\n')
        layout.add_widget(Button("Ok", self.close))
    #def fix(self):
        #super(ErrorFrame, self).fix()
        #origin = self._canvas.origin
        #dims = self._canvas.dimensions
        #self.dapp._scene.add_effect(Print(self._screen, StaticRenderer([self.dapp.tb_str]), origin[0], origin[1]))


