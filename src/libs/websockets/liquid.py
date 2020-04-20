import ast
import time
import liquidtap

from src.constants.wsconst import WsDataOrderbook
from src.libs.websockets.websocket_client_base import WebsocketClientBase


class WebsocketClientLiquid(WebsocketClientBase):
    def __init__(self, queue, exchange_id, symbol):
        self.queue = queue
        self.exchange_id = exchange_id
        self.symbol = symbol
        symbols = symbol.split("/")

        self.CHANNEL = "{}{}".format(str.lower(symbols[0]),
                                     str.lower(symbols[1]))

        self.ws = liquidtap.Client()
        self.ws.pusher.connection.bind('pusher:connection_established',
                                       self.on_connect)
        self.ws.pusher.connect()

    def on_connect(self, data):
        self.ws.pusher.subscribe("price_ladders_cash_{}_buy".format(
            self.CHANNEL)).bind('updated', self.on_orderbook_asks)
        self.ws.pusher.subscribe("price_ladders_cash_{}_sell".format(
            self.CHANNEL)).bind('updated', self.on_orderbook_bids)

    def on_orderbook_asks(self, data):
        data = ast.literal_eval(data)
        orderbook = WsDataOrderbook([], data)
        self.queue.put(orderbook)

    def on_orderbook_bids(self, data):
        data = ast.literal_eval(data)
        orderbook = WsDataOrderbook(data, [])
        self.queue.put(orderbook)

    def fetch_ticks(self):
        while True:
            time.sleep(0)
