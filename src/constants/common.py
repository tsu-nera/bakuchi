import os

DATETIME_BASE_FORMAT = '%Y-%m-%d %H:%M:%S'

DATA_DIR = "data"
RAWDATA_DIR = "rawdata"

HISTORICAL_DATA_DIR = "historicals"
BACKTEST_DATA_DIR = "backtests"
LOG_DIR = "logs"
TRADES_DIR = "trades"

HISTORICAL_LOG_FILE = "historical.log"
TRADING_LOG_FILE = "trading.log"
CCXT_LOG_FILE = "ccxt.log"
MARGIN_LOG_FILE = "margin.log"
ASSET_LOG_FILE = "asset.log"

HISTORICAL_DATA_DIR_PATH = os.path.join(DATA_DIR, HISTORICAL_DATA_DIR)
BACKTEST_DATA_DIR_PATH = os.path.join(DATA_DIR, BACKTEST_DATA_DIR)
TRADES_RAWDATA_DIR_PATH = os.path.join(RAWDATA_DIR, TRADES_DIR)

HISTORICAL_LOG_FILE_PATH = os.path.join(LOG_DIR, HISTORICAL_LOG_FILE)
TRADING_LOG_FILE_PATH = os.path.join(LOG_DIR, TRADING_LOG_FILE)
CCXT_LOG_FILE_PATH = os.path.join(LOG_DIR, CCXT_LOG_FILE)
MARGIN_LOG_FILE_PATH = os.path.join(LOG_DIR, MARGIN_LOG_FILE)
ASSET_LOG_FILE_PATH = os.path.join(LOG_DIR, ASSET_LOG_FILE)
