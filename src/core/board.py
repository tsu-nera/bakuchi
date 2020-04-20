import threading
from decimal import Decimal
from queue import Queue

from sortedcontainers import SortedDict

import src.utils.datetime as dt
from src.core.tick import Tick
from src.constants.wsconst import WsDataType
from src.libs.ccxt_client import CcxtClient
from src.libs.websocket_client import WebsocketClient
from src.loggers.logger import get_ccxt_logger


class Board():
    def __init__(self, exchange_id, symbol):
        self.__exchange_id = exchange_id
        self.__symbol = symbol

        self.__queue = Queue()
        self.__wsclient = WebsocketClient(self.__queue, exchange_id, symbol)
        self.__ccxtclient = CcxtClient(exchange_id, symbol)
        self.__logger = get_ccxt_logger()

        self.bids = SortedDict()
        self.asks = SortedDict()

        self.__build_board()

        producer_worker = threading.Thread(target=self.__wsclient.fetch_ticks,
                                           daemon=True)
        consumer_worker = threading.Thread(target=self.__update_board,
                                           daemon=True)

        producer_worker.start()
        consumer_worker.start()

    def __append_to_board(self, board, order_list):
        if len(order_list) == 0:
            return

        for order in order_list:
            rate = int(float(order[0]))
            amount = float(order[1])

            if amount != 0:
                board[rate] = amount
            elif rate in board:
                del board[rate]

    def __build_board(self):
        res = self.__ccxtclient.fetch_order_book()

        bids = res["bids"]
        asks = res["asks"]

        self.__append_to_board(self.bids, bids)
        self.__append_to_board(self.asks, asks)

    def __update_board(self):
        while True:
            if not self.__queue.empty():
                data = self.__queue.get()

                if data.type == WsDataType.TRADES:
                    self.__remove_order(data)
                else:
                    self.__append_order(data)

                self.__queue.task_done()

    def __append_order(self, data):
        self.__append_to_board(self.bids, data.bids)
        self.__append_to_board(self.asks, data.asks)

    def __remove_order(self, data):
        rate = int(data.rate)
        amount = data.amount
        side = data.side

        if data.side == "sell":
            board = self.bids
        else:
            board = self.asks

        if amount != 0:
            if rate in board:
                board[rate] = float(
                    Decimal(str(board[rate])) - Decimal(str(amount)))
                if board[rate] <= 0:
                    del board[rate]
        elif rate in board:
            del board[rate]

        rates = []
        if side == 'sell':
            for k in board.keys()[::-1]:
                if k > rate:
                    rates.append(k)
                else:
                    break
        else:
            for k in board.keys():
                if k < rate:
                    rates.append(k)
                else:
                    break

        for rate in rates:
            del board[rate]

    def __logging_tick(self, bid, ask):
        self.__logger.info('tick bid=%s ask=%s (%s:%s)', bid, ask,
                           self.__exchange_id.value, self.__symbol)

    def get_tick(self, amount=1.0):
        bids = list(self.bids.items()[::-1])
        asks = list(self.asks.items())

        if len(bids) == 0 or len(asks) == 0:
            return None

        i = 0
        s = 0
        while s <= amount:
            s += bids[i][1]
            i += 1

        bid = bids[i - 1][0]

        j = 0
        t = 0
        while t <= amount:
            t += asks[j][1]
            j += 1
        ask = asks[j - 1][0]

        self.__logging_tick(bid, ask)

        timestamp = dt.now_timestamp_ms()
        tick = Tick(timestamp, bid, ask)

        return tick

    def display(self):
        print("=== bids(買い注文) ===")
        print(list(self.bids.items()))
        print("=== asks(売り注文) ===")
        print(list(self.asks.items()))
        print()
