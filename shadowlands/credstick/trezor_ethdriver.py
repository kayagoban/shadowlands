
import sys
from time import sleep

import getpass

from trezorlib.client import ProtocolMixin, BaseClient 
from trezorlib.transport import enumerate_devices, get_transport, TransportException
from trezorlib import tools
from trezorlib import messages as proto 
import binascii
from eth_utils import decode_hex

from eth_account.internal.transactions import serializable_unsigned_transaction_from_dict

from shadowlands.credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
from shadowlands.tui.effects.message_dialog import MessageDialog 
from shadowlands.tui.effects.text_request_dialog import TextRequestDialog
from shadowlands.tui.debug import debug, end_debug
from web3 import Web3
import pdb

import logging
logging.basicConfig(level = logging.INFO, filename = "shadowlands.eth_node.log")


# The Trezor protocol is a dumpster fire of shitty design
# caused by the inability to authenticate without client
# side intervention.
#
# I hope you enjoy using this because I bled for its
# implementation.
#
class TrezorEthDriver(Credstick):
    transport = None
    state = None
    hdpath_base="44'/60'/0'/0"
    hdpath_index = '0'

    @classmethod
    def call_raw(cls, msg, atomic=True):
        #__tracebackhide__ = True  # pytest traceback hiding - this function won't appear in tracebacks

        cls.transport.begin_session()
        logging.info("call_raw transport.write(msg): %s", msg)
        cls.transport.write(msg)
        response = cls.transport.read()

        if atomic:
            cls.transport.end_session()

        return response

    @classmethod
    def open(cls):
        #pdb.set_trace()
        try:
            cls.transport = get_transport(None, prefix_search=False)
        except StopIteration as e:
           debug(); pdb.set_trace()
 
        init_msg = proto.Initialize()

        if cls.state is not None:
            init_msg.state = cls.state

        try:
            cls.features = cls.call_raw(init_msg)
            logging.info("call_raw transport.write(msg): %s", init_msg)
        except (TransportException):
            raise OpenCredstickError("Error opening Trezor")

    #self.features = expect(proto.Features)(self.call)(init_msg)

        #if str(cls.features.vendor) not in self.VENDORS:
        #    raise RuntimeError("Unsupported device")

        #cls.address = cls.derive()


    @classmethod
    def matrix_process(cls, text, calling_window):
        response = cls.call_raw(proto.PinMatrixAck(pin=text))
        if response.__class__.__name__ is 'EthereumAddress':
            address = '0x' + binascii.hexlify(response.address).decode('ascii')
            address = cls.eth_node.w3.toChecksumAddress(address)
            cls.address = address
        elif response.__class__.__name__ == 'PassphraseRequest':
            cls.passphrase_request_window()
        else:
            calling_window._scene.add_effect(MessageDialog(calling_window._screen, "Trezor is unlocked now.", destroy_window=calling_window))
            # open a message dialog, tell them they are now authenticated and to try whatever they were doing again

    @classmethod
    def passphrase_process(cls, text, calling_window):
        response = cls.call_raw(proto.PassphraseAck(passphrase=text))
        if response.__class__.__name__ is 'EthereumAddress':
            address = '0x' + binascii.hexlify(response.address).decode('ascii')
            address = cls.eth_node.w3.toChecksumAddress(address)
            cls.address = address
        else:
            calling_window._scene.add_effect(MessageDialog(calling_window._screen, "Trezor is unlocked now.", destroy_window=calling_window))
            # open a message dialog, tell them they are now authenticated and to try whatever they were doing again



    @classmethod
    def matrix_request_window(cls):
        legend = '''Use the numeric keypad to describe number positions. 
The layout is:
                  7 8 9
                  4 5 6
                  1 2 3'''
        scr = cls.interface._screen
        dialog = TextRequestDialog(scr, 
                                   height=13,
                                   width = 60,
                                   label_prompt_text=legend,
                                   label_height=5, 
                                   continue_button_text="Unlock",
                                   continue_function=cls.matrix_process,
                                   text_label="Your code:",
                                   hide_char="*",
                                   label_align="<",
                                   title="Trezor Auth",
                                   reset_scene=False
                                  )
        scr.current_scene.add_effect( dialog )

    @classmethod
    def passphrase_request_window(cls):
        scr = cls.interface._screen
        dialog = TextRequestDialog(scr, 
                                   height=9,
                                   width = 65,
                                   label_prompt_text="Enter your Trezor passphrase to unlock",
                                   label_height=1, 
                                   continue_button_text="Unlock",
                                   continue_function=cls.passphrase_process,
                                   text_label="Trezor Passphrase:",
                                   hide_char="*",
                                   label_align="<",
                                   title="Trezor Auth",
                                   reset_scene=False
                                  )
        scr.current_scene.add_effect( dialog )


 
    @classmethod
    def derive(cls, hdpath_base="44'/60'/0'/0", hdpath_index='0', set_address=False):
        logging.info("Attempting to derive %s/%s", hdpath_base, hdpath_index)

        hdpath = hdpath_base + '/' + hdpath_index
        address_n = tools.parse_path(hdpath)
        call_obj = proto.EthereumGetAddress(address_n=address_n, show_display=False)
        try:
            response = cls.call_raw(call_obj)

            while response.__class__.__name__ == 'ButtonRequest':
                response = cls.call_raw(proto.ButtonAck())

            if response.__class__.__name__ == 'PinMatrixRequest':
                cls.matrix_request_window()
            elif response.__class__.__name__ == 'PassphraseRequest':
                cls.passphrase_request_window()
            elif response.__class__.__name__ == 'Failure':
                raise DeriveCredstickAddressError
            else:
                logging.info("trezor response address: 0x%s", response)
                address = response.address
                if set_address is True:
                    cls.address = address
                    cls.hdpath_base = hdpath_base
                    cls.hdpath_index = hdpath_index
                    cls.config.hd_index = hdpath_index
                    cls.config.hd_base_path = hdpath_base

                return address

        except TransportException:
            raise DeriveCredstickAddressError



    @classmethod
    def signTx(cls, tx):

        def int_to_big_endian(value):
            return value.to_bytes((value.bit_length() + 7) // 8, 'big')

        address_n = tools.parse_path(cls.hdpath())
 
        msg = proto.EthereumSignTx(
            address_n=address_n,
            nonce=int_to_big_endian(tx['nonce']),
            gas_price=int_to_big_endian(tx['gasPrice']),
            gas_limit=int_to_big_endian(tx['gas']),
            chain_id=int(tx['chainId']),
            value=int_to_big_endian(tx['value']))

        if tx['to']:
            msg.to = tx['to']

        if tx['data'].__class__ is str:
            data = bytes.fromhex(tx['data'].replace('0x',''))
        elif tx['data'].__class__ is bytes:
            data = tx['data']

        if data:
            msg.data_length = len(data)
            data, chunk = data[1024:], data[:1024]
            msg.data_initial_chunk = chunk

        try:
            response = cls.call_raw(msg, atomic=False)
    
            # Confused?   Ask trezor why.  I don't know why.
            # ButtonAck is a no-op afaict.  But you still have to send it.
            # Punch the monkey.
            # Punch it.
            # Punch the monkey.
            # Punch the monkey.
            # Punch the monkey.
            while response.__class__.__name__ == 'ButtonRequest':
                response = cls.call_raw(proto.ButtonAck())

            if response.__class__.__name__ == 'PinMatrixRequest':
                cls.matrix_request_window()
                raise SignTxError("Credstick needs to be unlocked")
            elif response.__class__.__name__ == 'PassphraseRequest':
                cls.passphrase_request_window()
                raise SignTxError("Credstick needs to be unlocked")
            elif response.__class__.__name__ == 'Failure':
                raise SignTxError

        except TransportException:
            raise SignTxError

        while response.data_length is not None:
            data_length = response.data_length
            data, chunk = data[data_length:], data[:data_length]
            response = cls.call_raw(
                proto.EthereumTxAck(data_chunk=chunk), 
                atomic=False
            )

        # above, we were calling out with atomic=False to 
        # prevent the session from being terminated.
        cls.transport.end_session()

        _v = response.signature_v
        _r = response.signature_r
        _s = response.signature_s

        sutx = serializable_unsigned_transaction_from_dict(tx)

        return cls.signed_tx(sutx, _v, int(_r.hex(), 16), int(_s.hex(), 16))


    @classmethod
    def close(cls):
        pass


class SomeException(Exception):
    pass


