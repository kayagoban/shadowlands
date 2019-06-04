from shadowlands.sl_contract import SLContract
from web3.exceptions import ValidationError, NameNotFound
from eth_utils import decode_hex, encode_hex
from shadowlands.tui.debug import debug
import pdb

class DappNotFound(Exception):
    pass

class SLoader(SLContract):
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
        fn = self.functions.registerPackage(decode_hex(checksum.strip()), url.strip())
        return fn

    MAINNET='sloader.shadowlands.eth'
    ABI='''[{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"checksum","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"packages","outputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"checksum","type":"bytes32"},{"name":"uri","type":"string"}],"name":"registerPackage","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"sl_dapp","type":"address"}],"name":"uri","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"}]'''



