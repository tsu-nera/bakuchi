import os

from src.constants.common import HISTORICAL_DATA_DIR_PATH
from src.drivers.csv_driver import CsvDriver

TESTDATA_BITFLYER = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                 "2003100027_bitflyer.csv")
TESTDATA_COINCHECK = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                  "2003100027_coincheck.csv")


def run_backtest():
    print("=== backtest start ===")
    csv_driver = CsvDriver()

    # load dataset
    df_bf = csv_driver.read_df(TESTDATA_BITFLYER)
    df_cc = csv_driver.read_df(TESTDATA_COINCHECK)

    # run trade

    # evaluate result

    print("=== backtest end   ===")
