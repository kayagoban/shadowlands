import yaml
from yaml.constructor import ConstructorError
from collections import deque
from pathlib import Path
import sys
import logging
import threading

import pdb
from shadowlands.tui.debug import debug

class DuplicateTokenError(Exception):
    pass
class UnallowedTokenRemovalError(Exception):
    pass
class NoTokenMatchError(Exception):
    pass

class SLConfig():

    CURR_SYMBOLS = {
        'USD': '$',
        'GBP': '£',
        'EUR': '€',
        'BTC': 'Ƀ',
        'CHF': '',
        'AUD': '$',
        'RUB': '₽',
        'JPY': '¥',
        'CNY': '¥',
        'SGD': '$',
        'ETH': 'Ξ'
    }

    TOKENS = [
        ('DAI', '0x89d24A6b4CcB1B6fAA2625fE562bDD9a23260359', 1),
        ('MKR', '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2', 1),
        ('REP', '0x1985365e9f78359a9B6AD760e32412f4a445E862', 1),
        ('DGX', '0x4f3AfEC4E5a3F2A6a1A411DEF7D7dFe50eE057bF', 1),
        ('ZRX', '0xE41d2489571d322189246DaFA5ebDe1F4699F498', 1),
        ('LOOM', '0xA4e8C3Ec456107eA67d3075bF9e3DF3A75823DB0', 1),
        ('USDC', '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 1),
        ('WBTC', '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599', 1),
        ('WETH', '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 1)
    ]


    def __init__(self):
        self._hdpath = None
        self._dapp_configs = {}
        self._connection_strategy = None
        self._connection_args = []
        self._displayed_currency = 'USD' 
        self._sl_dapp_path = str(Path.home())
        self._config_file_path = Path.home().joinpath('.shadowlands').joinpath('config')
        self._txqueue = deque()
        self._txqueues = {}
        self._tokens = SLConfig.TOKENS
        self.write_lock = threading.Lock()
        self.txqueue_lock = threading.Lock()


        if not self._config_file_path.exists():
            self._write_config_file()

        self._read_yaml()

        try:
            self._load_properties()
        except (KeyError, TypeError):
            self._clobber_bad_file()
            # formatting error, possibly an incompatible cfg file.  We overwrite to fix this problem, better to lose some configs than die with an exception.

    def _clobber_bad_file(self):
        self._write_config_file()
        self._read_yaml()
        self._load_properties()

    def _read_yaml(self):
        f = open(str(self._config_file_path), 'r')
        try:
            self._options_dict = yaml.load(f.read(), Loader=yaml.FullLoader)
        except ConstructorError:
            self._clobber_bad_file()
            
        f.close()


    def _load_properties(self):
            self._connection_strategy = self._options_dict['network_options']['connection_strategy']
            self._connection_strategy = self._options_dict['network_options']['connection_args']

            self._displayed_currency = self._options_dict['displayed_currency']
            self._txqueue = self._options_dict['txqueue']
            # sl_dapp_path should probably be _sl_dapp_path.
            # But I tried that and THE UNIVERSE BROKE.
            # I don't know why it works and doesn't work.
            # I am re-examining my life.
            self.sl_dapp_path = self._options_dict['sl_dapp_path']
            self._dapp_configs = self._options_dict['dapp_configs']
            self._hdpath = self._options_dict['hdpath']
            self._tokens = self._options_dict['tokens']

    def _write_config_file(self):
        with self.write_lock:
          f = open(str(self._config_file_path), 'w')
          f.write(yaml.dump(self._config_dict()))
          f.close()

    def _config_dict(self):
        return {
            "displayed_currency": self._displayed_currency,
            "sl_dapp_path": self._sl_dapp_path,
            "dapp_configs": self._dapp_configs,
            "hdpath": self._hdpath,
            "txqueue": self._txqueue,
            "network_options": {
                "connection_strategy": self._connection_strategy,
                "connection_args": self._connection_args
            },
            "tokens": self._tokens
        }

    @property
    def sl_dapp_path(self):
        return self._sl_dapp_path

    @sl_dapp_path.setter
    def sl_dapp_path(self, new_value):
        if sys.path[0] == str(self._sl_dapp_path):
            sys.path[0] = str(new_value)
        else:
            sys.path.insert(0, str(new_value))
 
        self._sl_dapp_path = str(new_value)
        self._write_config_file()


    @property
    def dapp_configs(self):
        return self._dapp_configs

    @dapp_configs.setter
    def dapp_configs(self, new_value):
        self._dapp_configs = dict(new_value)
        self._write_config_file()

    # These two methods are used by SLDapp
    def dapp_config(self, dapp_key):
        try:
            return self._dapp_configs[dapp_key]
        except KeyError:
            self.set_dapp_config(dapp_key, dict())
            return self._dapp_configs[dapp_key]

    def set_dapp_config(self, dapp_key, new_value):
        config = dict(self.dapp_configs)
        config[dapp_key] = dict(new_value)
        self.dapp_configs = config


    def tokens(self, network_id):
        return [x for x in self._tokens if x[2] == network_id]

    def add_token(self, name, address, network_id):
        matches = [x for x in self.tokens(network_id)  if ((name == x[0] or address == x[1]) and network_id == x[2])]

        if len(matches) > 0:
            raise DuplicateTokenError

        self._tokens.append((name,address,network_id))
        self._write_config_file()


    def remove_token(self, name, network_id):
        matches = [x for x in self._tokens if name == x[0] and network_id == x[2]]
        if len(matches) < 1:
            raise NoTokenMatchError

        self._tokens.remove(matches[0])
        self._write_config_file()

    
    # Elements consist of 
    # { sx: signed_transaction, chain_id: integer_chain_id, rx: tx_receipt }

    def txqueue(self, chain_id):
        return [x for x in self._txqueue if x['rx'] != None and x['chain_id'] == chain_id]

    def txq_remove(self, chain_id, item):
      with self.txqueue_lock:
        self._txqueue.remove(item)
        self._write_config_file()
        logging.info("Removed tx from queue: {}".format(str(item)))

    def txq_next(self):
      return next(x for x in self._txqueue if x['rx'] == None)

    def txq_update(self, index, rx):
      with self.txqueue_lock:
        self._txqueue[index]['rx'] = rx

    def _txq_add(self, chain_id, item):
      with self.txqueue_lock:
        if item is None:
            return
        item = { 'sx': item, 'chain_id': chain_id, 'rx': None }
        self._txqueue.appendleft(item)
        self._write_config_file()
        logging.info("Added tx to queue:".format(str(item)))


    @property
    def hdpath(self):
        return self._hdpath

    @hdpath.setter
    def hdpath(self, new_value):
        self._hdpath = str(new_value)
        self._write_config_file()
 
    @property
    def connection_strategy(self):
      return self._connection_strategy

    @connection_strategy.setter
    def connection_strategy(self, new_value):
      self._connection_strategy = new_value
      self._write_config_file()

    @property
    def connection_args(self):
      return self._connection_args

    @connection_args.setter
    def connection_args(self, new_value):
      self._connection_args = new_value
      self._write_config_file()

    @property
    def displayed_currency(self):
        return self._displayed_currency

    @displayed_currency.setter
    def displayed_currency(self, new_value):
        self._displayed_currency = new_value
        self._write_config_file()

    @property
    def curr_symbol(self):
        return self.CURR_SYMBOLS[self._displayed_currency]



