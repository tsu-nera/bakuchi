import os
import shutil
import src.utils.datetime as dt

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path

from src.libs.ccxt_client import CcxtClient


def _get_tick(exchange_id):
    c = CcxtClient(exchange_id)
    tick = c.fetch_tick()
    return tick["bid"], tick["ask"]


def check_profit_margin():
    '''
    二つの取引所の価格差をチェックするツール
    '''
    # とりあえずこの2つで決め打ち
    ex_x_id = ccxtconst.EXCHANGE_ID_COINCHECK
    ex_y_id = ccxtconst.EXCHANGE_ID_LIQUID

    bid_x, ask_x = _get_tick(ex_x_id)
    bid_y, ask_y = _get_tick(ex_y_id)

    diff1 = bid_x - ask_y
    diff2 = bid_y - ask_x

    output1 = "buy {} at {}, sell {} at {}, then get profit {}".format(
        ask_y, ex_y_id, bid_x, ex_x_id, diff1)
    output2 = "buy {} at {}, sell {} at {}, then get profit {}".format(
        ask_x, ex_x_id, bid_y, ex_y_id, diff2)

    print(output1)
    print(output2)


def backup_trades():
    now_dirname = dt.now_dirname()

    from_dir_path = path.TRADES_RAWDATA_DIR_PATH
    to_dir_path = os.path.join(path.TRADES_DATA_DIR_PATH, now_dirname)

    if not os.path.exists(to_dir_path):
        os.mkdir(to_dir_path)

        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            from_file_name = "latest_trades_{}.csv".format(exchange_id)
            to_file_name = "{}.csv".format(exchange_id)

            from_file_path = os.path.join(from_dir_path, from_file_name)
            to_file_path = os.path.join(to_dir_path, to_file_name)

            shutil.copy(from_file_path, to_file_path)
