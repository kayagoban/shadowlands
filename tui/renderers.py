from asciimatics.renderers import DynamicRenderer
from tui.debug import debug
from decimal import Decimal


class NetworkStatusRenderer(DynamicRenderer):
    def __init__(self, _node):
        super(NetworkStatusRenderer, self).__init__(1, 25)
        self.node = _node

    def _render_now(self):
        try:
            network = self.node.networkName()
        except:
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
        except:
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
        try:
            usd = Decimal(self._interface.prices()['ETH']['USD'])
            eth = Decimal(self._interface.node.ethBalanceStr())
            val = str(round(usd * eth, 2))
            val = 'USD $' + val 
        except:
            val = 'Unknown'

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




