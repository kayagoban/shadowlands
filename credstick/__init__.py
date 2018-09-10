import hid

# TODO
# fork eth-account and eth-keys repos from the Web3.py project and 
# submit a PR to make this all a subsystem of web3

class NoCredstickFoundError(Exception):
    pass

class DeriveCredstickAddressError(Exception):
    pass

class OpenCredstickError(Exception):
    pass

class CloseCredstickError(Exception):
    pass

class SignTxError(Exception):
    pass



class Credstick(object):
    _driver = None
    manufacturerStr = None
    productStr = None
    address = None

    @classmethod
    def addressStr(cls):
        return '0x' + cls.address.decode('ascii')

    @classmethod
    def heartbeat(cls):
        return

    # For implementation of Trezor:
    # satoshi labs vendor id: '0x534c'
    # usage pages '0xf1d0', '0xff00'
    @classmethod
    def detect(cls):
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice['vendor_id'] == 0x2c97:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == 0) or ('usage_page' in hidDevice and hidDevice['usage_page'] == 0xffa0):
                    hidDevicePath = hidDevice['path']
                    if hidDevicePath is not None:
                        from credstick.ledger_ethdriver import LedgerEthDriver
                        return LedgerEthDriver

        raise NoCredstickFoundError("Could not identify any supported credstick")

    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def close(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def heartbeat(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def derive(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def signTx(cls, tx):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)


