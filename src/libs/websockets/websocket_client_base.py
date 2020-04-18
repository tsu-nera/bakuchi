from abc import ABCMeta, abstractmethod


class WebsocketClientBase(metaclass=ABCMeta):
    @abstractmethod
    def fetch_ticks(self):
        pass
