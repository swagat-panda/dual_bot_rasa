import uuid
import requests
import json

url = "PLEASE ENTER THE URL WHERE THE BOT IS RUNNING http://localhost:5005/rasa_bot"
sender_id = uuid.uuid4().hex


def talk_to_bot():
    input_json = {}
    input_json["sender_id"] = sender_id
    input_json["user_text"] = input("Please enter the query>> ")
    input_json["bot_id"] = input("please enter the bot_id [news_bot/wheather_bot]>> ")
    print(input_json)
    r = requests.post(url=url, json=input_json)
    print(r)
    print(json.dumps(r.json(), indent=4))


if __name__ == '__main__':
    while True:
        talk_to_bot()
