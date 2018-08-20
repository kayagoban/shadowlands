from credstick import Credstick
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException


# import pdb; pdb.set_trace()

class AddressError(Exception):
    pass

class LedgerEthDriver(Credstick):

    address = None

    @classmethod
    def derive(cls):
        try:
            #        import pdb; pdb.set_trace()
            dongle = getDongle(False)
            result = dongle.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
            offset = 1 + result[0]
            cls.address = result[offset + 1 : offset + 1 + result[offset]]
        except(CommException, IOError):
            raise AddressError("Could not get an address from your credstick, chummer.")
        return cls.addressStr()

       
    @classmethod
    def addressStr(cls):
        return '0x' + cls.address.decode('ascii')
 
