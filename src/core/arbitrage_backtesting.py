import time

from tabulate import tabulate

import src.config as config
import src.utils.datetime as dt

from src.core.arbitrage_base import ArbitrageBase
from src.models.tick import Tick
from src.core.exchange_backtesting import ExchangeBacktesting as Exchange

from src.utils.asset import format_btc, format_jpy
from src.utils.asset import read_trading_start_asset, read_trading_end_asset

from src.constants.arbitrage import Strategy


class ArbitrageBacktesting(ArbitrageBase):
    def __init__(self,
                 df_x,
                 df_y,
                 symbol,
                 exchange_x_id,
                 exchange_y_id,
                 timestamp,
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

        self.exchange_x = Exchange(timestamp, exchange_x_id)
        self.exchange_y = Exchange(timestamp, exchange_y_id)

        self.symbol = symbol
        self.start_timestamp = timestamp

        self.histories = []
        self.arbitrage_histories = []
        self.trade_count = 0

        self.start_asset = read_trading_start_asset(timestamp)
        self.end_asset = read_trading_end_asset(timestamp)

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

    def run(self,
            amount=None,
            open_threshold=None,
            profit_margin_diff=None,
            open_threshold_change_sec=None):

        self._update_run_params(amount, open_threshold, profit_margin_diff)
        self.analyzer.update_open_threshold_change_sec(
            open_threshold_change_sec)

        n = len(self.timestamps)

        for i in range(n):
            self.current_index = i
            self.next()

    def _get_tick(self):
        i = self.current_index

        timestamp = self.timestamps[i]
        # 暫定対処。xとyのロジックはいずれ撤廃するので、そのときの見直しでここも対応する。
        exchange_id = None
        tick_x = Tick(exchange_id, timestamp, self.x_bids[i], self.x_asks[i])
        tick_y = Tick(exchange_id, timestamp, self.y_bids[i], self.y_asks[i])

        return tick_x, tick_y

    def _record_history(self, timestamp, exchange_id, order_type, price):
        history = [timestamp, exchange_id.value, order_type, price]
        self.histories.append(history)

    def _record_arbitrage_history(self, timestamp, buy_exchange_id,
                                  sell_exchange_id, symbol, amount, margin):
        expected_profit = int(margin * amount)

        history = [
            timestamp, buy_exchange_id.value, sell_exchange_id.value, symbol,
            amount, expected_profit
        ]

        self.arbitrage_histories.append(history)

    def _action(self, result, tick_x, tick_y):
        if self.simulate_mode:
            time.sleep(1)

        timestamp_string = tick_x.timestamp.strftime(dt.DATETIME_BASE_FORMAT)

        if result == Strategy.BUY_X_SELL_Y:
            self.trade_count += 1
            self.exchange_x.order_buy(self.symbol, self.trade_amount,
                                      tick_x.ask)
            self._record_history(timestamp_string, self.exchange_x_id, "買い",
                                 tick_x.ask)

            self.exchange_y.order_sell(self.symbol, self.trade_amount,
                                       tick_y.bid)
            self._record_history(timestamp_string, self.exchange_y_id, "売り",
                                 tick_y.bid)

            profit_margin = self._get_profit_margin(tick_y.bid, tick_x.ask)

            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_x_id,
                                           self.exchange_y_id, self.symbol,
                                           self.trade_amount, profit_margin)
            if self.simulate_mode:
                print(tick_x.timestamp, result, profit_margin)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyx_selly()

        elif result == Strategy.BUY_Y_SELL_X:
            self.trade_count += 1
            self.exchange_y.order_buy(self.symbol, self.trade_amount,
                                      tick_y.ask)
            self._record_history(timestamp_string, self.exchange_y_id, "買い",
                                 tick_y.ask)

            self.exchange_x.order_sell(self.symbol, self.trade_amount,
                                       tick_x.bid)
            self._record_history(timestamp_string, self.exchange_x_id, "売り",
                                 tick_x.bid)

            profit_margin = self._get_profit_margin(tick_x.bid, tick_y.ask)
            self._record_arbitrage_history(timestamp_string,
                                           self.exchange_y_id,
                                           self.exchange_x_id, self.symbol,
                                           self.trade_amount, profit_margin)

            if self.simulate_mode:
                print(tick_x.timestamp, result, profit_margin)

            self._update_entry_open_margin(profit_margin)
            self._change_status_buyy_sellx()
        else:
            if self.simulate_mode:
                print(tick_x.timestamp, result)
            pass

    def _get_total_jpy(self):
        end_jpy_x = self.exchange_x.get_balance_jpy()
        end_btc_x = self.exchange_x.get_balance_btc()
        end_jpy_y = self.exchange_y.get_balance_jpy()
        end_btc_y = self.exchange_y.get_balance_btc()
        end_bid_x = self.df_x["bid"][0]
        end_bid_y = self.df_y["bid"][-1]

        start_total_jpy = self.start_asset["total"]["total_jpy"]
        end_total_jpy = sum([
            end_jpy_x, end_jpy_y, end_btc_x * end_bid_x, end_btc_y * end_bid_y
        ])

        return start_total_jpy, end_total_jpy

    def _prepare_result(self):
        # meta data
        self.result["record_count"] = len(self.timestamps)
        self.result["trade_count"] = self.trade_count
        self.result["trade_amount"] = self.trade_amount
        self.result["open_threshold"] = self.open_threshold
        self.result["profit_margin_diff"] = self.profit_margin_diff

        # stats
        self.result["start_price_jpy"] = self.start_asset["total"]["jpy"]
        self.result["end_price_jpy"] = format_jpy(
            sum([
                self.exchange_x.get_balance_jpy(),
                self.exchange_y.get_balance_jpy()
            ]))
        self.result["profit_jpy"] = self.result["end_price_jpy"] - self.result[
            "start_price_jpy"]

        self.result["start_price_btc"] = self.start_asset["total"]["btc"]
        self.result["end_price_btc"] = format_btc(
            sum([
                self.exchange_x.get_balance_btc(),
                self.exchange_y.get_balance_btc()
            ]))
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
        data.append(["取引単位[BTC]", self.result["trade_amount"]])
        data.append(["利確しきい値[JPY]", self.result["open_threshold"]])
        data.append(["損切りマージン[JPY]", self.result["profit_margin_diff"]])

        print("バックテスト情報")
        print(tabulate(data, numalign="right", stralign="right"))

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
        print(tabulate(data, numalign="right"))

    def _report_histories(self):
        data = self.histories

        headers = ["日時", "取引所", "注文", "価格"]
        data.insert(0, headers)

        print(tabulate(data, headers="firstrow"))

    def get_result_data(self):
        self._prepare_result()
        return self.result
