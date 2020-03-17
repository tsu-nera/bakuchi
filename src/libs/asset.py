import time
import ccxt
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
from src.libs.logger import get_asset_logger
import src.utils.private as private
import src.utils.public as public

from src.libs.ccxt_client import CcxtClient

EXCHANGE_ID_LIST = [
    ccxtconst.EXCHANGE_ID_COINCHECK, ccxtconst.EXCHANGE_ID_LIQUID
]


def format_jpy(jpy):
    return int(jpy)


def format_btc(btc):
    return round(btc, 6)


class Asset():
    def __init__(self, retry=True):
        self.retry = retry
        self.logger = get_asset_logger()

    def _create_asset(self, id, jpy, btc, btc_as_jpy, total_jpy):
        return {
            "id": id,
            "jpy": format_jpy(jpy),
            "btc": format_btc(btc),
            "btc_as_jpy": format_jpy(btc_as_jpy),
            "total_jpy": format_jpy(total_jpy)
        }

    def _update(self):
        self.assets = []
        self.total = {}

        for exchange_id in EXCHANGE_ID_LIST:
            jpy, btc = self._get_balance(exchange_id)

            asset = self._create_asset(exchange_id, jpy, btc)
            self.assets.append(asset)

        self.total["jpy"] = sum([asset["jpy"] for asset in self.assets])
        self.total["btc"] = sum([asset["btc"] for asset in self.assets])

    def _get_balance(self, exchange_id):
        # 短時間に複数回呼び出すとタイミングによってfetchがエラーするのでリトライを実施
        try:
            balance = private.fetch_balance(exchange_id)
        except ccxt.AuthenticationError:
            if self.retry:
                self.logger.info("fetch balance failed. retrying...")
                time.sleep(1)
                try:
                    balance = private.fetch_balance(exchange_id)
                except ccxt.AuthenticationError:
                    self.logger.error("fetch balance failed.")
                    return None, None
            else:
                self.logger.error("fetch balance failed.")
                return None, None
        return int(balance["JPY"]), round(float(balance["BTC"]), 6)

    def to_json(self):
        self._update()
        res = {}
        for asset in self.assets:
            res.update(asset)
        return {"asset": res}

    def run_bot(self):
        '''
        botからの定期実行用
        '''
        self._update()

        # csv出力
        # ログ出力
        # slack出力

    def display(self):
        '''
        資産をチェックするツール
        '''
        coincheck_id = ccxtconst.EXCHANGE_ID_COINCHECK
        liquid_id = ccxtconst.EXCHANGE_ID_LIQUID

        balance_coincheck = private.fetch_balance(coincheck_id)
        balance_liquid = private.fetch_balance(liquid_id)

        data = []

        LABEL_JPY = "JPY"
        LABEL_BTC = "BTC"

        headers = ["取引所", LABEL_JPY, LABEL_BTC]
        data.append(headers)
        data.append([
            coincheck_id,
            int(balance_coincheck[LABEL_JPY]), balance_coincheck[LABEL_BTC]
        ])
        data.append([
            liquid_id,
            int(balance_liquid[LABEL_JPY]), balance_liquid[LABEL_BTC]
        ])

        balance_jpy = int(balance_coincheck[LABEL_JPY] +
                          balance_liquid[LABEL_JPY])
        balance_btc = balance_coincheck[LABEL_BTC] + balance_liquid[LABEL_BTC]

        data.append(["合計", balance_jpy, balance_btc])

        print(tabulate(data, headers="firstrow"))

        coincheck_bid = public.fetch_tick(coincheck_id)["bid"]
        liquid_bid = public.fetch_tick(liquid_id)["bid"]

        def _calc_jpy(bid, btc):
            return int(bid * btc)

        print()
        print("総計: {}[JPY]".format(
            sum([
                int(balance_jpy),
                _calc_jpy(coincheck_bid, balance_coincheck[LABEL_BTC]),
                _calc_jpy(liquid_bid, balance_liquid[LABEL_BTC])
            ])))

    def _get_tick(self, exchange_id):
        c = CcxtClient(exchange_id)
        tick = c.fetch_tick()
        return tick["bid"], tick["ask"]

    def calc_btc_to_jpy(self, btc_amount):
        '''
        与えられたBTCの量から日本円の価格を計算する
        '''
        for exchange_id in EXCHANGE_ID_LIST:
            bid, _ = self._get_tick(exchange_id)

            price = int(btc_amount * bid)
            output = "{}[BTC] to {}[JPY] ({})".format(btc_amount, price,
                                                      exchange_id)
            print(output)

    def calc_jpy_to_btc(self, jpy_price):
        '''
        与えられた日本円の価格で購入できるBTCの量を計算する
        '''
        for exchange_id in EXCHANGE_ID_LIST:
            _, ask = self._get_tick(exchange_id)

            btc_amount = round(jpy_price / ask, 6)
            output = "{}[JPY] to {}[BTC] ({})".format(jpy_price, btc_amount,
                                                      exchange_id)
            print(output)

    def logging(self):
        self._update()

        for asset in self.assets:
            self.logger.info("asset: {}[JPY], {}[BTC] ({})".format(
                asset["jpy"], asset["btc"], asset["id"]))

        self.logger.info("asset: {}[JPY], {}[BTC] (total)".format(
            self.total["jpy"], self.total["btc"]))
