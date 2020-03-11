from src.libs.ccxt_client import CcxtClient


def fetch_balance(exchange_id):
    client = CcxtClient(exchange_id)

    print(client.fetch_balance())
