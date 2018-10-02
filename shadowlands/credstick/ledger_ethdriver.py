import rlp, struct
from hexbytes import HexBytes
from shadowlands.credstick import Credstick, DeriveCredstickAddressError, OpenCredstickError, CloseCredstickError, SignTxError
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

import random, string

#from shadowlands.tui.debug import debug
import pdb

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
P1_SUBSEQUENT_TRANS_DATA_BLOCK = b'\x80'  
P2_UNUSED_PARAMETER = b'\x00'
P2_UNUSED_PARAMETER2 = b'\x01'


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
def encode_path(pathStr):
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
    hdpath_base="44'/60'/0'"
    hdpath_index='0'
    _driver = None

    @classmethod
    def open(cls):
        try:
            # getDongle(True) forces verification of the user address on the device.
            cls._driver = getDongle(False)
            cls.manufacturerStr = cls._driver.device.get_manufacturer_string()
            cls.productStr = cls._driver.device.get_product_string()
        except (OSError, CommException):
            raise OpenCredstickError

    @classmethod
    def close(cls):
        cls._driver.device.close()
        cls._driver = None

    @classmethod
    def derive(cls, hdpath_base="44'/60'/0'", hdpath_index='0', set_address=False):
        try:
            hdpath = hdpath_base + '/' + hdpath_index
            encodedPath = encode_path(hdpath)
            derivationPathCount= (len(encodedPath) // 4).to_bytes(1, 'big')
            hd_payload = derivationPathCount + encodedPath 
            payloadSize = (len(hd_payload)).to_bytes(1, 'big')
            apdu = CLA + INS_OPCODE_GET_ADDRESS + P1_RETURN_ADDRESS + P2_NO_CHAIN_CODE + payloadSize + hd_payload
            #result = cls._driver.exchange(bytearray.fromhex('e002000011048000002c8000003c8000000000000000'))
            result = cls._driver.exchange(apdu)
            offset = 1 + result[0]
            address = result[offset + 1 : offset + 1 + result[offset]]
        except(CommException, IOError, BaseException) as e:
            raise DeriveCredstickAddressError("Could not derive an address from your credstick.")

        derived_address = '0x' + address.decode('ascii')
        if set_address is True:
            cls.address = derived_address
            cls.hdpath_base = hdpath_base
            cls.hdpath_index = hdpath_index
        return derived_address 

    @classmethod
    def version(cls):
        apdu = b'\xe0\x06\x00\x00\x00\x04'
        result = cls._driver.exchange(apdu)

    @classmethod
    def signTx(cls,transaction_dict=EXAMPLE_DICT):

        try:
            transaction_dict = cls.prepare_tx(transaction_dict)
            tx = UnsignedTransaction.from_dict(transaction_dict)
            encodedTx = rlp.encode(tx, UnsignedTransaction)
            encodedPath = encode_path(cls.hdpath())
            # Each path element is 4 bytes.  How many path elements are we sending?

            derivationPathCount= (len(encodedPath) // 4).to_bytes(1, 'big')

            # Prepend the byte representing the count of path elements to the path encoding itself.
            encodedPath = derivationPathCount + encodedPath 
            dataPayload = encodedPath + encodedTx

            # Big thanks to the Geth team for their ledger implementation (and documentation).
            # You guys are stars.
            #
            # To the others reading, the ledger can only take 255 bytes of data payload per apdu exchange.
            # hence, you have to chunk and use 0x08 for the P1 opcode on subsequent calls.

            p1_op = P1_FIRST_TRANS_DATA_BLOCK

            while len(dataPayload) > 0:
                chunkSize = 255
                if chunkSize > len(dataPayload):
                    chunkSize = len(dataPayload)
                
                encodedChunkSize = (chunkSize).to_bytes(1, 'big')
                apdu = CLA + INS_OPCODE_SIGN_TRANS + p1_op + P2_UNUSED_PARAMETER + encodedChunkSize + dataPayload[:chunkSize] 

                ## Keeping this here commented in case I need to debug it again.
                #apdufile = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)) 
                #f = open('logs/{}'.format(apdufile), 'wb')
                #f.write(apdu)
                #f.close()

                result = cls._driver.exchange(apdu)

                dataPayload = dataPayload[chunkSize:]
                p1_op = P1_SUBSEQUENT_TRANS_DATA_BLOCK

            v = result[0]
            r = int((result[1:1 + 32]).hex(), 16)
            s = int((result[1 + 32: 1 + 32 + 32]).hex(), 16)

            stx = cls.signed_tx(transaction_dict, v, r, s)

        except CommException as e:
            raise SignTxError("Ledger device threw error  while attempting SignTx with apdu {}:  {}".format(apdu, e.message))
        return stx
    

        '''for len(payload) > 0 {
            // Calculate the size of the next data chunk
            chunk := 255
            if chunk > len(payload) {
                    chunk = len(payload)
            }
            // Send the chunk over, ensuring it's processed correctly
            reply, err = w.ledgerExchange(ledgerOpSignTransaction, op, 0, payload[:chunk])
            if err != nil {
                    return common.Address{}, nil, err
            }
            // Shift the payload and ensure subsequent chunks are marked as such
            payload = payload[chunk:]
            op = ledgerP1ContTransactionData
    }'''


