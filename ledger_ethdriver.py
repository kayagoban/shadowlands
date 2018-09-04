import rlp, struct
from hexbytes import HexBytes
from credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException
from rlp import encode, decode
from rlp.sedes import big_endian_int, binary, Binary
###from rlp import Serializable
from rlp.sedes.serializable import Serializable
from eth_utils import decode_hex, encode_hex
from eth_keys.datatypes import PrivateKey
#from eth_account.internal.transactions import UnsignedTransaction, Transaction
from eth_account.datastructures import AttributeDict
from eth_utils.crypto import keccak

from eth_account.internal.transactions import (
    ChainAwareUnsignedTransaction,
    UnsignedTransaction,
    Transaction,
    encode_transaction,
    serializable_unsigned_transaction_from_dict,
    strip_signature,
)

#import pdb; pdb.set_trace()
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

# Ethereum ledger app opcodes 
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
# Seems to crash the app on the ledger.  Possibly incomplete documentation on this
# Opcode
#P1_SUBSEQUENT_TRANS_DATA_BLOCK = b'\x80'  
P2_UNUSED_PARAMETER = b'\x00'


BIP44_PATH="44'/60'/0'/0/0"
LEDGER_PATH="44'/60'/0'/0"

EXAMPLE_DICT = {
    'nonce': 80,
    'gasPrice': 21000,
    'gas': 4000000,
    'value': int(100000),
    'to': decode_hex('0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5'),
    'data': b''
}
 
# import pdb; pdb.set_trace()
def hd_path(pathStr=LEDGER_PATH):
    result = b''
    if len(pathStr) == 0:
        return result
    elements = pathStr.split('/')
    for pathElement in elements:
        element = pathElement.split('\'')
        if len(element) == 1:
            result = result + struct.pack(">I", int(element[0]))			
        else:
            result = result + struct.pack(">I", 0x80000000 | int(element[0]))
    return result


class LedgerEthDriver(Credstick):

    @classmethod
    def open(cls):
        try:
            # getDongle(True) forces verification of the user address on the device.
            cls._driver = getDongle(False)
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
        apdu = b'\xe0\x06\x00\x00\x00\x04'
        result = cls._driver.exchange(apdu)

    @classmethod
    def signTx(cls,transaction_dict=EXAMPLE_DICT):
        try:

            # Strip chainId if it's there...  the ledger doesn't like it.

            try:
                del(transaction_dict['chainId'])
            except:
                # Fine, if it isn't there it isn't there. jeez.
                pass

            # if to and data fields are hex strings, turn them into byte arrays
            if (transaction_dict['to']).__class__ == str:
                transaction_dict['to'] = decode_hex(transaction_dict['to'])

            if (transaction_dict['data']).__class__ == str:
                transaction_dict['data'] = decode_hex(transaction_dict['data'])

            '''
            tx = UnsignedTransaction.from_dict({
                'nonce': 80,
                'gasPrice': 21000,
                'gas': 4000000,
                'value': int(0.00001),
                'to': decode_hex('0xb75D1e62b10E4ba91315C4aA3fACc536f8A922F5'),
                'data': b''
            })
            '''
            tx = UnsignedTransaction.from_dict(transaction_dict)

            encodedTx = rlp.encode(tx, UnsignedTransaction)

            encodedPath = hd_path()
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
            
            trx = Transaction(tx.nonce, tx.gasPrice, tx.gas, tx.to, tx.value, tx.data, v, r, s)
            enctx = rlp.encode(trx)
            transaction_hash = keccak(enctx)

            attr_dict =  AttributeDict({
                'rawTransaction': HexBytes(enctx),
                'hash': HexBytes(transaction_hash),
                'r': r,
                's': s,
                'v': v,
            })

        except CommException:
            raise SignTxError("Error while attempting SignTx")

        return attr_dict


