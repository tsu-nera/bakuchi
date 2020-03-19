import os
import pandas as pd
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
import src.utils.json as json

from src.utils.asset import format_btc, format_jpy, format_jpy_float, btc_to_jpy


class TradeAnalysis():
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.dir_path = os.path.join(path.REPORTS_DIR, timestamp)
        self.trades_dir_path = os.path.join(self.dir_path, path.TRADES_DIR)

        self.df_cc = self.read_csv(ccxtconst.EXCHANGE_ID_COINCHECK)
        self.df_lq = self.read_csv(ccxtconst.EXCHANGE_ID_LIQUID)

        self.start_asset = self._read_asset("start")
        self.end_asset = self._read_asset("end")

    def _read_csv(self, file_path):
        return pd.read_csv(file_path, index_col="id",
                           parse_dates=["datetime"]).sort_values('datetime')

    def read_csv(self, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        file_path = os.path.join(self.trades_dir_path, file_name)
        return self._read_csv(file_path)

    def _read_config(self):
        file_path = os.path.join(self.dir_path, path.CONFIG_JSON_FILE)
        return json.read(file_path)

    def _read_asset(self, keyword):
        file_name = "{}.json".format(keyword)
        file_path = os.path.join(self.dir_path, path.ASSETS_DIR, file_name)
        return json.read(file_path)

    def run(self):
        pass

    def _report_trade_meta(self):
        data = []
        config = self._read_config()

        start_timestamp = self.df_cc.iloc[0]["datetime"]
        end_timestamp = self.df_cc.iloc[-1]["datetime"]

        data.append(["取引回数", len(self.df_cc)])
        data.append(["開始日時", start_timestamp])
        data.append(["終了日時", end_timestamp])
        data.append(["取引単位[BTC]", config["amount"]])
        data.append(["利確しきい値[JPY]", config["open_threshold"]])
        data.append(["損切りマージン[JPY]", config["profit_margin_diff"]])

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
            _report_trade_asset_result("JPY", self.start_asset["total"]["jpy"],
                                       self.end_asset["total"]["jpy"]))
        data.extend(
            _report_trade_asset_result("BTC", self.start_asset["total"]["btc"],
                                       self.end_asset["total"]["btc"]))
        data.extend(
            _report_trade_asset_result("TOTAL",
                                       self.start_asset["total"]["total_jpy"],
                                       self.end_asset["total"]["total_jpy"]))

        print("トレード結果")
        print(tabulate(data, tablefmt="grid", numalign="right"))

    def _report_trade_profits(self):

        notrade_start_total_jpy = self.start_asset['total']['total_jpy']
        notrade_end_total_jpy = format_jpy_float(
            self.start_asset['total']['jpy'] + sum([
                btc_to_jpy(self.start_asset[exchange_id]['btc'],
                           self.end_asset[exchange_id]['bid'])
                for exchange_id in ccxtconst.EXCHANGE_ID_LIST
            ]))
        market_profit_jpy = format_jpy_float(notrade_end_total_jpy -
                                             notrade_start_total_jpy)

        profits = []
        profits.append(["Bot利益", "トレード利益", "市場利益"])

        bot_profit = format_jpy_float(self.end_asset["total"]["total_jpy"] -
                                      self.start_asset["total"]["total_jpy"])

        trade_profit = bot_profit - market_profit_jpy
        profits.append([bot_profit, trade_profit, market_profit_jpy])

        print("トレード分析")
        print(
            tabulate(profits,
                     tablefmt="grid",
                     numalign="right",
                     headers="firstrow"))

    def display(self):
        self._report_trade_meta()
        print()
        self._report_trade_stats()
        print()
        self._report_trade_profits()

    def get_coincheck_df(self):
        return self.df_cc

    def get_liquid_df(self):
        return self.df_lq


def run_analysis(timestamp):
    print("=== trade analysis start ===")
    print()

    analysis = TradeAnalysis(timestamp)
    analysis.run()
    analysis.display()

    print()
    print("=== trade analysis end ===")
