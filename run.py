from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
from ast import literal_eval
import json

import logging
import rasa_core
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig
from rasa_core.run import serve_application
from rasa_core.channels.channel import InputChannel
import json
from rasa_core.tracker_store import MongoTrackerStore

import warnings
import ruamel.yaml as yaml

warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)
logger = logging.getLogger(__name__)

mongo_url = "mongodb://192.168.1.7:27017"

# loading the agent1
domain_file1 = "domain1.yml"
interpreter1 = RasaNLUInterpreter('./models/ner_a1')
action_endpoint1 = EndpointConfig(url="http://localhost:5055/webhook", serve_forever=True)
mongo_tracker1 = MongoTrackerStore(domain=domain_file1, host=mongo_url, db="agent_1")
agent_1 = Agent.load("./models/dialogue_agent_1", interpreter=interpreter1, tracker_store=mongo_tracker1,
                     action_endpoint=action_endpoint1)

# loading the agent2
domain_file2 = "domain2.yml"
interpreter2 = RasaNLUInterpreter('./models/ner_a2')
action_endpoint2 = EndpointConfig(url="http://localhost:5056/webhook", serve_forever=True)
mongo_tracker2 = MongoTrackerStore(domain=domain_file2, host=mongo_url, db="agent_2")
agent_2 = Agent.load("./models/dialogue_agent_2", interpreter=interpreter2, tracker_store=mongo_tracker2,
                     action_endpoint=action_endpoint2)

# creating a dict for agents
agents = {
    "news_bot": agent_1,
    "wheather_bot": agent_2
}


class RasaBot(object):
    def on_post(self, req, resp):
        input_json = req.stream.read()
        input_json = input_json.decode("utf-8")
        try:
            input_json = json.loads(input_json)
        except:
            input_json = literal_eval(input_json)
        try:
            current_agent = agents[input_json["bot_id"]]
            response = current_agent.handle_text(text_message=input_json["user_text"],
                                                 sender_id=input_json["sender_id"])
            resp.body = json.dumps(response)
            resp.status = falcon.HTTP_200
        except Exception as e:
            print(e)
            resp.status = falcon.HTTP_400
        return resp


app = falcon.API()
app.add_route('/rasa_bot', RasaBot())
# python -m rasa_core_sdk.endpoint -p 5055 --actions action1
