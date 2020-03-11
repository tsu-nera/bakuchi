from src.config import config


class Wallet():
    def __init__(self, exchange_id):
        self.exchange_id = exchange_id
        self.balance_jpy = config['backtest']["demo_balance_jpy"]
        self.balance_btc = config['backtest']["demo_balance_btc"]
