from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.sl_contract.sloader import SLoader
from shadowlands.utils import filehasher

from eth_utils import decode_hex
import wget, hashlib
from shadowlands.tui.debug import debug
import pdb

class ReleaseVersion(SLDapp):
    def initialize(self):
        self.sloader_contract = SLoader(self.node)
        self.add_sl_frame(ReleaseFrame(self, 7, 77, title='New Shadowlands Release'))

class ReleaseFrame(SLFrame):
    def initialize(self):
        self.uri = self.add_textbox("URI:")
        self.checksum = self.add_textbox("SHA256:")
        self.add_button_row([
            ("Deploy Release", self.ok_choice, 0),
            ("Cancel", self.close, 3)
        ])

    def ok_choice(self):
        #sl_zipfile = wget.download(self.url(), out="/tmp", bar=False)
        shasum = self.checksum()
        
        self.dapp.add_transaction_dialog(
            tx_fn=self.dapp.sloader_contract.register_package(
                shasum,
                self.uri()
            ),
        )
        self.close()

