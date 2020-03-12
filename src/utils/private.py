from src.libs.ccxt_client import CcxtClient


def fetch_balance(exchange_id):
    client = CcxtClient(exchange_id)

    balance = client.fetch_balance()["free"]
    print(balance)


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


def create_buy_order(exchange_id, amount):
    client = CcxtClient(exchange_id)

    order_info = client.create_market_buy_order(amount)

    print(order_info)


def create_sell_order(exchange_id, amount):
    client = CcxtClient(exchange_id)

    order_info = client.create_market_sell_order(amount)

    print(order_info)
