import os

import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
from src.drivers.csv_driver import CsvDriver
from src.core.arbitrage_backtesting import ArbitrageBacktesting

import src.utils.json as json


class Backtesting():
    def __init__(self, timestamp, simulate_mode=False, report=False):
        self.timestamp = timestamp
        self.csv_driver = CsvDriver()

        self.df_ex1 = self._read_df(exchange.ExchangeId.BITBANK)
        self.df_ex2 = self._read_df(exchange.ExchangeId.LIQUID)

        self.arbitrage = ArbitrageBacktesting(self.df_ex1, self.df_ex2,
                                              ccxtconst.SYMBOL_BTC_JPY,
                                              exchange.ExchangeId.BITBANK,
                                              exchange.ExchangeId.LIQUID,
                                              timestamp, simulate_mode)

    def _get_file_path(self, exchange_id):
        file_name = "{}.csv".format(exchange_id.value)
        return os.path.join(path.REPORTS_DATA_DIR_PATH, self.timestamp,
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
        return self.df_ex1

    def get_liquid_df(self):
        return self.df_ex2

    def get_result_data(self, report_mode=False):
        if report_mode:
            config_file_path = os.path.join(path.REPORTS_DATA_DIR_PATH,
                                            self.timestamp,
                                            path.CONFIG_JSON_FILE)
            config = json.read(config_file_path)
            self.arbitrage.run(amount=int(config["amount"]),
                               open_threshold=int(config["open_threshold"]),
                               profit_margin_diff=int(
                                   config["profit_margin_diff"]),
                               open_threshold_change_sec=int(
                                   config["open_threshold_change_sec"]))

        else:
            self.arbitrage.run()
        return self.arbitrage.get_result_data()


def run_backtesting(timestamp, simulate_mode=False):
    print("=== backtest start ===")
    print()

    backtest = Backtesting(timestamp, simulate_mode)
    backtest.run()
    backtest.display()

    print()
    print("=== backtest end ===")
