from abc import ABCMeta, abstractmethod


class ExchangeBase(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def order_buy(self, symbol, amount):
        pass

    @abstractmethod
    def order_sell(self, symbol, amount):
        pass
