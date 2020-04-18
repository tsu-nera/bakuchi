import json
from websocket import create_connection

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import WEBSOCKET_API_ENDPOINT_COINCHECK

import src.utils.datetime as dt


class WebsocketClientCoincheck(WebsocketClientBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.ws = create_connection(WEBSOCKET_API_ENDPOINT_COINCHECK)

        symbols = symbol.split("/")
        self.pair = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.channel = "{}-orderbook".format(self.pair)
        self.ws.send(json.dumps({
            "type": "subscribe",
            "channel": self.channel
        }))

    def fetch_ticks(self):
        while True:
            timestamp = dt.now_timestamp_ms()
            data = json.loads(self.ws.recv())
            ticks = {
                "timestamp": timestamp,
                "bids": data[1]["bids"],
                "asks": data[1]["asks"]
            }
            print(ticks)
