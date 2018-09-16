

from trezorlib.client import TrezorClient
from trezorlib.transport import enumerate_devices, get_transport
from trezorlib import tools
import binascii

from shadowlands.credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError

'''
from trezorlib import (
    btc,
    cardano,
    coins,
    cosi,
    debuglink,
    device,
    ethereum,
    firmware,
    lisk,
    log,
    messages as proto,
    misc,
    nem,
    ontology,
    protobuf,
    ripple,
    stellar,
    tools,
)
'''

#import pdb; pdb.set_trace()
class TrezorEthDriver(Credstick):

    @classmethod
    def open(cls):
        cls.address = cls.derive()
 
    @classmethod
    def derive(cls, path="44'/60'/0'/0/0"):
        #address = "44'/60'/0'/0"  # ledger so-called standard
        #address = "44'/60'/0'/0/0"  # trezor standard

        device = get_transport(None, prefix_search=False)
        client = TrezorClient(transport=device)
        address_n = tools.parse_path(path)
        address = client.ethereum_get_address(address_n, False)
        cls.address =  binascii.hexlify(address)

        return cls.addressStr()

        #result = "0x%s" % binascii.hexlify(address).decode()
        #return result



#TrezorEthDriver.derive()
