from time import sleep

import ccxt

from src.core.arbitrage_base import ArbitrageBase
from src.core.arbitrage_parallel import ArbitrageParallel
from src.core.circuit_breaker import CircuitBreaker
from src.core.board import Board

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
from src.constants.exchange import ExchangeId
from src.constants.arbitrage import Strategy, Action


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
        self.tick_interval_sec = config.TRADE_TICK_INTERVAL_SEC

        self.asset = Asset()
        self.slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)
        self.historical_logger = HistoricalLogger()

        self.order_logger = OrderLogger()

        self.circuit_breaker = CircuitBreaker(self.exchage_ids)

        self.parallel = ArbitrageParallel(exchange_id_x, exchange_id_y, symbol,
                                          demo_mode)

        self.board_x = Board(exchange_id_x, symbol)
        self.board_y = Board(exchange_id_y, symbol)

    def run(self):
        self._logging_trading_metadata()

        while True:
            sleep(self.tick_interval_sec)

            if self.circuit_breaker.is_server_maintenance():
                continue
            if self.circuit_breaker.is_opening_longtime(self.opened_timestamp):
                self.circuit_breaker.recover_opening_longtime(self)

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
            "amount={}, open_threshold={}, profit_margin_diff={}, tick_inverval_sec={}"
            .format(self.trade_amount, self.open_threshold,
                    self.profit_margin_diff, self.tick_interval_sec))

    def _logging_tick_margin(self, x, y):
        margin_buyx_selly = self._get_profit_margin(y.bid, x.ask)
        margin_buyy_sellx = self._get_profit_margin(x.bid, y.ask)

        base_message_format = "sell-{}/buy-{} margin:{}"
        if self.opened:
            if self.open_direction:
                message_format = base_message_format.format(
                    self.ex_id_y.value, self.ex_id_x.value, margin_buyx_selly)
            else:
                message_format = base_message_format.format(
                    self.ex_id_x.value, self.ex_id_y.value, margin_buyy_sellx)
        else:
            message_buyx_selly_format = base_message_format.format(
                self.ex_id_y.value, self.ex_id_x.value, margin_buyx_selly)
            message_buyy_sellx_format = base_message_format.format(
                self.ex_id_x.value, self.ex_id_y.value, margin_buyy_sellx)

        open_threshold_format = "open_threshold:{}".format(self.open_threshold)
        close_threshold_format = "close_threshold:{}".format(
            self._get_close_threshold())

        if self.opened:
            message = "waiting {} {}, {}".format(Action.CLOSING.value,
                                                 message_format,
                                                 close_threshold_format)
            self.logger_margin.info(message)
        else:
            message_buyx_selly = "waiting {} {}, {}".format(
                Action.OPENING.value, message_buyx_selly_format,
                open_threshold_format)
            message_buyy_sellx = "waiting {} {}, {}".format(
                Action.OPENING.value, message_buyy_sellx_format,
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
        # tick_x, tick_y = self.parallel.fetch_tick(eff=False)
        tick_x = self.board_x.get_eff_tick(self.trade_amount)
        tick_y = self.board_y.get_eff_tick(self.trade_amount)

        self.__raise_exception_if_occured(tick_x)
        self.__raise_exception_if_occured(tick_y)

        if tick_x and tick_y:
            self._logging_tick_margin(tick_x, tick_y)
            self._logging_tick_historical(tick_x, tick_y)
            self._logging_open_threshold_change()

        return tick_x, tick_y

    def __calc_expected_profit(self, bid, ask):
        price = bid - ask
        return round(price * self.trade_amount, 3)

    def _calc_price(self, rate):
        return round(self.trade_amount * rate, 3)

    def _get_log_label(self):
        return Action.CLOSING.value if self.opened else Action.OPENING.value

    def _format_expected_profit_message(self, buy_exchange_id, buy_ask,
                                        sell_exchange_id, sell_bid,
                                        expected_profit, profit_margin):
        label = self._get_log_label()
        return "[Expect] {} buy-{}({}), sell-{}({}), margin={}, profit={}".format(
            label, buy_exchange_id.value, buy_ask, sell_exchange_id.value,
            sell_bid, profit_margin, expected_profit)

    def _check_order_responses(self, buy, sell):
        def _check_insufficientfunds(e):
            if type(e) == ccxt.ExchangeNotAvailable or type(
                    e) == ccxt.InsufficientFunds:
                raise e

        _check_insufficientfunds(buy)
        _check_insufficientfunds(sell)

    def _action(self, stragegy, tick_x, tick_y):
        def __action_core(bid, ask, func_order):
            if self.ex_id_x == ExchangeId.COINCHECK or self.ex_id_x == ExchangeId.BITBANK:
                extinfo_ask = ask
            else:
                extinfo_ask = None
            if self.ex_id_y == ExchangeId.COINCHECK or self.ex_id_y == ExchangeId.BITBANK:

                extinfo_bid = bid
            else:
                extinfo_bid = None

            buy_resp, sell_resp = func_order(self.trade_amount,
                                             bid=extinfo_bid,
                                             ask=extinfo_ask)

            self._check_order_responses(buy_resp, sell_resp)

            profit_margin = self._get_profit_margin(bid, ask)
            profit = self.__calc_expected_profit(bid, ask)

            label = self._get_log_label()
            message = self._format_expected_profit_message(
                self.ex_id_x, ask, self.ex_id_y, bid, profit, profit_margin)

            self.logger_with_stdout.info(message)
            self.order_logger.logging(label, self.ex_id_x, ask,
                                      self._calc_price(ask), self.ex_id_y, bid,
                                      self._calc_price(bid), profit,
                                      profit_margin)

            self._update_entry_open_margin(profit_margin)
            self.slack.notify_order(self.ex_id_x, self.ex_id_y, self.symbol,
                                    self.trade_amount, profit)

        if stragegy == Strategy.BUY_X_SELL_Y:
            bid = tick_y.bid
            ask = tick_x.ask
            func_order = self.parallel.order_buyx_selly

            __action_core(bid, ask, func_order)

            self._change_status_buyx_selly()

        elif stragegy == Strategy.BUY_Y_SELL_X:
            bid = tick_x.bid
            ask = tick_y.ask
            func_order = self.parallel.order_buyy_sellx

            __action_core(bid, ask, func_order)

            self._change_status_buyy_sellx()
        else:
            pass

    def get_current_trading_data_dir(self):
        return self.historical_logger.dir_path

    def __raise_exception_if_occured(self, e):
        if isinstance(e, Exception):
            raise (e)

    def force_closing(self):
        if not self.opened:
            return

        if self.open_direction:
            stragegy = Strategy.BUY_X_SELL_Y
        else:
            stragegy = Strategy.BUY_Y_SELL_X

        # tick_x, tick_y = self.parallel.fetch_tick(eff=False)
        tick_x = self.board_x.get_eff_tick(self.trade_amount)
        tick_y = self.board_y.get_eff_tick(self.trade_amount)

        self._action(stragegy, tick_x, tick_y)
