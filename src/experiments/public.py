import time
from src.libs.ccxt_client import CcxtClient


def fetch_ticks(exchange_id):
    client = CcxtClient(exchange_id)

    for _ in range(10):
        ticker = client.fetch_tick()
        output = "bid:{} ask:{}".format(ticker["bid"], ticker["ask"])
        print(output)
        time.sleep(1)
