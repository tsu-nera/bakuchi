import os
import shutil
import json
from logging import getLogger

from src.libs.logger import create_csv_logger
import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
import src.config as config
# from src.libs.asset import Asset
import src.utils.datetime as dt


class HistoricalLogger():
    def __init__(self):
        self.exchange_ids = ccxtconst.EXCHANGE_ID_LIST
        self.dir_path = self._get_dir_path()
        self.info_file_path = self._get_info_file_path(self.dir_path)

        # create directory
        if os.path.exists(self.dir_path):
            shutil.rmtree(self.dir_path)
        os.mkdir(self.dir_path)

        info_dict = {
            "amount": config.TRADE_AMOUNT,
            "open_threshold": config.TRADE_OPEN_THRESHOLD,
            "profit_margin_diff": config.TRADE_PROFIT_MARGIN_DIFF,
            "open_threshold_change_sec": config.OPEN_THRESHOLD_CHANGE_SEC
        }

        json_file = open(self.info_file_path, 'w')
        json.dump(info_dict, json_file, indent=2)

        # initialze loggers
        [self._create_logger(exchange_id) for exchange_id in self.exchange_ids]

        # add header
        [
            self._logging_header(exchange_id)
            for exchange_id in self.exchange_ids
        ]

    def logging(self, exchange_id, timestamp, bid, ask):
        logger = self._get_logger(exchange_id)
        message = "{},{},{}".format(timestamp, bid, ask)
        logger.info(message)

    def _logging_header(self, exchange_id):
        header = 'timestamp,bid,ask'
        logger = self._get_logger(exchange_id)
        logger.info(header)

    def _get_dir_path(self):
        now_dirname = dt.now_dirname()
        return os.path.join(path.HISTORICAL_RAWDATA_DIR_PATH, now_dirname)

    def _get_file_path(self, dir_path, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(dir_path, file_name)

    def _get_info_file_path(self, dir_path):
        file_name = "info.json"
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
