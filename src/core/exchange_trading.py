from src.libs.ccxt_client import CcxtClient
from .exchange_base import ExchangeBase


class ExchangeTrading(ExchangeBase):
    def __init__(self, exchange_id, symbol):
        self.exchange_id = exchange_id
        self.symbol = symbol

        self.client = CcxtClient(exchange_id, symbol)

    def order_buy(self, amount, ask_for_coincheck=None):

        # coincheckは amountにBTCではなくて、JPYを指定する。
        # https://coincheck.com/ja/documents/exchange/api#order-new
        if ask_for_coincheck:
            price = int(ask_for_coincheck * amount)
            self.client.create_market_buy_order(price)
        else:
            self.client.create_market_buy_order(amount)

    def order_sell(self, amount):
        self.client.create_market_sell_order(amount)
