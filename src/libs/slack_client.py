import requests
import json

import src.utils.datetime as dt

NEWLINE = "\n"


class SlackClient():
    def __init__(self, url):
        self.url = url

    def notify(self, message):
        if self.url == "":
            # URLが設定されていない場合は空通知 開発環境を想定
            return

        payload = {"text": message}
        data = json.dumps(payload)
        requests.post(self.url, data=data)

    def notify_with_datetime(self, message):
        now_timestamp = dt.now_timestamp()
        self.notify(NEWLINE.join([now_timestamp, message]))

    def notify_error(self, message):
        self.notify_with_datetime(message)

    def notify_order(self, ex_id_ask, ex_id_bid, symbol, amount,
                     expected_profit):
        now_timestamp = dt.now_timestamp()

        emoji_gold = "💰"

        profit_message = "{}円の利益{}".format(expected_profit, emoji_gold)
        order_message = "{}の{}を{}で買い{}で売りました。".format(amount, symbol,
                                                      ex_id_ask.value,
                                                      ex_id_bid.value)

        message = NEWLINE.join(
            [profit_message, "", now_timestamp, order_message])

        self.notify(message)
