import time
import ccxt

import src.constants.ccxtconst as ccxtconst
from src.libs.logger import get_asset_logger
import src.utils.private as private

EXCHANGE_ID_LIST = [
    ccxtconst.EXCHANGE_ID_COINCHECK, ccxtconst.EXCHANGE_ID_LIQUID
]


class Asset():
    def __init__(self, retry=True):
        self.retry = retry
        self.logger = get_asset_logger()

    def _create_asset(self, id, jpy, btc):
        return {"id": id, "jpy": int(jpy), "btc": round(btc, 6)}

    def _update(self):
        self.assets = []
        self.total = {}

        for exchange_id in EXCHANGE_ID_LIST:
            jpy, btc = self._get_balance(exchange_id)

            asset = self._create_asset(exchange_id, jpy, btc)
            self.assets.append(asset)

        self.total["jpy"] = int(sum([asset["jpy"] for asset in self.assets]))
        self.total["btc"] = round(sum([asset["btc"] for asset in self.assets]),
                                  6)

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

    def logging(self):
        self._update()

        for asset in self.assets:
            self.logger.info("asset: {}[JPY], {}[BTC] ({})".format(
                asset["jpy"], asset["btc"], asset["id"]))

        self.logger.info("asset: {}[JPY], {}[BTC] (total)".format(
            self.total["jpy"], self.total["btc"]))
