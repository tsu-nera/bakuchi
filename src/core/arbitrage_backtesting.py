import time
from tabulate import tabulate

import src.config as config
import src.utils.datetime as dt

from src.core.arbitrage_base import ArbitrageBase
from src.core.tick import Tick
from src.core.exchange_backtesting import ExchangeBacktesting as Exchange


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
                                config.BACKTEST_OPEN_THRESHOLD,
                                config.BACKTEST_PROFIT_MARGIN_DIFF)

        self.result = {}

    def _update_run_params(self, amount, open_threshold, profit_margin_diff):
        if amount:
            self.trade_amount = amount
        if open_threshold:
            self.open_threshold = open_threshold
        if profit_margin_diff:
            self.profit_margin_diff = profit_margin_diff

    def run(self, amount=None, open_threshold=None, profit_margin_diff=None):
        self._update_run_params(amount, open_threshold, profit_margin_diff)

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
        timestamp_string = x.timestamp.strftime(dt.DATETIME_BASE_FORMAT)

        if result == self.STRATEGY_BUY_X_AND_SELL_Y:
            self.trade_count += 1
            self.exchange_x.order_buy(self.symbol, self.trade_amount, x.ask)
            self._record_history(timestamp_string, "買い", self.exchange_x_id,
                                 x.ask)

            self.exchange_y.order_sell(self.symbol, self.trade_amount, y.bid)
            self._record_history(timestamp_string, "売り", self.exchange_y_id,
                                 y.bid)

            profit_margin = self._get_profit_margin(y.bid, x.ask)

            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_x_id,
                                           self.exchange_y_id, self.symbol,
                                           self.trade_amount, profit_margin)
            if self.simulate_mode:
                print(x.timestamp, result, profit_margin)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyx_selly()

        elif result == self.STRATEGY_BUY_Y_AND_SELL_X:
            self.trade_count += 1
            self.exchange_y.order_buy(self.symbol, self.trade_amount, y.ask)
            self._record_history(timestamp_string, "買い", self.exchange_y_id,
                                 y.ask)

            self.exchange_x.order_sell(self.symbol, self.trade_amount, x.bid)
            self._record_history(timestamp_string, "売り", self.exchange_x_id,
                                 x.bid)

            profit_margin = self._get_profit_margin(x.bid, y.ask)
            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_y_id,
                                           self.exchange_x_id, self.symbol,
                                           self.trade_amount, profit_margin)

            if self.simulate_mode:
                print(x.timestamp, result, profit_margin)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyy_sellx()
        else:
            if self.simulate_mode:
                print(x.timestamp, result)
            pass

    def _get_total_jpy(self):
        start_jpy_x = config.BACKTEST_BALANCE_JPY
        start_btc_x = config.BACKTEST_BALANCE_BTC
        start_jpy_y = config.BACKTEST_BALANCE_JPY
        start_btc_y = config.BACKTEST_BALANCE_BTC
        start_bid_x = self.df_x["bid"][0]
        start_bid_y = self.df_y["bid"][-1]

        end_jpy_x = self.exchange_x.get_balance_jpy()
        end_btc_x = self.exchange_x.get_balance_btc()
        end_jpy_y = self.exchange_y.get_balance_jpy()
        end_btc_y = self.exchange_y.get_balance_btc()
        end_bid_x = self.df_x["bid"][0]
        end_bid_y = self.df_y["bid"][-1]

        start_total_jpy = sum([
            start_jpy_x, start_jpy_y, start_btc_x * start_bid_x,
            start_btc_y * start_bid_y
        ])
        end_total_jpy = sum([
            end_jpy_x, end_jpy_y, end_btc_x * end_bid_x, end_btc_y * end_bid_y
        ])

        return start_total_jpy, end_total_jpy

    def _prepare_result(self):
        # meta data
        self.result["record_count"] = len(self.timestamps)
        self.result["trade_count"] = self.trade_count
        self.result["start_timestamp"] = self.timestamps[0]
        self.result["end_timestamp"] = self.timestamps[-1]
        self.result["trade_amount"] = self.trade_amount
        self.result["open_threshold"] = self.open_threshold
        self.result["profit_margin_diff"] = self.profit_margin_diff

        # stats
        self.result["start_price_jpy"] = config.BACKTEST_BALANCE_JPY * 2
        self.result["end_price_jpy"] = sum([
            self.exchange_x.get_balance_jpy(),
            self.exchange_y.get_balance_jpy()
        ])
        self.result["profit_jpy"] = self.result["end_price_jpy"] - self.result[
            "start_price_jpy"]

        self.result["start_price_btc"] = config.BACKTEST_BALANCE_BTC * 2
        self.result["end_price_btc"] = sum([
            self.exchange_x.get_balance_btc(),
            self.exchange_y.get_balance_btc()
        ])
        self.result["profit_btc"] = self.result["end_price_btc"] - self.result[
            "start_price_btc"]

        total_start_price_jpy, total_end_price_jpy = self._get_total_jpy()

        self.result["total_start_price_jpy"] = total_start_price_jpy
        self.result["total_end_price_jpy"] = total_end_price_jpy
        self.result["total_profit_jpy"] = self.result[
            "total_end_price_jpy"] - self.result["total_start_price_jpy"]

    def report(self):
        self._prepare_result()

        self._report_trade_meta()
        print()
        self._report_trade_stats()

        # print()
        # self._report_histories()

    def _report_trade_meta(self):
        data = []

        data.append(["レコード数", self.result["record_count"]])
        data.append(["取引回数", self.result["trade_count"]])
        data.append(["開始日時", self.result["start_timestamp"]])
        data.append(["終了日時", self.result["end_timestamp"]])
        data.append(["取引単位[BTC]", self.result["trade_amount"]])
        data.append(["利確しきい値[JPY]", self.result["open_threshold"]])
        data.append(["損切りマージン[JPY]", self.result["profit_margin_diff"]])

        print("バックテスト情報")
        print(
            tabulate(data, tablefmt="grid", numalign="right",
                     stralign="right"))

    def _report_trade_stats(self):
        data = []

        def _report_trade_asset_result(label, start, end):
            data = []
            profit = end - start
            data.append(["開始[{}]".format(label), start])
            data.append(["終了[{}]".format(label), end])
            data.append(["利益[{}]".format(label), profit])
            return data

        data.extend(
            _report_trade_asset_result("JPY", self.result["start_price_jpy"],
                                       self.result["end_price_jpy"]))
        data.extend(
            _report_trade_asset_result("BTC", self.result["start_price_btc"],
                                       self.result["end_price_btc"]))

        data.extend(
            _report_trade_asset_result("TOTAL",
                                       self.result["total_start_price_jpy"],
                                       self.result["total_end_price_jpy"]))

        print("バックテスト結果")
        print(tabulate(data, tablefmt="grid", numalign="right"))

    def _report_histories(self):
        data = self.histories

        headers = ["日時", "取引所", "注文", "価格"]
        data.insert(0, headers)

        print(tabulate(data, headers="firstrow"))

    def get_result_data(self):
        self._prepare_result()
        return self.result
