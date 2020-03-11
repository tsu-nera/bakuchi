from .exchange_base import ExchangeBase
from src.config import config


class ExchangeBacktesting(ExchangeBase):
    def __init__(self):
        self.balance_jpy_init = float(config['backtest']["balance_jpy"])
        self.balance_btc_init = float(config['backtest']["balance_btc"])
        self.balance_jpy = self.balance_jpy_init
        self.balance_btc = self.balance_btc_init

    def _calc_price(self, amount, price):
        return amount * price

    def order_buy(self, symbol, amount, price):
        value = self._calc_price(amount, price)
        self.balance_jpy -= value
        self.balance_btc += amount

    def order_sell(self, symbol, amount, price):
        value = self._calc_price(amount, price)
        self.balance_jpy += value
        self.balance_btc -= amount

    def get_balance_btc(self):
        return self.balance_btc

    def get_profit_btc(self):
        return self.balance_btc - self.balance_btc_init

    def get_balance_jpy(self):
        return self.balance_jpy

    def get_profit_jpy(self):
        return self.balance_jpy - self.balance_jpy_init
