import os
import pandas as pd
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
import src.utils.json as json


class TradeAnalysis():
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.dir_path = os.path.join(path.REPORTS_DIR, timestamp)
        self.trades_dir_path = os.path.join(self.dir_path, path.TRADES_DIR)

        self.df_cc = self.read_csv(ccxtconst.EXCHANGE_ID_COINCHECK)
        self.df_lq = self.read_csv(ccxtconst.EXCHANGE_ID_LIQUID)

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

    def run(self):
        pass

    def _report_trade_meta(self):
        data = []
        config = self._read_config()

        start_timestamp = self.df_cc.iloc[0]["datetime"]
        end_timestamp = self.df_cc.iloc[-1]["datetime"]

        data.append(["開始日時", start_timestamp])
        data.append(["終了日時", end_timestamp])
        data.append(["取引単位[BTC]", config["amount"]])
        data.append(["利確しきい値[JPY]", config["open_threshold"]])
        data.append(["損切りマージン[JPY]", config["profit_margin_diff"]])

        print("バックテスト情報")
        print(tabulate(data, tablefmt="grid", numalign="right", stralign="right"))

    def _report_trade_stats(self):
        pass

    def display(self):
        self._report_trade_meta()
        print()
        self._report_trade_stats()

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
