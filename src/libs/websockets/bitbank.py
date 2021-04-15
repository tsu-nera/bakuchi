import socketio

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import WEBSOCKET_API_ENDPOINT_BITBANK, WsDataOrderbook, WsDataTrade

# api document for bitbank
# https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream_JP.md


class WebsocketClientBitbank(WebsocketClientBase):
    def __init__(self, queue, symbol):
        self.queue = queue
        self.symbol = symbol

        self.sio = socketio.Client()

        symbols = symbol.split("/")
        self.PAIR = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.CHANNEL_ORDERBOOK = "depth_whole_{}".format(self.PAIR)
        self.CHANNEL_TRADES = "transactions_{}".format(self.PAIR)

        self.__connect()

    def __connect(self):
        self.sio.on('connect', self.__on_connect)
        self.sio.on('trades', self.__on_trades)
        self.sio.on('orderbook', self.__on_orderbook)
        self.sio.connect(
            WEBSOCKET_API_ENDPOINT_BITBANK,
            transports=['websocket'],
        )

    def __on_orderbook(self, data):
        orderbook = WsDataOrderbook(data[1]["bids"], data[1]["asks"])
        self.queue.put(orderbook)

    def __on_trades(self, data):
        trade = WsDataTrade(float(data[2]), float(data[3]), data[4])
        self.queue.put(trade)

    def __on_connect(self):
        self.sio.emit('join-room', self.CHANNEL_ORDERBOOK)
        self.sio.emit('join-room', self.CHANNEL_TRADES)

    def fetch_ticks(self):
        self.sio.wait()
