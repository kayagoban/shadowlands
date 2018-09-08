from asciimatics.renderers import DynamicRenderer
from decimal import Decimal
from tui.errors import PriceError
from eth_node import NodeConnectionError

from tui.debug import debug
import pdb


 #debug(); pdb.set_trace()

class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        try:
            network = self.node.networkName()
        except NodeConnectionError:
            network = 'unavailable'

        return [network], None


class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 40)
        self.node = _node

    def _render_now(self):
        try:
            if not self.node.syncingHash():
                images = ['[synced: block ' + self.node.block + ']'
                         ]
            else:
                images = [ '[syncing:  ' + str(self.node.blocksBehind) + ' blocks to ' + str(self.node.syncing['highestBlock']) + ']' ]
        except NodeConnectionError:
            images = [ '[No blocks available]' ]


        return images, None

class AddressRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(AddressRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        try:
            addr = self._interface.credstick.addressStr()
        except:
            addr = 'Unknown'

        return [addr], None

class CredstickNameRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(CredstickNameRenderer, self).__init__(1, 9)
        self._interface = interface

    def _render_now(self):
        try:
            name = self._interface.credstick.manufacturerStr + ' ' + self._interface.credstick.productStr
        except:
            name = 'Unknown'
        return [name], None

class EthBalanceRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthBalanceRenderer, self).__init__(1, 30)
        self._interface = interface

    def _render_now(self):
        try:
            bal = self._interface.node.ethBalanceStr()
        except:
            bal = 'Unknown'
        return [bal], None

class EthValueRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthValueRenderer, self).__init__(1, 15)
        self._interface = interface

    def _render_now(self):
        curr = self._interface._config.displayed_currency
        try:
            currency_val = Decimal(self._interface.price())
        except (TypeError, KeyError, PriceError):
            return ['Unavailable'], None

        try:
            eth = Decimal(self._interface.node.ethBalanceStr())
        except NodeConnectionError:
            return ['Unavailable'], None
        if curr == 'BTC':
            decimal_places = 6
        else:
            decimal_places = 2

        val = str(round(currency_val * eth, decimal_places))
        val = f"{curr} {self._interface.CURR_SYMBOLS[curr]} {val}"

        return [val], None


class ENSRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(ENSRenderer, self).__init__(1, 16)
        self._interface = interface

    def _render_now(self):
        try:
            domain = self._interface.node.ens_domain()
        except:
            domain = 'Service unavailable'

        return [domain], None




