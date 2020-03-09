import ccxt  # noqa
import time
import os

from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst

HISTORICAL_DATA_DIR_PATH = os.path.join("data", "historicals")
HISTORICAL_DATA_PATH_BITFLYER = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                             "bitflyer.csv")
HISTORICAL_DATA_PATH_COINCHECK = os.path.join(HISTORICAL_DATA_DIR_PATH,
                                              "coincheck.csv")

PER_TICK_SEC = 1


def _format_csv(date, bid, ask):
    return "{},{},{}".format(date, bid, ask)


def save_ticks():
    fs_bf = open(HISTORICAL_DATA_PATH_BITFLYER, mode='w')
    fs_cc = open(HISTORICAL_DATA_PATH_COINCHECK, mode='w')

    header_string = 'date,bid,ask\n'
    fs_bf.write(header_string)
    fs_cc.write(header_string)

    client_bf = CcxtClient(ccxtconst.EXCHANGE_ID_BITFLYER)
    client_cc = CcxtClient(ccxtconst.EXCHANGE_ID_COINCHECK)

    for _ in range(1000000):
        tick_bf = client_bf.fetch_tick()
        tick_cc = client_cc.fetch_tick()

        if tick_bf and tick_cc:
            output_bf = _format_csv(tick_bf["date"], tick_bf["bid"],
                                    tick_bf["ask"])
            output_cc = _format_csv(tick_cc["date"], tick_cc["bid"],
                                    tick_cc["ask"])

            fs_bf.write(output_bf + '\n')
            fs_bf.flush()

            fs_cc.write(output_cc + '\n')
            fs_cc.flush()

            time.sleep(PER_TICK_SEC)
        else:
            time.sleep(10)

    fs_bf.close()
    fs_cc.close()
