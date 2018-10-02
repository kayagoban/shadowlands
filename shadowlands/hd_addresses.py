from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.tui.debug import debug
from shadowlands.credstick import DeriveCredstickAddressError
import pdb

class HDAddressPicker(SLDapp):
    def initialize(self):
        try:
            self.add_frame(PathPickerFrame, height=20, width=78, title="Select HDPath / Address")
        except DeriveCredstickAddressError:
            self.add_message_dialog("Your credstick refused to generate addresses")


class PathPickerFrame(SLFrame):
    def initialize(self):
        self.pathbox_value = self.add_textbox("HD Path Base", default_value=self.dapp.node.credstick.hdpath_base)
        self.add_button(self.change_base, "Change HDPath base")

        self.add_label("HD Paths [0-9]:")
        self.index_list_value = self.add_listbox(10, self._build_hdpaths(), on_select=self.choose_address)

        self.add_button(self.close, "Cancel")

    def _build_hdpaths(self):
        return [ 
            (
                self.path_string(path_element), 
                str(path_element)
            )
            for path_element in range(10)
        ]

    def path_string(self, path_element):
        address = self.dapp.node.credstick.derive( hdpath_base=self.dapp.node.credstick.hdpath_base, hdpath_index=str(path_element))

        
        '''
        bal = self.dapp.node.w3.fromWei(self.dapp.node.w3.eth.getBalance(address), 'ether')
        if bal is not None and bal != 0:
            bal = "  Ξ" + str(round(bal,5))
        else: 
            bal = ''
        try:
            ens_name = '  ' + self.dapp.node._ns.name(address)
        except:
            ens_name = ''
            '''

        return address #+ bal  + ens_name

# + self.dapp.node.credstick.hdpath_base + '/' +str(path_element)
    def change_base(self):
        self.dapp.node.credstick.derive(
            hdpath_base=self.pathbox_value(),
            hdpath_index=self.dapp.node.credstick.hdpath_index,
            set_address=True
        )
        self.close()

    def choose_address(self):
        self.dapp.node.credstick.derive(
            hdpath_base=self.dapp.node.credstick.hdpath_base,
            hdpath_index=self.index_list_value(),
            set_address=True
        )
        self.close()






    def _derive(self):
        self.dapp.node.credstick.derive(hdpath=self.pathbox_value())
        self.close()

'''44'/60'/0'/0/0
0xc7fBcad991C6FAAb188c615408Af3cebbf1FE2dF
'''

'''44'/60'/0'/0/1
0x35373597A64cDe438D24331a09B5A51009EE4e6f
'''



'''44'/60'/0'/0
0xC579e6BF41789dEeF2E0AaCa8fBb8b0F0c762898
'''

'''44'/60'/0'/1
0x5c27053A642B8dCc79385f47fCB25b5e72348feD
'''

