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
    file_name = "{}.csv".format(exchange_id)
    return os.path.join(dir_path, file_name)


def _format_csv(timestamp, bid, ask):
    return "{},{},{}".format(timestamp, bid, ask)


def save_ticks():
    dir_path = _get_dir_path()
    os.mkdir(dir_path)

    bf_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.BITFLYER)
    cc_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.COINCHECK)
    lq_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.LIQUID)
    bb_file_path = _get_file_path(dir_path, ccxtconst.ExchangeId.BITBANK)

    fs_bf = open(bf_file_path, mode='w')
    fs_cc = open(cc_file_path, mode='w')
    fs_lq = open(lq_file_path, mode='w')
    fs_bb = open(bb_file_path, mode='w')

    header_string = 'timestamp,bid,ask\n'
    fs_bf.write(header_string)
    fs_cc.write(header_string)
    fs_lq.write(header_string)
    fs_bb.write(header_string)

    client_bf = CcxtClient(ccxtconst.ExchangeId.BITFLYER)
    client_cc = CcxtClient(ccxtconst.ExchangeId.COINCHECK)
    client_lq = CcxtClient(ccxtconst.ExchangeId.LIQUID)
    client_bb = CcxtClient(ccxtconst.ExchangeId.BITBANK)

    try:
        for _ in range(1000000):
            tick_bf = client_bf.fetch_tick()
            tick_cc = client_cc.fetch_tick()
            tick_lq = client_lq.fetch_tick()
            tick_bb = client_bb.fetch_tick()

            if tick_bf and tick_cc and tick_lq and tick_bb:
                output_bf = _format_csv(tick_bf.timestamp, tick_bf.bid,
                                        tick_bf.ask)
                output_cc = _format_csv(tick_cc.timestamp, tick_cc.bid,
                                        tick_cc.ask)
                output_lq = _format_csv(tick_lq.timestamp, tick_lq.bid,
                                        tick_lq.ask)
                output_bb = _format_csv(tick_bb.timestamp, tick_bb.bid,
                                        tick_bb.ask)

                fs_bf.write(output_bf + '\n')
                fs_bf.flush()
                fs_cc.write(output_cc + '\n')
                fs_cc.flush()
                fs_lq.write(output_lq + '\n')
                fs_lq.flush()
                fs_bb.write(output_bb + '\n')
                fs_bb.flush()

                time.sleep(ccxtconst.TICK_INTERVAL_SEC)
            else:
                time.sleep(10)
    finally:
        fs_bf.close()
        fs_cc.close()
        fs_lq.close()
        fs_bb.close()
