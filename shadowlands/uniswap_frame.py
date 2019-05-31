from asciimatics.widgets import Text, Layout, Divider
from shadowlands.sl_frame import SLFrame
from shadowlands.uniswap.exchange import Exchange
from shadowlands.tui.debug import debug, end_debug
import pdb
from shadowlands.sl_contract.erc20 import Erc20
from decimal import Decimal, InvalidOperation


class UniswapFrame(SLFrame):
    def __init__(self, dapp, height, width, token_address, action='', sell_amount='', buy_amount='', **kwargs):
        self.token = Erc20(dapp.node, address=token_address)
        self._action = action
        self._buy_amount = buy_amount
        self._sell_amount = sell_amount

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


        super(UniswapFrame, self).__init__(dapp, height, width, title="Uniswap Exchange", **kwargs)

    def initialize(self):
        self.add_label("ETH liquidity: {}".format( str(round(self.exchange.eth_reserve, 3))), add_divider=False)
        self.add_label("{} liquidity: {}".format(self.token_symbol, str(round(self.exchange.token_reserve, 3))))

        self.add_label("Your ETH balance: {}".format(str(self.dapp.node.eth_balance)[:18]), add_divider=False)
        self.add_label("Your {} balance: {}".format(self.token_symbol, str(self.token.decimal_balance)[:18]))

        options = [
            ("Buy {} with ETH".format(self.token_symbol), 'buy'),
            ("Sell {} for ETH".format(self.token_symbol), 'sell')
        ]

        self.radiobutton_value = self.add_radiobuttons(options, on_change=self.blank_textfields, default_value=self._action)
    
        layout = Layout([100])
        self.add_layout(layout)

        token_default_value = ''
        eth_default_value = ''
        if self._action == 'buy': 
            #debug(); pdb.set_trace()
            token_default_value = str(self._buy_amount)[:14]
            if self._buy_amount is not '':
                eth_default_value = str(self.exchange.buy_token_calc_eth_input(self._buy_amount)[0])[:14]
        elif self._action == 'sell':
            token_default_value = self._sell_amount[:14]
            if self._sell_amount is not '':
                eth_default_value = str(self.exchange.sell_token_calc_eth_output(self._sell_amount)[0])[:14]

        self.token_amount = TokenValueText(self.radiobutton_value, self.exchange, default_value=token_default_value, label="{}:".format(self.token_symbol), on_change=self.token_value_dirty)
        self.eth_amount = EthValueText(self.radiobutton_value, self.exchange, default_value=eth_default_value, label="ETH:", on_change=self.eth_value_dirty)

        self.token_amount.set_eth_field(self.eth_amount)
        self.eth_amount.set_token_field(self.token_amount)

        layout.add_widget(self.token_amount)
        layout.add_widget(Divider(draw_line=False))
        layout.add_widget(self.eth_amount)
        layout.add_widget(Divider(draw_line=False))

        self.add_divider()

        self.add_button_row([("Transact", self.transact, 0), ("Back", self.close, 3)])

    def blank_textfields(self):
        self.token_amount._value = ''
        self.eth_amount._value = ''

    def transact(self):
        if not self.validate(self.radiobutton_value()):
            return

        if self.radiobutton_value() == 'buy':
            # send ether to exchange
            amount = self.dapp.node.w3.toWei(self.eth_amount._value, 'ether')
            self.dapp.add_send_dialog(
                {
                    'to': self.exchange.address,
                    'value': amount,
                    'nonce': self.dapp.node.next_nonce(),
                    'gas': 75000 
                }
            )
            self.close()

        elif self.radiobutton_value() == 'sell':
            token_amount = self.token.convert_to_integer(Decimal(self.token_amount._value)) 
            eth_amount = self.dapp.w3.toWei(self.eth_amount._value, 'ether')

            # check allowance to see if we need to approve
            allowance = self.token.self_allowance(self.exchange.address)

            if allowance < token_amount:
                self.dapp.add_transaction_dialog(
                    self.token.approve_unlimited(self.exchange.address),
                    title="Approve Exchange contract to handle your {}".format(self.token_symbol),
                    gas_limit=50000,
                )
                self.dapp.add_message_dialog("You must first approve the Exchange to handle your {}".format(self.token_symbol))
            else:
                self.dapp.add_transaction_dialog(
                    self.exchange.token_to_eth(token_amount, eth_amount),
                    title="Sell {} for ETH".format(self.token_symbol),
                    gas_limit=100000
                )
                self.dapp.add_message_dialog("The TX will have a 45min TTL and max 2% slippage from the exchange rate you agreed on.")

            self.close()

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

        try:
            eth_amount = Decimal(self.eth_amount._value)
            token_amount = Decimal(self.eth_amount._value)
        except InvalidOperation:
            errors.append("Could not convert currency amount to Decimal")

        if eth_amount <= 0 or token_amount <= 0:
            errors.append("Amounts must be positive decimal values")

        if action == 'buy':
            if eth_amount > self.dapp.node._wei_balance:
                errors.append("Not enough eth to make purchase")
        elif action == 'sell':
            if token_amount > self.token.my_balance():
                errors.append("Credstick doesn't have enough tokens to sell that amount")

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
                    self._value = "{:f}".format(self.exchange.sell_token_calc_token_input(amt)[0])[:19]
                elif self.radiobutton_value() == 'buy':
                    self._value = "{:f}".format(self.exchange.buy_token_calc_token_output(amt)[0])[:19]
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
                    self._value = "{:f}".format(self.exchange.sell_token_calc_eth_output(amt)[0])[:19]
                elif self.radiobutton_value() == 'buy':
                    self._value = "{:f}".format(self.exchange.buy_token_calc_eth_input(amt)[0])[:19]
            except InvalidOperation:
                self._value = ""

            self.token_value_dirty_flag = False
        super(EthValueText, self).update(frame_no)

