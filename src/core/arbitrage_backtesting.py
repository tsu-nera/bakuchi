from tabulate import tabulate

import src.config as config
from src.core.arbitrage_base import ArbitrageBase
from src.core.tick import Tick
from src.core.exchange_backtesting import ExchangeBacktesting as Exchange

import time


class ArbitrageBacktesting(ArbitrageBase):
    def __init__(self,
                 df_x,
                 df_y,
                 symbol,
                 exchange_x_id,
                 exchange_y_id,
                 simulate_mode=False):
        super().__init__()

        self.df_x = df_x
        self.df_y = df_y
        self.simulate_mode = simulate_mode

        self.timestamps = df_x.index
        self.x_bids = df_x.bid.tolist()
        self.x_asks = df_x.ask.tolist()
        self.y_bids = df_y.bid.tolist()
        self.y_asks = df_y.ask.tolist()

        self.current_index = 0

        self.exchange_x_id = exchange_x_id
        self.exchange_y_id = exchange_y_id

        self.exchange_x = Exchange()
        self.exchange_y = Exchange()

        self.symbol = symbol

        self.histories = []
        self.arbitrage_histories = []
        self.trade_count = 0

        self._update_run_params(config.BACKTEST_AMOUNT,
                                config.BACKTEST_PROFIT_MARGIN_THRESHOLD,
                                config.BACKTEST_PROFIT_MARGIN_DIFF)

    def _update_run_params(self, amount, profit_margin_threshold,
                           profit_margin_diff):
        if amount:
            self.trade_amount = amount
        if profit_margin_threshold:
            self.profit_margin_threshold = profit_margin_threshold
        if profit_margin_diff:
            self.profit_margin_diff = profit_margin_diff

    def run(self,
            amount=None,
            profit_margin_threshold=None,
            profit_margin_diff=None):
        self._update_run_params(amount, profit_margin_threshold,
                                profit_margin_diff)

        n = len(self.timestamps)

        for i in range(n):
            self.current_index = i
            self.next()

    def _get_tick(self):
        i = self.current_index

        timestamp = self.timestamps[i]
        tick_x = Tick(timestamp, self.x_bids[i], self.x_asks[i])
        tick_y = Tick(timestamp, self.y_bids[i], self.y_asks[i])

        return tick_x, tick_y

    def _record_history(self, timestamp, exchange_id, order_type, price):
        history = [timestamp, exchange_id, order_type, price]
        self.histories.append(history)

    def _record_arbitrage_history(self, timestamp, buy_exchange_id,
                                  sell_exchange_id, symbol, amount, margin):
        expected_profit = int(margin * amount)

        history = [
            timestamp, buy_exchange_id, sell_exchange_id, symbol, amount,
            expected_profit
        ]

        self.arbitrage_histories.append(history)

    def _action(self, result, x, y):
        if self.simulate_mode:
            time.sleep(1)
        timestamp_string = x.timestamp.strftime('%Y-%m-%d %H:%M:%S')

        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            self.trade_count += 1
            self.exchange_x.order_buy(self.symbol, self.trade_amount, x.ask)
            self._record_history(timestamp_string, "買い", self.exchange_x_id,
                                 x.ask)

            self.exchange_y.order_sell(self.symbol, self.trade_amount, y.bid)
            self._record_history(timestamp_string, "売り", self.exchange_y_id,
                                 y.bid)

            profit_margin = y.bid - x.ask
            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_x_id,
                                           self.exchange_y_id, self.symbol,
                                           self.trade_amount, profit_margin)
            if self.simulate_mode:
                print(x.timestamp, result, profit_margin)

            self._update_entry_profit_margin(profit_margin)
            self._rearrange_action_permission_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            self.trade_count += 1
            self.exchange_y.order_buy(self.symbol, self.trade_amount, y.ask)
            self._record_history(timestamp_string, "買い", self.exchange_y_id,
                                 y.ask)

            self.exchange_x.order_sell(self.symbol, self.trade_amount, x.bid)
            self._record_history(timestamp_string, "売り", self.exchange_x_id,
                                 x.bid)

            profit_margin = x.bid - y.ask
            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_y_id,
                                           self.exchange_x_id, self.symbol,
                                           self.trade_amount, profit_margin)

            if self.simulate_mode:
                print(x.timestamp, result, profit_margin)
                
            self._update_entry_profit_margin(profit_margin)
            self._rearrange_action_permission_buyy_sellx()
        else:
            if self.simulate_mode:
                print(x.timestamp, result)
            pass

    def report(self):
        self._report_trade_meta()
        print()
        self._report_trade_stats()

        # print()
        # self._report_histories()

    def _report_trade_meta(self):
        start_timestamp = self.timestamps[0]
        end_timestamp = self.timestamps[-1]

        data = []
        data.append(["開始日時", start_timestamp])
        data.append(["終了日時", end_timestamp])

        print("バックテスト情報")
        print(tabulate(data))
        print("利確しきい値 {}(JPY)".format(self.profit_margin_threshold))
        print("損切りマージン {}(JPY)".format(self.profit_margin_diff))
        print("取引単位 {}(BTC)".format(self.trade_amount))
        print("--------")

    def _report_trade_stats(self):
        data = []
        data2 = []

        total_profit_btc = round(
            self.exchange_x.get_profit_btc() +
            self.exchange_y.get_profit_btc(), 3)
        total_profit_jpy = int(self.exchange_x.get_profit_jpy() +
                               self.exchange_y.get_profit_jpy())
        total_balance_btc = round(
            self.exchange_x.get_balance_btc() +
            self.exchange_y.get_balance_btc(), 3)
        total_balance_jpy = int(self.exchange_x.get_balance_jpy() +
                                self.exchange_y.get_balance_jpy())

        init_balance_jpy = config.BACKTEST_BALANCE_JPY * 2
        init_balance_btc = config.BACKTEST_BALANCE_BTC * 2

        data.append(["レコード数", len(self.timestamps)])
        data.append(["取引回数", self.trade_count])
        data.append(["利益(JPY)", total_profit_jpy])
        data.append(["元金(JPY)", init_balance_jpy])
        data.append(["資産(JPY)", total_balance_jpy])

        data2.append(["利益(BTC)", total_profit_btc])
        data2.append(["元金(BTC)", init_balance_btc])
        data2.append(["資産(BTC)", total_balance_btc])

        print("バックテスト結果")
        print(tabulate(data2))
        print(tabulate(data))

    def _report_histories(self):
        data = self.histories

        headers = ["日時", "取引所", "注文", "価格"]
        data.insert(0, headers)

        print(tabulate(data, headers="firstrow"))
