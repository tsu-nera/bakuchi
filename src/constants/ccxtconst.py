from enum import Enum, auto

TICK_INTERVAL_SEC = 1


class TradeMode(Enum):
    NORMAL = auto()
    BOT = auto()


SYMBOL_BTC_JPY = "BTC/JPY"
SYMBOL_BTC_USD = "BTC/USD"
