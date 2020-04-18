import time
import liquidtap

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

        self.bids_buffer = None
        self.asks_buffer = None

    def fetch_ticks(self):
        while True:
            time.sleep(1)

    def on_connect(self, data):
        self.ws.pusher.subscribe("price_ladders_cash_{}_buy".format(
            self.channel)).bind('updated', self.fetch_ticks_asks)
        self.ws.pusher.subscribe("price_ladders_cash_{}_sell".format(
            self.channel)).bind('updated', self.fetch_ticks_bids)

    def fetch_ticks_asks(self, data):
        self.asks_buffer = data
        self.update_buffer()

    def fetch_ticks_bids(self, data):
        self.bids_buffer = data
        self.update_buffer()

    def update_buffer(self):
        if self.asks_buffer and self.bids_buffer:
            timestamp = dt.now_timestamp_ms()
            ticks = {
                "timestamp": timestamp,
                "bids": self.bids_buffer,
                "asks": self.asks_buffer
            }
            print(ticks)

            self.asks_buffer = None
            self.bids_buffer = None
