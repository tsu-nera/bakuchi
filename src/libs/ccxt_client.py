import sys

import ccxt

from src.loggers.logger import get_ccxt_logger
import src.constants.ccxtconst as ccxtconst
import src.utils.datetime as dt
from src.libs.exchanges.coincheck import Coincheck
from src.core.tick import Tick


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
        exchange_id_for_eval = exchange_id.value.replace("_demo", "")

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
                         self.exchange_id.value, self.symbol)

    def fetch_tick(self):
        timestamp = dt.now_timestamp()
        tick = self._exec()

        if tick:
            self._logging_tick(tick["bid"], tick["ask"])
            return Tick(timestamp, tick["bid"], tick["ask"])
        else:
            self.logger.error('(%s) %s', self.exchange_id.value,
                              "can't get tick")
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

    def fetch_order_book(self):
        return self.exchange.fetch_order_book(self.symbol)

    def get_positions(self):
        try:
            resp = self.exchange.private_get_position()
        except Exception as e:  # noqa
            print("{} api not found".format(self.exchange_id.value))
            resp = []

        return resp

    def create_market_sell_order(self, amount):
        self.logger.info('(%s:%s) order sell amount=%s',
                         self.exchange_id.value, self.symbol, amount)

        if self.demo_mode:
            return None

        if self.exchange_id == ccxtconst.ExchangeId.BITBANK:
            order_info = self.exchange.create_market_order(symbol=self.symbol,
                                                           side="sell",
                                                           amount=amount,
                                                           price=1)
            return order_info

        order_info = self.exchange.create_market_sell_order(symbol=self.symbol,
                                                            amount=amount)
        return order_info

    def create_market_buy_order(self, amount):
        self.logger.info('(%s:%s) order buy amount=%s', self.exchange_id.value,
                         self.symbol, amount)

        if self.demo_mode:
            return None

        # bitbankはpriceに値を設定しないと謎のエラールートにはいるので。
        # なんだこれは、バグか？へんなワークアラウンドロジックはいれたくないなあ。
        if self.exchange_id == ccxtconst.ExchangeId.BITBANK:
            order_info = self.exchange.create_market_order(symbol=self.symbol,
                                                           side="buy",
                                                           amount=amount,
                                                           price=1)
            return order_info

        order_info = self.exchange.create_market_buy_order(symbol=self.symbol,
                                                           amount=amount)
        return order_info

    def fetch_trades(self, mode):
        if self.exchange_id == ccxtconst.ExchangeId.COINCHECK:
            client = Coincheck()
            trades = client.fetch_my_trades(mode)
        elif self.exchange.has['fetchMyTrades']:

            if mode == ccxtconst.TradeMode.NORMAL:
                limit = 1000
            else:
                limit = 30

            trades = []
            resp = self.exchange.fetch_my_trades(self.symbol, limit=limit)
            for x in resp:
                trade = x['info']
                trades.append(trade)
        else:
            print("fetch_trades api is not supported in {}".format(
                self.exchange_id.value))
            return []

        res = []
        for trade in trades:
            trade["pair"] = self.symbol
            res.append(trade)
        return res

    def fetch_eff_tick(self, size=1):
        timestamp = dt.now_timestamp()

        book = self.exchange.fetch_order_book(self.symbol)

        if book:
            # 実効ASK計算
            i = 0
            s = 0
            while s <= size:
                s += book['asks'][i][1]
                i += 1

            # 実効BID計算
            j = 0
            t = 0
            while t <= size:
                t += book['bids'][j][1]
                j += 1

            bid = book['bids'][i - 1][0]
            ask = book['asks'][j - 1][0]

            self._logging_tick(bid, ask)

            return Tick(timestamp, bid, ask)
        else:
            self.logger.error('(%s) %s', self.exchange_id.value,
                              "can't get tick")
            return None
