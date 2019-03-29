from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.tui.debug import debug
from shadowlands.credstick import DeriveCredstickAddressError
import threading 
from time import sleep
import pdb

class HDAddressPicker(SLDapp):
    def initialize(self):
        self.range_base = 0
        self.range_index = 10

        self.show_wait_frame("Deriving Addresses...")
        threading.Thread(target=self._worker).start()

    def _worker(self):
        try:
            self.add_frame(PathPickerFrame, height=20, width=80, title="Select HDPath / Address")
        except DeriveCredstickAddressError:
            self.hide_wait_frame()
            self.add_message_dialog("Your credstick refused to generate addresses")

class PathPickerFrame(SLFrame):
       
    def initialize(self):
        self.add_label(
            "HD Paths [{}-{}]:".format(
                self.dapp.range_base, 
                self.dapp.range_index - 1
            ) 
        )
        self.index_list_value = self.add_listbox(
            10, 
            self._build_hdpaths(
                range(
                    self.dapp.range_base, 
                    self.dapp.range_index
                )
            ), 
            on_select=self.choose_address
        )

        self.add_button_row(
            [
                ("Prev 10", self.prev_10, 2),
                ("Next 10", self.next_10, 3),
            ]
        )

        self.add_divider(draw_line=False)

        self.pathbox_value = self.add_textbox("HD Path Base", default_value=self.dapp.node.credstick.hdpath_base)

        self.add_button_row(
            [
                ("Change HDPath base", self.change_base, 0),
                ("Cancel", self.close, 3)
            ]
        )

        self.dapp.hide_wait_frame()

    def next_10(self):
        self.dapp.range_base += 10
        self.dapp.range_index += 10
        self.dapp.show_wait_frame("Deriving addresses...")
        threading.Thread(target=self.dapp._worker).start()
        self.close()

    def prev_10(self):
        if self.dapp.range_base < 1:
            return

        self.dapp.range_base -= 10
        self.dapp.range_index -= 10
        self.dapp.show_wait_frame("Deriving addresses...")
        threading.Thread(target=self.dapp._worker).start()
        self.close()

    def _build_hdpaths(self, index_range):
        return [ 
            (
                self.path_string(path_element), 
                str(path_element)
            )
            for path_element in index_range 
        ]

    def path_string(self, path_element):
        address = self.dapp.node.credstick.derive( hdpath_base=self.dapp.node.credstick.hdpath_base, hdpath_index=str(path_element))

        try:
            bal = self.dapp.node.w3.fromWei(self.dapp.node.w3.eth.getBalance(address), 'ether')
            if bal is not None and bal != 0:
                bal = "  Ξ" + str(round(bal,5))
            else: 
                bal = '  Ξnull   ' 
        except:
            bal = ''

        try:
            ens_name = '  ' + self.dapp.node._ns.name(address)
        except:
            ens_name = '  No Reverse ENS'

        return str(path_element) +  ' ' + address + bal + ens_name

    def change_base(self):
        try:
            # if the credstick hdpathbase is different from what's
            # in the pathbox, derive.
            if self.dapp.node.credstick.hdpath_base == self.pathbox_value():
                self.close()
                return

            self.dapp.node.credstick.derive(
                hdpath_base=self.pathbox_value(),
                hdpath_index=self.dapp.node.credstick.hdpath_index,
                set_address=True
            )

            self.dapp.config.hd_base_path = self.pathbox_value()
        except DeriveCredstickAddressError:
            self.dapp.add_message_dialog("Could not derive address from your credstick")

        self.close()

    def choose_address(self):
        try:
            self.dapp.node.credstick.derive(
                hdpath_base=self.dapp.node.credstick.hdpath_base,
                hdpath_index=self.index_list_value(),
                set_address=True
            )
        except DeriveCredstickAddressError:
            self.dapp.add_message_dialog("Could not derive address from your credstick")
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

