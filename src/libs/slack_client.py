import datetime
import requests
import json
from src.env import SLACK_WEBHOOK_URL

NEWLINE = "\n"


class SlackClient():
    def notify(self, message):
        payload = {"text": message}
        data = json.dumps(payload)
        requests.post(SLACK_WEBHOOK_URL, data=data)

    def _get_datetime_string(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def notify_with_datetime(self, message):
        now_string = self._get_datetime_string()
        self.notify(NEWLINE.join([now_string, message]))

    def notify_order(self, buy_exchange_id, sell_exchange_id, symbol, amount,
                     expected_profit):
        now_string = self._get_datetime_string()

        emoji_gold = "💰"

        profit_message = "{}円の利益{}".format(expected_profit, emoji_gold)
        order_message = "{}の{}を{}で買い{}で売りました。".format(amount, symbol,
                                                      buy_exchange_id,
                                                      sell_exchange_id)

        message = NEWLINE.join([profit_message, "", now_string, order_message])

        self.notify(message)
