import datetime


def format_timestamp(timestamp):
    format_string = "%Y-%m-%d %H:%M:%S"
    return datetime.datetime.strftime(timestamp, format_string)
