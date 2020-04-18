import json
import socketio
from sortedcontainers import SortedDict

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import SOCKETIO_URL

import src.utils.datetime as dt


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.sio = socketio.Client(SOCKETIO_URL)

        symbols = symbol.split("/")
        self.pair = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))

        self.channel = "{}-orderbook".format(self.pair)

        self.bids = SortedDict()
        self.asks = SortedDict()

        self.connect()

    def connect(self):
        pass
