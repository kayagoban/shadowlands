from credstick import Credstick, DeriveError
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException


# import pdb; pdb.set_trace()

class LedgerEthDriver(Credstick):

    @classmethod
    def open(cls):
        cls._driver = getDongle(False)
        cls.manufacturerStr = cls._driver.device.get_manufacturer_string()
        cls.productStr = cls._driver.device.get_product_string()

    @classmethod
    def close(cls):
        cls._driver.device.close()

    @classmethod
    def derive(cls):
        try:
            result = cls._driver.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
            offset = 1 + result[0]
            cls.address = result[offset + 1 : offset + 1 + result[offset]]
        except(CommException, IOError):
            raise DeriveError("Could not derive an address from your credstick, user.")
        return cls.addressStr()

       
