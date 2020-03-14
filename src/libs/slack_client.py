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
