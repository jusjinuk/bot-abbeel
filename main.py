from flask import Flask, request
from slack_sdk import WebClient
from func import *
from misc import *
from bot import Bot
import os
import json
import openai

app = Flask(__name__)

# ID of the channel you want to send the message to
read_tokens()
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY
bot = Bot()


def handle_event(type, slack_event):
    event = slack_event["event"]
    if "type" not in slack_event or "channel" not in event:
        return response_ok()
    channel = event["channel"]

    print(slack_event)
    if type == "app_mention":
        ts = event["ts"]
        if not bot.mark(ts):
            return response_ok()
        query = event["text"]
        query = parse_mention(query, bot, client)
        user_id = event["user"]
        output, tokens = bot.user_chat(user_id, query, ts)
        answer = f"{output}\n\n`{tokens} tokens`"
        client.chat_postMessage(channel=channel, text=answer)
    return response_ok()


@app.route("/", methods=["POST"])
def handle():
    slack_event = json.loads(request.data)
    if "challenge" in slack_event:
        return handle_challenge(slack_event["challenge"])
    if "event" in slack_event:
        return handle_event(slack_event["event"]["type"], slack_event)
    return response_error()


if __name__ == "__main__":
    bot.init(client)
    app.run(host="0.0.0.0", port=5002)
