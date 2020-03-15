import os

import src.constants.ccxtconst as ccxtconst
from src.constants.common import BACKTEST_DATA_DIR_PATH
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting


def _get_file_path(timestamp, exchange_id):
    file_name = "{}.csv".format(exchange_id)
    return os.path.join(BACKTEST_DATA_DIR_PATH, timestamp, file_name)


def run_backtesting(timestamp):
    print("=== backtest start ===")
    print()

    # load dataset
    df_cc = read_coincheck_df(timestamp)
    df_lq = read_liquid_df(timestamp)

    # run trade
    arbitrage = ArbitrageBacktesting(df_cc, df_lq, ccxtconst.SYMBOL_BTC_JPY,
                                     ccxtconst.EXCHANGE_ID_COINCHECK,
                                     ccxtconst.EXCHANGE_ID_LIQUID)
    arbitrage.run()

    # show result
    arbitrage.report()

    print()
    print("=== backtest end ===")


def read_coincheck_df(timestamp):
    path = _get_file_path(timestamp, ccxtconst.EXCHANGE_ID_COINCHECK)
    csv_driver = CsvDriver()
    return csv_driver.read_df(path)


def read_liquid_df(timestamp):
    path = _get_file_path(timestamp, ccxtconst.EXCHANGE_ID_LIQUID)
    csv_driver = CsvDriver()
    return csv_driver.read_df(path)
