import os
from logging import getLogger

import src.utils.datetime as dt
import src.constants.path as path

from src.constants.exchange import EXCHANGE_ID_LIST

from src.loggers.logger import create_csv_logger

LOGGER_NAME_BOT_ORDER = "bot_order"


def get_bot_order_logger():
    return OrderLogger()


class OrderLogger():
    def __init__(self):
        self.bot_logger = create_csv_logger(path.BOT_ORDER_CSV_FILE_PATH,
                                            LOGGER_NAME_BOT_ORDER,
                                            mode="w")

        self.exchange_loggers = {}

        for exchange_id in EXCHANGE_ID_LIST:
            exchange_name = exchange_id.value
            exchange_logger_name = "{}".format(LOGGER_NAME_BOT_ORDER,
                                               exchange_name)
            csv_name = "{}.csv".format(exchange_logger_name, exchange_name)
            csv_path = os.path.join(path.ORDERS_LOG_DIR, csv_name)

            self.exchange_loggers[exchange_name] = create_csv_logger(
                csv_path, exchange_logger_name, mode="w")

        self.__logging_bot_header()

    def logging(self, order_type, buy_exchange, buy_rate, buy_price,
                sell_exchange, sell_rate, sell_price, profit, profit_margin):

        self.__logging_bot_order(order_type, buy_exchange, buy_rate, buy_price,
                                 sell_exchange, sell_rate, sell_price, profit,
                                 profit_margin)

    def __logging_bot_order(self, order_type, buy_exchange, buy_rate,
                            buy_price, sell_exchange, sell_rate, sell_price,
                            profit, profit_margin):
        bot_logger = getLogger(LOGGER_NAME_BOT_ORDER)
        timestamp = dt.now_timestamp()

        message = "{},{},{},{},{},{},{},{}".format(
            timestamp, order_type, buy_exchange.value, buy_rate, buy_price,
            sell_exchange.value, sell_rate, sell_price, profit, profit_margin)

        bot_logger.info(message)

    def __logging_bot_header(self):
        header = 'timestamp,order_type,buy_exchange,buy_rate,buy_price,sell_exchange,sell_rate,sell_price,profit,profit_margin'
        logger = getLogger(LOGGER_NAME_BOT_ORDER)
        logger.info(header)

    def __logging_exchange_order(self):
        pass

    def __logging_exchange_header(self):
        header = 'timestamp,pair,side,fee,amount,price,rate,id,order_id'
        logger = getLogger(LOGGER_NAME_BOT_ORDER)
        logger.info(header)
