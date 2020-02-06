from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import rasa_core
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.utils import EndpointConfig
from rasa_core.run import serve_application
from rasa_core.channels.channel import InputChannel
import json
from rasa_core.tracker_store import MongoTrackerStore, TrackerStore, InMemoryTrackerStore, RedisTrackerStore

import warnings
import ruamel.yaml as yaml
#python -m rasa_core_sdk.endpoint -p 5056 --actions action1
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)
domain_file = "domain2.yml"
logger = logging.getLogger(__name__)
interpreter = RasaNLUInterpreter('./models/ner_a2')
action_endpoint = EndpointConfig(url="http://localhost:5056/webhook", serve_forever=True)
mongo_tracker = MongoTrackerStore(domain=domain_file,host="mongodb://192.168.1.7:27017", db="agent_2")
agent = Agent.load("./models/dialogue_agent_2", interpreter=interpreter, tracker_store=mongo_tracker,
                   action_endpoint=action_endpoint)
# rasa_core.run.serve_application(agent,port=5007)
print(agent.handle_text(text_message="hi",sender_id="0368"))