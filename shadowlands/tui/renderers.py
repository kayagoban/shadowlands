from asciimatics.renderers import DynamicRenderer
from asciimatics.screen import Screen
from decimal import Decimal
from shadowlands.tui.errors import PriceError
from shadowlands.eth_node import NodeConnectionError
import qrcode
from shadowlands.tui.debug import debug
import pdb

SL_COLOR = (Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK)


def sl_color_map(image):
    return [SL_COLOR for _ in range(len(image))]


class TxQueueHashRenderer(DynamicRenderer):

    def __init__(self, interface):
        super(TxQueueHashRenderer, self).__init__(1, 32)
        self._interface = interface

    @property
    def txqueue(self):
        return self._interface.config.txqueue

    def _render_now(self):
        if len(self.txqueue(self._interface.node.network)) < 1:
            return [''], [()]

        image = "TXs: " 
        color_map = sl_color_map(image)

        for index, tx in enumerate(self.txqueue(self._interface.node.network)):
            #debug(); pdb.set_trace()

            if index > 0 and index < len(self.txqueue(self._interface.node.network)):
                image += '║'
                color_map += [SL_COLOR]
                
            tx_image = " {}) {} ".format(index, tx.hash.hex()[0:9])
            tx_map = sl_color_map(tx_image) 
            tx_map[1] = (Screen.COLOUR_WHITE, 
                         Screen.A_BOLD, 
                         Screen.COLOUR_BLACK) 
            image += tx_image 
            color_map += tx_map

        #debug(); pdb.set_trace()
        return [image], [color_map]


#debug(); pdb.set_trace()
def img_colour_map(image):
    return image, [[(Screen.COLOUR_GREEN, Screen.A_NORMAL, Screen.COLOUR_BLACK) for _ in range(len(image[0])) ] ]

class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        if self.node.connection_type and self.node.network_name:
            image =  ["{},  {}".format(self.node.connection_type, self.node.network_name)]
        else:
            image = ['No ethereum connection']

        return img_colour_map(image)


class BlockStatusRenderer(DynamicRenderer):

    def __init__(self, _node):
        super(BlockStatusRenderer, self).__init__(1, 40)
        self.node = _node

    def _render_now(self):
        syncing = self.node.syncing_hash

        if syncing is None or not ( syncing or self.node.best_block):
            return img_colour_map([ '[No blocks available]' ])

        elif syncing.__class__ == bool and syncing == False:
            images = ['[synced: block ' + str(self.node.best_block) + ']']
        else:
            images = [ '[syncing:  ' + str(self.node.blocks_behind) + ' blocks to ' + str(self.node.syncing_hash['highestBlock']) + ']' ]

        return img_colour_map(images)

class AddressRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(AddressRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            image = ['Unknown']
        else:
            image = [ self._interface.credstick.addressStr() ]

        return img_colour_map(image)


class HDPathRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(HDPathRenderer, self).__init__(1, 32)
        self._interface = interface

    def _render_now(self):
        if not self._interface.credstick:
            image = ['Unknown']
        else:
            image = [ self._interface.credstick.hdpath_base + '/' + self._interface.credstick.hdpath_index ]

        return img_colour_map(image)

def txqueue():
    #return []
    return [
        {
            'tx_hash': '0x36283e1c4d5ce3d671597ed05812a7562b05157b3559e264f4ab473a62dc5720',
            'description': 'Send Ether'
        },
        {
            'tx_hash': '0x291e0c845afd6dd2a21f4933ce374c5b86db5358b1b6576829b22d30a582e2bd',
            'description': 'Generate DAI'
        },
        {
           'tx_hash': '0x4c8bc0842ca19d90f4c1047a3961687ea494a1d8645df02f575be863ccb9d89c',
            'description': 'Materialize'
        },
        {
           'tx_hash': '0x961687ea494a1d8645df02f575be863ccb9d89c',
            'description': 'Materialize'
        },
        {
           'tx_hash': '0x5df02f575be863ccb9d89c',
            'description': 'Materialize'
        }
 
    ]



class CredstickNameRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(CredstickNameRenderer, self).__init__(1, 9)
        self._interface = interface

    def _render_now(self):
        space_available = 29 
        if not self._interface.credstick:
            image =  ['Unknown']
        else:
            name = self._interface.credstick.manufacturerStr + ' ' + self._interface.credstick.productStr
            padding = '═' * (space_available - len(name))
            image =  [ "{} {}".format(name,padding) ]
            
        return img_colour_map(image)

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
            return img_colour_map(['Unknown'])

        bal_str = 'Unknown'

        if bal:
            bal_str = str( bal )

        image  = [bal_str]

        return img_colour_map(image)


class EthValueRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthValueRenderer, self).__init__(1, 15)
        self._interface = interface

    def _render_now(self):
        curr = self._interface._config.displayed_currency
        try:
            currency_val = Decimal(self._interface._price_poller.eth_price)
        except (TypeError, KeyError, PriceError):
            return img_colour_map(['Unavailable'])

        try:
            eth = self._interface.node.eth_balance
        except AttributeError:
            return img_colour_map(['Unavailable'])

        if not eth:
            return img_colour_map(['Unavailable'])

        if curr == 'BTC':
            decimal_places = 6
        else:
            decimal_places = 2

        val = str(round(currency_val * eth, decimal_places))
        image = [ "{} {} {}".format(curr, self._interface._config.curr_symbol, val) ]

        return img_colour_map(image)


class ENSRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(ENSRenderer, self).__init__(1, 16)
        self._interface = interface

    def _render_now(self):
        domain = self._interface.node.ens_domain
        if not domain:
            domain = 'No Reverse ENS'

        image = [domain]

        return img_colour_map(image)




