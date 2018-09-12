from sl_dapp import SLDapp, SLFrame, NextFrame, ExitDapp
#from asciimatics.renderers import StaticRenderer, FigletText

from dapp.contracts.ens import Ens
from dapp.contracts.ens_registry import EnsRegistry
from dapp.contracts.ens_resolver import EnsResolver
from dapp.contracts.ens_reverse_resolver import EnsReverseResolver

from tui.debug import debug
import pdb
#debug(); pdb.set_trace()


class Dapp(SLDapp):
    def initialize(self):
        # the node object provides the ns library from web3.py
        # Some things are just easier using this lib.
        self._ns = self.node._ns
        ## Here we instantiate our own Contract classes
        self._ens = Ens(self._node)
        self._ens_registry = EnsRegistry(self._node)
        self._ens_resolver = EnsResolver(self._node)
        self._ens_reverse_resolver = EnsReverseResolver(self._node)

        # Add some frames for our application
        self.add_frame(ENSStatusFrame, name="ENSStatus", height=6, width=45, title="Check status on ENS domain")
        self.add_frame(ENSManageFrame, name="ENSManage", height=6, width=45, title="Manage an ENS domain")


# SLFrame gives you helper methods for rapid development.
# If you wish to do things yourself, you have the full asciimatics
# library at your disposal.
class ENSStatusFrame(SLFrame):
    def initialize(self):
        # add_textbox returns a function that will grab the value inside the textbox.
        self.box_value = self.add_textbox('ens_name', "ENS name:")

        # pass in callback functions with this method.
        self.add_ok_cancel_buttons(self._ok, self._cancel)

    def _ok(self):
        #debug(); pdb.set_trace()
        auction_status = self._dapp._ens.auction_status(self.box_value())
        # 2 means the domain is already owned. see ENS documentation.
        if auction_status == 2:
            # Note that we're using the web3.py ns library in this statement.
            owner = self._dapp._ns.owner(self.box_value())
            if self._dapp._node._credstick and owner == self._dapp._node._credstick.addressStr():
                # This method takes a message and the next Frame to move to.
                self.add_message_dialog("You own this ENS domain.", "ENSManage")
            else:
                self.add_message_dialog("Somebody else owns this ENS domain.", "ENSStatus")
        elif auction_status == 0:
            self.add_message_dialog("You can start an auction for this name.", "ENSStatus")
        elif auction_status == 1:
            self.add_message_dialog("The auction for this name has begun and you can bid.", "ENSStatus")
        elif auction_status == 4:
            self.add_message_dialog("It is time to reveal the bids for this name auction.", "ENSStatus")
        elif auction_status == 3:
            self.add_message_dialog("This name is forbidden by the ENS contract.", "ENSStatus")
        elif auction_status == 5:
            self.add_message_dialog("This name is not yet avialable for auction.", "ENSStatus")
                
    def _cancel(self):
        raise ExitDapp



class ENSManageFrame(SLFrame):
    def initialize(self):
        pass


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
 
