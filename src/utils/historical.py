import ccxt  # noqa
import time
import datetime
import os

from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst
from src.constants.common import HISTORICAL_DATA_DIR_PATH

PER_TICK_SEC = 1


def _get_dir_path():
    now = datetime.datetime.now()
    now_string = now.strftime("%y%m%d%H%M")
    return os.path.join(HISTORICAL_DATA_DIR_PATH, now_string)


def _get_file_path(dir_path, exchange_id):
    file_name = "{}.csv".format(exchange_id)
    return os.path.join(dir_path, file_name)


def _format_csv(date, bid, ask):
    return "{},{},{}".format(date, bid, ask)


def save_ticks():
    dir_path = _get_dir_path()
    os.mkdir(dir_path)

    bf_file_path = _get_file_path(dir_path, ccxtconst.EXCHANGE_ID_BITFLYER)
    cc_file_path = _get_file_path(dir_path, ccxtconst.EXCHANGE_ID_COINCHECK)
    lq_file_path = _get_file_path(dir_path, ccxtconst.EXCHANGE_ID_LIQUID)
    bb_file_path = _get_file_path(dir_path, ccxtconst.EXCHANGE_ID_BITBANK)

    fs_bf = open(bf_file_path, mode='w')
    fs_cc = open(cc_file_path, mode='w')
    fs_lq = open(lq_file_path, mode='w')
    fs_bb = open(bb_file_path, mode='w')

    header_string = 'date,bid,ask\n'
    fs_bf.write(header_string)
    fs_cc.write(header_string)
    fs_lq.write(header_string)
    fs_bb.write(header_string)

    client_bf = CcxtClient(ccxtconst.EXCHANGE_ID_BITFLYER)
    client_cc = CcxtClient(ccxtconst.EXCHANGE_ID_COINCHECK)
    client_lq = CcxtClient(ccxtconst.EXCHANGE_ID_LIQUID)
    client_bb = CcxtClient(ccxtconst.EXCHANGE_ID_BITBANK)

    try:
        for _ in range(1000000):
            tick_bf = client_bf.fetch_tick()
            tick_cc = client_cc.fetch_tick()
            tick_lq = client_lq.fetch_tick()
            tick_bb = client_bb.fetch_tick()

            if tick_bf and tick_cc and tick_lq and tick_bb:
                output_bf = _format_csv(tick_bf["date"], tick_bf["bid"],
                                        tick_bf["ask"])
                output_cc = _format_csv(tick_cc["date"], tick_cc["bid"],
                                        tick_cc["ask"])
                output_lq = _format_csv(tick_lq["date"], tick_lq["bid"],
                                        tick_lq["ask"])
                output_bb = _format_csv(tick_bb["date"], tick_bb["bid"],
                                        tick_bb["ask"])

                fs_bf.write(output_bf + '\n')
                fs_bf.flush()
                fs_cc.write(output_cc + '\n')
                fs_cc.flush()
                fs_lq.write(output_lq + '\n')
                fs_lq.flush()
                fs_bb.write(output_bb + '\n')
                fs_bb.flush()

                time.sleep(PER_TICK_SEC)
            else:
                time.sleep(10)
    finally:
        fs_bf.close()
        fs_cc.close()
        fs_lq.close()
        fs_bb.close()
