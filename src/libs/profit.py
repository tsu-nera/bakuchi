import os
import datetime

import pandas as pd
from statistics import mean

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient

import src.env as env
import src.utils.datetime as dt


class Profit():
    def __init__(self, retry=True):
        self.orders = {}

        order_columns = [
            "datetime", "pair", "side", "fee", "amount", "price", "rate"
        ]
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            self.orders[exchange_id] = pd.DataFrame(columns=order_columns)

        self.profits = []

    def __update(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            client = CcxtClient(exchange_id)
            orders = client.fetch_trades(ccxtconst.TradeMode.BOT)

            if exchange_id == ccxtconst.ExchangeId.COINCHECK:
                orders = self.__format_coincheck_orders(orders)
            else:
                orders = self.__format_fetched_orders(orders)

            fetced_df = pd.DataFrame.from_dict(orders)
            pre_df = self.orders[exchange_id]

            merged_df = pd.concat([pre_df, fetced_df]).drop_duplicates()
            self.orders[exchange_id] = merged_df

    def __create_trade(self, datetime, pair, side, fee, amount, price, rate):
        return {
            "datetime": datetime,
            "pair": pair,
            "side": side,
            "fee": fee,
            "amount": abs(round(float(amount), 9)),
            "price": round(abs(float(price)), 3),
            "rate": round(float(rate), 3)
        }

    def __convert_coincheck_datetime(self, d_str):
        timestamp = datetime.datetime.fromisoformat(d_str.replace('Z', ''))
        timestamp = timestamp + datetime.timedelta(hours=9)
        return timestamp.strftime(dt.DATETIME_BASE_FORMAT)

    def __format_coincheck_orders(self, data):
        orders = []
        for t in data:
            trade = self.__create_trade(
                self.__convert_coincheck_datetime(t["created_at"]), t["pair"],
                t["side"], float(t["fee"]), float(t["funds"]["btc"]),
                float(t["funds"]["jpy"]), float(t["rate"]))
            orders.append(trade)

        return self.__marge_duplicated_orders(orders)

    def __format_fetched_orders(self, data):
        orders = []

        for t in data:
            created_at = datetime.datetime.fromtimestamp(t["created_at"])
            timestamp = dt.format_timestamp(created_at)

            trade = self.__create_trade(timestamp, t["pair"], t["taker_side"],
                                        0, t["quantity"], t["price"],
                                        t["rate"])
            orders.append(trade)
        return self.__marge_duplicated_orders(orders)

    def __marge_duplicated_orders(self, orders):
        dup = [trade['datetime'] for trade in orders]
        dup_count_list = [dup.count(x) for x in dup]

        filterd_orders = []

        i = 0
        while i < len(dup):
            n = dup_count_list[i]

            if n > 1:
                current_trade = orders[i]
                total_amount = sum([orders[i + j]["amount"] for j in range(n)])
                total_price = sum([orders[i + j]["price"] for j in range(n)])
                average_rate = mean([orders[i + j]["rate"] for j in range(n)])

                trade = self.__create_trade(current_trade["datetime"],
                                            current_trade["pair"],
                                            current_trade["side"],
                                            current_trade["fee"], total_amount,
                                            total_price, average_rate)
            else:
                trade = orders[i]
            filterd_orders.append(trade)
            i += n

        return filterd_orders

    def run_bot(self):
        '''
        botからの定期実行用
        '''
        self.__update()

        # orders log
        self.__orders_to_csv()

        # profits log
        # self.__append_csv()
        # # ログ出力
        # self.__append_log()
        # # slack出力
        # self.__notify_slack()

    def __orders_to_csv(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            orders = self.orders[exchange_id]
            target_file = "{}.csv".format(exchange_id.value)
            target_path = os.path.join(path.ORDERS_LOG_DIR, target_file)

            orders.to_csv(target_path, index=None)

    def __notify_slack(self):
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

    def _log_format(self):
        return "({}) {}[JPY]/{}[BTC]({})/{}[TOTAL JPY]"

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

    def display(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            print(self.orders)
            print()
        print(self.profits)
