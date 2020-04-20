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
