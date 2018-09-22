from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.contract import Contract
from eth_utils import decode_hex
import wget, hashlib

class SLoader(Contract):
    def add_release(self, checksum, url):
        fn = self.functions.addRelease(decode_hex(checksum), url)
        return fn

    ROPSTEN='0xfa14f7fDD32c13F8548eD9634a7E770516E743D5'
    MAINNET='0x99AF965b51312C8869FAc5f527F47Af92fCCf83C'
    ABI='''[{"constant":true,"inputs":[],"name":"latestReleaseUrl","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"index","type":"uint8"}],"name":"releaseChecksum","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"checksum","type":"bytes32"},{"name":"url","type":"string"}],"name":"addRelease","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"index","type":"uint8"}],"name":"releaseUrl","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"releaseCount","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"latestReleaseChecksum","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"}]'''


class ReleaseVersion(SLDapp):
    def initialize(self):
        self.sloader_contract= SLoader(self.node)
        self.add_frame(ReleaseFrame, height=5, width=75, title='New Shadowlands Release')

def filehasher(zipfile):
    hasher = hashlib.sha256()
    with open(zipfile, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
        return hasher.hexdigest()

class ReleaseFrame(SLFrame):
    def initialize(self):
        self.url = self.add_textbox("URL:")
        self.add_ok_cancel_buttons(self.ok_choice, lambda: self.close())

    def ok_choice(self):
        sl_zipfile = wget.download(self.url(), out="/tmp", bar=False)
        shasum = filehasher(sl_zipfile)
        
        self.dapp.add_transaction_dialog(
            tx_fn=lambda: self.dapp.sloader_contract.add_release(
                shasum,
                self.url()
            ),
            destroy_window=self
        )

    def no_choice(self):
        self.dapp.add_transaction_dialog(
            tx_fn=lambda: self.dapp.sloader_contract.add_release(
                "c74160a24c9708c0ccd03a57f565d011ecb8d1321bc9df131f35d4707ea01146",
                "https://github.com/kayagoban/test/releases/download/0.0001a/shadowlands.zip"
            ),
            destroy_window=self
        )
