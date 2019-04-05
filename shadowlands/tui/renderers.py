from asciimatics.renderers import DynamicRenderer
from asciimatics.screen import Screen
from decimal import Decimal
from shadowlands.tui.errors import PriceError
from shadowlands.eth_node import NodeConnectionError
import qrcode
from shadowlands.tui.debug import debug
import pdb


#debug(); pdb.set_trace()

class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        if self.node.connection_type and self.node.network_name:
            return ["{},  {}".format(self.node.connection_type, self.node.network_name)], None

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


class HDPathRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(HDPathRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            return ['Unknown'], None

        hdpath = self._interface.credstick.hdpath_base + '/' + self._interface.credstick.hdpath_index
        return [hdpath], None

class TxQueueRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(TxQueueRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        tx_str = "        0) Send Ether     "
        return [tx_str], None

class TxQueueHashRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(TxQueueHashRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        tx_str = "TXs:  ║ 0xdeadbeef... ║"

        return [tx_str], None



class CredstickNameRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(CredstickNameRenderer, self).__init__(1, 9)
        self._interface = interface

    def _render_now(self):
        space_available = 29 
        if not self._interface.credstick:
            name = 'Unknown'
        else:
            name = self._interface.credstick.manufacturerStr + ' ' + self._interface.credstick.productStr
            padding = '═' * (space_available - len(name))
            name = "{} {}".format(name,padding)

            
        return [name], None

class QRCodeRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(QRCodeRenderer, self).__init__(17, 31)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            qr_image = ['No QR Data']
            colour_map = [None, 0, 0]
        else:

            #debug(); pdb.set_trace()
            qr = qrcode.QRCode(
                version=1,
                box_size=4,
                border=1,
            )

            #debug(); pdb.set_trace()
            qr.add_data(self._interface.credstick.addressStr())
            qr.make(fit=True)
            qr_string = qr.print_ascii(string_only=True)

            qr_image = qr_string.split('\n')
            #debug(); pdb.set_trace()
            colour_map = [[(Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK) for _ in range(self._width)]
                          for _ in range(self._height)]
        return qr_image, colour_map



class EthBalanceRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthBalanceRenderer, self).__init__(1, 30)
        self._interface = interface

    def _render_now(self):
        try:
            bal = self._interface.node.eth_balance
        except AttributeError:
            return ['Unknown'], None

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
            currency_val = Decimal(self._interface._price_poller.eth_price)
        except (TypeError, KeyError, PriceError):
            return ['Unavailable'], None

        try:
            eth = self._interface.node.eth_balance
        except AttributeError:
            return ['Unavailable'], None

        if not eth:
            return ['Unavailable'], None

        if curr == 'BTC':
            decimal_places = 6
        else:
            decimal_places = 2

        val = str(round(currency_val * eth, decimal_places))
        val = "{} {} {}".format(curr, self._interface._config.curr_symbol, val)

        return [val], None


class ENSRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(ENSRenderer, self).__init__(1, 16)
        self._interface = interface

    def _render_now(self):
        domain = self._interface.node.ens_domain
        if not domain:
            domain = 'No Reverse ENS'

        return [domain], None




