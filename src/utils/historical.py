import ccxt  # noqa
import time

import datetime
from src.constants.ccxtconst import SYMBOL_BTC_JPY

HISTORICAL_DATA_PATH_BITFLYER = "data/historicals/bitflyer.csv"
# HISTORICAL_DATA_PATH_COINCHECK = "data/historicals/bitflyer.csv"


def save_ticks(exchange_id):
    ex = eval('ccxt.{}()'.format(exchange_id))

    fs = open(HISTORICAL_DATA_PATH_BITFLYER, mode='w')

    fs.write('date,bid,ask\n')

    for _ in range(10):
        ticker = ex.fetch_ticker(SYMBOL_BTC_JPY)

        output = "{},{},{}".format(
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            ticker["bid"], ticker["ask"])
        print(output)
        fs.write(output + '\n')
        fs.flush()
        time.sleep(1)

    fs.close()
