import sys
import ccxt
import datetime
import requests

from src.libs.logger import get_ccxt_logger
import src.constants.ccxtconst as ccxtconst
from src.libs.exchanges.coincheck import Coincheck


class CcxtClient():
    def __init__(self,
                 exchange_id,
                 symbol=ccxtconst.SYMBOL_BTC_JPY,
                 demo_mode=False):
        self.demo_mode = demo_mode

        self.exchange_id = exchange_id
        self.symbol = symbol
        self.logger = get_ccxt_logger()

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
        self.logger.info('tick bid=%s ask=%s (%s:%s)', bid, ask,
                         self.exchange_id, self.symbol)

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
        try:
            resp = self.exchange.private_get_position()
        except Exception as e:  # noqa
            print("{} api not found".format(self.exchange_id))
            resp = []

        return resp

    def create_market_sell_order(self, amount):
        self.logger.info('(%s:%s) order sell amount=%s', self.exchange_id,
                         self.symbol, amount)

        if self.demo_mode:
            return None

        order_info = self.exchange.create_market_sell_order(symbol=self.symbol,
                                                            amount=amount)
        return order_info

    def create_market_buy_order(self, amount):
        self.logger.info('(%s:%s) order buy amount=%s', self.exchange_id,
                         self.symbol, amount)

        if self.demo_mode:
            return None

        order_info = self.exchange.create_market_buy_order(symbol=self.symbol,
                                                           amount=amount)

        return order_info

    def fetch_trades(self):
        if self.exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
            client = Coincheck()
            trades = client.fetch_my_trades()
        elif self.exchange.has['fetchMyTrades']:
            trades = []
            resp = self.exchange.fetch_my_trades(self.symbol, limit=150)
            for x in resp:
                trade = x['info']
                trade["rate"] = float(trade["price"])
                trade["price"] = round(
                    trade["rate"] * float(trade["quantity"]), 3)
                trades.append(trade)
        else:
            print("fetch_trades api is not supported in {}".format(
                self.exchange_id))
            return []

        res = []
        for trade in trades:
            trade["pair"] = self.symbol
            res.append(trade)
        return res
