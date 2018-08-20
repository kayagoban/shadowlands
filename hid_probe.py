import hid
from ledger_ethdriver import LedgerEthDriver

#        import pdb; pdb.set_trace()

class NoCredstickFoundError(Exception):
    pass

def find_credstick():
    for hidDevice in hid.enumerate(0, 0):
        if hidDevice['vendor_id'] == 0x2c97:
            if ('interface_number' in hidDevice and hidDevice['interface_number'] == 0) or ('usage_page' in hidDevice and hidDevice['usage_page'] == 0xffa0):
                hidDevicePath = hidDevice['path']
                if hidDevicePath is not None:
                    return LedgerEthDriver

    raise NoCredstickFoundError("Could not identify any supported credstick")

# satoshi labs vendor id: '0x534c'

# usage pages '0xf1d0', '0xff00'
