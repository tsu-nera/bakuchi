import ccxt
import datetime
import src.constants.ccxtconst as ccxtconst
import sys

from logging import getLogger


class CcxtClient():
    def __init__(self, exchange_id):
        self.logger = getLogger(__name__)

        self.exchange = eval('ccxt.{}()'.format(exchange_id))
        self.symbol = ccxtconst.SYMBOL_BTC_JPY  # とりあえず BTC/JPY固定

    def _exec(self, proc):
        try:
            return proc()
        except ccxt.ExchangeNotAvailable:
            self.logger.exception("exchange not available error occured")
            return None
        except ccxt.RequestTimeout:
            self.logger.exception("timeout error occured")
        except ccxt.RateLimitExceeded:
            self.logger.exception("rate limit error occured. exit.")
            sys.exit(1)
        except Exception as e:
            self.logger.exception("error occourd", e)
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
