import datetime

DATETIME_BASE_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_DIR_FORMAT = '%y%m%d%H%M'
DATE_DIR_FORMAT = '%y%m%d'


def format_timestamp(timestamp):
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def get_dt_dirname(timestamp):
    format_string = DATETIME_DIR_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def now_dirname():
    format_string = DATETIME_DIR_FORMAT
    return datetime.datetime.now().strftime(format_string)


def today_dirname():
    format_string = DATE_DIR_FORMAT
    return datetime.datetime.now().strftime(format_string)


def now_timestamp():
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.now().strftime(format_string)
