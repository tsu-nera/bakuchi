from time import sleep
import datetime

from .arbitrage_base import ArbitrageBase
from src.constants.ccxtconst import TICK_INTERVAL_SEC, EXCHANGE_ID_COINCHECK, EXCHANGE_ID_LIQUID
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
    def __init__(self, exchange_id_x, exchange_id_y, symbol, demo_mode=False):
        super().__init__()

        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y
        self.symbol = symbol
        self.demo_mode = demo_mode

        self.exchange_x = Exchange(exchange_id_x, symbol, demo_mode=demo_mode)
        self.exchange_y = Exchange(exchange_id_y, symbol, demo_mode=demo_mode)

        self.logger = get_trading_logger()
        self.logger_with_stdout = get_trading_logger_with_stdout()
        self.logger_margin = get_margin_logger()

        self.trade_amount = config.TRADE_AMOUNT
        self.open_threshold = config.TRADE_OPEN_THRESHOLD
        self.profit_margin_diff = config.TRADE_PROFIT_MARGIN_DIFF

        self.asset = Asset()
        self.slack = SlackClient()
        self.historical_logger = HistoricalLogger()

    def run(self):
        self._logging_trading_metadata()

        while True:
            sleep(TICK_INTERVAL_SEC)

            if not self.is_server_maintenance(
                    self.ex_id_x) and not self.is_server_maintenance(
                        self.ex_id_y):
                self.next()

    def _is_liquid_server_maintenance(self):
        now = datetime.datetime.now()
        # 6:55
        maintenance_start_time = datetime.datetime(now.year, now.month,
                                                   now.day, 6, 55, 0)
        # 7:05
        maintenance_end_time = datetime.datetime(now.year, now.month, now.day,
                                                 7, 5, 0)

        if maintenance_start_time <= now and now <= maintenance_end_time:
            self.logger_with_stdout.info(
                "liquid is currently daily server maintenance...(6:55-7:05)")
            return True
        else:
            return False

    def is_server_maintenance(self, exchange_id):
        # 臨時サーバメンテナンスのときもとりあえずここに判定を追記していく。

        if exchange_id == EXCHANGE_ID_LIQUID:
            return self._is_liquid_server_maintenance()
        else:
            return False

    def _logging_trading_metadata(self):
        self.logger_with_stdout.info(
            "amount={}, open_threshold={}, profit_margin_diff={}".format(
                self.trade_amount, self.open_threshold,
                self.profit_margin_diff))

    def _logging_tick_margin(self, x, y):
        buy_y_sell_x_margin = self._get_profit_margin(x.bid, y.ask)
        buy_x_sell_y_margin = self._get_profit_margin(y.bid, x.ask)

        message = "sell[{}] buy[{}] margin={}, sell[{}] buy[{}] margin={}, opened={}, open_threshold={}, close_threshold={}".format(
            self.ex_id_x, self.ex_id_y, buy_y_sell_x_margin, self.ex_id_y,
            self.ex_id_x, buy_x_sell_y_margin, self.opened,
            self.open_threshold, self._get_close_threshold())

        self.logger_margin.info(message)

    def _logging_tick_historical(self, x, y):
        self.historical_logger.logging(self.ex_id_x, x.timestamp, x.bid, x.ask)
        self.historical_logger.logging(self.ex_id_y, y.timestamp, y.bid, y.ask)

    def _logging_profit_margin_threshold_change(self):
        if self.analyzer.check_period_for_logging():
            old_threshold = self.open_threshold
            new_threshold = self.analyzer.get_new_profit_margin_threshold()

            message = "open threshold changed from {} to {}".format(
                old_threshold, new_threshold)
            self.logger_with_stdout.info(message)

    def _get_tick(self):
        x = self.exchange_x.fetch_tick()
        y = self.exchange_y.fetch_tick()

        tick_x = Tick(x["timestamp"], x["bid"], x["ask"]) if x else None
        tick_y = Tick(y["timestamp"], y["bid"], y["ask"]) if y else None

        if x and y:
            self._logging_tick_margin(tick_x, tick_y)
            self._logging_tick_historical(tick_x, tick_y)
            self._logging_profit_margin_threshold_change()

        return tick_x, tick_y

    def _calc_expected_profit(self, bid, ask):
        price = bid - ask
        return round(price * self.trade_amount, 1)

    def _calc_profit(self, buy_jpy, sell_jpy):
        price = sell_jpy - buy_jpy
        return round(price, 1)

    def _get_log_label(self):
        return self.ACTION_CLOSE if self.opened else self.ACTION_OPEN

    def _format_expected_profit_message(self, buy_exchange_id, buy_ask,
                                        sell_exchange_id, sell_bid,
                                        expected_profit, profit_margin):
        label = self._get_log_label()
        return "{} buy {}({}), sell {}({}), margin={}, profit={}".format(
            label, buy_exchange_id, buy_ask, sell_exchange_id, sell_bid,
            profit_margin, expected_profit)

    def _format_actual_profit_message(self, buy_exchange_id, buy_price_jpy,
                                      sell_exchange_id, sell_price_jpy,
                                      actual_profit, profit_margin):
        label = self._get_log_label()
        return "{} buy {}({}), sell {}({}), margin={}, profit={}".format(
            label, buy_exchange_id, round(buy_price_jpy, 3), sell_exchange_id,
            round(sell_price_jpy, 3), profit_margin, actual_profit)

    def _action(self, result, x, y):
        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            ask_for_coincheck = x.ask if self.ex_id_x == EXCHANGE_ID_COINCHECK else None
            bid_for_coincheck = y.bid if self.ex_id_y == EXCHANGE_ID_COINCHECK else None

            buy_resp = self.exchange_x.order_buy(
                self.trade_amount, ask_for_coincheck=ask_for_coincheck)
            sell_resp = self.exchange_y.order_sell(
                self.trade_amount, bid_for_coincheck=bid_for_coincheck)

            profit_margin = self._get_profit_margin(y.bid, x.ask)

            if (not self.demo_mode) or (buy_resp and sell_resp):
                profit = self._calc_profit(buy_resp["jpy"], sell_resp["jpy"])
                message = self._format_actual_profit_message(
                    self.ex_id_x, buy_resp["jpy"], self.ex_id_y,
                    sell_resp["jpy"], profit, profit_margin)
            else:
                profit = self._calc_expected_profit(y.bid, x.ask)
                message = self._format_expected_profit_message(
                    self.ex_id_x, x.ask, self.ex_id_y, y.bid, profit,
                    profit_margin)

            self.logger_with_stdout.info(message)

            # order をだした直後だと早すぎてassetに反映されていない。
            # クラッシュするので一旦封印
            # self.asset.logging()

            if not self.demo_mode:
                self.slack.notify_order(self.ex_id_x, self.ex_id_y,
                                        self.symbol, self.trade_amount, profit)

            self._update_entry_profit_margin(profit_margin)
            self._change_status_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            ask_for_coincheck = y.ask if self.ex_id_y == EXCHANGE_ID_COINCHECK else None
            bid_for_coincheck = x.bid if self.ex_id_x == EXCHANGE_ID_COINCHECK else None

            buy_resp = self.exchange_y.order_buy(
                self.trade_amount, ask_for_coincheck=ask_for_coincheck)
            sell_resp = self.exchange_x.order_sell(
                self.trade_amount, bid_for_coincheck=bid_for_coincheck)

            profit_margin = self._get_profit_margin(x.bid, y.ask)

            if (not self.demo_mode) or (buy_resp and sell_resp):
                profit = self._calc_profit(buy_resp["jpy"], sell_resp["jpy"])
                message = self._format_actual_profit_message(
                    self.ex_id_y, buy_resp["jpy"], self.ex_id_x,
                    sell_resp["jpy"], profit, profit_margin)
            else:
                profit = self._calc_expected_profit(x.bid, y.ask)
                message = self._format_expected_profit_message(
                    self.ex_id_y, y.ask, self.ex_id_x, x.bid, profit,
                    profit_margin)

            self.logger_with_stdout.info(message)

            # order をだした直後だと早すぎてassetに反映されていない。
            # クラッシュするので一旦封印
            # self.asset.logging()

            if not self.demo_mode:
                self.slack.notify_order(self.ex_id_y, self.ex_id_x,
                                        self.symbol, self.trade_amount, profit)

            self._update_entry_profit_margin(profit_margin)
            self._change_status_buyy_sellx()
        else:
            pass

    def get_current_trading_data_dir(self):
        return self.historical_logger.dir_path
