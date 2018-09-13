from sl_dapp import SLDapp, SLFrame, NextFrame, ExitDapp
#from asciimatics.renderers import StaticRenderer, FigletText

import random, string
from datetime import datetime, timedelta

from dapp.contracts.ens import Ens
from dapp.contracts.ens_registry import EnsRegistry
from dapp.contracts.ens_resolver import EnsResolver
from dapp.contracts.ens_reverse_resolver import EnsReverseResolver

from tui.debug import debug
import pdb
#debug(); pdb.set_trace()


# If you want the full power of asciimatics, you can override SLDapp
# and do basically whatever you want.  But it will be a ton of work. 
class Dapp(SLDapp):
    def initialize(self):
        # the node object provides the ns library from web3.py
        # Some things are just easier using this lib.
        self._ns = self.node._ns
        ## Here we instantiate our own Contract classes
        self.ens_contract = Ens(self._node)
        self.ens_registry_contract = EnsRegistry(self._node)
        self.ens_resolver_contract = EnsResolver(self._node)
        self.ens_reverse_resolver_contract = EnsReverseResolver(self._node)

        self._chosen_domain = None

        # add initial frame
        self.add_frame(ENSStatusFrame, height=6, width=55, title="Check status on ENS domain")

   # This method can catch key presses and mouse events
    def process_event(self, event):
        return None


# SLFrame gives you helper methods for rapid development.
# If you wish to do things yourself, you have the full asciimatics
# library at your disposal.
class ENSStatusFrame(SLFrame):
    def initialize(self):
        # add_textbox returns a function that will grab the value inside the textbox.
        self.box_value = self.add_textbox("ENS name:")

        # pass in callback functions with this method.
        self.add_ok_cancel_buttons(self._ok, self._cancel)

    def _ok(self):
        #debug(); pdb.set_trace()
        self.dapp._chosen_domain = self.box_value()
        auction_status = self.dapp.ens_contract.auction_status(self.dapp._chosen_domain)
        # 2 means the domain is already owned. see ENS documentation.
        if auction_status == 2:
            # node exposes the web3.py ens module functions.
            owner = self.dapp.node.ens.owner(self.dapp._chosen_domain)
            if self.dapp.node.credstick and owner == self.dapp.node.credstick.addressStr():
                # This method takes a message and the next Frame to move to.
                self.dapp.add_frame(ENSManageFrame, height=6, width=45, title="Manage your ENS domain")
                self.close()
            else:
                self.dapp.add_message_dialog("Somebody else owns this ENS domain.")
        elif auction_status in [0, 1, 4]:
            self.dapp.add_frame(ENSAuctionFrame, height=9, width=50, title="ENS domain auction")
            self.close()
        elif auction_status == 3:
            self.add_message_dialog("This name is forbidden by the ENS contract.")
        elif auction_status == 5:
            self.add_message_dialog("This name is not yet avialable for auction.")
                
    def _cancel(self):
        self.close()
        self.dapp.quit()


class ENSManageFrame(SLFrame):
    def initialize(self):
        self.add_label("Your domain  blah blha blah lbah")
        self.add_ok_cancel_buttons(None, self._cancel)

    def _ok(self):
        pass

    def _cancel(self):
       self.close()
       self.dapp.quit()



#debug(); pdb.set_trace()
#debug(); pdb.set_trace()

class ENSAuctionFrame(SLFrame):
    def initialize(self):
        auction_status = self._dapp.ens_contract.auction_status(self.dapp._chosen_domain)

        if auction_status == 0:
           self.add_label("You can start an auction for this name.")
           self.add_ok_cancel_buttons(self._start_auction_choice, self._cancel)
        elif auction_status == 1:
            self.add_label(f"The auction for '{self.dapp._chosen_domain}' has begun.")
            reveal_date = self.dapp.ens_contract.reveal_date(self.dapp._chosen_domain)
            time_left = reveal_date - datetime.now() - timedelta(days=2)

            if time_left.total_seconds() > 0:
                minutes_left = time_left.total_seconds() // 60
                hours_left = minutes_left // 60
                days_left = round(hours_left / 24, 1)
                if minutes_left < 60:
                    self.add_label(f"{minutes_left} minutes left to bid.")
                elif hours_left < 24:
                    self.add_label(f"{hours_left} hours left to bid.")
                else:
                    self.add_label(f"{days_left} days left to bid.")
                   
            self.bidvalue = self.add_textbox(f"Bid Amount {self.dapp.config.CURR_SYMBOLS['ETH']}")
            self.add_ok_cancel_buttons(self._make_bid_choice, self._cancel, ok_text="Bid")
 
            #salt = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])
        elif auction_status == 4:
            self.add_label("It is time to reveal the bids for this name auction.")

    def _start_auction_choice(self):
        self.dapp.add_transaction_dialog(
            self._send_auction_tx,
            destroy_window=self, 
            title="Begin Auction"
        )

    def _send_auction_tx(self):
        return self.dapp.ens_contract.start_auction(self.dapp._chosen_domain)

    def _make_bid_choice(self):
        self.dapp.add_transaction_dialog(
            self._make_bid_tx,
            tx_value=self.bidvalue(),
            destroy_window=self, 
            title=f"Bid on name '{self.dapp._chosen_domain}'"
        )

    def _make_bid_tx(self):
        return self.dapp.ens_contract.place_bid(self.dapp._chosen_domain,
                                     self.dapp.node.credstick.addressStr(),
                                     self.bidvalue(),
                                     "goopy goober guts")

    def _cancel(self):
       self.close()
       self.dapp.quit()


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
 
