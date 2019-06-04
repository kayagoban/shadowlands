from shadowlands.sl_dapp import SLDapp, SLFrame

from decimal import Decimal

from shadowlands.tui.debug import debug
import pdb

from shadowlands.sl_config import (
    DuplicateTokenError, 
    UnallowedTokenRemovalError, 
    NoTokenMatchError
)
from shadowlands.sl_contract.erc20 import Erc20
from shadowlands.sl_contract import ContractConfigError
from web3.exceptions import BadFunctionCallOutput

from shadowlands.uniswap.exchange import Exchange, ExchangeNotFound

class TokenUniswapper(SLDapp):

    def initialize(self):
        # List comprehension join. wheeee!
        # Such demeter's law, very undebug
        tokens = self.config.tokens(self.node.network)
        self.balances =  [{'name': x[0], 'address': x[1],'balance': y['balance']} for x in tokens for y in self.node.erc20_balances if x[0] == y['name'] ]
        height = 6+len(self.balances)
        self.selected_token = None
        self.add_frame(TokenFrame, height=height, width=40, title='Choose token to swap')

class TokenFrame(SLFrame):

    def initialize(self):
        self.add_label(
            "Token           ║ Balance",
            add_divider=False
        )
        self.add_label(
            "                ║",
            add_divider=False
        )

 
        options = [
            (
                "{} ║ {}".format(i['name'].ljust(15, ' '), str(i['balance'])[0:18]),
                i
            ) for i in self.dapp.balances]

        self.tokens_list = self.add_listbox(len(self.dapp.balances), options, on_change=self.select_token, on_select=self.trade)

        self.add_button_row([
            ("Back", self.close, 1)
        ],
        layout=[1, 1])

    def trade_lambda(self, token):
        return lambda: self.trade(token)

    def trade(self):
        token = self.dapp.selected_token
        try:
            self.dapp.add_uniswap_frame(token['address'])
        except ExchangeNotFound:
            self.dapp.add_message_dialog("There's no uniswap exchange for that token")
            return
        self.close()

   
    def select_token(self):
        self.dapp.selected_token = self.tokens_list()

    def token_detail(self):
        self.dapp.add_frame(TokenDetail, height=10, width=46, title=self.dapp.selected_token['name'])



class TokenDetail(SLFrame):
    def initialize(self):
        token = self.dapp.selected_token
        self.add_label("Symbol: {}".format(token['name']))
        self.add_label("Address:", add_divider=False)
        self.add_label(token['address'])
        self.add_label("Balance: {}".format(token['balance'].__str__()[0:18]))
        self.add_button_row([
            ("Uniswap", lambda: self.trade(token), 0),
            ("Remove", self.remove_token, 1),
            ("Back", self.close, 2)
        ], 
        layout=[3, 3, 3])
 
    def trade(self, token):
        self.dapp.add_uniswap_frame(token['address'])
        self.close()

    def remove_token(self):
        self.dapp.add_frame(RemoveTokenFrame, height=5, width=42, title='Remove Token')
        self.close()




