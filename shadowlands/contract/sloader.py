from shadowlands.contract import Contract
from web3.exceptions import ValidationError, NameNotFound
from eth_utils import decode_hex, encode_hex

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



