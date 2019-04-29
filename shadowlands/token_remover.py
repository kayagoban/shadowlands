from shadowlands.sl_dapp import SLDapp, SLFrame

#from decimal import Decimal

#from shadowlands.tui.debug import debug
#import pdb

from shadowlands.sl_config import (
    DuplicateTokenError, 
    UnallowedTokenRemovalError, 
    NoTokenMatchError
)
from shadowlands.contract.erc20 import Erc20
from shadowlands.contract import ContractConfigError
from web3.exceptions import BadFunctionCallOutput

#from shadowlands.uniswap.exchange import Exchange

class TokenRemover(SLDapp):

    def initialize(self):
        self.add_frame(RemoveTokenFrame, height=5, width=42, title='Remove Token')


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
            self.dapp.add_message_dialog("Removed Token.")
        except NoTokenMatchError:
            self.dapp.add_message_dialog("No matching token found to delete.")

        self.close()





