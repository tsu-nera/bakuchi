from time import sleep

from .arbitrage_base import ArbitrageBase
from src.libs.ccxt_client import CcxtClient
from src.constants.ccxtconst import TICK_INTERVAL_SEC
from .tick import Tick
from src.core.exchange_trading import ExchangeTrading as Exchange

from src.config import config
from src.libs.logger import get_trading_logger
from src.libs.logger import get_trading_logger_with_stdout


class ArbitrageTrading(ArbitrageBase):
    def __init__(self, exchange_id_x, exchange_id_y, symbol):
        super().__init__()

        self.profilt_mergin_threshold = int(
            config["trade"]["profit_mergin_threshold"])
        self.trade_amount = float(config["trade"]["amount"])

        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y
        self.symbol = symbol

        self.exchange_x = Exchange(exchange_id_x, symbol)
        self.exchange_y = Exchange(exchange_id_y, symbol)

        self.client_x = CcxtClient(exchange_id_x)
        self.client_y = CcxtClient(exchange_id_y)

        self.logger = get_trading_logger()
        self.logger_with_stdout = get_trading_logger_with_stdout()

        self.trade_amount = float(config["trade"]["amount"])
        self.profilt_mergin_threshold = int(
            config["trade"]["profit_mergin_threshold"])

    def run(self):
        while True:
            sleep(TICK_INTERVAL_SEC)
            self.next()

    def _get_tick(self):
        x = self.client_x.fetch_tick()
        y = self.client_y.fetch_tick()

        return Tick(x["timestamp"], x["bid"],
                    x["ask"]), Tick(y["timestamp"], y["bid"], y["ask"])

    def _action(self, result, x, y):
        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            self.exchange_x.order_buy(self.trade_amount)
            self.exchange_y.order_sell(self.trade_amount)

            profit = y.bid - x.ask
            message = "buy {} ask={}, sell {} bid={}, expected_profit={}".format(
                self.ex_id_x, x.ask, self.ex_id_y, y.bid, profit)

            self.logger_with_stdout.info(message)

            self._rearrange_action_permission_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            self.exchange_y.order_buy(self.trade_amount)
            self.exchange_x.order_sell(self.trade_amount)

            profit = x.bid - y.ask
            message = "buy {} ask={}, sell {} bid={}, expected_profit={}".format(
                self.ex_id_y, y.ask, self.ex_id_x, x.bid, profit)

            self.logger_with_stdout.info(message)

            self._rearrange_action_permission_buyy_sellx()

        else:
            pass
