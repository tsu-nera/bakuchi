import os
import glob

import pandas as pd

import src.utils.json as json
import src.constants.path as path

from src.utils.backtesting import Backtesting


def read_results():
    dir_path = path.REPORTS_DIR
    dir_path_list = glob.glob(os.path.join(dir_path, '*/'))

    results = []
    for dir_path in dir_path_list:
        file_path = os.path.join(dir_path, path.RESULT_JSON_FILE)
        result = json.read(file_path)
        results.append(result)

    df = pd.DataFrame(results)
    df = df.set_index("start_timestamp")
    df.index.name = "timestamp"

    return df


def get_profit_diff_df(timestamp):
    df = []

    return df
