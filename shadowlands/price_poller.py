
import threading, time
from cryptocompy import price
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
import logging


class PricePoller:
    def __init__(self, config):
        self._thread_shutdown = False
        self._config = config
        self._prices = None
        self._thread = None

    def eth_price_poller(self):
        currencies = ["USD", "GBP", "EUR", 'BTC', 'AUD', 'CHF', 'JPY', 'RUB', 'CNY', 'SGD']
        while True:
            # 5 minutes seems responsible.
            sleep_time=300
            try:
                logging.debug("Poll for ETH prices")
                self._prices = price.get_current_price("ETH", currencies) 
                sleep_time = 300
            except (ConnectionError, JSONDecodeError):
                self._prices = None
                # Retry faster to anticipate the connection coming back online
                sleep_time = 10 
            for i in range (sleep_time):
                time.sleep(1)
                if self._thread_shutdown:
                   return

    def start_thread(self):
        self._thread = threading.Thread(target=self.eth_price_poller)
        self._thread.start()

    def stop_thread(self):
        if self._thread == None:
            return
        self._thread_shutdown = True
        self._thread.join()

    @property
    def eth_price(self):
        return self._prices['ETH'][self._config.displayed_currency]

    @property
    def eth_prices(self):
        return self._prices['ETH']

