import json
from websocket import create_connection

from src.libs.websockets.websocket_client_base import WebsocketClientBase
from src.constants.wsconst import WEBSOCKET_API_ENDPOINT_BITBANK

import src.utils.datetime as dt

# api doc:
# https://github.com/bitbankinc/bitbank-api-docs/blob/master/public-stream_JP.md


class WebsocketClientBitbank(WebsocketClientBase):
    def __init__(self, symbol):
        self.symbol = symbol
        self.ws = create_connection(WEBSOCKET_API_ENDPOINT_BITBANK)

        symbols = symbol.split("/")
        self.pair = "{}_{}".format(str.lower(symbols[0]),
                                   str.lower(symbols[1]))
        self.channel = "depth_whole_{}".format(self.pair)
        self.ws.send(json.dumps({
            "type": "subscribe",
            "channel": self.channel
        }))

    def fetch_ticks(self):
        while True:
            # timestamp = dt.now_timestamp_ms()
            data = self.ws.recv()
            data = json.loads(data)
            ticks = {
                "timestamp": data[1]["timestamp"],
                "bids": data[1]["bids"],
                "asks": data[1]["asks"]
            }
            print(ticks)
