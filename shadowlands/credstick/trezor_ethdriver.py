
import sys
from time import sleep

import getpass

from trezorlib.client import ProtocolMixin, BaseClient 
from trezorlib.transport import enumerate_devices, get_transport, TransportException
from trezorlib import tools
from trezorlib import messages as proto 
import binascii

from shadowlands.credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
from shadowlands.tui.effects.widgets import TextRequestDialog, MessageDialog

from shadowlands.tui.debug import debug
import pdb


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
        try:
            cls.transport = get_transport(None, prefix_search=False)
        except StopIteration as e:
           debug(); pdb.set_trace()
 
        init_msg = proto.Initialize()

        if cls.state is not None:
            init_msg.state = cls.state

        try:
            cls.features = cls.call_raw(init_msg)
        except TransportException:
            raise OpenCredstickError("Error opening Trezor")

    #self.features = expect(proto.Features)(self.call)(init_msg)

        #if str(cls.features.vendor) not in self.VENDORS:
        #    raise RuntimeError("Unsupported device")

        #cls.address = cls.derive()

 
            #debug(); pdb.set_trace()
        #calling_window._destroy_window_stack()
        #calling_window._scene.remove_effect(calling_window)
        #calling_window._scene.reset()

    @classmethod
    def matrix_process(cls, text, calling_window):
        response = cls.call_raw(proto.PinMatrixAck(pin=text))
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
                                   height=14,
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
    def derive(cls, path="44'/60'/0'/0/0"):
        #address = "44'/60'/0'/0"  # ledger so-called standard
        #address = "44'/60'/0'/0/0"  # BIP44 standard (trezor)
        address_n = tools.parse_path(path)
        call_obj = proto.EthereumGetAddress(address_n=address_n, show_display=False)
        response = cls.call_raw(call_obj)
        if response.__class__.__name__ == 'PinMatrixRequest':
            cls.matrix_request_window()
            return None
        elif response.__class__.__name__ == 'Failure':
            return None
        else:
            address = '0x' + binascii.hexlify(response.address).decode('ascii')
            cls.address = cls.eth_node.w3.toChecksumAddress(address)
            return cls.address

        #result = "0x%s" % binascii.hexlify(address).decode()
        #return result



    @classmethod
    def signTx(cls, tx, path="44'/60'/0'/0/0"):

        def int_to_big_endian(value):
            return value.to_bytes((value.bit_length() + 7) // 8, 'big')

        tx = cls.prepare_tx(tx)

        #n = self._convert_prime(n)
        address_n = tools.parse_path(path)
 
        msg = proto.EthereumSignTx(
            address_n=address_n,
            nonce=int_to_big_endian(tx['nonce']),
            gas_price=int_to_big_endian(tx['gasPrice']),
            gas_limit=int_to_big_endian(tx['gas']),
            chain_id=int(cls.eth_node._network),
            value=int_to_big_endian(tx['value']))

        if tx['to']:
            msg.to = tx['to']

        data = tx['data']
        if data:
            msg.data_length = len(data)
            data, chunk = data[1024:], data[:1024]
            msg.data_initial_chunk = chunk

        #if chain_id:
        #    msg.chain_id = chain_id

        #if tx_type is not None:
        #    msg.tx_type = tx_type

        try:
            response = cls.call_raw(msg)

            # This is dumb.
            while response.__class__.__name__ == 'ButtonRequest':
                response = cls.call_raw(proto.ButtonAck())

            if response.__class__.__name__ == 'PinMatrixRequest':
                cls.matrix_request_window()
                raise SignTxError("Credstick needs to be unlocked")
 
            if response.__class__.__name__ == 'Failure':
                raise SignTxError

        except TransportException:
            raise SignTxError

        while response.data_length is not None:
            data_length = response.data_length
            data, chunk = data[data_length:], data[:data_length]
            response = cls.call_raw(proto.EthereumTxAck(data_chunk=chunk))
        
        v = response.signature_v
        r = response.signature_r
        s = response.signature_s

        stx = cls.signed_tx(tx, v, 
                            int(r.hex(), 16), 
                            int(s.hex(), 16)
                           )
        return stx

    #debug(); pdb.set_trace()

    @classmethod
    def close(cls):
        if cls.transport:
            cls.transport.close()


class SomeException(Exception):
    pass

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


