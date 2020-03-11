from time import sleep

from .arbitrage_base import ArbitrageBase
from src.libs.ccxt_client import CcxtClient
from .tick import Tick


class ArbitrageTrading(ArbitrageBase):
    TICK_INTERVAL_SEC = 1

    def __init__(self, exchange_id_x, exchange_id_y):
        super().__init__()

        self.ex_id_x = exchange_id_x
        self.ex_id_y = exchange_id_y

        self.client_x = CcxtClient(exchange_id_x)
        self.client_y = CcxtClient(exchange_id_y)

    def run(self):
        while True:
            sleep(self.TICK_INTERVAL_SEC)
            self.next()

    def _get_tick(self):
        x = self.client_x.fetch_tick()
        y = self.client_y.fetch_tick()

        return Tick(x["date"], x["bid"],
                    x["ask"]), Tick(y["date"], y["bid"], y["ask"])

    def _action(self, result, x, y):
        # とりあえずはbacktestingと同じ

        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            profit = y.bid - x.ask
            print(
                "Coincheckで1BTCを{}円で買いLiquidで1BTCを{}円で売れば、{}円の利益が出ます。".format(
                    x.ask, y.bid, profit))
        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            profit = x.bid - y.ask
            print(
                "Liquidで1BTCを{}円で買いCoincheckで1BTCを{}円で売れば、{}円の利益が出ます。".format(
                    y.ask, x.bid, profit))
        else:
            pass