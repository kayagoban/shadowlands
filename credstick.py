from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException

address = None

class AddressError(Exception):
    pass

def getAddress():
    global address

    try:
        dongle = getDongle(False)
        result = dongle.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
        offset = 1 + result[0]
        address = result[offset + 1 : offset + 1 + result[offset]]
    except(CommException, IOError):
        raise AddressError("Could not get an address from your credstick, chummer.")



def ledgerEthAddress():
    dongle = getDongle(False)
    result = dongle.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]
    return address
