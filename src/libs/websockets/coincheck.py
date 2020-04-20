import socketio

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import SOCKETIO_URL

import src.utils.datetime as dt


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, queue, exchange_id, symbol):
        self.queue = queue
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.sio = socketio.Client()

        symbols = symbol.split("/")
        self.PAIR = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.CHANNEL_ORDERBOOK = "{}-orderbook".format(self.PAIR)
        self.CHANNEL_TRADES = "{}-trades".format(self.PAIR)

        self.connect()

    def connect(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('trades', self.on_trades)
        self.sio.on('orderbook', self.on_orderbook)
        self.sio.connect(SOCKETIO_URL,
                         transports=['polling'],
                         socketio_path='socket.io')

    def on_orderbook(self, data):
        timestamp = dt.now_timestamp_ms()
        orderbook = {
            "timestamp": timestamp,
            "bids": data[1]["bids"],
            "asks": data[1]["asks"]
        }
        self.queue.put(orderbook)

    def on_trades(self, data):
        pass
        # print(data)
        # timestamp = dt.now_timestamp_ms()
        # orderbooks = {
        #     "timestamp": timestamp,
        #     "bids": data[1]["bids"],
        #     "asks": data[1]["asks"]
        # }
        # self.queue.put(orderbooks)

    def on_connect(self):
        self.sio.emit('subscribe', self.CHANNEL_ORDERBOOK)
        self.sio.emit('subscribe', self.CHANNEL_TRADES)

    def fetch_ticks(self):
        self.sio.wait()
