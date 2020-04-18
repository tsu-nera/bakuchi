import liquidtap
import time

import src.utils.datetime as dt
from src.libs.websockets.websocket_client_base import WebsocketClientBase


class WebsocketClientLiquid(WebsocketClientBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol
        symbols = symbol.split("/")
        self.channel = "{}{}".format(str.lower(symbols[0]),
                                     str.lower(symbols[1]))

        self.ws = liquidtap.Client()
        self.ws.pusher.connection.bind('pusher:connection_established',
                                       self.on_connect)
        self.ws.pusher.connect()

    def fetch_ticks(self):
        while True:
            time.sleep(1)

    def on_connect(self, data):
        self.ws.pusher.subscribe("price_ladders_cash_{}_buy".format(
            self.channel)).bind('updated', self.fetch_buy_ticks)
        self.ws.pusher.subscribe("price_ladders_cash_{}_sell".format(
            self.channel)).bind('updated', self.fetch_sell_ticks)

    def fetch_buy_ticks(self, data):
        timestamp = dt.now_timestamp()
        ticks = {"timestamp": timestamp, "asks": data}
        print(ticks)

    def fetch_sell_ticks(self, data):
        timestamp = dt.now_timestamp_ms()
        ticks = {"timestamp": timestamp, "bids": data}
        print(ticks)
