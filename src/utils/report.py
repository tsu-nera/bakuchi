import os
import glob
import shutil
from distutils.dir_util import copy_tree
import pandas as pd
import datetime

from tabulate import tabulate
from jinja2 import Environment, FileSystemLoader

import src.constants.path as path
import src.constants.exchange as exchange

from src.utils.backtesting import Backtesting
from src.utils.trade_analysis import TradeAnalysis

from src.utils.trade_history import save_report_trades
import src.utils.json as json
import src.utils.datetime as dt


def get_latest_dirpath(dir_path):
    return max(glob.glob(os.path.join(dir_path, '*/')), key=os.path.getmtime)


def generate(timestamp):
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = os.path.join(production_dir, timestamp)
    to_dir = os.path.join(path.REPORTS_DATA_DIR_PATH, timestamp)

    # ログをバックアップ
    copy_tree(from_dir, to_dir)

    # trade履歴をサイトから取得
    _fetch_trades(timestamp)

    # jupyter notebookの実行
    generate_notebook(timestamp)

    # 結果の出力
    display(timestamp)

    # 結果のエクスポート
    export_trade_result(timestamp)


def generate_latest():
    production_dir = path.PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH
    from_dir = get_latest_dirpath(production_dir)
    timestamp = from_dir.split('/')[-2]

    generate(timestamp)


def run_notebook(file_path):
    command_base = "jupyter nbconvert --to notebook --ExecutePreprocessor.timeout=-1 --execute --inplace --ExecutePreprocessor.kernel_name=python"
    command = " ".join([command_base, file_path])

    os.system(command)


def convert_nb_html(file_path):
    command_base = "jupyter nbconvert --to html"
    command = " ".join([command_base, file_path])

    os.system(command)


def generate_notebook(dir_name):
    from_dir = path.NOTEBOOK_TEMPLATES_DIR
    to_dir = os.path.join(path.REPORTS_DATA_DIR_PATH, dir_name)

    reports = [path.REPORT_BACKTEST, path.REPORT_TRADE]

    for report_name in reports:
        from_path = os.path.join(from_dir, report_name)
        to_path = os.path.join(to_dir, report_name)

        shutil.copy(from_path, to_path)

        run_notebook(to_path)
        convert_nb_html(to_path)


def _get_trade_timestamps(timestamp):
    dir_path = os.path.join(path.REPORTS_DATA_DIR_PATH, timestamp)

    def __read_asset(keyword):
        file_name = "{}.json".format(keyword)
        file_path = os.path.join(dir_path, path.ASSETS_DIR, file_name)
        return json.read(file_path)

    start_asset = __read_asset("start")
    end_asset = __read_asset("end")

    start_datetime = dt.parse_timestamp(start_asset["timestamp"])
    end_datetime = dt.parse_timestamp(end_asset["timestamp"])

    return start_datetime, end_datetime


def _fetch_trades(dir_name):
    start_timestamp, end_timestamp = _get_trade_timestamps(dir_name)
    save_report_trades(dir_name, start_timestamp, end_timestamp)


def display(timestamp):
    backtesting = Backtesting(timestamp)
    trade_analysis = TradeAnalysis(timestamp)

    backtest_data = backtesting.get_result_data(report_mode=True)
    trade_data = trade_analysis.get_result_data()

    def __report_trade_meta(backtest, trade):
        data = []
        data.append(["レコード数", backtest["record_count"], trade["record_count"]])
        data.append(["取引回数", backtest["trade_count"], trade["trade_count"]])
        data.append(
            ["開始日時", backtest["start_timestamp"], trade["start_timestamp"]])
        data.append(
            ["終了日時", backtest["end_timestamp"], trade["end_timestamp"]])
        data.append(["取引時間[H]", backtest["duration"], trade["duration"]])
        data.append(
            ["取引単位[BTC]", backtest["trade_amount"], trade["trade_amount"]])
        data.append([
            "利確しきい値[JPY]", backtest["open_threshold"], trade["open_threshold"]
        ])
        data.append([
            "損切りマージン[JPY]", backtest["profit_margin_diff"],
            trade["profit_margin_diff"]
        ])

        heading = "トレード情報"

        headers = ["", "バックテスト", "トレード"]
        body = tabulate(data,
                        numalign="right",
                        stralign="right",
                        headers=headers)

        return "\n".join([heading, body])

    def __report_trade_stats(backtest, trade):
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

        heading = "トレード結果"

        headers = ["", "バックテスト", "トレード"]
        body = tabulate(data, numalign="right", headers=headers)

        return "\n".join([heading, body])

    def __report_trade_profits(trade):

        profits = []
        profits.append(["Bot利益", "トレード利益", "市場利益"])

        profits.append([
            trade["bot_profit_jpy"], trade["trade_profit_jpy"],
            trade["market_profit_jpy"]
        ])

        heading = "トレード利益"
        body = tabulate(profits, numalign="right", headers="firstrow")

        return "\n".join([heading, body])

    def __generate_readme(date, result, timestamp):
        env = Environment(
            loader=FileSystemLoader(path.REPORTS_DATA_DIR_PATH, encoding='utf8'))
        template = env.get_template(path.README_TEMPLATE_FILE)
        readme = template.render(date=date, result=result)

        output_path = "/".join([path.REPORTS_DATA_DIR_PATH, timestamp, path.README_FILE])

        with open(output_path, mode='w') as f:
            f.write(str(readme))

    output_meta = __report_trade_meta(backtest_data, trade_data)
    output_stats = __report_trade_stats(backtest_data, trade_data)
    output_profits = __report_trade_profits(trade_data)

    header = datetime.datetime.strptime(
        timestamp, dt.DATETIME_DIR_FORMAT).strftime(dt.README_HEADER_FORMAT)

    body = "\n".join([output_meta, "\n", output_stats, "\n", output_profits])

    __generate_readme(header, body, timestamp)


def export_trade_result(timestamp):
    trade_analysis = TradeAnalysis(timestamp)
    trade_data = trade_analysis.get_result_data()

    trade_data["start_timestamp"] = dt.format_timestamp(
        trade_data["start_timestamp"])
    trade_data["end_timestamp"] = dt.format_timestamp(
        trade_data["end_timestamp"])
    trade_data["duration"] = int(trade_data["duration"].total_seconds())

    file_path = os.path.join(path.REPORTS_DATA_DIR_PATH, timestamp,
                             path.RESULT_JSON_FILE)

    json.write(file_path, trade_data)
