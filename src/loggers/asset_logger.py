import os
from logging import getLogger

import src.utils.datetime as dt
from src.loggers.logger import create_csv_logger
import src.constants.ccxtconst as ccxtconst
import src.constants.path as path


class AssetLogger():
    def __init__(self):
        self.exchange_ids = ["total"]
        [
            self.exchange_ids.append(exchange_id.value)
            for exchange_id in ccxtconst.EXCHANGE_ID_LIST
        ]

        self.dir_path = path.ASSET_DATA_DIR_PATH

        # initialze loggers
        [self._create_logger(exchange_id) for exchange_id in self.exchange_ids]

    def logging(self, exchange_id, jpy, btc, btc_as_jpy, total_jpy):
        logger = self._get_logger(exchange_id)
        timestamp = dt.now_timestamp()
        message = "{},{},{},{},{}".format(timestamp, jpy, btc, btc_as_jpy,
                                          total_jpy)
        logger.info(message)

    def _logging_header(self, exchange_id):
        header = 'timestamp,jpy,btc,btc_as_jpy,total_jpy'
        logger = self._get_logger(exchange_id)
        logger.info(header)

    def _get_file_path(self, dir_path, exchange_id):
        file_name = "{}.csv".format(exchange_id)
        return os.path.join(dir_path, file_name)

    def _get_logger_name(self, exchange_id):
        return "{}.asset".format(exchange_id)

    def _create_logger(self, exchange_id):
        file_path = self._get_file_path(self.dir_path, exchange_id)
        logger_name = self._get_logger_name(exchange_id)
        is_file_exist = os.path.exists(file_path)
        create_csv_logger(file_path, logger_name)

        if not is_file_exist:
            self._logging_header(exchange_id)

    def _get_logger(self, exchange_id):
        logger_name = self._get_logger_name(exchange_id)
        return getLogger(logger_name)
