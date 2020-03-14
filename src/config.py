import configparser

config = configparser.ConfigParser()
config.read('src/config.ini')

TRADE_AMOUNT = float(config["trade"]["amount"])
TRADE_PROFIT_MARGIN_THRESHOLD = int(config["trade"]["profit_margin_threshold"])
TRADE_DEMO_MODE = int(config["trade"]["demo_mode"])

BACKTEST_BALANCE_BTC = float(config["backtest"]["balance_btc"])
BACKTEST_BALANCE_JPY = int(config["backtest"]["balance_jpy"])
