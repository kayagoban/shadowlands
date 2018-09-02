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

# import pdb; pdb.set_trace()

menuSelection = None
credstick = None

# Flags to halt threads
credstick_thread_shutdown = False
price_poller_thread_shutdown = False

'''
boxDictionary = {
        '\\' : b'\xe2\x95\x9a',
        '-'  : b'\xe2\x95\x90',
        '/'  : b'\xe2\x95\x9d',
        '|'  : b'\xe2\x95\x91',
        '+'  : b'\xe2\x95\x94',
        '$'  : b'\xe2\x95\x97',
        }


def boxDecode(x):
    return ("".join(boxDictionary.get(i, i.encode('utf-8')).decode('utf-8') for i in x))


def blastOff():
    sys.stdout.write("\033[F")
    timeout = 0.11
    for x in range(70):
      time.sleep(timeout)
      sys.stdout.write(".")
      sys.stdout.flush()
      timeout = timeout * 0.93
    return

'''


def credstick_finder(interface):
    global credstick_thread_shutdown
    #import pdb; pdb.set_trace()
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
        prices = price.get_current_price("ETH", ["USD", "GBP", "EUR", 'BTC'])
        interface.update_prices(prices)
        # 5 minutes seems responsible.
        for i in range (150):
            time.sleep(2)
            if price_poller_thread_shutdown:
               return


# Get a connection
eth_node.connect()

# This is absurd.  There must be a better way of getting
# a singleton instance of web3.
# The problem is: invoking web3.auto gives a different w3 object than web3.auto.infura.
# I either must use the same switching logic in every module that needs w3, or I must
# distribute it everywhere.  Annoying but no way around it yet that I can see.
dapp.w3 = eth_node.web3_obj
dapp.register_w3_on_contracts()

# eth node heartbeat thread
t = threading.Thread(target=eth_node.heartbeat)
t.start()

# create interface 
interface = Interface(eth_node, dapp)

# price import thread
p = threading.Thread(target=eth_price_poller, args=[interface])
p.start()

# credstick finder thread
m = threading.Thread(target=credstick_finder, args = [interface])
m.start()


# Begin interface
interface.load()



# Shut it down.
if credstick != None:
    credstick.close()


credstick_thread_shutdown = True
sleep(0.65)
print("Closing credstick poller...")
sleep(0.5)
m.join()


price_poller_thread_shutdown = True
print("Waiting for price poller to shut down...")
sleep(0.2)
p.join()

eth_node.shutdown = True
sleep(0.3)
print("Closing connection to ethereum node...")
t.join()


exit()


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


