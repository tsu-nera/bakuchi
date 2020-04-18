import socketio

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import SOCKETIO_URL


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.sio = socketio.Client(SOCKETIO_URL)

        symbols = symbol.split("/")
        self.PAIR = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.CHANNEL = "{}-orderbook".format(self.PAIR)

    def connect(self):
        self.sio.on('connect', self.on_connect)
        self.sio.on('orderbook', self.on_orderbook)

        self.sio.connect(SOCKETIO_URL,
                         transports=['polling'],
                         socketio_path='socket.io')

    def on_orderbook(self, data):
        print(data)

    def on_connect(self):
        self.sio.emit('subscribe', self.CHANNEL)

    def fetch_ticks(self):
        self.connect()
