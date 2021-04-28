from src.utils.asset import read_trading_start_asset
from .exchange_base import ExchangeBase


class ExchangeBacktesting(ExchangeBase):
    def __init__(self, timestamp, exchange_id):
        self.__exchange_id = exchange_id
        self.__start_asset = read_trading_start_asset(timestamp)

        self.START_BALANCE_JPY = self.__start_asset[
            self.__exchange_id.value]["jpy"]
        self.START_BALANCE_BTC = self.__start_asset[
            self.__exchange_id.value]["btc"]
        self.START_TOTAL_JPY = self.__start_asset[
            self.__exchange_id.value]["total_jpy"]

        self.__balance_jpy = self.START_BALANCE_JPY
        self.__balance_btc = self.START_BALANCE_BTC

    def _calc_price(self, amount, price):
        return amount * price

    def order_buy(self, symbol, amount, price):
        value = self._calc_price(amount, price)
        self.__balance_jpy -= value
        self.__balance_btc += amount

    def order_sell(self, symbol, amount, price):
        value = self._calc_price(amount, price)
        self.__balance_jpy += value
        self.__balance_btc -= amount

    def get_balance_jpy(self):
        return self.__balance_jpy

    def get_balance_btc(self):
        return self.__balance_btc

    def get_profit_jpy(self):
        return self.__balance_jpy - self.START_BALANCE_JPY

    def get_profit_btc(self):
        return self.__balance_btc - self.START_BALANCE_BTC
