from slack_sdk import WebClient
import openai
import time


def system_prompt(user):
    prompt = f"""This conversation is done in a slack channel of Machine Learning Lab.
You are a helpful ChatBot (and SlackBot) named Abbeel.
User's name is {user} and user may speak in English or Korean.
Be as concise as possible."""
    return {"role": "system", "content": prompt}


class Bot:
    def init(self, client: WebClient):
        # https://api.slack.com/methods/users.list/
        self.prc = []
        self.users = dict()
        # Historys are identified by user id
        self.user_chats = dict()
        self.client = client

    def get_user_name(self, id):
        if id in self.users:
            name = self.users[id]
        else:
            response = self.client.users_info(user=id)
            name = response["user"]["profile"]["display_name"]
            if not name:
                name = response["user"]["profile"]["real_name"]
            self.users[id] = name
        return name

    def user_chat(self, user_id, text, ts):
        if not user_id in self.user_chats:
            self.user_chats[user_id] = Chat(self.get_user_name(user_id), text, ts)
        else:
            self.user_chats[user_id].add_chat("user", text, ts)
        chat: Chat = self.user_chats[user_id]
        chat_dict = chat.parse_to_openai_input()
        output, output_ts, tokens = self.send_to_openai(chat_dict)
        chat.add_chat("bot", output, output_ts)
        return output, tokens

    def send_to_openai(self, chat_dict):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=chat_dict
        )
        print(response)
        # Dummy
        output = response["choices"][0]["message"]["content"].strip()
        output_ts = time.time()
        tokens = response["usage"]["total_tokens"]
        return output, output_ts, tokens

    def mark(self, ts):
        # Check if bot is already processing
        if len(self.prc) > 0 and float(ts) <= float(self.prc[-1]):
            return False
        if ts in self.prc:
            return False
        self.prc.append(ts)
        if len(self.prc) > 50:
            self.prc.pop(0)
        return True


class Chat:
    def __init__(self, name, text, ts) -> None:
        self.name = name
        self.history = [text]
        # "user" or "bot"
        self.turn = "user"
        self.latest = ts

    def add_chat(self, turn, text, ts):
        if self.turn == turn:
            print("Not Ready")
            return False
        if self.turn == "bot":
            assert len(self.history) % 2 == 0
        else:
            assert len(self.history) % 2 == 1
        # Cleaning history to scalable amount
        if float(ts) - float(self.latest) > 180 and self.turn == "bot":
            self.history = []
        if len(self.history) > 2 and self.turn == "bot":
            del self.history[0 : len(self.history) - 2]
        self.history.append(text)
        self.turn = "bot" if self.turn == "user" else "user"
        self.latest = ts
        return True

    def parse_to_openai_input(self):
        assert self.turn == "user"
        assert len(self.history) % 2 == 1
        chats = []
        chats.append(system_prompt(self.name))
        for ind, chat in enumerate(self.history):
            if ind % 2 == 0:
                chats.append({"role": "user", "content": chat})
            else:
                chats.append({"role": "assistant", "content": chat})
        return chats
