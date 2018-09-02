class ContractConfigError(Exception):
    pass

class OpenContractError(Exception):
    pass

class NonStandardContractDecimalsError(Exception):
    pass

node = None

class Contract():

    networkDict = {
        '1': 'MAINNET',
        '2': 'MORDEN',
        '3': 'ROPSTEN',
        '4': 'RINKEBY',
        '42': 'KOVAN'
    }

    _contract = None


    @classmethod
    def load(cls, network = 'MAINNET'):
        try:
            _address = cls.__dict__[cls.networkName()]
        except:
            raise ContractConfigError('Could not find that contract definition for the current network.')

        try:
            cls._contract = cls.node.w3.eth.contract(_address, abi=cls.ABI)
        except:
            raise OpenContractError('Could not open the Dapp contract')

    
    @classmethod
    def networkName(cls):
        network = cls.node.w3.version.network
        if network is None:
            raise Exception
        return cls.networkDict[network]


