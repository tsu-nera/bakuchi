import json
from websocket import create_connection

from src.constants.wsconst import WEBSOCKET_ENDPOINTS


class WebsocketClient():
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.ws = create_connection(WEBSOCKET_ENDPOINTS[exchange_id])

        symbols = symbol.split("/")
        channel = "{}_{}-orderbook".format(symbols[0], symbols[1])

        self.ws.send(json.dumps({"type": "subscribe", "channel": channel}))

    def fetch_ticks(self):
        while True:
            print(self.ws.recv())
