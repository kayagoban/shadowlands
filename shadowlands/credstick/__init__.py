import hid, threading, time

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
    manufacturer = None
    product = None
    address = None
    detect_thread = None
    detect_thread_shutdown = False

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
        for hidDevice in hid.enumerate(0, 0):
            if hidDevice['vendor_id'] == 0x2c97:
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == 0) or ('usage_page' in hidDevice and hidDevice['usage_page'] == 0xffa0):
                    if hidDevice['path'] is not None:
                        from shadowlands.credstick.ledger_ethdriver import LedgerEthDriver
                        LedgerEthDriver.manufacturer = hidDevice['manufacturer_string']
                        LedgerEthDriver.product = hidDevice['product_string']
                        return LedgerEthDriver
            elif hidDevice['vendor_id'] == 0x534c:
                #import pdb; pdb.set_trace()
                if ('interface_number' in hidDevice and hidDevice['interface_number'] == -1) or ('usage_page' in hidDevice and hidDevice['usage_page'] in [0xf1d0, 0xff00]):
                    if hidDevice['path'] is not None:
                        from shadowlands.credstick.trezor_ethdriver import TrezorEthDriver
                        TrezorEthDriver.manufacturerStr = hidDevice['manufacturer_string']
                        TrezorEthDriver.productStr = hidDevice['product_string']
                        return TrezorEthDriver
 
        raise NoCredstickFoundError("Could not identify any supported credstick")

    @classmethod
    def start_detect_thread(cls):
        cls.detect_thread = threading.Thread(target=cls.credstick_finder)
        cls.detect_thread.start()

    @classmethod 
    def stop_detect_thread(cls):
        cls.detect_thread_shutdown = True 
        cls.detect_thread.join()

    @classmethod
    def credstick_finder(cls):
        not_found = True
        address = None

        while not_found:
            try: 
                credstick = cls.detect()
                credstick.open()
                while not address:
                    address = credstick.derive()
                    time.sleep(1)

                cls.eth_node.credstick = credstick
                cls.interface.credstick = credstick
                not_found = False
            except(NoCredstickFoundError, OpenCredstickError, DeriveCredstickAddressError):
                time.sleep(0.25)

            if cls.detect_thread_shutdown:
                break


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
    def derive(cls):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def signTx(cls, tx):
        raise NotImplementedError(optional_error_message)

    @classmethod
    def open(cls):
        raise NotImplementedError(optional_error_message)


