from shadowlands.contract import Contract
from eth_utils import decode_hex, encode_hex

from shadowlands.sl_dapp import SLDapp, SLFrame
from asciimatics.widgets import Layout, Label, Button, Divider, TextBox
from asciimatics.effects import Print
from asciimatics.renderers import StaticRenderer
from pathlib import Path
import pyperclip

from web3.exceptions import ValidationError, NameNotFound
import wget, zipfile, zipimport

from shadowlands.tui.debug import debug
import sys, textwrap, os, types, importlib, re, shutil, hashlib
import pdb

def filehasher(app_zipfile):
    hasher = hashlib.sha256()
    with open(str(app_zipfile), 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
        return hasher.hexdigest()

class DappNotFound(Exception):
    pass

class SLoader(Contract):
    def package(self, eth_address):
        try:
            try: 
                package = self.functions.packages(eth_address).call()
            except NameNotFound:
                # try tacking an .eth on to the address
                package = self.functions.packages(eth_address + '.eth').call()
        
            uri = package[1]
            checksum = encode_hex(package[0])
        except (ValidationError, NameNotFound):
            raise DappNotFound

        if uri == '' or checksum == '0000000000000000000000000000000000000000000000000000000000000000':
            raise DappNotFound

        return uri, checksum.replace('0x','')


    def register_package(self, checksum, url):
        fn = self.functions.registerPackage(decode_hex(checksum), url)
        return fn

    #ROPSTEN='0xfa14f7fDD32c13F8548eD9634a7E770516E743D5'
    #MAINNET='0x99AF965b51312C8869FAc5f527F47Af92fCCf83C'
    MAINNET='0x51d0cFa6Fc1bE1Df18cD4EA38c6e45751908c356'
    ABI='''[{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"checksum","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"packages","outputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"name":"registerPackage","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"uri","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]'''


class DappBrowser(SLDapp):
    def initialize(self):
        self.dapp_name = None
        self.add_frame(DappMenuFrame, height=8, width=50, title="Dapps Menu")
        self.digest = None

    def _dapps_in_path(self):
        chosen_path = Path(self.config._sl_dapp_path)
        gl = sorted(chosen_path.glob("*"))
        return [(x.name, x.name) for x in gl if x.is_dir() and self._is_dapp(x) is True]

    def _is_dapp(self, dirpath):
        if not dirpath.joinpath('__init__.py').exists():
            return False
        file_text = open(dirpath.joinpath('__init__.py'), 'r').read()
        if re.search(r'class Dapp', file_text) is not None:
            return True
        return False



class DappMenuFrame(SLFrame):
    def initialize(self):
        options = [
            ("Run local dapp", lambda: self.dapp.add_frame(RunLocalDappFrame, height=10, width=50, title="Run local Dapp") ),
            ("Change local dapp directory", lambda: self.dapp.add_frame(DappDirFrame, height=7, width=75, title="Change Dapp Directory") ),
            ("Deploy local dapp to network", lambda: self.dapp.add_frame(DeployChooseDappFrame, height=10, width=61, title="Deploy your Dapp") ),
            ("Run network dapp", lambda: self.dapp.add_frame(RunNetworkDappFrame, height=8, width=71, title="Run network Dapp") ),
        ]
        self._listbox_value = self.add_listbox(4, options, on_select=self._menu_action)
        self.add_button(self.close, "Cancel")

    def _menu_action(self):
        self._listbox_value()()
        self.close()


class DeployChooseDappFrame(SLFrame):
    def initialize(self):
        self.add_label("Your Dapps:")
        options = self.dapp._dapps_in_path
        self._listbox_value = self.add_listbox(4, options, on_select=self._choose_dapp)
        self.add_button(self.close, "Cancel")
 
    def _choose_dapp(self):
        self.dapp.dapp_name = self._listbox_value()
        self.dapp.add_frame(DeployMenuFrame, height=7, width=45, title="Deploy action")
        self.close()
        

class DeployMenuFrame(SLFrame):
    def initialize(self):
        options = [
            ("Create archive", self._create_archive),
            ("Register archive", self._register_archive)
        ]
        self._listbox_value = self.add_listbox(2, options, on_select=self._deploy_action)
        self.add_button(self.close, "Cancel")
 
    def _deploy_action(self):
        self._listbox_value()()

    def _create_archive(self):
        dapp_path = Path(self.dapp.config._sl_dapp_path).joinpath(self.dapp.dapp_name)

        # Remove all cached bytecode, leaving only the code
        pycaches = dapp_path.glob("**/__pycache__")
        for cache in pycaches:
            shutil.rmtree(str(cache))

        archive_path = Path("/tmp").joinpath(self.dapp.dapp_name)
        shutil.make_archive(str(archive_path), 'zip',  self.dapp.config._sl_dapp_path, self.dapp.dapp_name)

        self.dapp.digest = filehasher(str(archive_path)+".zip")   

        #debug(); pdb.set_trace()

        self.dapp.add_frame(AskClipboardFrame, height=3, width=65, title="Archive is in /tmp.  Copy Sha256 digest to clipboard?")
        #self.close()

    def _register_archive(self):
        self.dapp.add_frame(ReleaseFrame, height=7, width=75, title='Register Dapp to current address')
        self.close()

class ReleaseFrame(SLFrame):
    def initialize(self):
        self.sloader_contract = SLoader(self.dapp.node)
 
        self.uri = self.add_textbox("URI:")
        self.checksum = self.add_textbox("SHA256:")
        self.add_ok_cancel_buttons(self.ok_choice, lambda: self.close())

    def ok_choice(self):
        shasum = self.checksum()
        
        self.dapp.add_transaction_dialog(
            tx_fn=lambda: self.sloader_contract.register_package(
                shasum,
                self.uri()
            ),
        )
        self.close()


class AskClipboardFrame(SLFrame):
    def initialize(self):
        self.add_ok_cancel_buttons(self._copy_digest, cancel_fn=self.close)

    def _copy_digest(self):
        pyperclip.copy(self.dapp.digest)
        self.dapp.add_message_dialog("Sha256 digest has been copied to your clipboard")
        self.close()


class NetworkDappSLFrameMixin():
    def run_network_dapp(self, dapp_target):
        self.sloader_contract = SLoader(self.dapp.node)
        try:
            uri, checksum = self.sloader_contract.package(dapp_target)
        except DappNotFound:
                self.dapp.add_message_dialog("Could not find dapp at that address/name.")
                self.close()

        # check to see if anything in the cache meets our requirements.
        shadowlands_cache_dir = Path.home().joinpath(".shadowlands").joinpath("cache")

        app_zipfile = None

        for cached_file in shadowlands_cache_dir.iterdir():
            if checksum == filehasher(cached_file):
                app_zipfile = cached_file
                break

        if app_zipfile is None:

            try:
                app_zipfile = wget.download(uri, out=str(shadowlands_cache_dir), bar=None)
            except:
                self.dapp.add_message_dialog("Could not download dapp URI.  Aborting.")
                self.close()
            if checksum != filehasher(str(app_zipfile)):
                self.dapp.add_message_dialog("Checksum did not match dapp.  Aborting.")
                self.close()

            debug(); pdb.set_trace()

            archive = zipfile.ZipFile(str(app_zipfile), 'r')
            # Assumes only one directory in top of zip, containing dapp.
            top_level = archive.namelist()[0] 

            try:
                requirements = archive.read(top_level + 'requirements.txt')
                reqs = requirements.split()
            except KeyError:
                # No requirements.txt.
                reqs = []

            try:
                for req in reqs:
                    call(['pip','install', '-c', shadowlands_requirements,  req])
            except Exception as e:
                # Our dependencies were not installed, we have to scrap the file and try again next time.
                os.remove(str(app_zipfile))
                self.dapp.add_message_dialog("Error while gathering Shadowlands dependencies.")
                self.close()

            archive.close()
        
        #debug(); pdb.set_trace()
        # app_zipfile exists and all reqs installed.

        importer = zipimport.zipimporter(str(app_zipfile))
        archive = zipfile.ZipFile(str(app_zipfile), 'r')
        module_name = archive.namelist()[0].replace('/', '')
        dapp_module = importer.load_module(module_name)
    
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
            self.dapp._price_poller
        )
        self.close()


class RunNetworkDappFrame(SLFrame, NetworkDappSLFrameMixin):
    def initialize(self):
        self.add_label("Ex: ens.shadowlands, '0x5c27053A642B8dCc79385f47fCB25b5e72348feD'")
        self.textbox_value = self.add_textbox("Dapp location:")
        #self.add_button(self.run, "Download and Run")
        self.add_ok_cancel_buttons(self.run)

    def run(self):
        self.run_network_dapp(self.textbox_value())
        self.close()


class RunLocalDappFrame(SLFrame):
    def initialize(self):
        self.add_label("Your Dapps:")
        options = self.dapp._dapps_in_path
        self._listbox_value = self.add_listbox(4, options, on_select=self._run_dapp)
        self.add_button(self.close, "Cancel")

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


class DappDirFrame(SLFrame):
    def initialize(self):
        self.add_label("Dapps directory:")
        self.add_path_selector(self._select_dir_fn, "Change")
        self.add_button(self.close, "Cancel")

    def _select_dir_fn(self):
        self.dapp.add_frame(DirPickerFrame, height=21, width=70, title="Choose local Dapp directory")
        self.close()

    def add_path_selector(self, button_fn, text):
        layout = Layout([80, 20])
        self.add_layout(layout)
        layout.add_widget(Label(lambda: self.dapp.config.sl_dapp_path), 0)
        layout.add_widget(Button(text, button_fn), 1)
        layout.add_widget(Divider(draw_line=False))


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


