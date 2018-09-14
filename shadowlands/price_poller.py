
import threading, time
from cryptocompy import price


class PricePoller:
    def __init__(self, config):
        self._thread_shutdown = False
        self._config = config
        self._prices = None
        self._thread = None

    def eth_price_poller(self):
        currencies = ["USD", "GBP", "EUR", 'BTC', 'AUD', 'CHF', 'JPY', 'RUB', 'CNY', 'SGD']
        while True:
            #debug(); 
            #pdb.set_trace()
            self._prices = price.get_current_price("ETH", currencies) 
            # 5 minutes seems responsible.
            for i in range (150):
                time.sleep(2)
                if self._thread_shutdown:
                   return

    def start_thread(self):
        self._thread = threading.Thread(target=self.eth_price_poller)
        self._thread.start()

    def stop_thread(self):
        self._thread_shutdown = True
        self._thread.join()

    @property
    def eth_price(self):
        return self._prices['ETH'][self._config.displayed_currency]

    @property
    def eth_prices(self):
        return self._prices['ETH']

