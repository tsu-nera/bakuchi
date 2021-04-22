from abc import ABCMeta, abstractmethod


class Model(metaclass=ABCMeta):
    def to_json(self):
        return self.__dict__
