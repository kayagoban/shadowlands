class DeriveCredstickAddressError(Exception):
    pass

class OpenCredstickError(Exception):
    pass

class CloseCredstickError(Exception):
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


# The rest are unimplemented abstract methods

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
    def signTx(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)


