import ast
import time
import liquidtap

from src.constants.wsconst import WsDataOrderbook, WsDataTrade
from src.libs.websockets.websocket_client_base import WebsocketClientBase


class WebsocketClientLiquid(WebsocketClientBase):
    def __init__(self, queue, exchange_id, symbol):
        self.queue = queue
        self.exchange_id = exchange_id
        self.symbol = symbol
        symbols = symbol.split("/")

        self.CHANNEL = "{}{}".format(str.lower(symbols[0]),
                                     str.lower(symbols[1]))

        self.__ws = liquidtap.Client()
        self.__ws.pusher.connection.bind('pusher:connection_established',
                                         self.__on_connect)
        self.__ws.pusher.connect()

    def __on_connect(self, data):
        self.__ws.pusher.subscribe("price_ladders_cash_{}_buy".format(
            self.CHANNEL)).bind('updated', self.__on_orderbook_asks)
        self.__ws.pusher.subscribe("price_ladders_cash_{}_sell".format(
            self.CHANNEL)).bind('updated', self.__on_orderbook_bids)
        self.__ws.pusher.subscribe("executions_cash_{}".format(
            self.CHANNEL)).bind('created', self.__on_trades)
        # execution_details_cash も追加して executions_cashが遅延したときの対策をいれるか？

    def __on_orderbook_asks(self, data):
        data = ast.literal_eval(data)
        orderbook = WsDataOrderbook([], data)
        self.queue.put(orderbook)

    def __on_orderbook_bids(self, data):
        data = ast.literal_eval(data)
        orderbook = WsDataOrderbook(data, [])
        self.queue.put(orderbook)

    def __on_trades(self, data):
        data = ast.literal_eval(data)
        trade = WsDataTrade(data["price"], data["quantity"],
                            data["taker_side"])
        self.queue.put(trade)

    def fetch_ticks(self):
        while True:
            time.sleep(0)
