from src.core.arbitrage_base import ArbitrageBase
from src.core.tick import Tick
from src.core.exchange_backtesting import ExchangeBacktesting as Exchange


class ArbitrageBacktesting(ArbitrageBase):
    def __init__(self, df_x, df_y):
        super().__init__()

        self.df_x = df_x
        self.df_y = df_y

        self.dates = df_x.index
        self.x_bids = df_x.bid.tolist()
        self.x_asks = df_x.ask.tolist()
        self.y_bids = df_y.bid.tolist()
        self.y_asks = df_y.ask.tolist()

        self.current_index = 0

        self.exchange_x = Exchange()
        self.exchange_y = Exchange()

    def run(self):
        n = len(self.dates)

        for i in range(n):
            self.next()
            self.current_index = i

    def _get_tick(self):
        i = self.current_index

        date = self.dates[i]
        tick_x = Tick(date, self.x_bids[i], self.x_asks[i])
        tick_y = Tick(date, self.y_bids[i], self.y_asks[i])

        return tick_x, tick_y

    def _action(self, result, x, y):
        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            profit = y.bid - x.ask
            print("{} Coincheckで1BTCを{}円で買いLiquidで1BTCを{}円で売れば、{}円の利益が出ます。".
                  format(x.date, x.ask, y.bid, profit))
            self.exchange_x.buy()
            self.exchange_y.sell()
            self._rearrange_action_permission_buyx_selly()
        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            profit = x.bid - y.ask
            print("{} Liquidで1BTCを{}円で買いCoincheckで1BTCを{}円で売れば、{}円の利益が出ます。".
                  format(x.date, y.ask, x.bid, profit))
            self.exchange_y.buy()
            self.exchange_x.sell()
            self._rearrange_action_permission_buyy_sellx()
        else:
            pass

    def report(self):
        print()
        print("comming soon...")
