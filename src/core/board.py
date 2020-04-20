import threading
from queue import Queue

from src.constants.wsconst import WsDataType
from src.libs.websocket_client import WebsocketClient


class Board():
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.queue = Queue()
        self.client = WebsocketClient(self.queue, exchange_id, symbol)

        producer_worker = threading.Thread(target=self.client.fetch_ticks,
                                           daemon=True)
        consumer_worker = threading.Thread(target=self.build_board,
                                           daemon=True)

        self.bids = {}
        self.asks = {}

        producer_worker.start()
        consumer_worker.start()

    def build_board(self):
        while True:
            if not self.queue.empty():
                data = self.queue.get()

                if data.type == WsDataType.TRADES:
                    print(data)
                self.queue.task_done()

    def show(self):
        print(self.bids, self.asks)
