import configparser

config = configparser.ConfigParser()
config.read('src/config.ini')

OPEN_THRESHOLD_CHANGE_SEC = int(
    config["arbitrage"]["open_threshold_change_sec"])
FORCE_CLOSING_MIN = int(config["arbitrage"]["force_closing_min"])

TRADE_AMOUNT = float(config["trade"]["amount"])
TRADE_OPEN_THRESHOLD = int(config["trade"]["open_threshold"])
TRADE_MINIMUM_OPEN_THRESHOLD = int(config["trade"]["minimum_open_threshold"])
TRADE_PROFIT_MARGIN_DIFF = int(config["trade"]["profit_margin_diff"])
TRADE_TICK_INTERVAL_SEC = float(config["trade"]["tick_interval_sec"])

BACKTEST_AMOUNT = float(config["backtest"]["amount"])
BACKTEST_OPEN_THRESHOLD = int(config["backtest"]["open_threshold"])
BACKTEST_PROFIT_MARGIN_DIFF = int(config["backtest"]["profit_margin_diff"])

COINCHECK_ORDER_BUY_ADJUST_AMOUNT_BTC = float(
    config["coincheck"]["buy_adjusted_amount_btc"])
