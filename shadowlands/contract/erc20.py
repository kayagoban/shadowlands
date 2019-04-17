from shadowlands.contract import Contract

class TokenNotFound(Exception):
    pass


class Erc20(Contract):

    TOKENS = [
        ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'),
        ('DAI', '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359'),
        ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2'),
        ('REP', '0x1985365e9f78359a9B6AD760e32412f4a445E862'),
        ('DGX', '0x4f3AfEC4E5a3F2A6a1A411DEF7D7dFe50eE057bF'),
        ('DGD', '0xE0B7927c4aF23765Cb51314A0E0521A9645F0E2A'),
        ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498'),
        ('LOOM', '0xA4e8C3Ec456107eA67d3075bF9e3DF3A75823DB0'),
        ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'),
        ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'),
        ('Unicorn', '0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7')
    ]

    def __init__(self, node, address):
        super(Erc20, self).__init__(node, address=address)

    @classmethod
    def balance(cls, node, tokenaddr, target):
        return cls(node, tokenaddr).balanceOf(target)

    '''
       Returns a dictionary of token names and balances if not zero. 
       Usage: 
           Erc20.balances(eth_node, target_address)
       '''
    @classmethod
    def balances(cls, node, target):
        result = [{'name': x[0], 'balance': node.w3.fromWei(cls.balance(node, x[1], target), 'ether')} for x in cls.TOKENS]
        return [x for x in result if x['balance'] > 0]

    ''' 
        Returns an web3 ERC20 contract
        Usage:
        Erc20.factory(eth_node, 'WETH')
        '''
    @classmethod
    def factory(cls, node, token):

        #ALL_TOKENS = cls.TOKENS + node.config.tokens
        ALL_TOKENS = cls.TOKENS

        matches = [x for x in ALL_TOKENS if x[0] == token]

        if len(matches) < 1:
            raise TokenNotFound("Unknown token '{}'".format(token))

        # *security* Always take the first match to prefer the default over user-defined tokens
        token = matches[0]

        return cls(node, token[1])
        

    # Instance methods


    def balanceOf(self, target):
        return self.functions.balanceOf(target).call()

    def transfer(self, target, value):
        return self.functions.transfer(target, value)


    ABI='''
    [{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"guy","type":"address"},{"name":"wad","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"src","type":"address"},{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"wad","type":"uint256"}],"name":"withdraw","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"dst","type":"address"},{"name":"wad","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"deposit","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"},{"name":"","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"payable":true,"stateMutability":"payable","type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"guy","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}],"name":"Withdrawal","type":"event"}]
    '''


