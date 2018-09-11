
class ContractConfigError(Exception):
    pass

class OpenContractError(Exception):
    pass

class InvalidW3Error(Exception):
    pass


class Contract():

    def __init__(self, node):
        self._contract = None
        self._node = node

        if not _w3.isConnected():
            raise InvalidW3Error('w3 is not connected in the node you passed in to the Contract constructor')


        #try:
        address = cls.__dict__[node.networkName().upper()]
        #except:
        #    raise ContractConfigError('Could not find a contract address for the current network.')

        #try:
        self._contract = node.w3.eth.contract(address, abi=cls.ABI)
        #except:
        #    raise OpenContractError('Could not open the Dapp contract with the given address and ABI.')

    @property
    def w3(self):
        return self._node.w3

