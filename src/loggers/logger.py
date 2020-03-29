import logging

import src.constants.path as path

LOGGER_NAME_TRADING = "trading"
LOGGER_NAME_TRADING_WITH_STDOUT = "trading2"
LOGGER_NAME_CCXT = "ccxt"
LOGGER_NAME_MARGIN = "margin"
LOGGER_NAME_ASSET = "asset"
LOGGER_NAME_ASSET_CRON = "asset_cron"

formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s')
csv_formatter = logging.Formatter('%(message)s')


def create_file_logger(file_path, logger_name):
    logfile = logging.FileHandler(file_path, "a")
    logfile.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(logfile)


def create_csv_logger(file_path, logger_name):
    logfile = logging.FileHandler(file_path, "a")
    logfile.setFormatter(csv_formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(logfile)


trading_logfile = logging.FileHandler(path.TRADING_LOG_FILE_PATH, "a")
trading_logfile.setFormatter(formatter)
trading_logger = logging.getLogger(LOGGER_NAME_TRADING)
trading_logger.addHandler(trading_logfile)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

trading_logger_with_stdout = logging.getLogger(LOGGER_NAME_TRADING_WITH_STDOUT)
trading_logger_with_stdout.addHandler(trading_logfile)
trading_logger_with_stdout.addHandler(stream_handler)

create_file_logger(path.CCXT_LOG_FILE_PATH, LOGGER_NAME_CCXT)
create_file_logger(path.MARGIN_LOG_FILE_PATH, LOGGER_NAME_MARGIN)
create_file_logger(path.ASSET_LOG_FILE_PATH, LOGGER_NAME_ASSET)
create_file_logger(path.CRON_ASSET_LOG_FILE_PATH, LOGGER_NAME_ASSET_CRON)


def get_trading_logger():
    return logging.getLogger(LOGGER_NAME_TRADING)


def get_trading_logger_with_stdout():
    return logging.getLogger(LOGGER_NAME_TRADING_WITH_STDOUT)


def get_ccxt_logger():
    return logging.getLogger(LOGGER_NAME_CCXT)


def get_margin_logger():
    return logging.getLogger(LOGGER_NAME_MARGIN)


def get_asset_logger():
    return logging.getLogger(LOGGER_NAME_ASSET)


def get_asset_append_logger():
    return logging.getLogger(LOGGER_NAME_ASSET_CRON)
