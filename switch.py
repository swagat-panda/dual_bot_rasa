from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import logging

import pickle
import uuid

import logging
import inspect, os, sys

from rasa_core.tracker_store import TrackerStore
from rasa_core import utils
from rasa_core.agent import Agent
from rasa_core.domain import Domain, TemplateDomain
from rasa_core.events import SlotSet
from rasa_core.trackers import DialogueStateTracker
from rasa_core.tracker_store import MongoTrackerStore, TrackerStore, InMemoryTrackerStore, RedisTrackerStore
from rasa_core.interpreter import (NaturalLanguageInterpreter)
from rasa_core.channels.channel import UserMessage
from flask import Blueprint, request, jsonify, Flask, render_template
from rasa_core.utils import EndpointConfig

# connect to MongoDb from local network
import pymongo
from pymongo import MongoClient

mongo_service = os.environ['MONGO_SERVICE_HOST']
redis_service = os.environ['REDIS_SERVICE_HOST']

client = MongoClient('mongodb://{}:27017/'.format(mongo_service))
db = client.simba

mongo_tracker_store = MongoTrackerStore(domain=domain, host="mongodb://{}".format(mongo_service), db="main")
redis_store = RedisTrackerStore(domain, host=redis_service, port=6379)

# Agent number one
interpreter = RasaNLUInterpreter('./models/nlu/Auto/Auto')
domain = TemplateDomain.load("models/dialogue/domain.yml")
action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
tracker_store = RedisTrackerStore(domain, host="localhost", port=6379, db=13)

agent_one = Agent.load('domain', interpreter=interpreter, tracker_store=mongo_tracker_store,
                       action_endpoint=action_endpoint)

# Agent number two
# interpreter = RasaNLUInterpreter('./models/nlu/Auto/Auto')
# domain = TemplateDomain.load("models/dialogue/domain.yml")
# action_endpoint = EndpointConfig(url="http://localhost:5055/webhook")
# tracker_store = RedisTrackerStore(domain,host="localhost", port=6379, db= 13)

agent_two = Agent.load('domain', interpreter=interpreter, tracker_store=mongo_tracker_store,
                       action_endpoint=action_endpoint)

# start the server
app = Flask(__name__)


def switch_agent(argument):
    switcher = {
        "agent_one": agent_one,
        "agent_two": agent_two
    }
    return switcher.get(argument, "Invalid agent name.")


@app.route('/sendMessage')
def new_message():
    message = str(request.args.get('message'))
    current_agent_name = str(request.args.get('current_agent_name'))
    tracker = superagent.tracker_store.get_or_create_tracker(sender_id=callId)
    # You can either pass in the current agent with the request params, or you can save it in the tracker conversatio to
    # toggle between agents in one conversation, and handle the logic in your actions
    # current_agent_name = tracker.get_slot("current_agent")
    current_agent = switch_agent(current_agent_name)
    bot_response = current_agent.handle_text(text_message=message, sender_id=callId)
    result = ""
    for resp in bot_response:
        result += resp['text']

    return str(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, use_reloader=False)