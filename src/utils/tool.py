import time
import datetime

import numpy as np

import src.constants.ccxtconst as ccxtconst
import src.utils.trade_history as trade_history
import src.utils.private as private

from src.libs.ccxt_client import CcxtClient
from src.core.arbitrage_parallel import ArbitrageParallel


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


def adjust_coincheck_buy_amount():
    '''
    coincheck buyを orderしたときの価格の誤差を調査するツール
    '''
    adjust_amount_diff_list = [
        0, 0.000001, 0.000002, 0.000003, 0.000004, 0.000005
    ]
    amount = 0.006

    for adjust_amount_diff in adjust_amount_diff_list:
        print("amount={}, adjust_amount_diff={}".format(
            amount, adjust_amount_diff))

        adjusted_amount = amount + adjust_amount_diff

        count = 10

        print("order start count={}".format(count))

        for _ in range(count):
            order_info = private.create_coincheck_buy_order(
                ccxtconst.SYMBOL_BTC_JPY, adjusted_amount)
            print(order_info)
            time.sleep(5)

            order_info = private.create_coincheck_sell_order(
                ccxtconst.SYMBOL_BTC_JPY, amount)
            print(order_info)
            time.sleep(5)

        print("order end")

        print("get trade histories")
        trades = trade_history.get_trades(ccxtconst.EXCHANGE_ID_COINCHECK,
                                          count * 2)

        amounts = []
        for trade in trades:
            if trade["side"] == "buy":
                amounts.append(trade["amount"])

        print(amounts)

        print("buy amount mean: {}, std: {}".format(np.mean(amounts),
                                                    np.std(amounts)))

        print()


def ping(exchange_id):
    client = CcxtClient(exchange_id, ccxtconst.SYMBOL_BTC_JPY)

    print("PING {}".format(exchange_id))

    while True:
        start_timestamp = datetime.datetime.now()
        tick = client.fetch_tick()

        if tick:
            end_timestamp = datetime.datetime.now()

            ping_time_msec = round(
                (end_timestamp - start_timestamp).microseconds / 1000, 2)

            print("{} ping {} time={} ms ".format(start_timestamp, exchange_id,
                                                  ping_time_msec))
        else:
            print("{} can't access {}".format(start_timestamp, exchange_id))

        time.sleep(1)


def ping_with_thread():
    parallel = ArbitrageParallel(ccxtconst.EXCHANGE_ID_COINCHECK,
                                 ccxtconst.EXCHANGE_ID_LIQUID,
                                 ccxtconst.SYMBOL_BTC_JPY)

    responses = parallel.fetch_tick()

    return responses
