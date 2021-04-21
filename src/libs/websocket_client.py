import src.constants.exchange as exchange

from src.libs.websockets.coincheck import WebsocketClientCoincheck
from src.libs.websockets.liquid import WebsocketClientLiquid
from src.libs.websockets.bitbank import WebsocketClientBitbank


class WebsocketClient():
    def __init__(self, queue, exchange_id, symbol):
        self.queue = queue
        self.exchange_id = exchange_id
        self.symbol = symbol

        # coincheck 動かん...
        if self.exchange_id == exchange.ExchangeId.COINCHECK:
            self.ws = WebsocketClientCoincheck(queue, symbol)
        elif self.exchange_id == exchange.ExchangeId.LIQUID:
            self.ws = WebsocketClientLiquid(queue, symbol)
        elif self.exchange_id == exchange.ExchangeId.BITBANK:
            self.ws = WebsocketClientBitbank(queue, symbol)
        else:
            self.ws = None

    def fetch_ticks(self):
        self.ws.fetch_ticks()
