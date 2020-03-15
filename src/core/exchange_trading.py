from src.libs.ccxt_client import CcxtClient
from .exchange_base import ExchangeBase
import src.constants.ccxtconst as ccxtconst


class ExchangeTrading(ExchangeBase):
    def __init__(self, exchange_id, symbol, demo_mode=False):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.demo_mode = demo_mode

        self.client = CcxtClient(exchange_id, symbol, demo_mode=demo_mode)

    def fetch_tick(self):
        return self.client.fetch_tick()

    def _format_order_response(self, response, amount, bid_for_coincheck=None):
        info = response["info"]

        def _to_json(jpy, btc):
            return {
                "exchange_id": self.exchange_id,
                "symbol": self.symbol,
                "jpy": jpy,
                "btc": btc
            }

        if self.exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
            if info["order_type"] == "market_buy":
                jpy = float(info["market_buy_amount"])
            else:
                jpy = amount * bid_for_coincheck
            btc = amount
            return _to_json(jpy, btc)
        elif self.exchange_id == ccxtconst.EXCHANGE_ID_LIQUID:
            btc = float(info["quantity"])
            jpy = float(info["price"]) * btc
            return _to_json(jpy, btc)
        else:
            return {}

    def order_buy(self, amount, ask_for_coincheck=None):

        # coincheckは amountにBTCではなくて、JPYを指定する。
        # https://coincheck.com/ja/documents/exchange/api#order-new
        if ask_for_coincheck:
            price = int(ask_for_coincheck * amount)
            response = self.client.create_market_buy_order(price)
        else:
            response = self.client.create_market_buy_order(amount)

        if self.demo_mode or not response:
            return None
        else:
            return self._format_order_response(response, amount)

    def order_sell(self, amount, bid_for_coincheck=None):
        response = self.client.create_market_sell_order(amount)

        if self.demo_mode or not response:
            return None
        else:
            return self._format_order_response(
                response, amount, bid_for_coincheck=bid_for_coincheck)
