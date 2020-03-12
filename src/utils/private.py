from src.libs.ccxt_client import CcxtClient


def fetch_balance(exchange_id):
    client = CcxtClient(exchange_id)

    print(client.fetch_balance())


def fetch_open_orders(exchange_id):
    client = CcxtClient(exchange_id)

    print(client.fetch_open_orders())


def get_positions(exchange_id):
    client = CcxtClient(exchange_id)

    print(client.get_positions())


def create_buy_order(exchange_id, amount):
    client = CcxtClient(exchange_id)

    order_info = client.create_market_buy_order(amount)

    print(order_info)


def create_sell_order(exchange_id, amount):
    client = CcxtClient(exchange_id)

    order_info = client.create_market_sell_order(amount)

    print(order_info)
