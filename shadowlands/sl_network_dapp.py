from shadowlands.sl_dapp import SLDapp
from shadowlands.sl_contract.sloader import SLoader, DappNotFound
from pathlib import Path
import threading
import wget, zipfile, zipimport
import sys, textwrap, os, types, importlib, re, shutil
from subprocess import call, DEVNULL
from shadowlands.utils import filehasher

class SLNetworkDapp(SLDapp):
    def initialize(self):
        pass

    def __init__(self, screen, scene, eth_node, config, dapp_location, destroy_window=None):
        self.dapp_location = dapp_location
        super(SLNetworkDapp, self).__init__(screen, scene, eth_node, config, destroy_window=None)
        self.show_wait_frame()
        threading.Thread(target=self.run_network_dapp, args=[self.dapp_location]).start()
        #self.run_network_dapp(self.dapp_location)

    def run_network_dapp(self, dapp_target):
        self.sloader_contract = SLoader(self.node)
        try:
            uri, checksum = self.sloader_contract.package(dapp_target)
        except DappNotFound:
                self.hide_wait_frame()
                self.add_message_dialog("Could not find dapp at that address/name.")
                return

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
                self.hide_wait_frame()
                self.add_message_dialog("Could not download dapp URI.  Aborting.")
                return
            if checksum != filehasher(str(app_zipfile)):
                self.hide_wait_frame()
                self.add_message_dialog("Checksum did not match dapp.  Aborting.")
                return

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
                pipbin = Path.home().joinpath('.shadowlands').joinpath('bin').joinpath('pip')
                call([str(pipbin), 'install'] + reqs, stdout=DEVNULL)

            except Exception as e:
                # Our dependencies were not installed, we have to scrap the file and try again next time.
                os.remove(str(app_zipfile))
                self.hide_wait_frame()
                self.add_message_dialog("Error while gathering dependencies.")
                return

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
            self.add_message_dialog("Possible module name conflict.")
            self.hide_wait_frame()
            return

        self.hide_wait_frame()

        Dapp(
            self._screen, 
            self._scene, 
            self._node,
            self._config,
            self._price_poller
        )


