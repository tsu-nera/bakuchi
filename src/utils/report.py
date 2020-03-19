import os
import glob
from distutils.dir_util import copy_tree

from tabulate import tabulate

import src.constants.path as path

from src.utils.backtesting import Backtesting
from src.utils.trade_analysis import TradeAnalysis


def get_latest_dirpath(dir_path):
    return max(glob.glob(os.path.join(dir_path, '*/')), key=os.path.getmtime)


def generate(dir_name):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = os.path.join(production_dir, dir_name)
    to_dir = os.path.join(path.REPORTS_DIR, dir_name)

    copy_tree(from_dir, to_dir)


def generate_latest():
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = get_latest_dirpath(production_dir)
    dir_name = from_dir.split('/')[-2]

    generate(dir_name)


def display(timestamp):
    backtesting = Backtesting(timestamp)
    trade_analysis = TradeAnalysis(timestamp)

    backtest_data = backtesting.get_result_data()
    trade_data = trade_analysis.get_result_data()

    def _report_trade_meta(backtest, trade):
        data = []
        data.append(["レコード数", backtest["record_count"], trade["record_count"]])
        data.append(["取引回数", backtest["trade_count"], trade["trade_count"]])
        data.append(
            ["開始日時", backtest["start_timestamp"], trade["start_timestamp"]])
        data.append(
            ["終了日時", backtest["end_timestamp"], trade["end_timestamp"]])
        data.append(
            ["取引単位[BTC]", backtest["trade_amount"], trade["trade_amount"]])
        data.append([
            "利確しきい値[JPY]", backtest["open_threshold"], trade["open_threshold"]
        ])
        data.append([
            "損切りマージン[JPY]", backtest["profit_margin_diff"],
            trade["profit_margin_diff"]
        ])

        print("トレード情報")
        headers = ["", "バックテスト", "トレード"]
        print(
            tabulate(data,
                     tablefmt="grid",
                     numalign="right",
                     stralign="right",
                     headers=headers))

    def _report_trade_stats(backtest, trade):
        data = []

        data.append(
            ["開始[JPY]", backtest["start_price_jpy"], trade["start_price_jpy"]])
        data.append(
            ["終了[JPY]", backtest["end_price_jpy"], trade["end_price_jpy"]])
        data.append(["利益[JPY]", backtest["profit_jpy"], trade["profit_jpy"]])
        data.append(
            ["開始[BTC]", backtest["start_price_btc"], trade["start_price_btc"]])
        data.append(
            ["終了[BTC]", backtest["end_price_btc"], trade["end_price_btc"]])
        data.append(["利益[BTC]", backtest["profit_btc"], trade["profit_btc"]])
        data.append([
            "開始[TOTAL]", backtest["total_start_price_jpy"],
            trade["total_start_price_jpy"]
        ])
        data.append([
            "終了[TOTAL]", backtest["total_end_price_jpy"],
            trade["total_end_price_jpy"]
        ])
        data.append([
            "利益[TOTAL]", backtest["total_profit_jpy"],
            trade["total_profit_jpy"]
        ])

        print("トレード結果")
        headers = ["", "バックテスト", "トレード"]
        print(
            tabulate(data, tablefmt="grid", numalign="right", headers=headers))

    _report_trade_meta(backtest_data, trade_data)
    print()
    _report_trade_stats(backtest_data, trade_data)
