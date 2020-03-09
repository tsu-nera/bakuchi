import ccxt
import datetime
import src.constants.ccxtconst as ccxtconst
import time

from logging import getLogger


class CcxtClient():
    def __init__(self, exchange_id):
        self.logger = getLogger(__name__)

        self.exchange = eval('ccxt.{}()'.format(exchange_id))
        self.symbol = ccxtconst.SYMBOL_BTC_JPY  # とりあえず BTC/JPY固定

    def _exec(self, proc):
        try:
            return proc()
        except ccxt.ExchangeNotAvailable as e:
            self.logger.error("exchange not available error occured", e)
            return None
        except ccxt.RequestTimeout as e:
            self.logger.error("timeout error occured", e)
        except ccxt.RateLimitExceeded as e:
            self.logger.error("rate limit error occured. sleep 30sec", e)
            time.sleep(30)
        except Exception as e:
            self.logger.error("error occourd", e)
        return None

    def fetch_tick(self):
        date_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        proc = lambda: self.exchange.fetch_ticker(self.symbol)
        tick = self._exec(proc)

        return {
            "date": date_string,
            "bid": tick["bid"],
            "ask": tick["ask"]
        } if tick else None
