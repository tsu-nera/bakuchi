import time
import ccxt
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
from src.libs.logger import get_asset_logger
import src.utils.private as private

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient

import src.env as env
from src.utils.datetime import now_string

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

    def _get_tick(self, exchange_id):
        c = CcxtClient(exchange_id)
        tick = c.fetch_tick()
        return tick["bid"], tick["ask"]

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

            btc_as_jpy = self._calc_btc_to_jpy(exchange_id, btc)

            asset = self._create_asset(exchange_id, jpy, btc, btc_as_jpy,
                                       jpy + btc_as_jpy)
            self.assets.append(asset)

        def _sum(key):
            return sum([asset[key] for asset in self.assets])

        self.total["id"] = "total"
        self.total["jpy"] = _sum("jpy")
        self.total["btc"] = _sum("btc")
        self.total["btc_as_jpy"] = _sum("btc_as_jpy")
        self.total["total_jpy"] = _sum("total_jpy")

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
        self._notify_slack()

    def _notify_slack(self):
        slack = SlackClient(env.SLACK_WEBHOOK_URL_ASSET)

        lines = []
        lines.append("現在の資産状況は以下の通り({})".format(now_string()))
        lines.append("")

        for asset in self.assets:
            line = "[{}] {}円/{}BTC({}) 計{}円".format(asset["id"], asset["jpy"],
                                                    asset["btc"],
                                                    asset["btc_as_jpy"],
                                                    asset["total_jpy"])
            lines.append(line)
        line = "[{}] {}円/{}BTC({}) 計{}円".format(self.total["id"],
                                                self.total["jpy"],
                                                self.total["btc"],
                                                self.total["btc_as_jpy"],
                                                self.total["total_jpy"])
        lines.append(line)

        message = "\n".join(lines)
        slack.notify(message)

    def display(self):
        '''
        現在の資産を表示する
        '''
        self._update()

        data = []

        headers = ["取引所", "JPY", "BTC", "BTC[JPY]", "total[JPY]"]
        data.append(headers)

        for asset in self.assets:
            data.append([
                asset["id"], asset['jpy'], asset["btc"], asset["btc_as_jpy"],
                asset["total_jpy"]
            ])

        data.append([])
        data.append([
            "合計", self.total["jpy"], self.total["btc"],
            self.total["btc_as_jpy"], self.total["total_jpy"]
        ])

        print(tabulate(data, headers="firstrow"))

    def _calc_btc_to_jpy(self, exchange_id, btc_amount):
        '''
        与えられたBTCの量から日本円の価格を計算する
        '''
        bid, _ = self._get_tick(exchange_id)
        return format_jpy(btc_amount * bid)

    def calc_btc_to_jpy(self, btc_amount):
        '''
        与えられたBTCの量から日本円の価格を計算する
        '''
        for exchange_id in EXCHANGE_ID_LIST:
            price = self._calc_btc_to_jpy(exchange_id, btc_amount)
            output = "{}[BTC] to {}[JPY] ({})".format(btc_amount, price,
                                                      exchange_id)
            print(output)

    def _calc_jpy_to_btc(self, exchange_id, jpy_price):
        _, ask = self._get_tick(exchange_id)
        return format_btc(jpy_price / ask)

    def calc_jpy_to_btc(self, jpy_price):
        '''
        与えられた日本円の価格で購入できるBTCの量を計算する
        '''
        for exchange_id in EXCHANGE_ID_LIST:
            btc_amount = self._calc_jpy_to_btc(exchange_id, jpy_price)
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
