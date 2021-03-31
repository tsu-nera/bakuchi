import ccxt  # noqa
import time
import os

import src.utils.datetime as dt
from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst
from src.constants.path import HISTORICAL_DATA_DIR_PATH


def _get_dir_path():
    return os.path.join(HISTORICAL_DATA_DIR_PATH, dt.now_dirname())


def _get_file_path(dir_path, exchange_id):
    file_name = "{}.csv".format(exchange_id.value)
    return os.path.join(dir_path, file_name)


def _format_csv(timestamp, bid, ask):
    return "{},{},{}".format(timestamp, bid, ask)


def save_ticks():
    dir_path = _get_dir_path()
    os.mkdir(dir_path)

    bf_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.BITFLYER)
    ex1_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.COINCHECK)
    ex2_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.LIQUID)
    bb_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.BITBANK)

    fs_bf = open(bf_file_path, mode='w')
    fs_ex1 = open(ex1_file_path, mode='w')
    fs_ex2 = open(ex2_file_path, mode='w')
    fs_bb = open(bb_file_path, mode='w')

    header_string = 'timestamp,bid,ask\n'
    fs_bf.write(header_string)
    fs_ex1.write(header_string)
    fs_ex2.write(header_string)
    fs_bb.write(header_string)

    client_bf = CcxtClient(ccxtconst.ExchangeId.BITFLYER)
    client_ex1 = CcxtClient(ccxtconst.ExchangeId.COINCHECK)
    client_ex2 = CcxtClient(ccxtconst.ExchangeId.LIQUID)
    client_bb = CcxtClient(ccxtconst.ExchangeId.BITBANK)

    try:
        for _ in range(1000000):
            tick_bf = client_bf.fetch_tick()
            tick_ex1 = client_ex1.fetch_tick()
            tick_ex2 = client_ex2.fetch_tick()
            tick_bb = client_bb.fetch_tick()

            if tick_bf and tick_ex1 and tick_ex2 and tick_bb:
                output_bf = _format_csv(tick_bf.timestamp, tick_bf.bid,
                                        tick_bf.ask)
                output_ex1 = _format_csv(tick_ex1.timestamp, tick_ex1.bid,
                                         tick_ex1.ask)
                output_ex2 = _format_csv(tick_ex2.timestamp, tick_ex2.bid,
                                         tick_ex2.ask)
                output_bb = _format_csv(tick_bb.timestamp, tick_bb.bid,
                                        tick_bb.ask)

                fs_bf.write(output_bf + '\n')
                fs_bf.flush()
                fs_ex1.write(output_ex1 + '\n')
                fs_ex1.flush()
                fs_ex2.write(output_ex2 + '\n')
                fs_ex2.flush()
                fs_bb.write(output_bb + '\n')
                fs_bb.flush()

                time.sleep(ccxtconst.TICK_INTERVAL_SEC)
            else:
                time.sleep(10)
    finally:
        fs_bf.close()
        fs_ex1.close()
        fs_ex2.close()
        fs_bb.close()
