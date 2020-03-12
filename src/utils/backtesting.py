import os

import src.constants.ccxtconst as ccxtconst
from src.constants.common import HISTORICAL_DATA_DIR_PATH
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting


def _get_file_path(timestamp, exchange_id):
    file_name = "{}.csv".format(exchange_id)
    return os.path.join(HISTORICAL_DATA_DIR_PATH, timestamp, file_name)


def run_backtesting(timestamp):
    print("=== backtest start ===")
    print()

    csv_driver = CsvDriver()

    # load dataset
    df_cc = csv_driver.read_df(
        _get_file_path(timestamp, ccxtconst.EXCHANGE_ID_COINCHECK))
    df_lq = csv_driver.read_df(
        _get_file_path(timestamp, ccxtconst.EXCHANGE_ID_LIQUID))

    # run trade
    arbitrage = ArbitrageBacktesting(df_cc, df_lq, ccxtconst.SYMBOL_BTC_JPY,
                                     ccxtconst.EXCHANGE_ID_COINCHECK,
                                     ccxtconst.EXCHANGE_ID_LIQUID)
    arbitrage.run()

    # show result
    arbitrage.report()

    print()
    print("=== backtest end ===")
