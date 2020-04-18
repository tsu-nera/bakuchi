import os
import pandas as pd
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
import src.utils.json as json
import src.utils.datetime as dt

from src.utils.asset import format_jpy_float, btc_to_jpy

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class TradeAnalysis():
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.dir_path = os.path.join(path.REPORTS_DIR, timestamp)
        self.trades_dir_path = os.path.join(self.dir_path, path.TRADES_DIR)
        self.ticks_dir_path = os.path.join(self.dir_path, path.EXCHANGES_DIR)

        self.trades_cc = self.read_trades(ccxtconst.ExchangeId.COINCHECK)
        self.trades_lq = self.read_trades(ccxtconst.ExchangeId.LIQUID)

        self.start_asset = self._read_asset("start")
        self.end_asset = self._read_asset("end")

        self.ticks_cc = self.read_ticks(ccxtconst.ExchangeId.COINCHECK)
        self.ticks_lq = self.read_ticks(ccxtconst.ExchangeId.LIQUID)

        self.result = {}

    def _read_trades(self, file_path):
        return pd.read_csv(file_path, index_col="id",
                           parse_dates=["datetime"]).sort_values('datetime')

    def read_trades(self, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        file_path = os.path.join(self.trades_dir_path, file_name)
        return self._read_trades(file_path)

    def _read_ticks(self, file_path):
        return pd.read_csv(file_path,
                           index_col="timestamp",
                           parse_dates=["timestamp"]).sort_values('timestamp')

    def read_ticks(self, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        file_path = os.path.join(self.ticks_dir_path, file_name)
        return self._read_ticks(file_path)

    def _read_config(self):
        file_path = os.path.join(self.dir_path, path.CONFIG_JSON_FILE)
        return json.read(file_path)

    def _read_asset(self, keyword):
        file_name = "{}.json".format(keyword)
        file_path = os.path.join(self.dir_path, path.ASSETS_DIR, file_name)
        return json.read(file_path)

    def _prepare_result(self):
        config = self._read_config()

        # meta data
        self.result["record_count"] = len(self.ticks_cc)
        self.result["trade_count"] = len(self.trades_cc)
        self.result["start_timestamp"] = self.trades_cc.iloc[0]["datetime"]
        self.result["end_timestamp"] = self.trades_cc.iloc[-1]["datetime"]
        self.result["duration"] = self.result["end_timestamp"] - self.result[
            "start_timestamp"]
        self.result["trade_amount"] = config["amount"]
        self.result["open_threshold"] = config["open_threshold"]
        self.result["profit_margin_diff"] = config["profit_margin_diff"]

        # stats
        self.result["start_price_jpy"] = self.start_asset["total"]["jpy"]
        self.result["end_price_jpy"] = self.end_asset["total"]["jpy"]
        self.result["profit_jpy"] = self.result["end_price_jpy"] - self.result[
            "start_price_jpy"]

        self.result["start_price_btc"] = self.start_asset["total"]["btc"]
        self.result["end_price_btc"] = self.end_asset["total"]["btc"]
        self.result["profit_btc"] = self.result["end_price_btc"] - self.result[
            "start_price_btc"]

        self.result["total_start_price_jpy"] = self.start_asset["total"][
            "total_jpy"]
        self.result["total_end_price_jpy"] = self.end_asset["total"][
            "total_jpy"]
        self.result["total_profit_jpy"] = self.result[
            "total_end_price_jpy"] - self.result["total_start_price_jpy"]

        notrade_start_total_jpy = self.start_asset['total']['total_jpy']
        notrade_end_total_jpy = format_jpy_float(
            self.start_asset['total']['jpy'] + sum([
                btc_to_jpy(self.start_asset[exchange_id]['btc'],
                           self.end_asset[exchange_id]['bid'])
                for exchange_id in ccxtconst.ExchangeId.LIST
            ]))
        self.result["bot_profit_jpy"] = format_jpy_float(
            self.end_asset["total"]["total_jpy"] -
            self.start_asset["total"]["total_jpy"])

        self.result["market_profit_jpy"] = format_jpy_float(
            notrade_end_total_jpy - notrade_start_total_jpy)
        self.result["trade_profit_jpy"] = self.result[
            "bot_profit_jpy"] - self.result["market_profit_jpy"]

    def _report_trade_meta(self):
        data = []

        data.append(["レコード数", self.result["record_count"]])
        data.append(["取引回数", self.result["trade_count"]])
        data.append(["開始日時", self.result["start_timestamp"]])
        data.append(["終了日時", self.result["end_timestamp"]])
        data.append(["取引時間[H]", self.result["duration"]])
        data.append(["取引単位[BTC]", self.result["trade_amount"]])
        data.append(["利確しきい値[JPY]", self.result["open_threshold"]])
        data.append(["損切りマージン[JPY]", self.result["profit_margin_diff"]])

        print("トレード情報")
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

        print("トレード結果")
        print(tabulate(data, tablefmt="grid", numalign="right"))

    def _report_trade_profits(self):

        profits = []
        profits.append(["Bot利益", "トレード利益", "市場利益"])

        profits.append([
            self.result["bot_profit_jpy"], self.result["trade_profit_jpy"],
            self.result["market_profit_jpy"]
        ])

        print("トレード分析")
        print(
            tabulate(profits,
                     tablefmt="grid",
                     numalign="right",
                     headers="firstrow"))

    def display(self):
        self._prepare_result()

        self._report_trade_meta()
        print()
        self._report_trade_stats()
        print()
        self._report_trade_profits()

    def get_coincheck_trades_df(self):
        return self.trades_cc

    def get_liquid_trades_df(self):
        return self.trades_lq

    def get_coincheck_ticks_df(self):
        return self.ticks_cc

    def get_liquid_ticks_df(self):
        return self.ticks_lq

    def create_profit_df(self):
        df = pd.DataFrame({
            'timestamp': self.trades_cc['datetime'].to_list(),
            'cc_side': self.trades_cc['side'].to_list(),
            'cc_price': self.trades_cc['price'].to_list(),
            'lq_side': self.trades_lq['side'].to_list(),
            'lq_price': self.trades_lq['price'].to_list()
        })

        def _calc_profit(x):
            if x['cc_side'] == 'sell':
                cc_price = x['cc_price']
            else:
                cc_price = -1 * x['cc_price']

            if x['lq_side'] == 'sell':
                lq_price = x['lq_price']
            else:
                lq_price = -1 * x['lq_price']

            return cc_price + lq_price

        df['profit'] = df.apply(_calc_profit, axis=1)

        df.timestamp = pd.to_datetime(df.timestamp,
                                      format=dt.DATETIME_BASE_FORMAT)
        df = df.set_index('timestamp')

        return df

    def get_fig(
            self,
            tick_bids,
            tick_asks,
    ):
        timestamps = self.ticks_cc.index

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.set_xlabel('timestamp')
        ax.set_ylabel('btcjpy')
        ax.grid()
        fig.tight_layout()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))

        ax.plot(timestamps, tick_bids, lw=0.5)
        ax.plot(timestamps, tick_asks, lw=0.5)

        ax.scatter(self.trades_cc['datetime'], self.trades_cc['rate'])

        return fig, ax

    def get_result_data(self):
        self._prepare_result()
        return self.result


def run_analysis(timestamp):
    print("=== trade analysis start ===")
    print()

    analysis = TradeAnalysis(timestamp)
    analysis.display()

    print()
    print("=== trade analysis end ===")
