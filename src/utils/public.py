import time
from src.libs.ccxt_client import CcxtClient
import src.constants.ccxtconst as ccxtconst


def fetch_ticks(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    client = CcxtClient(exchange_id, symbol)

    while True:
        time.sleep(ccxtconst.TICK_INTERVAL_SEC)

        tick = client.fetch_tick()

        if not tick:
            print("no data...")
            continue

        output = "{} bid={} ask={}".format(tick["timestamp"], tick["bid"],
                                           tick["ask"])
        print(output)


def fetch_tick(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    client = CcxtClient(exchange_id, symbol)
    return client.fetch_tick()
