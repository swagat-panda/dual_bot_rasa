# url="http://192.168.1.83:5007/webhooks/rest/webhook"
# data={'sender': "1255435", "message": "wheather"}
#
import requests

# r=requests.post(url=url,json=data)
# print(r)
# import json
# print(json.dumps(r.json(),indent=4))

url = "http://192.168.1.83:5005/rasa_bot"
data = {'sender_id': 1455444455567, "user_text": "news", "bot_id": "news_bot"}
data1={'sender_id': 1455567, "user_text": "hi", "bot_id": "wheather_bot"}
r = requests.post(url=url, json=data1)
print(r)
import json

print(json.dumps(r.json(), indent=4))
