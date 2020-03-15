import slack
from src.env import SLACK_API_TOKEN

BOT_CHANNEL_NAME = "#bakuchi-bot"
USER_NAME = "trading bot"
SLACK_ICON_URL = "https://github.com/tsu-nera/bakuchi/blob/master/images/bitcoin.png"


class SlackClient():
    def __init__(self):
        self.client = slack.WebClient(token=SLACK_API_TOKEN)

    def notify(self, message):
        self.client.chat_postMessage(channel=BOT_CHANNEL_NAME,
                                     as_user=False,
                                     username=USER_NAME,
                                     icon_url=SLACK_ICON_URL,
                                     text=message)

    def notify_order(self, buy_exchange_id, sell_exchange_id, symbol, amount,
                     expected_profit):
        message = "[取引実行]{}を{}, {}で買い{}で売りました。\n期待される利益は{}円です。".format(
            symbol, amount, buy_exchange_id, sell_exchange_id, expected_profit)

        self.notify(message)
