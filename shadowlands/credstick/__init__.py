import hid, threading, time
from hexbytes import HexBytes
from eth_utils.crypto import keccak
import logging

#from shadowlands.credstick.transactions import (
#  AttributeDict,
#	encode_transaction,
#	Transaction, 
#	UnsignedTransaction
#)


import rlp
from time import sleep

from shadowlands.tui.debug import debug
import pdb


# TODO
# fork eth-account and eth-keys repos from the Web3.py project and 
# submit a PR to make this all a subsystem of web3

class NoCredstickFoundError(Exception):
    pass

class DeriveCredstickAddressError(Exception):
    pass

class OpenCredstickError(Exception):
    pass

class CloseCredstickError(Exception):
    pass

class SignTxError(Exception):
    pass

class Credstick(object):
    interface = None
    eth_node = None
    config = None
    manufacturer = None
    product = None
    address = None
    detect_thread = None
    detect_thread_shutdown = False
    hdpath = "44'/60'/0'/0 /0"
    mock_address = None
 

    @classmethod
    def addressStr(cls):
        return cls.address

    @classmethod
    def heartbeat(cls):
        return

    # For implementation of Trezor:
    # satoshi labs vendor id: '0x534c'
    # usage pages '0xf1d0', '0xff00'
    @classmethod
    def detect(cls):
        if cls.mock_address is not None:
            from shadowlands.credstick.mock_ethdriver import MockEthDriver
            return MockEthDriver

        def handle_trezor(hidDevice):
            from shadowlands.credstick.trezor_ethdriver import TrezorEthDriver
            TrezorEthDriver.manufacturerStr = hidDevice['manufacturer_string']
            if hidDevice['release_number'] == 256:
                TrezorEthDriver.productStr = 'Trezor One' 
                sleep(1)
            elif hidDevice['release_number'] == 512:
                TrezorEthDriver.productStr = 'Trezor T' 
            return TrezorEthDriver
 
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice['path'] is not None:
                if hidDevice['vendor_id'] == 0x2c97:
                    from shadowlands.credstick.ledger_ethdriver import LedgerEthDriver
                    LedgerEthDriver.manufacturer = hidDevice['manufacturer_string']
                    LedgerEthDriver.product = hidDevice['product_string']
                    return LedgerEthDriver
                elif hidDevice['vendor_id'] == 0x534c:
                    return handle_trezor(hidDevice)
                elif hidDevice['vendor_id'] == 0x1209:
                    return handle_trezor(hidDevice)

        raise NoCredstickFoundError("Could not identify any supported credstick")

    @classmethod
    def start_detect_thread(cls):
        cls.detect_thread = threading.Thread(target=cls.credstick_finder)
        #cls.credstick_finder()
        cls.detect_thread.start()

    @classmethod 
    def stop_detect_thread(cls):
        if cls.detect_thread == None:
            return
        cls.detect_thread_shutdown = True 
        cls.detect_thread.join()

    @classmethod
    def credstick_finder(cls):
        not_found = True
        while not_found:
            try: 
                credstick = cls.detect()
                credstick.open()
                logging.debug("credstick: attempt derive " + credstick.hdpath_default())
                credstick.derive(
                    set_address=True, 
                    hdpath=credstick.hdpath_default()
                )

                timeout = 30 

                while credstick.address is None and timeout > 0:
                    time.sleep(1)
                    timeout -= 1
                if credstick.address is None:
                    raise DeriveCredstickAddressError

                cls.eth_node.credstick = credstick
                cls.interface.credstick = credstick
                not_found = False
            except(NoCredstickFoundError, OpenCredstickError, DeriveCredstickAddressError):
                time.sleep(0.25)

            if cls.detect_thread_shutdown:
                break


    @classmethod
    def signed_tx(cls, sutx, v, r, s):
        enctx = encode_transaction(sutx, (v, r, s))
        transaction_hash = keccak(enctx)

        attr_dict =  AttributeDict({
            'rawTransaction': HexBytes(enctx),
            'hash': HexBytes(transaction_hash),
            'r': r,
            's': s,
            'v': v,
        })
        
        return attr_dict


    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def close(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def heartbeat(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def derive(cls, set_address=False, hdpath=None):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def signTx(cls, transaction_dict):
        raise NotImplementedError(optional_error_message)


    @classmethod
    def hdpath_default(cls):
        return cls.config.hdpath or cls.hdpath

