from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.contract import Contract
from shadowlands.contract.sloader import SLoader
from shadowlands.utils import filehasher

from eth_utils import decode_hex
import wget, hashlib
from shadowlands.tui.debug import debug
import pdb

class ReleaseVersion(SLDapp):
    def initialize(self):
        self.sloader_contract = SLoader(self.node)
        self.add_frame(ReleaseFrame, height=5, width=75, title='New Shadowlands Release')

class ReleaseFrame(SLFrame):
    def initialize(self):
        self.uri = self.add_textbox("URI:")
        self.checksum = self.add_textbox("SHA256:")
        self.add_ok_cancel_buttons(self.ok_choice, lambda: self.close())

    def ok_choice(self):
        #sl_zipfile = wget.download(self.url(), out="/tmp", bar=False)
        shasum = self.checksum()
        
        self.dapp.add_transaction_dialog(
            tx_fn=lambda: self.dapp.sloader_contract.register_package(
                shasum,
                self.uri()
            ),
            destroy_window=self
        )

