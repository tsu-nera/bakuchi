from abc import ABCMeta, abstractmethod


class ExchangeBase(metaclass=ABCMeta):
    @abstractmethod
    def order_buy(self, symbol, amount):
        raise NotImplementedError

    @abstractmethod
    def order_sell(self, symbol, amount):
        raise NotImplementedError
