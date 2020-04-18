import socketio

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import SOCKETIO_URL

import src.utils.datetime as dt


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.sio = socketio.Client()

        symbols = symbol.split("/")
        self.PAIR = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.CHANNEL = "{}-orderbook".format(self.PAIR)

        self.connect()

    def connect(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('orderbook', self.on_orderbook)
        self.sio.connect(SOCKETIO_URL,
                         transports=['polling'],
                         socketio_path='socket.io')

    def on_orderbook(self, data):
        timestamp = dt.now_timestamp_ms()
        ticks = {
            "timestamp": timestamp,
            "bids": data[1]["bids"],
            "asks": data[1]["asks"]
        }
        print(ticks)

    def on_connect(self):
        self.sio.emit('subscribe', self.CHANNEL)

    def fetch_ticks(self):
        self.sio.wait()
