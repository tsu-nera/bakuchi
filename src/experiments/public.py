import time
from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst


def fetch_ticks(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    client = CcxtClient(exchange_id, symbol)

    for _ in range(10):
        ticker = client.fetch_tick()
        output = "bid:{} ask:{}".format(ticker["bid"], ticker["ask"])
        print(output)
        time.sleep(1)
