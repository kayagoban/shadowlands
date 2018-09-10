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
        if self.node.connection_type and self.node.network_name:
            return [f'{self.node.connection_type},  {self.node.network_name}'], None

        return ['No ethereum connection'], None


class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 40)
        self.node = _node

    def _render_now(self):
        syncing = self.node.syncing_hash
        if not ( syncing or self.node.best_block):
            return [ '[No blocks available]' ], None


        if syncing == None:
            return [ '[No blocks available]' ], None
        elif syncing.__class__ == bool and syncing == False:
            images = ['[synced: block ' + str(self.node.best_block) + ']'
                     ]
        else:
            images = [ '[syncing:  ' + str(self.node.blocks_behind) + ' blocks to ' + str(self.node.syncing_hash['highestBlock']) + ']' ]


        return images, None

class AddressRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(AddressRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            return ['Unknown'], None

        addr = self._interface.credstick.addressStr()
        return [addr], None

class CredstickNameRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(CredstickNameRenderer, self).__init__(1, 9)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            name = 'Unknown'
        else:
            name = self._interface.credstick.manufacturerStr + ' ' + self._interface.credstick.productStr
        return [name], None

class EthBalanceRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthBalanceRenderer, self).__init__(1, 30)
        self._interface = interface

    def _render_now(self):
        bal = self._interface.node.eth_balance
        if bal:
            bal_str = str( bal )
        else:
            bal_str = 'Unknown'
        return [bal_str], None

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

        eth = self._interface.node.eth_balance
        if not eth:
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
        domain = self._interface.node.ens_domain
        if not domain:
            domain = 'Service unavailable'

        return [domain], None




