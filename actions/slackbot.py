import json
import os
import requests
# from pprint import pprint as pp
from dotenv import load_dotenv
from slackclient.settings import BASE_DIR

load_dotenv(os.path.join(BASE_DIR, '.env'))

SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')


def slack_post_msg(text, channel, **kwargs):
    data = {
        "token": SLACK_BOT_TOKEN,
        "channel": channel,
        "text": f'{text}'
    }

    data.update(kwargs)

    response = requests.post(
        url="https://slack.com/api/chat.postMessage",
        data=data
    )
