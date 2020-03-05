import ccxt
from time import sleep
import src.constants.ccxtconst as cctxconst

bf = ccxt.bitflyer()
cc = ccxt.coincheck()


def _diff(a, b):
    return abs(a - b)


def trade():

    while True:
        bf_tick = bf.fetch_ticker(cctxconst.SYMBOL_BTC_JPY)
        cc_tick = cc.fetch_ticker(cctxconst.SYMBOL_BTC_JPY)

        bf_ask = bf_tick["ask"]
        bf_bid = bf_tick["bid"]
        cc_ask = cc_tick["ask"]
        cc_bid = cc_tick["bid"]

        print("[bitFlyer] ask:{} bid:{}".format(bf_ask, bf_bid))
        print("[Coincheck] ask:{} bid:{}".format(cc_ask, cc_bid))

        print("---")

        if not (not (bf_ask < cc_bid) and not (cc_ask < bf_bid)):
            break

        sleep(1)

    if bf_ask < cc_bid:
        print("bitFlyerで1BTCを{}円で買いCoincheckで1BTCを{}円で売れば、{}円の利益が出ます。".format(
            bf_ask, cc_bid, cc_bid - bf_ask))

    if cc_ask < bf_bid:
        print("Coincheckで1BTCを{}円で買いbidFlyerで1BTCを{}円で売れば、{}円の利益が出ます。".format(
            cc_ask, bf_bid, bf_bid - cc_ask))
