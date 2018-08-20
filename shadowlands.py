#!/usr/bin/env python

import npyscreen, sys, os, hashlib, argparse
import struct, time, locale, qrcode_terminal, threading
import tty, termios
from pyfiglet import Figlet
import eth_node
from hid_probe import find_credstick
from credstick import Credstick, DeriveError, OpenError, CloseError

#import credstick 
#from credstick import AddressError

# import pdb; pdb.set_trace()

menuSelection = None
credstick = None

networkName = {
    '1': 'MainNet',
    '2': 'Morden',
    '3': 'Ropsten',
    '4': 'Rinkeby',
    '42': 'Kovan'
}

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


# Get a connection
eth_node.connect()
t = threading.Thread(target=eth_node.heartbeat)
t.start()

def header():
    if eth_node.localNode:
        nodeString = 'local' 
    else:
        nodeString = 'infura'

    print('Connected to ' + nodeString + ' node at ' + eth_node.nodeVersion)


    if not eth_node.syncing:
        print('[synced: block ' + eth_node.block + ']' + '\t\tNetwork: ' + networkName[eth_node.network]) 
    else:
        print('[syncing:  ' + str(eth_node.blocksBehind) + ' blocks to ' 
              + str(eth_node.syncing['highestBlock']) + ']' +  '\t\tNetwork: ' + networkName[eth_node.network]) 
 
def loadingScreen():
    os.system("clear")
    header()       
    print(Figlet(font='slant').renderText('Shadowlands') )
    print('public terminal \t\t' + 'v0.01' )
    print( '\n\n\n\n\n' )
    print('Welcome, chummer.  Insert your credstick to log in.')
    return

def mainMenu():
    os.system("clear")
    header()
    print('\n')
    print(boxDecode("  +- %s %s ---------------------------------------$") 
          %(credstick.manufacturerStr, credstick.productStr))
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  Address: %s' ) %(credstick.addressStr()) )
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  Ξth: ' + eth_node.ethBalanceStr() + ''))
    print(boxDecode('  |  Dai: ' ))
    print(boxDecode('  |                                    '))
    print(boxDecode('  \\-------------------------------------------------------/'))
    print('\n')
    print(boxDecode('  +- Things to do -------------------------------------$'))
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  (S)end ether and tokens '))
    print(boxDecode('  |  (B)rowse your transaction history '))
    print(boxDecode('  |  (C)opy your address to the system clipboard '))
    print(boxDecode('  |  (V)iew your address QRcode '))
    print(boxDecode('  |  (T)rade Ether for Dai '))
    print(boxDecode('  |  (O)pen a CDP loan [borrow dai against your ether]'))
    print(boxDecode('  |  (R)egister your ENS name '))
    print(boxDecode('  |  (C)hat on the whispernet '))
    print(boxDecode('  |  (P)ublic forums '))
    print(boxDecode('  |  (B)rowse the take-out menu '))
    print(boxDecode('  |                                    '))
    print(boxDecode('  \\----------------------------------------------------/'))
    print('\n  Type the letter of your selection and hit enter:')
 
    return

def blastOff():
    sys.stdout.write("\033[F")
    timeout = 0.11
    for x in range(70):
      time.sleep(timeout)
      sys.stdout.write(".")
      sys.stdout.flush()
      timeout = timeout * 0.93
    return


def mainMenuLoop():
    global menuSelection, old_settings
    while menuSelection is None:
        mainMenu()
        time.sleep(0.25)


# Begin screen displays

loadingScreen()

while True:
    try: 
        credstick = find_credstick()
        credstick.open()
        eth_node.ethAddress = credstick.derive()
        eth_node.poll()
        blastOff()

        break
    except(NoCredstickFoundError, DeriveError):
        time.sleep(0.25)
        loadingScreen()


# Show main menu in a thread to provide live updates
m = threading.Thread(target=mainMenuLoop)
m.start()


menuSelection = input()
m.join()


os.system("clear")
print( "You selected " + menuSelection.upper())

import pdb; pdb.set_trace()


# Check the file for tampering
def file_checksum():
    script_path = os.path.abspath(__file__)
    shahash = hashlib.sha256()
    with open(script_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shahash.update(chunk)
    return shahash.hexdigest()




#import subprocess
#subprocess.call(["/usr/bin/open", 'http://apple.com'])


#import pyperclip
#pyperclip.copy('The text to be copied to the clipboard.')

# o = qrcode_terminal.qr_terminal_str('0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898', 1)


