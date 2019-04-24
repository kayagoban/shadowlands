from asciimatics.widgets import Text, Layout, Divider
from shadowlands.sl_frame import SLFrame
from shadowlands.uniswap.exchange import Exchange
from shadowlands.tui.debug import debug
import pdb
from shadowlands.contract.erc20 import Erc20
from decimal import Decimal, InvalidOperation


class UniswapFrame(SLFrame):
    def __init__(self, dapp, height, width, token_address, **kwargs):

        self.token = Erc20(dapp.node, address=token_address)
        try:
            self.token_symbol = self.token.symbol()
        except OverflowError:
            self.token = Erc20(
                dapp.node, 
                address=token_address,
                provided_abi=Erc20.DS_TOKEN_ABI
            )
            self.token_symbol = self.token.symbol().rstrip(b'\x00').decode()
        except Exception as e:
            self.token_symbol = '???'

        self.exchange = Exchange(dapp.node, token_address)

        # Dirty flags for updating token and eth text fields
        #self.token_value_dirty_flag = False
        #self.eth_value_dirty_flag = False

        #debug(); pdb.set_trace()

        super(UniswapFrame, self).__init__(dapp, height, width, title="Uniswap Exchange", **kwargs)

    def initialize(self):

        #self.add_label("Using Uniswap {} exchange:".format(self.token_symbol), add_divider=False)
        #self.add_label(self.exchange.address)
        #self.add_label("for {} contract at:".format(self.token_symbol), add_divider=False)
        #self.add_label(self.token.address)

        #result = self.exchange.buy_token_calc_token_output(1000000)
        #self.add_label("Exchange rate: {}/ETH: {}".format(self.token_symbol, round(result[1], 5)))

        self.add_label("ETH liquidity: {}".format( str(round(self.exchange.eth_reserve, 3))))
        self.add_label("{} liquidity: {}".format(self.token_symbol, str(round(self.exchange.token_reserve, 3))))

        options = [
            ("Buy {} for ETH".format(self.token_symbol), 'buy'),
            ("Sell {} for ETH".format(self.token_symbol), 'sell')
        ]

        self.radiobutton_value = self.add_radiobuttons(options, on_change=self.blank_textfields)
    
        layout = Layout([100])
        self.add_layout(layout)
        self.token_amount = TokenValueText(self.radiobutton_value, self.exchange, label="{}:".format(self.token_symbol), on_change=self.token_value_dirty)
        self.eth_amount = EthValueText(self.radiobutton_value, self.exchange, label="ETH:", on_change=self.eth_value_dirty)

        self.token_amount.set_eth_field(self.eth_amount)
        self.eth_amount.set_token_field(self.token_amount)

        layout.add_widget(self.token_amount)
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(self.eth_amount)
        layout.add_widget(Divider(draw_line=False))

        self.add_button_row([("Transact", self.transact, 0), ("Back", self.close, 3)])

    def blank_textfields(self):
        self.token_amount._value = ''
        self.eth_amount._value = ''

    def transact(self):
        if self.radiobutton_value() == 'buy':
            self.buy_token()
        elif self.radiobutton_value() == 'sell':
            self.sell_token()

    def buy_token(self):
        if not self.validate('buy'):
            return

    def sell_token(self):
        if not self.validate('sell'):
            return

    def token_value_dirty(self):
        self.eth_amount.token_value_dirty_flag = True

    def eth_value_dirty(self):
        self.token_amount.eth_value_dirty_flag = True

    def validate(self, action):
        errors = self.errors(action)
        if len(errors) > 0:
            for e in errors:
                self.dapp.add_message_dialog(e)
            return False
        return True


    def errors(self, action):
        errors = []

        # is the amount a decimal?
        try:
            amount = Decimal(self.amount())
        except InvalidOperation:
            errors.append("Invalid Amount given")

        # is the amount > 0?
        if amount <= 0:
            errors.append("Amount must be a positive decimal value")

        try:
            decimals = Decimal(10 ** self.token.decimals())
            amount = amount * decimals
        except: 
            errors.append("Decimal conversion error")

        if action == 'buy':
            eth_cost = self.exchange.eth_cost(amount)
            if eth_cost[0] > self.dapp.node._wei_balance:
                errors.append("You don't have enough Eth to perform transaction")

            if  amount > self.exchange.token_reserve(as_int=False):
                errors.append("Exchange doesn't have enough {} to perform transaction".format(self.token_symbol))

        #elif action == 'sell':
        #    if self.token.my_balance() < amount
        #        errors.append("You don't have enough {} to perform transaction".format(self.token_symbol))
        #
        #    # is there enough ETH liquidity to satisfy transaction?
        #    if self.exchange.token_cost(amount)[0]
        #    #if amount > self.exchange.

        return errors

class TokenValueText(Text):
    def __init__(self, radiobutton, exchange, **kwargs):
        self.eth_value_dirty_flag = False
        self.radiobutton_value = radiobutton
        self.eth_amount = None
        self.exchange = exchange
        super(TokenValueText, self).__init__(**kwargs)

    def set_eth_field(self, textfield):
        self.eth_amount = textfield

    def update(self, frame_no):
        if self.eth_value_dirty_flag:
            try:
                amt = Decimal(self.eth_amount._value)
                if self.radiobutton_value() == 'sell':
                    self._value = round(self.exchange.sell_token_calc_token_input(amt)[0], 7).__str__()
                elif self.radiobutton_value() == 'buy':
                    self._value = round(self.exchange.buy_token_calc_token_output(amt)[0], 7).__str__()
            except InvalidOperation:
                self._value=""
            self.eth_value_dirty_flag = False

        super(TokenValueText, self).update(frame_no)


class EthValueText(Text):
    def __init__(self, radiobutton, exchange, **kwargs):
        self.token_value_dirty_flag = False
        self.radiobutton_value = radiobutton
        self.token_amount = None
        self.exchange = exchange
        super(EthValueText, self).__init__(**kwargs)

    def set_token_field(self, textfield):
        self.token_amount = textfield

    def update(self, frame_no):
        if self.token_value_dirty_flag:
            try:
                amt = Decimal(self.token_amount._value)
                if self.radiobutton_value() == 'sell':
                    self._value = round(self.exchange.sell_token_calc_eth_output(amt)[0], 7).__str__()
                elif self.radiobutton_value() == 'buy':
                    self._value = round(self.exchange.buy_token_calc_eth_input(amt)[0], 7).__str__()
            except InvalidOperation:
                self._value = ""

            self.token_value_dirty_flag = False
        super(EthValueText, self).update(frame_no)

