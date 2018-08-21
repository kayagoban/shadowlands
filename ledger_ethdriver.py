from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException
from rlp import encode, decode
from rlp.sedes import big_endian_int, binary, Binary
#from rlp import Serializable
from rlp.sedes.serializable import Serializable
from eth_utils import decode_hex, encode_hex

## Constants for APDU exchanges

"""
// The transaction signing protocol is defined as follows:
//
//   CLA | INS | P1 | P2 | Lc  | Le
//   ----+-----+----+----+-----+---
//    E0 | 04  | 00: first transaction data block
//               80: subsequent transaction data block
//                  | 00 | variable | variable
//
// Where the input for the first transaction block (first 255 bytes) is:
//
//   Description                                      | Length
//   -------------------------------------------------+----------
//   Number of BIP 32 derivations to perform (max 10) | 1 byte
//   First derivation index (big endian)              | 4 bytes
//   ...                                              | 4 bytes
//   Last derivation index (big endian)               | 4 bytes
//   RLP transaction chunk                            | arbitrary
//
"""

# Ethereaum ledger app opcodes 
CLA = b'\xe0'
INS_OPCODE_GET_ADDRESS = b'\x02'
INS_OPCODE_SIGN_TRANS = b'\x04'
INS_OPCODE_GET_VERSION = b'\x06'

# get address protocol
P1_RETURN_ADDRESS = b'\x00'
P1_RETURN_AND_VERIFY_ADDRESS = b'\x01'
P2_NO_CHAIN_CODE = b'\x00'
P2_RETURN_CHAIN_CODE = b'\x01'

# transaction protocol
P1_FIRST_TRANS_DATA_BLOCK = b'\x00'
P1_SUBSEQUENT_TRANS_DATA_BLOCK = b'\x80'
P2_UNUSED_PARAMETER = b'\x00'



# import pdb; pdb.set_trace()

class LedgerEthDriver(Credstick):

    @classmethod
    def open(cls):
        try:
            cls._driver = getDongle(False)
            #cls._driver = getDongle(True)
            cls.manufacturerStr = cls._driver.device.get_manufacturer_string()
            cls.productStr = cls._driver.device.get_product_string()
        except OSError:
            raise OpenCredstickError


    @classmethod
    def close(cls):
        cls._driver.device.close()
        cls._driver = None

    @classmethod
    def derive(cls):
        try:
            result = cls._driver.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
            offset = 1 + result[0]
            cls.address = result[offset + 1 : offset + 1 + result[offset]]
        except(CommException, IOError):
            raise DeriveCredstickAddressError("Could not derive an address from your credstick, user.")
        return cls.addressStr()

    @classmethod
    def version(cls):
        try:
            apdu = b'\xe0\x06\x00\x00\x00\x04'
            result = cls._driver.exchange(apdu)
            import pdb; pdb.set_trace()
        except(CommException, IOError):
            raise DeriveError("Could not derive an address from your credstick, user.")
        return cls.addressStr()

    @classmethod
    def signTx(cls, encodedTx, pathStr="44'/60'/0'/0"):
        import pdb; pdb.set_trace()
        encodedPath = cls._hd_path(pathStr)
        # Each path element is 4 bytes.  How many path elements are we sending?
        derivationPathCount= (len(encodedPath) // 4).to_bytes(1, 'big')
        # Prepend the byte representing the count of path elements to the path encoding itself.
        encodedPath = derivationPathCount + encodedPath 
        dataPayloadSize = (len(encodedPath) + len(encodedTx)).to_bytes(1, 'big')
        dataPayload = dataPayloadSize + encodedPath + encodedTx
        apdu = CLA + INS_OPCODE_SIGN_TRANS + P1_FIRST_TRANS_DATA_BLOCK + P2_UNUSED_PARAMETER + dataPayloadSize + encodedPath + encodedTx


        result = cls._driver.exchange(apdu)
        v = result[0]
        r = int((result[1:1 + 32]).hex(), 16)
        s = int((result[1 + 32: 1 + 32 + 32]).hex(), 16)
        tx = Transaction(tx.nonce, tx.gasprice, tx.startgas, tx.to, tx.value, tx.data, v, r, s)
        return encode_hex(rlp.encode(tx))

    @classmethod
    def _hd_path(cls, pathStr="44'/60'/0'/0"):
        result = b''
        if len(path) == 0:
            return result
        elements = path.split('/')
        for pathElement in elements:
            element = pathElement.split('\'')
            if len(element) == 1:
                result = result + struct.pack(">I", int(element[0]))			
            else:
                result = result + struct.pack(">I", 0x80000000 | int(element[0]))
                return result


address = Binary.fixed_length(20, allow_empty=True)

class UnsignedTransaction(Serializable):
	fields = [
		('nonce', big_endian_int),
		('gasprice', big_endian_int),
		('startgas', big_endian_int),
		('to', address),
		('value', big_endian_int),
		('data', binary)
	]	

	def __init__(self, nonce, gasprice, startgas, to, value, data):
		super(Transaction, self).__init__(nonce, gasprice, startgas, to, value, data)


class Transaction(Serializable):
	fields = [
		('nonce', big_endian_int),
		('gasprice', big_endian_int),
		('startgas', big_endian_int),
		('to', address),
		('value', big_endian_int),
		('data', binary),
		('v', big_endian_int),
		('r', big_endian_int),
		('s', big_endian_int),
	]	

	def __init__(self, nonce, gasprice, startgas, to, value, data, v=0, r=0, s=0):
		super(Transaction, self).__init__(nonce, gasprice, startgas, to, value, data, v, r, s)


