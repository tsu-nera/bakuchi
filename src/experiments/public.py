import ccxt  # noqa
import time

# from pprint import pprint
from src.constants.ccxtlib import SYMBOL_BTC_JPY


def fetch_ticks(exchange_id):
    ex = eval('ccxt.{}()'.format(exchange_id))

    for _ in range(10):
        ticker = ex.fetch_ticker(SYMBOL_BTC_JPY)
        # pprint(ticker)
        output = "bid:{} ask:{}".format(ticker["bid"], ticker["ask"])
        print(output)
        time.sleep(1)
