import src.constants.ccxtconst as ccxtconst
from src.libs.websockets.coincheck import WebsocketClientCoincheck


class WebsocketClient():
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        if self.exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
            self.ws = WebsocketClientCoincheck(exchange_id, symbol)

    def fetch_ticks(self):
        while True:
            print(self.ws.fetch_ticks())
