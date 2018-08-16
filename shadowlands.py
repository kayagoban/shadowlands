
import npyscreen, os, hashlib, argparse, struct
from pyfiglet import Figlet
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException

def file_checksum():
    script_path = os.path.abspath(__file__)
    shahash = hashlib.sha256()
    with open(script_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            shahash.update(chunk)
    return shahash.hexdigest()


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
    return result

def ledgerPublicAddress()
    donglePath = parse_bip32_path(args.path)
#apdu = "e0020100".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath
    apdu = "e0020000".decode('hex') + chr(len(donglePath) + 1) + chr(len(donglePath) / 4) + donglePath

    dongle = getDongle(True)
    result = dongle.exchange(bytes(apdu))
    offset = 1 + result[0]
    address = result[offset + 1 : offset + 1 + result[offset]]

    print "Public key " + str(result[1 : 1 + result[0]]).encode('hex')
    print "Address 0x" + str(address)
    return address


## Loading Screen

os.system('clear')
print '[ '+ file_checksum() + ' ]'
print Figlet(font='slant').renderText('Shadowlands') 
print 'by CeilingCat\t\t' + 'v0.01\t\t' 
print '\n\n\n\n\n'

input('Welcome, chummer.  Insert your credstick to log in.\n\n')
#print('Welcome, chummer.  Insert your credstick to log in.\n\n')



#input('Welcome, chummer.  Insert your credstick to log in.\n\n')
   #     or just press enter to begin without an account.\n')


class MyTestApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.registerForm("MAIN", MainForm())

# This form class defines the display that will be presented to the user.

class MainForm(npyscreen.Form):
    def create(self):

        self.add(npyscreen.TitleText, name = "Text:", value= "Hellow World!" )

    def afterEditing(self):
        self.parentApp.setNextForm(None)

if __name__ == '__main__':
    TA = MyTestApp()
    TA.run()




