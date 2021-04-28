from logging import getLogger

import src.utils.datetime as dt
import src.constants.path as path
from src.loggers.logger import create_csv_logger

LOGGER_NAME_ORDER = "bot_order"


class OrderLogger():
    def __init__(self):
        self.logger = create_csv_logger(path.BOT_ORDER_CSV_FILE_PATH,
                                        LOGGER_NAME_ORDER,
                                        mode="w")
        self.__logging_header()

    def logging(self, order_type, buy_exchange, buy_rate, buy_price,
                sell_exchange, sell_rate, sell_price, profit, profit_margin):
        logger = getLogger(LOGGER_NAME_ORDER)
        timestamp = dt.now_timestamp()

        message = "{},{},{},{},{},{},{},{}".format(
            timestamp, order_type, buy_exchange.value, buy_rate, buy_price,
            sell_exchange.value, sell_rate, sell_price, profit, profit_margin)

        logger.info(message)

    def __logging_header(self):
        header = 'timestamp,order_type,buy_exchange,buy_rate,buy_price,sell_exchange,sell_rate,sell_price,profit,profit_margin'
        logger = getLogger(LOGGER_NAME_ORDER)
        logger.info(header)
