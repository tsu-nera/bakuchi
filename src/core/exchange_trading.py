from .exchange_base import ExchangeBase
# from src.config import config


class ExchangeTrading(ExchangeBase):
    def __init__(self, exchange_id):
        self.exchange_id = exchange_id

    def order_buy(self, symbol, amount, price):
        pass

    def order_sell(self, symbol, amount, price):
        pass
