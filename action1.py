from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet, UserUtteranceReverted
from typing import Dict, Text, Any, List  # -*- coding: utf-8 -*-
from rasa_core_sdk import Tracker
from rasa_core_sdk.executor import CollectingDispatcher
import requests
import json


class News(Action):
    def name(self) -> Text:
        return "action_news"

    def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print(json.dumps(tracker.slots,indent=4))
        dispatcher.utter_message("we got a hit in news api")


class Wheather(Action):
    def name(self) -> Text:
        return "action_wheather"
    def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        print(json.dumps(tracker.slots, indent=4))
        dispatcher.utter_message("got a hit in Wheather api ")