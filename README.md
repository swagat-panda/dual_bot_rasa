# dual_bot_rasa

#TO RUN THE BOT
* first give the host ip of the mongodb in run.py line no -25 and give your ip in the talk_to_bot.py Line number-5
* run the 2 action i.e (action1.py,action2.py)
cmd-python -m rasa_core_sdk.endpoint -p 5055 --actions action1 and
python -m rasa_core_sdk.endpoint -p 5056 --actions action2
* then run the run.py file where 2 bots are loaded
cmd- gunicorn -b 0.0.0.0:5005 run:app

#talk to bot
* run the talk_to_bot.py file and you will be able to talk to the 2 bots
CMD- python talk_to_bot.py

#train the bot(optional because models are already given)
* run the 2 python file train_agent1.py and train_agent2.py

## Download all the required python packages from requirements.txt
cmd - pip install -r requirements.txt