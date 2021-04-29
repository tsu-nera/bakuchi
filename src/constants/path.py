import os

# directory name
PRODUCTION_DIR = "../bakuchi_production"
DATA_DIR = "data"
RAWDATA_DIR = "rawdata"
HISTORICAL_DATA_DIR = "historicals"
BACKTEST_DATA_DIR = "backtests"
LOG_DIR = "logs"
TRADES_DIR = "trades"
ORDERS_DIR = "orders"
CRON_DIR = "cron"
ASSETS_DIR = "assets"
REPORTS_DIR = "reports"
TICKS_DIR = "ticks"
NOTEBOOKS_DIR = "notebooks"
TEMPLATES_DIR = "templates"

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
BOT_ORDER_CSV_FILE = "bot_order.csv"
BOT_PROFIT_CSV_FILE = "bot_profit.csv"

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
REPORTS_DATA_DIR_PATH = os.path.join(DATA_DIR, REPORTS_DIR)
TRADES_DATA_DIR_PATH = os.path.join(DATA_DIR, TRADES_DIR)
ORDERS_DATA_DIR_PATH = os.path.join(DATA_DIR, ORDERS_DIR)

# data/orders

# rawdata
TRADES_RAWDATA_DIR_PATH = os.path.join(RAWDATA_DIR, TRADES_DIR)
HISTORICAL_RAWDATA_DIR_PATH = os.path.join(RAWDATA_DIR, HISTORICAL_DATA_DIR)

# logs
TRADES_LOG_DIR = os.path.join(LOG_DIR, TRADES_DIR)
ORDERS_LOG_DIR = os.path.join(LOG_DIR, ORDERS_DIR)
CRON_LOG_DIR = os.path.join(LOG_DIR, CRON_DIR)
ASSETS_LOG_DIR = os.path.join(LOG_DIR, ASSETS_DIR)

# logs/trades
TRADING_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, TRADING_LOG_FILE)
CCXT_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, CCXT_LOG_FILE)
MARGIN_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, MARGIN_LOG_FILE)
ASSET_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, ASSET_LOG_FILE)
PROFIT_LOG_FILE_PATH = os.path.join(TRADES_LOG_DIR, PROFIT_LOG_FILE)

TRADES_LOGS = [
    CCXT_LOG_FILE_PATH, MARGIN_LOG_FILE_PATH, ASSET_LOG_FILE_PATH,
    TRADING_LOG_FILE_PATH, PROFIT_LOG_FILE_PATH
]

# logs/orders
BOT_PROFIT_CSV_FILE_PATH = os.path.join(ORDERS_LOG_DIR, BOT_PROFIT_CSV_FILE)
BOT_ORDER_CSV_FILE_PATH = os.path.join(ORDERS_LOG_DIR, BOT_ORDER_CSV_FILE)

# logs/assets
TRADING_START_ASSET_FILE_PATH = os.path.join(ASSETS_LOG_DIR,
                                             TRADING_START_ASSET_FILE)
TRADING_END_ASSET_FILE_PATH = os.path.join(ASSETS_LOG_DIR,
                                           TRADING_END_ASSET_FILE)

TRADES_ASSETS = [TRADING_START_ASSET_FILE_PATH, TRADING_END_ASSET_FILE_PATH]

# logs/cron
CRON_ASSET_LOG_FILE_PATH = os.path.join(CRON_LOG_DIR, ASSET_LOG_FILE)

# data/notebooks
NOTEBOOK_TEMPLATES_DIR = os.path.join(DATA_DIR, NOTEBOOKS_DIR, TEMPLATES_DIR)
