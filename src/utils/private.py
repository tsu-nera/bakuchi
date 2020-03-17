import time

from src.core.exchange_trading import ExchangeTrading as Exchange
from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst


def fetch_balance(exchange_id):
    client = CcxtClient(exchange_id)

    return client.fetch_balance()['total']


def fetch_open_orders(exchange_id):
    client = CcxtClient(exchange_id)

    open_orders = client.fetch_open_orders()
    print(open_orders)


def get_positions(exchange_id):
    client = CcxtClient(exchange_id)

    positions = client.get_positions()

    # 取得できる情報が多すぎるのて間引く
    data = []
    for position in positions:
        if position["currentQty"] == 0:
            continue

        output = {
            "symbol": position["symbol"],
            "timestamp": position["openingTimestamp"],
            "size": position["currentQty"],
        }
        data.append(output)

    print(data)


def create_buy_order(exchange_id, symbol, amount, ask_for_coincheck=None):
    ex = Exchange(exchange_id, symbol)
    order_info = ex.order_buy(amount, ask_for_coincheck)
    return order_info


def create_sell_order(exchange_id, symbol, amount, bid_for_coincheck=None):
    ex = Exchange(exchange_id, symbol)
    order_info = ex.order_sell(amount, bid_for_coincheck)
    return order_info


def create_coincheck_buy_order(symbol, amount):
    exchange_id = ccxtconst.EXCHANGE_ID_COINCHECK
    client = CcxtClient(exchange_id)
    tick = client.fetch_tick()

    ask = float(tick["ask"])
    bid = float(tick["bid"])

    if amount < 0.005:
        n = int(amount * 1000)
        amount_buy = 0.007
        amount_sell = 0.006

        order_info = []

        for _ in range(n):
            info = create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                    amount_buy, ask)
            order_info.append(info)
            time.sleep(1)

            info = create_sell_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                     amount_sell, bid)
            order_info.append(info)
            time.sleep(1)
    else:
        order_info = create_buy_order(exchange_id, symbol, amount, ask)
    return order_info


def create_coincheck_sell_order(symbol, amount):
    exchange_id = ccxtconst.EXCHANGE_ID_COINCHECK
    client = CcxtClient(exchange_id)
    tick = client.fetch_tick()
    ask = float(tick['ask'])
    bid = float(tick["bid"])

    if amount < 0.005:
        n = int(amount * 1000)
        amount_sell = 0.007
        amount_buy = 0.006

        order_info = []

        for _ in range(n):
            info = create_sell_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                     amount_sell, bid)
            order_info.append(info)
            time.sleep(1)

            info = create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                    amount_buy, ask)
            order_info.append(info)
            time.sleep(1)
    else:
        order_info = create_sell_order(exchange_id, symbol, amount, bid)
    return order_info


def fetch_trades(exchange_id):
    client = CcxtClient(exchange_id)
    return client.fetch_trades()
