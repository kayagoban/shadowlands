from shadowlands.credstick import Credstick

class MockEthDriver(Credstick):

    @classmethod
    def open(cls):
        cls.manufacturerStr = "Soykaf Digital"
        cls.productStr = "MockStick 3000"
 
    @classmethod
    def derive(cls, hdpath_base="44'/60'/0'", hdpath_index='0', set_address=False):
        cls.address = Credstick.mock_address
        cls.hdpath_base = hdpath_base 
        cls.hdpath_index = hdpath_index
        return Credstick.mock_address

    @classmethod
    def close(cls):
        pass

    @classmethod
    def signTx(cls, transaction_dict):
        raise Exception("Mockstick cannot sign Txs")

