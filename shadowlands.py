import npyscreen, sys, os, hashlib, argparse, struct, time, locale, qrcode_terminal
from pyfiglet import Figlet
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException
from web3.auto.infura import w3

# Get a connection

"""
try:
    connected = w3.isConnected()
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
except(TypeError)
    os.environ['INFURA_API_KEY'] = '3404d141198b45b191c7af24311cd9ea'
    from web3.auto.infura import w3
    try:
        w3.isConnected()
    except(TypeError)

    printf("Sorry chummer, couldn't find a node.")
        exit()
""" 

#throws  web3.utils.threads.Timeout
if not w3.isConnected():
    from web3.auto import w3
    if connected and w3.version.node.startswith('Parity'):
        enode = w3.parity.enode
    elif connected and w3.version.node.startswith('Geth'):
        enode = w3.admin.nodeInfo['enode']
    else:
        printf("Sorry chummer, couldn't find a node.")
        exit()

# Check the file for tampering
def file_checksum():
    script_path = os.path.abspath(__file__)
    shahash = hashlib.sha256()
    with open(script_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shahash.update(chunk)
    return shahash.hexdigest()


def ledgerEthAddress():
    dongle = getDongle(False)
    result = dongle.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]
    return address

## Loading Screen
#print('[ '+ file_checksum() + ' ]')
def loadingScreen():
    os.system("clear")
    print('Connected to ' + w3.version.node)
    print('[block ' + str(w3.eth.blockNumber) + ']')
    print(Figlet(font='slant').renderText('Shadowlands') )
    print('public terminal \t\t' + 'v0.01' )
    print( '\n\n\n\n\n' )
    print('Welcome, chummer.  Insert your credstick to log in.\n\n')
    return

def headerLine():
    return print('Welcome, ' + ethAddress + '\t[block ' + str(w3.eth.blockNumber) + ']')

boxDictionary = {
'\\' : b'\xe2\x95\x9a',
'-'  : b'\xe2\x95\x90',
'/'  : b'\xe2\x95\x9d',
'|'  : b'\xe2\x95\x91',
'+'  : b'\xe2\x95\x94',
'%'  : b'\xe2\x95\x97',
}

def boxDecode(x):
    return (''.join(boxDictionary.get(i, i.encode('utf-8')).decode('utf-8') for i in x))

def ethBalance(address):
    bal = w3.eth.getBalance(address)
    return str(w3.fromWei(bal, 'ether'))

def mainMenu():
    os.system("clear")
    headerLine()
    print('\n')
    print(boxDecode('  +- Account Balances ------------------%'))
    print(boxDecode('  |                                    '))
    print(boxDecode('  |  Ξth: ' + ethBalance(ethAddress) + ''))
    print(boxDecode('  |  Dai: ' + ethBalance(ethAddress) + ''))
    print(boxDecode('  \\------------------------------------/'))
    return




loadingScreen()

while True:
    try: 
        #address = ledgerPublicAddress()
        address = ledgerEthAddress()
        break
    except(CommException, IOError):
        time.sleep(1.5)
        loadingScreen()

ethAddress = '0x' + address.decode('utf-8') 
        
mainMenu()


input()




# o = qrcode_terminal.qr_terminal_str('0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898', 1)

"""
def parse_bip32_path(path="44'/60'/0'/0"):
    if len(path) == 0:
        return ""
    result = ""
    elements = path.split('/')
    for pathElement in elements:
        element = pathElement.split('\'')
        if len(element) == 1:
            result = result + struct.pack(">I", int(element[0]))
        else:
            result = result + struct.pack(">I", 0x80000000 | int(element[0]))
            print("element[0]: " + element[0])
            print( "pathcode: " + (struct.pack(">I", 0x80000000 | int(element[0]))).encode('hex'))

    return result

def ledgerPublicAddress():
    donglePath = parse_bip32_path()
#apdu = "e0020100".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath
    apdu = "e0020000".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath

    dongle = getDongle(True)
    print 'donglepath: ' + donglePath.encode('hex')
    print "Apdu: " + bytes(apdu).encode('hex')
    #print "Apdu bytes: " + bytes(apdu)
    result = dongle.exchange(bytes(apdu))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]

 #   print "Public key " + str(result[1 : 1 + result[0]]).encode('hex')
 #   print "Address 0x" + str(address)
    return address
"""


