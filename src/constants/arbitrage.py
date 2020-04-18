from enum import Enum, auto


class Action(Enum):
    OPENING = auto()
    CLOSING = auto()


class Strategy(Enum):
    BUY_X_SELL_Y = auto()
    BUY_Y_SELL_X = auto()
    DO_NOTHING = auto()
