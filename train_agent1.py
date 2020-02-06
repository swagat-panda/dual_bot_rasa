from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

## train the first agent nlu and core
from rasa_nlu.training_data import load_data
from rasa_nlu.model import Trainer
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu import config


import logging

from rasa_core.agent import Agent
from rasa_core.policies.keras_policy import KerasPolicy
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.form_policy import FormPolicy

import warnings
import ruamel.yaml as yaml
warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)
logging.basicConfig(level='INFO')

'''
training the nlu
'''
args1 = {"pipeline": "tensorflow_embedding"}
conf1 = RasaNLUModelConfig(args1)
trainer1 = Trainer(conf1)

#nlu for agent 1
training_data1 = load_data("./data1/nlu.md")
Interpreter1 = trainer1.train(training_data1)
model_directory1 = trainer1.persist('./models', fixed_model_name="ner_a1")

#core for agent1
domain_file = "domain1.yml"
training_data_file = './data1/stories.md'
model_path = './models/dialogue_agent_1'
agent = Agent(domain_file, policies=[MemoizationPolicy(max_history=3), KerasPolicy(max_history=3, epochs=500, batch_size=10), FormPolicy()])
data = agent.load_data(training_data_file)
agent.train(data)
agent.persist(model_path)
agent = Agent(domain_file, policies=[MemoizationPolicy(), KerasPolicy(max_history=3, epochs=500, batch_size=50)])
data = agent.load_data(training_data_file)

agent.train(data)

agent.persist(model_path)

