import os
import pandas as pd

import src.constants.path as path


def read_asset(exchange_id_str):
    file_name = "{}.csv".format(exchange_id_str)
    file_path = os.path.join(path.ASSET_DATA_DIR_PATH, file_name)
    return pd.read_csv(file_path, index_col=0, parse_dates=[0])


def read_asset_total():
    return read_asset("total")


def format_jpy(jpy):
    return int(jpy)


def format_jpy_float(jpy):
    return round(jpy, 3)


def format_btc(btc):
    return round(btc, 3)


def format_btc_more(btc):
    return round(btc, 6)


def btc_to_jpy(btc_amount, bid):
    return btc_amount * bid
