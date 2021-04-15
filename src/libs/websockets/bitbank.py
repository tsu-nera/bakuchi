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

        self.PAIR = self._build_pair(symbol)
        self.CHANNEL_ORDERBOOK = "depth_whole_{}".format(self.PAIR)
        self.CHANNEL_TRADES = "transactions_{}".format(self.PAIR)

        self.__connect()

    def __connect(self):
        self.sio.on('connect', self.__on_connect)
        self.sio.on('message', self.__on_message)
        self.sio.connect(
            WEBSOCKET_API_ENDPOINT_BITBANK,
            transports=['websocket'],
        )

    def __on_message(self, data):
        room_name = data["room_name"]
        data = data["message"]["data"]

        if room_name == self.CHANNEL_ORDERBOOK:
            orderbook = WsDataOrderbook(data["bids"], data["asks"])
            self.queue.put(orderbook)
        elif room_name == self.CHANNEL_TRADES:
            transactions = data["transactions"]

            for transaction in transactions:
                rate = int(transaction["price"])
                amount = float(transaction["amount"])
                side = transaction["side"]
                trade = WsDataTrade(rate, amount, side)
                self.queue.put(trade)
        else:
            pass

    def __on_connect(self):
        self.sio.emit('join-room', self.CHANNEL_ORDERBOOK)
        self.sio.emit('join-room', self.CHANNEL_TRADES)

    def fetch_ticks(self):
        self.sio.wait()
