

class ContractConfigError(Exception):
    pass

class OpenContractError(Exception):
    pass

class InvalidW3Error(Exception):
    pass


class Contract():

    def __init__(self, node, provided_address=None, provided_abi=None):
        self._contract = None
        self._node = node

        if not self._node._w3.isConnected():
            raise InvalidW3Error('w3 is not connected in the node you passed in to the Contract constructor')

        try:
            if provided_address is None:
                address = self.__class__.__dict__[node.network_name.upper()]
            else:
                address = provided_address 
        except:
            raise ContractConfigError('Could not find a contract address for the current network.')

        try:
            if provided_abi is None:
                self._contract = node.w3.eth.contract(address, abi=self.ABI)
            else: 
                self._contract = node.w3.eth.contract(address, abi=provided_abi)
        except:
            raise OpenContractError('Could not open the Dapp contract with the given address and ABI.')

    @property
    def w3(self):
        return self._node.w3
   
    @property
    def sha3(self):
        return self._node.w3.sha3

    @property
    def functions(self):
        return self._contract.functions

    def toWei(self, amount, denomination):
        return self._node.w3.toWei(amount, denomination)

    def fromWei(self, amount, denomination):
        return self._node.w3.fromWei(amount, denomination)
    
