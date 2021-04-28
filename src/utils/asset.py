import os
import pandas as pd

import src.utils.json as json
import src.constants.path as path


def read_asset(exchange_id_str):
    file_name = "{}.csv".format(exchange_id_str)
    file_path = os.path.join(path.ASSET_DATA_DIR_PATH, file_name)
    return pd.read_csv(file_path, index_col=0, parse_dates=[0])


def read_asset_total():
    return read_asset("total")


def __asset_file_path(timestamp, filename):
    return os.path.join(path.REPORTS_DATA_DIR_PATH, timestamp, path.ASSETS_DIR,
                        filename)


def read_trading_start_asset(timestamp):
    file_path = __asset_file_path(timestamp, path.TRADING_START_ASSET_FILE)
    return json.read(file_path)


def read_trading_end_asset(timestamp):
    file_path = __asset_file_path(timestamp, path.TRADING_END_ASSET_FILE)
    return json.read(file_path)


# rateはこれ
def format_jpy(jpy):
    return int(jpy)


# rate以外は基本これ
def format_jpy_float(jpy):
    return round(jpy, 3)


def format_btc(btc):
    return round(btc, 3)


def format_btc_more(btc):
    return round(btc, 6)


def btc_to_jpy(btc_amount, bid):
    return btc_amount * bid
