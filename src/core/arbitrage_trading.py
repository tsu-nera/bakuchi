from time import sleep
import ccxt

from src.core.tick import Tick
from src.core.arbitrage_base import ArbitrageBase
from src.core.arbitrage_parallel import ArbitrageParallel
from src.core.circuit_breaker import CircuitBreaker

from src.libs.asset import Asset
from src.libs.slack_client import SlackClient

from src.loggers.logger import get_trading_logger
from src.loggers.logger import get_trading_logger_with_stdout
from src.loggers.logger import get_margin_logger
from src.loggers.historical_logger import HistoricalLogger
from src.loggers.order_logger import OrderLogger

import src.utils.datetime as dt

import src.env as env
import src.config as config
from src.constants.ccxtconst import TICK_INTERVAL_SEC, EXCHANGE_ID_COINCHECK


class ArbitrageTrading(ArbitrageBase):
    def __init__(self, exchange_id_x, exchange_id_y, symbol, demo_mode=False):
        super().__init__()

        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y
        self.exchage_ids = [self.ex_id_x, self.ex_id_y]

        self.symbol = symbol
        self.demo_mode = demo_mode

        self.logger = get_trading_logger()
        self.logger_with_stdout = get_trading_logger_with_stdout()
        self.logger_margin = get_margin_logger()

        self.trade_amount = config.TRADE_AMOUNT
        self.open_threshold = config.TRADE_OPEN_THRESHOLD
        self.profit_margin_diff = config.TRADE_PROFIT_MARGIN_DIFF

        self.asset = Asset()
        self.slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)
        self.historical_logger = HistoricalLogger()
        self.order_logger = OrderLogger()

        self.circuit_breaker = CircuitBreaker(self.exchage_ids)

        self.parallel = ArbitrageParallel(exchange_id_x, exchange_id_y, symbol,
                                          demo_mode)

    def run(self):
        self._logging_trading_metadata()

        while True:
            sleep(TICK_INTERVAL_SEC)

            if self.circuit_breaker.is_server_maintenance():
                continue

            try:
                self.next()
            except ccxt.ExchangeNotAvailable:
                self.circuit_breaker.recover_exchange_not_available()
            except ccxt.InsufficientFunds:
                self.circuit_breaker.recover_exchange_not_available()
            except ccxt.NetworkError:
                self.circuit_breaker.recover_network_error()
            except ccxt.DDoSProtection:
                self.circuit_breaker.recover_ddos_protection()

    def _logging_trading_metadata(self):
        self.logger_with_stdout.info(
            "amount={}, open_threshold={}, profit_margin_diff={}".format(
                self.trade_amount, self.open_threshold,
                self.profit_margin_diff))

    def _logging_tick_margin(self, x, y):
        margin_buyx_selly = self._get_profit_margin(y.bid, x.ask)
        margin_buyy_sellx = self._get_profit_margin(x.bid, y.ask)

        base_message_format = "sell-{}/buy-{} margin:{}"
        if self.opened:
            if self.open_direction:
                message_format = base_message_format.format(
                    self.ex_id_y, self.ex_id_x, margin_buyx_selly)
            else:
                message_format = base_message_format.format(
                    self.ex_id_x, self.ex_id_y, margin_buyy_sellx)
        else:
            message_buyx_selly_format = base_message_format.format(
                self.ex_id_y, self.ex_id_x, margin_buyx_selly)
            message_buyy_sellx_format = base_message_format.format(
                self.ex_id_x, self.ex_id_y, margin_buyy_sellx)

        open_threshold_format = "open_threshold:{}".format(self.open_threshold)
        close_threshold_format = "close_threshold:{}".format(
            self._get_close_threshold())

        if self.opened:
            message = "waiting {} {}, {}".format(self.ACTION_CLOSING,
                                                 message_format,
                                                 close_threshold_format)
            self.logger_margin.info(message)
        else:
            message_buyx_selly = "waiting {} {}, {}".format(
                self.ACTION_OPENING, message_buyx_selly_format,
                open_threshold_format)
            message_buyy_sellx = "waiting {} {}, {}".format(
                self.ACTION_OPENING, message_buyy_sellx_format,
                open_threshold_format)

            if margin_buyx_selly > margin_buyy_sellx:
                self.logger_margin.info(message_buyx_selly)
            else:
                self.logger_margin.info(message_buyy_sellx)

    def _logging_tick_historical(self, x, y):
        timestamp = dt.now_timestamp()
        self.historical_logger.logging(self.ex_id_x, timestamp, x.bid, x.ask,
                                       x.timestamp)
        self.historical_logger.logging(self.ex_id_y, timestamp, y.bid, y.ask,
                                       y.timestamp)

    def _logging_open_threshold_change(self):
        if self.analyzer.check_period_for_logging():
            old_threshold = self.open_threshold
            new_threshold = self.analyzer.get_new_open_threshold()

            message = "open threshold changed from {} to {}".format(
                old_threshold, new_threshold)
            self.logger_with_stdout.info(message)

    def _get_tick(self):
        x, y = self.parallel.fetch_tick(eff=True)

        self.raise_exception_if_occured(x)
        self.raise_exception_if_occured(y)

        tick_x = Tick(x["timestamp"], x["bid"], x["ask"]) if x else None
        tick_y = Tick(y["timestamp"], y["bid"], y["ask"]) if y else None

        if x and y:
            self._logging_tick_margin(tick_x, tick_y)
            self._logging_tick_historical(tick_x, tick_y)
            self._logging_open_threshold_change()

        return tick_x, tick_y

    def _calc_expected_profit(self, bid, ask):
        price = bid - ask
        return round(price * self.trade_amount, 1)

    def _calc_profit(self, buy_jpy, sell_jpy):
        price = sell_jpy - buy_jpy
        return round(price, 1)

    def _calc_price(self, rate):
        return self.trade_amount * rate

    def _get_log_label(self):
        return self.ACTION_CLOSING if self.opened else self.ACTION_OPENING

    def _format_expected_profit_message(self, buy_exchange_id, buy_ask,
                                        sell_exchange_id, sell_bid,
                                        expected_profit, profit_margin):
        label = self._get_log_label()
        return "{} buy-{}({}), sell-{}({}), margin={}, profit={}".format(
            label, buy_exchange_id, buy_ask, sell_exchange_id, sell_bid,
            profit_margin, expected_profit)

    def _format_actual_profit_message(self, buy_exchange_id, buy_price_jpy,
                                      sell_exchange_id, sell_price_jpy,
                                      actual_profit, profit_margin):
        label = self._get_log_label()
        return "{} buy-{}({}), sell-{}({}), margin={}, profit={}".format(
            label, buy_exchange_id, round(buy_price_jpy, 3), sell_exchange_id,
            round(sell_price_jpy, 3), profit_margin, actual_profit)

    def _check_order_responses(self, buy, sell):
        def _check_insufficientfunds(e):
            if type(e) == ccxt.ExchangeNotAvailable or type(
                    e) == ccxt.InsufficientFunds:
                raise e

        _check_insufficientfunds(buy)
        _check_insufficientfunds(sell)

    def _action(self, result, x, y):
        label = self._get_log_label()

        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            ask_for_coincheck = x.ask if self.ex_id_x == EXCHANGE_ID_COINCHECK else None
            bid_for_coincheck = y.bid if self.ex_id_y == EXCHANGE_ID_COINCHECK else None

            buy_resp, sell_resp = self.parallel.order_buyx_selly(
                self.trade_amount,
                bid=bid_for_coincheck,
                ask=ask_for_coincheck)

            self._check_order_responses(buy_resp, sell_resp)

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

            self.order_logger.logging(label, self.ex_id_x, x.ask,
                                      self._calc_price(x.ask), self.ex_id_y,
                                      y.bid, self._calc_price(y.bid), profit,
                                      profit_margin)

            if not self.demo_mode:
                self.slack.notify_order(self.ex_id_x, self.ex_id_y,
                                        self.symbol, self.trade_amount, profit)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            ask_for_coincheck = y.ask if self.ex_id_y == EXCHANGE_ID_COINCHECK else None
            bid_for_coincheck = x.bid if self.ex_id_x == EXCHANGE_ID_COINCHECK else None

            buy_resp, sell_resp = self.parallel.order_buyy_sellx(
                self.trade_amount,
                bid=bid_for_coincheck,
                ask=ask_for_coincheck)

            self._check_order_responses(buy_resp, sell_resp)

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
            self.order_logger.logging(label, self.ex_id_y, y.ask,
                                      self._calc_price(y.ask), self.ex_id_x,
                                      x.bid, self._calc_price(x.bid), profit,
                                      profit_margin)

            if not self.demo_mode:
                self.slack.notify_order(self.ex_id_y, self.ex_id_x,
                                        self.symbol, self.trade_amount, profit)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyy_sellx()
        else:
            pass

    def get_current_trading_data_dir(self):
        return self.historical_logger.dir_path

    def raise_exception_if_occured(self, e):
        if isinstance(e, Exception):
            raise (e)
