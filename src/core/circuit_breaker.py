import datetime
import time

from src.libs.logger import get_trading_logger_with_stdout
import src.constants.ccxtconst as ccxtconst
import src.utils.private as private

import src.config as config


class CircuitBreaker():
    def __init__(self, exchange_ids):
        self.exchange_ids = exchange_ids
        self.logger = get_trading_logger_with_stdout()

        self.trade_amount_btc = config.TRADE_AMOUNT

    def _display_message(self):
        self.logger.info("=============================")
        self.logger.info("= CIRCUIT BREAKER CALLED!!! =")
        self.logger.info("=============================")

    def _wait(self, sec):
        self.logger.info("waiting for {} sec ...".format(sec))
        time.sleep(sec)

    def _is_liquid_server_maintenance(self):
        now = datetime.datetime.now()
        # 6:55
        maintenance_start_time = datetime.datetime(now.year, now.month,
                                                   now.day, 6, 55, 0)
        # 7:05
        maintenance_end_time = datetime.datetime(now.year, now.month, now.day,
                                                 7, 5, 0)

        if maintenance_start_time <= now and now <= maintenance_end_time:
            self.logger.info(
                "liquid is currently daily server maintenance...(6:55-7:05)")
            return True
        else:
            return False

    def _is_server_maintenance(self, exchange_id):
        # 臨時サーバメンテナンスのときもとりあえずここに判定を追記していく。

        if exchange_id == ccxtconst.EXCHANGE_ID_LIQUID:
            return self._is_liquid_server_maintenance()
        else:
            return False

    def is_server_maintenance(self):
        # 臨時サーバメンテナンスのときもとりあえずここに判定を追記していく。

        return any([
            self._is_server_maintenance(exchange_id)
            for exchange_id in self.exchange_ids
        ])

    def recover_exchange_not_available(self):
        self._display_message()

        self._wait(3)

        self.logger.info("exchange not available error recovery start")

        self._recover_exchange_not_available()

        self.logger.info("exchange not available error recovery completed")

    def _move_jpy_to_btc(self, exchange_id, amount):
        time.sleep(1)
        if exchange_id == ccxtconst.EXCHANGE_ID_COINCHECK:
            private.create_coincheck_buy_order(ccxtconst.SYMBOL_BTC_JPY,
                                               amount)
        else:
            private.create_buy_order(exchange_id, ccxtconst.SYMBOL_BTC_JPY,
                                     amount)

    def _recover_exchange_not_available(self):
        # 資産状況のチェック
        assets_btc = []
        assets_jpy = []

        for exchange_id in self.exchange_ids:
            balance = private.fetch_balance(exchange_id)

            asset_btc = {"id": exchange_id, "value": balance["BTC"]}
            asset_jpy = {"id": exchange_id, "value": balance["JPY"]}
            assets_btc.append(asset_btc)
            assets_jpy.append(asset_jpy)

        for asset in assets_btc:
            exchange_id = asset['id']
            btc = asset['value']
            amount = config.TRADE_AMOUNT

            if btc < amount:
                self.logger.info(
                    '{} BTC is not enough (available:{} / neseccery:{})'.
                    format(exchange_id, btc, amount))

                move_amount = amount - btc + 0.001
                self.logger.info('try buy {} BTC at {}'.format(
                    move_amount, exchange_id))
                self._move_jpy_to_btc(exchange_id, move_amount)

        # BTC to JPY は未実装
        # 現状coincheckのBTCが不足するエラーのみなので
