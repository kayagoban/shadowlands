import json
#import web3
from solc import compile_source
#from web3.contract import ConciseContract
import pyperclip
import pdb
from shadowlands.sl_dapp import SLDapp

#pdb.set_trace()


class Deployer(SLDapp):
    FILEPATH='shadowlands/sloader.sol'

    def initialize(self):
        contract_source_code = open(self.FILEPATH, 'r').read()
        compiled_sol = compile_source(contract_source_code, optimize=True) # Compiled source code
        contract_interface = compiled_sol['<stdin>:SLoader']
        SLoader = self.node.w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

        # copy abi to the clipboard
        pyperclip.copy(str(contract_interface['abi']))

        self.add_transaction_dialog(
            lambda: SLoader.constructor(),
            title="Deploy",
            gas_limit=900000
        )


