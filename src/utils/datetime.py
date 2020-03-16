import datetime
import src.constants.common as common


def format_timestamp(timestamp):
    format_string = common.DATETIME_BASE_FORMAT
    return datetime.datetime.strftime(timestamp, format_string)
