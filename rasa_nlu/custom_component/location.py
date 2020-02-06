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

LOCATION_MODEL_FILE_NAME = "location.pkl"


class LocationExtractor(Component):
    """A custom location Extractor component"""

    name = "location"
    provides = ["entities"]
    requires = ["tokens"]
    defaults = {}
    language_list = ["en"]

    def __init__(self, component_config=None):
        super(LocationExtractor, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Load the location polarity labels from the text
           file, retrieve training tokens and after formatting
           data train the classifier."""
        DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        DATA_PATH = os.path.join(DATA_PATH, "data.csv")
        data_frame_location = pd.read_csv(DATA_PATH)
        # data_frame_location = data_frame_location["location"]
        # location = list(data_frame_location)
        # location_lowercase = []
        # for loop in location:
        #     location_lowercase.append(loop.lower())
        self.clf = data_frame_location

    def convert_to_rasa(self, value, confidence, statename, Districtname):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "destination",
                  "statename": statename,
                  "Districtname": Districtname,
                  "extractor": "LocationExtractor"}

        return entity

    def preprocessing(self, tokens):
        """Create bag-of-words representation of the training examples."""

        return ({word: True for word in tokens})

    def process(self, message, **kwargs):
        """Retrieve the tokens of the new message, pass it to the classifier
            and append prediction results to the message class."""
        print("got here**********999999999999999")
        print(type(self.clf))
        # if not self.clf:
        #     print("got here**********")
        #     # component is either not trained or didn't
        #     # receive enough training data
        #     entity = None
        # else:
        # with open('location.pkl', 'rb') as handle:
        #     location_list = pickle.load(handle)
        location_list = self.clf
        print("got here**********")
        print(type(location_list))
        # DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        # DATA_PATH = os.path.join(DATA_PATH, "data.csv")
        # data_frame_location = pd.read_csv(DATA_PATH)
        # data_frame_location = data_frame_location["location"]
        # location = list(data_frame_location)
        # print(location,type(location))
        # location_lowercase=[]
        # for loop in location:
        #     location_lowercase.append(loop.lower())
        user_input = message.text
        # user_input=user_input.split()
        DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        DATA_PATH = os.path.join(DATA_PATH, "loc_syno.json")
        with open(DATA_PATH, "r") as f:
            syno = json.load(f)
        print(user_input, "---->input in location")

        # values = [substring for substring in location_list if user_input.find(substring) != -1]
        values = [substring for substring in location_list if substring in user_input]
        final_value = []
        final_state = []
        final_dist = []
        for index, row in location_list.iterrows():
            if fuzz.token_set_ratio(row['Locality'].lower(), user_input) > 90:
                final_value.append(row['Locality'].lower())
                final_state.append(row['StateName'].lower())
                final_dist.append(row["Districtname"].lower())
        for index in range(len(final_value)):
            if final_value[index] in syno.keys():
                final_value[index] = syno[final_value[index]]

        print(values, "-------------> got all location.py")
        final_value = list(set(final_value))
        print(final_value, "-------> after location ")
        entity = []

        DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        DATA_PATH = os.path.join(DATA_PATH, "exception.json")
        with open(DATA_PATH, "r") as f:
            exception_dict = json.load(f)
        matched_data = []
        matched_data = list(set(final_value).intersection(set(exception_dict.keys())))
        for eachData in matched_data:
            if fuzz.token_set_ratio(exception_dict[eachData], user_input) > 90:
                if fuzz.token_set_ratio(eachData, user_input) > 90:
                    get_delete_index = final_value.index(eachData)
                    final_value.pop(get_delete_index)
                    final_state.pop(get_delete_index)
                    final_dist.pop(get_delete_index)
        if len(final_value) > 0:
            for value, state, dist in zip(final_value, final_state, final_dist):
                confidence = True
                entity.append(self.convert_to_rasa(value, confidence, state, dist))
        entity = list(set(entity))
        # else:
        #     value=None
        #     confidence=False
        #     entity.append(self.convert_to_rasa(value, confidence))
        print(entity, "--------------------->location.py")

        message.set("entities", entity, add_to_output=True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed directory."""

        classifier_file = os.path.join(model_dir, LOCATION_MODEL_FILE_NAME)
        utils.pycloud_pickle(classifier_file, self)
        return {"classifier_file": LOCATION_MODEL_FILE_NAME}

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
        file_name = meta.get("classifier_file", LOCATION_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)

        if os.path.exists(classifier_file):
            return utils.pycloud_unpickle(classifier_file)
        else:
            return cls(meta)
