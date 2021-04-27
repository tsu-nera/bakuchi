import os
import pandas as pd
from tabulate import tabulate

import src.constants.exchange as exchange
import src.constants.path as path
import src.utils.json as json
import src.utils.datetime as dt

from src.utils.asset import format_jpy_float, btc_to_jpy

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class TradeAnalysis():
    def __init__(self, timestamp):
        # TODO 決め打ちの Exchange idなのであとで修正が入る
        self.__ex1_id = exchange.EXCHANGE_ID_LIST[0]
        self.__ex2_id = exchange.EXCHANGE_ID_LIST[1]

        self.timestamp = timestamp
        self.dir_path = os.path.join(path.REPORTS_DATA_DIR_PATH, timestamp)
        self.trades_dir_path = os.path.join(self.dir_path, path.TRADES_DIR)
        self.ticks_dir_path = os.path.join(self.dir_path, path.EXCHANGES_DIR)

        self.start_asset = self.__read_asset("start")
        self.end_asset = self.__read_asset("end")

        self.__start_timestamp = self.start_asset["timestamp"]
        self.__start_datetime = dt.parse_timestamp(self.__start_timestamp)
        self.__end_timestamp = self.end_asset["timestamp"]
        self.__end_datetime = dt.parse_timestamp(self.__end_timestamp)

        self.trades_ex1 = self.read_trades(self.__ex1_id)
        self.trades_ex2 = self.read_trades(self.__ex2_id)

        self.ticks_ex1 = self.read_ticks(self.__ex1_id)
        self.ticks_ex2 = self.read_ticks(self.__ex2_id)

        self.result = {}

    def __read_trades(self, file_path):
        return pd.read_csv(file_path, index_col="id",
                           parse_dates=["datetime"]).sort_values('datetime')

    def read_trades(self, exchange_id):
        file_name = "{}.csv".format(exchange_id.value)
        file_path = os.path.join(self.trades_dir_path, file_name)
        trades = self.__read_trades(file_path)

        return trades[(trades["datetime"] >= self.__start_datetime)
                      & (trades["datetime"] < self.__end_datetime)]

    def __read_ticks(self, file_path):
        return pd.read_csv(file_path,
                           index_col="timestamp",
                           parse_dates=["timestamp"]).sort_values('timestamp')

    def read_ticks(self, exchange_id):
        file_name = "{}.csv".format(exchange_id.value)
        file_path = os.path.join(self.ticks_dir_path, file_name)
        return self.__read_ticks(file_path)

    def __read_config(self):
        file_path = os.path.join(self.dir_path, path.CONFIG_JSON_FILE)
        return json.read(file_path)

    def __read_asset(self, keyword):
        file_name = "{}.json".format(keyword)
        file_path = os.path.join(self.dir_path, path.ASSETS_DIR, file_name)
        return json.read(file_path)

    def __prepare_result(self):
        config = self.__read_config()

        # meta data
        self.result["record_count"] = len(self.ticks_ex1)
        self.result["trade_count"] = len(self.trades_ex1)
        self.result["start_timestamp"] = self.__start_timestamp
        self.result["end_timestamp"] = self.__end_timestamp

        self.result["duration"] = self.__end_datetime - self.__start_datetime
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
                btc_to_jpy(self.start_asset[exchange_id.value]['btc'],
                           self.end_asset[exchange_id.value]['bid'])
                for exchange_id in exchange.EXCHANGE_ID_LIST
            ]))
        self.result["bot_profit_jpy"] = format_jpy_float(
            self.end_asset["total"]["total_jpy"] -
            self.start_asset["total"]["total_jpy"])

        self.result["market_profit_jpy"] = format_jpy_float(
            notrade_end_total_jpy - notrade_start_total_jpy)
        self.result["trade_profit_jpy"] = self.result[
            "bot_profit_jpy"] - self.result["market_profit_jpy"]

    def __report_trade_meta(self):
        data = []

        data.append(["レコード数", self.result["record_count"]])
        data.append(["取引回数", self.result["trade_count"]])
        data.append(["開始日時", self.result["start_timestamp"]])
        data.append(["終了日時", self.result["end_timestamp"]])
        data.append(["取引時間[H]", self.result["duration"]])
        data.append(["取引単位[BTC]", self.result["trade_amount"]])
        data.append(["利確しきい値[JPY]", self.result["open_threshold"]])
        data.append(["損切りマージン[JPY]", self.result["profit_margin_diff"]])

        heading = "トレード情報"
        body = tabulate(data, numalign="right", stralign="right")

        return "\n".join([heading, body])

    def __report_trade_stats(self):
        data = []

        def __report_trade_asset_result(label, start, end):
            data = []
            profit = end - start
            data.append(["開始[{}]".format(label), start])
            data.append(["終了[{}]".format(label), end])
            data.append(["利益[{}]".format(label), profit])
            return data

        data.extend(
            __report_trade_asset_result("JPY", self.result["start_price_jpy"],
                                        self.result["end_price_jpy"]))
        data.extend(
            __report_trade_asset_result("BTC", self.result["start_price_btc"],
                                        self.result["end_price_btc"]))
        data.extend(
            __report_trade_asset_result("TOTAL",
                                        self.result["total_start_price_jpy"],
                                        self.result["total_end_price_jpy"]))

        heading = "トレード結果"
        body = tabulate(data, numalign="right")

        return "\n".join([heading, body])

    def __report_trade_profits(self):

        profits = []
        profits.append(["Bot利益", "トレード利益", "市場利益"])

        profits.append([
            self.result["bot_profit_jpy"], self.result["trade_profit_jpy"],
            self.result["market_profit_jpy"]
        ])

        heading = "トレード利益"
        body = tabulate(profits, numalign="right", headers="firstrow")

        return "\n".join([heading, body])

    def display(self):
        self.__prepare_result()

        output_meta = self.__report_trade_meta()
        output_stats = self.__report_trade_stats()
        output_profits = self.__report_trade_profits()

        output = "\n".join(
            [output_meta, "\n", output_stats, "\n", output_profits])

        print(output)

    def get_ex1_trades_df(self):
        return self.trades_ex1

    def get_ex2_trades_df(self):
        return self.trades_ex2

    def get_ex1_ticks_df(self):
        return self.ticks_ex1

    def get_ex2_ticks_df(self):
        return self.ticks_ex2

    def create_profit_df(self):
        df = pd.DataFrame({
            'timestamp': self.trades_ex1['datetime'].to_list(),
            'ex1_side': self.trades_ex1['side'].to_list(),
            'ex1_price': self.trades_ex1['price'].to_list(),
            'ex2_side': self.trades_ex2['side'].to_list(),
            'ex2_price': self.trades_ex2['price'].to_list()
        })

        def __calc_profit(x):
            if x['ex1_side'] == 'sell':
                ex1_price = x['ex1_price']
            else:
                ex1_price = -1 * x['ex1_price']

            if x['ex2_side'] == 'sell':
                ex2_price = x['ex2_price']
            else:
                ex2_price = -1 * x['ex2_price']

            return round(ex1_price + ex2_price, 3)

        df['profit'] = df.apply(__calc_profit, axis=1)

        df.timestamp = pd.to_datetime(df.timestamp,
                                      format=dt.DATETIME_BASE_FORMAT)
        df = df.set_index('timestamp')

        return df

    def get_fig(
        self,
        tick_bids,
        tick_asks,
    ):
        timestamps = self.ticks_ex1.index

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.set_xlabel('timestamp')
        ax.set_ylabel('btcjpy')
        ax.grid()
        fig.tight_layout()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
        ax.ticklabel_format(style="plain", axis="y")

        ax.plot(timestamps, tick_bids, lw=0.5)
        ax.plot(timestamps, tick_asks, lw=0.5)

        ax.scatter(self.trades_ex1['datetime'], self.trades_ex1['rate'])

        return fig, ax

    def get_result_data(self):
        self.__prepare_result()
        return self.result


def run_analysis(timestamp):
    print("=== trade analysis start ===")
    print()

    analysis = TradeAnalysis(timestamp)
    analysis.display()

    print()
    print("=== trade analysis end ===")
