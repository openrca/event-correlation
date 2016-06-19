import copy
import json
import logging
import math

import numpy as np

from core import event, rule
from core.event import Event


class Sequence:
    def __init__(self, events, length, rules=None, calculatedRules=None):
        if (rules is None):
            rules = []
        if (calculatedRules is None):
            calculatedRules = []

        self.events = events
        self.length = length
        self.rules = rules
        self.calculatedRules = calculatedRules

    def getEvents(self, eventType=None):
        res = []
        for e in self.events:
            if (eventType is None or e.eventType == eventType):
                res.append(e)
        return res

    def getEvent(self, index):
        result = []
        for e in self.events:
            if (index < math.floor(e.timestamp)):
                break
            if (math.floor(e.timestamp) == index):
                result.append(e)
        if (len(result) == 0):
            result.append(Event(timestamp=index))
        return result

    def getCalculatedRule(self, trigger, response):
        return self._getRule(trigger, response, self.calculatedRules)

    def getRule(self, trigger, response):
        return self._getRule(trigger, response, self.rules)

    @staticmethod
    def _getRule(trigger, response, rules):
        if (isinstance(trigger, Event)):
            trigger = trigger.eventType
        if (isinstance(response, Event)):
            response = response.eventType

        for r in rules:
            if (r.trigger == trigger and r.response == response):
                return r
        return None

    def asVector(self, eventType):
        l = [e for e in self.getEvents(eventType) if e.occurred]
        v = np.zeros(len(l))
        i = 0
        for e in l:
            v[i] = e.timestamp
            i += 1
        return v

    def __len__(self):
        return len(self.events)

    def __str__(self):
        tokens = []

        seq = copy.copy(self.getEvents())
        for i in range(self.length):
            if (len(seq) > 0 and seq[0].timestamp <= i):
                while (len(seq) > 0 and seq[0].timestamp <= i):
                    e = seq.pop(0)
                    tokens.append(e.getExternalRepresentation())
            else:
                tokens.append("_")
        return "".join(tokens)

    def asJson(self):
        events = []
        for e in self.getEvents():
            events.append(e.asJson())
        rules = []
        for r in self.rules:
            rules.append(r.asJson())
        calculatedRules = []
        for r in self.calculatedRules:
            calculatedRules.append(r.asJson())
        return {
            "length": self.length,
            "events": events,
            "rules": rules,
            "calculatedRules": calculatedRules
        }

    def store(self, filename):
        with open(filename, "w+") as file:
            file.write(json.dumps(self.asJson()))


def load(value):
    if (isinstance(value, str)):
        value = json.loads(value)

    try:
        length = int(value["length"])

        events = []
        for item in value["events"]:
            e = event.load(item)
            if (e not in events):
                events.append(e)
            while (e.triggered is not None):
                e = e.triggered
                if (e not in events):
                    events.append(e)
        events.sort(key=lambda x: x.timestamp)

        rules = []
        if ("rules" in value):
            for item in value["rules"]:
                r = rule.load(item)
                rules.append(r)

        calculatedRules = []
        if ("rules" in value):
            for item in value["calculatedRules"]:
                r = rule.load(item)
                calculatedRules.append(r)

        seq = Sequence(events, length, rules)
        seq.calculatedRules = calculatedRules
        logging.debug("Loaded sequence: " + str(seq))
        return seq
    except KeyError:
        raise ValueError("Missing parameter 'length' and/or 'events'")


def loadFromFile(filename):
    with open(filename, "r") as file:
        content = json.loads("".join(file.readlines()))

        entry = load(content)
        return entry
