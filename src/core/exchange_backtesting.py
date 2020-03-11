from .exchange_base import ExchangeBase
from src.config import config


class ExchangeBacktesting(ExchangeBase):
    def __init__(self):
        self.balance_jpy = float(config['backtest']["balance_jpy"])
        self.balance_btc = float(config['backtest']["balance_btc"])

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

    def get_balances(self):
        return {"BTC": self.balance_btc, "JPY": self.balance_jpy}
