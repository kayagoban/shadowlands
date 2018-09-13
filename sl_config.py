from pathlib import Path
import yaml
from yaml.constructor import ConstructorError
import pdb

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
        'SGD': '$'

    }

    def __init__(self, config_file_path=None):
        self._http_uri = ''
        self._websocket_uri = ''
        self._ipc_path = ''
        self._default_method = None
        self._displayed_currency = 'USD' 

        if config_file_path:
            self._config_file_path = config_file_path
        else:
            self._config_file_path = Path.home().joinpath(".shadowlands.cfg")

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
        f = open(self._config_file_path, 'r')
        try:
            self._options_dict = yaml.load(f.read())
        except ConstructorError:
            self._clobber_bad_file()
            
        f.close()

    def _load_properties(self):
            self._default_method = self._options_dict['network_options']['default_method']
            self._http_uri = self._options_dict['network_options']['http_uri']
            self._websocket_uri = self._options_dict['network_options']['websocket_uri']
            self._ipc_path = self._options_dict['network_options']['ipc_path']
            self._displayed_currency = self._options_dict['displayed_currency']
           
    def _write_config_file(self):
        f = open(self._config_file_path, 'w')
        f.write(yaml.dump(self._config_dict()))
        f.close()

    def _config_dict(self):
        return {
            "displayed_currency": self._displayed_currency,
            "network_options": {
                "default_method": self._default_method,
                "http_uri": self._http_uri,
                "websocket_uri": self._websocket_uri,
                "ipc_path": self._ipc_path
            }
        }

    @property
    def default_method(self):
        return self._default_method

    @default_method.setter
    def default_method(self, new_value):
        #pdb.set_trace()
        self._default_method = new_value
        self._write_config_file()

    @property
    def http_uri(self):
        return self._http_uri

    @http_uri.setter
    def http_uri(self, new_value):
        self._http_uri = new_value
        self._write_config_file()

    @property
    def websocket_uri(self):
        return self._websocket_uri

    @websocket_uri.setter
    def websocket_uri(self, new_value):
        self._websocket_uri = new_value
        self._write_config_file()

    @property
    def ipc_path(self):
        return self._ipc_path

    @ipc_path.setter
    def ipc_path(self, new_value):
        self._ipc_path = new_value
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



