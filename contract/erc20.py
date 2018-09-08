from contract import Contract

class Erc20(Contract):

    @classmethod
    def load(cls, network = 'MAINNET'):
        super().load()
        if cls._contract.functions.decimals().call() != 18:
            raise NonStandardContractDecimalsError('Shadowlands assumes 18 decimal places on ERC20 contracts in its conversion methods.  Refusing to load contract for the safety of the user.')

    @classmethod
    def transfer(cls, destination, value):
        if cls._contract == None:
            cls.load()
        fn = cls._contract.functions.transfer(destination, value)
        return fn
