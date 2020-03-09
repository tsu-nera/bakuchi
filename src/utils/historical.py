import ccxt  # noqa
import time
import os

import datetime
import src.constants.ccxtconst as ccxtconst

HISTORICAL_DATA_DIR_PATH = os.path.join("data", "historicals")
HISTORICAL_DATA_PATH_BITFLYER = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                             "bitflyer.csv")
HISTORICAL_DATA_PATH_COINCHECK = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                              "coincheck.csv")


def save_ticks():

    ex_bf = eval('ccxt.{}()'.format(ccxtconst.EXCHANGE_ID_BITFLYER))
    ex_cc = eval('ccxt.{}()'.format(ccxtconst.EXCHANGE_ID_COINCHECK))

    fs_bf = open(HISTORICAL_DATA_PATH_BITFLYER, mode='w')
    fs_cc = open(HISTORICAL_DATA_PATH_COINCHECK, mode='w')

    header_string = 'date,bid,ask\n'
    fs_bf.write(header_string)
    fs_cc.write(header_string)

    for _ in range(1000000):
        date_string = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            ticker_bf = ex_bf.fetch_ticker(ccxtconst.SYMBOL_BTC_JPY)
            ticker_cc = ex_cc.fetch_ticker(ccxtconst.SYMBOL_BTC_JPY)

            output_bf = "{},{},{}".format(date_string, ticker_bf["bid"],
                                          ticker_bf["ask"])
            output_cc = "{},{},{}".format(date_string, ticker_cc["bid"],
                                          ticker_cc["ask"])

            fs_bf.write(output_bf + '\n')
            fs_bf.flush()

            fs_cc.write(output_cc + '\n')
            fs_cc.flush()

            time.sleep(1)
        except ccxt.RequestTimeout as e:
            print("{} timeout error occured".format(date_string), e)
            time.sleep(10)

    fs_bf.close()
    fs_cc.close()
