from src.libs.ccxt_client import CcxtClient
from .exchange_base import ExchangeBase
import src.constants.exchange as exchange

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

    def _format_order_response(self, response, amount, extinfo=None):
        info = response["info"]

        def _to_json(jpy, btc):
            return {
                "exchange_id": self.exchange_id,
                "symbol": self.symbol,
                "jpy": jpy,
                "btc": btc
            }

        if self.exchange_id == exchange.ExchangeId.COINCHECK:
            if info["order_type"] == "market_buy":
                jpy = float(info["market_buy_amount"])
            else:
                jpy = float(amount) * float(extinfo)
            btc = amount
            return _to_json(jpy, btc)
        elif self.exchange_id == exchange.ExchangeId.LIQUID:
            btc = float(info["quantity"])
            jpy = float(info["price"]) * btc
            return _to_json(jpy, btc)
        elif amount and extinfo:
            btc = amount
            jpy = amount * extinfo
            return _to_json(jpy, btc)
        else:
            return {}

    def order_buy(self, amount, extinfo_ask=None):

        # coincheckは amountにBTCではなくて、JPYを指定する。
        # https://coincheck.com/ja/documents/exchange/api#order-new
        if self.exchange_id == exchange.ExchangeId.COINCHECK:
            # coincheckでは buyでどうも実際よりも低い値で注文が成立されるので
            # 補正値でrequestを出してみる
            adjusted_amount = amount + COINCHECK_ORDER_BUY_ADJUST_AMOUNT_BTC
            price = int(extinfo_ask * adjusted_amount)
            response = self.client.create_market_buy_order(price)
        else:
            response = self.client.create_market_buy_order(amount)

        if self.demo_mode or not response:
            return None
        else:
            return self._format_order_response(response,
                                               amount,
                                               extinfo=extinfo_ask)

    def order_sell(self, amount, extinfo_bid=None):
        response = self.client.create_market_sell_order(amount)

        if self.demo_mode or not response:
            return None
        else:
            return self._format_order_response(response,
                                               amount,
                                               extinfo=extinfo_bid)
