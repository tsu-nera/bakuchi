from logging import getLogger

import src.utils.datetime as dt
from src.loggers.logger import create_csv_logger
import src.constants.path as path

LOGGER_NAME_EXPECTED_ORDER = "expected_order"
LOGGER_NAME_ACTUAL_ORDER = "actual_order"


def get_expected_order_logger():
    return OrderLogger(LOGGER_NAME_EXPECTED_ORDER,
                       path.EXPECTED_ORDER_CSV_FILE_PATH)


def get_actual_order_logger():
    return OrderLogger(LOGGER_NAME_ACTUAL_ORDER,
                       path.ACTUAL_ORDER_CSV_FILE_PATH)


class OrderLogger():
    def __init__(self, logger_name, log_file_path):
        self.logger_name = logger_name
        self.logger = create_csv_logger(log_file_path, logger_name, mode="w")
        self.__logging_header()

    def logging(self, order_type, buy_exchange, buy_rate, buy_price,
                sell_exchange, sell_rate, sell_price, profit, profit_margin):
        logger = getLogger(self.logger_name)
        timestamp = dt.now_timestamp()

        message = "{},{},{},{},{},{},{},{}".format(
            timestamp, order_type, buy_exchange.value, buy_rate, buy_price,
            sell_exchange.value, sell_rate, sell_price, profit, profit_margin)

        logger.info(message)

    def __logging_header(self):
        header = 'timestamp,order_type,buy_exchange,buy_rate,buy_price,sell_exchange,sell_rate,sell_price,profit,profit_margin'
        logger = getLogger(self.logger_name)
        logger.info(header)
