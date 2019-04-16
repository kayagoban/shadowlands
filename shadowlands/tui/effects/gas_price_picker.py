from asciimatics.widgets import RadioButtons 
from decimal import Decimal

from shadowlands.tui.debug import debug
import pdb


class GasPricePicker(RadioButtons):
    def __init__(self, on_change=None, interface=None, **kwargs):
        """
        :param options: A list of (text, value) tuples for each radio button.
        :param label: An optional label for the widget.
        :param name: The internal name for the widget.
        :param on_change: Optional function to call when text changes.

        Also see the common keyword arguments in :py:obj:`.Widget`.
        """
        self._interface = interface

        gas_price_wei = self._interface.node.w3.eth.gasPrice
        try:
            gas_price_minus_20_percent = gas_price_wei - gas_price_wei * Decimal(.2)
        except TypeError as e:
            print("gas_price_wei from w3.eth.gasPrice was unexpectedly a dict?")
            print(str(gas_price_wei))

        gas_price_gwei = self._interface.node.w3.fromWei(gas_price_wei, 'gwei')
        gas_price_gwei_m20 = self._interface.node.w3.fromWei(gas_price_minus_20_percent, 'gwei')

        #debug(); pdb.set_trace()

        _options = [
                (str(gas_price_gwei) + ' gwei  |from w3.gasPrice()' , gas_price_gwei), 
                (str(round(gas_price_gwei_m20, 3)) + ' gwei (-20%)', gas_price_gwei_m20), 
                ('Enter custom gas price', '0')
        ]

        super(GasPricePicker, self).__init__(_options, on_change=on_change, label=' Gas Price:', name='gasoptions', **kwargs)

        # preset the value to the first option value
        #self._value = self._options[0][1]
   


