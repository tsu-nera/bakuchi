import os

from src.constants.common import HISTORICAL_DATA_DIR_PATH
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting

TESTDATA_COINCHECK = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                  "2003100027_coincheck.csv")
TESTDATA_LIQUID = os.path.join(HISTORICAL_DATA_DIR_PATH,
                               "2003100027_liquid.csv")


def run_backtesting():
    print("=== backtest start ===")
    csv_driver = CsvDriver()

    # load dataset
    df_cc = csv_driver.read_df(TESTDATA_COINCHECK)
    df_lq = csv_driver.read_df(TESTDATA_LIQUID)

    # run trade
    arbitrage = ArbitrageBacktesting(df_cc, df_lq)
    arbitrage.run()

    # show result
    arbitrage.report()

    print("=== backtest end   ===")
