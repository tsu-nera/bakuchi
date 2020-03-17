import src.constants.ccxtconst as ccxtconst
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
