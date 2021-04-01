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
            elif exchange_id == ccxtconst.ExchangeId.LIQUID:
                orders = self.__format_liquid_orders(orders)
            elif exchange_id == ccxtconst.ExchangeId.BITBANK:
                orders = self.__format_bitbank_orders(orders)
            else:
                orders = []

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
            "amount": abs(round(float(amount), 9)),  # 注文量
            "price": round(abs(float(price)), 3),  # 実際の価格 amount x rate
            "rate": round(float(rate), 3)  # 現在の価値
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

            trade = self.__create_order(timestamp, t["pair"], t["side"],
                                        float(t["fee"]),
                                        float(t["funds"]["btc"]),
                                        float(t["funds"]["jpy"]),
                                        float(t["rate"]))
            orders.append(trade)

        return self.__marge_duplicated_orders(orders)

    def __format_liquid_orders(self, data):
        orders = []

        for t in data:
            created_at = datetime.datetime.fromtimestamp(t["created_at"])
            timestamp = dt.format_timestamp(created_at)
            if not self.__is_valid_timestamp(timestamp):
                continue

            amount = float(t["quantity"])
            rate = float(t["price"])
            price = amount * rate
            trade = self.__create_order(timestamp, t["pair"], t["taker_side"],
                                        0, amount, price, rate)
            orders.append(trade)
        return self.__marge_duplicated_orders(orders)

    def __format_bitbank_orders(self, data):
        orders = []

        for t in data:
            created_at = datetime.datetime.fromtimestamp(
                int(t["executed_at"] / 1000))
            timestamp = dt.format_timestamp(created_at)
            if not self.__is_valid_timestamp(timestamp):
                continue

            amount = float(t["amount"])
            rate = float(t["price"])
            price = amount * rate
            trade = self.__create_order(timestamp, t["pair"], t["side"], 0,
                                        amount, price, rate)
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
                x_price = x_price
            else:
                x_price = -1 * x_price

            if y_side == 'sell':
                y_price = y_price
            else:
                y_price = -1 * y_price

            return round(x_price + y_price, 3)

        self.profits = []
        self.total_profit = 0

        x_orders = self.orders[ccxtconst.EXCHANGE_ID_LIST[0]]
        y_orders = self.orders[ccxtconst.EXCHANGE_ID_LIST[1]]

        if len(x_orders) > len(y_orders):
            x_orders = x_orders[:len(y_orders)]
        elif len(x_orders) < len(y_orders):
            y_orders = y_orders[:len(x_orders)]

        x_orders.index = x_orders["datetime"]
        y_orders.index = y_orders["datetime"]
        x_orders = x_orders.sort_index()
        y_orders = y_orders.sort_index()

        timestamps = x_orders["datetime"].tolist()
        x_sides = x_orders["side"].tolist()
        x_prices = x_orders["price"].tolist()
        y_sides = y_orders["side"].tolist()
        y_prices = y_orders["price"].tolist()

        for timestamp, x_side, x_price, y_side, y_price in zip(
                timestamps, x_sides, x_prices, y_sides, y_prices):
            profit = __calc_profit(x_side, x_price, y_side, y_price)
            data = {
                "timestamp": timestamp,
                "x_side": x_side,
                "x_price": x_price,
                "y_side": y_side,
                "y_price": y_price,
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
