import os
import time
from threading import Thread

import pandas as pd

import src.constants.ccxtconst as ccxtconst
import src.constants.path as path
from src.config import PROFIT_UPDATE_INTERVAL_MIN

from src.libs.slack_client import SlackClient

import src.utils.trade_history as history

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
        self.start_timestamp = dt.now()
        self.total_profit = 0

        self.__logger = get_profit_logger()

    def __update(self):
        self.__update_orders()
        self.__update_profits()

    def __update_orders(self):
        for exchange_id in ccxtconst.EXCHANGE_ID_LIST:
            since = dt.to_since(self.start_timestamp.timestamp())
            orders = history.fetch_trades(exchange_id,
                                          ccxtconst.TradeMode.BOT,
                                          since=since)

            fetched_df = pd.DataFrame.from_dict(orders)
            pre_df = self.orders[exchange_id]

            merged_df = pd.concat([pre_df, fetched_df]).drop_duplicates()
            self.orders[exchange_id] = merged_df

    def __create_order(self, timestamp, pair, side, fee, amount, price, rate):
        return {
            "datetime": timestamp,
            "pair": pair,
            "side": side,
            "fee": fee,
            "amount": abs(round(float(amount), 9)),  # 注文量
            "price": round(abs(float(price)), 3),  # 実際の価格 amount x rate
            "rate": round(float(rate), 3)  # 現在の価値
        }

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
            self.total_profit = round(self.total_profit + profit, 3)

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
