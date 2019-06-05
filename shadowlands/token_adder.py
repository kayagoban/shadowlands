from shadowlands.sl_dapp import SLDapp, SLFrame

#from decimal import Decimal

#from shadowlands.tui.debug import debug
#import pdb

from shadowlands.sl_config import (
    DuplicateTokenError, 
    UnallowedTokenRemovalError, 
    NoTokenMatchError
)
from shadowlands.sl_contract.erc20 import Erc20
from shadowlands.sl_contract import ContractConfigError
from web3.exceptions import BadFunctionCallOutput

#from shadowlands.uniswap.exchange import Exchange

class TokenAdder(SLDapp):

    def initialize(self):
        self.balances = self.node.erc20_balances
        self.selected_token = None
        self.add_sl_frame(AddTokenFrame(self, 7, 57, title='Add Token'))


class AddTokenFrame(SLFrame):
    def initialize(self):
        self.token_name_value = self.add_textbox("Token Name:")
        self.token_addr_value = self.add_textbox("Address:")
        self.add_button_row([
            ("Add Token", self.add_token, 2),
            ("Back", self.close, 3)
        ])


    def add_token(self):
        if not self.validate(self.token_addr_value()):
            self.dapp.add_message_dialog("Fail: contract failed sanity check.")
            self.close()
            return
        try:
            self.dapp.config.add_token(self.token_name_value(), self.token_addr_value(), self.dapp.node.network)
        except DuplicateTokenError:
            self.dapp.add_message_dialog("Fail: token is already in the list.")

        self.dapp.add_message_dialog("Added {}.".format(self.token_name_value()))
        self.close()

    # Make sure the erc20 is erc20ish
    def validate(self, address):
        try:
            contract = Erc20(self.dapp.node, address=address)
            contract.functions.balanceOf(address).call()
        except (BadFunctionCallOutput, ContractConfigError):
            return False

        return True






class RemoveTokenFrame(SLFrame):
    def initialize(self):
        self.token_name_value = self.add_textbox("Token Name:")
        self.add_button_row([
            ("Remove Token", self.remove_token, 0),
            ("Back", self.close, 3)
        ])

    def remove_token(self):
        try:
            self.dapp.config.remove_token(self.token_name_value(), self.dapp.node.network)
        except UnallowedTokenRemovalError:
            self.dapp.add_message_dialog("That token is hardcoded; you cannot remove it.")
        except NoTokenMatchError:
            self.dapp.add_message_dialog("No matching token found to delete.")

        self.dapp.add_message_dialog("Removed Token.")

        self.close()





