import os
import time
import datetime
from threading import Thread

import pandas as pd
from statistics import mean

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
from src.config import PROFIT_UPDATE_INTERVAL_MIN

from src.libs.ccxt_client import CcxtClient
from src.libs.slack_client import SlackClient

import src.env as env
import src.utils.datetime as dt
from src.loggers.logger import get_profit_logger


class Profit(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.orders = {}

        order_columns = [
            "datetime", "pair", "side", "fee", "amount", "price", "rate"
        ]
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            self.orders[exchange_id] = pd.DataFrame(columns=order_columns)

        self.profits = []
        self.start_timestamp = datetime.datetime.now()
        self.total_profit = 0

        self.__logger = get_profit_logger()

    def __update(self):
        self.__update_orders()
        self.__update_profits()

    def __update_orders(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            client = CcxtClient(exchange_id)
            orders = client.fetch_trades(ccxtconst.TradeMode.BOT)

            if exchange_id == ccxtconst.ExchangeId.COINCHECK:
                orders = self.__format_coincheck_orders(orders)
            else:
                orders = self.__format_fetched_orders(orders)

            fetched_df = pd.DataFrame.from_dict(orders)
            pre_df = self.orders[exchange_id]

            merged_df = pd.concat([pre_df, fetched_df]).drop_duplicates()
            self.orders[exchange_id] = merged_df

    def __create_order(self, datetime, pair, side, fee, amount, price, rate):
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

    def __is_valid_timestamp(self, timestamp):
        timestamp = datetime.datetime.strptime(timestamp,
                                               dt.DATETIME_BASE_FORMAT)
        return timestamp > self.start_timestamp

    def __format_coincheck_orders(self, data):
        orders = []
        for t in data:
            timestamp = self.__convert_coincheck_datetime(t["created_at"])
            if not self.__is_valid_timestamp(timestamp):
                continue

            trade = self.__creppate_order(timestamp, t["pair"], t["side"],
                                        float(t["fee"]),
                                        float(t["funds"]["btc"]),
                                        float(t["funds"]["jpy"]),
                                        float(t["rate"]))
            orders.append(trade)

        return self.__marge_duplicated_orders(orders)

    def __format_fetched_orders(self, data):
        orders = []

        for t in data:
            created_at = datetime.datetime.fromtimestamp(t["created_at"])
            timestamp = dt.format_timestamp(created_at)
            if not self.__is_valid_timestamp(timestamp):
                continue

            trade = self.__create_order(timestamp, t["pair"], t["taker_side"],
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

                order = self.__create_order(current_trade["datetime"],
                                            current_trade["pair"],
                                            current_trade["side"],
                                            current_trade["fee"], total_amount,
                                            total_price, average_rate)
            else:
                order = orders[i]
            filterd_orders.append(order)
            i += n

        return filterd_orders

    def __update_profits(self):
        def __calc_profit(x_side, x_price, y_side, y_price):
            if x_side == 'sell':
                cc_price = x_price
            else:
                cc_price = -1 * x_price

            if y_side == 'sell':
                lq_price = y_price
            else:
                lq_price = -1 * y_price

            return int(cc_price + lq_price)

        self.profits = []
        self.total_profit = 0

        # とりあえずcoincheckとliquid固定で。
        cc_orders = self.orders[ccxtconst.ExchangeId.COINCHECK]
        lq_orders = self.orders[ccxtconst.ExchangeId.LIQUID]

        if len(cc_orders) > len(lq_orders):
            cc_orders = cc_orders[:len(lq_orders)]
        elif len(cc_orders) < len(lq_orders):
            lq_orders = lq_orders[:len(cc_orders)]

        cc_orders.index = cc_orders["datetime"]
        lq_orders.index = lq_orders["datetime"]
        cc_orders = cc_orders.sort_index()
        lq_orders = lq_orders.sort_index()

        timestamps = cc_orders["datetime"].tolist()
        cc_sides = cc_orders["side"].tolist()
        cc_prices = cc_orders["price"].tolist()
        lq_sides = lq_orders["side"].tolist()
        lq_prices = lq_orders["price"].tolist()

        for timestamp, cc_side, cc_price, lq_side, lq_price in zip(
                timestamps, cc_sides, cc_prices, lq_sides, lq_prices):
            profit = __calc_profit(cc_side, cc_price, lq_side, lq_price)
            data = {
                "timestamp": timestamp,
                "cc_side": cc_side,
                "cc_price": cc_price,
                "lq_side": lq_side,
                "lq_price": lq_price,
                "profit": profit
            }
            self.profits.append(data)
            self.total_profit += profit

    def run(self):
        while True:
            self.run_bot()
            time.sleep(PROFIT_UPDATE_INTERVAL_MIN * 60)

    def run_bot(self):
        '''
        botからの定期実行用
        '''
        self.__update()

        # orders log
        self.__orders_to_csv()

        # profit log
        self.__profits_to_csv()
        # ログ出力
        self.__logging()
        # slack出力
        self.__notify_slack()

    def __orders_to_csv(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            orders = self.orders[exchange_id]
            target_file = "{}.csv".format(exchange_id.value)
            target_path = os.path.join(path.ORDERS_LOG_DIR, target_file)

            orders.to_csv(target_path, index=None)

    def __profits_to_csv(self):
        df = pd.DataFrame.from_dict(self.profits)
        df.to_csv(path.PROFIT_CSV_FILE_PATH, index=None)

    def __logging(self):
        message = "profit={}".format(self.total_profit)
        self.__logger.info(message)

    def __notify_slack(self):
        slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)
        emoji_gold = "💰"
        message = "[速報] {}円の利益がでました{}".format(self.total_profit, emoji_gold)
        slack.notify_with_datetime(message)

    def display(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            print(self.orders)
            print()
        print(self.profits)
