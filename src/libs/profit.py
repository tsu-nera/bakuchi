import os
import time
from threading import Thread

import pandas as pd

import src.constants.exchange as exchange
import src.constants.ccxtconst as ccxtconst
import src.constants.path as path

from src.config import PROFIT_UPDATE_INTERVAL_MIN

from src.libs.slack_client import SlackClient

import src.utils.trade_history as history

import src.env as env
import src.utils.datetime as dt

from src.utils.asset import format_jpy_float
from src.libs.asset import Asset

from src.loggers.logger import get_profit_logger


class Profit(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.orders = {}

        order_columns = [
            "datetime", "pair", "side", "fee", "amount", "price", "rate"
        ]
        for exchange_id in exchange.EXCHANGE_ID_LIST:
            self.orders[exchange_id] = pd.DataFrame(columns=order_columns)

        self.asset = Asset()

        self.profits = []
        self.start_timestamp = dt.now()
        self.total_profit = 0

        self.__logger = get_profit_logger()

    def __update(self):
        self.__update_orders()
        self.__update_profits()
        self.__update_profit_stats()

    def __update_orders(self):
        for exchange_id in exchange.EXCHANGE_ID_LIST:
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

        x_orders = self.orders[exchange.EXCHANGE_ID_LIST[0]]
        y_orders = self.orders[exchange.EXCHANGE_ID_LIST[1]]

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

    def __update_profit_stats(self):
        self.asset.force_update()
        _, _, _, self.current_asset_total = self.asset.get_total()
        self.current_btcs = self.asset.get_btcs()

        # Bot稼動での利益
        self.stats_bot = self.calc_bot_profit()

        # 市場利益
        self.stats_market = self.calc_market_profit()

        # 稼動時の利益から市場利益を除いた、純粋なトレード利益
        self.stats_trade = self.calc_trade_profit(self.stats_bot,
                                                  self.stats_market)

    def run(self):
        jpy, btc, btc_as_jpy, total_jpy = self.asset.get_total()

        self.start_asset_jpy = jpy
        self.start_asset_btc_total = btc
        self.start_asset_btc_as_jpy = btc_as_jpy
        self.start_asset_total = total_jpy
        self.current_asset_total = self.start_asset_total

        self.start_btcs = self.asset.get_btcs()
        self.current_btcs = self.start_btcs

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
        for exchange_id in exchange.EXCHANGE_ID_LIST:
            orders = self.orders[exchange_id]
            target_file = "{}.csv".format(exchange_id.value)
            target_path = os.path.join(path.ORDERS_LOG_DIR, target_file)

            orders.to_csv(target_path, index=None)

    def __profits_to_csv(self):
        df = pd.DataFrame.from_dict(self.profits)
        df.to_csv(path.PROFIT_CSV_FILE_PATH, index=None)

    def __logging(self):
        message = "profit={}, bot={}, market={}, trade={}".format(
            self.total_profit, self.stats_bot, self.stats_market,
            self.stats_trade)
        self.__logger.info(message)

    def __notify_slack(self):
        slack = SlackClient(env.SLACK_WEBHOOK_URL_TRADE)
        emoji_gold = "💰"
        message = "[速報] {}円の利益がでました{}".format(self.total_profit, emoji_gold)
        slack.notify_with_datetime(message)

    def display(self):
        for exchange_id in exchange.EXCHANGE_ID_LIST:
            print(self.orders)
            print()
        print(self.profits)

    def calc_bot_profit(self):
        return format_jpy_float(self.current_asset_total -
                                self.start_asset_total)

    def calc_market_profit(self):
        # トレード開始時に保持していたBTCに市場の値動きの差分をかける
        market_profit = 0
        for exchange_id in exchange.EXCHANGE_ID_LIST:
            current_bid = self.current_btcs[exchange_id.value]["bid"]
            start_bid = self.start_btcs[exchange_id.value]["bid"]

            bid_diff = current_bid - start_bid

            market_profit += self.start_btcs[
                exchange_id.value]["btc"] * bid_diff

        return format_jpy_float(market_profit)

    def calc_trade_profit(self, bot_profit, market_profit):
        return format_jpy_float(bot_profit - market_profit)
