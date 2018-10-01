from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.contract import Contract
from eth_utils import decode_hex
import wget, hashlib

class SLoader(Contract):
    def register_package(self, checksum, url):
        fn = self.functions.registerPackage(decode_hex(checksum), url)
        return fn

    #ROPSTEN='0xfa14f7fDD32c13F8548eD9634a7E770516E743D5'
    #MAINNET='0x99AF965b51312C8869FAc5f527F47Af92fCCf83C'
    MAINNET='0x51d0cFa6Fc1bE1Df18cD4EA38c6e45751908c356'
    ABI='''[{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"checksum","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"packages","outputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"name":"registerPackage","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"uri","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]'''



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
            tx_fn=lambda: self.dapp.sloader_contract.register_package(
                shasum,
                self.url()
            ),
            destroy_window=self
        )

