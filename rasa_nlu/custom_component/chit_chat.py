# from rasa_nlu.components import Component
# from rasa_nlu import utils
# from rasa_nlu.model import Metadata
from rasa_nlu.components import Component
from rasa_nlu import utils
import typing
from typing import Any, Optional, Text, Dict

if typing.TYPE_CHECKING:
    from rasa_nlu.model import Metadata

import nltk
from nltk.classify import NaiveBayesClassifier
import pandas as pd
import os
import pickle
import json
from fuzzywuzzy import fuzz

CHITCHAT_MODEL_FILE_NAME = "chitchat.pkl"


class ChitChatExtractor(Component):
    """A custom ChitChatExtractor component"""

    name = "chitchat"
    provides = ["entities"]
    requires = ["tokens"]
    defaults = {}
    language_list = ["en"]

    def __init__(self, component_config=None):
        super(ChitChatExtractor, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Load the location polarity labels from the text
           file, retrieve training tokens and after formatting
           data train the classifier."""
        DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        DATA_PATH = os.path.join(DATA_PATH, "chitchat_data.json")
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
        self.clf = data

    def convert_to_rasa(self, value, confidence, entity_got):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": entity_got,
                  "extractor": "ChitChatExtractor"}

        return entity

    def preprocessing(self, tokens):
        """Create bag-of-words representation of the training examples."""

        return ({word: True for word in tokens})

    def process(self, message, **kwargs):
        """Retrieve the tokens of the new message, pass it to the classifier
            and append prediction results to the message class."""

        if not self.clf:
            # component is either not trained or didn't
            # receive enough training data
            entity = None
        else:
            data_dict = self.clf
            user_input = message.text
            total_entity=[]
            user_input_list=user_input.split()
            for entity in data_dict.keys():
                got=set(user_input_list).intersection(set(data_dict[entity]))
                if len(got)>0:
                    got=list(got)
                    for loop in got:
                        total_entity.append(self.convert_to_rasa(loop,True,entity))
                else:
                    pass
            if len(total_entity)>0:
                message.set("chit_chat", total_entity, add_to_output=True)



    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed directory."""

        classifier_file = os.path.join(model_dir, CHITCHAT_MODEL_FILE_NAME)
        utils.pycloud_pickle(classifier_file, self)
        return {"classifier_file": CHITCHAT_MODEL_FILE_NAME}

    @classmethod
    def load(
            cls,
            meta: Dict[Text, Any],
            model_dir: Optional[Text] = None,
            model_metadata: Optional["Metadata"] = None,
            cached_component: Optional["Component"] = None,
            **kwargs: Any
    ) -> "Component":
        meta = model_metadata.for_component(cls.name)
        file_name = meta.get("classifier_file", CHITCHAT_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)

        if os.path.exists(classifier_file):
            return utils.pycloud_unpickle(classifier_file)
        else:
            return cls(meta)
