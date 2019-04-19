from shadowlands.sl_dapp import SLDapp, SLFrame

from decimal import Decimal

from shadowlands.tui.debug import debug
import pdb

from shadowlands.sl_config import (
    DuplicateTokenError, 
    UnallowedTokenRemovalError, 
    NoTokenMatchError
)
from shadowlands.contract.erc20 import Erc20
from shadowlands.contract import ContractConfigError
from web3.exceptions import BadFunctionCallOutput

class TokenViewer(SLDapp):

    def initialize(self):
        self.balances = self.node.erc20_balances
        height = 4+len(self.balances)
        self.add_frame(TokenFrame, height=height, width=71, title='Tokens')

class TokenFrame(SLFrame):

    def initialize(self):
        tokens = Erc20.tokens(self.dapp.node.network) + self.dapp.config.tokens(self.dapp.node.network)

        # List comprehension join. wheeee!
        balances =  [{'name': x[0], 'address': x[1], 'balance': y['balance']} for x in tokens for y in self.dapp.balances if x[0] == y['name']]


        for i in balances:
            name = i['name'].ljust(7, ' ')
            self.add_label(
                "{} ║ {} ║ {}".format(name, i['address'], i['balance']),
                add_divider=False
            )

        self.add_divider()
        self.add_button_row([
            ("Add Token", self.add_token, 1),
            ("Remove Token", self.remove_token, 2),
            ("Back", self.close, 3)
        ])

    def add_token(self):
        self.dapp.add_frame(AddTokenFrame, height=7, width=57, title='Add Token')
        self.close()

    def remove_token(self):
        self.dapp.add_frame(RemoveTokenFrame, height=5, width=42, title='Remove Token')
        self.close()


        pass

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





