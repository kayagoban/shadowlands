#!/usr/bin/env python

import sys, os, hashlib, argparse, struct, time, locale, qrcode_terminal, threading
import tty, termios
from namehash import namehash
from pyfiglet import Figlet
from cryptocompy import price
import eth_node
import dapp
from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, NoCredstickFoundError
from tui.tui import Interface
from asciimatics.exceptions import NextScene
from time import sleep
import pdb
from sl_config import SLConfig

#pdb.set_trace()

menuSelection = None
credstick = None

# Flags to halt threads
credstick_thread_shutdown = False
price_poller_thread_shutdown = False

def credstick_finder(interface):
    global credstick_thread_shutdown
    not_found = True

    while not_found:
        try: 
            credstick = Credstick.detect()
            credstick.open()
            eth_node.ethAddress = credstick.derive()
            dapp.credstick = credstick
            eth_node.poll()
            not_found = False
            interface.set_credstick(credstick)
        except(NoCredstickFoundError, OpenCredstickError, DeriveCredstickAddressError):
            time.sleep(0.25)

        if credstick_thread_shutdown:
            break



def eth_price_poller(interface):
    global price_poller_thread_shutdown

    while True:
        try:
            prices = price.get_current_price("ETH", ["USD", "GBP", "EUR", 'BTC'])
            interface.update_prices(prices)
        except:
            interface.update_prices(None)

        # 5 minutes seems responsible.
        for i in range (150):
            time.sleep(2)
            if price_poller_thread_shutdown:
               return




# Create or Read personal config files that contains
# network preferences, etc

#pdb.set_trace()
sl_config = SLConfig()

eth_node.sl_config = sl_config



#Begin
###############

#eth_node.connect_w3_local()

if sl_config.default_method:
    sl_config.default_method()

t = threading.Thread(target=eth_node.heartbeat)
t.start()

dapp.node = eth_node
dapp.register_node_on_contracts()

# create interface 
interface = Interface(eth_node, dapp, sl_config)

# price import thread
p = threading.Thread(target=eth_price_poller, args=[interface])
p.start()

# credstick finder thread
m = threading.Thread(target=credstick_finder, args = [interface])
m.start()


#m.join()
#rx = dapp.send_erc20('WETH', '0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.00001)
#rx = dapp.send_ether('0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.0000001337)
#import pdb; pdb.set_trace()





# Begin interface

interface.load()



# Shut it down.
if credstick != None:
    credstick.close()


credstick_thread_shutdown = True
print("Closing credstick poller...")
m.join()


price_poller_thread_shutdown = True
print("Waiting for price poller to shut down...")
p.join()

eth_node.shutdown = True
print("Closing connection to ethereum node...")
t.join()


sys.exit(0)



# start up credstick detect method in a thread, pass in the interface.
# when the credstick is detected, it will send 
 

# Show main menu in a thread to provide live updates


#menuSelection = input()
#m.join()


#os.system("clear")


def send_tx(rx):
    if rx != None:
        print('Transaction sent.')
        print(rx)


#rx = dapp.send_erc20('WETH', '0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.00001)

#dapp.send_ether('0x1545fed39abc1b82c4711d8888fb35a87304817a', 0.00001)

# import pdb; pdb.set_trace()


# dapp.send_ether('0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.000001337)
#rx = dapp.ens_reveal_bid('kayagoban.eth', '0.01', 'harbor habit lottery')

# rx = dapp.ens_finalize_auction('cthomas')

#dapp.register_ens_resolver('mindmyvagina')

#dapp.set_ens_resolver_address('mindmyvagina', eth_node.ethAddress)

# dapp.set_ens_reverse_lookup('ceilingcat')



"""
# Check the file for tampering
def file_checksum():
    script_path = os.path.abspath(__file__)
    shahash = hashlib.sha256()
    with open(script_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shahash.update(chunk)
    return shahash.hexdigest()
"""



# For launching etherscan to view transactions
#import subprocess
#subprocess.call(["/usr/bin/open", 'http://apple.com'])


# for copying to clipboard
#import pyperclip
#pyperclip.copy('The text to be copied to the clipboard.')

# For qrcode feature
# o = qrcode_terminal.qr_terminal_str('0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898', 1)


