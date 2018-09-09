


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
 
