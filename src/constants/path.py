import os

PRODUCTION_DIR = "../bakuchi_production"
DATA_DIR = "data"
RAWDATA_DIR = "rawdata"

HISTORICAL_DATA_DIR = "historicals"
BACKTEST_DATA_DIR = "backtests"
LOG_DIR = "logs"
TRADES_DIR = "trades"
CRON_DIR = "cron"
ASSETS_DIR = "assets"

HISTORICAL_LOG_FILE = "historical.log"
TRADING_LOG_FILE = "trading.log"
CCXT_LOG_FILE = "ccxt.log"
MARGIN_LOG_FILE = "margin.log"
ASSET_LOG_FILE = "asset.log"

# bakuchi_production
PRODUCTION_HISTORICAL_RAWDATA_DIR_PATH = os.path.join(PRODUCTION_DIR,
                                                      RAWDATA_DIR,
                                                      HISTORICAL_DATA_DIR)

# data
BACKTEST_DATA_DIR_PATH = os.path.join(DATA_DIR, BACKTEST_DATA_DIR)
ASSET_DATA_DIR_PATH = os.path.join(DATA_DIR, ASSETS_DIR)
HISTORICAL_DATA_DIR_PATH = os.path.join(DATA_DIR, HISTORICAL_DATA_DIR)
ASSET_DATA_DIR_PATH = os.path.join(DATA_DIR, ASSETS_DIR)
TRADES_DATA_DIR_PATH = os.path.join(DATA_DIR, TRADES_DIR)

# rawdata
TRADES_RAWDATA_DIR_PATH = os.path.join(RAWDATA_DIR, TRADES_DIR)
HISTORICAL_RAWDATA_DIR_PATH = os.path.join(RAWDATA_DIR, HISTORICAL_DATA_DIR)

# logs
TRADES_LOG_DIR = os.path.join(LOG_DIR, TRADES_DIR)
CRON_LOG_DIR = os.path.join(LOG_DIR, CRON_DIR)

# logs/trades
HISTORICAL_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, HISTORICAL_LOG_FILE)
TRADING_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, TRADING_LOG_FILE)
CCXT_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, CCXT_LOG_FILE)
MARGIN_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, MARGIN_LOG_FILE)
ASSET_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, ASSET_LOG_FILE)

# logs/cron
CRON_ASSET_LOG_FILE_PATH = os.path.join(CRON_LOG_DIR, ASSET_LOG_FILE)
