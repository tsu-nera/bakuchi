from time import sleep

from .arbitrage_base import ArbitrageBase
from src.libs.ccxt_client import CcxtClient
from src.constants.ccxtconst import TICK_INTERVAL_SEC, EXCHANGE_ID_COINCHECK
from .tick import Tick
from src.core.exchange_trading import ExchangeTrading as Exchange
from src.libs.asset import Asset
from src.libs.slack_client import SlackClient

import src.config as config
from src.libs.logger import get_trading_logger
from src.libs.logger import get_trading_logger_with_stdout

from src.libs.logger import get_margin_logger
from src.libs.historical_logger import HistoricalLogger


class ArbitrageTrading(ArbitrageBase):
    def __init__(self, exchange_id_x, exchange_id_y, symbol):
        super().__init__()

        self.trade_amount = config.TRADE_AMOUNT
        self.profit_margin_threshold = config.TRADE_PROFIT_MARGIN_THRESHOLD

        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y
        self.symbol = symbol

        self.exchange_x = Exchange(exchange_id_x, symbol)
        self.exchange_y = Exchange(exchange_id_y, symbol)

        self.client_x = CcxtClient(exchange_id_x)
        self.client_y = CcxtClient(exchange_id_y)

        self.logger = get_trading_logger()
        self.logger_with_stdout = get_trading_logger_with_stdout()
        self.logger_margin = get_margin_logger()

        self.trade_amount = config.TRADE_AMOUNT
        self.profit_margin_threshold = config.TRADE_PROFIT_MARGIN_THRESHOLD

        self.asset = Asset()
        self.slack = SlackClient()
        self.historical_logger = HistoricalLogger()

    def run(self):
        self.logger_with_stdout.info(
            "amount={}, profit_margin_threshold={}".format(
                self.trade_amount, self.profit_margin_threshold))

        while True:
            sleep(TICK_INTERVAL_SEC)
            self.next()

    def _logging_tick_margin(self, x, y):
        buy_y_sell_x_margin = x.bid - y.ask
        buy_x_sell_y_margin = y.bid - x.ask

        message = "sell[{}] buy[{}] margin={}, sell[{}] buy[{}] margin={}, action_permission={}".format(
            self.ex_id_x, self.ex_id_y, buy_y_sell_x_margin, self.ex_id_y,
            self.ex_id_x, buy_x_sell_y_margin, self.action_permission)

        self.logger_margin.info(message)

    def _logging_tick_historical(self, x, y):
        self.historical_logger.logging(self.ex_id_x, x.timestamp, x.bid, x.ask)
        self.historical_logger.logging(self.ex_id_y, y.timestamp, y.bid, x.ask)

    def _get_tick(self):
        x = self.client_x.fetch_tick()
        y = self.client_y.fetch_tick()

        tick_x = Tick(x["timestamp"], x["bid"], x["ask"]) if x else None
        tick_y = Tick(y["timestamp"], y["bid"], y["ask"]) if y else None

        if x and y:
            self._logging_tick_margin(tick_x, tick_y)
            self._logging_tick_historical(tick_x, tick_y)

        return tick_x, tick_y

    def _calc_expected_profit(self, bid, ask):
        price = bid - ask
        return round(price * self.trade_amount, 1)

    def _action(self, result, x, y):
        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            ask_for_coincheck = x.ask if self.ex_id_x == EXCHANGE_ID_COINCHECK else None
            self.exchange_x.order_buy(self.trade_amount, ask_for_coincheck)
            self.exchange_y.order_sell(self.trade_amount)

            profit = self._calc_expected_profit(y.bid, x.ask)
            message = "buy {} ask={}, sell {} bid={}, expected_profit={}".format(
                self.ex_id_x, x.ask, self.ex_id_y, y.bid, profit)

            self.logger_with_stdout.info(message)

            # order をだした直後だと早すぎてassetに反映されていない。
            # クラッシュするので一旦封印
            # self.asset.logging()

            self.slack.notify(message)

            self._rearrange_action_permission_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            ask_for_coincheck = y.ask if self.ex_id_y == EXCHANGE_ID_COINCHECK else None
            self.exchange_y.order_buy(self.trade_amount, ask_for_coincheck)
            self.exchange_x.order_sell(self.trade_amount)

            profit = self._calc_expected_profit(x.bid, y.ask)
            message = "buy {} ask={}, sell {} bid={}, expected_profit={}".format(
                self.ex_id_y, y.ask, self.ex_id_x, x.bid, profit)

            self.logger_with_stdout.info(message)

            # order をだした直後だと早すぎてassetに反映されていない。
            # クラッシュするので一旦封印
            # self.asset.logging()

            self._rearrange_action_permission_buyy_sellx()

        else:
            pass
