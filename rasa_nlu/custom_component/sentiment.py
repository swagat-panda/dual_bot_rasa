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
import os

SENTIMENT_MODEL_FILE_NAME = "sentiment_classifier.pkl"


class SentimentAnalyzer(Component):
    """A custom sentiment analysis component"""

    name = "sentiment"
    provides = ["entities"]
    requires = ["tokens"]
    defaults = {}
    language_list = ["en"]

    def __init__(self, component_config=None):
        super(SentimentAnalyzer, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Load the sentiment polarity labels from the text
           file, retrieve training tokens and after formatting
           data train the classifier."""
        DATA_PATH = os.path.abspath(os.path.dirname(__file__))
        DATA_PATH = os.path.join(DATA_PATH, "labels.txt")
        with open(DATA_PATH, 'r') as f:
            labels = f.read().splitlines()

        training_data = training_data.training_examples  # list of Message objects
        tokens = [list(map(lambda x: x.text, t.get('tokens'))) for t in training_data]
        processed_tokens = [self.preprocessing(t) for t in tokens]
        labeled_data = [(t, x) for t, x in zip(processed_tokens, labels)]
        self.clf = NaiveBayesClassifier.train(labeled_data)

    def convert_to_rasa(self, value, confidence):
        """Convert model output into the Rasa NLU compatible output format."""

        entity = {"value": value,
                  "confidence": confidence,
                  "entity": "sentiment",
                  "extractor": "sentiment_extractor"}

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
            tokens = [t.text for t in message.get("tokens")]
            tb = self.preprocessing(tokens)
            print(tb,"-------------->sentiment.py")
            pred = self.clf.prob_classify(tb)
            print(self.clf,"-------------->sentiment.py")
            print(pred,"-------------->sentiment.py")

            sentiment = pred.max()
            confidence = pred.prob(sentiment)

            entity = self.convert_to_rasa(sentiment, confidence)

            message.set("entities", [entity], add_to_output=True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed directory."""

        classifier_file = os.path.join(model_dir, SENTIMENT_MODEL_FILE_NAME)
        utils.pycloud_pickle(classifier_file, self)
        return {"classifier_file": SENTIMENT_MODEL_FILE_NAME}

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
        file_name = meta.get("classifier_file", SENTIMENT_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)

        if os.path.exists(classifier_file):
            return utils.pycloud_unpickle(classifier_file)
        else:
            return cls(meta)