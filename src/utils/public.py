import time
from queue import Queue
import threading

from src.libs.ccxt_client import CcxtClient
from src.libs.websocket_client import WebsocketClient
import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
from src.core.board import Board, Tick
import src.utils.datetime as dt


def _logging(timestamp, bid, ask):
    output = "{} bid={} ask={}".format(timestamp, bid, ask)
    print(output)


def fetch_ticks(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY, eff=False):
    client = CcxtClient(exchange_id, symbol)

    while True:
        time.sleep(exchange.TICK_INTERVAL_SEC)

        if not eff:
            tick = client.fetch_tick()
        else:
            tick = client.fetch_eff_tick()

        if not tick:
            print("no data...")
            continue

        timestamp = dt.now_timestamp_ms()
        tick = Tick(timestamp, int(tick.bid), int(tick.ask))
        print(tick)


def fetch_tick(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    client = CcxtClient(exchange_id, symbol)
    return client.fetch_tick()


def fetch_ws_ticks(exchange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    __queue = Queue()
    client = WebsocketClient(__queue, exchange_id, symbol)

    worker = threading.Thread(target=client.fetch_ticks, daemon=True)
    worker.start()

    while True:
        if not __queue.empty():
            data = __queue.get()
            print(data)
            __queue.task_done()
        else:
            print(__queue.qsize())
        time.sleep(1)


def fetch_board(exhange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    board = Board(exhange_id, symbol)

    while True:
        board.display()
        time.sleep(5)


def fetch_board_tick(exhange_id, symbol=ccxtconst.SYMBOL_BTC_JPY):
    board = Board(exhange_id, symbol)

    while True:
        time.sleep(1)
        tick = board.get_eff_tick()
        print(tick)
