from asciimatics.renderers import DynamicRenderer
from asciimatics.screen import Screen
from decimal import Decimal
from shadowlands.tui.errors import PriceError
from shadowlands.sl_node import NodeConnectionError
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

            if index > 0 and index < len(self.txqueue(self._interface.node.network)):
                image += '║'
                color_map += [SL_COLOR]
                
            tx_image = " {}) {} ".format(index, tx['rx'].hash.hex()[0:9])
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
        images = ['[block ' + str(self.node.best_block) + ']']
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
            image = [ self._interface.credstick.hdpath ]

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
    def __init__(self, interface, add_padding=True):
        super(CredstickNameRenderer, self).__init__(1, 9)
        self._interface = interface
        self._node = interface.node
        self._add_padding = add_padding

    def _render_now(self):
        space_available = 29 
        if not self._interface.credstick:
            #image = ['blergh']
            image =  ['Please insert Credstick.']
        else:
            name = self._interface.credstick.manufacturerStr + ' ' + self._interface.credstick.productStr
            address = self._interface.credstick.address
            hdpath = self._interface.credstick.hdpath
            if self._add_padding:
                padding = '═' * (space_available - len(name))
            else:
                padding = "detected.       \nHD derivation {}\nEthereum address {}\nResolving ENS...\nLoading Eth balance...\nLoading Erc20 balances...".format(hdpath, address)

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
            bal_str = "{:f}".format( bal )

        image  = [bal_str]

        return img_colour_map(image)


class EthValueRenderer(DynamicRenderer):
    def __init__(self, interface):
        super(EthValueRenderer, self).__init__(1, 15)
        self._interface = interface

    def _render_now(self):
        bal = self._interface._node.eth_balance

        if bal is None or self._interface._node.eth_price is None:
            return img_colour_map([''])

        val = str(bal * self._interface._node.eth_price)[0:18]
        image = [ "{} {} {}".format('USD', '$', val) ]

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




