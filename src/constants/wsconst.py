import src.constants.ccxtconst as ccxtconst
from enum import Enum, auto

WEBSOCKET_API_ENDPOINT_COINCHECK = "wss://ws-api.coincheck.com/"
WEBSOCKET_API_ENDPOINT_LIQUID = "wss://ws-api.coincheck.com/"
SOCKETIO_URL = 'https://ws.coincheck.com'

WEBSOCKET_ENDPOINTS = {
    ccxtconst.ExchangeId.COINCHECK: WEBSOCKET_API_ENDPOINT_COINCHECK,
    ccxtconst.ExchangeId.LIQUID: WEBSOCKET_API_ENDPOINT_LIQUID
}


class WsDataType(Enum):
    ORDERBOOK = auto()
    TRADES = auto()


class WsDataOrderbook():
    def __init__(self, bids, asks):
        self.type = WsDataType.ORDERBOOK
        self.bids = bids
        self.asks = asks

    def __str__(self):
        return "orderbook: bids:{}, asks:{}".format(self.bids, self.asks)


class WsDataTrade():
    def __init__(self, rate, amount, side):
        self.type = WsDataType.TRADES
        self.rate = rate
        self.amount = amount
        self.side = side

    def __str__(self):
        return "trade: rate:{}, amount:{}, side:{}".format(
            self.rate, self.amount, self.side)