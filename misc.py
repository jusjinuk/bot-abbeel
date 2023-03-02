from slack_sdk import WebClient
from bot import Bot
import os
import re


def read_tokens():
    if os.path.isfile("tokens.txt"):
        with open("tokens.txt") as f:
            text = f.readlines()
        tokens = dict()
        for line in text:
            key, val = line.strip().split("=")
            tokens[key] = val
            os.environ[key] = val


def parse_mention(input, bot: Bot, client: WebClient):
    # Define the pattern to match
    pattern = re.compile("<@(.+?)>")

    output = input
    user_ids = pattern.findall(input)
    for user_id in user_ids:
        name = bot.get_user_name(user_id)
        output = output.replace(f"<@{user_id}>", f"@{name}")
    # Remove double spaces
    output = re.sub(r"\s{2,}", " ", output).strip()
    return output
