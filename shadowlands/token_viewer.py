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

from shadowlands.uniswap.exchange import Exchange

class TokenViewer(SLDapp):

    def initialize(self):
        self.balances = self.node.erc20_balances
        self.selected_token = None
        height = 6+len(self.balances)
        self.add_frame(TokenFrame, height=height, width=40, title='ERC20 Tokens')

class TokenFrame(SLFrame):

    def initialize(self):
        tokens = self.dapp.config.tokens(self.dapp.node.network)

        # List comprehension join. wheeee!
        balances =  [{'name': x[0], 'address': x[1],'balance': y['balance']} for x in tokens for y in self.dapp.balances if x[0] == y['name']]

        self.add_label(
            "Token           ║ Balance",
            add_divider=False
        )
        self.add_label(
            "                ║",
            add_divider=False
        )

 
        #self.add_divider(draw_line=True)
        #self.add_divider()
        options = [
            (
                "{} ║ {}".format(i['name'].ljust(15, ' '), str(i['balance'])[0:18]),
                i
            ) for i in balances]

        self.tokens_list = self.add_listbox(len(balances), options, on_change=self.select_token, on_select=self.token_detail)

        #for i in balances:
        #    name = i['name'].ljust(7, ' ')
        #    self.add_label_with_button(
        #        "{} ║ {}".format(name, round(i['balance'], 7)),
        #        "Trade {}".format(i['name']),
        #        self.trade_lambda(i),
        #        add_divider=False,
        #        layout_distribution=[55, 45]
        #    )

        #self.add_divider()
        self.add_button_row([
            #("Uniswap", self.trade_lambda(tokens_list), 0),
            ("Select", self.token_detail, 0),
            ("Add Token", self.add_token, 1),
            ("Back", self.close, 2)
        ],
        layout=[3, 4, 3])

    def trade_lambda(self, token):
        return lambda: self.trade(token)

   
    def add_token(self):
        self.dapp.add_frame(AddTokenFrame, height=7, width=57, title='Add Token')
        self.close()

    def select_token(self):
        self.dapp.selected_token = self.tokens_list()

    def token_detail(self):
        self.dapp.add_frame(TokenDetail, height=10, width=46, title=self.dapp.selected_token['name'])
        #self.close()



class TokenDetail(SLFrame):
    def initialize(self):
        token = self.dapp.selected_token
        self.add_label("Symbol: {}".format(token['name']))
        self.add_label("Address:", add_divider=False)
        self.add_label(token['address'])
        #debug(); pdb.set_trace()
        self.add_label("Balance: {}".format(token['balance'].__str__()[0:18]))
        self.add_button_row([
            ("Uniswap", lambda: self.trade(token), 0),
            ("Remove", self.remove_token, 1),
            ("Back", self.close, 2)
        ], 
        layout=[3, 3, 3])
 
    def trade(self, token):
        #debug(); pdb.set_trace()
        #token = token._value
        self.dapp.add_uniswap_frame(token['address'])
        self.close()

    def remove_token(self):
        self.dapp.add_frame(RemoveTokenFrame, height=5, width=42, title='Remove Token')
        self.close()




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





