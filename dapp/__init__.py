from sl_dapp import SLDapp
from asciimatics.scene import Scene
from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button
from asciimatics.exceptions import NextScene
#from asciimatics.renderers import StaticRenderer, FigletText
from tui.errors import ExitDapp

from dapp.contracts.ens import Ens
from dapp.contracts.ens_registry import EnsRegistry
from dapp.contracts.ens_resolver import EnsResolver
from dapp.contracts.ens_reverse_resolver import EnsReverseResolver

class Dapp(SLDapp):
    # You get self._node and self._screen for free.
    # Most of the useful things you do are through self._node.
    
    def initialize(self):
        self._ens = Ens(self._node)
        self._ens_registry = EnsRegistry(self._node)
        self._ens_resolver = EnsResolver(self._node)
        self._ens_reverse_resolver = EnsReverseResolver(self._node)

    

    @property
    def scenes(self):
        return [
            Scene([ContactView(self._screen)], -1, name="ENSQuery"),
        ]


class ContactView(Frame):
    def __init__(self, screen):
        super(ContactView, self).__init__(screen,
                                          screen.height * 2 // 3,
                                          screen.width * 2 // 3,
                                          hover_focus=True,
                                          title="ENS",
                                          reduce_cpu=True)

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Text("Name:", "name"))
        layout = Layout([1, 1, 1, 1])
        self.add_layout(layout)
        layout.add_widget(Button("OK", self._ok), 0)
        layout.add_widget(Button("Cancel", self._cancel), 3)
 
        self.fix()
 
    def _ok(self):
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
 
