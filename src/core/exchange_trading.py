from src.libs.ccxt_client import CcxtClient
from .exchange_base import ExchangeBase
import src.constants.ccxtconst as ccxtconst

from src.config import COINCHECK_ORDER_BUY_ADJUST_AMOUNT_BTC  # , TRADE_AMOUNT


class ExchangeTrading(ExchangeBase):
    def __init__(self, exchange_id, symbol, demo_mode=False):
        self.exchange_id = exchange_id
        self.symbol = symbol
        self.demo_mode = demo_mode

        self.client = CcxtClient(exchange_id, symbol, demo_mode=demo_mode)

    def fetch_tick(self, eff=False):
        if not eff:
            return self.client.fetch_tick()
        else:
            # 取引が成立しないのでamountを設定しない。
            # return self.client.fetch_eff_tick()
            return self.client.fetch_eff_tick()

    def _format_order_response(self, response, amount, bid_for_coincheck=None):
        info = response["info"]

        def _to_json(jpy, btc):
            return {
                "exchange_id": self.exchange_id,
                "symbol": self.symbol,
                "jpy": jpy,
                "btc": btc
            }

        if self.exchange_id == ccxtconst.ExchangeId.COINCHECK:
            if info["order_type"] == "market_buy":
                jpy = float(info["market_buy_amount"])
            else:
                jpy = amount * bid_for_coincheck
            btc = amount
            return _to_json(jpy, btc)
        elif self.exchange_id == ccxtconst.ExchangeId.LIQUID:
            btc = float(info["quantity"])
            jpy = float(info["price"]) * btc
            return _to_json(jpy, btc)
        else:
            return {}

    def order_buy(self, amount, ask_for_coincheck=None):

        # coincheckは amountにBTCではなくて、JPYを指定する。
        # https://coincheck.com/ja/documents/exchange/api#order-new
        if ask_for_coincheck:
            # coincheckでは buyでどうも実際よりも低い値で注文が成立されるので
            # 補正値でrequestを出してみる
            adjusted_amount = amount + COINCHECK_ORDER_BUY_ADJUST_AMOUNT_BTC
            price = int(ask_for_coincheck * adjusted_amount)
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
