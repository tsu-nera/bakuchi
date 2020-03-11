from src.libs.ccxt_client import CcxtClient


def fetch_balance(exchange_id):
    client = CcxtClient(exchange_id)

    print(client.fetch_balance())


def create_order(exchange_id, order_side, amount):
    client = CcxtClient(exchange_id)

    order_info = client.create_order(order_side, amount)

    print(order_info)
