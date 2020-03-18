import os
import pandas as pd

import src.constants.path as path


def read_asset(exchange_id):
    file_name = "{}.csv".format(exchange_id)
    file_path = os.path.join(path.ASSET_DATA_DIR_PATH, file_name)
    return pd.read_csv(file_path, index_col=0, parse_dates=[0])


def read_asset_total():
    return read_asset("total")
