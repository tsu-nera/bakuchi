import os

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting


class Backtesting():
    def __init__(self, timestamp, simulate_mode=False):
        self.timestamp = timestamp
        self.csv_driver = CsvDriver()

        self.df_cc = self._read_df(ccxtconst.EXCHANGE_ID_COINCHECK)
        self.df_lq = self._read_df(ccxtconst.EXCHANGE_ID_LIQUID)

        self.arbitrage = ArbitrageBacktesting(self.df_cc, self.df_lq,
                                              ccxtconst.SYMBOL_BTC_JPY,
                                              ccxtconst.EXCHANGE_ID_COINCHECK,
                                              ccxtconst.EXCHANGE_ID_LIQUID,
                                              simulate_mode)

    def _get_file_path(self, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(path.REPORTS_DIR, self.timestamp,
                            path.EXCHANGES_DIR, file_name)

    def _read_df(self, exchange_id):
        path = self._get_file_path(exchange_id)
        return self.csv_driver.read_df(path)

    def run(self,
            amount=None,
            profit_margin_threshold=None,
            profit_margin_diff=None):
        # run trade
        self.arbitrage.run(amount, profit_margin_threshold, profit_margin_diff)

    def get_trade_histories(self):
        return self.arbitrage.histories

    def get_arbitrage_histories(self):
        return self.arbitrage.arbitrage_histories

    def display(self):
        # show result
        self.arbitrage.report()

    def get_coincheck_df(self):
        return self.df_cc

    def get_liquid_df(self):
        return self.df_lq

    def get_result_data(self):
        return self.arbitrage.get_result_data()


def run_backtesting(timestamp, simulate_mode=False):
    print("=== backtest start ===")
    print()

    backtest = Backtesting(timestamp, simulate_mode)
    backtest.run()
    backtest.display()

    print()
    print("=== backtest end ===")
