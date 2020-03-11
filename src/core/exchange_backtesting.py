from .exchange_base import ExchangeBase
from src.config import config


class ExchangeBacktesting(ExchangeBase):
    def __init__(self):
        self.balance_jpy = config['backtest']["balance_jpy"]
        self.balance_btc = config['backtest']["balance_btc"]

    def order_buy(self, symbol, amount, price):
        pass

    def order_sell(self, symbol, amount, price):
        pass
