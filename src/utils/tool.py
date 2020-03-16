import os
import pandas as pd

from tabulate import tabulate

import src.utils.public as public
import src.utils.private as private
import src.constants.ccxtconst as ccxtconst
from src.libs.ccxt_client import CcxtClient

import src.constants.common as common

EXCHANGE_ID_LIST = [
    ccxtconst.EXCHANGE_ID_COINCHECK, ccxtconst.EXCHANGE_ID_LIQUID
]


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

    if diff1 > diff2:
        output = "buy {} at {}, sell {} at {}, then get profit {}".format(
            ask_y, ex_y_id, bid_x, ex_x_id, diff1)
    else:
        output = "buy {} at {}, sell {} at {}, then get profit {}".format(
            ask_x, ex_x_id, bid_y, ex_y_id, diff2)

    print(output)


def check_asset():
    '''
    資産をチェックするツール
    '''
    coincheck_id = ccxtconst.EXCHANGE_ID_COINCHECK
    liquid_id = ccxtconst.EXCHANGE_ID_LIQUID

    balance_coincheck = private.fetch_balance(coincheck_id)
    balance_liquid = private.fetch_balance(liquid_id)

    data = []

    LABEL_JPY = "JPY"
    LABEL_BTC = "BTC"

    headers = ["取引所", LABEL_JPY, LABEL_BTC]
    data.append(headers)
    data.append([
        coincheck_id,
        int(balance_coincheck[LABEL_JPY]), balance_coincheck[LABEL_BTC]
    ])
    data.append(
        [liquid_id,
         int(balance_liquid[LABEL_JPY]), balance_liquid[LABEL_BTC]])

    balance_jpy = int(balance_coincheck[LABEL_JPY] + balance_liquid[LABEL_JPY])
    balance_btc = balance_coincheck[LABEL_BTC] + balance_liquid[LABEL_BTC]

    data.append(["合計", balance_jpy, balance_btc])

    print(tabulate(data, headers="firstrow"))

    coincheck_bid = public.fetch_tick(coincheck_id)["bid"]
    liquid_bid = public.fetch_tick(liquid_id)["bid"]

    def _calc_jpy(bid, btc):
        return int(bid * btc)

    print()
    print("総計: {}[JPY]".format(
        sum([
            int(balance_jpy),
            _calc_jpy(coincheck_bid, balance_coincheck[LABEL_BTC]),
            _calc_jpy(liquid_bid, balance_liquid[LABEL_BTC])
        ])))


def calc_btc_to_jpy(btc_amount):
    '''
    与えられたBTCの量から日本円の価格を計算する
    '''
    for exchange_id in EXCHANGE_ID_LIST:
        bid, _ = _get_tick(exchange_id)

        price = int(btc_amount * bid)
        output = "{}[BTC] to {}[JPY] ({})".format(btc_amount, price,
                                                  exchange_id)
        print(output)


def calc_jpy_to_btc(jpy_price):
    '''
    与えられた日本円の価格で購入できるBTCの量を計算する
    '''
    for exchange_id in EXCHANGE_ID_LIST:
        _, ask = _get_tick(exchange_id)

        btc_amount = round(jpy_price / ask, 6)
        output = "{}[JPY] to {}[BTC] ({})".format(jpy_price, btc_amount,
                                                  exchange_id)
        print(output)


def save_trades(exchange_id):
    trades = private.fetch_trades(exchange_id)

    file_name = "latest_trades_{}.csv".format(exchange_id)
    file_path = os.path.join(common.TRADES_RAWDATA_DIR_PATH, file_name)

    df = pd.DataFrame.from_dict(trades)

    df.to_csv(file_path, index=None)
