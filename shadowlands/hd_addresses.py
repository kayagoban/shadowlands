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
        self.add_sl_frame(PathPickerFrame(self, 6, 25, title="Select HDPath"))

class PathPickerFrame(SLFrame):
       
    def initialize(self):
        self.add_divider()
        self.pathbox_value = self.add_textbox("", default_value=self.dapp.node.credstick.hdpath)
        self.add_button_row(
            [
                ("Ok", self.change_path, 2),
            ]
        )
        self.dapp.hide_wait_frame()

    def change_path(self):
        try:
            # if the credstick hdpathbase is different from what's
            # in the pathbox, derive.
            if self.dapp.node.credstick.hdpath == self.pathbox_value():
                self.close()
                return

            self.dapp.node.credstick.derive(
                hdpath=self.pathbox_value(),
                set_address=True
            )

            self.dapp.config.hdpath = self.pathbox_value()
            #self.dapp.node._update_status()
        except DeriveCredstickAddressError:
            self.dapp.add_message_dialog("Could not derive address from your credstick")

        self.close()


