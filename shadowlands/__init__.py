#!/usr/bin/env python

import sys

from shadowlands.credstick import Credstick
from shadowlands.sl_config import SLConfig
from shadowlands.eth_node import Node
from shadowlands.price_poller import PricePoller
from shadowlands.tui.tui import Interface

import pdb
from shadowlands.tui.debug import debug

#pdb.set_trace()

# Read from config file
sl_config = SLConfig()

# Start network subsystem
eth_node = Node(sl_config)

# Eth node heartbeat
eth_node.start_heartbeat_thread()

# price import thread
price_poller = PricePoller(sl_config)
price_poller.start_thread()

# create user interface 
interface = Interface(eth_node, price_poller, sl_config)


# Begin interface
interface.load()

# Shut it all down.
if interface.credstick is not None:
    interface.credstick.close()

print("Closing credstick poller...")
Credstick.stop_detect_thread()

print("Closing price poller...")
price_poller.stop_thread()

print("Closing connection to ethereum node...")
eth_node.stop_thread()


sys.exit(0)






#m.join()
#rx = dapp.send_erc20('WETH', '0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.00001)
#import pdb; pdb.set_trace()





# start up credstick detect method in a thread, pass in the interface.
# when the credstick is detected, it will send 
 

# Show main menu in a thread to provide live updates


#menuSelection = input()
#m.join()


#os.system("clear")


#rx = dapp.send_erc20('WETH', '0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.00001)

#dapp.send_ether('0x1545fed39abc1b82c4711d8888fb35a87304817a', 0.00001)

# import pdb; pdb.set_trace()


# dapp.send_ether('0xF6E0084B5B687f684C2065B9Ed48Cc039C333844', 0.000001337)
#rx = dapp.ens_reveal_bid('kayagoban.eth', '0.01', 'harbor habit lottery')



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


