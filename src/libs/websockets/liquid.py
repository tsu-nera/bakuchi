import liquidtap
import time


class WebsocketClientLiquid():
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.ws = liquidtap.Client()
        self.ws.pusher.connection.bind('pusher:connection_established',
                                       self.on_connect)
        self.ws.pusher.connect()

        while True:
            time.sleep(1)

    def on_connect(self, data):
        print(data)
        self.ws.pusher.subscribe("price_ladders_cash_btcjpy_buy").bind(
            'updated', self.fetch_ticks)

    def fetch_ticks(self, data):
        print(data)
