import logging
import src.constants.common as common

LOGGER_NAME_ASSET = "asset"

formatter = logging.Formatter('[%(levelname)s:%(asctime)s] %(message)s')
historical_formatter = logging.Formatter('%(message)s')


def create_file_logger(file_path, logger_name):
    logfile = logging.FileHandler(file_path, "a")
    logfile.setFormatter(formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(logfile)


def create_historical_logger(file_path, logger_name):
    logfile = logging.FileHandler(file_path, "a")
    logfile.setFormatter(historical_formatter)
    logger = logging.getLogger(logger_name)
    logger.addHandler(logfile)


create_file_logger(common.ASSET_LOG_FILE_PATH, LOGGER_NAME_ASSET)


def get_asset_logger():
    return logging.getLogger(LOGGER_NAME_ASSET)
