from shadowlands.contract import Contract

class EnsReverseResolver(Contract):
    MAINNET='0x9062C0A6Dbd6108336BcBe4593a3D1cE05512069'
    ABI='[{"constant":false,"inputs":[{"name":"owner","type":"address"},{"name":"resolver","type":"address"}],"name":"claimWithResolver","outputs":[{"name":"node","type":"bytes32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"owner","type":"address"}],"name":"claim","outputs":[{"name":"node","type":"bytes32"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"ens","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"defaultResolver","outputs":[{"name":"","type":"address"}],"payable":false,"type":"function"},{"constant":true,"inputs":[{"name":"addr","type":"address"}],"name":"node","outputs":[{"name":"ret","type":"bytes32"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"name","type":"string"}],"name":"setName","outputs":[{"name":"node","type":"bytes32"}],"payable":false,"type":"function"},{"inputs":[{"name":"ensAddr","type":"address"},{"name":"resolverAddr","type":"address"}],"payable":false,"type":"constructor"}]'

    def set_name(self, name):
        if self._contract == None:
           self.load()

        if not name.endswith(".eth"):
            name += '.eth'

        fn = self._contract.functions.setName(name)
        return fn
 



