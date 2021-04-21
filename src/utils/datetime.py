import datetime

DATETIME_BASE_FORMAT = '%Y-%m-%d %H:%M:%S'
DATETIME_DIR_FORMAT = '%y%m%d_%H%M'
DATE_DIR_FORMAT = '%y%m%d'
DATETIME_MS_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
README_HEADER_FORMAT = '%Y/%m/%d'


def format_timestamp(timestamp):
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def parse_timestamp(timestamp):
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.strptime(timestamp, format_string)


def get_dt_dirname(timestamp):
    format_string = DATETIME_DIR_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)


def now_dirname():
    format_string = DATETIME_DIR_FORMAT
    return datetime.datetime.now().strftime(format_string)


def today_dirname():
    format_string = DATE_DIR_FORMAT
    return datetime.datetime.now().strftime(format_string)


def now():
    return datetime.datetime.now()


def now_timestamp():
    format_string = DATETIME_BASE_FORMAT
    return datetime.datetime.now().strftime(format_string)


def utcnow():
    return datetime.datetime.utcnow()


def now_timestamp_ms():
    format_string = DATETIME_MS_FORMAT
    return datetime.datetime.now().strftime(format_string)[:-3]


def to_millsecond(timestamp):
    return int(timestamp.timestamp() * 1000)


def from_millsecond(datetime_ms):
    return datetime.datetime.fromtimestamp(int(datetime_ms / 1000))


def convert_coincheck_datetime(d_str):
    timestamp = datetime.datetime.fromisoformat(d_str.replace('Z', ''))
    timestamp = timestamp + datetime.timedelta(hours=9)
    return timestamp


def to_timestamp(timestamp):
    datetime_millsecond = datetime.datetime.fromtimestamp(
        to_millsecond(timestamp))
    return format_timestamp(datetime_millsecond)
