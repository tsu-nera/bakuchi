import src.constants.ccxtconst as ccxtconst
from src.libs.logger import get_asset_logger
import src.utils.private as private

EXCHANGE_ID_LIST = [
    ccxtconst.EXCHANGE_ID_COINCHECK, ccxtconst.EXCHANGE_ID_LIQUID
]


class Asset():
    def __init__(self):
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
                                  3)

    def _get_balance(self, exchange_id):
        balance = private.fetch_balance(exchange_id)
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
