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

    def _exec(self):
        try:
            return self.exchange.fetch_ticker(self.symbol)
        except ccxt.ExchangeNotAvailable as e:
            self.logger.error(e)
            self.logger.errro("exchange not available error occured")
            return None
        except ccxt.RequestTimeout as e:
            self.logger.error(e)
            self.logger.error("timeout error occured")
            return None
        except ccxt.RateLimitExceeded as e:
            self.logger.error(e)
            self.logger.error("rate limit error occured. exit.")
            sys.exit(1)
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("error occourd")
            return None

    def fetch_tick(self):
        date_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        tick = self._exec()

        return {
            "date": date_string,
            "bid": tick["bid"],
            "ask": tick["ask"]
        } if tick else None
