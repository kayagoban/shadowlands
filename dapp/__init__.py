from sl_dapp import SLDapp, SLFrame
from asciimatics.scene import Scene
from asciimatics.exceptions import NextScene
#from asciimatics.renderers import StaticRenderer, FigletText
from tui.errors import ExitDapp

from dapp.contracts.ens import Ens
from dapp.contracts.ens_registry import EnsRegistry
from dapp.contracts.ens_resolver import EnsResolver
from dapp.contracts.ens_reverse_resolver import EnsReverseResolver

from tui.debug import debug
import pdb

class Dapp(SLDapp):
    def initialize(self):
        self._ns = self.node._ns
        self._ens = Ens(self._node)
        self._ens_registry = EnsRegistry(self._node)
        self._ens_resolver = EnsResolver(self._node)
        self._ens_reverse_resolver = EnsReverseResolver(self._node)

    @property
    def scenes(self):
        return [
            Scene([ENSSearchFrame(self, 6, 45, title="Enter the name to manage or acquire")], -1, name="ENSQuery"),
        ]


class ENSSearchFrame(SLFrame):
    def initialize(self):
        self.add_textbox('ens_name', "ENS name:")

    def _ok(self):
        debug()
        pdb.set_trace()
        ens_name = self.find_widget('ens_name')
        """
        ethRegistrar.entries(web3.sha3('name'))[0];
        This will return a single integer between 0 and 5. The full 
        solidity data structure for this can be viewed here in the 
        Registrar contract. The numbers represent different ‘states’ 
        a name is currently in.

        0 - Name is available and the auction hasn’t started
        1 - Name is available and the auction has been started
        2 - Name is taken and currently owned by someone
        3 - Name is forbidden
        4 - Name is currently in the ‘reveal’ stage of the auction
        5 - Name is not yet available due to the ‘soft launch’ of names.
        """
        result = self._dapp._ens.name_status(ens_name._value)



        result = self._dapp._ns.owner(ens_name._value)
        

        #self.save()
        #self._model.update_current_contact(self.data)
        raise NextScene("Main")

    @staticmethod
    def _cancel():
        raise ExitDapp



# NOTE it occurs to me that there is no real need for these helper functions.
# node.push ( method, gasprice ) is all that's needed.


# reveal_bid('ceilingcat', '0.01', 'burly jumper knife')
def ens_reveal_bid(name, bid_amount, secret, gas_price):
    return push(
        Ens.unsealBid(name, bid_amount, secret), gas_price
    )

# ens_finalize_auction(name)
def ens_finalize_auction(name, gas_price):
    return push(
        Ens.finalizeAuction(name), gas_price
    )

# Sets the resolver on your name record.  No idea why we have to do this - there should 
# only be one resolver per ENS registrar.  But who am I to question the gods?
#
# Both of these invocations have the same precise effect.  the .eth domain will be added
# if it is not already in the string.
#
# register_ens_resolver('ceilingcat')
# register_ens_resolver('ceilingcat.eth')
def register_ens_resolver(name, gas_price):
    return push( 
        EnsRegistry.set_resolver(name), gas_price
    )

# Sets the address that your name resolves to.  Will fail if your credstick does not
# own the name.
#
# set_ens_resolver_address('ceilingcat', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5')
# set_ens_resolver_address('ceilingcat.eth', '0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5')
def set_ens_resolver_address(name, address_target, gas_price):
    return push(
        EnsResolver.set_address(name, address_target), gas_price
    )

# Sets the reverse record for the name given to the address of your credstick,
# if indeed you own the name.  This is how you set your nick.
# 
# set_ens_reverse_lookup('ceilingcat')
# set_ens_reverse_lookup('ceilingcat.eth')
def set_ens_reverse_lookup(name, gas_price):
    return push(
        EnsReverseResolver.set_name(name), gas_price
    )
 
