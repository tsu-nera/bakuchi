import configparser

config = configparser.ConfigParser()
config.read('src/config.ini')

OPEN_THRESHOLD_CHANGE_SEC = int(
    config["arbitrage"]["open_threshold_change_sec"])

TRADE_AMOUNT = float(config["trade"]["amount"])
TRADE_OPEN_THRESHOLD = int(config["trade"]["open_threshold"])
TRADE_PROFIT_MARGIN_DIFF = int(config["trade"]["profit_margin_diff"])

BACKTEST_AMOUNT = float(config["backtest"]["amount"])
BACKTEST_OPEN_THRESHOLD = int(config["backtest"]["open_threshold"])
BACKTEST_PROFIT_MARGIN_DIFF = int(config["backtest"]["profit_margin_diff"])
BACKTEST_BALANCE_BTC = float(config["backtest"]["balance_btc"])
BACKTEST_BALANCE_JPY = int(config["backtest"]["balance_jpy"])
