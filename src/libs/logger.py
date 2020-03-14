import logging

import src.constants.common as common

LOGGER_NAME_TRADING = "trading"
LOGGER_NAME_TRADING_WITH_STDOUT = "trading2"
LOGGER_NAME_CCXT = "ccxt"
LOGGER_NAME_MARGIN = "margin"

formatter = logging.Formatter('[%(levelname)s]%(asctime)s %(message)s')

trading_logfile = logging.FileHandler(common.TRADING_LOG_FILE_PATH, "w")
trading_logfile.setFormatter(formatter)
trading_logger = logging.getLogger(LOGGER_NAME_TRADING)
trading_logger.addHandler(trading_logfile)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

trading_logger_with_stdout = logging.getLogger(LOGGER_NAME_TRADING_WITH_STDOUT)
trading_logger_with_stdout.addHandler(trading_logfile)
trading_logger_with_stdout.addHandler(stream_handler)

ccxt_logfile = logging.FileHandler(common.CCXT_LOG_FILE_PATH, "w")
ccxt_logfile.setFormatter(formatter)
ccxt_logger = logging.getLogger(LOGGER_NAME_CCXT)
ccxt_logger.addHandler(ccxt_logfile)

margin_logfile = logging.FileHandler(common.MARGIN_LOG_FILE_PATH, "w")
margin_logfile.setFormatter(formatter)
margin_logger = logging.getLogger(LOGGER_NAME_MARGIN)
margin_logger.addHandler(margin_logfile)


def get_trading_logger():
    return logging.getLogger(LOGGER_NAME_TRADING)


def get_trading_logger_with_stdout():
    return logging.getLogger(LOGGER_NAME_TRADING_WITH_STDOUT)


def get_ccxt_logger():
    return logging.getLogger(LOGGER_NAME_CCXT)


def get_margin_logger():
    return logging.getLogger(LOGGER_NAME_MARGIN)
