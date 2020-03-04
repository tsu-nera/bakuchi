import ccxt
import time

# from pprint import pprint


def bitflyer():
    bitflyer = ccxt.bitflyer()

    for _ in range(10):
        ticker = bitflyer.fetch_ticker('BTC/JPY')
        # pprint(ticker)
        output = "bid:{} ask:{}".format(ticker["bid"], ticker["ask"])
        print(output)
        time.sleep(1)
