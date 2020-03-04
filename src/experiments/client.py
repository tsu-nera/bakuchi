import ccxt
import time

# from pprint import pprint

bitflyer = ccxt.bitflyer()

while range(10):
    ticker = bitflyer.fetch_ticker('BTC/JPY')
    # pprint(ticker)
    output = "bid:{} ask:{}".format(ticker["bid"], ticker["ask"])
    print(output)
    time.sleep(1)
