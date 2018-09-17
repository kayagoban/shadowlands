
import sys
from time import sleep

import getpass

from trezorlib.client import ProtocolMixin, BaseClient 
from trezorlib.transport import enumerate_devices, get_transport
from trezorlib import tools
from trezorlib import messages as proto 
import binascii

from shadowlands.credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
from shadowlands.tui.effects.widgets import TextRequestDialog

from shadowlands.tui.debug import debug



'''
    @session
    def call_raw(self, msg):
        __tracebackhide__ = True  # pytest traceback hiding - this function won't appear in tracebacks
        self.transport.write(msg)
        return self.transport.read()

    @session
    def call(self, msg):
        resp = self.call_raw(msg)
        handler_name = "callback_%s" % resp.__class__.__name__
        handler = getattr(self, handler_name, None)

        if handler is not None:
            msg = handler(resp)
            if msg is None:
                raise ValueError("Callback %s must return protobuf message, not None" % handler)
            resp = self.call(msg)

        return resp


    @field('address')
    @expect(proto.EthereumAddress)
    def ethereum_get_address(self, n, show_display=False, multisig=None):
        n = self._convert_prime(n)
        return self.call(proto.EthereumGetAddress(address_n=n, show_display=show_display))

    @session
    def ethereum_sign_tx(self, n, nonce, gas_price, gas_limit, to, value, data=None, chain_id=None, tx_type=None):
        def int_to_big_endian(value):
            return value.to_bytes((value.bit_length() + 7) // 8, 'big')

        n = self._convert_prime(n)

        msg = proto.EthereumSignTx(
            address_n=n,
            nonce=int_to_big_endian(nonce),
            gas_price=int_to_big_endian(gas_price),
            gas_limit=int_to_big_endian(gas_limit),
            value=int_to_big_endian(value))

        if to:
            msg.to = to

        if data:
            msg.data_length = len(data)
            data, chunk = data[1024:], data[:1024]
            msg.data_initial_chunk = chunk

        if chain_id:
            msg.chain_id = chain_id

        if tx_type is not None:
            msg.tx_type = tx_type

        response = self.call(msg)

        while response.data_length is not None:
            data_length = response.data_length
            data, chunk = data[data_length:], data[:data_length]
            response = self.call(proto.EthereumTxAck(data_chunk=chunk))

        return response.signature_v, response.signature_r, response.signature_s

    @expect(proto.EthereumMessageSignature)
    def ethereum_sign_message(self, n, message):
        n = self._convert_prime(n)
        message = normalize_nfc(message)
        return self.call(proto.EthereumSignMessage(address_n=n, message=message))

    def ethereum_verify_message(self, address, signature, message):
        message = normalize_nfc(message)
        try:
            resp = self.call(proto.EthereumVerifyMessage(address=address, signature=signature, message=message))
        except CallException as e:
            resp = e
        if isinstance(resp, proto.Success):
            return True
        return False

    def init_device(self):
        init_msg = proto.Initialize()
        if self.state is not None:
            init_msg.state = self.state
        self.features = expect(proto.Features)(self.call)(init_msg)
        if str(self.features.vendor) not in self.VENDORS:
            raise RuntimeError("Unsupported device")

'''

class TrezorEthDriver(Credstick):
    transport = None
    state = None

    @classmethod
    def call_raw(cls, msg):
        #__tracebackhide__ = True  # pytest traceback hiding - this function won't appear in tracebacks
        cls.transport.session_begin()
        cls.transport.write(msg)
        response = cls.transport.read()
        cls.transport.session_end()
        return response

    @classmethod
    def open(cls):
        sleep(2)
        cls.transport = get_transport(None, prefix_search=False)
 
        init_msg = proto.Initialize()

        if cls.state is not None:
            init_msg.state = cls.state
        cls.features = cls.call_raw(init_msg)
        #self.features = expect(proto.Features)(self.call)(init_msg)

        #if str(cls.features.vendor) not in self.VENDORS:
        #    raise RuntimeError("Unsupported device")

        #cls.address = cls.derive()

    @classmethod
    def matrix_process(cls, text, calling_window):
        response = cls.call_raw(proto.PinMatrixAck(pin=text))
        calling_window._destroy_window_stack()
 
    @classmethod
    def derive(cls, path="44'/60'/0'/0/0"):
        #address = "44'/60'/0'/0"  # ledger so-called standard
        #address = "44'/60'/0'/0/0"  # trezor standard
        #n = self._convert_prime(n)
        address_n = tools.parse_path(path)
        call_obj = proto.EthereumGetAddress(address_n=address_n, show_display=False)
        response = cls.call_raw(call_obj)
        if response.__class__.__name__ == 'PinMatrixRequest':
            legend = '''Use the numeric keypad to describe number positions. 
The layout is:
                      7 8 9
                      4 5 6
                      1 2 3'''
            scr = cls.interface._screen
            dialog = TextRequestDialog(scr, 
                                       height=14,
                                       width = 60,
                                       label_prompt_text=legend,
                                       label_height=5, 
                                       continue_button_text="Unlock",
                                       continue_function=cls.matrix_process,
                                       text_label="Your code:",
                                       hide_char="*",
                                       label_align="<",
                                       title="Trezor Auth"
                                      )
            scr.current_scene.add_effect( dialog )
            return None
        elif response.__class__.__name__ == 'Failure':
            return None
        else:
            address = '0x' + binascii.hexlify(response.address).decode('ascii')
            cls.address = cls.eth_node.w3.toChecksumAddress(address)
            return cls.address

        #result = "0x%s" % binascii.hexlify(address).decode()
        #return result


class NotImplementedError(Exception):
    pass

class SLMixin(object):
    # This class demonstrates easy test-based UI
    # integration between the device and wallet.
    # You can implement similar functionality
    # by implementing your own GuiMixin with
    # graphical widgets for every type of these callbacks.

    def __init__(self, *args, interface=None, **kwargs):
        super(SLMixin, self).__init__(*args, **kwargs)
        self.screen  = interface._screen

    def callback_PinMatrixRequest(self, msg):
        self.screen.current_scene.add_effect(YesNoDialog(self.screen, 15, 45) )
        #import pdb; pdb.set_trace()
        #raise NotImplementedError("Trezor pin matrix request not yet implemented")
    '''
        if msg.type == proto.PinMatrixRequestType.Current:
            desc = 'current PIN'
        elif msg.type == proto.PinMatrixRequestType.NewFirst:
            desc = 'new PIN'
        elif msg.type == proto.PinMatrixRequestType.NewSecond:
            desc = 'new PIN again'
        else:
            desc = 'PIN'

        self.print("Use the numeric keypad to describe number positions. The layout is:")
        self.print("    7 8 9")
        self.print("    4 5 6")
        self.print("    1 2 3")
        self.print("Please enter %s: " % desc)
        pin = getpass.getpass('')
        if not pin.isdigit():
            raise ValueError('Non-numerical PIN provided')
        return proto.PinMatrixAck(pin=pin)
'''


    @staticmethod
    def print(text):
        print(text, file=sys.stderr)

    def callback_ButtonRequest(self, msg):
        # log("Sending ButtonAck for %s " % get_buttonrequest_value(msg.code))
        return proto.ButtonAck()

    def callback_RecoveryMatrix(self, msg):
        raise NotImplementedError("Trezor revovery matrix not yet implemented")
    '''
        if self.recovery_matrix_first_pass:
            self.recovery_matrix_first_pass = False
            self.print("Use the numeric keypad to describe positions.  For the word list use only left and right keys.")
            self.print("Use backspace to correct an entry.  The keypad layout is:")
            self.print("    7 8 9     7 | 9")
            self.print("    4 5 6     4 | 6")
            self.print("    1 2 3     1 | 3")
        while True:
            character = getch()
            if character in ('\x03', '\x04'):
                return proto.Cancel()

            if character in ('\x08', '\x7f'):
                return proto.WordAck(word='\x08')

            # ignore middle column if only 6 keys requested.
            if msg.type == proto.WordRequestType.Matrix6 and character in ('2', '5', '8'):
                continue

            if character.isdigit():
                return proto.WordAck(word=character)
'''

    def callback_PassphraseRequest(self, msg):
        raise NotImplementedError("Trezor passphrase request not yet implemented")
    '''
        if msg.on_device is True:
            return proto.PassphraseAck()

        if os.getenv("PASSPHRASE") is not None:
            self.print("Passphrase required. Using PASSPHRASE environment variable.")
            passphrase = Mnemonic.normalize_string(os.getenv("PASSPHRASE"))
            return proto.PassphraseAck(passphrase=passphrase)

        self.print("Passphrase required: ")
        passphrase = getpass.getpass('')
        self.print("Confirm your Passphrase: ")
        if passphrase == getpass.getpass(''):
            passphrase = Mnemonic.normalize_string(passphrase)
            return proto.PassphraseAck(passphrase=passphrase)
        else:
            self.print("Passphrase did not match! ")
            exit()
'''

    def callback_PassphraseStateRequest(self, msg):
        raise NotImplementedError("Trezor passphrase state request not yet implemented")
        #return proto.PassphraseStateAck()

    def callback_WordRequest(self, msg):
        raise NotImplementedError("Trezor word request not yet implemented")
    '''
        if msg.type in (proto.WordRequestType.Matrix9,
                        proto.WordRequestType.Matrix6):
            return self.callback_RecoveryMatrix(msg)
        self.print("Enter one word of mnemonic: ")
        word = input()
        if self.expand:
            word = self.mnemonic_wordlist.expand_word(word)
        return proto.WordAck(word=word)
'''
    '''
from trezorlib import (
    btc,
    cardano,
    coins,
    cosi,
    debuglink,
    device,
    ethereum,
    firmware,
    lisk,
    log,
    messages as proto,
    misc,
    nem,
    ontology,
    protobuf,
    ripple,
    stellar,
    tools,
)
'''

class SLTrezorClient(ProtocolMixin, SLMixin, BaseClient):
    def __init__(self, transport, *args, **kwargs):
        super().__init__(transport=transport, *args, **kwargs)


#TrezorEthDriver.derive()
