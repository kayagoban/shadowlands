from shadowlands.contract import Contract
from shadowlands.tui.debug import debug
from eth_utils import decode_hex
from datetime import datetime
import pdb
#debug(); pdb.set_trace()

class EnsAuction(Contract):
############################
# Contract read-only methods
############################

    def auction_status(self, name):
        status = self.functions.entries(self.sha3(text=name)).call()
        return status[0]

    def reveal_date(self, name):
        status = self.functions.entries(self.sha3(text=name)).call()
        reveal_timestamp = status[2]
        return datetime.fromtimestamp(reveal_timestamp)
        
    def winning_bid_amount(self, name):
        value = self.functions.entries(self.sha3(text="dapps")).call()[4]
        return self.fromWei(value, 'ether')

    def winning_bidder(self, name):
        value = self.functions.entries(self.sha3(text="dapps")).call()[1]
        return value

    '''
    def shaBid1(self, name, bidding address, bid_amt_ether, secret):
        bid = self.functions.shaBid(
            self.sha3(text=name), bidding_address, self.toWei(bid_amt_ether, 'ether'), self.sha3(text=secret)
        ).call()
        debug(); pdb.set_trace()
        return bid
 
    def shaBid2(self, name, bidding address, bid_amt_ether, secret):
        bid = self.functions.shaBid(
            self.sha3(text=name), bidding_address, self.toWei(bid_amt_ether, 'ether'), self.sha3(text=secret)
        ).call()
        debug(); pdb.set_trace()
        return bid
'''
 

########
# TXs  (notice they return the function objects themselves)
########

    #debug(); pdb.set_trace()

    def start_auction(self, name):
        fn = self.functions.startAuction(self.sha3(text=name))
        return fn

    def place_bid(self, name, bidding_address, bid_amt_ether, secret):
        bid = self.functions.shaBid(
            self.sha3(text=name), bidding_address, self.toWei(bid_amt_ether, 'ether'), self.sha3(text=secret)
        ).call()
        fn = self.functions.newBid(bid)
        return fn

    '''
    def place_bid_hex_decoded(self, name, bidding_address, bid_amt_ether, secret):
        bid = self.functions.shaBid(
            self.sha3(text=name), bidding_address, self.toWei(bid_amt_ether, 'ether'), self.sha3(text=secret)
        ).call()
        fn = self.functions.newBid(bid)
        return fn
'''


    def unsealBid(self, name, bidAmount, secret):
        # here we actually remove the .eth if it is there.
        if name.endswith(".eth"):
            name = name.replace('.eth', '')

        _namesha3 = self.sha3(text=name)
        secret_hash = self.sha3(text=secret)

        _value = self.toWei(bidAmount, 'ether')

        fn = self.functions.unsealBid(_namesha3, _value, secret_hash)
        return fn

# Check for the winning bidder
# ethRegistrar.entries(web3.sha3('name'))[1]).owner();
# Check for the winning bid
# ethRegistrar.entries(web3.sha3('name'))[4], 'ether');
# Transferring ownership of the deed to the name
# ethRegistrar.transfer(web3.sha3('name'), newDeedOwnerAddress, {from: currentDeedOwnerAddress})

    def finalizeAuction(self, name):
        # here we actually remove the .eth if it is there.
        if name.endswith(".eth"):
            name = name.replace('.eth', '')

        _namesha3 = self.sha3(text=name)

        fn = self.functions.finalizeAuction(_namesha3)
        return fn

####################################################################
# And down below here we have our ABI and network address constants.
####################################################################
    MAINNET='0x6090A6e47849629b7245Dfa1Ca21D94cd15878Ef'
    ABI=''' 
[{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"releaseDeed","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"getAllowedTime","outputs":[{"name":"timestamp","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"unhashedName","type":"string"}],"name":"invalidateName","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"hash","type":"bytes32"},{"name":"owner","type":"address"},{"name":"value","type":"uint256"},{"name":"salt","type":"bytes32"}],"name":"shaBid","outputs":[{"name":"sealedBid","type":"bytes32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"bidder","type":"address"},{"name":"seal","type":"bytes32"}],"name":"cancelBid","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"entries","outputs":[{"name":"","type":"uint8"},{"name":"","type":"address"},{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"ens","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"},{"name":"_value","type":"uint256"},{"name":"_salt","type":"bytes32"}],"name":"unsealBid","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"transferRegistrars","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"bytes32"}],"name":"sealedBids","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"state","outputs":[{"name":"","type":"uint8"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"},{"name":"newOwner","type":"address"}],"name":"transfer","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"_hash","type":"bytes32"},{"name":"_timestamp","type":"uint256"}],"name":"isAllowed","outputs":[{"name":"allowed","type":"bool"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"finalizeAuction","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"registryStarted","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"launchLength","outputs":[{"name":"","type":"uint32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"sealedBid","type":"bytes32"}],"name":"newBid","outputs":[],"payable":true,"type":"function"},{"constant":false,"inputs":[{"name":"labels","type":"bytes32[]"}],"name":"eraseNode","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hashes","type":"bytes32[]"}],"name":"startAuctions","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"hash","type":"bytes32"},{"name":"deed","type":"address"},{"name":"registrationDate","type":"uint256"}],"name":"acceptRegistrarTransfer","outputs":[],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"_hash","type":"bytes32"}],"name":"startAuction","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"rootNode","outputs":[{"name":"","type":"bytes32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"hashes","type":"bytes32[]"},{"name":"sealedBid","type":"bytes32"}],"name":"startAuctionsAndBid","outputs":[],"payable":true,"type":"function"},{"inputs":[{"name":"_ens","type":"address"},{"name":"_rootNode","type":"bytes32"},{"name":"_startDate","type":"uint256"}],"payable":false,"type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":false,"name":"registrationDate","type":"uint256"}],"name":"AuctionStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":true,"name":"bidder","type":"address"},{"indexed":false,"name":"deposit","type":"uint256"}],"name":"NewBid","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":true,"name":"owner","type":"address"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"status","type":"uint8"}],"name":"BidRevealed","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":true,"name":"owner","type":"address"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"registrationDate","type":"uint256"}],"name":"HashRegistered","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":false,"name":"value","type":"uint256"}],"name":"HashReleased","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"hash","type":"bytes32"},{"indexed":true,"name":"name","type":"string"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"registrationDate","type":"uint256"}],"name":"HashInvalidated","type":"event"}]
'''


