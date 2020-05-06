import os

# directory name
PRODUCTION_DIR = "../bakuchi_production"
DATA_DIR = "data"
RAWDATA_DIR = "rawdata"
HISTORICAL_DATA_DIR = "historicals"
BACKTEST_DATA_DIR = "backtests"
LOG_DIR = "logs"
TRADES_DIR = "trades"
CRON_DIR = "cron"
ASSETS_DIR = "assets"
REPORTS_DIR = "reports"
EXCHANGES_DIR = "exchanges"
NOTEBOOKS_DIR = "notebooks"
TEMPLATES_DIR = "templates"
ORDERS_DIR = "orders"

# file name
TRADING_LOG_FILE = "trading.log"
CCXT_LOG_FILE = "ccxt.log"
MARGIN_LOG_FILE = "margin.log"
ASSET_LOG_FILE = "asset.log"
PROFIT_LOG_FILE = "profit.log"

CONFIG_JSON_FILE = "config.json"
TRADING_START_ASSET_FILE = "start.json"
TRADING_END_ASSET_FILE = "end.json"
RESULT_JSON_FILE = "result.json"
ORDER_CSV_FILE = "order.csv"
PROFIT_CSV_FILE = "profit.csv"

REPORT_BACKTEST = "backtest.ipynb"
REPORT_TRADE = "trade.ipynb"

README_TEMPLATE_FILE = "README.tpl.md"
README_FILE = "README.md"

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
ASSETS_LOG_DIR = os.path.join(LOG_DIR, ASSETS_DIR)
ORDERS_LOG_DIR = os.path.join(LOG_DIR, ORDERS_DIR)

# logs/trades
TRADING_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, TRADING_LOG_FILE)
CCXT_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, CCXT_LOG_FILE)
MARGIN_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, MARGIN_LOG_FILE)
ASSET_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, ASSET_LOG_FILE)
PROFIT_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, PROFIT_LOG_FILE)

# logs/orders
PROFIT_CSV_FILE_PATH = os.path.join(ORDERS_LOG_DIR, PROFIT_CSV_FILE)
ORDER_CSV_FILE_PATH = os.path.join(ORDERS_LOG_DIR, ORDER_CSV_FILE)

TRADES_LOGS = [
    CCXT_LOG_FILE_PATH, MARGIN_LOG_FILE_PATH, ASSET_LOG_FILE_PATH,
    TRADING_LOG_FILE_PATH
]

# logs/assets
TRADING_START_ASSET_FILE_PATH = os.path.join(ASSETS_LOG_DIR,
                                             TRADING_START_ASSET_FILE)
TRADING_END_ASSET_FILE_PATH = os.path.join(ASSETS_LOG_DIR,
                                           TRADING_END_ASSET_FILE)

TRADES_ASSETS = [TRADING_START_ASSET_FILE_PATH, TRADING_END_ASSET_FILE_PATH]

# logs/cron
CRON_ASSET_LOG_FILE_PATH = os.path.join(CRON_LOG_DIR, ASSET_LOG_FILE)

# notebooks
NOTEBOOK_TEMPLATES_DIR = os.path.join(NOTEBOOKS_DIR, TEMPLATES_DIR)
