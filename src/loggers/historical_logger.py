import os
import shutil
from logging import getLogger

from src.loggers.logger import create_csv_logger
import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
import src.config as config
import src.utils.datetime as dt
import src.utils.json as json


class HistoricalLogger():
    def __init__(self):
        self.exchange_ids = ccxtconst.ExchangeId.LIST
        self.dir_path = self._get_dir_path()
        self.config_file_path = self._get_config_file_path(self.dir_path)

        # create directory
        if os.path.exists(self.dir_path):
            shutil.rmtree(self.dir_path)

        os.mkdir(self.dir_path)
        os.mkdir(os.path.join(self.dir_path, path.EXCHANGES_DIR))

        self._dump_config()

        # initialze loggers
        [self._create_logger(exchange_id) for exchange_id in self.exchange_ids]

        # add header
        [
            self._logging_header(exchange_id)
            for exchange_id in self.exchange_ids
        ]

    def _dump_config(self):
        config_dict = {
            "amount":
            config.TRADE_AMOUNT,
            "open_threshold":
            config.TRADE_OPEN_THRESHOLD,
            "profit_margin_diff":
            config.TRADE_PROFIT_MARGIN_DIFF,
            "open_threshold_change_sec":
            config.OPEN_THRESHOLD_CHANGE_SEC,
            "coincheck_order_buy_adjust_amount_btc":
            config.COINCHECK_ORDER_BUY_ADJUST_AMOUNT_BTC
        }

        json.write(self.config_file_path, config_dict)

    def logging(self, exchange_id, timestamp, bid, ask, tick_timestamp):
        logger = self._get_logger(exchange_id)
        message = "{},{},{},{}".format(timestamp, bid, ask, tick_timestamp)
        logger.info(message)

    def _logging_header(self, exchange_id):
        header = 'timestamp,bid,ask,tick_timestamp'
        logger = self._get_logger(exchange_id)
        logger.info(header)

    def _get_dir_path(self):
        return os.path.join(path.HISTORICAL_RAWDATA_DIR_PATH, dt.now_dirname())

    def _get_file_path(self, dir_path, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(dir_path, path.EXCHANGES_DIR, file_name)

    def _get_config_file_path(self, dir_path):
        file_name = path.CONFIG_JSON_FILE
        return os.path.join(dir_path, file_name)

    def _get_logger_name(self, exchange_id):
        return "{}.historical".format(exchange_id)

    def _create_logger(self, exchange_id):
        file_path = self._get_file_path(self.dir_path, exchange_id)
        logger_name = self._get_logger_name(exchange_id)
        create_csv_logger(file_path, logger_name)

    def _get_logger(self, exchange_id):
        logger_name = self._get_logger_name(exchange_id)
        return getLogger(logger_name)
