import src.env as env
from enum import Enum

TICK_INTERVAL_SEC = 1


class ExchangeId(Enum):
    BITFLYER = "bitflyer"
    COINCHECK = "coincheck"
    LIQUID = "liquid"
    BITBANK = "bitbank"
    BITMEX = "bitmex"
    BITMEX_DEMO = "bitmex_demo"
    GEMINI_DEMO = "gemini_demo"


# 現在対応している取引所
EXCHANGE_ID_LIST = [ExchangeId.COINCHECK, ExchangeId.LIQUID]

SYMBOL_BTC_JPY = "BTC/JPY"
SYMBOL_BTC_USD = "BTC/USD"

API_KEY = "apiKey"
API_SECRET = "apiSecret"

EXCHANGE_AUTH_DICT = {
    ExchangeId.BITFLYER: {
        API_KEY: env.BITFLYER_API_KEY,
        API_SECRET: env.BITFLYER_API_SECRET
    },
    ExchangeId.COINCHECK: {
        API_KEY: env.COINCHECK_API_KEY,
        API_SECRET: env.COINCHECK_API_SECRET
    },
    ExchangeId.LIQUID: {
        API_KEY: env.LIQUID_API_KEY,
        API_SECRET: env.LIQUID_API_SECRET
    },
    ExchangeId.BITBANK: {
        API_KEY: env.BITBANK_API_KEY,
        API_SECRET: env.BITBANK_API_SECRET
    },
    ExchangeId.BITMEX: {
        API_KEY: env.BITMEX_API_KEY,
        API_SECRET: env.BITMEX_API_SECRET
    },
    ExchangeId.BITMEX_DEMO: {
        API_KEY: env.BITMEX_TESTNET_API_KEY,
        API_SECRET: env.BITMEX_TESTNET_API_SECRET
    },
    ExchangeId.GEMINI_DEMO: {
        API_KEY: env.GEMINI_SANDBOX_API_KEY,
        API_SECRET: env.GEMINI_SANDBOX_API_SECRET
    }
}
