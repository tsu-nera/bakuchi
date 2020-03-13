import sys
import ccxt
import datetime

import src.constants.ccxtconst as ccxtconst
import src.constants.common as common

import logging
from logging import getLogger, basicConfig

formatter = '[%(levelname)s]%(asctime)s %(message)s'
basicConfig(filename=common.CCXT_LOG_FILE_PATH,
            level=logging.INFO,
            format=formatter)


class CcxtClient():
    def __init__(self, exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
        self.logger = getLogger(__name__)

        self.exchange_id = exchange_id
        self.symbol = symbol

        # for demo trade
        exchange_id_for_eval = exchange_id.replace("_demo", "")

        self.exchange = eval('ccxt.{}()'.format(exchange_id_for_eval))

        # for bitmex exchange
        if 'test' in self.exchange.urls:
            self.exchange.urls['api'] = self.exchange.urls['test']

        auth = ccxtconst.EXCHANGE_AUTH_DICT[exchange_id]
        self.exchange.apiKey = auth[ccxtconst.API_KEY]
        self.exchange.secret = auth[ccxtconst.API_SECRET]

    def _exec(self):
        try:
            return self.exchange.fetch_ticker(self.symbol)
        except ccxt.ExchangeNotAvailable as e:
            self.logger.error(e)
            self.logger.error("exchange not available error occured")
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

    def _logging_tick(self, bid, ask):
        self.logger.info('(%s)(%s) tick bid=%s ask=%s', self.exchange_id,
                         self.symbol, bid, ask)

    def fetch_tick(self):
        timestamp_string = datetime.datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S')

        tick = self._exec()

        if tick:
            self._logging_tick(tick["bid"], tick["ask"])
            return {
                "timestamp": timestamp_string,
                "bid": tick["bid"],
                "ask": tick["ask"]
            }
        else:
            self.logger.error('(%s) %s', self.exchange_id, "can't get tick")
            return None

    def fetch_balance(self):
        balance = self.exchange.fetch_balance()
        return balance

    def symbols(self):
        markets = self.exchange.markets
        if markets:
            return list(markets.keys())
        else:
            return []

    def fetch_open_orders(self):
        return self.exchange.fetch_open_orders()

    def get_positions(self):
        return self.exchange.private_get_position()

    def create_market_sell_order(self, amount):
        order_info = self.exchange.create_market_sell_order(symbol=self.symbol,
                                                            amount=amount)

        return order_info

    def create_market_buy_order(self, amount):
        order_info = self.exchange.create_market_buy_order(symbol=self.symbol,
                                                           amount=amount)

        return order_info
