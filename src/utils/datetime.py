import datetime

DATETIME_BASE_FORMAT = '%Y-%m-%d %H:%M:%S'


def format_timestamp(timestamp):
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def get_dt_dir_name(timestamp):
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def now_string():
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.now().strftime(format_string)
