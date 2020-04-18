import src.constants.ccxtconst as ccxtconst

from src.libs.websockets.coincheck import WebsocketClientCoincheck
from src.libs.websockets.liquid import WebsocketClientLiquid


class WebsocketClient():
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        if self.exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
            self.ws = WebsocketClientCoincheck(exchange_id, symbol)
        elif self.exchange_id == ccxtconst.EXCHANGE_ID_LIQUID:
            self.ws = WebsocketClientLiquid(exchange_id, symbol)
        else:
            self.ws = None

    def fetch_ticks(self):
        while True:
            print(self.ws.fetch_ticks())
