import os

import src.constants.ccxtconst as ccxtconst
from src.constants.common import BACKTEST_DATA_DIR_PATH
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting


class Backtesting():
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.csv_driver = CsvDriver()

        self.df_cc = self._read_df(ccxtconst.EXCHANGE_ID_COINCHECK)
        self.df_lq = self._read_df(ccxtconst.EXCHANGE_ID_LIQUID)

    def _get_file_path(self, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(BACKTEST_DATA_DIR_PATH, self.timestamp, file_name)

    def _read_df(self, exchange_id):
        path = self._get_file_path(exchange_id)
        return self.csv_driver.read_df(path)

    def run(self):
        print("=== backtest start ===")
        print()

        # run trade
        arbitrage = ArbitrageBacktesting(self.df_cc, self.df_lq,
                                         ccxtconst.SYMBOL_BTC_JPY,
                                         ccxtconst.EXCHANGE_ID_COINCHECK,
                                         ccxtconst.EXCHANGE_ID_LIQUID)
        arbitrage.run()

        # show result
        arbitrage.report()

        print()
        print("=== backtest end ===")

    def get_coincheck_df(self):
        return self.df_cc

    def get_liquid_df(self):
        return self.df_lq


def run_backtesting(timestamp):
    backtest = Backtesting(timestamp)
    backtest.run()
