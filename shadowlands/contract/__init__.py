
class ContractConfigError(Exception):
    pass

class InvalidW3Error(Exception):
    pass


class Contract():
    def __init__(self, node, address=None, provided_abi=None):
        self._contract = None
        self._node = node

        if not self._node._w3.isConnected():
            raise InvalidW3Error('w3 is not connected in the node you passed in to the Contract constructor')

        try:
            if address is None:
                address = self.__class__.__dict__[node.network_name.upper()]
                if address is '':
                    raise
        except:
            raise ContractConfigError(
                'No address given for contract on this network.  Did you set the address constant for {}?'.format(
                    node.network_name.upper()
                )
            )

        # If on MAINNET, Attempt to resolve
        try:
            # This is the best way to verify the hex string address is actually an address.
            address = node.w3.toChecksumAddress(address)
        except ValueError:
            # if on mainnet, we can attempt to resolve the address if this is really an ENS name.
            if node.network_name.upper() == 'MAINNET':
                address = node.ens.address(address)
                if address is None:
                    raise ContractConfigError('Attempt to resolve contract address from ENS failed.')
            else:
                raise ContractConfigError("Given contract address '{}' does not appear to be valid.".format(address))

        if self.ABI is None and provided_abi is None:
            raise ContractConfigError('Could not open the Dapp contract with the given address and ABI.')

        if provided_abi is None:
            self._contract = node.w3.eth.contract(address, abi=self.ABI)
        else: 
            self._contract = node.w3.eth.contract(address, abi=provided_abi)

        if self._contract == None:
            raise ContractConfigError('Could not open the Dapp contract with the given address and ABI.')

    @property
    def w3(self):
        return self._node.w3
   
    @property
    def sha3(self):
        return self._node.w3.sha3

    @property
    def functions(self):
        return self._contract.functions

    @property
    def address(self):
        return self._contract.address 

    def toWei(self, amount, denomination):
        return self._node.w3.toWei(amount, denomination)

    def fromWei(self, amount, denomination):
        return self._node.w3.fromWei(amount, denomination)

    
    
