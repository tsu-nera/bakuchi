import slack
from src.env import SLACK_API_TOKEN

BOT_CHANNEL_NAME = "#bakuchi-bot"


class SlackClient():
    def __init__(self):
        self.client = slack.WebClient(token=SLACK_API_TOKEN)

        self.channel = BOT_CHANNEL_NAME
        self.user_name = "trading bot"

    def notify(self, message):
        self.client.chat_postMessage(channel=self.channel,
                                     as_user=False,
                                     username=self.user_name,
                                     text=message)
