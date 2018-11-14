from shadowlands.sl_dapp import SLDapp, SLFrame
from shadowlands.tui.debug import debug
import pdb

class QRCodeDisplay(SLDapp):
    def initialize(self):
        self.add_frame(QRFrame, height=20, width=35)

class QRFrame(SLFrame):
    def initialize(self):
        self.add_qrcode(self.dapp.node.credstick.address)
        self.add_button(self.close, 'OK')
