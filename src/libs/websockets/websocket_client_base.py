from abc import ABCMeta, abstractmethod


class WebsocketClientBase(metaclass=ABCMeta):
    @abstractmethod
    def fetch_ticks(self):
        raise NotImplementedError

    def _build_pair(self, symbol):
        symbols = symbol.split("/")
        return "{}_{}".format(str.lower(symbols[0]), str.lower(symbols[1]))
