import os
import time
import ccxt
from tabulate import tabulate

import src.constants.ccxtconst as ccxtconst
from src.libs.logger import get_asset_logger, get_asset_append_logger
import src.utils.private as private
import src.utils.json as json

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient
from src.libs.asset_logger import AssetLogger

import src.env as env
import src.utils.datetime as dt
import src.constants.path as path

from src.utils.asset import format_jpy, format_btc


class Asset():
    TRADIGNG_START = "start"
    TRADING_END = "end"

    def __init__(self, retry=True):
        self.retry = retry
        self.logger = get_asset_logger()
        self.append_logger = get_asset_append_logger()
        self.csv_logger = AssetLogger()

    def _get_tick(self, exchange_id):
        c = CcxtClient(exchange_id)
        tick = c.fetch_tick()
        return tick["bid"], tick["ask"]

    def _create_asset(self, id, jpy, btc, btc_as_jpy, total_jpy, bid, ask):
        return {
            "id": id,
            "jpy": format_jpy(jpy),
            "btc": format_btc(btc),
            "btc_as_jpy": format_jpy(btc_as_jpy),
            "total_jpy": format_jpy(total_jpy),
            "bid": bid,
            "ask": ask
        }

    def _update(self):
        self.assets = []
        self.total = {}

        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            jpy, btc = self._get_balance(exchange_id)

            btc_as_jpy = self._calc_btc_to_jpy(exchange_id, btc)

            bid, ask = self._get_tick(exchange_id)

            asset = self._create_asset(exchange_id, jpy, btc, btc_as_jpy,
                                       jpy + btc_as_jpy, bid, ask)
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
        self._append_csv()
        # ログ出力
        self._append_log()
        # slack出力
        self._notify_slack()

    def _notify_slack(self):
        slack = SlackClient(env.SLACK_WEBHOOK_URL_ASSET)

        lines = []
        lines.append("現在の資産状況は以下の通り({})".format(dt.now_timestamp()))
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
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
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
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            btc_amount = self._calc_jpy_to_btc(exchange_id, jpy_price)
            output = "{}[JPY] to {}[BTC] ({})".format(jpy_price, btc_amount,
                                                      exchange_id)
            print(output)

    def _log_format(self):
        return "({}) {}[JPY]/{}[BTC]({})/{}[TOTAL JPY]"

    def save(self, keyword):
        self._update()

        # ログファイルへ
        self._logging()

        # jsonへ
        self._logging_json(keyword)

    def _logging_json(self, keyword):
        file_name = "{}.json".format(keyword)
        dir_path = path.ASSETS_LOG_DIR

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

        file_path = os.path.join(dir_path, file_name)

        data = {}
        data["timestamp"] = dt.now_timestamp()
        data["total"] = self.total

        for asset in self.assets:
            data[asset["id"]] = asset

        json.write(file_path, data)

    def _logging(self):
        def _log(id, jpy, btc, btc_as_jpy, total_jpy):
            log_format = self._log_format()
            self.logger.info(
                log_format.format(id, jpy, btc, btc_as_jpy, total_jpy))

        for asset in self.assets:
            _log(asset["id"], asset["jpy"], asset["btc"], asset["btc_as_jpy"],
                 asset["total_jpy"])

        _log(self.total["id"], self.total["jpy"], self.total["btc"],
             self.total["btc_as_jpy"], self.total["total_jpy"])

    def _append_log(self):
        def _log(id, jpy, btc, btc_as_jpy, total_jpy):
            log_format = self._log_format()
            self.append_logger.info(
                log_format.format(id, jpy, btc, btc_as_jpy, total_jpy))

        for asset in self.assets:
            _log(asset["id"], asset["jpy"], asset["btc"], asset["btc_as_jpy"],
                 asset["total_jpy"])

        _log(self.total["id"], self.total["jpy"], self.total["btc"],
             self.total["btc_as_jpy"], self.total["total_jpy"])

    def _append_csv(self):
        for asset in self.assets:
            self.csv_logger.logging(asset["id"], asset["jpy"], asset["btc"],
                                    asset["btc_as_jpy"], asset["total_jpy"])

        self.csv_logger.logging(self.total["id"], self.total["jpy"],
                                self.total["btc"], self.total["btc_as_jpy"],
                                self.total["total_jpy"])
