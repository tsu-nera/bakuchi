from src.constants.exchange import EXCHANGE_ID_LIST
from src.libs.ccxt_client import CcxtClient


class Ticker():
    def __init__(self):
        self.clients = [
            CcxtClient(exchange_id) for exchange_id in EXCHANGE_ID_LIST
        ]

    def get_ticks(self):
        ticks = []
